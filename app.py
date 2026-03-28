import streamlit as st
import requests
import pandas as pd
import sqlite3
from database import init_db, save_job
from googlesearch import search as gsearch  # pip install googlesearch-python

st.set_page_config(page_title="Ashby Job Tracker", layout="wide")
init_db()

# --- 1. SEARCH/DISCOVERY LOGIC ---
def discover_new_slugs(query="site:jobs.ashbyhq.com"):
    new_slugs = set()
    # This searches Google for the ashby domain
    for url in gsearch(query, stop=10):
        parts = url.split('/')
        if len(parts) >= 4:
            slug = parts[3].split('?')[0]
            if slug not in ['search', 'terms', 'privacy', '']:
                new_slugs.add(slug)
    return list(new_slugs)

# --- 2. SIDEBAR ---
st.sidebar.title("Settings")

# Tabs for Organization
tab1, tab2 = st.tabs(["📋 My List", "🔍 Discovery"])

with tab1:
    company_input = st.text_area("Known Slugs (one per line)", "openai\nnotion\nramp")
    companies = [s.strip() for s in company_input.split('\n') if s.strip()]

with tab2:
    st.write("Find new Ashby users via Google:")
    if st.button("Search for New Companies"):
        with st.spinner("Searching Google..."):
            found_slugs = discover_new_slugs()
            st.write(f"Found: {', '.join(found_slugs)}")
            # This appends them to your list automatically
            companies.extend(found_slugs)

# --- 3. SYNC LOGIC ---
if st.sidebar.button("🚀 Sync All Jobs"):
    with st.spinner("Syncing..."):
        for slug in set(companies): # Use set() to avoid duplicates
            try:
                r = requests.get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}")
                data = r.json()
                for job in data.get('jobs', []):
                    # Fixed URL logic to prevent errors
                    link = job.get('jobPostUrl') or job.get('jobUrl') or f"https://jobs.ashbyhq.com/{slug}/{job['id']}"
                    save_job(job['id'], slug, job['title'], job['location'], link)
            except Exception as e:
                st.sidebar.warning(f"Skipped {slug}: {e}")
    st.sidebar.success("Sync complete!")

# --- 4. MAIN DASHBOARD ---
# (Keep the same display logic from the previous step here)