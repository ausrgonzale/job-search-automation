import os
import csv
import html
import argparse
import requests
import pathlib
from datetime import datetime
from dotenv import load_dotenv

# ------------------------------------------------
# LOAD ENVIRONMENT
# ------------------------------------------------

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

if not RAPIDAPI_KEY:
    print("ERROR: RAPIDAPI_KEY environment variable not set")
    exit()

# ------------------------------------------------
# CONFIG
# ------------------------------------------------

REPORT_DIR = "reports"
PREVIOUS_FILE = "previous_jobs.csv"

os.makedirs(REPORT_DIR, exist_ok=True)

session = requests.Session()

# ------------------------------------------------
# ROLE EXPANSION
# ------------------------------------------------

MANAGER_ROLES = [
    "QA Manager",
    "Quality Engineering Manager",
    "Test Manager",
    "Automation Manager",
    "SDET Manager",
    "QE Manager"
]

ROLE_EXPANSION = {
    "qa manager": MANAGER_ROLES,
    "test manager": MANAGER_ROLES,
    "qe manager": MANAGER_ROLES
}

def expand_roles(role):

    role_key = role.lower().strip()

    roles = ROLE_EXPANSION.get(role_key)

    if roles:
        return roles

    return [role]

# ------------------------------------------------
# CLI INPUT
# ------------------------------------------------

parser = argparse.ArgumentParser(description="Job Search Automation")

parser.add_argument(
    "--role",
    required=True,
    help="Job role to search (example: QA Manager)"
)

parser.add_argument(
    "--location",
    default="Remote",
    help="Comma separated locations (example: Remote,Austin TX)"
)

args = parser.parse_args()

base_role = args.role.strip()
locations = [l.strip() for l in args.location.split(",")]

roles = expand_roles(base_role)

print("\nSearching roles:")
for r in roles:
    print(" ", r)

# ------------------------------------------------
# LOAD PREVIOUS JOBS
# ------------------------------------------------

previous_jobs = set()

if os.path.exists(PREVIOUS_FILE):

    with open(PREVIOUS_FILE, newline="", encoding="utf8") as f:

        reader = csv.DictReader(f)

        for row in reader:
            key = row["Title"] + row["Company"]
            previous_jobs.add(key)

# ------------------------------------------------
# COLLECT JOBS
# ------------------------------------------------

jobs = []

url = "https://jsearch.p.rapidapi.com/search"

headers = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
}

for search_role in roles:
    for location in locations:

        params = {
            "query": f"{search_role} in {location}",
            "num_pages": "3"
        }

        try:

            r = session.get(url, headers=headers, params=params, timeout=30)

            data = r.json()

            results = data.get("data", [])

            print(f"JSearch {search_role} ({location}): {len(results)} jobs")

            for j in results:

                job = {
                    "title": j.get("job_title",""),
                    "company": j.get("employer_name",""),
                    "city": j.get("job_city",""),
                    "state": j.get("job_state",""),
                    "source": j.get("job_publisher",""),
                    "posted": j.get("job_posted_at_datetime_utc"),
                    "url": j.get("job_apply_link","")
                }

                key = job["title"] + job["company"]

                job["is_new"] = key not in previous_jobs

                jobs.append(job)

        except Exception as e:
            print("JSearch error:", e)

# ------------------------------------------------
# DEDUPLICATION
# ------------------------------------------------

unique = []
seen = set()

for job in jobs:

    key = job["title"] + job["company"]

    if key not in seen:
        seen.add(key)
        unique.append(job)

jobs = unique

print("\nUnique jobs:", len(jobs))

# ------------------------------------------------
# SORT BY DATE
# ------------------------------------------------

jobs.sort(
    key=lambda j: j.get("posted") or "",
    reverse=True
)

# ------------------------------------------------
# BUILD HTML ROWS
# ------------------------------------------------

rows = ""

for job in jobs:

    posted_raw = job.get("posted")
    posted = str(posted_raw)[:10] if posted_raw else ""

    location_display = ", ".join(filter(None,[job["city"],job["state"]]))

    row_style = " style='background-color:#d4f7d4'" if job.get("is_new") else ""

    rows += f"""
<tr{row_style}>
<td>{html.escape(job['title'])}</td>
<td>{html.escape(job['company'])}</td>
<td>{location_display}</td>
<td>{job['source']}</td>
<td>{posted}</td>
<td><a href="{job['url']}">Apply</a></td>
</tr>
"""

# ------------------------------------------------
# BUILD HTML REPORT
# ------------------------------------------------

new_count = sum(1 for j in jobs if j.get("is_new"))

html_doc = f"""
<html>
<body>

<h2>QA Leadership Job Search Report</h2>

<p>Total Jobs Found: {len(jobs)}</p>
<p>New Jobs Since Last Run: {new_count}</p>
<p>Search Role: {base_role}</p>
<p>Locations: {", ".join(locations)}</p>

<table border=1 cellpadding="6" cellspacing="0">

<tr>
<th>Title</th>
<th>Company</th>
<th>Location</th>
<th>Source</th>
<th>Posted</th>
<th>Link</th>
</tr>

{rows}

</table>

</body>
</html>
"""

filename = os.path.join(
    REPORT_DIR,
    f"jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
)

with open(filename,"w",encoding="utf8") as f:
    f.write(html_doc)

# ------------------------------------------------
# CSV EXPORT
# ------------------------------------------------

csvfile = filename.replace(".html",".csv")

with open(csvfile,"w",newline="",encoding="utf8") as f:

    writer = csv.writer(f)

    writer.writerow([
        "Title","Company","City","State","Source","Posted","Apply Link"
    ])

    for job in jobs:

        posted_raw = job.get("posted")
        posted = str(posted_raw)[:10] if posted_raw else ""

        writer.writerow([
            job["title"],
            job["company"],
            job["city"],
            job["state"],
            job["source"],
            posted,
            job["url"]
        ])

print("\nReport written:", filename)
print("CSV export:", csvfile)

# ------------------------------------------------
# SAVE CURRENT JOBS FOR NEXT RUN
# ------------------------------------------------

with open(PREVIOUS_FILE, "w", newline="", encoding="utf8") as f:

    writer = csv.writer(f)

    writer.writerow(["Title", "Company"])

    for job in jobs:
        writer.writerow([job["title"], job["company"]])

print("Saved job history for next run.")
print("\n\n\nScript execution completed!")