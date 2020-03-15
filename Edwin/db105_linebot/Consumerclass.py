from confluent_kafka import Consumer, KafkaException, KafkaError
import sys

class Consumer:
    ipAddr = None
    topicName = None
    aConsumer = None

    def error_cb(self, err):
        print('Error: %s' % err)

    def my_assign(consumer_instance, partitions):
        for p in partitions:
            p.offset = 0
        print('assign', partitions)
        consumer_instance.assign(partitions)

    def __init__(self):
        self.ipAddr = "127.0.0.1"

    def setIP(self, ip):
        self.ipAddr = ip

    def setTopic(self, topic):
        self.topicName = topic

    def getConsumer(self):
        props = {
            'bootstrap.servers': self.ipAddr,  # Kafka集群在那裡? (置換成要連接的Kafka集群)
            # 'bootstrap.servers': '104.199.134.68:9092',  # <-- 置換成要連接的Kafka集群
            'group.id': 'DB105Heart',  # ConsumerGroup的名稱 (置換成你/妳的學員ID)
            'auto.offset.reset': 'earliest',  # Offset從最前面開始
            'session.timeout.ms': 6000,  # consumer超過6000ms沒有與kafka連線，會被認為掛掉了
            'error_cb': error_cb  # 設定接收error訊息的callback函數
        }

        aConsumer = Consumer(props)
        aConsumer.subscribe([self.topicName], on_assign=my_assign)



