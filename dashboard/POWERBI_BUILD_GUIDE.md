# 🇮🇪 Power BI Dashboard — Build Guide

Complete step-by-step guide to build the 4-page Ireland Jobs Dashboard in Power BI Desktop.

---

## Step 1: Import Data

1. Open **Power BI Desktop**
2. Click **Get Data** → **Text/CSV**
3. Import these files from `dashboard/data/`:

| File | Table Name | Purpose |
|---|---|---|
| `fact_jobs.csv` | fact_jobs | Main job postings table |
| `dim_skills.csv` | dim_skills | Skills dimension with demand metrics |
| `job_skills.csv` | job_skills | Bridge table (many-to-many) |
| `summary_stats.csv` | summary_stats | KPI card values |
| `skill_fit.csv` | skill_fit | Your skills vs market demand |

4. Click **Transform Data** to open Power Query
5. Verify data types:
   - `date_posted` → Date
   - `salary_min`, `salary_max`, `salary_avg` → Decimal Number
   - `job_id`, `skill_id` → Whole Number
6. Click **Close & Apply**

---

## Step 2: Data Model (Relationships)

Go to **Model View** and create these relationships:

```
fact_jobs.job_id  ──── 1:* ────  job_skills.job_id
dim_skills.skill_id  ──── 1:* ────  job_skills.skill_id
```

Power BI may auto-detect these. If not, drag `job_id` from `fact_jobs` to `job_id` in `job_skills`, and `skill_id` from `dim_skills` to `skill_id` in `job_skills`.

---

## Step 3: DAX Measures

Go to **Report View**, click on `fact_jobs` table, and create these measures:

### Core Measures

```dax
Total Jobs = COUNTROWS(fact_jobs)

Total Companies = DISTINCTCOUNT(fact_jobs[company])

Avg Salary = AVERAGE(fact_jobs[salary_avg])

Median Salary = MEDIAN(fact_jobs[salary_avg])

Jobs With Salary =
    CALCULATE(
        COUNTROWS(fact_jobs),
        NOT(ISBLANK(fact_jobs[salary_avg]))
    )

% With Salary =
    DIVIDE([Jobs With Salary], [Total Jobs], 0) * 100
```

### Skill Measures (create in dim_skills table)

```dax
Skill Job Count = COUNTROWS(job_skills)

Skill % of Jobs =
    DIVIDE(
        COUNTROWS(job_skills),
        CALCULATE(COUNTROWS(fact_jobs), ALL(dim_skills)),
        0
    ) * 100
```

### Fit Score Measures (create in skill_fit table)

```dax
Skills You Have =
    CALCULATE(
        COUNTROWS(skill_fit),
        skill_fit[you_have] = "Yes"
    )

Total Demanded Skills = COUNTROWS(skill_fit)

Fit Score =
    DIVIDE([Skills You Have], [Total Demanded Skills], 0) * 100
```

---

## Step 4: Dashboard Pages

### Color Theme

Use this professional color palette throughout:

| Color | Hex | Use For |
|---|---|---|
| Primary Blue | `#4361EE` | Bars, headers |
| Dark Purple | `#3A0CA3` | Accents |
| Pink | `#F72585` | Highlights, gaps |
| Cyan | `#4CC9F0` | Positive/success |
| Yellow | `#F9C74F` | Warnings |
| Dark BG | `#1A1A2E` | Background (dark mode) |

---

### Page 1: Market Overview 📊

**Layout:** Top KPI row + 4 charts below

| Visual | Type | Fields | Settings |
|---|---|---|---|
| **KPI: Total Jobs** | Card | `[Total Jobs]` | Font 28pt, blue |
| **KPI: Avg Salary** | Card | `[Avg Salary]` | Format as currency |
| **KPI: Companies** | Card | `[Total Companies]` | Font 28pt |
| **KPI: % With Salary** | Card | `[% With Salary]` | Add "%" suffix |
| **Jobs by Category** | Horizontal Bar | Y: `job_category`, X: `[Total Jobs]` | Sort descending, data labels on |
| **Seniority Split** | Donut Chart | Legend: `seniority`, Values: `[Total Jobs]` | Show percentages |
| **Work Model** | Stacked Bar | X: `work_model`, Y: `[Total Jobs]` | Color by work_model |
| **Postings Over Time** | Line Chart | X: `date_posted` (Month), Y: `[Total Jobs]` | Smooth lines |

