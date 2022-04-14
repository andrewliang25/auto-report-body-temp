# -*- coding: utf-8 -*-
"""
Auto Report Body Temperature

Since COVID-19 pandemic, my company requested employees to report body temperature 3 times per day through Microsoft Forms.
So I wrote a script to fill in forms and submit automatically on scheduled days and time with Python and Selenium.
"""

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
# from webdriver_manager.utils import ChromeType
import time
import random
import schedule
import datetime
import getpass
from loader import Loader

def schedule_auto_report_body_temp(account, password):
    schedule.every().day.at("09:00").do(report_body_temp_on_weekdays, "早上", account, password)
    schedule.every().day.at("12:00").do(report_body_temp_on_weekdays, "中午", account, password)
    schedule.every().day.at("18:00").do(report_body_temp_on_weekdays, "下午", account, password)
    
    # Checks whether a scheduled task is pending to run or not
    with Loader("Schedule Pending..."):
        while True:
            schedule.run_pending()
            time.sleep(1)
        
    return


def report_body_temp_on_weekdays(time_period_string, account, password):
    print("Task start at " + datetime.datetime.now().strftime("%H:%M:%S") + ".")
    
    if datetime.datetime.today().isoweekday() > 5:
        print("Today is weekend, no need to report body temp.")
        return
    
    sleep_time = random.randint(0, 600)
    print("Will start reporting at " + (datetime.datetime.now() + datetime.timedelta(seconds=sleep_time)).strftime("%H:%M:%S") + ".")
    time.sleep(sleep_time)
    
    report_body_temp(time_period_string, get_body_temp(), account, password)


def get_body_temp():
    return round(random.uniform(35.7, 36.5), 1)


def report_body_temp(time_period_string, body_temp, account, password):
    print("Start reporting at " + datetime.datetime.now().strftime("%H:%M:%S") + ".")
    
    body_temp_report_form_url = "https://forms.office.com/pages/responsepage.aspx?id=pSz4zODECk-s8yyNA5auoPhR9A61DCRFqLLx7a3usHZURE44T1dHVUFMWk1CRVc5WEVXVFExM0QyMi4u"
    fill_report_body_temp_action_list = [
    # enter account
    {'type': 'write', 'xpath': '//*[@id="i0116"]', 'text': account},
    {'type': 'click', 'xpath': '//*[@id="idSIButton9"]', 'text': ''},
    # enter password and login
    {'type': 'write', 'xpath': '//*[@id="i0118"]', 'text': password},
    {'type': 'click', 'xpath': '//*[@id="idSIButton9"]', 'text': ''},
    # click not to keep logged in
    {'type': 'click', 'xpath': '//*[@id="idBtn_Back"]', 'text': ''},
    # choose time period
    {'type': 'click', 'xpath': '//*[@id="form-container"]//input[@value="'+ time_period_string +'"]', 'text': ''},
    # enter body temp
    {'type': 'write', 'xpath': '//*[@id="form-container"]//input[@placeholder="數目必須介於 33.5 ~ 42.9 之間"]', 'text': body_temp},
    # choose not feeling bad
    {'type': 'click', 'xpath': '//*[@id="form-container"]//input[@value="1.無"]', 'text': ''},
    # check send email receipt
    {'type': 'click', 'xpath': '//*[@id="form-container"]/div/div/div[1]/div/div[1]/div[2]/div[3]/div/div/label/input', 'text': ''},
    # submit
    {'type': 'click', 'xpath': '//*[@id="form-container"]//button[@title="提交"]', 'text': ''},
    # wait finish
    {'type': 'wait', 'xpath': '//*[@id="form-container"]/div/div/div[1]/div/div[2]/div[1]/div[2]/span', 'text': ''}]

    selenium_chrome_robot(body_temp_report_form_url, fill_report_body_temp_action_list, headless_mode=True)
    
    return


def selenium_chrome_robot(input_url, input_action_list, headless_mode=False):
    # 0. init
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_service = Service(ChromeDriverManager().install())
    # 1. set headless
    if headless_mode:
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
    # 2. set user-agent
    ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) " \
         "AppleWebKit/537.36 (KHTML, like Gecko) " \
         "Chrome/92.0.4515.159 Safari/537.36"
    chrome_options.add_argument('user-agent={}'.format(ua))
    # 3. open browser
    print("Open browser at " + datetime.datetime.now().strftime("%H:%M:%S") + ".")
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    driver.set_window_size(1024, 768)
    # 4. run action
    try:
        print("Run action.")
        driver.implicitly_wait(10)
        driver.get(input_url)
        for temp_action in input_action_list:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, temp_action['xpath'])))
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, temp_action['xpath'])))
            time.sleep(1)
            if temp_action['type'] == 'click':
                driver.find_element(By.XPATH, temp_action['xpath']).click()
            if temp_action['type'] == 'write':
                driver.find_element(By.XPATH, temp_action['xpath']).send_keys(temp_action['text'])
    except Exception as ex:
        print('Exception:' + str(ex))
    finally:
        driver.quit()
        print("Browser closed at " + datetime.datetime.now().strftime("%H:%M:%S") + ".")
    return


def main():
    print("Auto Report Body Temperature \n" \
          "report at 9, 12, 18 on weekdays")
    account = input("Enter Account: ")
    password = getpass.getpass("Enter Password: ")
    schedule_auto_report_body_temp(account, password)


if __name__ == "__main__":
    main()