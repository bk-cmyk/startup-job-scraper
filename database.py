import sqlite3

def init_db():
    conn = sqlite3.connect("jobs.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS jobs 
                 (id TEXT PRIMARY KEY, company TEXT, title TEXT, 
                  location TEXT, url TEXT, first_seen DATETIME)''')
    conn.commit()
    conn.close()

def save_job(job_id, company, title, location, url):
    conn = sqlite3.connect("jobs.db")
    c = conn.cursor()
    # "INSERT OR IGNORE" ensures we don't save the same job twice
    c.execute("INSERT OR IGNORE INTO jobs VALUES (?, ?, ?, ?, ?, datetime('now'))", 
              (job_id, company, title, location, url))
    conn.commit()
    conn.close()
