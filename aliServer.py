from aliCheck import AliCheck
from flask import Flask, request

app = Flask(__name__)


@app.route('/captcha', methods=['POST'])
def captcha():
    app_key = request.json['appId']
    app_scene = request.json['scene']
    print("app_key:{} app_scene:{}".format(app_key, app_scene))
    resSession = AliCheck(app_key=app_key, app_scene=app_scene).getCaptchaParams()
    return resSession


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000)
