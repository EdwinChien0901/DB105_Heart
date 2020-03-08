import mysql.connector

mydb = mysql.connector.connect(
  host="35.194.224.128",
  user="root",
  passwd="iii"
)

print(mydb)