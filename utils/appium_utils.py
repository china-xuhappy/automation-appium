import os
import subprocess
import time
from random import randint
from utils.variable import GetVariable as common
import requests

# 向上滑动
from sqlalchemy import and_

from controller.appium.models import UiAppium


def swipe_up(driver, t=500, n=1):
    try:
        s = driver.get_window_size()
        x1 = s['width'] * 0.5  # x坐标
        y1 = s['height'] * 0.75  # 起点y坐标
        y2 = s['height'] * 0.25  # 终点y坐标
        for i in range(n):
            driver.swipe(x1, y1, x1, y2, t)
    except Exception as e:

        return {"status": False, "errorContent": {"hint": "swipe_up： 上滑失败", "content": str(e)}, "errorCode": common.SwipeError}

    return {"status": True}


# 向下滑动
def swipe_down(driver, t=500, n=1):
    try:
        s = driver.get_window_size()
        x1 = s['width'] * 0.5  # x坐标
        y1 = s['height'] * 0.25  # 起点y坐标
        y2 = s['height'] * 0.75  # 终点y坐标
        for i in range(n):
            driver.swipe(x1, y1, x1, y2, t)
    except Exception as e:
        return {"status": False, "errorContent": {"hint": "swipe_up： 下滑失败", "content": str(e)}, "errorCode": common.SwipeError}

    return {"status": True}


# 向左滑动
def swipe_left(driver, t=888, n=1):
    try:
        s = driver.get_window_size()
        x1 = s['width'] * 0.85
        y1 = s['height'] * 0.5
        x2 = s['width'] * 0.20
        for i in range(n):
            driver.swipe(x1, y1, x2, y1, t)
    except Exception as e:
        return {"status": False, "errorContent": {"hint": "swipe_up： 左滑失败", "content": str(e)}, "errorCode": common.SwipeError}

    return {"status": True}


def swipe_right(driver, t=500, n=1):

    try:
        l = driver.get_window_size()
        x1 = l['width'] * 0.25
        y1 = l['height'] * 0.5
        x2 = l['width'] * 0.75
        for i in range(n):
            driver.swipe(x1, y1, x2, y1, t)
    except Exception as e:
        return {"status": False, "errorContent": {"hint": "swipe_up： 右滑失败", "content": str(e)}, "errorCode": common.SwipeError}

    return {"status": True}


def get_device_list():
    """
    获取设备列表
    :return:
    """
    devices = []
    result = subprocess.Popen("adb devices", shell=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE).stdout.readlines()
    result.reverse()

    for line in result[1:]:
        if b"attached" not in line.strip():
            devices.append(str(line.split()[0], encoding="utf-8"))

        else:
            break
    return devices


def start_appium_server(address, udid, port):
    """
    启动appium 服务
    :return:
    """
    # subprocess.Popen(
    #     "start appium --address {address} --port {port} --udid {udid} -bp {bp}  --command-timeout {timout} "
    #     "--session-override".format(address=address, port=port, udid=udid, bp=bp, timout=300), shell=True,
    #     stdout=subprocess.PIPE)

    os.system("start appium --address {address} --port {port} --udid {udid} --command-timeout {timout} "
              "--session-override".format(address=address, port=port, udid=udid, timout=60 * 60))
    while True:
        time.sleep(5)
        if requests.get("http://{address}:{port}/wd/hub/status".format(address=address, port=port)):
            return True


def get_appium_port():
    """
    获取appium 启动时的port
    :return:
    """
    while True:
        port = randint(9900, 9999)  # 随机获取port
        # 未启动返回port
        if get_connect_appium_pid(port) == 0:
            return port


def get_connect_appium_pid(port):
    """
    通过port 获取正在运行的pid
    :param port:
    :return:
    """
    # 查找对应端口的pid
    cmd_find = 'netstat -aon | findstr %s' % port

    result = os.popen(cmd_find)
    text = result.read()
    if text != "":
        text = text.split("\n")[0]
        pid = text[-5:]
        return pid

    return 0


def kill_appium_server(port):
    """
    关闭appium服务
    :param port:
    :return:
    """
    pid = get_connect_appium_pid(port)
    if pid != 0:
        cmd_kill = 'taskkill -f -pid %s' % pid
        os.popen(cmd_kill)
        print("apppium-server killed: ", cmd_kill)
        return True
    else:
        print("The appium-server port is not occupied and is available")

    return False
