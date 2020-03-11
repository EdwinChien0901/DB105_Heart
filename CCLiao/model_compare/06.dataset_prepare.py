import csv
import jieba
from wordcloud import WordCloud
import pandas as pd
import numpy as np
from sklearn.utils import shuffle

# 停用字字典(將停用字放在一個list裡面)==============================================
stopword_path = r'./dict_for_jieba/stopwords_v2.txt'
stopword_list = []
with open(stopword_path, 'r', encoding='utf-8') as f:
    for eachline in f.readlines():
        eachline = eachline.strip()  # 去除前後空白
        stopword_list.append(eachline.replace('\n', ''))
# print(stopword_list)

# 加入自定義字典 & 繁中字典=========================================================
jieba.set_dictionary('./dict_for_jieba/big_new_dict.txt')
jieba.load_userdict('./dict_for_jieba/self_define_dict.txt')  ### 自定義字典一定要放在繁中字典的code下面!!!!!


# 輸入list，回傳每個元素皆去掉頭尾空白的list，並去除空值
def list_strip(ori_list):
    for ll, content in enumerate(ori_list):
        ori_list[ll] = content.strip()
    ori_list = list(filter(None, ori_list))
    return ori_list


# 讀取所有拿痞克邦及隨意窩的網誌，且為貼好標籤的檔案，將其對照tag計數，並隨機抽出2000篇存檔
df_all = pd.read_csv('con_spot_tag.csv')
df_all.dropna(axis=0, subset=['tag'], inplace=True)
df_all.reset_index(drop=True, inplace=True)
# print(df_all.loc[:1999,['con','tag']])
print(df_all)

# 讀取所有tag
tag_list = []
with open('tags_v3', 'r', encoding='utf-8') as file:
        tag_list.append(file.read())

tag_list = list_strip(tag_list[0].split(' '))
print('共有{}個標籤'.format(len(tag_list)))

# 將每篇網誌斷詞
data_set_df = pd.DataFrame()
for i, con in enumerate(df_all['con']):
    segments = jieba.cut(con)
    remainderWords = " ".join(list(filter(lambda a: a not in stopword_list and a != '\n', segments)))
    df = pd.DataFrame(data=[{'con': remainderWords}],columns=['con'])
    data_set_df = data_set_df.append(df, ignore_index=True)
    if i % 100 == 0:
        print(i)
print(data_set_df)


# 建立矩陣
for tag in tag_list:
    data_set_df[tag] = 0
data_set_df['sum'] = 0

# 貼上每篇網誌的標籤
for i, con in enumerate(data_set_df['con']):
    tags = list_strip(df_all['tag'][i].split(' '))

    for tag in tags:
        if tags.count(tag)>1:
            print(tags)
        data_set_df.loc[i, tag] += 1
    if i % 100 == 0:
        print(i)

# 儲存結果
# data_set_df.to_csv('data_set.csv',index=False)
# shuffle(data_set_df).to_csv('shuffle_data_set.csv',index=False)