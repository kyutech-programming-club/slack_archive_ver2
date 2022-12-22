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
# def get_channel_id():
#     url = 'https://slack.com/api/conversations.list'
#     r = requests.get(url, headers=headers)
#     channel_data = r.json()
#     channels = channel_data["channels"]
#     channel_id_list = []  # この配列にIDを格納
#     for i in channels:
#         channel_id_list.append(i["id"])
#     return channel_id_list  # 配列を返す
channel_id_list = ["CRRLNR1AM", "CHKEQGFUG", "CRSDL3YNP", "C03CR11BLNS"]


# # チャンネルからメッセージを取得
# def get_messages(id, today, oldest):
#     url = 'https://slack.com/api/conversations.history'
#     data = {
#         "channel": id,
#         "include_all_metadata": False,
#         "oldest": oldest
#     }
#     r = requests.get(url, headers=headers, params=data)
#     history = r.json()
#     messages = history["messages"]
#     messages.reverse()
#     messages_json = json.dumps(messages, ensure_ascii=False, indent=4)
#     with open(f'{today}_{id}.json', 'w') as f:
#         json.dump(messages, f, ensure_ascii=False, indent=4)
#     return messages_json


# メッセージのリプライを取得
def get_replies(id, ts):
    url = 'https://slack.com/api/conversations.replies'
    data = {
        "channel": id,
        "ts": ts,
    }
    r = requests.get(url, headers=headers, params=data)
    replies = r.json()
    replies = replies['messages']
    formatted_replies = []
    for i in replies:
        if "files" not in i:
            formatted_replies.append({
                "user": i["user"],
                "ts": i["ts"],
                "text": i["text"],
                "files": []
            })
        else:
            files = []
            for j in i["files"]:
                files.append({
                    "name": j["name"],
                    "file_url": j["url_private"]
                })
            formatted_replies.append({
                "user": i["user"],
                "ts": i["ts"],
                "text": i["text"],
                "files": files
            })
    # formatted_replies配列の０番目はリプライされたメッセージなので必要ない。配列の０番目を消す
    formatted_replies.pop(0)
    with open('replies.json', 'w') as f:
        json.dump(formatted_replies, f, ensure_ascii=False, indent=4)
    return formatted_replies

# get_replies("CRRLNR1AM", "1670943931.945099")


# チャンネルからメッセージを取得
def get_messages(id, oldest, today):
    url = 'https://slack.com/api/conversations.history'
    data = {
        "channel": id,
        "include_all_metadata": False,
        "oldest": oldest
    }
    r = requests.get(url, headers=headers, params=data)
    history = r.json()
    messages = history["messages"]
    messages.reverse()
    formatted_messages = []
    for i in messages:
        replies = get_replies(id, i["ts"])
        if "files" not in i:
            formatted_messages.append({
                "user": i["user"],
                "ts": i["ts"],
                "text": i["text"],
                "files": [],
                "replies": replies
            })
        else:
            files = []
            for j in i["files"]:
                files.append({
                    "name": j["name"],
                    "file_url": j["url_private"]
                })
            formatted_messages.append({
                "user": i["user"],
                "ts": i["ts"],
                "text": i["text"],
                "files": files,
                "replies": replies
            })

    messages_json = json.dumps(
        formatted_messages, ensure_ascii=False, indent=4)
    with open(f'{today}_{id}.json', 'w') as f:
        json.dump(formatted_messages, f, ensure_ascii=False, indent=4)
    return formatted_messages

# get_messages("CRRLNR1AM")


# get_replies("CRRLNR1AM", "1670987280.647039")

# def get_replies():
#     url = 'https://slack.com/api/conversations.replies'
#     data = {
#         "channel": "CRRLNR1AM",
#         "ts": "1670985270.379639",
#     }
#     r = requests.get(url, headers=headers, params=data)
#     replies = r.json()
#     replies = replies['messages']
#     replies_json = json.dumps(replies, ensure_ascii=False, indent=4)
#     with open('replies.json', 'w') as f:
#         json.dump(replies, f, ensure_ascii=False, indent=4)
#     return replies
# get_replies()


def send_message():
    url = "https://slack.com/api/chat.postMessage"
    data = {
        'channel': "C03CR11BLNS",
        'text': "botが送れる文字数のテスト"
    }
    r = requests.post(url, headers=headers, data=data)
    print(r.json())


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
    # 今月一日０時０分のdatetime
    now_dt = datetime.datetime.strptime(
        f'{now.year}-{now.month}-01 00:00:00', "%Y-%m-%d %H:%M:%S")
    # 今月一日０時０分のunixts
    now_ts = now_dt.timestamp()
    # 先月一日のunixts
    # 今月一日０時０分のunixtsから先月の秒数(3600*24*日数)を引いている
    # 32400足しているのは日本時間に変換するため
    oldest = int(int(now_ts) - calendar.monthrange(now.year,
                 now.month - 1)[1] * 86400 + 32400)

    # 標準では1
    target_day = 22

    if now.day == target_day:
        today = str(now.year) + str(now.month)

        for id in channel_id_list:
            get_messages(id, oldest, today)
            print("ok")

        while now.day == target_day:
            print("finish")
            time.sleep(10)
    time.sleep(10)


# チャンネルidのリストは手作業で作る
# get_replies()
