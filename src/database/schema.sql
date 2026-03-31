-- ============================================================
-- Ireland Jobs Dashboard - Database Schema
-- Star Schema: fact_jobs + dim_skills + job_skills
-- Database: DuckDB
-- ============================================================

-- Drop tables if they exist (for re-runs)
DROP TABLE IF EXISTS job_skills;
DROP TABLE IF EXISTS dim_skills;
DROP TABLE IF EXISTS fact_jobs;

-- ============================================================
-- Fact Table: Jobs
-- ============================================================
CREATE TABLE fact_jobs (
    job_id          INTEGER PRIMARY KEY,
    job_title       VARCHAR,
    job_category    VARCHAR(50),
    company         VARCHAR(200),
    location        VARCHAR(200),
    city            VARCHAR(50),
    work_model      VARCHAR(20),
    seniority       VARCHAR(30),
    salary_min      DECIMAL,
    salary_max      DECIMAL,
    salary_avg      DECIMAL,
    salary_text     VARCHAR(100),
    description     TEXT,
    date_posted     DATE,
    url             VARCHAR(500),
    source          VARCHAR(50)
);

-- ============================================================
-- Dimension Table: Skills
-- ============================================================
CREATE TABLE dim_skills (
    skill_id        INTEGER PRIMARY KEY,
    skill_name      VARCHAR(100),
    skill_category  VARCHAR(50)
);

-- ============================================================
-- Junction Table: Job ↔ Skill (many-to-many)
-- ============================================================
CREATE TABLE job_skills (
    job_id          INTEGER REFERENCES fact_jobs(job_id),
    skill_id        INTEGER REFERENCES dim_skills(skill_id),
    PRIMARY KEY (job_id, skill_id)
);

-- ============================================================
-- Useful Views
-- ============================================================

-- Skills ranked by demand
CREATE OR REPLACE VIEW v_skill_demand AS
SELECT
    s.skill_name,
    s.skill_category,
    COUNT(*) AS job_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(DISTINCT job_id) FROM job_skills), 1) AS pct_of_jobs
FROM job_skills js
JOIN dim_skills s ON js.skill_id = s.skill_id
GROUP BY s.skill_name, s.skill_category
ORDER BY job_count DESC;

-- Average salary by category
CREATE OR REPLACE VIEW v_salary_by_category AS
SELECT
    job_category,
    COUNT(*) AS job_count,
    ROUND(AVG(salary_avg), 0) AS avg_salary,
    ROUND(MIN(salary_min), 0) AS min_salary,
    ROUND(MAX(salary_max), 0) AS max_salary
FROM fact_jobs
WHERE salary_avg IS NOT NULL
GROUP BY job_category
ORDER BY avg_salary DESC;

-- Jobs by city
CREATE OR REPLACE VIEW v_jobs_by_city AS
SELECT
    city,
    COUNT(*) AS job_count,
    ROUND(AVG(salary_avg), 0) AS avg_salary
FROM fact_jobs
GROUP BY city
ORDER BY job_count DESC;
