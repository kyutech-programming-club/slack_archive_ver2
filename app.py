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

token = "xoxb-597500547424-4511524546932-1IceRYRCELawwzsu9HC95Emx"
headers = {"Authorization": "Bearer " + token}

now = datetime.datetime.now()

channel_id_list = [
    "CRRLNR1AM",
    "CHKEQGFUG",
    "CRSDL3YNP",
    "C03CR11BLNS",
    "C01UPH3NNHX",
    "C01A5Q99N11",
    "CHP0PBR63",
    "CJ9B42GM9",
    "CS1U1M8AZ",
    "C017NF5Q97B",
    "C01TN9KAX4J",
]


# メッセージのリプライを取得
def get_replies(id, ts):
    url = "https://slack.com/api/conversations.replies"
    data = {
        "channel": id,
        "ts": ts,
    }
    r = requests.get(url, headers=headers, params=data)
    replies = r.json()
    replies = replies["messages"]
    formatted_replies = []
    for i in replies:
        if "files" not in i:
            formatted_replies.append(
                {"user": i["user"], "ts": i["ts"],
                    "text": i["text"], "files": []}
            )
        else:
            files = []
            for j in i["files"]:
                files.append({"name": j["name"], "file_url": j["url_private"]})
            formatted_replies.append(
                {"user": i["user"], "ts": i["ts"],
                    "text": i["text"], "files": files}
            )
    formatted_replies.pop(0)
    return formatted_replies


# チャンネルからメッセージを取得
def get_messages(id, oldest, latest):
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
        replies = get_replies(id, i["ts"])
        if "files" not in i:
            formatted_messages.append(
                {
                    "user": i["user"],
                    "ts": i["ts"],
                    "text": i["text"],
                    "files": [],
                    "replies": replies,
                }
            )
        else:
            files = []
            for j in i["files"]:
                files.append({"name": j["name"], "file_url": j["url_private"]})
            formatted_messages.append(
                {
                    "user": i["user"],
                    "ts": i["ts"],
                    "text": i["text"],
                    "files": files,
                    "replies": replies,
                }
            )
    return formatted_messages


def send_to_database(id, oldest, latest, name):
    messages = get_messages(id, oldest, latest)
    doc_ref = db.collection("messages").document(id)
    # firestore.ArrayUnion　<=おまじない
    doc_ref.set({name: firestore.ArrayUnion(messages)})


def time_range():
    now_dt = datetime.datetime.strptime(
        f"{now.year}-{now.month}-01 00:00:00", "%Y-%m-%d %H:%M:%S"
    )
    now_ts = now_dt.timestamp()
    time_difference = 32400
    if now.month == 1:
        month_range = calendar.monthrange(now.year - 1, 12)[1]
    else:
        month_range = calendar.monthrange(now.year, now.month - 1)[1]
    oldest = int(now_ts - month_range * 86400 + time_difference)
    latest = int(now_ts + time_difference)
    return oldest, latest


def data_name() -> str:
    if now.month == 1:
        name = str(now.year - 1) + str(12)
    else:
        name = str(now.year) + str(now.month - 1)
    return name


def loop():
    if now.day == 1:
        oldest, latest = time_range()
        name = data_name()

        for id in channel_id_list:
            send_to_database(id, oldest, latest, name)
            print("ok")
    print("finish")


def test(id, oldest):
    url = "https://slack.com/api/conversations.history"
    data = {
        "channel": id,
        "include_all_metadata": False,
        "oldest": oldest,
    }
    r = requests.get(url, headers=headers, params=data)
    history = r.json()
    messages = history["messages"]
    print(messages)


schedule.every().day.at("00:00").do(loop)


while True:
    schedule.run_pending()
    time.sleep(1)
