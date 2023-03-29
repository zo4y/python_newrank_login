import json
import os
import random

from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


class AliCheck(object):

    def __init__(self, app_key, app_scene):
        self.options = self.initOptions()
        self._html = self.setBrowser(app_key, app_scene)
        self.browser = webdriver.Chrome(executable_path="bin/chromedriver", options=self.options)

    def setBrowser(self, app_key, app_scene):
        self._html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <script src="https://g.alicdn.com/AWSC/AWSC/awsc.js"></script>
        </head>
        <body>
        <div id="nc"></div>
        <script>
            // 实例化nc
            AWSC.use("nc", function (state, module) {
                // 初始化
                window.nc = module.init({
                    // 应用类型标识。它和使用场景标识（scene字段）一起决定了滑动验证的业务场景与后端对应使用的策略模型。您可以在阿里云验证码控制台的配置管理页签找到对应的appkey字段值，请务必正确填写。
                    appkey: "app_key",
                    //使用场景标识。它和应用类型标识（appkey字段）一起决定了滑动验证的业务场景与后端对应使用的策略模型。您可以在阿里云验证码控制台的配置管理页签找到对应的scene值，请务必正确填写。
                    scene: "app_scene",
                    // 声明滑动验证需要渲染的目标ID。
                    renderTo: "nc",
                    //前端滑动验证通过时会触发该回调参数。您可以在该回调参数中将会话ID（sessionId）、签名串（sig）、请求唯一标识（token）字段记录下来，随业务请求一同发送至您的服务端调用验签。
                    success: function (data) {
                        document.body.innerHTML += "<br /><br /><h2>打码成功！</h2><p><textarea id=\\"mync\\">" + JSON.stringify(data) + "</textarea></p>";
                    },
                    // 滑动验证失败时触发该回调参数。
                    fail: function (failCode) {
                        document.body.innerHTML += "<br /><br /><h2>打码失败！</h2><p><textarea id=\\"mync\\">" + JSON.stringify(failCode) + "</textarea></p>";
                    },
                    // 验证码加载出现异常时触发该回调参数。
                    error: function (errorCode) {
                        document.body.innerHTML += "<br /><br /><h2>验证码出现异常！</h2><p><textarea id=\\"mync\\">" + JSON.stringify(errorCode) + "</textarea></p>";
                    }
                });
            })
        </script>
        </body>
        </html>
        '''
        self._html = self._html.replace("app_key", app_key).replace("app_scene", app_scene)
        with open("static/ali.html", "w", encoding="UTF-8") as file:
            file.write(self._html)
        return self._html

    def initOptions(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument("user-agent=" + UserAgent().chrome)
        self.options.add_argument("--headless")
        return self.options

    def getCaptchaParams(self):
        # 调用函数在页面加载前执行脚本
        with open('static/stealth.js', 'r') as f:
            stealth_js = f.read()

        self.browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': stealth_js})

        self.browser.get("file://" + os.path.abspath("static/ali.html"))
        slideBtn = self.browser.find_element(by=By.CSS_SELECTOR, value=".btn_slide")
        slideOffsetWidth = self.browser.execute_script(
            "return (document.querySelector(\".nc_scale\").clientWidth - document.querySelector(\".nc_iconfont\").clientWidth);")
        actions = ActionChains(self.browser)

        offsets = []  # 规避可疑轨迹
        while slideOffsetWidth > 0:
            myOffset = random.randint(50, 120)
            if slideOffsetWidth < myOffset:
                myOffset = slideOffsetWidth
            slideOffsetWidth -= myOffset
            offsets.append(myOffset)

        actions.click_and_hold(slideBtn).perform()

        for slideWidth in offsets:
            actions.move_by_offset(xoffset=slideWidth, yoffset=0).perform()
        actions.release().perform()

        resSession = None
        while resSession is None:
            try:
                resSession = self.browser.find_element(by=By.CSS_SELECTOR, value="#mync").get_attribute("innerHTML")
            except Exception as e:
                resSession = None

        return json.loads(resSession)
