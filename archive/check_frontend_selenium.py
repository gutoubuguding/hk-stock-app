from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--disable-gpu')
opts.add_argument('--no-sandbox')
opts.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

driver = webdriver.Chrome(options=opts)
try:
    for path in ['/', '/stock/00700', '/watchlist', '/alerts']:
        driver.get('http://localhost:3000' + path)
        time.sleep(3)
        body = driver.find_element(By.TAG_NAME, 'body').text
        severe = [x for x in driver.get_log('browser') if x.get('level') == 'SEVERE' and 'favicon' not in x.get('message', '')]
        print('---', path)
        print('body_len:', len(body))
        print(body[:500].replace('\n', ' | '))
        print('severe:', severe)
finally:
    driver.quit()
