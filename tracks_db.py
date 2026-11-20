import os
import re
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tracks.db")

# Create DB
con = sqlite3.connect(DB_PATH, check_same_thread=False)
con.execute("PRAGMA journal_mode=WAL") # Write-Ahead Log
con.executescript("""
CREATE TABLE IF NOT EXISTS tracks(
    id        INTEGER PRIMARY KEY, 
    uid       TEXT UNIQUE,     
    norm      TEXT UNIQUE,      
    file_id   TEXT NOT NULL,
    msg_id    INTEGER,          
    title     TEXT,
    performer TEXT,
    source    TEXT
);
CREATE VIRTUAL TABLE IF NOT EXISTS tracks_fts USING fts5(
    title, performer,
    content='tracks', content_rowid='id',
    tokenize='unicode61', prefix='2 3'
);
DROP TRIGGER IF EXISTS tracks_ai;
DROP TRIGGER IF EXISTS tracks_ad;
DROP TRIGGER IF EXISTS tracks_au;
""")

TLD = r"(?:net|ru|com|org|me|su|ua|fm|cc|info|biz)"
JUNK = [
    re.compile(rf"\s*[\[(][^\])]*\.{TLD}[^\])]*[\])]", re.I),   
    re.compile(rf"\s*\b[\w-]+\.{TLD}\s*$", re.I),                
    re.compile(r"\s*[\[(]\s*без рекламы\s*[\])]", re.I),         
    re.compile(r"<unknown>", re.I),
]

def clean(s):
    s = s or ""
    for p in JUNK:
        s = p.sub("", s)
    return re.sub(r"\s+", " ", s).strip(" -–—_")

def prepare(title, performer):
    title, performer = clean(title), clean(performer)
    if not performer and " - " in title:
        performer, title = [x.strip() for x in title.split(" - ", 1)]
    norm = re.sub(r"[\W_]+", "", f"{performer}{title}".lower())
    return title, performer, norm