#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.support.wait import WebdriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup as Soup
import pandas as pd
import numpy as np
import re


class HSR_crawler():


    def __init__(self):

        self.driver = webdriver.Chrome()
        self.driver.get("http://www.google.com")

    def get_target(self, target_name):

        WebdriverWait(self.driver,10).until(EC.presence_of_element_located((By.NAME,"q")))
        elem = self.driver.find_element_by_name("q")
        elem.clear()
        elem.send_keys(target_name)
        elem.send_keys(Keys.RETURN)
        soup = Soup(self.driver.page_source,"html.parser")
        web_adddress = soup.find_all("div",class_="usJj9c")[0].a['href']
        self.driver.get(soup.find_all("div",class_="usJj9c")[0].a['href'])

    def hsr_search_setting(self):

        WebdriverWait(self.driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"body > div.swal2-container.swal2-center.swal2-noanimation > div > div.swal2-actions > button.swal2-confirm.swal2-styled")))
        self.driver.find_element_by_css_selector("body > div.swal2-container.swal2-center.swal2-noanimation > div > div.swal2-actions > button.swal2-confirm.swal2-styled").click()
        self.driver.find_element_by_css_selector("#select_location01").click()
        select = Select(self.driver.find_element_by_css_selector("#select_location01"))
        select.select_by_value("TaiPei")
        self.driver.find_element_by_css_selector("#select_location02").click()
        select = Select(self.driver.find_element_by_css_selector("#select_location02"))
        select.select_by_value("TaiNan")
        self.driver.find_element_by_id("start-search").click()

    def get_time_table(self):

        WebdriverWait(self.driver,10).until(EC.presence_of_element_located((By.NAME,"timeTable")))
        soup = Soup(self.driver.page_source,"html.parser")
        head = soup.find_all("div",class_="tr-thead")
        body = soup.find_all("div",class_="tr-tbody")
        tmp = [i.text.replace(' ', '').replace('\n', '') for i in head[0].find_all("div")]
        tmp = tmp[0:5]
        tmp.append('各站時間')
        tmpb = [i.text.replace(' ', '').replace('\n', '') for i in body[0].find_all("div")]
        tmpb_ = [i for i in tmpb if len(i)>3]
        tmpb_ = np.array(tmpb_).reshape(-1, 8)
        tmpb_ = np.delete(tmpb_, [2, 7], axis=1)
        df = pd.DataFrame(tmpb_,columns=tmp)

        return df

    def run(self):
        self.get_target('台灣高鐵')
        self.hsr_search_setting()
        df = get_time_table()
        print(df)

if '__main__' == __name__ :


    crawler = HSR_crawler()
    crawler.run()
