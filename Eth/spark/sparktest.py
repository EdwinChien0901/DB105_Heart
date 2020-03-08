from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql import SparkSession
import csv

with open('testresult.csv', newline='', encoding='utf-8') as csvfile:
    rows = csv.reader(csvfile)
    rows = list(rows)

#print(rows)
#SQLContext.createDataFrame(row).collect()

    #from 01 to ch
# tags = []
#
# for i in range(1, len(rows)):
#     tmp = []
#     for j in range(len(rows[i])):
#         if rows[i][j] == '1':
#             print(rows[i][j])
#             tmp.append(rows[0][j])
#     tags.append(tmp)
#
# print(tags)

    #choose
spark = SparkSession.builder.appName('test').config(key='test', value='tea').getOrCreate()
print(spark.sparkContext)
chooseplace = spark.createDataFrame(rows)
chooseplace.createOrReplaceTempView("rows")
    #1Q
# if(firstkey=="雙北"):
#     area = spark.sql("SELECT places FROM rows WHERE area="新北市" && area="臺北市"")
# else
#     area = spark.sql("SELECT places FROM rows WHERE area==firstkey")

    #2Q
# if(2key=="雨天備案"):
#     place1 = area.filter("SELECT places FROM rows WHERE tags == 博物館 || tags == 餐廳 || tags==咖啡廳")
# elif(2key=="戶外玩樂"):
#     place1 = spark.sql("SELECT places FROM rows WHERE tags == 公園 || tags == 夜景 || tags==農場")
# elif(2key=="崇尚自然"):
#     place1 = spark.sql("SELECT places FROM rows WHERE tags == 花海 || tags == 步道 || tags==露營")
# else:

    #3Q
