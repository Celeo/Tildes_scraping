import os
import sqlite3

from constants import DB_FILE_NAME

if os.path.exists(DB_FILE_NAME):
    os.remove(DB_FILE_NAME)
connection = sqlite3.connect(DB_FILE_NAME)
cursor = connection.cursor()


def make_tables():
    cursor.execute('''CREATE TABLE IF NOT EXISTS topics (
        id TEXT PRIMARY KEY,
        group_name TEXT NOT NULL,
        title TEXT NOT NULL,
        link TEXT,
        content TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS tags (
        topic_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        FOREIGN KEY (topic_id) REFERENCES topics(id)
    )''')
    connection.commit()


def record_topic(topic_id, group, title, link, content, tags):
    cursor.execute('INSERT INTO topics VALUES (?, ?, ?, ?, ?)', (topic_id, group, title, link, content))
    connection.commit()
    for tag in tags:
        cursor.execute('INSERT INTO tags VALUES (?, ?)', (topic_id, tag))
    connection.commit()
