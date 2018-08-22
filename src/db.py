import sqlite3

from .constants import DB_FILE_NAME


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
        group_name TEXT NOT NULL,
        name TEXT NOT NULL,
        FOREIGN KEY (topic_id) REFERENCES topics(id)
    )''')
    connection.commit()


def record_topic(topic_id, group, title, link, comments_link, content, tags):
    """Insert the data into the tables."""
    cursor.execute(query_insert_to_topics, (topic_id, group, title, link, comments_link, content, topic_id, group))
    cursor.execute('DELETE FROM tags WHERE topic_id = ? AND group_name = ?', (topic_id, group))
    connection.commit()
    for tag in tags:
        cursor.execute('INSERT INTO tags VALUES (?, ?, ?)', (topic_id, group, tag))
    connection.commit()


query_insert_to_topics = '''
INSERT INTO topics
SELECT ?, ?, ?, ?, ?, ?
WHERE NOT EXISTS (
    SELECT 1
    FROM topics
    WHERE id = ? AND group_name = ?
)
'''
