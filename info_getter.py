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
        executable_path: str = r"F:\project\python\merchant_crawler\chromedriver_win32\chromedriver.exe"
        self.driver = Chrome(executable_path=executable_path)
        self.driver.get(self.url)

    def do_crawl(self):
        tinh_selection = self.driver.find_element(By.ID, "maTinh")
        tinh = [{
            "id": element.get_property("value"),
            "name": element.text
        } for element in tinh_selection.find_elements(By.TAG_NAME, "option")][1:]
        for i, item in enumerate(tinh):
            tinh_choice = Select(tinh_selection)
            tinh_choice.select_by_value(item['id'])
            time.sleep(1)
            item['district'] = self.do_crawl_quan_huyen()
        self.driver.close()
        return tinh

    def do_crawl_quan_huyen(self):
        quan_huyen_selection = self.driver.find_element(By.ID, "maHuyen")
        data = quan_huyen_selection.find_elements(By.TAG_NAME, "option")[1:]
        time.sleep(1)
        quan_huyen = []
        data_len = len(data)
        for i in range(data_len):
            try:
                new_item = {
                    "id": data[i].get_property("value"),
                    "name": data[i].text
                }
            except Exception as e:
                quan_huyen_selection = self.driver.find_element(By.ID, "maHuyen")
                data = quan_huyen_selection.find_elements(By.TAG_NAME, "option")[1:]
                time.sleep(1)
                new_item = {
                    "id": data[i].get_property("value"),
                    "name": data[i].text
                }
            quan_huyen.append(new_item)
        return quan_huyen


if __name__ == "__main__":
    url = r'https://www.gdt.gov.vn/wps/portal/home/hct'
    crawler = InfoGetter(url)
    data = crawler.do_crawl()
    save_path = r'./district.json'
    open(save_path, 'w', encoding='utf-8').write(json.dumps(data, indent=4))

