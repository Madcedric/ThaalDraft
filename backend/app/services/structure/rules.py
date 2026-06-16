from typing import Dict, List, Set
from dataclasses import dataclass, field


SECTION_LABELS = {
    "title",
    "authors",
    "abstract",
    "keywords",
    "introduction",
    "background",
    "related_work",
    "literature_review",
    "methods",
    "methodology",
    "materials",
    "materials_and_methods",
    "experimental",
    "experiments",
    "results",
    "findings",
    "analysis",
    "discussion",
    "conclusion",
    "conclusions",
    "acknowledgements",
    "acknowledgments",
    "references",
    "bibliography",
    "appendix",
    "supplementary",
}

HEADING_TO_LABEL: Dict[str, str] = {
    "abstract": "abstract",
    "summary": "abstract",
    "introduction": "introduction",
    "background": "background",
    "related work": "related_work",
    "literature review": "literature_review",
    "methods": "methods",
    "methodology": "methods",
    "materials and methods": "materials_and_methods",
    "materials & methods": "materials_and_methods",
    "experimental": "experimental",
    "experiments": "experimental",
    "results": "results",
    "findings": "results",
    "analysis": "analysis",
    "discussion": "discussion",
    "conclusion": "conclusion",
    "conclusions": "conclusion",
    "acknowledgements": "acknowledgements",
    "acknowledgments": "acknowledgements",
    "references": "references",
    "bibliography": "references",
    "works cited": "references",
    "appendix": "appendix",
    "supplementary material": "supplementary",
    "supplementary information": "supplementary",
}

SECTION_ORDER = [
    "title",
    "authors",
    "abstract",
    "keywords",
    "introduction",
    "background",
    "related_work",
    "literature_review",
    "methods",
    "materials_and_methods",
    "experimental",
    "results",
    "analysis",
    "discussion",
    "conclusion",
    "acknowledgements",
    "references",
    "appendix",
    "supplementary",
]

CONFIDENCE_WEIGHTS = {
    "exact_heading_match": 1.0,
    "normalized_heading_match": 0.95,
    "keyword_match": 0.85,
    "position_heuristic": 0.6,
    "content_analysis": 0.5,
    "format_signal": 0.9,
}


@dataclass
class SectionPattern:
    label: str
    keywords: List[str] = field(default_factory=list)
    position_weight: float = 0.0
    content_indicators: List[str] = field(default_factory=list)


KNOWN_SECTION_PATTERNS: Dict[str, SectionPattern] = {
    "abstract": SectionPattern(
        label="abstract",
        keywords=["abstract", "summary"],
        position_weight=0.9,
        content_indicators=["this paper", "we present", "in this study", "this study"],
    ),
    "introduction": SectionPattern(
        label="introduction",
        keywords=["introduction", "intro", "background"],
        position_weight=0.8,
        content_indicators=["recently", "has been", "previous work", "in this paper"],
    ),
    "methods": SectionPattern(
        label="methods",
        keywords=["method", "methods", "methodology", "materials and methods", "approach", "experimental"],
        position_weight=0.5,
        content_indicators=["we used", "we applied", "dataset", "experiment", "model", "algorithm"],
    ),
    "results": SectionPattern(
        label="results",
        keywords=["results", "findings", "analysis", "evaluation", "experiments"],
        position_weight=0.4,
        content_indicators=["table", "figure", "showed", "achieved", "accuracy", "performance"],
    ),
    "discussion": SectionPattern(
        label="discussion",
        keywords=["discussion", "interpretation"],
        position_weight=0.3,
        content_indicators=["suggests", "indicates", "compared to", "consistent with", "limitation"],
    ),
    "conclusion": SectionPattern(
        label="conclusion",
        keywords=["conclusion", "conclusions", "summary", "final remarks", "closing remarks"],
        position_weight=0.2,
        content_indicators=["in conclusion", "we have shown", "future work", "further research"],
    ),
    "references": SectionPattern(
        label="references",
        keywords=["references", "bibliography", "works cited", "citations"],
        position_weight=0.1,
        content_indicators=["doi:", "http", "vol.", "pp.", "et al."],
    ),
}


DOCX_STYLE_MAP: Dict[str, str] = {
    "title": "title",
    "heading 1": "section",
    "heading 2": "subsection",
    "heading 3": "subsection",
    "heading 4": "subsection",
    "normal": "body",
}


LATEX_COMMAND_MAP: Dict[str, str] = {
    "\\section": "section",
    "\\subsection": "subsection",
    "\\subsubsection": "subsection",
    "\\paragraph": "subsection",
}
