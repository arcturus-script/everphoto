from datetime import datetime


def handler(fn):
    def inner(*args, **kwargs):
        res = fn(*args, **kwargs)

        if res.get("status", False):
            result = [
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
                        "contents": [
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

            if res.get("收藏"):
                result.append(
                    {
                        "txt": {
                            "content": "任务情况",
                        },
                        "table": {
                            "contents": [
                                ("任务", "执行结果"),
                                ("收藏", f"{res['收藏']}"),
                                ("隐藏", f"{res['隐藏']}"),
                                ("相册", f"{res['相册']}"),
                                ("备注", f"{res['备注']}"),
                            ]
                        },
                    }
                )

            return result

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
            ]

    return inner


# 日期字符串格式化
def dateTime_format(dt: str) -> str:
    try:
        dl = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S+08:00")

        return dl.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        print(f"Format failed, because: {e}")
