from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import random

option = webdriver.ChromeOptions()
option.add_experimental_option('excludeSwitches', ['enable-automation'])  # 这里去掉window.navigator.webdriver的特性
option.add_argument("--disable-blink-features=AutomationControlled")
option.add_argument("window-size=1200x600")


class QP(object):
    def __init__(self):
        self.login_url = "https://kyfw.12306.cn/otn/resources/login.html"
        self.login_success_url = "https://kyfw.12306.cn/otn/view/index.html"
        # 苏州北-衢州
        # self.query_url = 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs=%E8%8B%8F%E5%B7%9E%E5%8C%97,' \
        #                  'OHH&ts=%E8%A1%A2%E5%B7%9E,QEH&date=2022-05-16&flag=N,N,Y '
        # 南昌-衢州
        self.query_url = 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs=%E5%8D%97%E6%98%8C,' \
                         'NCG&ts=%E8%A1%A2%E5%B7%9E,QEH&date=2022-05-16&flag=N,N,Y '
        self.confirm_passenger_url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        self.driver = webdriver.Chrome(options=option)
        self.from_station = '南昌'
        # self.from_station = '苏州北'
        self.to_station = '衢州'
        self.departure_time = '2022-05-16'
        # self.departure_time = '2022-05-14'
        self.passengers = '徐梓婷'.split(',')
        self.train_id = 'G7375,G1496'.split(',')

    def move_to_gap(self, slider, tracks):
        """
        拖动滑块
        :param slider: 滑块
        :param tracks: 轨迹
        :return:
        """
        # 模拟滑动滑块
        action = ActionChains(self.driver)
        action.click_and_hold(slider).perform()
        # action.reset_actions()   # 清除之前的action
        for i in tracks:
            action.move_by_offset(xoffset=i, yoffset=0).perform()
        # time.sleep(0.5)
        action.release().perform()

    def get_tracks(self, distance):
        """
        根据偏移量获取移动轨迹
        :param distance:偏移量
        :return:移动轨迹
        """
        # 移动轨迹
        tracks = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 4 / 5
        # 计算间隔
        t = 1
        # 初速度
        v = random.randint(0, 9)
        while current < distance:
            if current < mid:
                # 加速度为正2
                a = random.randint(5, 9)
            else:
                # 加速度为负3
                a = -3
            # 初速度v0
            v0 = v
            # 当前速度
            v = v0 + a * t
            # 移动距离
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹
            tracks.append(round(move))
        return tracks

    def _auth(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'nc_1__scale_text'))
        )
        sliding_text = self.driver.find_element(By.ID, 'nc_1__scale_text')
        sliding_btn = self.driver.find_element(By.ID, 'nc_1_n1z')
        distance = sliding_text.size['width'] - sliding_btn.size['width']
        tracks = self.get_tracks(distance)
        # print(tracks)
        self.move_to_gap(sliding_btn, tracks)

    def login(self):
        username = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'J-userName'))
        )

        # WebDriverWait(self.driver, 10).until(
        #     EC.visibility_of_element_located((By.ID, 'J-userName'))
        # )
        # username = self.driver.find_element(By.ID, 'J-userName')
        # self.driver.implicitly_wait(10)
        # ActionChains(self.driver).move_to_element(username).click(username).perform()
        username.send_keys('13184643209')

        password = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'J-password'))
        )
        # self.driver.implicitly_wait(10)
        # ActionChains(self.driver).move_to_element(password).click(password).perform()
        password.send_keys('2020njdx')

        login = self.driver.find_element(By.ID, 'J-login')
        login.click()

        # 滑块验证
        self._auth()

    # -----------------------------------------------------------------------------------------------

    def _login(self):
        self.driver.get(self.login_url)

        self.login()

        WebDriverWait(self.driver, 10).until(
            EC.url_to_be(self.login_success_url)
        )

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'btn.btn-primary.ok'))
        )

        self.driver.find_element(By.CLASS_NAME, 'btn.btn-primary.ok').click()

        print("Login Success!")

    def _query(self):
        self.driver.get(self.query_url)

        # TODO# 进入查询界面将窗口关闭
        WebDriverWait(self.driver, 100).until(
            EC.presence_of_element_located((By.ID, 'qd_closeDefaultWarningWindowDialog_id'))
        )

        # 应该用id
        # 这个页面class = btn92s的不止一个
        close = self.driver.find_element(By.ID, 'qd_closeDefaultWarningWindowDialog_id')
        close.click()

        # 等待填入信息
        # WebDriverWait(self.driver, 100).until(
        #     EC.text_to_be_present_in_element_value((By.ID, 'fromStationText'), self.from_station)
        # )
        #
        # WebDriverWait(self.driver, 100).until(
        #     EC.text_to_be_present_in_element_value((By.ID, 'toStationText'), self.to_station)
        # )
        #
        # WebDriverWait(self.driver, 100).until(
        #     EC.text_to_be_present_in_element_value((By.ID, 'train_date'), self.departure_time)
        # )

        query_btn = self.driver.find_element(By.ID, 'query_ticket')
        query_btn.click()

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, ".//tbody[@id='queryLeftTable']/tr"))
        )

        train_list = self.driver.find_elements(By.XPATH, ".//tbody[@id='queryLeftTable']/tr[not(@datatran)]")

        while True:
            flag = False
            for train in train_list:
                train_id = train.find_element(By.CLASS_NAME, 'number').text
                if train_id in self.train_id:
                    left_ticket = train.find_element(By.XPATH, ".//td[4]").text
                    print("票状态:" + left_ticket)
                    # if self.driver.current_url != self.confirm_passenger_url:
                    #     print("No")
                    if left_ticket == '有' or left_ticket.isdigit():
                        reserve_btn = train.find_element(By.CLASS_NAME, 'btn72')
                        reserve_btn.click()
                        flag = True
                        break
            if flag:
                break

        self.driver.implicitly_wait(10)
        username = self.driver.find_elements(By.ID, 'login')
        # if self.driver.current_url != self.confirm_passenger_url:
        if len(username) != 0:
            print(len(username))
            print(username)
            # return
            # self.login()
        # self.login()

        WebDriverWait(self.driver, 10).until(
            EC.url_to_be(self.confirm_passenger_url)
        )

    def _order_ticket(self):
        # 看乘客信息有没有出现
        # WebDriverWait(self.driver, 10).until(
        #     EC.presence_of_element_located((By.XPATH, ".//ul[@id='normal_passenger_id']/li"))
        # )
        self.driver.implicitly_wait(10)
        passengers = self.driver.find_elements(By.XPATH, ".//ul[@id='normal_passenger_id']/li/label")

        while len(passengers) == 0:
            self._query()
            # WebDriverWait(self.driver, 10).until(
            #     EC.presence_of_element_located((By.XPATH, ".//ul[@id='normal_passenger_id']/li"))
            # )
            self.driver.implicitly_wait(10)
            passengers = self.driver.find_elements(By.XPATH, ".//ul[@id='normal_passenger_id']/li/label")

        for p in passengers:
            p_name = p.text
            if p_name in self.passengers:
                p.click()

        submit_btn = self.driver.find_element(By.ID, 'submitOrder_id')
        submit_btn.click()

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'dhtmlx_wins_body_outer'))
        )

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'qr_submit_id'))
        )

        confirm = self.driver.find_element(By.ID, 'qr_submit_id')
        # while confirm:
        #     confirm.click()
        #     confirm = self.driver.find_element(By.ID, 'qr_submit_id')
        return

    def run(self):
        self._login()
        self._query()
        self._order_ticket()


if __name__ == '__main__':
    qp = QP()
    qp.run()
