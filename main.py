import json

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def load_config():
    with open('config.json') as f:
        return json.load(f)


def create_driver(config):
    chrome_options = webdriver.ChromeOptions()
    if config['browser']['headless']:
        chrome_options.add_argument("headless")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.implicitly_wait(config['timeout'])
    driver.set_page_load_timeout(config['timeout'])
    return driver


def flow_login(driver, config):
    driver.get('https://tildes.net/login')
    driver.find_element_by_id('username').send_keys(config['login']['username'])
    driver.find_element_by_id('password').send_keys(config['login']['password'])
    driver.find_element_by_xpath('/html/body/main/form/div[4]/button').click()
    WebDriverWait(driver, config['timeout']).until(EC.title_is('Tildes'))


def main():
    config = load_config()
    driver = create_driver(config)
    flow_login(driver, config)
    driver.quit()


if __name__ == '__main__':
    main()
