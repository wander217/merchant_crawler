import copy
import json
import threading
import time
import numpy as np
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
from threading import Thread


class HouseHoldTaxInfo:
    def __init__(self, url: str, city_title: dict):
        self.data = []
        self.driver = None
        self.url = url
        self.city_title = city_title
        self.open()

    def open(self):
        executable_path: str = r"F:\project\python\merchant_crawler\chromedriver_win32\chromedriver.exe"
        self.driver = Chrome(executable_path=executable_path)
        self.driver.get(self.url)

    def do_crawl(self):
        tinh_selection = self.driver.find_element(By.ID, "maTinh")
        tinh_choice = Select(tinh_selection)
        tinh_choice.select_by_value(self.city_title['id'])
        time.sleep(1)
        self.do_crawl_quan_huyen()

    def do_crawl_quan_huyen(self):
        quan_huyen_selection = self.driver.find_element(By.ID, "maHuyen")
        district_title: list = self.city_title['district']
        for i, item in enumerate(district_title):
            quan_huyen_choice = Select(quan_huyen_selection)
            quan_huyen_choice.select_by_value(item['id'])
            find_btn = self.driver.find_element(By.ID, "nttSearchButton")
            action = ActionChains(self.driver)
            action.click(on_element=find_btn)
            action.perform()
            time.sleep(1)
            self.do_get_page(item['id'])
            self.data.clear()

    def do_get_page(self, item):
        while True:
            table = self.driver.find_element(By.CLASS_NAME, "ta_border")
            rows = table.find_elements(By.TAG_NAME, "tr")[2:]
            for row in rows:
                try:
                    self.data.append([col.text for col in row.find_elements(By.TAG_NAME, "td")])
                except Exception as e:
                    print(e)
            self.do_save(item)
            try:
                time.sleep(1)
                next_btn = self.driver.find_element(By.ID, "nextPage")
                action = ActionChains(self.driver)
                action.click(on_element=next_btn)
                action.perform()
                time.sleep(1.5)
            except Exception as e:
                break

    def do_save(self, huyen_code: str):
        head = ("stt", "ho_ten", "ma_so_thue",
                "ki_lap_bo", "dia_chi",
                "nganh_nghe", "doanh_thu",
                "tong_so_thue", "thue_gtgt",
                "thue_tncn", "thue_ttdb",
                "thue_tai_nguyen", "thue_bvmt",
                "phi_bvmt")
        df = pd.DataFrame(index=head, data=np.transpose(self.data, (1, 0)))
        df.transpose().to_excel(r"data/{}_{}.xlsx".format(self.city_title['id'], huyen_code))


def do_crawl(url, selected_data):
    crawler = HouseHoldTaxInfo(url, city_title=selected_data)
    crawler.do_crawl()


if __name__ == "__main__":
    url = r'https://www.gdt.gov.vn/wps/portal/home/hct'
    district_data = r'./district.json'
    data = json.loads(open(district_data, 'r', encoding='utf-8').read())
    select_data = None
    for item in data:
        if item['name'] == 'Hà Nội':
            select_data = item
            break

    thread_num = 3
    data_len = len(select_data['district'])
    part_len = data_len // thread_num
    threads = []
    for i in range(thread_num):
        new_data = select_data['district'][i * part_len:min([(i + 1) * part_len, data_len])]
        tmp = copy.deepcopy(select_data)
        tmp['district'] = new_data
        thread = Thread(target=do_crawl, args=(url, tmp))
        threads.append(thread)

    for i in range(thread_num):
        threads[i].start()

    for i in range(thread_num):
        threads[i].join()
