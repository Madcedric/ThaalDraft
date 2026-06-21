import sys
import os
import time
import asyncio
import logging
from typing import Dict

# Add the root directory to sys.path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.services import job_service, document_service, struct_service
from app.services.document_parser import parse_document
from app.services.manuscript.engine import build_manuscript
from app.api.routes.websockets import manager
from app.services.citation.analyzer import analyze_citations

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def process_parse_job(job: Dict):
    job_id = job.get("id")
    document_id = job.get("document_id")
    payload = job.get("payload", {})
    file_path = payload.get("file_path")
    file_ext = payload.get("file_ext", "unknown")

    logger.info(f"Processing parse job {job_id} for document {document_id}")

    try:
        if not file_path or not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Perform heavy parsing
        parsed_data = parse_document(file_path)
        structured_data = struct_service.normalize_classification(parsed_data, file_type=file_ext)
        manuscript = build_manuscript(structured_data)
        structured_data["manuscript_model"] = manuscript.model_dump()

        # Fetch existing document to inject parsed_json (which updates the normalized tables)
        doc = document_service.get_document(document_id)
        if doc:
            # Run citation analysis asynchronously as part of the parse job
            citation_report = analyze_citations(
                structured_json=structured_data,
                document_id=document_id,
                resolve_dois=True  # Enabled for async worker
            )
            structured_data["citation_report"] = citation_report.model_dump()

            doc["parsed_json"] = structured_data
            # Re-create the document record to update the normalized tables with the new data
            document_service.create_document_record(doc)
            
            # Update document status
            document_service.update_document(document_id, {"status": "structured"})

        # Mark job as completed
        job_service.update_job(job_id, {"status": "completed", "result": {"message": "Parsed successfully"}})
        logger.info(f"Job {job_id} completed successfully.")

        # Try to notify websockets (synchronously for now to avoid asyncio loop issues in this script)
        # In a real async worker, we'd use asyncio.run(manager.broadcast_to_document(...))
        try:
            asyncio.run(manager.broadcast_to_document(document_id, {"event": "job_completed", "job_type": "parse"}))
        except Exception:
            pass

    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        job_service.update_job(job_id, {"status": "failed", "error_message": str(e)})
        try:
            asyncio.run(manager.broadcast_to_document(document_id, {"event": "job_failed", "job_type": "parse"}))
        except Exception:
            pass


def main_loop():
    logger.info("Starting background queue worker...")
    while True:
        try:
            job = job_service.claim_next_job()
            if job:
                job_type = job.get("job_type")
                if job_type == "parse":
                    process_parse_job(job)
                else:
                    logger.warning(f"Unknown job type: {job_type}")
                    job_service.update_job(job.get("id"), {"status": "failed", "error_message": f"Unknown job type: {job_type}"})
            else:
                # Polling interval
                time.sleep(2)
        except Exception as e:
            logger.error(f"Worker loop error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main_loop()
