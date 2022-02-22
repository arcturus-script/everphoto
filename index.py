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
            b = Everphoto(i["account"], i['password'])
            res = b.start()

            msg_list.extend(res)

        if type:
            push(type, "微博", msg_list)
        else:  # 不开启服务
            print("未开启推送")
    else:  # 单独推送
        for i in multi:
            b = Everphoto(i["account"], i['password'])
            res = b.start()

            alone_type = i.get("push")  # 单独推送类型

            if alone_type:
                push(alone_type, "微博", res)
            else:
                print("未开启推送")

if __name__ == "__main__":
    main()