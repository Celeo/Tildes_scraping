#!/usr/bin/env python3
from datetime import datetime
import logging
import os
import sys
from threading import Thread

from src import (
    load_config,
    create_driver,
    get_session_cookie,
    create_http_session,
    pause
)
from src.scrapper import (
    flow_login,
    flow_get_all_groups,
    flow_get_all_topics_for_group,
    flow_get_comments_from_topics
)
from src.db import make_tables, create_session


logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s %(message)s', datefmt='%I:%M:%S')


if os.path.exists('data.db'):
    os.makedirs('db_bak', exist_ok=True)
    os.rename('data.db', 'db_bak/data.db.bak-' + datetime.now().strftime('%Y%m%d_%H%M%S'))

config = load_config()
make_tables()
session = create_session()

if len(sys.argv) == 2:
    http_session = create_http_session(sys.argv[1])
else:
    driver = create_driver(config)
    flow_login(driver, config)
    session_token = get_session_cookie(driver)
    logging.info(f'Session token: {session_token}')
    http_session = create_http_session(session_token)
    driver.quit()


group_names = flow_get_all_groups(http_session, config)

all_topics = []
topic_threads = []
for group in group_names:
    thread = Thread(target=flow_get_all_topics_for_group, args=(http_session, group, all_topics))
    topic_threads.append(thread)
    thread.start()
    pause(0.5)
logging.info('Waiting for threads to finish')
for thread in topic_threads:
    thread.join()

session.add_all(all_topics)
session.commit()

all_comments = []
comment_threads = []
topic_chunk_count = 10
topic_chunks = [
    list(i) for i in zip(
        *[all_topics[i:i + topic_chunk_count] for i in range(0, len(all_topics), topic_chunk_count)]
    )
]
for chunk in topic_chunks:
    logging.info(f'Starting comment thread with {len(chunk)} topics')
    thread = Thread(target=flow_get_comments_from_topics(http_session, chunk, all_comments))
    comment_threads.append(thread)
    thread.start()
    pause(0.5)
logging.info('Waiting for threads to finish')
for thread in comment_threads:
    thread.join()

session.add_all(all_comments)
session.commit()
