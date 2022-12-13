# https://infinite-earth-07156.herokuapp.com

from flask import Flask, request
import json
import requests



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

# for j in get_channel_id():
#     print(j)



#全てのチャンネルからメッセージを取得
def get_messages():
    url = 'https://slack.com/api/conversations.history'
    # for i in get_channel_ID:
    #     payload = {
    #     "channel": i
    #     }   
    #     r = requests.get(url, headers=headers, params=payload)
    #     archive = r.json()
    #     print(archive)    
    payload = {
        "channel": "CHKEQGFUG"
    }
    r = requests.get(url, headers=headers, params=payload)
    history = r.json()
    messages = history["messages"]
    messages_json = json.dumps(messages, sort_keys=True,ensure_ascii=False, indent=2)
    print(messages_json)   
    return messages
    
get_messages()




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

# get_archive()