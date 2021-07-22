"""
用户相关接口
"""
import time

import requests
from flask import Blueprint, jsonify, g, render_template, request
from flask_restful import Api, Resource, marshal_with, reqparse, fields
from sqlalchemy import and_

from config import URL_PATH
from controller.appium.models import UiExecuteCase, UiAppium, UiDevices
from utils.appium_utils import start_appium_server, swipe_left, kill_appium_server, get_device_list, get_appium_port, \
    get_connect_appium_pid
from utils.operateElement import OperateElement
from utils.utils_tool import get_user_ip

appium = Blueprint('appium', __name__, url_prefix='/appium')
from exts import db, appium_drivers
from appium import webdriver

api = Api(appium)
from utils import restful
# from controller.appium.models import AlterUser
import json


@appium.route("/startAppium", methods=['POST'])
def start_appium():
    """
    启动appium
    :return:
    """
    data = request.get_data()
    json_data = json.loads(data.decode("utf-8"))
    caseId = json_data["caseId"]
    appium_port = json_data["appium_port"]

    if caseId is not None:
        db.session.add(UiExecuteCase(caseId=caseId))

    deviceName = json_data["deviceName"]
    appium_ip = json_data["appium_ip"]

    appiums = UiAppium.query.filter(
        and_(UiAppium.device_name == deviceName, UiAppium.status == 1, UiAppium.appium_port == appium_port)).all()
    if len(appiums) != 0:
        isTrue = False
        for appium in appiums:
            if get_connect_appium_pid(appium.appium_port) == 0:
                # 说明服务已经被终止了，但是数据库没变。  强制终止 或者 电脑关机
                appium.status = 0
                db.session.commit()
                if appium.device_name in appium_drivers:
                    appium_drivers.pop(appium.device_name)
            else:
                isTrue = True

        if isTrue:
            # 该设备服务正在启动，无需重复启动。 直接走下面连接
            return restful.success()

    start_appium_server(address=appium_ip, udid=deviceName, port=appium_port)
    appium_new = UiAppium(appium_port=appium_port, appium_bp=0,
                          appium_args=str(json.dumps(obj={}, ensure_ascii=False)),
                          appium_ip=appium_ip, device_name=deviceName)
    db.session.add(appium_new)

    db.session.commit()

    return restful.success()


@appium.route("/connectAppium", methods=['POST'])
def connect_appium():
    """
    连接appium driver

    1.如果正在连接 给参数是否重新连接。
    2.判断没有连接 自动连接
    :return:
    """
    data = request.get_data()
    json_data = json.loads(data.decode("utf-8"))
    appium_args = json_data["appiumArgs"]
    appPackage = appium_args["appPackage"]
    appActivity = appium_args["appActivity"]
    platformName = appium_args["platformName"]
    platformVersion = appium_args["platformVersion"]
    isAgain = json_data["isAgain"]  # 0无需重新连接，1重新连接
    deviceName = json_data["deviceName"]

    # 查找设备正在连接的appium， 按理说这个数据在启动的时候已经扯平了。 不会出现搜索不对的数据
    appium = UiAppium.query.filter(and_(UiAppium.device_name == deviceName, UiAppium.status == 1)).first()
    if deviceName in appium_drivers and appium is None:  # 没有正在连接的appium，需要连接
        if isAgain == 0:
            return restful.success()

    desired_caps = {"platformName": platformName, "platformVersion": platformVersion, "deviceName": deviceName,
                    "appPackage": appPackage, "appActivity": appActivity, "newCommandTimeout": 60 * 60}

    # cap.setCapability("noSign", "True"); //不重新签名apk
    # cap.setCapability("noReset", "True"); //是否不需要重新安装app

    # 启动完需要开启一个1小时的 清除设备的定时任务
    driver = webdriver.Remote('http://{ip}:{port}/wd/hub'.format(ip=appium.appium_ip, port=appium.appium_port),
                              desired_caps)

    # print(driver.page_source)
    # # print(driver.name)
    # print(driver.application_cache)
    # print(driver.get_settings())
    # print(driver.contexts)
    # print(driver.current_context)
    appium.appium_args = str(json.dumps(obj=desired_caps, ensure_ascii=False))
    appium_drivers[deviceName] = driver

    db.session.commit()

    return restful.success()


@appium.route("/executeStep", methods=['POST'])
def execute_step():
    """
    执行步骤
    :return:
    """
    data = request.get_data()
    operation = json.loads(data.decode("utf-8"))
    print("执行操作参数: ", operation)
    deviceObj = operation["deviceObj"]
    # 执行的时候有可能服务被终止 或者 什么操作。 这个只是就需要强制警告他们 终止测试 或者 重新启动服务
    # get_connect_appium_pid(deviceObj["device_port"]) == 0 这个不能放在前面 不然每次都执行
    if deviceObj["deviceName"] not in appium_drivers:
        return restful.server_error(message="服务没启动好..")

    driver = appium_drivers[deviceObj["deviceName"]]
    result = OperateElement(driver).operate_element(operation)

    if not result["status"]:
        if get_connect_appium_pid(deviceObj["device_port"]) == 0:
            return restful.server_error(message="服务崩溃了...", data=result)

        # 失败
        image_url = "E:\\screenshots\\{name}.png".format(name=str((int(round(time.time())))))
        driver.get_screenshot_as_file(image_url)

        files = {'file': open(image_url, 'rb')}
        resultObj = requests.post("http://10.0.3.246:8083/uploadingImage", files=files).json()
        image_url = resultObj["msg"]

        errorContent = result["errorContent"]
        errorContent["image_url"] = image_url

    print("执行操作返回结果:", result)
    return restful.success(data=result)


@appium.route("/quitServer", methods=['POST'])
def quit_server():
    """
    停止appium服务
    :return:
    """
    data = request.get_data()
    json_data = json.loads(data.decode("utf-8"))
    deviceName = json_data["deviceName"]
    quitType = json_data["quitType"]  # 0关闭appium driver连接， 1关闭所有服务
    ip = json_data["ip"]

    print("deviceName", deviceName)
    appium = UiAppium.query.filter(UiAppium.device_name == deviceName).first()

    devices = UiDevices.query.filter(UiDevices.ip == ip).all()
    for device in devices:
        device.status = 0
        if quitType == 1:
            if device.device in appium_drivers:
                appium_drivers.pop(appium.device_name)
                print("删除成功: ", appium_drivers)
            kill_appium_server(device.device_port)
            appium.status = 0  # 停止

        elif quitType == 0:
            print("删除之前: ", appium_drivers)
            if device.device in appium_drivers:
                appium_drivers[device.device].close_app()
                appium_drivers[device.device].quit()
                appium_drivers.pop(appium.device_name)
                print("删除成功: ", appium_drivers)

    db.session.commit()
    return restful.success()


@appium.route("/getConnectDevices")
def get_connect_devices():
    """
    获取本地正在连接的设备
    :return:
    """
    # 获取可用设备

    return restful.success(data=get_device_list())
