#!/usr/bin/env python3
"""
Load cleaned CSV data into DuckDB database.

Creates the star schema tables and loads data from the processed CSVs.
Also runs validation queries to verify data integrity.

Usage:
    python -m src.database.load_data
"""

import os
import sys

import duckdb

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.scraper.config import DATA_PROCESSED, DATABASE_PATH


def load_data(db_path: str = None, data_dir: str = None):
    """
    Load processed CSVs into DuckDB.

    1. Creates schema from schema.sql
    2. Loads fact_jobs, dim_skills, job_skills from CSVs
    3. Runs validation queries
    """
    if db_path is None:
        db_path = DATABASE_PATH
    if data_dir is None:
        data_dir = DATA_PROCESSED

    # Remove existing DB for clean load
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"🗑️  Removed existing database: {db_path}")

    conn = duckdb.connect(db_path)
    print(f"📂 Connected to DuckDB: {db_path}")

    # ============================================================
    # 1. Create schema
    # ============================================================
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")
    with open(schema_path, "r") as f:
        schema_sql = f.read()

    # Strip comment lines, then split on semicolons
    lines = [l for l in schema_sql.splitlines() if not l.strip().startswith("--")]
    clean_sql = "\n".join(lines)
    for statement in clean_sql.split(";"):
        stmt = statement.strip()
        if stmt:
            conn.execute(stmt)

    # Verify tables exist
    tables = conn.execute("SHOW TABLES").fetchall()
    print(f"✅ Schema created — tables: {[t[0] for t in tables]}")

    # ============================================================
    # 2. Load data from CSVs
    # ============================================================
    jobs_csv = os.path.join(data_dir, "jobs_cleaned.csv")
    skills_csv = os.path.join(data_dir, "dim_skills.csv")
    job_skills_csv = os.path.join(data_dir, "job_skills.csv")

    # Load fact_jobs
    conn.execute(f"""
        INSERT INTO fact_jobs
        SELECT * FROM read_csv_auto('{jobs_csv}', header=True)
    """)
    job_count = conn.execute("SELECT COUNT(*) FROM fact_jobs").fetchone()[0]
    print(f"📊 Loaded {job_count} jobs into fact_jobs")

    # Load dim_skills
    conn.execute(f"""
        INSERT INTO dim_skills
        SELECT * FROM read_csv_auto('{skills_csv}', header=True)
    """)
    skill_count = conn.execute("SELECT COUNT(*) FROM dim_skills").fetchone()[0]
    print(f"🔧 Loaded {skill_count} skills into dim_skills")

    # Load job_skills
    conn.execute(f"""
        INSERT INTO job_skills
        SELECT * FROM read_csv_auto('{job_skills_csv}', header=True)
    """)
    pair_count = conn.execute("SELECT COUNT(*) FROM job_skills").fetchone()[0]
    print(f"🔗 Loaded {pair_count} job-skill pairs into job_skills")

    # ============================================================
    # 3. Validation queries
    # ============================================================
    print("\n" + "=" * 60)
    print("📋 VALIDATION RESULTS")
    print("=" * 60)

    # Table counts
    print(f"\n📊 Table row counts:")
    print(f"   fact_jobs:   {job_count}")
    print(f"   dim_skills:  {skill_count}")
    print(f"   job_skills:  {pair_count}")

    # Jobs by category
    print(f"\n📊 Jobs by category:")
    result = conn.execute("""
        SELECT job_category, COUNT(*) AS cnt
        FROM fact_jobs
        GROUP BY job_category
        ORDER BY cnt DESC
    """).fetchall()
    for row in result:
        print(f"   {row[0]}: {row[1]}")

    # Top 10 skills
    print(f"\n🏆 Top 10 skills:")
    result = conn.execute("SELECT * FROM v_skill_demand LIMIT 10").fetchall()
    for row in result:
        print(f"   {row[0]} ({row[1]}): {row[2]} jobs ({row[3]}%)")

    # Salary by category
    print(f"\n💰 Salary by category:")
    result = conn.execute("SELECT * FROM v_salary_by_category").fetchall()
    for row in result:
        if row[2]:
            print(f"   {row[0]}: avg €{row[2]:,.0f} ({row[1]} jobs)")

    # Jobs by city
    print(f"\n📍 Jobs by city:")
    result = conn.execute("SELECT * FROM v_jobs_by_city LIMIT 8").fetchall()
    for row in result:
        salary_str = f", avg €{row[2]:,.0f}" if row[2] else ""
        print(f"   {row[0]}: {row[1]} jobs{salary_str}")

    print("\n" + "=" * 60)
    print(f"✅ Database loaded and validated: {db_path}")
    print("=" * 60)

    conn.close()


if __name__ == "__main__":
    load_data()
