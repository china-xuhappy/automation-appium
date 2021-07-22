from concurrent.futures.thread import ThreadPoolExecutor

from flask_sqlalchemy import SQLAlchemy
from redis import Redis
from flask_pymongo import PyMongo

db = SQLAlchemy(session_options={"autoflush": False})
redis_test2 = None # Redis
mongo = PyMongo()

executor = ThreadPoolExecutor(max_workers=10)

appium_drivers = {}  # 存储appium driver 操作时方便知道是那个driver  可能会有多个
