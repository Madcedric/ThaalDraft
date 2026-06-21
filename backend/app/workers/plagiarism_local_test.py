"""Local tester for plagiarism check logic.

Runs `check_against_corpus` from `plagiarism_service` with sample texts.
"""
import sys
from pathlib import Path

# Ensure project root is on path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.services import plagiarism_service


def main():
    target = (
        "This study investigates the effects of transformer-based models on natural language tasks. "
        "We evaluate performance across multiple datasets and show substantial improvements."
    )

    corpus = [
        {"id": "doc1", "text": "Transformer-based models improve NLP tasks significantly."},
        {"id": "doc2", "text": "A different paper about biology and gene expression."},
        {"id": "doc3", "text": "This study investigates transformer models and shows improvements across datasets."},
    ]

    results = plagiarism_service.check_against_corpus(target, corpus, top_n=3)
    print("Plagiarism check results:")
    for r in results:
        print(f"- {r['document_id']}: {r['score']:.4f}")


if __name__ == '__main__':
    main()
