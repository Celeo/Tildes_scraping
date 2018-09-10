from datetime import datetime
import logging
import json
from time import sleep
from typing import Dict

import requests
from selenium.webdriver.remote.webdriver import WebDriver
from selenium import webdriver


def load_config():
    """Load and return the config from file."""
    with open('config.json') as f:
        return json.load(f)


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


def get_session_cookie(driver: WebDriver) -> str:
    """Gets the session cookie value from the driver's cookies."""
    for cookie in driver.get_cookies():
        if cookie['name'] == 'session':
            return cookie['value']


def create_http_session(session_token: str) -> requests.Session:
    """Create a new requests session with the session token as a cookie."""
    session = requests.Session()
    session.cookies.set('session', session_token)
    return session


def pause(duration: int) -> None:
    """Sleep for the duration."""
    logging.debug(f'Waiting for {duration} seconds')
    sleep(duration)


def timestamp_to_datetime(timestamp: str) -> datetime:
    """Converts a Tildes timestamp to a datetime object."""
    return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
