# 📊 Data Jobs & Skills Market Dashboard

End-to-end data analytics project analyzing **1,930 real LinkedIn job postings** to uncover trends in the data job market — skills demand, salary benchmarks, and career insights.

## Key Findings

| Metric | Value |
|---|---|
| Jobs Analyzed | 1,930 |
| Unique Companies | 1,172 |
| Skills Extracted | 131 |
| #1 Skill | SQL (30.5%) |
| Avg Salary — Data Scientist | $160,068 |
| Avg Salary — Data Analyst | $110,658 |

## Tech Stack

| Layer | Technology |
|---|---|
| Data Collection | Python, BeautifulSoup, Kaggle API |
| Data Cleaning | Pandas, Regex, Custom NLP |
| Database | DuckDB (Star Schema) |
| Analysis | Jupyter, Plotly, Seaborn |
| Dashboard | Power BI |
| Version Control | Git, GitHub |

## Project Structure

```
├── src/
│   ├── scraper/          # Indeed scraper + Kaggle adapter
│   ├── cleaning/         # Dedup, standardize, skill extraction
│   └── database/         # DuckDB schema + loader + PBI export
├── notebooks/
│   └── 03_eda_analysis.ipynb   # EDA with 20+ Plotly charts
├── dashboard/
│   ├── data/             # Power BI-ready CSVs
│   └── ireland_jobs_theme.json
├── data/
│   └── reference/        # Skill keyword dictionary
└── reports/
    └── analysis_report.md
```

## Data Pipeline

```
LinkedIn (3.3M postings)
    ↓ Filter for data roles
2,000 raw listings
    ↓ Dedup + clean
1,930 cleaned jobs
    ↓ Skill extraction (131 skills)
8,966 job-skill pairs
    ↓ Load into DuckDB
Star Schema (3 tables + 3 views)
    ↓ Export
Power BI Dashboard
```

## Setup & Run

```bash
# Clone and install
git clone https://github.com/EhtishamAziz01/data-jobs-dashboard.git
cd data-jobs-dashboard
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run full pipeline
python -m src.scraper.kaggle_adapter --source linkedin --limit 2000
python -m src.cleaning.run_cleaning
python -m src.database.load_data

# Open analysis notebook
jupyter notebook notebooks/03_eda_analysis.ipynb
```

## Database Schema

```sql
fact_jobs (job_id, job_title, job_category, company, city, salary_avg, ...)
dim_skills (skill_id, skill_name, skill_category)
job_skills (job_id, skill_id)  -- bridge table

-- Analytical views
v_skill_demand    -- skill rankings with % of jobs
v_salary_by_category  -- avg salary per role type
v_jobs_by_city    -- geographic distribution
```

## Analysis Highlights

**Top Skills**: SQL (30.5%) → Excel (30.1%) → Python (23.1%) → Communication (24.3%)

**Salary by Role** (USD):
- Data Scientist: $160K avg
- Data Engineer: $152K avg
- Data Analyst: $111K avg

**Insight**: Upskilling from Data Analyst → Data Engineer yields a ~$42K salary increase on average.

## Author

**Ehtisham Aziz** — B.Sc. Digital Business & Data Science | Le Wagon Data Science Bootcamp

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin)](https://linkedin.com/in/ehtishamaziz)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=flat&logo=github)](https://github.com/EhtishamAziz01)
