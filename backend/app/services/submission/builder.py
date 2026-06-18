from typing import Any, Dict, List, Optional
import os
import uuid
import time
import json
from .schema import (
    PackageComponent,
    PackageComponentItem,
    PackageStatus,
    SubmissionPackage,
    CoverLetter,
    AuthorStatement,
    ConflictStatement,
)


def _generate_cover_letter_text(
    journal_name: str,
    editor_name: str,
    manuscript_title: str,
    authors: List[str],
    key_findings: str,
    significance: str,
) -> str:
    author_list = ", ".join(authors) if authors else "the authors"
    findings = key_findings or "The key findings of this research are presented in the attached manuscript."
    sig = significance or "This work contributes to the field and we believe it would be of interest to your readership."

    return f"""Dear {editor_name or 'Editor-in-Chief'},

We are pleased to submit our manuscript entitled "{manuscript_title}" for consideration for publication in {journal_name or 'your journal'}.

On behalf of {author_list}, I confirm that this manuscript has not been published elsewhere and is not under consideration by another journal. All authors have approved the manuscript and agree with its submission.

{findings}

{sig}

We believe this work meets the scope and standards of {journal_name or 'your journal'} and would benefit your readership.

Thank you for considering our submission.

Sincerely,
{author_list}
"""


def _generate_author_statement_text(
    manuscript_title: str,
    authors: List[str],
    contributions: Dict[str, str],
) -> str:
    lines = [
        f"Author Contribution Statement for \"{manuscript_title}\"",
        "",
        "All authors contributed to this research and manuscript preparation.",
        "",
    ]

    if contributions:
        for author, contribution in contributions.items():
            lines.append(f"{author}: {contribution}")
    else:
        for author in authors:
            lines.append(f"{author}: Contributed to research design, data analysis, and manuscript preparation.")

    lines.extend([
        "",
        "All authors reviewed and approved the final manuscript.",
    ])

    return "\n".join(lines)


def _generate_conflict_statement_text(
    manuscript_title: str,
    authors: List[str],
    conflicts: List[str],
) -> str:
    if conflicts:
        conflict_text = "The following conflicts of interest have been declared:\n" + "\n".join(
            f"- {c}" for c in conflicts
        )
    else:
        conflict_text = "The authors declare no conflicts of interest."

    return f"""Conflict of Interest Statement for "{manuscript_title}"

{conflict_text}

All authors have completed the ICMJE Conflict of Interest Disclosure Form.
"""


def _generate_compliance_report_text(
    compliance_report: Optional[Dict],
    journal_name: str,
) -> str:
    if not compliance_report:
        return f"Compliance Report for {journal_name}\n\nNo compliance analysis has been performed."

    score = compliance_report.get("score", {})
    issues = compliance_report.get("issues", [])

    lines = [
        f"Compliance Report for {journal_name}",
        f"Overall Score: {score.get('overall', 0)}%",
        "",
        "Check Results:",
    ]

    for issue in issues:
        status = issue.get("status", "unknown")
        message = issue.get("message", "")
        lines.append(f"  [{status.upper()}] {message}")

    lines.extend([
        "",
        f"Checks Performed: {compliance_report.get('checks_performed', 0)}",
        f"Checks Passed: {compliance_report.get('checks_passed', 0)}",
        f"Checks Failed: {compliance_report.get('checks_failed', 0)}",
    ])

    return "\n".join(lines)


def _generate_review_report_text(
    review_report: Optional[Dict],
    journal_name: str,
) -> str:
    if not review_report:
        return f"Reviewer Report for {journal_name}\n\nNo review analysis has been performed."

    readiness = review_report.get("publication_readiness", {})
    strengths = review_report.get("strengths", [])
    weaknesses = review_report.get("weaknesses", [])
    suggestions = review_report.get("improvement_suggestions", [])

    lines = [
        f"Reviewer Report for {journal_name}",
        f"Publication Readiness: {readiness.get('overall', 0)}% - {readiness.get('label', 'Unknown')}",
        "",
        "Strengths:",
    ]

    for s in strengths:
        lines.append(f"  + {s.get('title', '')}: {s.get('description', '')}")

    lines.append("")
    lines.append("Weaknesses:")

    for w in weaknesses:
        lines.append(f"  - [{w.get('severity', '').upper()}] {w.get('title', '')}: {w.get('description', '')}")

    lines.append("")
    lines.append("Improvement Suggestions:")

    for suggestion in suggestions:
        lines.append(f"  * {suggestion}")

    return "\n".join(lines)


