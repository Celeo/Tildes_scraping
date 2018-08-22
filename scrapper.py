import logging
import json
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from constants import CONFIG_FILE_NAME
from db import make_tables, record_topic


logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s %(message)s', datefmt='%I:%M:%S')


def load_config():
    """Load and return the config from file."""
    with open(CONFIG_FILE_NAME) as f:
        return json.load(f)


def create_driver(config):
    """Create, configure, and return the driver."""
    chrome_options = webdriver.ChromeOptions()
    if config['browser']['headless']:
        logging.debug('Adding headless argument to Chrome options')
        chrome_options.add_argument("headless")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.implicitly_wait(config['timeout'])
    driver.set_page_load_timeout(config['timeout'])
    return driver


def wait_for_title(driver, config, title):
    """Wait for the driver's page's title to be the passed value."""
    WebDriverWait(driver, config['timeout']).until(EC.title_is(title))


def flow_login(driver, config):
    """Perform the login flow."""
    logging.info('Logging in')
    driver.get('https://tildes.net/login')
    driver.find_element_by_id('username').send_keys(config['login']['username'])
    driver.find_element_by_id('password').send_keys(config['login']['password'])
    driver.find_element_by_xpath('/html/body/main/form/div[4]/button').click()
    # Can't just click the submit button; have to actually wait for the form to submit
    # and the next page to arrive, as determined by the driver's current title.
    wait_for_title(driver, config, 'Tildes')


def flow_get_all_groups(driver, config):
    """Get all the groups on the site."""
    driver.get('https://tildes.net/groups')
    groups = []
    for ele in driver.find_elements_by_class_name('link-group'):
        groups.append(ele.text)
    return groups


def flow_store_all_topics_for_group(driver, config, group):
    """Get all the topics in the group on the site."""
    logging.debug(f'Navigating to first topic listing for group {group}')
    driver.get(f'https://tildes.net/{group}?order=new&period=all&per_page=100')
    while True:
        # it's way faster to use bs4 than to use the browser functions to find things on the page
        soup = BeautifulSoup(driver.page_source, features='html.parser')
        logging.debug('Parsing out topics')
        for article_ele in soup.find_all('article', class_='topic'):
            content = None
            if article_ele.find('details', class_='topic-text-excerpt'):
                content = '\n'.join([e.text for e in article_ele.find('details', class_='topic-text-excerpt').find_all('p')])
            record_topic(
                article_ele['id'].split('-')[1],
                group,
                article_ele.find('a').text,
                article_ele.find('a')['href'],
                article_ele.find('div', class_='topic-info-comments').find('a')['href'],
                content,
                [e.find('a').text for e in article_ele.find_all('li', class_='label-topic-tag')]
            )
        logging.debug('Checking for more pages of topics')
        if config['browser']['nav_next'] and soup.find('a', id='next-page'):
            logging.info(f'Navigating to next page in {group}')
            driver.find_element_by_id('next-page').click()
        else:
            logging.info(f'No more topics in {group}')
            break
        pause(1)


def pause(duration):
    """Sleep for the duration."""
    logging.debug(f'Waiting for {duration} seconds')
    sleep(duration)


def main():
    """Main processing control and loop."""
    driver = None
    try:
        logging.info('Setting up')
        config = load_config()
        make_tables()
        driver = create_driver(config)
        flow_login(driver, config)
        logging.info('Getting all group names')
        group_names = flow_get_all_groups(driver, config)
        for group in group_names:
            logging.info(f'Getting topics in {group}')
            flow_store_all_topics_for_group(driver, config, group)
            pause(5)
        logging.info('Closing down the browser')
        driver.quit()
    finally:
        if driver:
            driver.quit()


if __name__ == '__main__':
    main()
