config = {
    "multi": [
        {
            "account": "",
            "country": "+86",  # 区号
            "password": "",
            "push": "pushplus",  # together 为 True 时失效, 不写不推送

            # 这里不想执行每日任务就删掉这个
            # 不要留着但是内容都是不对的...
            "daily_task": {
                "md5": "",
                "memo": "( •̀ ω •́ )✧",  # 自定义图片备注
                "asset_id": 8989899898,
                "tag_id": 10909090,
            },
        },
        # {
        #     "account": "123",
        #     "password": "123",
        #     "push": "pushplus",
        # },
    ],
    "together": True,  # 是否合并发送结果, 不写或 True 时合并发送
    "push": "pushplus",  # 推送类型, together 为 True 或者不写时必须有, 否则不推送
}
