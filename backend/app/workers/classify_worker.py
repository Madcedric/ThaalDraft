"""One-shot classify worker.

Processes a single pending `classify` job by running deterministic section classification.
"""
import os
from datetime import datetime
from app.services import job_service, document_service, ai_service


def iso_now():
    return datetime.utcnow().isoformat() + "Z"


def process_one():
    job = job_service.fetch_pending_job(job_type="classify")
    if not job:
        print("No pending classify jobs found.")
        return

    job_id = job.get("id")
    print(f"Picked classify job {job_id}")

    job_service.update_job(job_id, {"status": "started", "started_at": iso_now()})

    document_id = job.get("document_id")
    doc = document_service.get_document(document_id)
    if not doc:
        job_service.update_job(
            job_id,
            {"status": "failed", "result": {"error": "document not found"}, "finished_at": iso_now()},
        )
        return

    parsed = doc.get("parsed_json")
    if not parsed:
        job_service.update_job(
            job_id,
            {"status": "failed", "result": {"error": "no parsed_json to classify"}, "finished_at": iso_now()},
        )
        return

    try:
        result = ai_service.classify_structure(parsed)

        document_service.update_document(
            document_id,
            {"ai_classification": result, "updated_at": iso_now()},
        )

        struct_job = {
            "document_id": document_id,
            "type": "structure",
            "status": "pending",
            "payload": {},
        }
        job_service.create_job(struct_job)

        job_service.update_job(
            job_id,
            {"status": "finished", "result": result, "finished_at": iso_now()},
        )
        print(f"Classify job {job_id} finished and structure job enqueued.")
    except Exception as e:
        print(f"Classify job {job_id} failed: {e}")
        job_service.update_job(
            job_id,
            {"status": "failed", "result": {"error": str(e)}, "finished_at": iso_now()},
        )


if __name__ == "__main__":
    process_one()
