"""One-shot parse worker.

Usage: run this script to process a single pending `parse` job. Designed to be run by a simple supervisor
or scheduled loop. It will:
 - fetch one pending job
 - mark job started
 - download the document file (Supabase or local uploads)
 - run `parse_docx` to extract structure
 - update `documents.parsed_json` and mark job finished
"""
import os
import time
from datetime import datetime
from app.services import job_service, document_service, storage_service
from app.services.document_parser import parse_document

UPLOAD_DIR = "uploads"


def find_local_file(filename: str) -> str | None:
    # Try to locate the file under uploads directory by filename suffix
    if not filename:
        return None
    for root, dirs, files in os.walk(UPLOAD_DIR):
        for f in files:
            if f.endswith(filename):
                return os.path.join(root, f)
    return None


def iso_now():
    return datetime.utcnow().isoformat() + "Z"


def process_one():
    job = job_service.fetch_pending_job()
    if not job:
        print("No pending jobs found.")
        return

    job_id = job.get("id")
    print(f"Picked job {job_id}")

    # mark started
    job_service.update_job(job_id, {"status": "started", "started_at": iso_now()})

    document_id = job.get("document_id")
    if not document_id:
        job_service.update_job(job_id, {"status": "failed", "result": {"error": "missing document_id"}, "finished_at": iso_now()})
        return

    doc = document_service.get_document(document_id)
    if not doc:
        job_service.update_job(job_id, {"status": "failed", "result": {"error": "document not found"}, "finished_at": iso_now()})
        return

    filename = doc.get("filename")
    storage_path = doc.get("storage_path")

    local_path = None
    try:
        if storage_path:
            # download from Supabase storage to uploads/<basename>
            basename = os.path.basename(storage_path)
            dest = os.path.join(UPLOAD_DIR, f"job_{job_id}_{basename}")
            ok = storage_service.download_file_from_supabase(storage_path, dest)
            if not ok:
                raise RuntimeError("failed to download from storage")
            local_path = dest
        else:
            # fall back to local upload directory
            local_path = find_local_file(filename)
            if not local_path:
                raise RuntimeError("local file not found")

        # run parse
        parsed = parse_document(local_path)

        # update document parsed_json
        document_service.update_document(document_id, {"parsed_json": parsed, "status": "parsed", "updated_at": iso_now()})

        # enqueue classification job for AI processing
        classify_job = {
            "document_id": document_id,
            "type": "classify",
            "status": "pending",
            "payload": {}
        }
        job_service.create_job(classify_job)

        # mark job finished
        job_service.update_job(job_id, {"status": "finished", "result": parsed, "finished_at": iso_now()})
        print(f"Job {job_id} processed successfully; classification job enqueued.")
    except Exception as e:
        print(f"Job {job_id} failed: {e}")
        job_service.update_job(job_id, {"status": "failed", "result": {"error": str(e)}, "finished_at": iso_now()})


if __name__ == "__main__":
    process_one()
