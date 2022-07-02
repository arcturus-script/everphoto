from everphoto import Everphoto
from config import config
from push import push


def main(*arg):
    together = config.get("together")
    type = config.get("push")
    multi = config.get("multi")

    if together is None or together:  # 如果需要一并推送
        msg_list = []
        for i in multi:
            country = i.get("country", "+86")
            daily_task = i.get("daily_task")
            b = Everphoto(i["account"], i["password"], country)

            res = b.start(daily_task)

            msg_list.extend(res)

        if type:
            push(type, "时光相册", msg_list)
        else:  # 不开启服务
            print("未开启推送")
    else:  # 单独推送
        for i in multi:
            country = i.get("country", "+86")
            daily_task = i.get("daily_task")
            b = Everphoto(i["account"], i["password"], country)

            res = b.start(daily_task)

            alone_type = i.get("push")  # 单独推送类型

            if alone_type:
                push(alone_type, "时光相册", res)
            else:
                print("未开启推送")


if __name__ == "__main__":
    main()
