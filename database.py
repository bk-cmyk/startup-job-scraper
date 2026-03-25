{\rtf1\ansi\ansicpg1252\cocoartf2761
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import sqlite3\
\
def init_db():\
    conn = sqlite3.connect("jobs.db")\
    c = conn.cursor()\
    c.execute('''CREATE TABLE IF NOT EXISTS jobs \
                 (id TEXT PRIMARY KEY, company TEXT, title TEXT, \
                  location TEXT, url TEXT, first_seen DATETIME)''')\
    conn.commit()\
    conn.close()\
\
def save_job(job_id, company, title, location, url):\
    conn = sqlite3.connect("jobs.db")\
    c = conn.cursor()\
    # "INSERT OR IGNORE" ensures we don't save the same job twice\
    c.execute("INSERT OR IGNORE INTO jobs VALUES (?, ?, ?, ?, ?, datetime('now'))", \
              (job_id, company, title, location, url))\
    conn.commit()\
    conn.close()}