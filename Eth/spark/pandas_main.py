import pandas as pd

with open('tagsv3.txt') as file:
    tags = file.read()
tags = tags.replace('\n', '')
tags = tags.split(' ')

testkey = ['雨天備案', '人文', '家人']
number = pd.DataFrame(columns=['num', 'value'])
for i in range(len(tags)):
    number.loc[i] = [i, tags[i]]
print(number)
number.to_csv('tagindex.csv', index=False)

tagdf = pd.DataFrame(columns=['team', 'value'])
tagdf.loc[0] = [ '雨天備案', ['博物館', '餐廳', '咖啡廳']]
tagdf.loc[1] = [ '戶外玩樂', ['公園', '夜景', '農場']]
tagdf.loc[2] = [ '半戶外方案', ['校園', '遊樂園', '園區', '廟宇', '老街', '觀光工廠', '溫泉', '夜市', '車站', '展覽']]
tagdf.loc[3] = [ '崇尚自然', ['花海', '步道', '露營']]
tagdf.loc[4] = [ '人文', ['歷史', '藝術', '異國']]
tagdf.loc[5] = [ '自然', ['自然']]
tagdf.loc[6] = [ '購物觀光', ['美食', '拍照']]
tagdf.loc[7] = [ '情人', ['情侶']]
tagdf.loc[8] = [ '家人', ['親子']]
tagdf.loc[9] = [ '寵物', ['寵物']]

user = [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3,0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3]
k = 0.3
for z in range(len(testkey)):
    for i in range(len(tagdf)):
        if testkey[z] == tagdf.at[i, 'team']:
            tmpindex = i
            print(tmpindex)

    for i in range(len(number)):
        for j in range(len(tagdf.at[tmpindex, 'value'])):
            if tagdf.at[tmpindex, 'value'][j] == number.at[i, 'value']:
                user[number.at[i, 'num']] += k
    print(user)
    k = k-0.1