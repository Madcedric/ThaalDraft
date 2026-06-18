"""One-shot format worker.

Consumes `format` jobs and generates DOCX/PDF exports from `documents.structured_json`.
Currently supports DOCX generation for the 'ieee' template.
"""
import os
from datetime import datetime
from app.services import job_service, document_service, storage_service, format_service, export_service, pdf_service


def iso_now():
    return datetime.utcnow().isoformat() + "Z"


def process_one():
    job = job_service.fetch_pending_job(job_type="format")
    if not job:
        print("No pending format jobs found.")
        return

    job_id = job.get("id")
    print(f"Picked format job {job_id}")

    job_service.update_job(job_id, {"status": "started", "started_at": iso_now()})

    document_id = job.get("document_id")
    payload = job.get("payload") or {}
    template = payload.get("template", "ieee")
    fmt = payload.get("format", "docx")

    doc = document_service.get_document(document_id)
    if not doc:
        job_service.update_job(job_id, {"status": "failed", "result": {"error": "document not found"}, "finished_at": iso_now()})
        return

    structured = doc.get("parsed_json")
    if not structured:
        job_service.update_job(job_id, {"status": "failed", "result": {"error": "no parsed_json available"}, "finished_at": iso_now()})
        return

    try:
        # Generate DOCX
        out_dir = "exports"
        os.makedirs(out_dir, exist_ok=True)
        filename = f"{document_id}_{template}.{fmt}"
        output_path = os.path.join(out_dir, filename)

        if fmt == "docx":
            format_service.format_to_docx(structured, output_path, template=template)
        elif fmt == "pdf":
            # Generate DOCX to temporary path, then convert to PDF
            temp_docx = os.path.join(out_dir, f"{document_id}_{template}.docx")
            format_service.format_to_docx(structured, temp_docx, template=template)
            # Convert
            pdf_ok = pdf_service.convert_docx_to_pdf(temp_docx, output_path)
            if not pdf_ok:
                raise RuntimeError("PDF conversion failed; ensure LibreOffice or docx2pdf is available")
        else:
            raise ValueError("Only 'docx' and 'pdf' export are supported by format_worker currently")

        # Upload to storage
        storage_path = storage_service.upload_file_to_supabase(output_path, f"exports/{filename}")

        # Create export record
        exp = export_service.create_export(document_id, fmt, storage_path or output_path)

        # Update document status
        document_service.update_document(document_id, {"status": "formatted", "updated_at": iso_now()})

        job_service.update_job(job_id, {"status": "finished", "result": {"export": exp}, "finished_at": iso_now()})
        print(f"Format job {job_id} finished; export created: {exp}")
    except Exception as e:
        print(f"Format job {job_id} failed: {e}")
        job_service.update_job(job_id, {"status": "failed", "result": {"error": str(e)}, "finished_at": iso_now()})


if __name__ == "__main__":
    process_one()
