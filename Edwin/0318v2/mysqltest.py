import mysql.connector
import pandas as pd

def sqlcon(key):
  testkey = key
  mydb = mysql.connector.connect(
    host="35.194.224.128",
    user="root",
    passwd="iii",
    auth_plugin='mysql_native_password'
  )

  mycursor = mydb.cursor(buffered=True, dictionary=True)

  placetag = pd.DataFrame(columns=['team', 'value'])
  placetag.loc[0] = ['雙北', '\"新北市\"']
  placetag.loc[1] = ['雙北', '\"臺北市\"']
  placetag.loc[2] = ['基隆', '\"基隆市\"']
  placetag.loc[3] = ['宜蘭', '\"宜蘭縣\"']
  placetag.loc[4] = ['桃園', '\"桃園市\"']

  mycursor.execute("show databases;")
  mycursor.execute("use db105_heart;")
  if testkey[0]!='雙北':
    for i in range(len(placetag)):
      if testkey[0] == placetag.at[i, 'team']:
        tmpindex = i
        sql = ("select place_name from north_place_google_api_area_v4 where area={};".format(placetag.at[tmpindex, "value"]))
        mycursor.execute(sql)

        myresult = mycursor.fetchall()

        places = []
        for x in myresult:
          places.append(list(x.values()))

        for i in range(len(places)):
          places[i] = places[i][0]
        #print(places)

        places_selected = pd.DataFrame(columns=['value'])
        for i in range(len(places)):
          places_selected.loc[i] = places[i]

        print(places_selected)
        places_selected.to_csv('places_selected.csv', index=False, encoding='utf-8')
  else:
    sql = ("select place_name from north_place_google_api_area where area={};".format(placetag.at[0, "value"]))

    mycursor.execute(sql)

    myresult = mycursor.fetchall()

    places = []
    for x in myresult:
      places.append(list(x.values()))

    for i in range(len(places)):
      places[i] = places[i][0]
    #print(places)

    places_selected = pd.DataFrame(columns=['value'])
    for i in range(len(places)):
      places_selected.loc[i] = places[i]

    #print(places_selected)

    sql = ("select place_name from north_place_google_api_area where area={};".format(placetag.at[1, "value"]))
    mycursor.execute(sql)

    myresult = mycursor.fetchall()

    places = []
    for x in myresult:
      places.append(list(x.values()))

    for i in range(len(places)):
      places[i] = places[i][0]
    #print(places)

    places_selected = pd.DataFrame(columns=['value'])
    for i in range(len(places)):
      places_selected.loc[i+len(places)] = places[i]
    places_selected.to_csv('places_selected.csv', index=False, encoding='utf-8')
    #print(places_selected)