def _generate_citation_report_text(
    citation_report: Optional[Dict],
    journal_name: str,
) -> str:
    if not citation_report:
        return f"Citation Report for {journal_name}\n\nNo citation analysis has been performed."

    health = citation_report.get("health_score", {})
    issues = citation_report.get("issues", [])

    lines = [
        f"Citation Report for {journal_name}",
        f"Health Score: {health.get('overall', 0)}%",
        f"Total Citations: {citation_report.get('total_citations', 0)}",
        f"Total References: {citation_report.get('total_references', 0)}",
        "",
        "Issues Found:",
    ]

    for issue in issues:
        severity = issue.get("severity", "info")
        message = issue.get("message", "")
        lines.append(f"  [{severity.upper()}] {message}")

    return "\n".join(lines)


def build_submission_package(
    document_id: str,
    journal_id: str,
    journal_name: str,
    template_id: Optional[str],
    components: List[PackageComponent],
    structured_data: Dict[str, Any],
    compliance_report: Optional[Dict] = None,
    review_report: Optional[Dict] = None,
    citation_report: Optional[Dict] = None,
    cover_letter: Optional[CoverLetter] = None,
    author_statement: Optional[AuthorStatement] = None,
    conflict_statement: Optional[ConflictStatement] = None,
    output_dir: str = "submission_packages",
) -> SubmissionPackage:
    start_time = time.time()

    package = SubmissionPackage(
        document_id=document_id,
        journal_id=journal_id,
        journal_name=journal_name,
        template_id=template_id or journal_id,
        status=PackageStatus.GENERATING,
    )

    os.makedirs(output_dir, exist_ok=True)

    component_items: List[PackageComponentItem] = []

    for comp in components:
        item = PackageComponentItem(
            component=comp,
            filename="",
        )

        try:
            if comp == PackageComponent.MANUSCRIPT_DOCX:
                from app.services.formatting.engine import format_document
                from app.services.formatting.schema import ExportType

                fmt_template = template_id or journal_id
                output = format_document(
                    document_id=document_id,
                    structured_data=structured_data,
                    template_id=fmt_template,
                    export_type=ExportType.DOCX,
                    output_dir=output_dir,
                )
                item.filename = os.path.basename(output.file_path)
                item.file_path = output.file_path
                item.file_size = os.path.getsize(output.file_path) if output.file_path else None
                item.status = "completed"

            elif comp == PackageComponent.MANUSCRIPT_PDF:
                from app.services.formatting.engine import format_document
                from app.services.formatting.schema import ExportType

                fmt_template = template_id or journal_id
                output = format_document(
                    document_id=document_id,
                    structured_data=structured_data,
                    template_id=fmt_template,
                    export_type=ExportType.PDF,
                    output_dir=output_dir,
                )
                item.filename = os.path.basename(output.file_path)
                item.file_path = output.file_path
                item.file_size = os.path.getsize(output.file_path) if output.file_path else None
                item.status = "completed"

            elif comp == PackageComponent.COMPLIANCE_REPORT:
                content = _generate_compliance_report_text(compliance_report, journal_name)
                filename = f"{document_id}_compliance_report.txt"
                filepath = os.path.join(output_dir, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                item.filename = filename
                item.file_path = filepath
                item.file_size = os.path.getsize(filepath)
                item.status = "completed"

            elif comp == PackageComponent.REVIEW_REPORT:
                content = _generate_review_report_text(review_report, journal_name)
                filename = f"{document_id}_review_report.txt"
                filepath = os.path.join(output_dir, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                item.filename = filename
                item.file_path = filepath
                item.file_size = os.path.getsize(filepath)
                item.status = "completed"

            elif comp == PackageComponent.CITATION_REPORT:
                content = _generate_citation_report_text(citation_report, journal_name)
                filename = f"{document_id}_citation_report.txt"
                filepath = os.path.join(output_dir, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                item.filename = filename
                item.file_path = filepath
                item.file_size = os.path.getsize(filepath)
                item.status = "completed"

            elif comp == PackageComponent.COVER_LETTER:
                if cover_letter:
                    content = _generate_cover_letter_text(
                        cover_letter.journal_name,
                        cover_letter.editor_name,
                        cover_letter.manuscript_title,
                        cover_letter.authors,
                        cover_letter.key_findings,
                        cover_letter.significance,
                    )
                else:
                    title = structured_data.get("title", "Untitled Manuscript")
                    authors_data = structured_data.get("authors", [])
                    if isinstance(authors_data, list) and len(authors_data) > 0:
                        if isinstance(authors_data[0], dict):
                            author_names = [a.get("name", str(a)) for a in authors_data]
                        else:
                            author_names = [str(a) for a in authors_data]
                    else:
                        author_names = ["the authors"]
                    content = _generate_cover_letter_text(
                        journal_name, "", title, author_names, "", ""
                    )
                filename = f"{document_id}_cover_letter.txt"
                filepath = os.path.join(output_dir, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                item.filename = filename
                item.file_path = filepath
                item.file_size = os.path.getsize(filepath)
                item.status = "completed"

            elif comp == PackageComponent.AUTHOR_STATEMENT:
                if author_statement:
                    content = _generate_author_statement_text(
                        author_statement.manuscript_title,
                        author_statement.authors,
                        author_statement.contributions,
                    )
                else:
                    title = structured_data.get("title", "Untitled Manuscript")
                    authors_data = structured_data.get("authors", [])
                    if isinstance(authors_data, list) and len(authors_data) > 0:
                        if isinstance(authors_data[0], dict):
                            author_names = [a.get("name", str(a)) for a in authors_data]
                        else:
                            author_names = [str(a) for a in authors_data]
                    else:
                        author_names = ["the authors"]
                    content = _generate_author_statement_text(title, author_names, {})
                filename = f"{document_id}_author_statement.txt"
                filepath = os.path.join(output_dir, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                item.filename = filename
                item.file_path = filepath
                item.file_size = os.path.getsize(filepath)
                item.status = "completed"

            elif comp == PackageComponent.CONFLICT_STATEMENT:
                if conflict_statement:
                    content = _generate_conflict_statement_text(
                        conflict_statement.manuscript_title,
                        conflict_statement.authors,
                        conflict_statement.conflicts,
                    )
                else:
                    title = structured_data.get("title", "Untitled Manuscript")
                    authors_data = structured_data.get("authors", [])
                    if isinstance(authors_data, list) and len(authors_data) > 0:
                        if isinstance(authors_data[0], dict):
                            author_names = [a.get("name", str(a)) for a in authors_data]
                        else:
                            author_names = [str(a) for a in authors_data]
                    else:
                        author_names = ["the authors"]
                    content = _generate_conflict_statement_text(title, author_names, [])
                filename = f"{document_id}_conflict_statement.txt"
                filepath = os.path.join(output_dir, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                item.filename = filename
                item.file_path = filepath
                item.file_size = os.path.getsize(filepath)
                item.status = "completed"

        except Exception as e:
            item.status = "failed"
            item.error = str(e)

        component_items.append(item)

    package.components = component_items

    all_completed = all(c.status == "completed" for c in component_items)
    any_failed = any(c.status == "failed" for c in component_items)

    if all_completed:
        package.status = PackageStatus.COMPLETED
    elif any_failed:
        package.status = PackageStatus.FAILED
    else:
        package.status = PackageStatus.COMPLETED

    package.completed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    processing_time_ms = (time.time() - start_time) * 1000
    package.processing_metadata = {
        "processing_time_ms": round(processing_time_ms, 2),
        "components_requested": len(components),
        "components_completed": sum(1 for c in component_items if c.status == "completed"),
        "components_failed": sum(1 for c in component_items if c.status == "failed"),
    }

    return package
