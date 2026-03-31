#!/usr/bin/env python3
"""
Export data in Power BI-optimized format.

Exports clean CSVs with proper data types and pre-computed measures
that make Power BI import seamless. Also creates a summary stats table.

Usage:
    python -m src.database.export_for_powerbi
"""

import os
import sys
import duckdb
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.scraper.config import DATA_PROCESSED, DATABASE_PATH

PBI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "dashboard", "data")


def export_for_powerbi():
    """Export Power BI-ready tables from DuckDB."""
    os.makedirs(PBI_DIR, exist_ok=True)
    conn = duckdb.connect(DATABASE_PATH, read_only=True)

    # ============================================================
    # 1. Fact Jobs — enriched with computed columns
    # ============================================================
    jobs = conn.execute("""
        SELECT
            j.*,
            CASE
                WHEN salary_avg IS NOT NULL THEN 'Yes'
                ELSE 'No'
            END AS has_salary,
            COALESCE(salary_avg, 0) AS salary_avg_filled,
            COUNT(js.skill_id) AS skill_count
        FROM fact_jobs j
        LEFT JOIN job_skills js ON j.job_id = js.job_id
        GROUP BY ALL
    """).fetchdf()

    # Ensure proper types for Power BI
    jobs['date_posted'] = pd.to_datetime(jobs['date_posted'], errors='coerce')
    jobs.to_csv(os.path.join(PBI_DIR, "fact_jobs.csv"), index=False)
    print(f"✅ fact_jobs.csv: {len(jobs)} rows")

    # ============================================================
    # 2. Dim Skills — with demand metrics pre-computed
    # ============================================================
    skill_stats = conn.execute("""
        SELECT
            s.skill_id,
            s.skill_name,
            s.skill_category,
            COUNT(js.job_id) AS job_count,
            ROUND(COUNT(js.job_id) * 100.0 / (SELECT COUNT(*) FROM fact_jobs), 1) AS pct_of_jobs,
            ROUND(AVG(j.salary_avg), 0) AS avg_salary_for_skill
        FROM dim_skills s
        LEFT JOIN job_skills js ON s.skill_id = js.skill_id
        LEFT JOIN fact_jobs j ON js.job_id = j.job_id
        GROUP BY s.skill_id, s.skill_name, s.skill_category
        ORDER BY job_count DESC
    """).fetchdf()

    skill_stats.to_csv(os.path.join(PBI_DIR, "dim_skills.csv"), index=False)
    print(f"✅ dim_skills.csv: {len(skill_stats)} rows")

    # ============================================================
    # 3. Job Skills — bridge table
    # ============================================================
    job_skills = conn.execute("SELECT * FROM job_skills").fetchdf()
    job_skills.to_csv(os.path.join(PBI_DIR, "job_skills.csv"), index=False)
    print(f"✅ job_skills.csv: {len(job_skills)} rows")

    # ============================================================
    # 4. Summary Stats — for KPI cards
    # ============================================================
    summary = conn.execute("""
        SELECT
            COUNT(*) AS total_jobs,
            COUNT(DISTINCT company) AS total_companies,
            COUNT(DISTINCT city) AS total_cities,
            ROUND(AVG(salary_avg), 0) AS avg_salary,
            ROUND(MEDIAN(salary_avg), 0) AS median_salary,
            ROUND(MIN(salary_avg), 0) AS min_salary,
            ROUND(MAX(salary_avg), 0) AS max_salary,
            (SELECT job_category FROM fact_jobs GROUP BY job_category ORDER BY COUNT(*) DESC LIMIT 1) AS top_category,
            (SELECT city FROM fact_jobs GROUP BY city ORDER BY COUNT(*) DESC LIMIT 1) AS top_city
        FROM fact_jobs
        WHERE salary_avg IS NOT NULL
    """).fetchdf()

    summary.to_csv(os.path.join(PBI_DIR, "summary_stats.csv"), index=False)
    print(f"✅ summary_stats.csv: KPI data exported")

    # ============================================================
    # 5. Your Skills — for Fit Score page
    # ============================================================
    my_skills = [
        'python', 'sql', 'pandas', 'numpy', 'docker', 'fastapi', 'git', 'github',
        'machine learning', 'scikit-learn', 'nlp', 'feature engineering',
        'data cleaning', 'data pipeline', 'etl', 'bigquery', 'gcp', 'google cloud',
        'streamlit', 'mlflow', 'dbt', 'excel', 'data quality',
        'exploratory data analysis', 'data visualization', 'github actions',
        'communication', 'collaboration', 'teamwork', 'power bi',
    ]

    fit_df = skill_stats.copy()
    fit_df['you_have'] = fit_df['skill_name'].isin(my_skills).map({True: 'Yes', False: 'No'})
    fit_df['status'] = fit_df['you_have'].map({'Yes': '✅ You Have', 'No': '❌ Gap'})
    fit_df.to_csv(os.path.join(PBI_DIR, "skill_fit.csv"), index=False)
    print(f"✅ skill_fit.csv: {len(fit_df)} rows (with your fit data)")

    conn.close()

    print(f"\n📁 All Power BI data exported to: {PBI_DIR}")
    print(f"   Import these CSVs into Power BI Desktop via Get Data > Text/CSV")


if __name__ == "__main__":
    export_for_powerbi()
