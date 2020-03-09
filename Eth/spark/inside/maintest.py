from pyspark import SparkContext
from pyspark.sql import SQLContext
import mysqltest
import pandas_main
import os

#kafka consumer
# consumer = KafkaConsumer('my_favorite_topic')
# for msg in consumer:
#     print(msg)

#mysql
#SparkContext(master=None, appName=None, sparkHome=None, pyFiles=None, environment=None, batchSize=0, serializer=PickleSerializer(), conf=None, gateway=None, jsc=None, profiler_cls=<class 'pyspark.profiler.BasicProfiler'>)
# sc = SparkContext()
# sqlContext = SQLContext(sc)
# dataframe_mysql = sqlContext.read.format("jdbc").options(
#     url="jdbc:mysql://localhost:3306/my_bd_name",
#     driver = "com.mysql.jdbc.Driver",
#     dbtable = "my_tablename",
#     user="root",
#     password="root").load()

#mainsql
k1 = ['雙北']
k2 = ['戶外玩樂', '自然', '朋友']
mysqltest.sqlcon(k1)
ranking = pandas_main.pandascon(k2)
print(ranking)

	

#produce to redis
