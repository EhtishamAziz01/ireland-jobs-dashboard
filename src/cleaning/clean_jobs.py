#!/usr/bin/env python3
"""
Data cleaning pipeline for job listings.

Handles:
- Deduplication (same title + company + location)
- Job title standardization into categories
- Location parsing and city extraction
- Salary normalization (annualized)
- Seniority inference from title
- Data quality checks

Usage:
    python -m src.cleaning.clean_jobs
"""

import os
import sys
import re
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.scraper.config import TITLE_CATEGORIES, CITY_MAPPINGS, DATA_RAW, DATA_PROCESSED


def load_raw_data(filepath: str = None) -> pd.DataFrame:
    """Load raw job data from CSV."""
    if filepath is None:
        filepath = os.path.join(DATA_RAW, "jobs_raw.csv")

    df = pd.read_csv(filepath, encoding="utf-8")
    print(f"📥 Loaded {len(df)} raw job listings from {filepath}")
    return df


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate job listings based on title + company + location."""
    before = len(df)
    df = df.drop_duplicates(subset=["job_title", "company", "location"], keep="first")
    removed = before - len(df)
    print(f"🔄 Deduplication: removed {removed} duplicates ({len(df)} remaining)")
    return df.reset_index(drop=True)


def standardize_titles(df: pd.DataFrame) -> pd.DataFrame:
    """
    Map raw job titles to standardized categories.
    Adds a 'job_category' column.
    """
    def categorize(title: str) -> str:
        if not isinstance(title, str):
            return "Other"
        title_lower = title.lower()
        for category, keywords in TITLE_CATEGORIES.items():
            for keyword in keywords:
                if keyword in title_lower:
                    return category
        return "Other"

    df["job_category"] = df["job_title"].apply(categorize)

    # Log distribution
    dist = df["job_category"].value_counts()
    print(f"📊 Title categories:\n{dist.to_string()}")
    return df


def parse_locations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract standardized city name from location strings.
    Adds 'city' and 'work_model' (On-site/Remote/Hybrid) columns.
    """
    def extract_city(location: str) -> str:
        if not isinstance(location, str):
            return "Unknown"
        loc_lower = location.lower()
        for key, city in CITY_MAPPINGS.items():
            if key in loc_lower:
                return city
        return "Other"

    def extract_work_model(location: str) -> str:
        if not isinstance(location, str):
            return "On-site"
        loc_lower = location.lower()
        if "remote" in loc_lower:
            return "Remote"
        elif "hybrid" in loc_lower:
            return "Hybrid"
        return "On-site"

    df["city"] = df["location"].apply(extract_city)
    df["work_model"] = df["location"].apply(extract_work_model)

    print(f"📍 City distribution:\n{df['city'].value_counts().head(10).to_string()}")
    return df


def normalize_salaries(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure salaries are annualized floats.
    Adds 'salary_avg' column.
    """
    df["salary_min"] = pd.to_numeric(df["salary_min"], errors="coerce")
    df["salary_max"] = pd.to_numeric(df["salary_max"], errors="coerce")

    df["salary_avg"] = df[["salary_min", "salary_max"]].mean(axis=1)

    has_salary = df["salary_avg"].notna().sum()
    total = len(df)
    print(f"💰 Salary data available: {has_salary}/{total} ({has_salary/total*100:.0f}%)")

    return df


def infer_seniority(df: pd.DataFrame) -> pd.DataFrame:
    """
    Infer seniority from job title if not already set.
    """
    def infer(row):
        if pd.notna(row.get("seniority")) and row["seniority"]:
            return row["seniority"]
        title = str(row.get("job_title", "")).lower()
        if any(kw in title for kw in ["junior", "jr", "entry", "graduate", "grad"]):
            return "Junior"
        elif any(kw in title for kw in ["senior", "sr", "lead", "principal", "staff"]):
            return "Senior"
        elif any(kw in title for kw in ["mid", "intermediate"]):
            return "Mid-Level"
        return "Not Specified"

    df["seniority"] = df.apply(infer, axis=1)
    print(f"🎯 Seniority distribution:\n{df['seniority'].value_counts().to_string()}")
    return df


def add_job_id(df: pd.DataFrame) -> pd.DataFrame:
    """Add a unique job_id column."""
    df.insert(0, "job_id", range(1, len(df) + 1))
    return df


def clean_text_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Clean whitespace and encoding issues in text fields."""
    text_cols = ["job_title", "company", "location", "description"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace("nan", None)
    return df


def run_cleaning_pipeline(input_path: str = None, output_dir: str = None) -> pd.DataFrame:
    """
    Execute the full cleaning pipeline and save results.

    Returns the cleaned DataFrame.
    """
    if output_dir is None:
        output_dir = DATA_PROCESSED
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("🧹 STARTING DATA CLEANING PIPELINE")
    print("=" * 60)

    # Load
    df = load_raw_data(input_path)

    # Clean
    df = clean_text_fields(df)
    df = deduplicate(df)
    df = standardize_titles(df)
    df = parse_locations(df)
    df = normalize_salaries(df)
    df = infer_seniority(df)
    df = add_job_id(df)

    # Select and order columns for output
    output_cols = [
        "job_id", "job_title", "job_category", "company", "location",
        "city", "work_model", "seniority", "salary_min", "salary_max",
        "salary_avg", "salary_text", "description", "date_posted",
        "url", "source",
    ]
    df = df[[c for c in output_cols if c in df.columns]]

    # Save
    output_path = os.path.join(output_dir, "jobs_cleaned.csv")
    df.to_csv(output_path, index=False, encoding="utf-8")

    print("=" * 60)
    print(f"✅ Cleaning complete: {len(df)} jobs saved to {output_path}")
    print(f"   Columns: {list(df.columns)}")
    print("=" * 60)

    return df


if __name__ == "__main__":
    run_cleaning_pipeline()
