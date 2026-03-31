#!/usr/bin/env python3
"""
Run the full cleaning pipeline: clean_jobs → extract_skills.

Usage:
    python -m src.cleaning.run_cleaning
    python -m src.cleaning.run_cleaning --input data/raw/jobs_raw.csv
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.cleaning.clean_jobs import run_cleaning_pipeline
from src.cleaning.extract_skills import run_skill_extraction


def main():
    parser = argparse.ArgumentParser(description="Run the full data cleaning pipeline")
    parser.add_argument("--input", type=str, default=None, help="Path to raw jobs CSV")
    parser.add_argument("--output", type=str, default=None, help="Output directory for processed data")
    args = parser.parse_args()

    # Step 1: Clean jobs
    print("\n" + "🟦 " * 20)
    print("STEP 1: CLEANING JOB LISTINGS")
    print("🟦 " * 20 + "\n")
    df = run_cleaning_pipeline(input_path=args.input, output_dir=args.output)

    # Step 2: Extract skills
    print("\n" + "🟩 " * 20)
    print("STEP 2: EXTRACTING SKILLS")
    print("🟩 " * 20 + "\n")
    run_skill_extraction(output_dir=args.output)

    print("\n" + "✅ " * 20)
    print("FULL CLEANING PIPELINE COMPLETE")
    print("✅ " * 20)


if __name__ == "__main__":
    main()
