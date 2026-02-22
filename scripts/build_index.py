"""
build_index.py — Standalone script to build the ChromaDB vector index.

Usage:
    python scripts/build_index.py [--naac-dir PATH] [--mvsr-dir PATH]
                                  [--naac-version VERSION] [--mvsr-year YEAR]

Run this once after placing your documents in:
    data/naac_requirements/criterion_<N>/
    data/mvsr_evidence/<category>/
"""

import argparse
import sys
import os

# Ensure the project root is on the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ingestion.ingest import run_full_ingestion


def main():
    parser = argparse.ArgumentParser(
        description="Build ChromaDB vector index from NAAC and MVSR documents."
    )
    parser.add_argument(
        "--naac-dir",
        default="data/naac_requirements",
        help="Root directory containing NAAC requirement PDFs (default: data/naac_requirements)",
    )
    parser.add_argument(
        "--mvsr-dir",
        default="data/mvsr_evidence",
        help="Root directory containing MVSR evidence PDFs (default: data/mvsr_evidence)",
    )
    parser.add_argument(
        "--naac-version",
        default="2025",
        help="NAAC framework version label to tag documents with (default: 2025)",
    )
    parser.add_argument(
        "--mvsr-year",
        type=int,
        default=2024,
        help="Year label for MVSR evidence documents (default: 2024)",
    )
    args = parser.parse_args()

    print(f"Building index …")
    print(f"  NAAC dir  : {args.naac_dir}")
    print(f"  MVSR dir  : {args.mvsr_dir}")
    print(f"  NAAC ver  : {args.naac_version}")
    print(f"  MVSR year : {args.mvsr_year}")
    print()

    counts = run_full_ingestion(
        naac_dir=args.naac_dir,
        mvsr_dir=args.mvsr_dir,
        naac_version=args.naac_version,
        mvsr_year=args.mvsr_year,
    )

    print()
    print("Index build complete:")
    print(f"  NAAC chunks ingested : {counts['naac_chunks']}")
    print(f"  MVSR chunks ingested : {counts['mvsr_chunks']}")


if __name__ == "__main__":
    main()
