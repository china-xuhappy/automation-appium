# -*- coding: utf-8 -*-
import json

import requests
from selenium.webdriver.support.ui import WebDriverWait
import selenium.common.exceptions
import time

from controller.appium.models import UiActivitys
from utils.appium_utils import swipe_up, swipe_down, swipe_left, swipe_right
from utils.assert_utils import assertEqual
from utils.variable import GetVariable as common


class OperateElement(object):
    """
    此脚本主要用于查找元素是否存在，操作页面元素
    """

    def __init__(self, driver=""):
        self.driver = driver

    def findElement(self, operate):
        try:
            element = WebDriverWait(self.driver, common.WAIT_TIME_LONG).until(
                lambda x: elements_by(operate, self.driver))

            print(element)
            return element
        except selenium.common.exceptions.TimeoutException as e:
            return {
                "status": False,
                "errorContent": {"hint": "findElement： 获取元素失败", "content": str(e)},
                "errorCode": common.ElementNotfound
            }
        except selenium.common.exceptions.NoSuchElementException as e:
            print("找不到数据", operate)
            return {
                "status": False,
                "errorContent": {"hint": "findElement： 获取元素失败", "content": str(e)},
                "errorCode": common.ElementNotfound
            }

    def operate_element(self, operate):
        elements = {
            common.CLICK: lambda: self.operate_click(operate),
            common.SEND_KEYS: lambda: self.send_keys(operate),
            common.SWITCHUI: lambda: self.switch_ui(operate),
            common.BACK: lambda: self.back(),

            common.SWIPETOP: lambda: swipe_up(self.driver),
            common.SWIPEDOWN: lambda: swipe_down(self.driver),
            common.SWIPELEFT: lambda: swipe_left(self.driver),
            common.SWIPERIGHT: lambda: swipe_right(self.driver),

            common.SKIP: lambda: skip(operate, self.driver),
            common.APPEAR: lambda: appear(operate, self.driver),
        }
        return elements[operate["operation"]]()

    def back(self):
        """
        返回键
        :return:
        """
        self.driver.press_keycode(common.KEYCODE_BACK)
        return {"status": True}

    def operate_click(self, operate):
        """
        点击方法
        :param operate:
        :return:
        """
        element = operate["element"]
        try:
            if element["element_type"] == common.find_element_by_id or element[
                "element_type"] == common.find_element_by_name or \
                    element["element_type"] == common.find_element_by_xpath:
                self.findElement(element).click()

            if element["element_type"] == common.find_elements_by_id or element[
                "element_type"] == common.find_elements_by_name:
                self.findElement(element)[element["index"]].click()

            return {"status": True}
        except Exception as e:
            return {"status": False, "errorContent": {"hint": "operate_click： 点击元素失败", "content": str(e)}, "errorCode": common.ClickError}

    def send_keys(self, operate):
        """
        输入方法
        :param operate:
        :return:
        """
        try:
            element = operate["element"]

            print("输入:", element["content"])
            self.findElement(element).send_keys(element["content"])
            return {"status": True}

        except Exception as e:
            return {"status": False, "errorContent": {"hint": "send_keys： 输入元素失败", "content": str(e)}, "errorCode": common.SendKeysError}

    def switch_ui(self, operate):
        """
        切换界面,
        :param operate:
        :return:
        """
        try:
            activityId = operate["activityObj"]["activityId"]
            activity = UiActivitys.query.filter(UiActivitys.id == activityId).first()

            current_activity = self.driver.current_activity  # 当前的页面
            time.sleep(1)
            expect_activity = activity.activity_path  # 需要跳转的页面
            if current_activity == expect_activity:  # 如果当前页面 和 需要跳转的一直 则不做操作. 主要是给一个测试用例执行失败，然后跳转用的
                return {"status": True}

            # self.driver.start_activity(app_package="com.Autoyol.auto", app_activity=activity.activity_path)
        except Exception as e:
            return {"status": False, "errorContent": {"hint": "switch_ui： 切换页面失败", "content": str(e)}, "errorCode": common.SwitchUiError}

        return {"status": True}


def skip(operate, driver):
    """
    断言跳转 是否跳转到某个界面

    True 测试成功
    False 断言失败 有图片地址
    :param operate:
    :param driver:
    :return:
    """

    activityId = operate["activityObj"]["activityId"]
    activity = UiActivitys.query.filter(UiActivitys.id == activityId).first()

    expect_activity = activity.activity_path  # 预计
    actual_activity = ""
    isError = False
    i = 0
    while i <= 3:  # 预防未跳转过去，循环断言三次。
        actual_activity = driver.current_activity  # 实际结果
        if assertEqual(expect_activity, actual_activity):
            isError = True
            break
        i += 1
        time.sleep(1)

    if not isError:
        return {
            "status": False,
            "errorContent": {
                "hint": "skip ：页面跳转失败- 预期结果: (" + expect_activity + ") 实际结果: (" + actual_activity + ")",
                "content": "跳转失败"
            },
            "errorCode": common.SkipError
        }

    return {"status": True}


def appear(operate, driver):
    """
    断言出现，判断是否出现某个元素
    :param operate:
    :param driver:
    :return:
    """
    element = operate["element"]
    try:
        WebDriverWait(driver, common.WAIT_TIME_SHORT).until(lambda x: elements_by(element, driver))
        return {"status": True}

    except selenium.common.exceptions.TimeoutException as e:
        print("超时")
        return {
            "status": False,
            "errorContent": {
                "hint": "appear：断言元素出现失败- 预期结果: (" + str(json.dumps(obj=element, ensure_ascii=False)) + ") 实际结果: (" + "None" + ")",
                "content": str(e)
            },
            "errorCode": common.AppearError
        }
    except selenium.common.exceptions.NoSuchElementException as e:
        print("找不到数据")
        return {
            "status": False,
            "errorContent": {
                "hint": "appear： 断言元素出现失败- 预期结果: (" + str(json.dumps(obj=element, ensure_ascii=False)) + ") 实际结果: (" + "None" + ")",
                "content": str(e)
            },
            "errorCode": common.AppearError
        }


# 封装常用的标签
def elements_by(operate, driver):
    elements = {
        common.find_element_by_id: lambda: driver.find_element_by_id(operate["element_path"]),
        common.find_element_by_name: lambda: driver.find_element_by_name(operate['element_path']),
        common.find_element_by_xpath: lambda: driver.find_element_by_xpath(operate["element_path"]),
        common.find_element_by_class_name: lambda: driver.find_element_by_class_name(operate['element_path']),

        common.find_elements_by_id: lambda: driver.find_elements_by_id(operate["element_path"]),
        common.find_elements_by_name: lambda: driver.find_elements_by_name(operate['element_path'])[operate['index']],
        common.find_elements_by_class_name: lambda: driver.find_elements_by_class_name(operate['element_path'])[
            operate['index']]
    }
    return elements[operate["element_type"]]()
