import logging
import json
import os

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


CONFIG_FILE_NAME = 'config.json'
OUTPUT_FILE_NAME = 'data_output.json'

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s %(message)s', datefmt='%I:%M:%S')


def load_config():
    """Load and return the config from file."""
    with open(CONFIG_FILE_NAME) as f:
        return json.load(f)


def save_to_file(data):
    """Save the data to the output data file."""
    if os.path.exists(OUTPUT_FILE_NAME):
        logging.debug('Deleting existing data output file')
        os.remove(OUTPUT_FILE_NAME)
    with open(OUTPUT_FILE_NAME, 'w') as f:
        json.dump(data, f, indent=2)


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
    driver.get('https://tildes.net/login')
    driver.find_element_by_id('username').send_keys(config['login']['username'])
    driver.find_element_by_id('password').send_keys(config['login']['password'])
    driver.find_element_by_xpath('/html/body/main/form/div[4]/button').click()
    wait_for_title(driver, config, 'Tildes')


def flow_get_all_groups(driver, config):
    """Get all the groups on the site."""
    driver.get('https://tildes.net/groups')
    groups = []
    for ele in driver.find_elements_by_class_name('link-group'):
        groups.append(ele.text)
    return groups


def flow_get_all_topics_for_group(driver, config, group):
    """Get all the topics in the group on the site."""
    driver.get(f'https://tildes.net/{group}?order=new&period=all')
    topics = []
    for ele in driver.find_elements_by_xpath('//h1[contains(@class, "topic-title")]/a'):
        topics.append(ele.text)
    return topics


def main():
    """Main processing."""
    driver = None
    try:
        logging.info('Setting up')
        config = load_config()
        driver = create_driver(config)
        flow_login(driver, config)
        data = {}
        logging.info('Getting all group names')
        data['group_names'] = flow_get_all_groups(driver, config)
        for group in data['group_names']:
            logging.info(f'Getting topics in {group}')
            data[group] = {'topics': flow_get_all_topics_for_group(driver, config, group)}
        logging.info('Saving collected data')
        save_to_file(data)
        logging.info('Closing down the browser')
        driver.quit()
    finally:
        if driver:
            driver.quit()


if __name__ == '__main__':
    main()
