from datetime import datetime
import logging
import json
from time import sleep
from typing import Dict
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


def pause(duration: int) -> None:
    """Sleep for the duration."""
    logging.debug(f'Waiting for {duration} seconds')
    sleep(duration)


def timestamp_to_datetime(timestamp: str) -> datetime:
    """Converts a Tildes timestamp to a datetime object."""
    return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')
