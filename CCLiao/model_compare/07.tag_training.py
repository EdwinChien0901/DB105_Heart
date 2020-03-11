import csv
import jieba
from wordcloud import WordCloud
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import BernoulliNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
import numpy as np


# 輸入list，回傳每個元素皆去掉頭尾空白的list，並去除空值
def list_strip(ori_list):
    for ll, content in enumerate(ori_list):
        ori_list[ll] = content.strip()
    ori_list = list(filter(None, ori_list))
    return ori_list

# 讀取tag列表
tag_list = []
with open('tags_v3', 'r', encoding='utf-8') as file:
        tag_list.append(file.read())

tag_list = tag_list[0].split(' ')
tag_list = list_strip(tag_list)
print('共有{}個標籤'.format(len(tag_list)))

# 讀取資料 預計有2000篇網誌 應該是拿痞克邦及隨意窩亂數排列，且貼完標籤
# 讀取完之後將資料分成train_data及test_data，到這邊皆為dataframe格式，分別為1600筆及400筆
all_data_df = pd.read_csv("shuffle_data_set.csv")
train_data_df = all_data_df[:3200]
test_data_df = all_data_df[3200:4000]

# 將訓練集以及測試集轉換成model可以吃進去的格式
print("共有{}篇訓練資料".format(len(train_data_df)))
vectorizer = CountVectorizer()
train_data = np.array(train_data_df['con'].values.tolist())
train_data = vectorizer.fit_transform(train_data)

print("共有{}篇測試資料".format(len(test_data_df)))
test_data = np.array(test_data_df['con'].values.tolist())
test_data = vectorizer.transform(test_data)


# 針對不同的mode進行訓練，每個model將會對不同的tag分別進行2元分類的訓練
# 建立model
MNB_model = []
BNB_model = []
CLF_model = []

# 訓練MultinomialNB
for i in range(len(tag_list)):
    mnb_model = MultinomialNB()
    # print(train_data_df[tag_list[i]])
    train_data_result = np.array(train_data_df[tag_list[i]], dtype=int)
    # train_data_result.todense()
    MNB_model.append(mnb_model.fit(train_data, train_data_result))

# 訓練BernoulliNB
for i in range(len(tag_list)):
    bnb_model = BernoulliNB()
    train_data_result = np.array(train_data_df[tag_list[i]], dtype=int)
    BNB_model.append(bnb_model.fit(train_data, train_data_result))

# 訓練隨機森林 RandomForestClassifier() # max_depth=2, random_state=0)
for i in range(len(tag_list)):
    clf_model = RandomForestClassifier(min_samples_split=5,min_samples_leaf=3,)
    train_data_result = np.array(train_data_df[tag_list[i]], dtype=int)
    CLF_model.append(clf_model.fit(train_data, train_data_result))

# 使用訓練好的model預測測試集
MNB_predict_result = []
BNB_predict_result = []
CLF_predict_result = []

for i in range(len(MNB_model)):
    MNB_predict_result.append(list(MNB_model[i].predict(test_data)))

for i in range(len(BNB_model)):
    BNB_predict_result.append(list(BNB_model[i].predict(test_data)))

for i in range(len(CLF_model)):
    CLF_predict_result.append(list(CLF_model[i].predict(test_data)))

MNB_df = pd.DataFrame(MNB_predict_result).T
BNB_df = pd.DataFrame(BNB_predict_result).T
CLF_df = pd.DataFrame(CLF_predict_result).T

print(MNB_df.sum())
print(BNB_df.sum())
print(CLF_df.sum())

# 讀取正確解答
correct_df = pd.DataFrame()
for i in range(len(tag_list)):
	correct_df[tag_list[i]] = test_data_df[tag_list[i]]
correct_df.reset_index(drop=True, inplace=True)
# print(correct_df.sum())

# 將訓練結果存成csv
MNB_df.to_csv('result_MNB.csv',index=False)
BNB_df.to_csv('result_BNB.csv',index=False)
CLF_df.to_csv('result_CLF.csv',index=False)

correct_df.to_csv('result_correct.csv',index=False)