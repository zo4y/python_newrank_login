import hashlib
import requests

from random import random
from urllib.parse import urlencode


def ali_check():
    url = "http://127.0.0.1:5000/captcha"

    body = {
        "appId": "FFFF0N00000000009594",
        "scene": "nc_login"
    }

    resp = requests.post(url=url, json=body)
    return resp.json()


def login(account, password):
    url = "https://newrank.cn/nr/user/login/loginByAccount"

    ali = ali_check()
    password = hashlib.md5(password.encode("utf-8")).hexdigest()
    password = hashlib.md5((password + "daddy").encode("utf-8")).hexdigest()

    body = {
        "account": account,
        "adeOrMedia": "0",
        "password": password,  # md5(md5(password)+daddy)
        "scene": "nc_login",
        "sessionId": ali['sessionId'],
        "sig": ali['sig'],
        "state": "1",
        "token": ali['token'],
        "nonce": hashlib.md5(str(random()).encode("utf-8")).hexdigest()[-9:],  # Math.random().toString(16).slice(-9)
    }

    xyz = hashlib.md5(("/nr/user/login/loginByAccount?AppKey=joker&" + urlencode(body)).encode("utf-8")).hexdigest()
    body.setdefault("xyz", xyz)

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "newrank.cn",
        "Origin": "https://newrank.cn",
        "Referer": "https://newrank.cn/user/login",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    }

    resp = requests.post(url=url, data=urlencode(body), headers=headers).json()

    print(resp)


if __name__ == '__main__':
    login("account", "password")
