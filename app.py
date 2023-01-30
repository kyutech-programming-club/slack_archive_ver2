import json
import os
from dotenv import load_dotenv
import schedule
import time
import requests
import datetime
import time
import calendar
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate(
    "./slackbot-database-68d26-firebase-adminsdk-c6efu-bd77b4b931.json"
)
firebase_admin.initialize_app(cred)
db = firestore.client()

load_dotenv()
slack_app_token = os.environ["SLACK_APP_TOKEN"]
apps_member_id = os.environ["APPS_MEMBER_ID"]

headers = {"Authorization": "Bearer " + slack_app_token}
now = datetime.datetime.now()
time_difference = 32400


# ワークスペース内の全チャンネルのidを取得
def get_channel_id():
    url = "https://slack.com/api/conversations.list"
    r = requests.get(url, headers=headers)
    channel_data = r.json()
    channels = channel_data["channels"]
    channel_id_list = []  # この配列にIDを格納
    for i in channels:
        channel_id_list.append(i["id"])
    # with open("./test.json", "w") as f:
    #     json.dump(channel_data, f, indent=4)
    return channel_id_list  # チャンネルidの配列を返す


# チャンネル内のuseridを取得
def get_users(channel_id):
    url = "https://slack.com/api/conversations.members"
    data = {"channel": channel_id}
    r = requests.get(url, headers=headers, params=data)
    user_data = r.json()
    members = user_data["members"]
    # print(len(user_data["members"]))
    # with open("./test.json", "w") as f:
    #     json.dump(user_data, f, indent=4)
    return members  # チャンネル内の全メンバーの配列を返す


def get_user_name(id):
    url = "https://slack.com/api/users.info"
    data = {"user": id}
    r = requests.get(url, headers=headers, params=data)
    user_data = r.json()
    user_name = (
        user_data["user"]["profile"]["display_name"] if "user" in user_data else ""
    )
    return user_name


# ワークスペース内の全てユーザーの名前とidを取得
def get_user_list():
    url = "https://slack.com/api/users.list"
    r = requests.get(url, headers=headers)
    user_data = r.json()
    members_name_and_id = {}
    if "members" in user_data:
        members = user_data["members"]
        for i in members:
            if not i["deleted"] and not i["is_bot"] and i["id"] != "USLACKBOT":
                user_id = i["id"]
                user_name = get_user_name(user_id)
                user_name = user_name if user_name != "" else i["real_name"]
            else:
                user_id = "no_id"
                user_name = "no_name"
            members_name_and_id.update({f"{user_id}": user_name})
    return members_name_and_id


# メッセージのリプライを取得
def get_replies(id, ts, users_info) -> list:
    print(ts)
    url = "https://slack.com/api/conversations.replies"
    data = {
        "channel": id,
        "ts": ts,
    }
    r = requests.get(url, headers=headers, params=data)

    formatted_replies = []
    # if r.json()["has_more"] == True:
    if "messages" in r.json():
        replies = r.json()["messages"]
        for i in replies:
            # リプライに添付されたファイル
            files = []
            if "files" in i:
                for j in i["files"]:
                    files.append({"name": j["name"], "file_url": j["url_private"]})

            # user_id, user_nameを定義
            user_id = i["user"] if "user" in i else "no_id"
            user_name = users_info[user_id] if user_id in users_info else "no_name"

            formatted_replies.append(
                {
                    "user_id": user_id,
                    "user_name": user_name,
                    "ts": i["ts"],
                    "text": i["text"],
                    "files": files,
                }
            )
        formatted_replies.pop(0)
    print("ok")
    return formatted_replies


# チャンネルからメッセージを取得
def get_messages(id, oldest, latest, users_list) -> list:
    print(id)
    url = "https://slack.com/api/conversations.history"
    data = {
        "channel": id,
        "include_all_metadata": False,
        "oldest": oldest,
        "latest": latest,
    }
    r = requests.get(url, headers=headers, params=data)

    history = r.json()
    messages = history["messages"]
    messages.reverse()
    formatted_messages = []

    for i in messages:
        # メッセージに付いた返信を取得
        replies = get_replies(id, i["ts"], users_list)

        # メッセージに添付されたファイルを取得
        files = []
        if "files" in i:
            for j in i["files"]:
                files.append({"name": j["name"], "file_url": j["url_private"]})

        # user_id, user_nameを定義
        user_id = i["user"] if "user" in i else "no_id"
        user_name = users_list[user_id] if user_id in users_list else "no_name"

        formatted_messages.append(
            {
                "user_id": user_id,
                "user_name": user_name,
                "ts": i["ts"],
                "text": i["text"],
                "files": files,
                "replies": replies,
            }
        )
    return formatted_messages


# 取得するメッセージの範囲を設定
def time_range() -> int:
    now_dt = datetime.datetime.strptime(
        f"{now.year}-{now.month}-01 00:00:00", "%Y-%m-%d %H:%M:%S"
    )
    now_ts = now_dt.timestamp()

    month_range = (
        calendar.monthrange(now.year - 1, 12)[1]
        if now.month == 1
        else calendar.monthrange(now.year, now.month - 1)[1]
    )

    oldest = int(now_ts - month_range * 86400 + time_difference)
    latest = int(now_ts + time_difference)
    return oldest, latest


# firestoreに送るときの名前を設定
def data_name() -> str:
    name = (
        str(now.year - 1) + str(12)
        if now.month == 1
        else str(now.year) + str(now.month - 1)
    )
    return name


# firestoreに送信
def send_to_database(id, oldest, latest, name, users_list):
    messages = get_messages(id, oldest, latest, users_list)
    doc_ref = db.collection("messages").document(id)
    # firestore.ArrayUnion　<=おまじない
    doc_ref.set({name: firestore.ArrayUnion(messages)})


# 色々な関数を呼び出す
def loop():
    if now.day == 1:
        oldest, latest = time_range()
        name = data_name()

        channel_id_list = []
        # このアプリが追加されているチャンネルのidを取得
        for i in get_channel_id():
            for j in get_users(i):
                if apps_member_id == j:
                    channel_id_list.append(i)
                    print(i)
        print("got all the IDs")
        print("")

        users_list = get_user_list()
        print("got user list")
        print("")

        # id毎にfirestoreに送信
        for id in channel_id_list:
            send_to_database(id, oldest, latest, name, users_list)
            print("")
    print("finish")


# 実行スケジュールを設定
schedule.every().day.at("00:00").do(loop)

# 常に実行
while True:
    schedule.run_pending()
    time.sleep(1)
