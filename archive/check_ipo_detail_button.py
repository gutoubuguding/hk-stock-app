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
    driver.get('http://localhost:3000/stock/02493?source=ipo&name=IPO_TEST')
    time.sleep(5)
    body = driver.find_element(By.TAG_NAME, 'body').text
    buttons = driver.find_elements(By.XPATH, "//button[contains(., '开始分析') or contains(., '開始分析')]")
    print('body_len:', len(body))
    print('has_name:', 'IPO_TEST' in body)
    print('buttons:', len(buttons))
    print('disabled:', [b.get_attribute('disabled') for b in buttons])
    severe = [x for x in driver.get_log('browser') if x.get('level') == 'SEVERE' and 'favicon' not in x.get('message', '')]
    print('severe:', severe)
finally:
    driver.quit()
