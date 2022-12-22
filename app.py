from flask import Flask, request
import json
import requests
import datetime
import time
import calendar
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("./slackbot-database-68d26-firebase-adminsdk-c6efu-bd77b4b931.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

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
    formatted_replies.pop(0)
    return formatted_replies


# チャンネルからメッセージを取得
def get_messages(id, oldest):
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
    return formatted_messages


#firestoreに送信
def send_to_database(id, oldest, last_month):
    messages = get_messages(id, oldest)
    doc_ref = db.collection("messages").document(id)
    doc_ref.set({last_month: firestore.ArrayUnion(messages)})



# @app.route('/', methods=["GET"])
# def return_messages():
#     return get_replies()


# if __name__ == '__main__':
#     app.debug = True
#     app.run(debug=True, host='0.0.0.0', port=8090)

# https://infinite-earth-07156.herokuapp.com


while True:
    now = datetime.datetime.now()
    # 今月1日0時0分のdatetime
    now_dt = datetime.datetime.strptime(
        f'{now.year}-{now.month}-01 00:00:00', "%Y-%m-%d %H:%M:%S")
    # 今月1日0時0分のunixts
    now_ts = now_dt.timestamp()
    #時差
    time_difference = 32400
    # 先月1日のunixts
    # 今月1日0時0分のunixtsから先月の秒数(3600*24*日数)を引いている
    # time_differenceを足しているのは日本時間に変換するため
    oldest = int(int(now_ts) - calendar.monthrange(now.year,
                 now.month - 1)[1] * 86400 + time_difference)
    #メッセージを取得する日
    target_day = 1
    if now.day == target_day:
        if now.month == 1:
            last_month = str(now.year - 1) + str(now.month - 1)
        else:
            last_month = str(now.year) + str(now.month - 1)

        for id in channel_id_list:
            send_to_database(id, oldest, last_month)
            print("ok")
        print("finish")
    while now.day == target_day:   
            time.sleep(10)
    time.sleep(10)