**Slicers** (add to top or side):
- `job_category` (Dropdown)
- `city` (Dropdown)
- `seniority` (Buttons)
- `work_model` (Buttons)

---

### Page 2: Skills Demand 🔧

| Visual | Type | Fields | Settings |
|---|---|---|---|
| **Top 15 Skills** | Horizontal Bar | Y: `skill_name`, X: `[Skill Job Count]` | Sort desc, data labels, color by `skill_category` |
| **Skills Treemap** | Treemap | Group: `skill_category` → `skill_name`, Values: `[Skill Job Count]` | Auto color |
| **Skill Category Breakdown** | 100% Stacked Bar | X: `job_category` (from fact_jobs via bridge), Y: `[Skill Job Count]`, Legend: `skill_category` | Shows skill mix per role |
| **Skills Table** | Table/Matrix | `skill_name`, `skill_category`, `[Skill Job Count]`, `[Skill % of Jobs]`, `avg_salary_for_skill` | Conditional formatting on job_count |

---

### Page 3: Salary Insights 💰

| Visual | Type | Fields | Settings |
|---|---|---|---|
| **Salary by Category** | Box/Whisker or Clustered Bar | X: `job_category`, Y: `salary_avg` | Filter: `has_salary = "Yes"` |
| **Salary by Seniority** | Grouped Bar | X: `seniority`, Y: `[Avg Salary]` | Color by seniority |
| **Salary by City** | Bar Chart | X: `city`, Y: `[Avg Salary]`, Size: `[Total Jobs]` | Sort by avg salary |
| **Highest Paying Skills** | Horizontal Bar | Y: `skill_name` (from skill_fit), X: `avg_salary_for_skill` | Filter top 15, sort desc |
| **Salary Table** | Matrix | Rows: `job_category`, Columns: `seniority`, Values: `[Median Salary]` | Conditional formatting, heat colors |

---

### Page 4: Your Fit Score ⭐

| Visual | Type | Fields | Settings |
|---|---|---|---|
| **Fit Score Gauge** | Gauge | Value: `[Fit Score]`, Max: 100 | Green/yellow/red bands |
| **Skills You Have** | Card | `[Skills You Have]` | Green color |
| **Total Skills** | Card | `[Total Demanded Skills]` | — |
| **Skills You Have** | Horizontal Bar | Y: `skill_name`, X: `job_count` (from skill_fit) | Filter: `you_have = "Yes"`, sort desc, cyan bars |
| **Skills Gaps** | Horizontal Bar | Y: `skill_name`, X: `job_count` (from skill_fit) | Filter: `you_have = "No"`, sort desc, pink bars |
| **Combined Chart** | Stacked Bar | Y: `skill_name`, X: `job_count`, Legend: `status` | Top 25 only, color: cyan/pink |

---

## Step 5: Polish

1. **Title bar**: Add a text box at the top of each page with the page title + 🇮🇪 emoji
2. **Navigation**: Insert buttons to switch between pages (Insert → Buttons → Navigation)
3. **Tooltips**: Add custom tooltips showing skill details or salary breakdowns
4. **Conditional formatting**: Apply color scales to salary columns in tables
5. **Dark theme** (optional): Format → Theme → select a dark theme, or import custom JSON
6. **Remove chart clutter**: Hide axis labels where obvious, reduce gridlines

---

## Step 6: Publish & Share

1. **Save** as `ireland_jobs_dashboard.pbix` in `dashboard/`
2. **Publish** to Power BI Service (free account): File → Publish → My Workspace
3. **Share the link** — add it to your CV and LinkedIn
4. **Take screenshots** for README: save to `dashboard/screenshots/`

---

## Quick Reference: Power BI Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+Enter` | Apply formula |
| `Ctrl+D` | Duplicate visual |
| `Alt+Click` | Multi-select slicers |
| `Ctrl+Shift+C` | Copy formatting |
| `Ctrl+Shift+V` | Paste formatting |
