from ast import Num
import hashlib
import time
import requests as req
from datetime import datetime


def handler(fn):
    def inner(*args, **kwargs):
        res = fn(*args, **kwargs)

        if res["status"]:
            a = [
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
                        "content": res["message"],
                    },
                    "table": {
                        "content": [
                            ("描述", "内容"),
                            ("今日获得", f"{res['reward']}M"),
                            ("明日获得", f"{res['tomorrow']}M"),
                            ("总共获得", f"{res['total']}M"),
                            ("连续签到", f"{res['continuity']}天"),
                            ("注册时间", f"{res['created']}"),
                            ("注册天数", f"{res['day']}天"),
                        ]
                    },
                },
            ]

            if res.get("收藏") is not None:
                a.append(
                    {
                        "txt": {
                            "content": "任务情况",
                        },
                        "table": {
                            "content": [
                                ("任务", "执行结果"),
                                ("收藏", f"{res['收藏']}"),
                                ("隐藏", f"{res['隐藏']}"),
                                ("相册", f"{res['相册']}"),
                                ("备注", f"{res['备注']}"),
                            ]
                        },
                    }
                )

            a.append({"txt": {"content": ""}})

            return a
        else:
            # 登录失败 or 签到失败
            return [
                {
                    "h4": {
                        "content": f"账号: {res['account']}",
                    },
                    "txt": {
                        "content": res["message"],
                    },
                },
                {"txt": {"content": ""}},
            ]

    return inner


# 日期字符串格式化
def dateTime_format(dt: str) -> str:
    try:
        dl = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S+08:00")

        return dl.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        print(f"格式化日期时出错, 原因: {e}")


class Everphoto:
    # 登录地址
    LOGIN_URL = "https://web.everphoto.cn/api/auth"
    # 签到地址
    CHECKIN_URL = "https://openapi.everphoto.cn/sf/3/v4/PostCheckIn"
    # 每日奖励
    DAILY_REWARD = "https://openapi.everphoto.cn/sf/3/v4/MissionRewardClaim"
    # 备注, 收藏
    CMD = "https://openapi.everphoto.cn/sf/3/v4/PostSyncCommand"

    def __init__(
        self,
        account: str,
        password: str,
        country_code: str = "+86",
    ) -> None:
        self.__account = account
        self.__password = password
        self.headers = {
            "user-agent": "EverPhoto/4.5.0 (Android;4050002;MuMu;23;dev)",
            "application": "tc.everphoto",
        }
        self.userInfo = {}
        self.country_code = country_code
        self.cmd = 1  # 执行任务的 id

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
            res = req.post(
                Everphoto.LOGIN_URL,
                data=data,
                headers=self.headers,
            ).json()

            if res.get("code") == 0:
                print(f"🎉 登录账号 {self.__account} 成功")

                data = res.get("data")

                self.headers.update(
                    {"authorization": f"Bearer {data['token']}"},
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
                return {"status": True}
            else:
                raise Exception(res.get("message"))
        except Exception as e:
            print(f"😭 登录账号 {self.__account} 时出现错误, 原因: {e}")

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

            res = req.post(
                Everphoto.CHECKIN_URL,
                headers=headers,
            ).json()

            code = res.get("code")

            if code == 0:
                print(f"🎉 账号 {self.__account} 签到成功")

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
                # 服务器内部错误?
                raise Exception(res.get("message"))
            else:
                raise Exception("其他错误")
        except Exception as e:
            print(f"账号 {self.__account} 签到时出现错误, 原因: {e}")

            return {
                "status": False,
                "message": f"签到失败, 原因: {e}",
            }

    # 获取任务奖励
    def reward(self):
        try:
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

            # 状态信息
            codeMap = {
                0: "获取奖励成功",
                20128: "任务状态不正确",
                30005: "系统内部错误",
            }

            print("+++++获取每日任务奖励+++++")
            res = {}
            for key, task in tasks.items():
                resp = req.post(
                    Everphoto.DAILY_REWARD,
                    headers=headers,
                    json=task,
                ).json()

                print(f"{key} ---> {codeMap.get(resp['code'], '其他错误')}")

                res[key] = codeMap.get(resp["code"], "其他错误")

            return res
        except Exception as e:
            print(f"账号 {self.__account} 获取每日奖励时出现错误, 原因: {e}")

    # 执行命令
    def command(
        self,
        type: str,
        cmd: str,
        params: object,
    ) -> None:
        try:
            headers = {
                "content-type": "application/json",
                "host": "openapi.everphoto.cn",
                "connection": "Keep-Alive",
            }

            headers.update(self.headers)

            cmd = {
                "commands": [
                    {
                        "command": cmd,  # 执行的命令
                        "command_id": self.cmd,
                        "created_at": int(round(time.time() * 1000)),
                        "param": params,
                    }
                ],
                "space_id": 0,
            }

            self.cmd += 1  # 任务 ID 自增

            resp = req.post(
                Everphoto.CMD,
                headers=headers,
                json=cmd,
            ).json()

            res = resp["data"]["results"][0]

            if res["code"] == 0:
                print(f"{type}成功")
            else:
                raise Exception(res["msg"])
        except Exception as e:
            print(f"{type}时出错, 原因: {e}")

    # 做任务
    def task(
        self,
        *,
        asset_id: Num,
        tag_id: Num,
        md5: str,
        memo: str = "( •̀ ω •́ )✧",
    ) -> None:
        tasks = [
            {
                "type": "收藏相片",
                "cmd": "asset_add_to_tag",
                "params": {
                    "asset_ids": [asset_id],
                    "tag_id": 70001,
                    "tag_id_type": 2,
                },
            },
            {
                "type": "取消收藏相片",
                "cmd": "asset_remove_from_tag",
                "params": {
                    "asset_ids": [asset_id],
                    "tag_id": 70001,
                    "tag_id_type": 2,
                },
            },
            {
                "type": "隐藏相片",
                "cmd": "asset_add_to_tag",
                "params": {
                    "asset_ids": [asset_id],
                    "tag_id": 70003,
                    "tag_id_type": 2,
                },
            },
            {
                "type": "取消隐藏相片",
                "cmd": "asset_remove_from_tag",
                "params": {
                    "asset_ids": [asset_id],
                    "tag_id": 70003,
                    "tag_id_type": 2,
                },
            },
            {
                "type": "相片添加到相册",
                "cmd": "asset_add_to_tag",
                "params": {
                    "asset_ids": [asset_id],
                    "tag_id": tag_id,
                    "tag_id_type": 2,
                },
            },
            {
                "type": "取消隐藏相片",
                "cmd": "asset_remove_from_tag",
                "params": {
                    "asset_ids": [asset_id],
                    "tag_id": tag_id,
                    "tag_id_type": 2,
                },
            },
            {
                "type": "相片备注",
                "cmd": "post_asset_supplement",
                "params": {
                    "md5": md5,
                    "memo": memo,
                },
            },
        ]

        for task in tasks:
            self.command(**task)

    @handler
    def start(self, op):
        r = self.login()
        if r["status"]:
            res = self.checkin()

            result = {}
            result.update(self.userInfo)

            result.update(res)

            if op is not None:
                # 执行任务
                self.task(**op)
                res2 = self.reward()

                if res2 is not None:
                    result.update(res2)

            return result
        else:
            return {
                "status": False,
                "message": f"登录失败, 原因: {r['message']}",
                "account": self.__account,
            }
