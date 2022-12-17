from flask import Flask, request
import json
import requests
import datetime
import time


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
    # messages配列の順番を逆にする
    messages.reverse()
    messages_json = json.dumps(messages, ensure_ascii=False, indent=4)
    # with open('test.json', 'w') as f:
    #     json.dump(messages, f, ensure_ascii=False, indent=4)
    return messages_json


#データサーバーに送るためにmessagesとrepliesをいい感じにまとめる
def format_messages():

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
    target = 17

    if now.day == target:
        ts = int(time.time()) #現在のunix時間
        #ここですべての関数を呼び出す

        while now.day == target:
            time.sleep(10)

    time.sleep(10)
 


get_replies()