"""
job_matcher.py
--------------
PIPELINE STEP 8: Real-Time Job Matching

Fetches live job postings from the Adzuna Jobs API based on:
  - Best matched job role (from Step 5)
  - Location extracted from resume (from Step 3) or user-provided

Adzuna API:
  - Free tier: 10,000 calls/month
  - India endpoint: api.adzuna.com/v1/api/jobs/in/search/1
  - Supports location-based filtering and keyword search

Returns real job listings with title, company, salary, and apply URL.
"""

import os
import requests
from typing import Optional


ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "")
ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api/jobs/in/search/1"


def fetch_jobs(
    job_title: str,
    location: Optional[str] = None,
    results_per_page: int = 8
) -> dict:
    """
    Fetches real job listings from Adzuna for a given role and location.

    Args:
        job_title: Best matched job role from classifier
        location: City/location string (from parser or user input)
        results_per_page: Number of listings to fetch

    Returns:
        dict with job listings and metadata
    """
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        return _mock_jobs(job_title, location)

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": results_per_page,
        "what": job_title,
        "content-type": "application/json",
        "sort_by": "relevance"
    }

    if location:
        params["where"] = location

    try:
        response = requests.get(ADZUNA_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        jobs = []
        for job in data.get("results", []):
            salary_min = job.get("salary_min")
            salary_max = job.get("salary_max")
            salary_str = _format_salary(salary_min, salary_max)

            jobs.append({
                "title": job.get("title", "").strip(),
                "company": job.get("company", {}).get("display_name", "N/A"),
                "location": job.get("location", {}).get("display_name", location or "India"),
                "salary": salary_str,
                "description": job.get("description", "")[:200] + "..." if job.get("description") else "",
                "url": job.get("redirect_url", ""),
                "created": job.get("created", "")[:10],  # Date only
                "source": "Adzuna"
            })

        return {
            "jobs": jobs,
            "total_found": data.get("count", len(jobs)),
            "query": {"role": job_title, "location": location or "India"},
            "status": "success"
        }

    except requests.exceptions.ConnectionError:
        return {
            "jobs": [],
            "status": "error",
            "message": "Could not connect to jobs API. Check your internet connection."
        }
    except requests.exceptions.HTTPError as e:
        return {
            "jobs": [],
            "status": "error",
            "message": f"Jobs API error: {str(e)}"
        }
    except Exception as e:
        return {
            "jobs": [],
            "status": "error",
            "message": f"Unexpected error fetching jobs: {str(e)}"
        }
    response = requests.get(ADZUNA_BASE_URL, params=params, timeout=10)
    response.raise_for_status()
    print("ADZUNA RAW RESPONSE:", response.text[:500])  # ADD THIS LINE
    data = response.json()



def _format_salary(salary_min, salary_max) -> str:
    """Formats salary range into a readable string."""
    if not salary_min and not salary_max:
        return "Not disclosed"
    if salary_min and salary_max:
        return f"₹{int(salary_min):,} - ₹{int(salary_max):,}"
    if salary_min:
        return f"₹{int(salary_min):,}+"
    return f"Up to ₹{int(salary_max):,}"


def _mock_jobs(job_title: str, location: Optional[str]) -> dict:
    """
    Returns placeholder jobs when API keys are not configured.
    Used during development/demo.
    """
    return {
        "jobs": [
            {
                "title": f"{job_title}",
                "company": "Demo Company (Configure Adzuna API)",
                "location": location or "India",
                "salary": "Competitive",
                "description": "Configure your Adzuna API keys in the .env file to see real job listings.",
                "url": f"https://www.linkedin.com/jobs/search/?keywords={job_title.replace(' ', '%20')}",
                "created": "Today",
                "source": "Mock"
            }
        ],
        "total_found": 1,
        "query": {"role": job_title, "location": location or "India"},
        "status": "mock",
        "message": "Add ADZUNA_APP_ID and ADZUNA_APP_KEY to .env for real listings"
    }
