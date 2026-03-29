import streamlit as st
import requests
import pandas as pd
import sqlite3
from database import init_db, save_job

# Robust import for the Google Search tool
try:
    from googlesearch import search as gsearch
except ImportError:
    gsearch = None

st.set_page_config(page_title="Ashby Job Tracker", layout="wide", page_icon="🚀")

# Initialize the database on startup
init_db()

# --- HELPER FUNCTIONS ---

def discover_new_slugs(query="site:jobs.ashbyhq.com"):
    """Searches Google for Ashby job board URLs and extracts the company slug."""
    new_slugs = set()
    if not gsearch:
        return []
    
    try:
        # Changed 'stop' to 'num_results' to fix the TypeError
        for url in gsearch(query, num_results=15):
            parts = url.split('/')
            if len(parts) >= 4:
                # URL is usually https://jobs.ashbyhq.com/company-name
                slug = parts[3].split('?')[0].split('#')[0]
                if slug not in ['search', 'terms', 'privacy', '']:
                    new_slugs.add(slug)
    except Exception as e:
        st.error(f"Search error: {e}")
        
    return list(new_slugs)

# --- SIDEBAR UI ---

st.sidebar.title("🛠️ Control Panel")

# Using tabs in the sidebar to keep it tidy
sb_tab1, sb_tab2 = st.sidebar.tabs(["Existing List", "Find New"])

with sb_tab1:
    default_slugs = "openai\nnotion\nramp\nvercel\nlinear\nposthog"
    company_input = st.text_area("Company Slugs (one per line)", default_slugs, height=200)
    companies = [s.strip() for s in company_input.split('\n') if s.strip()]

with sb_tab2:
    st.write("Find companies using Ashby via Google")
    search_query = st.text_input("Search Query", "site:jobs.ashbyhq.com head of")
    if st.button("🔍 Discover Slugs"):
        with st.spinner("Searching..."):
            found = discover_new_slugs(search_query)
            if found:
                st.success(f"Found: {', '.join(found)}")
                st.info("Copy these into the 'Existing List' tab to sync them.")
            else:
                st.warning("No new slugs found. Try a different query.")

st.sidebar.markdown("---")

if st.sidebar.button("🚀 Sync All Jobs", use_container_width=True):
    with st.spinner("Fetching latest postings..."):
        progress_bar = st.sidebar.progress(0)
        for idx, slug in enumerate(set(companies)):
            try:
                r = requests.get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}", timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    jobs_list = data.get('jobs', [])
                    for job in jobs_list:
                        # SAFE DATA RETRIEVAL (Fixes 'jobPostUrl' error)
                        job_id = job.get('id', 'unknown_id')
                        title = job.get('title', 'Unknown Title')
                        location = job.get('location', 'Remote/Various')
                        
                        # Fallback chain for the URL
                        url = job.get('jobPostUrl') or job.get('jobUrl') or f"https://jobs.ashbyhq.com/{slug}/{job_id}"
                        
                        save_job(job_id, slug, title, location, url)
                else:
                    st.sidebar.warning(f"Skipped {slug}: {r.status_code}")
            except Exception as e:
                st.sidebar.error(f"Error {slug}: {str(e)}")
            
            progress_bar.progress((idx + 1) / len(set(companies)))
        st.sidebar.success("Sync Complete!")

# --- MAIN DASHBOARD UI ---

st.title("🚀 Startup Job Tracker")
st.markdown("Monitoring the latest roles from top-tier Ashby-hosted job boards.")

# Display stats
conn = sqlite3.connect("jobs.db")
try:
    df = pd.read_sql_query("SELECT * FROM jobs ORDER BY first_seen DESC", conn)
    
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Jobs", len(df))
        col2.metric("Companies", df['company'].nunique())
        col3.metric("Latest Sync", df['first_seen'].max()[:10])

        st.markdown("---")
        
        # Search and Filter
        search_term = st.text_input("🎯 Filter by title, company, or location:", "")
        if search_term:
            df = df[df.apply(lambda row: search_term.lower() in row.astype(str).str.lower().values, axis=1)]

        # Display Data
        st.dataframe(
            df,
            column_config={
                "url": st.column_config.LinkColumn("Application Link"),
                "first_seen": st.column_config.DatetimeColumn("Date Found"),
                "company": st.column_config.TextColumn("Company", help="Ashby Slug")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Download Option
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", csv, "ashby_jobs.csv", "text/csv")
        
    else:
        st.info("The database is currently empty. Add slugs in the sidebar and click 'Sync All Jobs'.")
except Exception as e:
    st.error(f"Database Error: {e}")
finally:
    conn.close()