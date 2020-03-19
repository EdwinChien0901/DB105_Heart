#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from confluent_kafka import Consumer, KafkaException, KafkaError
import sys
#import mysqltest
#import pandas_main
import os, json
import maintest as mt
import spot_recommend as sr
import pic_similarity as ps
import util

# 用來接收從Consumer instance發出的error訊息
def error_cb(err):
    print('Error: %s' % err)


# 轉換msgKey或msgValue成為utf-8的字串
def try_decode_utf8(data):
    if data:
        return data.decode('utf-8')
    else:
        return None


# 指定要從哪個partition, offset開始讀資料
def my_assign(consumer_instance, partitions):
    for p in partitions:
        p.offset = 0
    print('assign', partitions)
    consumer_instance.assign(partitions)


if __name__ == '__main__':
    # 步驟1.設定要連線到Kafka集群的相關設定
    # Consumer configuration
    # See https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
    props = {
        'bootstrap.servers': '35.194.224.128:9092',       # Kafka集群在那裡? (置換成要連接的Kafka集群)
        #'bootstrap.servers': '104.199.134.68:9092',  # <-- 置換成要連接的Kafka集群
        'group.id': 'DB105',                     # ConsumerGroup的名稱 (置換成你/妳的學員ID)
        'auto.offset.reset': 'earliest',             # Offset從最前面開始
        #'auto.offset.reset': 'latest',  # Offset從最前面開始
        'session.timeout.ms': 6000,                  # consumer超過6000ms沒有與kafka連線，會被認為掛掉了
        'error_cb': error_cb                         # 設定接收error訊息的callback函數
    }
    # 步驟2. 產生一個Kafka的Consumer的實例

    # 步驟3. 指定想要訂閱訊息的topic名稱
    topicName = ["questionaire", "recommendation", "picsimilarity"]
    consumers = []
    # 步驟4. 讓Consumer向Kafka集群訂閱指定的topic
    for t in topicName:
        consumers.append(Consumer(props))
        #consumer = Consumer(props)
        #consumers.append(Consumer(props).subscribe([t], on_assign=my_assign))
    for t, consumer in enumerate(consumers):
        consumer.subscribe([topicName[t]], on_assign=my_assign)

    # 步驟5. 持續的拉取Kafka有進來的訊息
    count = 0
    try:
        while True:
            # 請求Kafka把新的訊息吐出來
            for t, consumer in enumerate(consumers):
                records = consumer.consume(num_messages=500, timeout=1.0)  # 批次讀取
                if records is None:
                    continue

                for record in records:
                    # 檢查是否有錯誤
                    if record is None:
                        continue
                    if record.error():
                        # Error or event
                        if record.error().code() == KafkaError._PARTITION_EOF:
                            # End of partition event
                            sys.stderr.write('%% {} [{}] reached end at offset {} - {}\n'.format(record.topic(),
                                                                                                 record.partition(),
                                                                                                 record.offset()))

                        else:
                            # Error
                            raise KafkaException(record.error())
                    else:
                        # ** 在這裡進行商業邏輯與訊息處理 **
                        # 取出相關的metadata
                        topic = record.topic()
                        partition = record.partition()
                        offset = record.offset()
                        timestamp = record.timestamp()
                        # 取出msgKey與msgValue
                        msgKey = try_decode_utf8(record.key())
                        msgValue = try_decode_utf8(record.value())

                        # 秀出metadata與msgKey & msgValue訊息
                        count += 1
                        print('{}-{}-{} : ({} , {})'.format(topic, partition, offset, msgKey, msgValue))

                        if topicName[t] == "questionaire":
                            k1, k2 = [], []
                            # valueDict = dict(msgValue)
                            valueDict = json.loads(msgValue.replace("'", "\""))
                            # print(valueDict)
                            if len(valueDict.keys()) > 4:
                                continue

                            for i, k in enumerate(valueDict.keys()):
                                # print(i, len(valueDict.keys()))
                                if i < (len(valueDict.keys()) - 1):
                                    k2.append(k)
                                else:
                                    k1.append(k)
                                # k1 = ['宜蘭']
                                # k2 = ['戶外玩樂', '人文', '親子']
                            # print("k1:k2", k1, k2)
                            reList = mt.do_compare(k1, k2)
                            # mysqltest.sqlcon(k1)
                            # ranking = pandas_main.pandascon(k2)
                            # print("reList:", reList)
                            rekey = "{}-re".format(msgKey)
                            rc = util.getRedis(True)
                            if (rc.exists(rekey)):
                                rc.delete(rekey)
                            for site in reList:
                                util.redisLPush(rekey, site)
                        elif topicName[t] == "recommendation":
                            print("recommendation", msgKey)
                            recommend_list = sr.spotRecommend(msgValue)
                            for site in recommend_list:
                                util.redisLPush(msgKey, site)
                            print(recommend_list)
                        elif topicName[t] == "picsimilarity":
                            file = util.getRedisImg(msgKey)
                            city = msgValue
                            print("file path:", city, os.path.abspath(file))
                            ans = ps.pic_compare(city, os.path.abspath(file))
                            print(ans)
                            util.redisSetData("{0}-pic".format(msgKey), str(ans))


    except KeyboardInterrupt as e:
        sys.stderr.write('Aborted by user\n')
    except Exception as e:
        print(e)
        #sys.stderr.write("error:")

    finally:
        # 步驟6.關掉Consumer實例的連線
        for t, consumer in enumerate(consumers):
            consumer.close()
