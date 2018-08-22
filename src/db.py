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
    cursor.execute('''CREATE TABLE IF NOT EXISTS comments (
        id TEXT PRIMARY KEY,
        topic_id TEXT NOT NULL,
        group_name TEXT NOT NULL,
        author TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        content TEXT NOT NULL,
        FOREIGN KEY (topic_id) REFERENCES topics(id)
    )
    ''')
    connection.commit()


def record_topic(topic: str, group: str, title: str, link: str, comments_link: str, content: str, tags: str) -> None:
    """Save topic and tag data."""
    cursor.execute(query_delete_from_topics, (topic, group))
    cursor.execute(query_insert_to_topics, (topic, group, title, link, comments_link, content))
    cursor.execute(query_delete_from_tags, (topic, group))
    for tag in tags:
        cursor.execute(query_insert_to_tags, (topic, group, tag))
    connection.commit()


def record_comment(comment_id, topic: str, group: str, author: str, timestamp: str, content: str) -> None:
    """Save the comment data."""
    cursor.execute(query_delete_from_comments, (comment_id, topic, group))
    cursor.execute(query_insert_to_comments, (comment_id, topic, group, author, timestamp, content))
    connection.commit()


query_delete_from_topics = 'DELETE FROM topics WHERE id = ? AND group_name = ?'
query_insert_to_topics = 'INSERT INTO topics VALUES (?, ?, ?, ?, ?, ?)'

query_delete_from_tags = 'DELETE FROM tags WHERE topic_id = ? AND group_name = ?'
query_insert_to_tags = 'INSERT INTO tags VALUES (?, ?, ?)'

query_delete_from_comments = 'DELETE FROM comments WHERE id = ? AND topic_id = ? AND group_name = ?'
query_insert_to_comments = 'INSERT INTO comments VALUES (?, ?, ?, ?, ?, ?)'
