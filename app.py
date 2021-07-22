from gevent.pywsgi import WSGIServer
from flask import Flask
from controller.appium import appium
import config
from controller.appium.models import UiDevices
from exts import db, mongo


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    app.register_blueprint(appium)

    db.init_app(app)
    mongo.init_app(app)
    return app


app = create_app()


@app.route('/')
def hello_world():
    return 'Hello World!'.replace("\\\\", "/")


if __name__ == '__main__':
    app.run(host="127.0.0.1", debug=True, port=6060, threaded=True)

"""

#获取apk信息
aapt dump badging E:\aotu.apk


install_app #安装应用
is_app_installed 检查app是否有安装
remove_app 卸载新版本
close_app 关闭应用
start_activity 跳转界面
driver.reset()  # 重新打开APP。 卸载到安装然后打开那样。最新的。
driver.start_activity(app_package="com.Autoyol.auto", app_activity=activity.activity_path)

"""
