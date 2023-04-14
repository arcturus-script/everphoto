## 时光相册签到(云函数版)

配置 config.py , 执行入口改为 index.main

```python
# config.py

push = {
  "type": "pushplus",
  "key": "069ac93da07...",
}

config = {
    "multi": [
        {
            "account": "189...",
            "country": "+86",
            "password": "root123",
            "push": push,
        },
        {
            "account": "186...",
            "password": "root123",
            "push": push,
        }
    ],
}
```
