import logging
import re
from typing import Dict, List

from bs4 import BeautifulSoup
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .src import timestamp_to_datetime
from .db import Topic, Tag, Comment


def flow_login(driver: WebDriver, config: Dict) -> None:
    """Perform the login flow."""
    logging.info('Logging in')
    driver.get('https://tildes.net/login')
    driver.find_element_by_id('username').send_keys(config['login']['username'])
    driver.find_element_by_id('password').send_keys(config['login']['password'])
    driver.find_element_by_xpath('/html/body/main/form/div[4]/button').click()
    WebDriverWait(driver, config['timeout']).until(EC.title_is('Tildes'))


def flow_login_cookie(driver: WebDriver, cookie: str) -> None:
    """Sets the login cookie in the driver."""
    logging.info('Setting browser cookie and checking logged in status')
    driver.get('https://tildes.net')
    driver.add_cookie({'name': 'session', 'value': cookie})
    driver.get('https://tildes.net')
    assert driver.title == 'Tildes', 'Cookie was unsuccessful in getting into the site'


def flow_get_all_groups(driver: WebDriver, config: Dict) -> List[str]:
    """Get all the groups."""
    driver.get('https://tildes.net/groups')
    groups = []
    for ele in driver.find_elements_by_class_name('link-group'):
        groups.append(ele.text)
    return groups


def flow_store_all_topics_for_group(driver: WebDriver, config: Dict, group: str) -> List[Topic]:
    """Record all the topics in the group."""
    topics = []
    logging.info(f'Gettings topics in {group}')
    driver.get(f'https://tildes.net/{group}?order=new&period=all&per_page=100')
    while True:
        soup = BeautifulSoup(driver.page_source, features='html.parser')
        logging.debug('Parsing out topics')
        for article_ele in soup.find_all('article', class_='topic'):
            content = None
            if article_ele.find('details', class_='topic-text-excerpt'):
                content = '\n'.join([e.text for e in article_ele.find('details', class_='topic-text-excerpt').find_all('p')])
            topic_id = article_ele['id'].split('-')[1]
            topic = Topic(
                group=group,
                tildes_id=topic_id,
                title=article_ele.find('a').text,
                link=article_ele.find('a')['href'],
                content=article_ele.find('div', class_='topic-info-comments').find('a')['href'],
                comments=content,
                author=article_ele.find('a', class_='link-user').text,
                submitted=timestamp_to_datetime(article_ele.find('time')['datetime'])
            )
            tags = []
            for tag_name in [e.find('a').text for e in article_ele.find_all('li', class_='label-topic-tag')]:
                tags.append(Tag(topic=topic, name=tag_name))
            topic.tags = tags
            topics.append(topic)
        logging.debug('Checking for more pages of topics')
        if config['browser']['nav_next'] and soup.find('a', id='next-page'):
            logging.info(f'Navigating to next page in {group}')
            driver.find_element_by_id('next-page').click()
        else:
            logging.info(f'No more topics in {group}')
            break
    return topics


def flow_get_comments_from_topic(driver: WebDriver, config: Dict, group: str, topic: str) -> List:
    """Record all the comments on the topic in the group."""
    comments = []
    url = f'https://tildes.net/{group}/{topic}'
    driver.get(url)
    if driver.title == '404 Not Found':
        logging.error(f'Topic "{topic}" not found in group "{group}"')
        return
    soup = BeautifulSoup(driver.page_source, features='html.parser')
    logging.debug('Parsing out comments')
    for article in soup.find_all('article', id=re.compile('comment-\w+')):
        if article.find('div', class_='is-comment-deleted'):
            continue
        # FIXME need topic ref
        comment = Comment(
            topic=None,
            tildes_id=article['id'].split('-')[1],
            author=article.find('header').find('a')['href'].split('/')[-1],
            submitted=timestamp_to_datetime(article.find('header').find('time')['datetime']),
            content=article.find('div', class_='comment-text').text.strip()
        )
        comments.append(comment)
    logging.info(f'Stored all comments from {url}')
    return comments
