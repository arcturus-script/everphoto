import hashlib
import requests as req


def handler(fn):
    """
    将结果整理成字典
    """

    def inner(*args, **kwargs):
        res = fn(*args, **kwargs)

        if res["status"]:
            return [
                {
                    "h4": {
                        "content": f"账号: {res['account']}",
                    }
                },
                {
                    "h4": {
                        "content": f"用户名: {res['name']}",
                    }
                },
                {
                    "txt": {
                        "content": res["msg"],
                    },
                    "table": {
                        "content": [
                            ("描述", "内容"),
                            ("今日获得", f"{res['rwd']}M"),
                            ("明日获得", f"{res['tomorrow']}M"),
                            ("总共获得", f"{res['total']}M"),
                            ("连续签到", f"{res['continuity']}天"),
                            ("已注册", f"{res['created']}天"),
                            ("文件数", res["file_num"]),
                        ]
                    },
                },
            ]
        else:
            return [
                {
                    "h4": {
                        "content": f"账号: {res['account']}",
                    },
                    "txt": {
                        "content": res["msg"],
                    },
                }
            ]

    return inner


class Everphoto:
    # 登录地址
    LOGIN_URL = "https://web.everphoto.cn/api/auth"
    # 签到地址
    CHECKIN_URL = "https://api.everphoto.cn/users/self/checkin/v2"

    def __init__(self, account: str, password: str) -> None:
        self.__account = account
        self.__password = password
        self.headers = {
            "User-Agent": "EverPhoto/2.7.0 (Android;2702;ONEPLUS A6000;28;oppo)",
            "application": "tc.everphoto",
        }

    # 获取 md5 加密后的密码
    def get_pwd_md5(self) -> str:
        salt = "tc.everphoto."
        pwd = salt + self.__password
        md5 = hashlib.md5(pwd.encode())
        return md5.hexdigest()

    # 登陆
    def login(self, country_code: str = "+86"):
        try:
            data = {
                "mobile": f"{country_code}{self.__account}",
                "password": self.get_pwd_md5(),
            }
            res = req.post(
                Everphoto.LOGIN_URL,
                data=data,
                headers=self.headers,
            ).json()

            if res.get("code") == 0:
                print(f"登录账号 {self.__account} 成功...")
                return res.get("data")
            else:
                print(f"登录账号 {self.__account} 失败...")
        except Exception as ex:
            print(f"登录账号 {self.__account} 时出现错误...., 原因: {ex}")

    # 签到
    def checkin(self):
        try:
            res = req.post(
                Everphoto.CHECKIN_URL,
                headers=self.headers,
            ).json()

            if res.get("code") == 0:
                print(f"账号 {self.__account} 签到完成...")
                return res.get("data")
            else:
                print(f"账号 {self.__account} 签到失败...")
        except Exception as ex:
            print(f"账号 {self.__account} 签到时出现错误, 原因: {ex}")

    @handler
    def start(self):
        # 开始登陆
        login_res = self.login()
        if login_res is not None:
            profile = login_res.get("user_profile")
            self.headers.update({"authorization": f"Bearer {login_res.get('token')}"})

            # 开始签到
            data = self.checkin()

            if data is not None:

                if data.get("checkin_result") is True:
                    rwd = data["reward"] / (1024 * 1024)  # 今日获得
                    msg = "签到成功"
                else:
                    rwd = 0
                    msg = "已签到"

                return {
                    "status": True,
                    "msg": msg,
                    "account": self.__account,  # 账号
                    "name": profile.get("name"),  # 用户名
                    "created": profile["days_from_created"],  # 注册天数
                    "file_num": profile["estimated_media_num"],  # 文件数
                    "tomorrow": data["tomorrow_reward"] / (1024 * 1024),  # 明日获得
                    "total": data["total_reward"] / (1024 * 1024),  # 总获得空间
                    "continuity": data["continuity"],  # 连续签到天数
                    "rwd": rwd,  # 今日获得
                }
            else:
                return {
                    "status": False,
                    "msg": "签到失败",
                    "account": self.__account,
                }
        else:
            return {
                "status": False,
                "msg": "登录失败",
                "account": self.__account,
            }
