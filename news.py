import requests
from datetime import datetime
import sqlite3
import json
from bs4 import BeautifulSoup
import sys

# 1. Accumulate all the HN/Lobsters articles today at x time
# 2. Store these articles in an SQLite database
# 3. Send me a summary of these articles via email by the end of the week

con = sqlite3.connect("tops.db")
cursor = con.cursor()

def create_table():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    con.commit()

def write_entry(title, url):
    # if an entry with the same url exists, do not insert it again
    cursor.execute('''
        SELECT COUNT(*) FROM news WHERE url = ?
    ''', (url,))
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"Entry with URL {url} already exists, skipping insertion.")
        return
    # insert the new entry
    print(f"Inserting entry: {title} - {url}")
    cursor.execute('''
        INSERT INTO news (title, url) VALUES (?, ?)
    ''', (title, url))
    con.commit()

# get entries added within the last week
def get_recent_week_entries():
    cursor.execute('''
        SELECT * FROM news WHERE timestamp >= datetime('now', '-7 days')
    ''')
    return cursor.fetchall()

LOBSTERS_URL = "https://lobste.rs"
top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty"
top_stories = requests.get(top_stories_url).content
top_stories = json.loads(top_stories)

class NewsEntry:
    def __init__(self, title, url):
        self.title = title
        self.url = url

    def __repr__(self):
        return f"NewsEntry(title={self.title}, url={self.url})"

def get_hn_entry(id):
    url = f"https://hacker-news.firebaseio.com/v0/item/{id}.json?print=pretty"
    result = json.loads(requests.get(url).content)
    
    if (result.get("kids", None) is not None): del result["kids"]
    if (result.get("score", None) is not None): del result["score"]
    if (result.get("by", None) is not None): del result["by"]
    if (result.get("descendants", None) is not None): del result["descendants"]
    
    result["time"] = datetime.fromtimestamp(result["time"]).isoformat()
    
    return result
    
def get_hn_entries() -> list[NewsEntry]:
    entries = []
    for id in top_stories[:30]:
        entry = get_hn_entry(id)
        entries.append(NewsEntry(entry["title"], entry["url"]))
    return entries


def get_lobsters_entries() -> list[NewsEntry]:
    lobsters_page = requests.get(LOBSTERS_URL).content
    soup = BeautifulSoup(lobsters_page, "html.parser")
    stories = soup.find_all("li", class_="story")
    entries = []
    for story in stories:
        found_it = story.find("a", class_="u-url")
        url = found_it.get("href", None)
        title = found_it.contents[0]
        entry = NewsEntry(title, url)
        entries.append(entry)
    return entries 

def get_and_write_news():
    create_table()
    hn_entries = get_hn_entries()
    lobste_entries = get_lobsters_entries()
    entries = hn_entries + lobste_entries
    for entry in entries:
        write_entry(entry.title, entry.url)
   
# run this script daily
if sys.argv[1] == "fetch":
    get_and_write_news()