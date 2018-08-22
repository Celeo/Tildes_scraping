import logging
import re
from time import sleep
from typing import Dict, List

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .db import record_topic, record_comment


def create_driver(config: Dict) -> WebDriver:
    """Create, configure, and return a new driver."""
    chrome_options = webdriver.ChromeOptions()
    if config['browser']['headless']:
        logging.debug('Adding headless argument to Chrome options')
        chrome_options.add_argument("headless")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.implicitly_wait(config['timeout'])
    driver.set_page_load_timeout(config['timeout'])
    return driver


def pause(duration: int) -> None:
    """Sleep for the duration."""
    logging.debug(f'Waiting for {duration} seconds')
    sleep(duration)


def flow_login(driver: WebDriver, config: Dict) -> None:
    """Perform the login flow."""
    logging.info('Logging in')
    driver.get('https://tildes.net/login')
    driver.find_element_by_id('username').send_keys(config['login']['username'])
    driver.find_element_by_id('password').send_keys(config['login']['password'])
    driver.find_element_by_xpath('/html/body/main/form/div[4]/button').click()
    # Can't just click the submit button; have to actually wait for the form to submit
    # and the next page to arrive, as determined by the driver's current title.
    WebDriverWait(driver, config['timeout']).until(EC.title_is('Tildes'))


def set_login_cookie(driver: WebDriver, cookie: str) -> None:
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


def flow_store_all_topics_for_group(driver: WebDriver, config: Dict, group: str, scan_comments: bool) -> None:
    """Record all the topics in the group."""
    logging.info(f'Gettings topics in {group}')
    driver.get(f'https://tildes.net/{group}?order=new&period=all&per_page=100')
    while True:
        # it's way faster to use bs4 than to use the browser functions to find things on the page
        soup = BeautifulSoup(driver.page_source, features='html.parser')
        logging.debug('Parsing out topics')
        for article_ele in soup.find_all('article', class_='topic'):
            content = None
            if article_ele.find('details', class_='topic-text-excerpt'):
                content = '\n'.join([e.text for e in article_ele.find('details', class_='topic-text-excerpt').find_all('p')])
            topic_id = article_ele['id'].split('-')[1]
            record_topic(
                topic_id,
                group,
                article_ele.find('a').text,
                article_ele.find('a')['href'],
                article_ele.find('div', class_='topic-info-comments').find('a')['href'],
                content,
                [e.find('a').text for e in article_ele.find_all('li', class_='label-topic-tag')]
            )
            if scan_comments:
                flow_get_comments_from_topic(driver, config, group, topic_id)
        logging.debug('Checking for more pages of topics')
        if config['browser']['nav_next'] and soup.find('a', id='next-page'):
            logging.info(f'Navigating to next page in {group}')
            driver.find_element_by_id('next-page').click()
            pause(3)
        else:
            logging.info(f'No more topics in {group}')
            break


def flow_get_comments_from_topic(driver: WebDriver, config: Dict, group: str, topic: str) -> None:
    """Record all the comments on the topic in the group."""
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
        record_comment(
            article['id'].split('-')[1],
            topic,
            group,
            article.find('header').find('a')['href'].split('/')[-1],
            article.find('header').find('time')['datetime'],
            article.find('div', class_='comment-text').text.strip()
        )
    logging.info(f'Stored all comments from {url}')
    pause(1)
