from fastapi import APIRouter, HTTPException, Depends
from app.services.reviewer import ReviewAnalysisRequest, ReviewAnalysisResponse, analyze_review
from app.services.document_service import DocumentService
from app.api.routes.auth import get_current_user

router = APIRouter()
document_service = DocumentService()


@router.post("/{document_id}/review/analyze", response_model=ReviewAnalysisResponse)
async def analyze_document_review(
    document_id: str,
    request: ReviewAnalysisRequest,
    current_user: dict = Depends(get_current_user),
):
    """Analyze document and generate reviewer feedback."""
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
                detail="Document must be structured before review analysis",
            )

        citation_report = None
        if hasattr(doc, "citation_report") and doc.citation_report:
            citation_report = doc.citation_report if isinstance(doc.citation_report, dict) else None

        report = analyze_review(
            document_id=document_id,
            structured_data=structured_data,
            citation_report=citation_report,
            journal_id=request.journal_id,
        )

        document_service.update_document(document_id, {"review_report": report.model_dump()})

        return ReviewAnalysisResponse(
            document_id=document_id,
            report=report,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}/review")
async def get_document_review(
    document_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get existing review report for a document."""
    try:
        doc = document_service.get_document(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc.user_id != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Not authorized")

        review_report = getattr(doc, "review_report", None)
        if not review_report:
            raise HTTPException(
                status_code=404,
                detail="No review report found. Run analysis first.",
            )

        return {"document_id": document_id, "report": review_report}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
