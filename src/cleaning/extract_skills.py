#!/usr/bin/env python3
"""
Skill extraction from job descriptions.

Parses job descriptions using a keyword dictionary to identify
required skills and tools, then outputs a job-skill mapping table.

Usage:
    python -m src.cleaning.extract_skills
"""

import os
import sys
import re
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.scraper.config import load_skill_keywords, DATA_PROCESSED


def extract_skills_from_text(text: str, skill_dict: dict) -> list[dict]:
    """
    Extract skills from a text by matching against the keyword dictionary.

    Returns a list of dicts: [{"skill_name": ..., "skill_category": ...}, ...]
    """
    if not isinstance(text, str) or not text.strip():
        return []

    text_lower = text.lower()
    found_skills = []
    seen = set()

    for category, keywords in skill_dict.items():
        for keyword in keywords:
            # Use word boundary matching for short keywords to avoid false positives
            if len(keyword) <= 3:
                pattern = r"\b" + re.escape(keyword) + r"\b"
                if re.search(pattern, text_lower):
                    if keyword not in seen:
                        found_skills.append({
                            "skill_name": keyword,
                            "skill_category": category,
                        })
                        seen.add(keyword)
            else:
                if keyword in text_lower and keyword not in seen:
                    found_skills.append({
                        "skill_name": keyword,
                        "skill_category": category,
                    })
                    seen.add(keyword)

    return found_skills


def build_skill_tables(jobs_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Build the dim_skills and job_skills tables from cleaned job data.

    Args:
        jobs_df: Cleaned jobs DataFrame with 'job_id' and 'description' columns.

    Returns:
        (dim_skills_df, job_skills_df)
    """
    skill_dict = load_skill_keywords()

    # Collect all unique skills and job-skill pairs
    all_skills = {}  # skill_name -> {skill_id, skill_category}
    job_skill_pairs = []
    skill_id_counter = 1

    for _, row in jobs_df.iterrows():
        job_id = row["job_id"]
        description = row.get("description", "")

        # Also search in the title for additional context
        title = row.get("job_title", "")
        combined_text = f"{title} {description}"

        skills = extract_skills_from_text(combined_text, skill_dict)

        for skill in skills:
            skill_name = skill["skill_name"]

            # Add to dimension table if new
            if skill_name not in all_skills:
                all_skills[skill_name] = {
                    "skill_id": skill_id_counter,
                    "skill_name": skill_name,
                    "skill_category": skill["skill_category"],
                }
                skill_id_counter += 1

            # Add job-skill relationship
            job_skill_pairs.append({
                "job_id": job_id,
                "skill_id": all_skills[skill_name]["skill_id"],
            })

    # Build DataFrames
    dim_skills = pd.DataFrame(list(all_skills.values()))
    job_skills = pd.DataFrame(job_skill_pairs).drop_duplicates()

    print(f"🔧 Extracted {len(dim_skills)} unique skills across {len(job_skills)} job-skill pairs")
    print(f"📊 Skills by category:\n{dim_skills['skill_category'].value_counts().to_string()}")

    return dim_skills, job_skills


def run_skill_extraction(input_path: str = None, output_dir: str = None):
    """
    Run the skill extraction pipeline.

    Reads cleaned jobs, extracts skills, saves dim_skills and job_skills CSVs.
    """
    if input_path is None:
        input_path = os.path.join(DATA_PROCESSED, "jobs_cleaned.csv")
    if output_dir is None:
        output_dir = DATA_PROCESSED

    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("🔍 STARTING SKILL EXTRACTION")
    print("=" * 60)

    # Load cleaned jobs
    jobs_df = pd.read_csv(input_path, encoding="utf-8")
    print(f"📥 Loaded {len(jobs_df)} cleaned jobs")

    # Extract skills
    dim_skills, job_skills = build_skill_tables(jobs_df)

    # Save
    dim_skills_path = os.path.join(output_dir, "dim_skills.csv")
    job_skills_path = os.path.join(output_dir, "job_skills.csv")

    dim_skills.to_csv(dim_skills_path, index=False, encoding="utf-8")
    job_skills.to_csv(job_skills_path, index=False, encoding="utf-8")

    # Top skills summary
    skill_counts = (
        job_skills.merge(dim_skills, on="skill_id")
        .groupby("skill_name")
        .size()
        .sort_values(ascending=False)
        .head(15)
    )
    print(f"\n🏆 Top 15 skills:\n{skill_counts.to_string()}")

    print("=" * 60)
    print(f"✅ Skill extraction complete:")
    print(f"   dim_skills: {len(dim_skills)} skills → {dim_skills_path}")
    print(f"   job_skills: {len(job_skills)} pairs → {job_skills_path}")
    print("=" * 60)


if __name__ == "__main__":
    run_skill_extraction()
