from confluent_kafka import Consumer, KafkaException, KafkaError
import sys
import util
import json

def error_cb(err):
    print('Error: %s' % err)


def my_assign(consumer_instance, partitions):
    for p in partitions:
        p.offset = 0
    print('assign', partitions)
    consumer_instance.assign(partitions)    
# 轉換msgKey或msgValue成為utf-8的字串
def try_decode_utf8(data):
    if data:
        return data.decode('utf-8')
    else:
        return None

if __name__ == "__main__":
    ipAddr = "35.194.224.128:9092"
    #topicName = "followUser"
    topicName = sys.argv[1]
    print("topic:", topicName)
    props = {
        'bootstrap.servers': ipAddr,  # Kafka集群在那裡? (置換成要連接的Kafka集群)
        # 'bootstrap.servers': '104.199.134.68:9092',  # <-- 置換成要連接的Kafka集群
        'group.id': 'DB105Heart',  # ConsumerGroup的名稱 (置換成你/妳的學員ID)
        'auto.offset.reset': 'earliest',  # Offset從最前面開始
        'session.timeout.ms': 6000,  # consumer超過6000ms沒有與kafka連線，會被認為掛掉了
        'error_cb': error_cb  # 設定接收error訊息的callback函數
    }

    aConsumer = Consumer(props)
    aConsumer.subscribe([topicName], on_assign=my_assign)
    try:
        count = 0
        while True:
            # 請求Kafka把新的訊息吐出來
            records = aConsumer.consume(num_messages=500, timeout=1.0)  # 批次讀取
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


                    #util.insertUserInfo(userDoc):
                    # 秀出metadata與msgKey & msgValue訊息
                    count += 1
                    print("count:", count)
                    print('{}-{}-{} : ({} , {})'.format(topic, partition, offset, msgKey, msgValue))
                    #with open('./userinfo.txt', 'a', encoding="utf-8") as f:
                    #    f.write(msgValue)
                        #f.write(json.loads(json.dumps(vars(msgValue), sort_keys=True)))

                    util.insertUserInfo(json.loads(msgValue))
    except KeyboardInterrupt as e:
        sys.stderr.write('Aborted by user\n')
    except Exception as e:
        sys.stderr.write(e)

    finally:
        # 步驟6.關掉Consumer實例的連線
        aConsumer.close()