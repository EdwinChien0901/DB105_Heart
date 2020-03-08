from confluent_kafka import Producer
import redis
from elasticsearch import Elasticsearch
import numpy as np
import os, cv2
import MySQLdb
import pymongo

siteList = ["基隆","台北","宜蘭","桃園", "台北101", "國立故宮博物院", "九份", "中正紀念堂", "陽明山國家公園", "龍山寺",
            "野柳", "十分瀑布", "象山", "臺北市立動物園", "國立國父紀念館", "北投溫泉博物館", "饒河街觀光夜市",
            "金瓜石", "十分老街", "淡水漁人碼頭", "貓空", "松山文創園區", "國民革命忠烈祠", "淡水紅毛城", "地熱谷", "龜山島"]

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

#Get Connections
def getMongoDB():
    myclient = pymongo.MongoClient("mongodb://35.194.224.128:27017")

    return myclient

def getMsSQLConn():
    db = MySQLdb.connect(host='35.194.224.128', user='db105adm', passwd='db105heart', db='db105_heart', port=3306, charset='utf8')

    return db

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


#Redis Operation
def setRedisImg(lineToken, imgByte):
    r = getRedis(True)
    try:
        r.set(lineToken, imgByte)
    except Exception as e:
        print("error:", e)
    finally:
        r.close()

def getRedisImg(lineToken):
    r = getRedis(False)
    fileName = ""

    try:
        img1_bytes_ = r.get(lineToken)
        print(img1_bytes_)
        decoded = cv2.imdecode(np.frombuffer(img1_bytes_, np.uint8), 1)
        fileName = "./{0}.jpg".format(lineToken)
        cv2.imwrite(fileName.format(), decoded)
    except Exception as e:
        print("error:", e)
    finally:
        r.close()

    return os.path.abspath(fileName)

def redisLPush(key, value):
    r = getRedis(True)
    r.lpush(key, value)

def redisLRange(key, sidx, eidx):
    r = getRedis(True)
    lList = r.lrange(key, sidx, eidx)

    return lList

def redisLPopAll(key):
    r = getRedis(True)
    value = r.rpop(key)

    while value != None:
        value = r.rpop(key)

#MongoDB Operation
def findMongoDataURL(dbName, colName, siteName):
    #db.gina_scrapy.find({tags : "台北"})
    #db.gina_scrapy.find({tags : "基隆"}, {_id:0,tags:1, url:1, title:1}).limit(5)
    #db.BackPacker.createIndex({content : "text"})})
    #db.BackPacker.find({ $text : { $search : "基隆" }})

    monCli = getMongoDB()
    urlList = []
    try:
        mydb = monCli[dbName]
        mycol = mydb[colName]
        rd = mycol.find({"$text" : { "$search" : siteName }}).limit(5)

        for er in rd:
            doc = dict(er)
            urlList.append(doc["url"])
    except Exception as e:
        print("error:", e)
    finally:
        monCli.close()

    return urlList

#MySQL Operation
def getSiteList():
    sqlConn = getMsSQLConn()

    try:
        cursor = sqlConn.cursor()
        sql_str = 'select * from product'
        cursor.execute(sql_str)
        datarows = cursor.fetchall()
        siteList.clear()
        for row in datarows:
            #print(row[2])
            siteList.append(row[2])

    except Exception as e:
        print("error:", e)
    finally:
        sqlConn.close()

    return siteList

def insertUserInfo(userDoc):
    sqlConn = getMsSQLConn()

    try:
      sqlStr = """insert into db105_heart.users (user_name, picture_url, status_message, user_id, datetime) 
                  values ('{0}', '{1}', '{2}', '{3}', now())"""
      sqlStr = sqlStr.format(userDoc["display_name"], userDoc["picture_url"], userDoc["status_message"], userDoc["user_id"])
      #print("sqlStr:", sqlStr)
      cursor = sqlConn.cursor()
      cursor.execute(sqlStr)
      sqlConn.commit()
    except Exception as e:
        print("error:", e)
    finally:
        sqlConn.close()

#Kafka Operation
def sendKafkaMsg(topicName, value, token):
    prod = getProducer()
    value = {}
    value["key"] = token
    value["value"] = value

    prod.produce(topicName, value=str(value), key=token)
    prod.flush()

#ELK Operation
def insertELK(idx, doc):
    #es = Elasticsearch('http://192.168.11.129:9200')
    es = Elasticsearch('http://35.194.224.128:9200')
    res = es.index(index=idx, doc_type='elk', body=doc)

#Other Operations
def getTemplateJson():
    return templateJson

def getUseMenuJson():
    return useMenuJson


if __name__ == "__main__":
    #list = getSiteList()
    #print(list)
    list = findMongoDataURL("python_heart", "BackPacker", "基隆 勸濟堂")
    print(list)

