import logging
import re
from typing import Dict, List

from bs4 import BeautifulSoup
import requests
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from . import timestamp_to_datetime, pause, get_url
from .db import Topic, Tag, Comment


def flow_login(driver: WebDriver, config: Dict) -> None:
    """Perform the login flow."""
    logging.info('Logging in')
    driver.get('https://tildes.net/login')
    driver.find_element_by_id('username').send_keys(config['login']['username'])
    driver.find_element_by_id('password').send_keys(config['login']['password'])
    driver.find_element_by_xpath('/html/body/main/form/div[4]/button').click()
    WebDriverWait(driver, config['timeout']).until(EC.title_is('Tildes'))


def flow_get_all_groups(session: requests.Session, config: Dict) -> List[str]:
    """Get all the groups."""
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
