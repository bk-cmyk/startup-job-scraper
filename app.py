import streamlit as st
import requests
import pandas as pd
import sqlite3

# Safely import googlesearch
try:
    from googlesearch import search as gsearch
except ImportError:
    gsearch = None

# ... (Database functions from previous steps) ...

if st.sidebar.button("🔍 Sync Jobs"):
    with st.spinner("Fetching jobs..."):
        for slug in companies:
            try:
                r = requests.get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}")
                if r.status_code == 200:
                    data = r.json()
                    for job in data.get('jobs', []):
                        # FIX: This line prevents the 'jobPostUrl' error
                        job_id = job.get('id', 'N/A')
                        title = job.get('title', 'Unknown')
                        location = job.get('location', 'Remote')
                        # Fallback chain for the URL
                        url = job.get('jobPostUrl') or job.get('jobUrl') or f"https://jobs.ashbyhq.com/{slug}"
                        
                        save_job(job_id, slug, title, location, url)
                    st.sidebar.success(f"Updated {slug}")
                else:
                    st.sidebar.warning(f"Skipped {slug}: Board not found")
            except Exception as e:
                st.sidebar.error(f"Error with {slug}: {str(e)}")