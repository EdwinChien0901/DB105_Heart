import csv
import jieba
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import numpy as np

with open('000.csv', 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    data = list(reader)

filename = ['1.csv', '2.csv', '3.csv', '4.csv', '5.csv']

taginlocation = []

for z in range(0, len(filename)+1):
    try:#clean
        for i in range(1, len(data)):
            data[i][1] = data[i][1].replace('\'', '')
            data[i][1] = data[i][1].replace('[', '')
            data[i][1] = data[i][1].replace(']', '')
            data[i][1] = data[i][1].replace(' ', '')
            data[i][1] = data[i][1].split(',')
    except AttributeError:
        print('AttributeError')
    #placesdictionary
    conlist = []

    jieba.load_userdict('bigdict_v4-2.csv')#指定使用者自定義斷字字典

    for i in range(1, len(data)):
        conlist.append(list(jieba.cut(data[i][0], cut_all=False)))
    #匯入地點字典
    with open('bigdict_v4-2.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        raw = list(reader)
    rawdict = []

    for i in raw:
        rawdict.append(i[0])

    #貼地點
    location = []
    for i in range(len(conlist)):
        tmp = []
        for j in range(len(conlist[i])):
            for k in range(len(rawdict)):
                if conlist[i][j] == rawdict[k]:
                    tmp.append(rawdict[k])
        location.append(tmp)

    conindex = []

    for i in range(len(location)):
        for j in range(len(location[i])):
            location[i][j] = location[i][j].replace(' ', '')#去空值
        location[i] = list(filter(None, location[i]))#去無值
        location[i] = list(set(location[i]))#去重複值
        conindex.append(i)
        taginlocation.append(location[i])

    #tagsdictionary
    taglist = []

    with open('tags_v2', 'r', encoding='utf-8') as file:
        taglist.append(file.read())

    taglist = taglist[0].split(' ')
    taglist = list(filter(None, taglist))
    #製作稀疏矩陣
    df = pd.DataFrame(columns=taglist, index = conindex)
    print(len(df))
    try:
        for i in range(len(data)):
            #print(i)
            for j in range(1, len(data[i][1])):
                for k in range(len(taglist)):
                    #print(len(data[i]))
                    #print(j, k)
                    if data[i][1][j] == taglist[k]:
                        #print(j, k)
                        #print(taglist[k])
                        #print(i, df.loc[i]['tag'][j], taglist[k])
                        #print(dfz.loc[1])
                        df.loc[i][taglist[k]] = 1
                    else:
                        if df.loc[i][taglist[k]] == 1:
                            continue
                        else:
                            df.loc[i][taglist[k]] = 0
    except KeyError:
        print('KeyError')
        df.loc[len(df)-1] = df.loc[len(df)-2]# fakevalue

    #訓練資料
    testdata = []

    for i in range(1, len(data)):
        testdata.append(data[i][0])

    vectorizer = CountVectorizer()
    t1 = np.array(testdata)
    t1 = vectorizer.fit_transform(t1)
    #檢查nan，若有則以0代替
    for i in range(len(df)):
        for j in range(len(df.loc[i])):
            if pd.isnull(df.loc[i][j]):
                df.loc[i][j] = 0
            else:
                continue
    #模型
    model = []
    for i in range(len(taglist)):
        MNB_model = MultinomialNB()
        df[taglist[i]] = np.array(df[taglist[i]], dtype=int)
        #print(t1.shape)
        #print(df[taglist[i]].shape) #檢查是否有長度不一
        model.append(MNB_model.fit(t1, df[taglist[i]]))

    #testmodel
    try:
        with open(filename[z], 'r', encoding='utf-8') as file:
            traindata = file.read()

        traindata = traindata.split('\n')

        t2 = np.array(traindata)
        t2 = vectorizer.transform(t2)

        trainresult = []

        for i in range(len(model)):
            trainresult.append(list(model[i].predict(t2)))
    except IndexError:
        break
    #記錄地點
    temperatecon = []

    for i in range(len(traindata)):
        k=0
        temperatenam = []
        for j in range(len(trainresult)):
            k = k+trainresult[j][i]
            #print(trainresult[j][i])
            if trainresult[j][i]==1:
                temperatenam.append(taglist[j])
        if k>0:
            temperatecon.append([i, temperatenam])

    for i in range(len(temperatecon)):
        data.append([traindata[temperatecon[i][0]], temperatecon[i][1]])
        print(temperatecon[i][1])

#result
df.to_csv('testresult.csv', index=0)

with open('tagnamepertext.csv', 'w', encoding='utf-8') as file:
    writer = csv.writer(file)
    for i in taginlocation:
        writer.writerow(i)