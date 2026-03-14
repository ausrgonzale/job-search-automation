# Job Search Script — Overview & Setup Guide

---

## What the Script Does

### Core Functionality
The script searches multiple job boards simultaneously using a single keyword and location, then delivers results in three formats at once — terminal, CSV, and HTML report.

### Job Sources Included
| Source | What It Covers | API Key Required? |
|---|---|---|
| **RemoteOK** | Remote-only jobs across all industries | No |
| **JSearch (via RapidAPI)** | Aggregates LinkedIn, Indeed, ZipRecruiter, Glassdoor | Yes (free) |
| **Arbeitnow** | Tech/developer-focused jobs, GitHub ecosystem friendly | No |

### Search Features
- Search by job title or keyword (e.g. "Python Developer", "Data Analyst")
- Filter by location (e.g. "Austin, TX") or leave blank for remote/anywhere
- Skips sources gracefully if they are unavailable or missing an API key

### Output: Terminal
- Displays a color-coded table using the `rich` library
- Columns: Title, Company, Location, Source, Date Posted

### Output: CSV File
- Saves a timestamped `.csv` file in the same folder as the script
- Filename format: `jobs_python_developer_20240310_143022.csv`
- Columns: title, company, location, source, posted, url

### Output: HTML Report
- Saves a styled `.html` file with the same timestamp naming
- Includes clickable "Apply" links for each job
- Optionally opens in your browser automatically after the search

### Dynamic Source Management
You can add, remove, or toggle sources without editing the core script logic:

```python
add_source(MyNewSource())           # Add a new source
remove_source("RemoteOK")           # Permanently remove a source
toggle_source("RemoteOK", False)    # Disable temporarily
toggle_source("RemoteOK", True)     # Re-enable
```

---

## Setup Steps

### Step 1 — Install Python dependencies
Open your terminal and run:
```bash
pip install requests rich
```

### Step 2 — Get a free RapidAPI key (for LinkedIn / Indeed / ZipRecruiter)
1. Go to: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
2. Click **Subscribe to Test** and choose the free plan
3. Copy your API key from the dashboard

### Step 3 — Add your API key to the script
Open `job_search.py` and find this line near the top:
```python
RAPIDAPI_KEY = "YOUR_RAPIDAPI_KEY_HERE"
```
Replace `YOUR_RAPIDAPI_KEY_HERE` with your actual key. Save the file.

> **Note:** RemoteOK and Arbeitnow work immediately without any key. Only skip this step if you don't need LinkedIn/Indeed/ZipRecruiter results.

### Step 4 — Run the script
```bash
python job_search.py
```

### Step 5 — Enter your search when prompted
```
Job title / keyword: Python Developer
Location (leave blank for remote/any): Austin, TX
```

The script will search all active sources, print results to the terminal, and save both a CSV and HTML file in the same directory as `job_search.py`.

---

## Adding a Custom Job Source

To plug in any new job board with a public API, create a class like this and add it to the registry:

```python
class MyCustomSource(JobSource):
    name = "My Job Board"

    def search(self, keyword: str, location: str) -> list[dict]:
        # Call your API here
        return [
            self._job(
                title    = "Software Engineer",
                company  = "Acme Corp",
                location = "Remote",
                url      = "https://example.com/apply",
                source   = self.name,
                posted   = "2024-03-10"
            )
        ]

add_source(MyCustomSource())
```

---

## File Output Reference

| File | Description |
|---|---|
| `jobs_<keyword>_<timestamp>.csv` | Spreadsheet-ready results |
| `jobs_<keyword>_<timestamp>.html` | Styled browser report with apply links |
