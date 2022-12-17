from flask import Flask, request
import json
import requests
import datetime
import time
import calendar
import pandas as pd


app = Flask(__name__)
token = "xoxb-597500547424-4511524546932-o3RDC4fjQtLnQOvDn1RVhTz8"
headers = {"Authorization": "Bearer " + token}




# ワークスペース内の全チャンネルのID取得
def get_channel_id():
    url = 'https://slack.com/api/conversations.list'
    r = requests.get(url, headers=headers)
    channel_data = r.json()
    channels = channel_data["channels"]
    channel_id_list = []  # この配列にIDを格納
    for i in channels:
        channel_id_list.append(i["id"])
    print(channel_id_list)
    return channel_id_list  # 配列を返す


def send_message():
    url = "https://slack.com/api/chat.postMessage"
    data = {
        'channel': "C03CR11BLNS",
        'text': "botが送れる文字数のテスト"
    }
    r = requests.post(url, headers=headers, data=data)
    print(r.json())



# チャンネルからメッセージを取得
def get_messages(id,ts):
    url = 'https://slack.com/api/conversations.history'
    data = {
        "channel": id, 
        "include_all_metadata": True,
        "oldest": ts
    }
    r = requests.get(url, headers=headers, params=data)
    history = r.json()
    messages = history["messages"]
    # messages.reverse()
    messages_json = json.dumps(messages, ensure_ascii=False, indent=4)
    with open('test.json', 'w') as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)
    return messages_json


#データサーバーに送るためにmessagesとrepliesをいい感じにまとめる
def format_messages(id):

    return ""


# メッセージのリプライを取得
def get_replies():
    url = 'https://slack.com/api/conversations.replies'
    data = {
        "channel": "CRSDL3YNP",
        "ts": "1670979340.818239",
    }
    r = requests.get(url, headers=headers, params=data)
    replies = r.json()
    replies = replies['messages']
    replies_json = json.dumps(replies, ensure_ascii=False, indent=4)
    with open('replies.json', 'w') as f:
        json.dump(replies, f, ensure_ascii=False, indent=4)
    return replies


# よくわからん機能
def get_archive():
    url = 'https://slack.com/api/conversations.archive'
    data = {
        "channel": "C03CR11BLNS"
    }
    r = requests.post(url, headers=headers, data=data)
    archive = r.json()
    print(archive)
    return archive


# @app.route('/', methods=["GET"])
# def return_messages():
#     return get_replies()


# if __name__ == '__main__':
#     app.debug = True
#     app.run(debug=True, host='0.0.0.0', port=8090)

# https://infinite-earth-07156.herokuapp.com


# 関数をfor文で回したら全チャンネルのメッセージとれるかも
# for id in get_channel_id():
#     get_messages(id)




while True:
    now = datetime.datetime.now()
    #今月一日０時０分のdatetime
    now_ts_assoc = datetime.datetime.strptime(f'{now.year}-{now.month}-01 00:00:00', "%Y-%m-%d %H:%M:%S") 
    #今月一日０時０分のunixts
    now_ts = now_ts_assoc.timestamp()
    #先月一日のunixts
    #今月一日０時０分のunixtsから先月の秒数(3600*24*日数)を引いている
    # 32400足しているのは日本時間に変換するため
    oldest = int(int(now_ts) - calendar.monthrange(now.year, now.month - 1)[1] * 86400 + 32400) 

    target_day = 17 

    if now.day == target_day:
        get_messages('CHKEQGFUG',oldest)
        print("test3")
        # for i in get_channel_id():
        #     format_messages(i)  
        time.sleep(10)    
        while now.day == target_day:
            time.sleep(10)
    time.sleep(10)
 


#get_replies()