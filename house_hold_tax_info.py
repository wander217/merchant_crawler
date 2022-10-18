import copy
import json
import time
import unicodedata
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
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
        self.time_out = 20

    def open(self):
        executable_path: str = r"./chromedriver_win32/chromedriver.exe"
        self.driver = Chrome(executable_path=executable_path)
        self.driver.get(self.url)

    def do_crawl(self):
        for district in self.city_title['district']:
            # for commune in district['commune']:
            self.district_crawl(district)

    def district_crawl(self, district: dict):
        try:
            self.open()
            element_present = EC.presence_of_element_located((By.ID, "maTinh"))
            WebDriverWait(driver=self.driver, timeout=self.time_out).until(element_present)
            time.sleep(2)

            tinh_selection = self.driver.find_element(By.ID, "maTinh")
            tinh_choice = Select(tinh_selection)
            tinh_choice.select_by_visible_text(self.city_title['id'])
            element_present = EC.presence_of_element_located((By.XPATH,
                                                              "/html/body/div/div[1]/div[4]/div[4]/div[2]/div/div[1]/div[1]/div/div/div[2]/div/form/div[2]/select/option[2]"))
            WebDriverWait(driver=self.driver, timeout=self.time_out).until(element_present)
            time.sleep(2)

            quan_huyen_selection = self.driver.find_element(By.ID, "maHuyen")
            quan_huyen_choice = Select(quan_huyen_selection)
            quan_huyen_choice.select_by_visible_text(district['id'])
            element_present = EC.presence_of_element_located((By.XPATH,
                                                              "/html/body/div/div[1]/div[4]/div[4]/div[2]/div/div[1]/div[1]/div/div/div[2]/div/form/div[3]/select"))
            WebDriverWait(driver=self.driver, timeout=self.time_out).until(element_present)
            time.sleep(2)

            # xa_selection = self.driver.find_element(By.ID, "maXa")
            # xa_choice = Select(xa_selection)
            # xa_choice.select_by_visible_text(commune['id'])
            # time.sleep(2)

            find_btn = self.driver.find_element(By.ID, "nttSearchButton")
            action = ActionChains(self.driver)
            action.click(on_element=find_btn)
            action.perform()
            time.sleep(2)

            self.do_get_page(district['id'])
            self.data.clear()
            self.driver.quit()
        except TimeoutException as e:
            print(e)

    def do_get_page(self, district_id: int):
        while True:
            time_out = 5
            element_present = EC.presence_of_element_located((By.XPATH,
                                                              "/html/body/div/div[1]/div[4]/div[4]/div[2]/div/div[1]/div[1]/div/div/div[2]/div/form/div[10]/div[4]/table"))
            WebDriverWait(driver=self.driver, timeout=time_out).until(element_present)
            try:
                table = self.driver.find_element(By.XPATH,
                                                 "/html/body/div/div[1]/div[4]/div[4]/div[2]/div/div[1]/div[1]/div/div/div[2]/div/form/div[10]/div[4]/table")
                cells = table.find_elements(By.TAG_NAME, "td")
                self.data.extend(np.array([cell.text for cell in cells]).reshape(-1, 14).tolist())
            except Exception as e:
                print("Mạng chậm")
            self.do_save(district_id)
            try:
                next_btn = self.driver.find_element(By.ID, "nextPage")
                action = ActionChains(self.driver)
                action.click(on_element=next_btn)
                action.perform()
                time.sleep(2)
            except Exception as e:
                break

    def do_save(self, district_id: int):
        head = ("stt", "ho_ten", "ma_so_thue",
                "ki_lap_bo", "dia_chi",
                "nganh_nghe", "doanh_thu",
                "tong_so_thue", "thue_gtgt",
                "thue_tncn", "thue_ttdb",
                "thue_tai_nguyen", "thue_bvmt",
                "phi_bvmt")
        df = pd.DataFrame(index=head, data=np.transpose(self.data, (1, 0)))
        df.transpose().to_excel(r"data/{}_{}.xlsx".format(self.city_title['id'], district_id))


def do_crawl(url, selected_data):
    crawler = HouseHoldTaxInfo(url, city_title=selected_data)
    crawler.do_crawl()


if __name__ == "__main__":
    url = r'https://www.gdt.gov.vn/wps/portal/home/hct'
    district_data = r'./commune.json'
    data = json.loads(open(district_data, 'r', encoding='utf-8').read())
    select_data = None
    for item in data:
        # if item['name'] == 'TP Hồ Chí Minh':
        if unicodedata.normalize("NFC", item['id']) == unicodedata.normalize("NFC", 'Hà Nội'):
            # if unicodedata.normalize("NFC", item['name']) == unicodedata.normalize("NFC", 'TP Hồ Chí Minh'):
            select_data = item
            break

    thread_num = 10
    data_len = len(select_data['district'])
    part_len = data_len // thread_num
    threads = []
    for i in range(thread_num):
        new_data = select_data['district'][i * part_len:min([(i + 1) * part_len, data_len])]
        tmp = copy.deepcopy(select_data)
        tmp['district'] = new_data
        thread = Thread(target=do_crawl, args=(url, tmp))
        threads.append(thread)

    start = 2
    for i in range(start, start + 1):
        threads[i].start()

    for i in range(start, start + 1):
        threads[i].join()
