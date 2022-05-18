"""
批量下载教学立方视频
1.打开教学立方网站并登录
"""
import urllib3
import requests
import certifi
import cryptography
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains

option = webdriver.ChromeOptions()
option.add_experimental_option('excludeSwitches', ['enable-automation'])  # 这里去掉window.navigator.webdriver的特性
option.add_argument("--disable-blink-features=AutomationControlled")
option.add_argument("window-size=1200x600")


class VideoDownload(object):
    def __init__(self):
        self.driver = webdriver.Chrome(options=option)
        self.home_url = 'https://teaching.applysquare.com/S/Index/index'
        self.login_url = 'https://teaching.applysquare.com/Home/User/login'
        self.username = '13184643209'
        self.password = '2020njdx'

    """
    登录
    """

    def _login(self):
        # 打开教学立方网址
        self.driver.get(self.login_url)
        # 输入用户名
        """
        element not interactable 问题
        是因为在页面中存在多个 name = email 的 input
        """
        WebDriverWait(self.driver, 100).until(
            EC.presence_of_element_located((By.NAME, 'email'))
        )
        usernames = self.driver.find_elements(By.NAME, 'email')
        for username in usernames:
            if username.get_attribute('placeholder') == '请输入手机号码':
                username.send_keys(self.username)
        # 输入密码
        password = WebDriverWait(self.driver, 100).until(
            EC.presence_of_element_located((By.NAME, 'password'))
        )
        password.send_keys(self.password)
        # 登录按钮
        login_btn = WebDriverWait(self.driver, 100).until(
            EC.presence_of_element_located((By.ID, 'id_login_button'))
        )
        login_btn.click()
        # 等待进入主页面
        WebDriverWait(self.driver, 100).until(
            EC.url_to_be(self.home_url)
        )

    def _inMainVideos(self):
        # 选择相应课程
        course = WebDriverWait(self.driver, 100).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="wrapper"]/div/div/div/div[2]/div/div[3]/div/div[1]/div[2]/h4/span'))
        )
        # course = self.driver.find_element(By.XPATH, '//*[@id="wrapper"]/div/div/div/div[2]/div/div[3]/div/div[1]/div[2]/h4/span')
        course.click()

        # '课件'是否显示出来
        # TODO 存在bug: 有时候课件显示不出来，停滞
        WebDriverWait(self.driver, 100).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="wrapper"]/div/div[1]/div/div/ul/li[2]/a'))
        )
        slides = self.driver.find_elements(By.XPATH, '//*[@id="wrapper"]/div/div[1]/div/div/ul/li[2]/ul/li[2]/a')
        print("课件是否展示:" + str(len(slides)))
        while len(slides) == 0:  # 没有点击'资源'
            resources = WebDriverWait(self.driver, 100).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="wrapper"]/div/div[1]/div/div/ul/li[2]/a'))
            )
            resources.click()
            slides = self.driver.find_elements(By.XPATH, '//*[@id="wrapper"]/div/div[1]/div/div/ul/li[2]/ul/li[2]/a')
        # 获取'课件'元素
        slide = WebDriverWait(self.driver, 100).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="wrapper"]/div/div[1]/div/div/ul/li[2]/ul/li[2]/a'))
        )
        slide.click()

    def _travelVideosAllPages(self):
        # 确定页数
        WebDriverWait(self.driver, 100).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="content_right"]/div/div[1]/div[3]/div[2]/nav/ul/li'))
        )
        pages = self.driver.find_elements(By.XPATH, '//*[@id="content_right"]/div/div[1]/div[3]/div[2]/nav/ul/li')
        last_page = ""
        for i in range(len(pages)):
            text = pages[i].text
            if text == "尾页":
                last_page = pages[i - 1].text
                break
            if text == "下一页":
                last_page = pages[i - 1].text
                break
        if last_page[0] == '.':
            page_num = int(last_page[2])
        else:
            page_num = int(last_page)
        print("共有" + str(page_num) + "页")
        # 遍历每一页
        for i in range(1, page_num + 1):
            # 获得当前所在页
            cur_page = self.driver.find_element(By.XPATH,
                                                '//*[@id="content_right"]/div/div[1]/div[3]/div[2]/nav/ul/li[@class="active"]')
            print("现在在" + cur_page.text + "页,需要去" + str(i) + "页")
            while int(cur_page.text) != i:
                next_page_btn = self.driver.find_elements(By.XPATH,
                                                          '//*[@id="content_right"]/div/div[1]/div[3]/div[2]/nav/ul/li')
                print("click" + next_page_btn[-2].text)
                btn = next_page_btn[-2].find_element(By.XPATH, './/a')
                WebDriverWait(self.driver, 100).until(
                    EC.element_to_be_clickable(btn)
                )
                btn.click()  # TODO click 一次循环后报错 Message: stale element reference: element is not attached to the page document
                while True:
                    try:
                        print("第" + cur_page.text + "页:" + cur_page.get_attribute('class'))
                    except:
                        print("换页成功")
                        break
                break
                cur_page = WebDriverWait(self.driver, 100).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="content_right"]/div/div[1]/div[3]/div[2]/nav/ul/li[@class="active"]'))
                )
                print("现在在" + cur_page.text + "页")
                # break
            # if int(cur_page.text) == i:  # 在预期页面，处理该页面上所有视频
            #     print("处理第" + cur_page.text + "页")
            #     # self._travelVideosInSinglePage()
            #     print("...")
            #     print("处理完毕")
            # break

    def _travelVideosInSinglePage(self):
        # 等待视频和课件加载出来
        WebDriverWait(self.driver, 100).until(
            EC.presence_of_element_located((By.XPATH, '//tbody/tr/td[6]'))
        )
        # 获取视频和课件
        table = self.driver.find_elements(By.XPATH, '//tbody/tr')
        for tr in table:
            # 获取每一个行的资源类型
            tr_type = tr.find_element(By.XPATH, './/td[6]').text  # TODO:也存在报错问题
            if tr_type == '音视频':  # 是音视频时
                title = tr.find_element(By.XPATH, './/td[1]/span').text
                print("title: " + title)
                inVideo = tr.find_element(By.XPATH, './/td[7]/a')  # 获取'查看'a标签
                print("type: " + inVideo.text)
                inVideo.click()
                WebDriverWait(self.driver, 100).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'video'))
                )
                self._dealVideo(title)
                return

    def _dealVideo(self, title):
        # 获取video元素
        src = ''
        while src == '':
            video = WebDriverWait(self.driver, 100).until(
                EC.presence_of_element_located((By.TAG_NAME, 'video'))
            )
            src = video.get_attribute('src')
        print("src(before):" + src)
        # 处理src 直接下载
        new_src = ''
        for i in range(len(src)):
            print(src[i], end=' ')
            if src[i] == '?':
                new_src = src[0:(i - 8)]

        print("\nsrc(after):" + new_src)
        self.driver.get(new_src)

    def run(self):
        # TODO
        """
        1. 解决运行过程中，有些地方会停滞的问题
        2. 已完成一个视频的下载工作，后续需要完成下载该课程下所有视频的工作
        """
        self._login()
        self._inMainVideos()
        self._travelVideosAllPages()
        # self._travelVideosInSinglePage()


if __name__ == '__main__':
    vd = VideoDownload()
    vd.run()
