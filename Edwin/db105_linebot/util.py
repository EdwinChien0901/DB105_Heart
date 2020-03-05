from confluent_kafka import Producer
import redis
from elasticsearch import Elasticsearch
import numpy as np
import os, cv2

siteList = ["基隆","台北","宜蘭","桃園"]

templateJson = """
{
  "type": "template",
  "altText": "this is a buttons template",
  "template": {
    "type": "buttons",
    "actions": [
      {
        "type": "postback",
        "label": "site1",
        "text": "site1",
        "data": "site1"
      },
      {
        "type": "postback",
        "label": "site2",
        "text": "site2",
        "data": "site2"
      },
      {
        "type": "postback",
        "label": "site3",
        "text": "site3",
        "data": "site3"
      },
      {
        "type": "postback",
        "label": "site4",
        "text": "site4",
        "data": "site4"
      }
    ],
    "thumbnailImageUrl": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSv1fMLTdWkPX1v881nrllXtJFJb_bYC6MTilfM6El7f39Bc3a0",
    "title": "你接下來還可以去這裡玩!!!",
    "text": "-"
  }
}
"""

useMenuJson = """
{
  "type": "text",
  "text": "有任何問題，可以使用以下圖文選單來進行喔～～"
}
"""

# 用來接收從Consumer instance發出的error訊息
def error_cb(err):
    print('Error: %s' % err)

def getProducer():
    # 步驟1. 設定要連線到Kafka集群的相關設定
    props = {
        # Kafka集群在那裡?
        'bootstrap.servers': '35.194.224.128:9092',  # <-- 置換成要連接的Kafka集群
        'error_cb': error_cb  # 設定接收error訊息的callback函數
    }
    # 步驟2. 產生一個Kafka的Producer的實例
    producer = Producer(props)

    return producer

def getRedis(isDecode):
    r = redis.Redis(host="34.85.107.158", port=6379, decode_responses=isDecode)
    #r = redis.Redis(host="192.168.11.129", port=6379, decode_responses=isDecode)
    return r

def getTemplateJson():
    return templateJson

def getSiteList():
    return siteList

def sendKafkaMsg(topicName, value, token):
    prod = getProducer()
    value = {}
    value["key"] = token
    value["value"] = value

    prod.produce(topicName, value=str(value), key=token)
    prod.flush()

def getUseMenuJson():
    return useMenuJson


def insertELK(idx, doc):
    #es = Elasticsearch('http://192.168.11.129:9200')
    es = Elasticsearch('http://35.194.224.128:9200')
    res = es.index(index=idx, doc_type='elk', body=doc)

def setRedisImg(lineToken, imgByte):
    r = getRedis(True)
    r.set(lineToken, imgByte)

def getRedisImg(lineToken):
    r = getRedis(False)
    img1_bytes_ = r.get(lineToken)
    print(img1_bytes_)
    decoded = cv2.imdecode(np.frombuffer(img1_bytes_, np.uint8), 1)
    fileName = "./{0}.jpg".format(lineToken)
    cv2.imwrite(fileName.format(), decoded)

    return os.path.abspath(fileName)

