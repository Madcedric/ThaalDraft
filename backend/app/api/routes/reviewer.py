from fastapi import APIRouter, HTTPException, Depends
from app.services.reviewer import ReviewAnalysisRequest, ReviewAnalysisResponse
from app.services.reviewer.engine_v2 import review_manuscript
from app.services.manuscript.engine import build_manuscript
from app.services.manuscript.model import manuscript_from_dict, StructuredManuscript
from app.services import document_service
from app.api.routes.auth import get_current_user

router = APIRouter()


@router.post("/{document_id}/review/analyze", response_model=ReviewAnalysisResponse)
async def analyze_document_review(
    document_id: str,
    request: ReviewAnalysisRequest,
    current_user: dict = Depends(get_current_user),
):
    """Analyze document and generate reviewer feedback using AI."""
    try:
        doc = document_service.get_document(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc.get("user_id") != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Not authorized")

        structured_data = doc.get("parsed_json") or {}
        if not structured_data:
            raise HTTPException(
                status_code=400,
                detail="Document must be structured before review analysis",
            )

        manuscript_data = structured_data.get("manuscript_model")
        if manuscript_data:
            manuscript = manuscript_from_dict(manuscript_data)
        else:
            manuscript = build_manuscript(structured_data)
            structured_data["manuscript_model"] = manuscript.model_dump()
            document_service.update_document(document_id, {"parsed_json": structured_data})

        review_result = review_manuscript(manuscript, journal_id=request.journal_id)

        existing = doc.get("parsed_json") or {}
        existing["review_report"] = review_result
        document_service.update_document(document_id, {"parsed_json": existing})

        from app.services.reviewer.schema import (
            ReviewReport,
            ReviewCategory,
            ReviewFinding,
            ReviewSeverity,
            ReviewStrength,
            CategoryScore,
            PublicationReadiness,
        )

        strengths = []
        for s in review_result.get("strengths", []):
            try:
                cat = ReviewCategory(s.get("category", "writing_quality"))
                strengths.append(ReviewStrength(
                    category=cat,
                    title=s.get("title", "Strength"),
                    description=s.get("description", ""),
                ))
            except (ValueError, TypeError):
                continue

        weaknesses = []
        for w in review_result.get("weaknesses", []):
            try:
                cat = ReviewCategory(w.get("category", "writing_quality"))
                sev_str = w.get("severity", "minor")
                sev = ReviewSeverity(sev_str) if sev_str in [s.value for s in ReviewSeverity] else ReviewSeverity.MINOR
                weaknesses.append(ReviewFinding(
                    category=cat,
                    severity=sev,
                    title=w.get("title", "Issue"),
                    description=w.get("description", ""),
                    recommendation=w.get("recommendation"),
                ))
            except (ValueError, TypeError):
                continue

        suggestions = review_result.get("improvement_suggestions", [])

        cs_data = review_result.get("category_scores", {})
        category_scores = []
        for cat_name, score_val in cs_data.items():
            try:
                cat = ReviewCategory(cat_name)
                category_scores.append(CategoryScore(
                    category=cat,
                    score=float(score_val),
                    summary=f"Score: {score_val}/100",
                    finding_count=0,
                ))
            except (ValueError, TypeError):
                continue

        pr_data = review_result.get("publication_readiness", {})

        report = ReviewReport(
            document_id=document_id,
            journal_id=request.journal_id,
            strengths=strengths,
            weaknesses=weaknesses,
            missing_references=[],
            improvement_suggestions=suggestions,
            category_scores=category_scores,
            publication_readiness=PublicationReadiness(
                overall=float(pr_data.get("overall", 50)),
                label=pr_data.get("label", "Needs Revision"),
                summary=pr_data.get("summary", ""),
            ),
            total_findings=len(weaknesses),
            critical_count=sum(1 for w in weaknesses if w.severity == ReviewSeverity.CRITICAL),
            major_count=sum(1 for w in weaknesses if w.severity == ReviewSeverity.MAJOR),
            minor_count=sum(1 for w in weaknesses if w.severity == ReviewSeverity.MINOR),
            suggestion_count=len(suggestions),
            analysis_method=review_result.get("analysis_method", "unknown"),
        )

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

        if doc.get("user_id") != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Not authorized")

        review_report = (doc.get("parsed_json") or {}).get("review_report")
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
