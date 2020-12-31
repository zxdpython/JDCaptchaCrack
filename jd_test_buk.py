import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import cv2, numpy as np
from selenium.webdriver import ActionChains


class JD():
    def __init__(self, account, password):
        self.wait = None
        self.account = account
        self.password = password
        # 设置
        chrome_options = Options()
        # 无头模式启动
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument("--start-maximized")
        # 谷歌文档提到需要加上这个属性来规避bug
        chrome_options.add_argument('--disable-gpu')
        # 设置屏幕器宽高
        chrome_options.add_argument("--window-size=1440,750")
        self.driver = webdriver.Chrome(
            "./chromedriver_win32/chromedriver")
        self.driver.maximize_window()

    def run(self, url):
        self.driver.get(url)
        self.driver.implicitly_wait(4)
        lotab = self.driver.find_elements_by_class_name("login-tab-r")
        lotab[0].click()
        time.sleep(1)
        name = self.driver.find_element_by_id("loginname")
        name.send_keys(self.account)
        time.sleep(1)
        pwd = self.driver.find_element_by_id("nloginpwd")
        pwd.send_keys(self.password)
        time.sleep(1.3)
        logbtn = self.driver.find_element_by_id("loginsubmit")
        logbtn.click()
        print("into")
        time.sleep(5)
        # slide = self.driver.find_element_by_class_name("JDJRV-suspend-slide")
        # if slide:
        #     print("进入滑块验证码流程")
        self.driver.get("https://sz.jd.com/sz/view/indexs.html")
        print("goto")
        trade_button = self.driver.find_element(By.XPATH, '//*[@id="deal"]/a/span')
        trade_button.click()
        print("trade")
        time.sleep(5)
        date_input = self.driver.find_element(By.XPATH, '//*[@id="container"]/div/div[2]/div[1]/div/p')
        ActionChains(self.driver).move_to_element(date_input).perform()
        print("date input")
        time.sleep(3)
        month_label = self.driver.find_element(By.XPATH, '//*[@id="graceDataPikcerPopupWrap24_1609318091717"]/ul/li[3]')
        self.driver.switch_to.frame(1)
        ActionChains(self.driver).move_to_element(month_label).perform()
        print("mouth label")
        time.sleep(3)
        time.sleep(20)
        # 关闭selenium
        self.driver.close()


if __name__ == '__main__':
    url = 'https://passport.jd.com/new/login.aspx'
    account = 'xht10090563'
    password = 'w10090563'
    h = JD(account, password)
    h.run(url)
