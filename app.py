import streamlit as st
import requests
import pandas as pd
import sqlite3
from database import init_db, save_job

# Try to import, but don't crash the whole app if it's missing
try:
    from googlesearch import search as gsearch
except ImportError:
    gsearch = None

st.set_page_config(page_title="Ashby Job Tracker", layout="wide")
init_db()

# --- SIDEBAR ---
st.sidebar.title("Settings")
company_input = st.sidebar.text_area("Company Slugs", "openai\nnotion\nramp\nvercel")
companies = [s.strip() for s in company_input.split('\n') if s.strip()]

if st.sidebar.button("🔍 Sync Jobs"):
    with st.spinner("Fetching jobs..."):
        for slug in companies:
            try:
                r = requests.get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}")
                if r.status_code != 200:
                    st.sidebar.error(f"Could not find company: {slug}")
                    continue
                
                data = r.json()
                jobs_found = data.get('jobs', [])
                
                for job in jobs_found:
                    # FIX: Safely check for different possible URL keys
                    job_id = job.get('id')
                    title = job.get('title', 'Unknown Title')
                    location = job.get('location', 'Remote/Unknown')
                    
                    # Ashby sometimes uses 'jobUrl' or 'jobPostUrl'
                    url = job.get('jobPostUrl') or job.get('jobUrl') or f"https://jobs.ashbyhq.com/{slug}/{job_id}"
                    
                    save_job(job_id, slug, title, location, url)
                    
                st.sidebar.success(f"Synced {len(jobs_found)} jobs for {slug}")
                
            except Exception as e:
                st.sidebar.error(f"Error fetching {slug}: {str(e)}")

# --- DISCOVERY ---
st.sidebar.markdown("---")
st.sidebar.subheader("Discovery Mode")
if st.sidebar.button("Find New Ashby Slugs"):
    if gsearch:
        with st.spinner("Searching Google..."):
            results = [res for res in gsearch("site:jobs.ashbyhq.com", stop=5)]
            st.sidebar.write("Found these URLs:")
            for r in results:
                st.sidebar.caption(r)
    else:
        st.sidebar.warning("Install 'googlesearch-python' to use this feature.")

# --- MAIN DASHBOARD ---
st.title("🚀 Startup Job Tracker")
conn = sqlite3.connect("jobs.db")
try:
    df = pd.read_sql_query("SELECT * FROM jobs ORDER BY first_seen DESC", conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No jobs in database yet. Click 'Sync' in the sidebar.")
except Exception:
    st.info("Database is initializing...")
finally:
    conn.close()