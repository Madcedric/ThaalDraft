from fastapi import APIRouter, HTTPException, Depends
from app.services.compliance import (
    ComplianceAnalysisRequest,
    ComplianceAnalysisResponse,
    analyze_compliance,
    get_all_journal_rules,
    get_journal_rule,
)
from app.services.document_service import DocumentService
from app.services.citation.analyzer import analyze_citations
from app.api.routes.auth import get_current_user

router = APIRouter()
document_service = DocumentService()


@router.get("/compliance/journals")
async def list_compliance_journals():
    """List all supported journals with their compliance rules."""
    journals = get_all_journal_rules()
    return {"journals": [j.model_dump() for j in journals]}


@router.get("/compliance/journals/{journal_id}")
async def get_compliance_journal(journal_id: str):
    """Get compliance rules for a specific journal."""
    rule = get_journal_rule(journal_id)
    if not rule:
        raise HTTPException(status_code=404, detail=f"Journal '{journal_id}' not found")
    return rule.model_dump()


@router.post("/{document_id}/compliance/analyze", response_model=ComplianceAnalysisResponse)
async def analyze_document_compliance(
    document_id: str,
    request: ComplianceAnalysisRequest,
    current_user: dict = Depends(get_current_user),
):
    """Analyze document compliance against journal requirements."""
    try:
        doc = document_service.get_document(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc.user_id != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Not authorized")

        structured_data = doc.structured_json or {}
        if not structured_data:
            raise HTTPException(
                status_code=400,
                detail="Document must be structured before compliance analysis",
            )

        citation_report = None
        if hasattr(doc, "citation_report") and doc.citation_report:
            citation_report = doc.citation_report if isinstance(doc.citation_report, dict) else None

        report = analyze_compliance(
            document_id=document_id,
            journal_id=request.journal_id,
            structured_data=structured_data,
            citation_report=citation_report,
        )

        document_service.update_document(document_id, {"compliance_report": report.model_dump()})

        return ComplianceAnalysisResponse(
            document_id=document_id,
            report=report,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}/compliance")
async def get_document_compliance(
    document_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get existing compliance report for a document."""
    try:
        doc = document_service.get_document(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc.user_id != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Not authorized")

        compliance_report = getattr(doc, "compliance_report", None)
        if not compliance_report:
            raise HTTPException(
                status_code=404,
                detail="No compliance report found. Run analysis first.",
            )

        return {"document_id": document_id, "report": compliance_report}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
