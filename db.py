import os
import sqlite3

from constants import DB_FILE_NAME

# always remove any existing file - no support for _adding_ data yet
if os.path.exists(DB_FILE_NAME):
    os.remove(DB_FILE_NAME)
connection = sqlite3.connect(DB_FILE_NAME)
cursor = connection.cursor()


def make_tables():
    """Create all the database tables if they don't exist."""
    cursor.execute('''CREATE TABLE IF NOT EXISTS topics (
        id TEXT NOT NULL,
        group_name TEXT NOT NULL,
        title TEXT NOT NULL,
        link TEXT,
        comments_link TEXT,
        content TEXT,
        UNIQUE(id, group_name)
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS tags (
        topic_id TEXT NOT NULL,
        name TEXT NOT NULL,
        FOREIGN KEY (topic_id) REFERENCES topics(id)
    )''')
    connection.commit()


def record_topic(topic_id, group, title, link, comments_link, content, tags):
    """Insert the data into the tables."""
    cursor.execute('INSERT INTO topics VALUES (?, ?, ?, ?, ?, ?)', (topic_id, group, title, link, comments_link, content))
    connection.commit()
    for tag in tags:
        cursor.execute('INSERT INTO tags VALUES (?, ?)', (topic_id, tag))
    connection.commit()
