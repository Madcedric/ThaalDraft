from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from app.services.auth import get_current_user
from app.services import document_service
from app.services.citation.analyzer import analyze_citations
from app.services.citation.schema import CitationAnalysisResponse

router = APIRouter()


@router.post("/{document_id}/citations/analyze", response_model=CitationAnalysisResponse)
async def analyze_document_citations(
    document_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Run full citation analysis on a structured document."""
    try:
        doc = document_service.get_document(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        structured = doc.get("structured_json")
        if not structured:
            raise HTTPException(status_code=400, detail="Document has not been structured yet")

        report = analyze_citations(
            structured_json=structured,
            document_id=document_id,
            resolve_dois=False,
        )

        document_service.update_document(
            document_id,
            {"citation_report": report.model_dump(), "updated_at": datetime.utcnow().isoformat() + "Z"},
        )

        return CitationAnalysisResponse(
            document_id=document_id,
            report=report,
            status="completed",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}/citations")
async def get_citation_report(
    document_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get citation report for a document."""
    try:
        doc = document_service.get_document(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        citation_report = doc.get("citation_report")
        if not citation_report:
            raise HTTPException(status_code=404, detail="Citation analysis not yet performed")

        return {"document_id": document_id, "report": citation_report}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}/citations/health")
async def get_citation_health(
    document_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get citation health score for a document."""
    try:
        doc = document_service.get_document(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        citation_report = doc.get("citation_report")
        if not citation_report:
            raise HTTPException(status_code=404, detail="Citation analysis not yet performed")

        health = citation_report.get("health_score", {})
        return {
            "document_id": document_id,
            "health_score": health,
            "total_citations": citation_report.get("total_citations", 0),
            "total_references": citation_report.get("total_references", 0),
            "resolved_citations": citation_report.get("resolved_citations", 0),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
