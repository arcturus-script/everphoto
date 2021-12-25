import os
import hashlib
import requests
import json
import push

Account = os.environ['Account'].split(',')  # 账号
Password = os.environ['Password'].split(',')  # 登录密码


login_url = 'https://web.everphoto.cn/api/auth'  # 时光相册登录地址
checkin_url = 'https://api.everphoto.cn/users/self/checkin/v2'  # 时光相册签到地址


# 获取 md5 加密后的密码
def get_pwd_md5(pwd):
    salt = 'tc.everphoto.'
    pwd = salt + pwd
    md5 = hashlib.md5(pwd.encode())
    return md5.hexdigest()


# 登陆
def login(act, pwd, headers, CountryCode='+86'):
    data = 'mobile=%s%s&password=%s' % (CountryCode, act, pwd)
    rep = requests.post(login_url, data=data, headers=headers)
    rep_datas = json.loads(rep.text)['data']
    return rep_datas


# 签到
def checkin(headers):
    checkin_response = requests.post(checkin_url, headers=headers)
    checkin_datas = json.loads(checkin_response.text)
    return checkin_datas


def start():
    detail = dict()  # 用于存放签到情况
    for act, pwd in zip(Account, Password):
        headers = {
            'User-Agent':
            'EverPhoto/2.7.0 (Android;2702;ONEPLUS A6000;28;oppo)',
            'application': 'tc.everphoto'
        }
        # 开始登陆
        rep_datas = login(act, get_pwd_md5(pwd), headers)
        print(rep_datas)
        headers['authorization'] = 'Bearer ' + rep_datas['token']
        # 开始签到
        checkin_data = checkin(headers)
        print(checkin_data)

        user_profile = rep_datas['user_profile']
        checkin_data = checkin_data['data']

        if checkin_data['checkin_result'] is True:
            rwd = checkin_data['reward'] / (1024 * 1024)  # 今日获得
            status = '签到成功'
        else:
            rwd = ''
            status = '已签到'

        c = {
            'account': act,  # 账号
            'name': user_profile['name'],  # 用户名
            'days_from_created': user_profile['days_from_created'],  # 注册天数
            'estimated_media_num': user_profile['estimated_media_num'],  # 文件数
            'to_rwd': checkin_data['tomorrow_reward'] / (1024 * 1024),  # 明日获得
            't_rwd': checkin_data['total_reward'] / (1024 * 1024),  # 总获得空间
            'continuity': checkin_data['continuity'],  # 连续签到天数
            'status': status,
            'rwd': rwd  # 今日获得
        }

        detail[act] = c

    push_type = os.getenv('push_type', '0')
    # push_type = '2'
    if push_type == '1':
        # 使用企业微信推送
        AgentId = os.environ['AgentId']  # 应用 ID
        Secret = os.environ['Secret']  # 应用密钥
        EnterpriseID = os.environ['EnterpriseID']  # 企业 ID
        Touser = os.getenv('Touser', '@all')  # 用户 ID

        for item in detail.values():
            content = '今日签到奖励：%sM\n明日签到奖励：%sM\n总共获得空间：%sM\n连续签到：%s天\n注册时长：%s\n文件数：共%s张相片/视频' % (
                item['rwd'], item['to_rwd'], item['t_rwd'], item['continuity'],
                item['days_from_created'], item['estimated_media_num'])
            p = push.qiye_wechat(AgentId, Secret, EnterpriseID, Touser)
            p.push_text_message('时光相册', content, item['name'], item['account'])
    elif push_type != '0':
        key = os.getenv('key', '0')
        if key != '0':
            content = ''
            for item in detail.values():
                ct = '### 账号：%s\n### 用户名：%s\n|描述|详情|\n|:--:|:--:|\n|今日签到奖励|%sM|\n|明日签到奖励|%sM|\n|总共获得空间|%sM|\n|连续签到|%s天|\n|注册时长|%s天|\n|文件数|%s个|\n' % (
                    item['account'], item['name'], item['rwd'], item['to_rwd'],
                    item['t_rwd'], item['continuity'],
                    item['days_from_created'], item['estimated_media_num'])
                content = content + ct

            if push_type == '2':
                # 使用 sever 酱推送
                p = push.server(key)
            elif push_type == '3':
                # 使用 pushplus 酱推送
                p = push.pushplus(key)

            p.push_message('时光相册', content)
        else:
            print('忘记填 key 了哦🦉')


def main(*arg):
    return start()


if __name__ == '__main__':
    main()
