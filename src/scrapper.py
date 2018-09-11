import logging
import re
from typing import Dict, List

from bs4 import BeautifulSoup
import requests

from . import timestamp_to_datetime, pause, get_url
from .db import Topic, Tag, Comment


def flow_login(http_session: requests.Session, config: Dict) -> None:
    """Perform a login."""
    logging.info('Logging in')
    r = http_session.get('https://tildes.net/login')
    soup = BeautifulSoup(r.text, 'html.parser')
    data = {
        'username': config['login']['username'],
        'password': config['login']['password'],
        'csrf_token': soup.find('input', {'name': 'csrf_token'})['value'],
        'keep': 'on'
    }
    headers = {'Referer': 'https://tildes.net/'}
    r = http_session.post('https://tildes.net/login', data=data, headers=headers)
    assert r.status_code == 200


def flow_get_all_groups(session: requests.Session, config: Dict) -> List[str]:
    """Get all the groups."""
    logging.info('Getting all groups')
    resp = session.get('https://tildes.net/groups')
    soup = BeautifulSoup(resp.text, features='html.parser')
    groups = []
    for ele in soup.find_all('a', class_='link-group'):
        groups.append(ele.text)
    return groups


def flow_get_all_topics_for_group(session: requests.Session, group: str, all_topics: List) -> None:
    """Record all the topics in the group."""
    logging.info(f'Gettings topics in {group}')
    resp = get_url(session, f'https://tildes.net/{group}?order=new&period=all&per_page=100')
    while True:
        soup = BeautifulSoup(resp.text, features='html.parser')
        logging.debug('Parsing out topics')
        for article_ele in soup.find_all('article', class_='topic'):
            content = None
            if article_ele.find('details', class_='topic-text-excerpt'):
                content = '\n'.join([e.text for e in article_ele.find('details', class_='topic-text-excerpt').find_all('p')])
            topic_id = article_ele['id'].split('-')[1]
            topic = Topic(
                tildes_id=topic_id,
                group=group,
                title=article_ele.find('a').text,
                link=article_ele.find('a')['href'],
                content=content,
                author=article_ele.find('a', class_='link-user').text,
                submitted=timestamp_to_datetime(article_ele.find('time')['datetime'])
            )
            tags = []
            for tag_name in [e.find('a').text for e in article_ele.find_all('li', class_='label-topic-tag')]:
                tags.append(Tag(topic=topic, name=tag_name))
            topic.tags = tags
            all_topics.append(topic)
        logging.debug('Checking for more pages of topics')
        next_page = soup.find('a', id='next-page')
        if next_page:
            logging.debug(f'Navigating to next page in {group}')
            if next_page:
                resp = get_url(session, next_page['href'])
                pause(0.5)
        else:
            logging.debug(f'No more topics in {group}')
            break


def flow_get_comments_from_topics(
    session: requests.Session, topics: List[Topic], all_comments: List[Comment]
) -> None:
    """Record all the comments on the topic in the group."""
    for topic in topics:
        url = f'https://tildes.net/{topic.group}/{topic.tildes_id}'
        logging.info(f'Getting comments from: {url}')
        resp = get_url(session, url)
        soup = BeautifulSoup(resp.text, features='html.parser')
        logging.debug('Parsing out comments')
        for article in soup.find_all('article', id=re.compile('comment-\w+')):
            if article.find('div', class_='is-comment-deleted') or article.find('div', class_='is-comment-removed'):
                continue
            if article.find('div', class_='is-comment-removed'):
                continue
            comment = Comment(
                topic=topic,
                tildes_id=article['id'].split('-')[1],
                author=article.find('header').find('a')['href'].split('/')[-1],
                submitted=timestamp_to_datetime(article.find('header').find('time')['datetime']),
                content=article.find('div', class_='comment-text').text.strip()
            )
            all_comments.append(comment)
        logging.debug(f'Stored all comments from {url}')
    pause(0.5)
