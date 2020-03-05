import pandas as pd
from sklearn.utils import shuffle


# # 簡單整理貼標過的文章，將str轉成list
# test_df = pd.read_csv('000.csv', header=0)
# for i, aa in enumerate(test_df['tag']):
#     test_df['tag'][i] = eval(aa)
# test_df.to_csv('clean_tagged_sample.csv',index=False)


# # 將已貼標的資料集隨機排序
# shuffle_df = shuffle(test_df)
# shuffle_df.to_csv('random_clean_tagged_sample.csv',index=False)


# 整理景點字典
# spot_df = pd.read_csv('bigdict_v4-2.csv',header = None)
spot_df = pd.read_csv('bigdict_new.csv',header = 0)['value']
# spot_df = pd.read_csv('spot_list.csv',header = None)
print(spot_df)
spot_df.drop_duplicates(inplace = True)
print(spot_df)
spot_df.to_csv('spot_list.csv',index=False)


# # 整理隨意窩文章
test_df = pd.read_table('xuite_1.txt')
testdata = test_df.values.tolist()
ttdata = []
for i, aaa in enumerate(testdata):
    if len(aaa[0]) > 10:
    	ttdata.append(aaa[0])
xuite_df = pd.DataFrame(ttdata)
xuite_df.columns = ['con']
xuite_df.to_csv('xuite.csv',index=False)



# 結合隨意窩以及痞克邦的網誌 約4500篇
bind_df = pd.DataFrame()
df3 = pd.DataFrame()
df4 = pd.DataFrame()
df1 = pd.read_csv('xuite.csv')
df2 = pd.read_csv('all.csv')
# 篩選隨意窩超過100字的網誌
for aa in df1['con']:
    if type(aa) == float:
        pass
    elif len(aa) > 100:
        df = pd.DataFrame(
        data=[{'con': aa
              }],
        columns=['con'])
        df3 = df3.append(df, ignore_index=True)
print(df3['con'])

# 篩選痞克邦超過300字的網誌
for aa in df2['article content']:
    if type(aa) == float:
        pass
    elif len(aa) > 300:
        df = pd.DataFrame(
        data=[{'con': aa
              }],
        columns=['con'])
        df4 = df4.append(df, ignore_index=True)
print(df4['con'])

bind_df = df3.append(df4, ignore_index=True)
print(bind_df)

for a in bind_df['con']:
    if len(a)<100:
        print(a)

# 存檔
bind_df.to_csv('combine.csv',index=False)
# shuffle(bind_df).to_csv('shuffle_combine.csv',index=False)
