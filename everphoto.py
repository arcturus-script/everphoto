from tools import handler, dateTime_format
import hashlib
import requests as re


# 登录地址
LOGIN_URL = "https://web.everphoto.cn/api/auth"

# 签到地址
CHECKIN_URL = "https://openapi.everphoto.cn/sf/3/v4/PostCheckIn"

# 每日奖励
DAILY_REWARD = "https://openapi.everphoto.cn/sf/3/v4/MissionRewardClaim"

# 备注, 收藏等任务共同的 api
CMD = "https://openapi.everphoto.cn/sf/3/v4/PostSyncCommand"

# 任务状态回调
TASKREPORT = "https://openapi.everphoto.cn/sf/3/v4/MissionReport"


class Everphoto:
    def __init__(self, **config) -> None:
        self.__account = config.get("account")
        self.__password = config.get("password")
        self.userInfo = {}
        self.country_code = config.get("country", "+86")
        self.cmd = 1  # task id
        self.needTask = config.get("tasks", False)
        self.headers = {
            "user-agent": "EverPhoto/4.5.0 (Android;4050002;MuMu;23;dev)",
            "application": "tc.everphoto",
        }

    # 获取 md5 加密后的密码
    def get_pwd_md5(self) -> str:
        salt = "tc.everphoto."
        pwd = salt + self.__password
        md5 = hashlib.md5(pwd.encode())
        return md5.hexdigest()

    # 登陆
    def login(self):
        try:
            data = {
                "mobile": f"{self.country_code}{self.__account}",
                "password": self.get_pwd_md5(),
            }

            print(f"++ 开始登录账号 {self.__account} ++")

            res = re.post(LOGIN_URL, data=data, headers=self.headers).json()

            if res.get("code") == 0:
                print(f"++ 登录账号 {self.__account} 成功 ++")

                data = res.get("data")

                self.headers.update(
                    {
                        "authorization": f"Bearer {data['token']}",
                    },
                )

                profile = data["user_profile"]

                self.userInfo.update(
                    {  # 账号
                        "account": self.__account,
                        # 用户名
                        "name": profile["name"],
                        # vip等级
                        "vip": profile.get("vip_level"),
                        # 创建时间
                        "created": dateTime_format(profile["created_at"]),
                        # 注册时长
                        "day": profile["days_from_created"],
                    },
                )

                return {
                    "status": True,
                }
            else:
                raise Exception(res.get("message"))
        except Exception as e:
            print(f"[error] 登录账号 {self.__account} 时出现错误, 原因: {e}")

            return {
                "status": False,
                "message": e,
            }

    # 签到
    def checkin(self):
        try:
            headers = {
                "content-type": "application/json",
                "host": "openapi.everphoto.cn",
                "connection": "Keep-Alive",
            }

            headers.update(self.headers)

            print(f"++ 账号 {self.__account} 开始签到 ++")

            res = re.post(CHECKIN_URL, headers=headers).json()

            code = res.get("code")

            if code == 0:
                print(f"++ 账号 {self.__account} 签到成功 ++")

                data = res.get("data")

                if data.get("checkin_result") is True:
                    rwd = data["reward"] / (1024 * 1024)  # 今日获得
                    msg = "签到成功"
                else:
                    rwd = 0
                    msg = "今日已签到"

                return {
                    "status": True,
                    "reward": rwd,
                    "message": msg,
                    # 连续签到天数
                    "continuity": data.get("continuity"),
                    # 总计获得
                    "total": data.get("total_reward") / (1024 * 1024),
                    # 明日可获得
                    "tomorrow": data.get("tomorrow_reward") / (1024 * 1024),
                }
            elif code == 20104:
                # 未登录
                raise Exception(res.get("message"))
            elif code == 30001:
                # 服务器内部错误
                raise Exception(res.get("message"))
            else:
                raise Exception("其他错误")
        except Exception as e:
            print(f"[error] 账号 {self.__account} 签到时出现错误, 原因: {e}")

            return {
                "status": False,
                "message": f"签到失败, 原因: {e}",
            }

    # 获取任务奖励
    def reward(self):
        headers = {
            "content-type": "application/json",
            "host": "openapi.everphoto.cn",
            "connection": "Keep-Alive",
        }

        headers.update(self.headers)

        # 任务奖励列表
        tasks = {
            "收藏": {"mission_id": "star"},
            "隐藏": {"mission_id": "hide"},
            "相册": {"mission_id": "add_to_album"},
            "备注": {"mission_id": "remark"},
        }

        # 状态信息, 将会运用到消息推送
        codeMap = {
            0: "获取奖励成功",
            20128: "任务状态不正确",
            30005: "系统内部错误",
        }

        print("+++++++ 开始完成每日任务 +++++++")

        for key, task in tasks.items():
            resp = re.post(TASKREPORT, headers=headers, json=task).json()

            if resp.get("code") == 0:
                print(f"[success] {key}")
            else:
                print(f"[failed] {key} --> {resp.get('message')}")

        print("+++++++ 获取每日任务奖励 +++++++")

        res = {}

        for key, task in tasks.items():
            resp = re.post(DAILY_REWARD, headers=headers, json=task).json()

            msg = codeMap.get(resp["code"], "error")

            print(f"[{msg}] {key}")

            res[key] = msg

        return res

    @handler
    def start(self):
        r = self.login()

        if r.get("status"):
            result = {}
            result.update(self.userInfo)

            res = self.checkin()  # 签到

            result.update(res)

            # 每日任务
            if self.needTask:
                result.update(self.reward())

            return result
        else:
            return {
                "status": False,
                "message": f"登录失败, 原因: {r['message']}",
                "account": self.__account,
            }
