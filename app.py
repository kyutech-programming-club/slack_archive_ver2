from flask import Flask, request
import json
import requests


app = Flask(__name__)
token = "xoxb-597500547424-4511524546932-o3RDC4fjQtLnQOvDn1RVhTz8"
headers = {"Authorization": "Bearer " + token}


#ワークスペース内の全チャンネルのID取得
def get_channel_id():
    url = 'https://slack.com/api/conversations.list'
    r = requests.get(url, headers=headers)
    channel_data = r.json()
    channels = channel_data["channels"]
    channel_id_list = []      #この配列にIDを格納
    for i in channel_data["channels"]:
        channel_id_list.append(i["id"])
    return channel_id_list #配列を返す




#チャンネルからメッセージを取得
def get_messages(id):
    url = 'https://slack.com/api/conversations.history'    
    data = {
        "channel": id, #適当な変数(チャンネルid)に後で変える
        'include_all_metadata': True
    }
    r = requests.get(url, headers=headers, params=data)
    history = r.json()
    messages = history["messages"]
    messages.reverse()      #messages配列の順番を逆にした
    messages_json = json.dumps(messages, ensure_ascii=False, indent=4)   
    print(messages_json)
    # with open('test.json', 'w') as f:
    #     json.dump(messages, f, ensure_ascii=False, indent=4)
    return messages_json


#メッセージのリプライを取得
def get_replies():
    url = 'https://slack.com/api/conversations.replies'
    data = {
        "channel": "CRSDL3YNP",
        "ts": "1670979340.818239",
    }
    r = requests.get(url, headers=headers, params=data)
    replies = r.json()
    
    replies_json = json.dumps(replies["messages"], ensure_ascii=False, indent=4)   
    print(replies_json)
    return replies



#よくわからん機能
def get_archive():
    url = 'https://slack.com/api/conversations.archive'
    data = {
        "channel": "C03CR11BLNS"
    }
    r = requests.post(url, headers=headers, data=data)  
    archive = r.json()
    print(archive)
    return archive


@app.route('/', methods=["GET"])
def return_messages():
    return get_replies()
    

if __name__ == '__main__':
    app.debug = True
    app.run(debug=True, host='0.0.0.0', port=8081)
    
# https://infinite-earth-07156.herokuapp.com



#関数をfor文で回したら全チャンネルのメッセージとれるかも
# for id in get_channel_id():
#     get_messages(id)
