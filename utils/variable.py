__author__ = 'shikun'


# 查找元素的方式
class GetVariable(object):
    NAME = "name"
    ID = "id"
    XPATH = "xPath"
    INDEX = "index"

    find_element_by_id = "ID"
    find_element_by_xpath = "XPath"
    find_element_by_class_name = "ClassName"
    find_element_by_name = "Name"

    # 后面暂不支持
    find_elements_by_id = "IDS"
    find_elements_by_name = "by_names"
    find_element_by_link_text = "by_link_text"
    find_elements_by_link_text = "by_link_texts"
    find_elements_by_xpath = "by_xpaths"
    find_elements_by_class_name = "class_names"
    SELENIUM = "selenium"
    APPIUM = "appium"
    ANDROID = "android"
    IOS = "ios"
    IE = "ie"
    FOXFIRE = "foxfire"
    CHROME = "chrome"

    CLICK = "点击"
    SWIPELEFT = "左滑"
    SWIPERIGHT = "右滑"
    SWIPETOP = "上滑"
    SWIPEDOWN = "下滑"

    SEND_KEYS = "输入"
    BACK = "返回"

    # 错误日志
    ElementNotfound = 00
    SendKeysError = 0o1
    ClickError = 0o2
    SwitchUiError = 0o3
    SwipeError = 0o4

    # assert
    SkipError = 11
    AppearError = 12

    WAIT_TIME_LONG = 10
    WAIT_TIME_SHORT = 5

    # 断言
    SKIP = "断言跳转"
    APPEAR = "断言出现"

    SWITCHUI = "切换界面"


    #物理按键
    KEYCODE_HOME = 3 #HOME建
    KEYCODE_BACK = 4 #返回键

    KEYCODE_ENTER  = 66 #回车键
    KEYCODE_ESCAPE = 111 #ESC键
