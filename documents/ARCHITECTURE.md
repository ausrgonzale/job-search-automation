Job Search Automation Tool
System Architecture & Design Document

Author: Ron Gonzalez
Purpose: Automated job discovery, filtering, ranking, and reporting.

1. System Overview

The Job Search Automation Tool is a Python-based automation system that searches multiple job boards, aggregates results, filters them based on user criteria, ranks results by relevance, and generates reports.

The system is designed to support automated job discovery workflows while demonstrating modern automation engineering practices including:

modular architecture

concurrent API execution

extensible source providers

automated filtering

data persistence

AI-assisted ranking

scheduled automation

2. High-Level System Architecture
flowchart TD

A[User Runs Script] --> B[Input Collection]

B --> C[Search Controller]

C --> D1[RemoteOK Source]
C --> D2[JSearch API Source]
C --> D3[Arbeitnow Source]

D1 --> E[Job Results]
D2 --> E
D3 --> E

E --> F[Result Aggregation]

F --> G[Deduplication Engine]

G --> H[Filtering Layer]

H --> H1[Keyword Matching]
H --> H2[Location Filter]
H --> H3[Work Environment Filter]
H --> H4[Job Type Filter]
H --> H5[Date Filter (Last 48 Hours)]

H5 --> I[Relevance Scoring Engine]

I --> J[Final Job List]

J --> K[Terminal Table Output]

J --> L[HTML Report Generator]

L --> M[Browser View]

J --> N[(SQLite Job Database)]
3. System Components
3.1 Main Controller

Entry point: main() function.

Responsibilities:

Collect user input

Initialize search parameters

Trigger multi-source job searches

Apply filtering and ranking

Generate output reports

Input order:

Job Description(s)

Job Location

Work Environment (remote / hybrid / onsite)

Job Type (full-time / contract / part-time)

4. Source Provider Architecture

The system uses a provider-based architecture.

Each job board is implemented as a subclass of JobSource.

class JobSource:
    def search(self, keyword, location):
        pass

Providers return normalized job objects.

Example structure:

{
 title,
 company,
 location,
 url,
 source,
 posted
}
5. Job Data Sources
RemoteOK Provider

API:
https://remoteok.com/api

Characteristics:

Remote-first job board

Free public API

No authentication required

JSearch Provider

API aggregator via RapidAPI.

Aggregates results from:

LinkedIn

Indeed

ZipRecruiter

Glassdoor

Authentication required:

RAPIDAPI_KEY
Arbeitnow Provider

API:

https://www.arbeitnow.com/api/job-board-api

Focus:

tech jobs

startup jobs

6. Parallel Search Execution

The system uses concurrent execution.

Technology:

ThreadPoolExecutor

Purpose:

Run API calls simultaneously

Reduce overall search time

Avoid blocking operations

Execution model:

Search Controller
   ├── RemoteOK Search
   ├── JSearch API Search
   └── Arbeitnow Search
7. Result Aggregation

Results from all providers are merged into a unified list.

Key steps:

Collect results from each provider

Normalize job data

Aggregate results

8. Deduplication Engine

Duplicate jobs are removed using unique identifiers.

Primary key:

job URL

Fallback key:

title + company

This ensures identical listings across multiple job boards appear only once.

9. Filtering Engine

After aggregation, results pass through the filtering layer.

Keyword Matching

Phrase-first matching prevents partial matches.

Example:

Quality Engineering Manager

will not return unrelated titles such as:

Account Manager
Engineering Representative
Location Filtering

Matches jobs based on user-provided location.

Example:

Texas
Austin
Remote
Work Environment Filtering

Supported values:

remote

hybrid

onsite

Job Type Filtering

Supported values:

full-time

contract

part-time

Date Filtering

Jobs are limited to those posted within the last 48 hours.

Logic:

datetime.now() - timedelta(days=2)
10. AI Relevance Scoring Engine

After filtering, jobs are ranked using a scoring algorithm.

Purpose:

prioritize the most relevant job listings

surface leadership roles

improve result quality

Example scoring factors:

Factor	Points
Keyword match	+5
Manager role	+3
Director role	+2
Location match	+2

Example scoring function:

def score_job(job, keywords):

    score = 0
    text = f"{job['title']} {job['company']} {job['location']}".lower()

    for keyword in keywords:
        if keyword.lower() in text:
            score += 5

    if "manager" in text:
        score += 3

    if "director" in text:
        score += 2

    return score

Jobs are sorted by score.

11. Data Persistence Layer

The system supports persistent job storage using SQLite.

Purpose:

track historical job discoveries

prevent duplicate listings across runs

track application status

Database file:

jobs.db

Schema:

CREATE TABLE jobs (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 title TEXT,
 company TEXT,
 location TEXT,
 source TEXT,
 url TEXT UNIQUE,
 posted_date TEXT,
 discovered_date TEXT,
 status TEXT DEFAULT 'new'
);

Status options:

new

applied

interested

rejected

12. Output Layer

The system generates two output formats.

Terminal Display

Uses the Rich Python library.

Displays a formatted table including:

Title

Company

Location

Source

Posted Date

HTML Report

A timestamped HTML report is generated.

Example filename:

jobs_20260312_093210.html

Report includes:

job title

company

location

job source

posted date

apply link

13. Scheduled Automation

The tool can be scheduled to run automatically.

Linux / Mac

Using cron:

0 8 * * * python3 job_search.py

Runs daily at 8 AM.

Windows

Using Task Scheduler.

Schedule daily execution of the script.

14. Email Notification System

The script can email job results automatically.

Email includes:

HTML report attachment

job summary

SMTP example:

smtp.gmail.com

Purpose:

deliver daily job search results

eliminate manual script execution

15. Internal Python Architecture
flowchart TD

A[main()] --> B[Input Collection]

B --> C[search_jobs()]

C --> D[ThreadPoolExecutor]

D --> E1[RemoteOK.search()]
D --> E2[JSearch.search()]
D --> E3[Arbeitnow.search()]

E1 --> F[Normalized Job Objects]
E2 --> F
E3 --> F

F --> G[Deduplication Engine]

G --> H[Filtering Engine]

H --> H1[Keyword Matching]
H --> H2[Location Filter]
H --> H3[Environment Filter]
H --> H4[Job Type Filter]
H --> H5[Date Filter]

H5 --> I[Relevance Scoring Engine]

I --> J[Final Job List]

J --> K[Terminal Output]

J --> L[HTML Report]

J --> M[(SQLite Database)]
16. Security Considerations

API keys are managed via environment variables.

Example:

export RAPIDAPI_KEY="your_key"

Benefits:

prevents credentials from being committed to source control

improves deployment security

17. Performance Optimizations
HTTP Connection Pooling

Uses:

requests.Session()

Benefits:

persistent connections

faster API calls

Parallel Execution

Multiple APIs run concurrently.

Benefits:

faster job retrieval

reduced total search time

18. Project Structure

Recommended repository layout:

job-search-automation/

job_search.py
README.md
ARCHITECTURE.md
requirements.txt

database/
    jobs.db

reports/
    jobs_YYYYMMDD.html

diagrams/
    architecture.png
19. Future Enhancements

Potential upgrades:

AI job matching against resume

job recommendation engine

Slack / Teams notifications

web dashboard

job analytics

historical trend analysis

machine learning relevance ranking

20. Target Use Cases

This system supports:

automated job discovery

portfolio automation projects

engineering architecture demonstrations

QA / SDET leadership portfolio examples

End of Document