{\rtf1\ansi\ansicpg1252\cocoartf2761
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import requests\
import pandas as pd\
import sqlite3\
from database import init_db, save_job\
\
st.set_page_config(page_title="Ashby Job Tracker", layout="wide")\
init_db()\
\
# 1. Sidebar for Configuration\
st.sidebar.title("Settings")\
companies = st.sidebar.text_area("Company Slugs (one per line)", "openai\\nnotion\\nramp\\nvercel").split('\\n')\
\
if st.sidebar.button("\uc0\u55357 \u56589  Sync Jobs"):\
    with st.spinner("Fetching latest postings..."):\
        for slug in companies:\
            if not slug.strip(): continue\
            try:\
                r = requests.get(f"https://api.ashbyhq.com/posting-api/job-board/\{slug.strip()\}")\
                data = r.json()\
                for job in data.get('jobs', []):\
                    save_job(job['id'], slug, job['title'], job['location'], job['jobPostUrl'])\
            except Exception as e:\
                st.sidebar.error(f"Error fetching \{slug\}: \{e\}")\
    st.sidebar.success("Sync complete!")\
\
# 2. Main Dashboard\
st.title("\uc0\u55357 \u56960  Early Stage Job Board")\
\
# Load data from SQLite\
conn = sqlite3.connect("jobs.db")\
df = pd.read_sql_query("SELECT * FROM jobs ORDER BY first_seen DESC", conn)\
conn.close()\
\
if not df.empty:\
    # Search functionality\
    search = st.text_input("Search titles or companies...", "")\
    filtered_df = df[df.apply(lambda row: search.lower() in row.astype(str).str.lower().values, axis=1)]\
    \
    # Display as a clean table\
    st.dataframe(\
        filtered_df, \
        column_config=\{\
            "url": st.column_config.LinkColumn("Apply Link")\
        \},\
        use_container_width=True,\
        hide_index=True\
    )\
else:\
    st.info("No jobs found. Add company slugs in the sidebar and hit 'Sync'.")}