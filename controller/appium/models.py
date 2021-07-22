"""
和数据库 映射类
"""
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from exts import db
from datetime import datetime


class UiExecuteCase(db.Model):
    """
    appium 跑用例 记录
    """
    __tablename__ = "ui_execute_case"
    id = db.Column(db.Integer(), unique=False, primary_key=True, autoincrement=True)
    caseId = db.Column(db.String(255))
    create_time = db.Column(db.DateTime)  # 创建时间
    source = db.Column(db.String(2))  # 来源：0手动执行，1定时任务

    def __init__(self, caseId):
        self.caseId = caseId
        self.source = 0
        self.create_time = datetime.now()


class UiAppium(db.Model):
    """
    appium 管理
    """
    __tablename__ = "ui_appium"
    id = db.Column(db.Integer(), unique=False, primary_key=True, autoincrement=True)
    appium_port = db.Column(db.String(255))  # appium port
    appium_bp = db.Column(db.String(255))  # appium bp port
    appium_args = db.Column(db.String(255))  # appium 执行参数
    appium_ip = db.Column(db.String(255))  # appium ip
    create_time = db.Column(db.DateTime)  # 创建时间
    status = db.Column(db.String(2))  # 执行状态 0未启动 1启动中

    device_name = db.Column(db.String(255))  # 暂不使用deviceId， 不同项目查SQL不方便。 后期优化

    def __init__(self, appium_port, appium_bp, appium_args, appium_ip, device_name):
        self.appium_port = appium_port
        self.appium_bp = appium_bp
        self.appium_args = appium_args
        self.appium_ip = appium_ip
        self.status = 1
        self.create_time = datetime.now()
        self.device_name = device_name


class UiDevices(db.Model):
    """
    设备表， 存储设备用的
    """
    __tablename__ = "ui_devices"
    id = db.Column(db.Integer(), unique=False, primary_key=True, autoincrement=True)
    device = db.Column(db.String(255))  # 设备udid
    ip = db.Column(db.String(255))  # 设备ip，绑定到那台机器上
    describe = db.Column(db.String(255))  # 设备描述
    userId = db.Column(db.Integer())  # userId
    create_time = db.Column(db.DateTime)  # 创建时间

    device_port = db.Column(db.String(255))  # appium port
    device_bp = db.Column(db.String(255))  # appium bp port

    status = db.Column(db.String(2))  # 状态 0未使用，1正在执行

    def __init__(self, device, ip, userId):
        self.device = device
        self.ip = ip
        self.describe = None
        self.userId = userId
        self.create_time = datetime.now()
        self.status = 0


class UiActivitys(db.Model):
    __tablename__ = "ui_activitys"
    id = db.Column(db.Integer(), unique=False, primary_key=True, autoincrement=True)
    activity_name = db.Column(db.String(255))  # 页面中文名
    activity_path = db.Column(db.String(255))  # Android 配置的activity地址

    def __init__(self, projectName):
        self.projectName = projectName
        self.is_delete = 0
        self.project_type = 0
