"""One-shot citation worker.

Processes a single pending `citation` job by running citation analysis on the document's structured JSON.
"""
from datetime import datetime
from app.services import job_service, document_service
from app.services.citation.analyzer import analyze_citations


def iso_now():
    return datetime.utcnow().isoformat() + "Z"


def process_one():
    job = job_service.fetch_pending_job(job_type="citation")
    if not job:
        print("No pending citation jobs found.")
        return

    job_id = job.get("id")
    print(f"Picked citation job {job_id}")

    job_service.update_job(job_id, {"status": "started", "started_at": iso_now()})

    document_id = job.get("document_id")
    doc = document_service.get_document(document_id)
    if not doc:
        job_service.update_job(
            job_id,
            {"status": "failed", "result": {"error": "document not found"}, "finished_at": iso_now()},
        )
        return

    structured = doc.get("parsed_json")
    if not structured:
        job_service.update_job(
            job_id,
            {"status": "failed", "result": {"error": "no parsed_json for citation analysis"}, "finished_at": iso_now()},
        )
        return

    try:
        report = analyze_citations(
            structured_json=structured,
            document_id=document_id,
            resolve_dois=False,
        )

        existing = doc.get("parsed_json") or {}
        existing["citation_report"] = report.model_dump()
        document_service.update_document(
            document_id,
            {"parsed_json": existing, "updated_at": iso_now()},
        )

        job_service.update_job(
            job_id,
            {"status": "finished", "result": report.model_dump(), "finished_at": iso_now()},
        )
        print(f"Citation job {job_id} finished.")
    except Exception as e:
        print(f"Citation job {job_id} failed: {e}")
        job_service.update_job(
            job_id,
            {"status": "failed", "result": {"error": str(e)}, "finished_at": iso_now()},
        )


if __name__ == "__main__":
    process_one()
