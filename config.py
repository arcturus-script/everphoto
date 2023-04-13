config = {
    "multi": [
        {
            "account": "",
            "country": "+86",  # 区号
            "password": "",
            "push": "pushplus",  # together 为 True 时失效, 不写不推送
        },
        # {
        #     "account": "123",
        #     "password": "123",
        #     "push": "pushplus",
        # },
    ],
    "together": True,  # 是否合并发送结果, 不写或 True 时合并发送
    "push": "pushplus",  # 推送类型, together 为 True 或者不写时必须有, 否则不推送
    "key": "xxxx",  # 推送服务的 key
    # 这个专门用于企业微信, 要用则取消注释, 顺便把上面那个注释掉
    # "key": {
    #   "agentid": "xxx",
    #   "corpSecret": "xxx",
    #   "corpid": "xxx"
    # }
}
