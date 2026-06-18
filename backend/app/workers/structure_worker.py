"""One-shot structure worker.

Consumes `structure` jobs, normalizes AI classification + parsed JSON into a stable structured JSON,
and updates the `documents.structured_json` field.
"""
from app.services import job_service, document_service, struct_service


def iso_now():
    from datetime import datetime
    return datetime.utcnow().isoformat() + "Z"


def process_one():
    job = job_service.fetch_pending_job(job_type="structure")
    if not job:
        print("No pending structure jobs found.")
        return

    job_id = job.get("id")
    print(f"Picked structure job {job_id}")

    job_service.update_job(job_id, {"status": "started", "started_at": iso_now()})

    document_id = job.get("document_id")
    doc = document_service.get_document(document_id)
    if not doc:
        job_service.update_job(job_id, {"status": "failed", "result": {"error": "document not found"}, "finished_at": iso_now()})
        return

    parsed = doc.get("parsed_json")
    ai_class = doc.get("ai_classification")
    filename = doc.get("filename") or ""
    file_ext = filename.split(".")[-1] if "." in filename else "unknown"
    if not parsed:
        job_service.update_job(job_id, {"status": "failed", "result": {"error": "no parsed_json to structure"}, "finished_at": iso_now()})
        return

    try:
        structured = struct_service.normalize_classification(parsed, ai_class, file_type=file_ext)

        document_service.update_document(document_id, {"parsed_json": structured, "status": "structured", "updated_at": iso_now()})

        job_service.update_job(job_id, {"status": "finished", "result": structured, "finished_at": iso_now()})
        print(f"Structure job {job_id} finished.")
    except Exception as e:
        print(f"Structure job {job_id} failed: {e}")
        job_service.update_job(job_id, {"status": "failed", "result": {"error": str(e)}, "finished_at": iso_now()})


if __name__ == "__main__":
    process_one()
