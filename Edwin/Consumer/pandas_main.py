import pandas as pd

def pandascon(key):
    with open('tagsv3.txt', encoding='utf-8') as file:
        tags = file.read()
    tags = tags.replace('\ufeff', '')
    tags = tags.replace('\n', '')
    tags = tags.split(' ')

    testkey = key
    number = pd.DataFrame(columns=['num', 'value'])
    for i in range(len(tags)):
        number.loc[i] = [i, tags[i]]
    #print(number)
    number.to_csv('tagindex.csv', index=False)

    tagdf = pd.DataFrame(columns=['team', 'value'])
    tagdf.loc[0] = [ '雨天備案', ['博物館', '餐廳', '咖啡廳']]
    tagdf.loc[1] = [ '戶外玩樂', ['公園', '夜景', '農場']]
    tagdf.loc[2] = [ '半戶外方案', ['校園', '遊樂園', '園區', '廟宇', '老街', '觀光工廠', '溫泉', '夜市', '車站', '展覽']]
    tagdf.loc[3] = [ '崇尚自然', ['花海', '步道', '露營']]
    tagdf.loc[4] = [ '人文風格', ['歷史', '藝術', '異國']]
    tagdf.loc[5] = [ '自然風格', ['自然', '景觀']]
    tagdf.loc[6] = [ '購物觀光', ['美食', '拍照']]
    tagdf.loc[7] = [ '情人', ['情侶']]
    tagdf.loc[8] = [ '家人', ['親子']]
    tagdf.loc[9] = [ '寵物', ['寵物']]

    user = [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3,0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3]
    k = 0.1

    for z in range(len(testkey)):
        if testkey[z] == '朋友':
            continue
        for i in range(len(tagdf)):
            if testkey[z] == tagdf.at[i, 'team']:
                tmpindex = i
                #print(tmpindex)
            else:
                tmpindex = 0

        for i in range(len(number)):
            for j in range(len(tagdf.at[tmpindex, 'value'])):
                if tagdf.at[tmpindex, 'value'][j] == number.at[i, 'value']:
                    user[number.at[i, 'num']] += k
        #print(user)
        k = k+0.2

    csv = pd.read_csv('spotweight.csv')

    #print(user)
    # print(number.at[0, 'value'])
    # print(csv.at[0, number.at[0, 'value']])
    tag_weight = []
    for i in range(len(csv)):
        tmp = []
        for j in range(len(user)):
            c = user[j]*csv.at[i, number.at[j, 'value']]
            tmp.append(c)
        tag_weight.append(tmp)

    #print(tag_weight)

    tag_weight_added = []
    for i in range(len(tag_weight)):
        z = 0
        for j in range(len(tag_weight[i])):
            z = z+tag_weight[i][j]
        tag_weight_added.append(z)

    #print(tag_weight_added)

    tag_spot = pd.DataFrame(columns=['spot', 'value'])
    for i in range(len(tag_weight_added)):
        tag_spot.loc[i] = [csv.at[i, 'spot'], tag_weight_added[i]]

    #print(tag_spot)

    final_tag = pd.DataFrame(columns=['spot', 'value'])
    places_selected = pd.read_csv('places_selected.csv')
    o=0
    for i in range(len(places_selected)):
        for j in range(len(tag_spot)):
            if tag_spot.at[j, 'spot'] == places_selected.at[i, 'value']:
                final_tag.loc[o] = [places_selected.at[i, 'value'], tag_spot.at[j, 'value']]
                o = o+1

    final_tag = final_tag.sort_values(by=['value'], ascending=False)
    final_tag = final_tag.reset_index(drop=True)
    #print(final_tag)
    output_tag = []
    le = 4
    for i in range(le):
        output_tag.append(final_tag.at[i, 'spot'])
    #print(output_tag)
    return output_tag
