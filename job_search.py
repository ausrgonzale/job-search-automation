import os
import csv
import html
import argparse
import requests
import webbrowser
import pathlib
from datetime import datetime

# ------------------------------------------------
# CONFIG
# ------------------------------------------------

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

if not RAPIDAPI_KEY:
    print("ERROR: RAPIDAPI_KEY environment variable not set")
    exit()

REPORT_DIR = "reports"
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
    help="Location (example: Remote or Austin TX)"
)

args = parser.parse_args()

base_role = args.role.strip()
###location = args.location.strip() - Remove me it this change works
locations = [l.strip() for l in args.location.split(",")]

roles = expand_roles(base_role)

print("\nSearching roles:")
for r in roles:
    print(" ", r)

jobs = []

# ------------------------------------------------
# JSEARCH (LinkedIn / Indeed / ZipRecruiter)
# ------------------------------------------------

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

            print(f"JSearch {search_role}: {len(results)} jobs")

            for j in results:

                jobs.append({
                    "title": j.get("job_title",""),
                    "company": j.get("employer_name",""),
                    "city": j.get("job_city",""),
                    "state": j.get("job_state",""),
                    "source": j.get("job_publisher",""),
                    "posted": j.get("job_posted_at_datetime_utc"),
                    "url": j.get("job_apply_link","")
                })

        except Exception as e:
            print("JSearch error:", e)


# ------------------------------------------------
# GREENHOUSE JOB BOARDS
# ------------------------------------------------

try:

    boards = session.get(
        "https://boards-api.greenhouse.io/v1/boards",
        timeout=30
    ).json().get("boards",[])

    for board in boards[:100]:

        token = board.get("token")

        try:

            r = session.get(
                f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs",
                timeout=30
            )

            data = r.json().get("jobs",[])

            for job in data:

                title = job.get("title","").lower()

                if not any(word in title for role in roles for word in role.lower().split()):
                    continue

                location_data = job.get("location",{}).get("name","")

                jobs.append({
                    "title": job.get("title",""),
                    "company": board.get("name",""),
                    "city": location_data,
                    "state": "",
                    "source": "Greenhouse",
                    "posted": "",
                    "url": job.get("absolute_url","")
                })

        except:
            continue

    print("Greenhouse scan complete")

except Exception as e:
    print("Greenhouse error:", e)


# ------------------------------------------------
# LEVER JOB BOARDS
# ------------------------------------------------

try:

    lever_data = session.get(
        "https://api.lever.co/v0/postings",
        timeout=30
    ).json()

    for job in lever_data:

        title = job.get("text","").lower()

        if not any(word in title for role in roles for word in role.lower().split()):
            continue

        location_data = job.get("categories",{}).get("location","")

        jobs.append({
            "title": job.get("text",""),
            "company": job.get("company",""),
            "city": location_data,
            "state": "",
            "source": "Lever",
            "posted": "",
            "url": job.get("hostedUrl","")
        })

    print("Lever scan complete")

except Exception as e:
    print("Lever error:", e)


print("\nTotal jobs collected:", len(jobs))

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

print("Unique jobs:", len(jobs))


# ------------------------------------------------
# SORT BY DATE
# ------------------------------------------------

jobs.sort(
    key=lambda j: j.get("posted") or "",
    reverse=True
)

# ------------------------------------------------
# HTML REPORT
# ------------------------------------------------

rows = ""

for job in jobs:

    posted_raw = job.get("posted")
    posted = str(posted_raw)[:10] if posted_raw else ""

    location_display = ", ".join(filter(None,[job["city"],job["state"]]))

    rows += f"""
<tr>
<td>{html.escape(job['title'])}</td>
<td>{html.escape(job['company'])}</td>
<td>{location_display}</td>
<td>{job['source']}</td>
<td>{posted}</td>
<td><a href="{job['url']}">Apply</a></td>
</tr>
"""

html_doc = f"""
<html>
<body>
<h2>QA Leadership Job Search Report</h2>
<p>Total Jobs Found: {len(jobs)}</p>
<p>Search Role: {base_role}</p>
<p>Location: {",".join(locations)}</p>

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
# OPEN REPORT
# ------------------------------------------------

path = pathlib.Path(filename).resolve()

webbrowser.open(path.as_uri())

print(f'\nReports available at: {path}')