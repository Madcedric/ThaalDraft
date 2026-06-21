"""One-shot plagiarism worker.

Fetches a pending `plagiarism` job, compares the target document against other documents,
stores a plagiarism report and updates job status.
"""
from app.services import job_service, document_service, plagiarism_service


def iso_now():
    from datetime import datetime
    return datetime.utcnow().isoformat() + "Z"


def process_one():
    job = job_service.fetch_pending_job(job_type="plagiarism")
    if not job:
        print("No pending plagiarism jobs found.")
        return

    job_id = job.get("id")
    print(f"Picked plagiarism job {job_id}")

    job_service.update_job(job_id, {"status": "started", "started_at": iso_now()})

    document_id = job.get("document_id")
    doc = document_service.get_document(document_id)
    if not doc:
        job_service.update_job(job_id, {"status": "failed", "result": {"error": "document not found"}, "finished_at": iso_now()})
        return

    # Build text from parsed_json
    parsed = doc.get("parsed_json") or {}
    parts = []
    if parsed.get("title"):
        parts.append(parsed.get("title"))
    if parsed.get("abstract"):
        parts.append(parsed.get("abstract"))
    for s in parsed.get("sections", []):
        if isinstance(s, dict):
            parts.append(s.get("heading", ""))
            parts.append(s.get("content", ""))
    target_text = "\n".join([p for p in parts if p])

    # Get comparison corpus (other documents)
    corpus = document_service.list_documents_texts(exclude_document_id=document_id, limit=200)

    try:
        matches = plagiarism_service.check_against_corpus(target_text, corpus, top_n=10)
        report = {"matches": matches}

        rec = plagiarism_service.create_plagiarism_record(document_id, report)

        job_service.update_job(job_id, {"status": "finished", "result": {"plagiarism": rec}, "finished_at": iso_now()})
        print(f"Plagiarism job {job_id} finished; report stored: {rec}")
    except Exception as e:
        print(f"Plagiarism job {job_id} failed: {e}")
        job_service.update_job(job_id, {"status": "failed", "result": {"error": str(e)}, "finished_at": iso_now()})


if __name__ == "__main__":
    process_one()
