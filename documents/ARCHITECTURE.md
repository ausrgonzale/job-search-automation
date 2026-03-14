Job Search Automation Architecture

This document describes the architecture and data flow of the Job Search Automation system.

Overview

The system collects job postings from multiple sources, aggregates them, and generates reports highlighting newly discovered jobs.

Automation is handled via GitHub Actions, allowing the system to run on a schedule.

System Components
Job Search Script
job_search.py

Responsibilities:

Accept command line arguments

Expand leadership role variations

Query external job APIs

Normalize job data

Remove duplicates

Detect newly discovered jobs

Generate reports

External Data Sources

The system integrates with multiple job platforms.

JSearch API

Primary job search API used to retrieve job postings.

Capabilities:

Multi-location search

Keyword matching

Pagination

Greenhouse Job Boards

Scans public Greenhouse job boards for matching roles.

Lever Job Boards

Scans Lever-hosted job postings.

Data Processing Pipeline
User Input
   ↓
Role Expansion
   ↓
API Queries
   ↓
Job Aggregation
   ↓
Deduplication
   ↓
New Job Detection
   ↓
Report Generation
Job Aggregation

Jobs from multiple sources are normalized into a common structure:

{
  title
  company
  city
  state
  source
  posted
  url
}
Duplicate Removal

Duplicates are identified using:

title + company

Only unique jobs are retained.

New Job Detection

Each run compares current results against a stored history file.

previous_jobs.csv

Logic:

if job not in previous run
    mark as NEW

New jobs are highlighted in reports.

Report Generation

Two report formats are produced.

HTML Report

Purpose:

Human readable

highlights new jobs

clickable application links

CSV Export

Purpose:

Data analysis

spreadsheet processing

Persistence

The system stores previously seen jobs in:

previous_jobs.csv

This file enables detection of new postings between runs.

GitHub Actions Automation

Automation is handled by:

.github/workflows/job-search.yml

Workflow process:

Scheduler
   ↓
GitHub Runner
   ↓
Install Python
   ↓
Install Dependencies
   ↓
Run job_search.py
   ↓
Generate Reports
   ↓
Upload Artifacts
   ↓
Persist Job History
Security

API credentials are stored securely using:

GitHub Secrets

Example:

RAPIDAPI_KEY

Secrets are injected into the workflow environment.

Scalability

The system is designed to support additional data sources.

Future integrations could include:

LinkedIn scraping

Indeed APIs

company career pages

Future Architecture Improvements

Potential enhancements include:

notification services (email or Slack)

job ranking based on skill match

AI summarization of job descriptions

dashboard interface

database persistence

Summary

The project demonstrates a complete automation pipeline:

Data Collection
+ Data Processing
+ Report Generation
+ Scheduled Execution

It showcases automation engineering concepts using Python and GitHub Actions.