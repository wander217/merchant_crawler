import json
import time
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


class InfoGetter:
    def __init__(self, url: str):
        self.driver = None
        self.url = url
        self.open()

    def open(self):
        executable_path: str = r"./chromedriver_win32/chromedriver.exe"
        self.driver = Chrome(executable_path=executable_path)
        self.driver.get(self.url)

    def do_crawl(self):
        tinh_selection = self.driver.find_element(By.ID, "maTinh")
        tinh = [{"id": item} for item in tinh_selection.text.split("\n")]
        for i, item in enumerate(tinh):
            tinh_choice = Select(tinh_selection)
            tinh_choice.select_by_visible_text(item['id'])
            time.sleep(2)
            item['district'] = self.do_crawl_quan_huyen()
        self.driver.close()
        return tinh

    def do_crawl_quan_huyen(self):
        huyen_selection = self.driver.find_element(By.ID, "maHuyen")
        huyen = [{"id": item} for item in huyen_selection.text.split("\n")]
        for i, item in enumerate(huyen):
            tinh_choice = Select(huyen_selection)
            tinh_choice.select_by_visible_text(item['id'])
            time.sleep(2)
            xa_selection = self.driver.find_element(By.ID, "maXa")
            item['commune'] = [{"id": item} for item in xa_selection.text.split("\n")]
        return huyen


if __name__ == "__main__":
    url = r'https://www.gdt.gov.vn/wps/portal/home/hct'
    crawler = InfoGetter(url)
    data = crawler.do_crawl()
    save_path = r'./commune.json'
    open(save_path, 'w', encoding='utf-8').write(json.dumps(data, indent=4))
