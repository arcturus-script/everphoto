<div align="center">
<h1>时光相册签到(腾讯云函数版)</h1>

[![GitHub issues](https://img.shields.io/github/issues/ICE99125/TimeAlbum?color=red&style=for-the-badge)](https://github.com/ICE99125/TimeAlbum/issues) [![GitHub forks](https://img.shields.io/github/forks/ICE99125/TimeAlbum?style=for-the-badge)](https://github.com/ICE99125/TimeAlbum/network) [![GitHub stars](https://img.shields.io/github/stars/ICE99125/TimeAlbum?style=for-the-badge)](https://github.com/ICE99125/TimeAlbum/stargazers) [![Python](https://img.shields.io/badge/python-3.6%2B-orange?style=for-the-badge)](https://www.python.org/)

</div>

### 使用步骤

1. 新建云函数

   [![5JqucR.png](https://z3.ax1x.com/2021/10/16/5JqucR.png)](https://imgtu.com/i/5JqucR)

2. 选择 python3.6

   [![5Jqm9J.png](https://z3.ax1x.com/2021/10/16/5Jqm9J.png)](https://imgtu.com/i/5Jqm9J)

3. 将函数名改成 index.main

   [![5Jqn39.png](https://z3.ax1x.com/2021/10/16/5Jqn39.png)](https://imgtu.com/i/5Jqn39)

4. 修改环境变量

   [![5JqZh4.png](https://z3.ax1x.com/2021/10/16/5JqZh4.png)](https://imgtu.com/i/5JqZh4)

5. 输入账号和密码，以及推送类型，修改超时时间

   [![5JqKj1.png](https://z3.ax1x.com/2021/10/16/5JqKj1.png)](https://imgtu.com/i/5JqKj1)

### 环境变量

|      键      |            描述            |                     性质                      |
| :----------: | :------------------------: | :-------------------------------------------: |
|   Account    |           手机号           |           必填,多账户使用 `,` 分割            |
|   Password   |          账号密码          |           必填,多账户使用 `,` 分割            |
|  push_type   |        推送服务类型        |              可填,不填不使用推送              |
|   AgentId    |           应用id           |                                               |
| EnterpriseID |           企业id           |                                               |
|    Secret    |          应用密钥          |                                               |
|    Touser    |      不填默认全部成员      |                                               |
|     key      | sever酱 和 pushplus 的 key | push_type 选择 2 或 3 但是不写 key 也不会推送 |

📌 push_type

|  值  |   描述   |
| :--: | :------: |
|  0   |  默认值  |
|  1   | 企业微信 |
|  2   | sever酱  |
|  3   | pushplus |
