# 讀取網誌、景點、tag的檔案
# df.drop_duplicates(subset = '', keep = first, inplace = False)

import pandas as pd

def list_strip(ori_list):
    for ll, content in enumerate(ori_list):
        ori_list[ll] = content.strip()
    ori_list = list(filter(None, ori_list))
    return ori_list

# 讀取網誌、景點、tag的檔案，將含有空值的資料去除
data_df = pd.read_csv('con_spot_tag.csv')
print(len(data_df))
data_df.dropna(axis=0, how='any', inplace=True)
data_df.reset_index(drop=True, inplace=True)
print(len(data_df))

print(data_df['spot'][2000])
print(data_df['tag'][2000])

# 讀取所有tag
tag_list = []
with open('tags_v3', 'r', encoding='utf-8') as file:
        tag_list.append(file.read())

tag_list = list_strip(tag_list[0].split(' '))
print('共有{}個標籤'.format(len(tag_list)))

# 讀取所有景點
spot_tag_df = pd.read_csv('spot_list.csv',header = None)
spot_tag_df.columns = ['spot']

# 建立矩陣
# aa = ['tag1','tag2','tag3']
for tag in tag_list:
	spot_tag_df[tag] = 0
spot_tag_df['sum'] = 0
# print(spot_df)

# 針對每筆資料寫入矩陣
# 把景點以及tag各自拆成list，然後寫成三層的迴圈
for i, nn in enumerate(data_df['spot']):
	spots = list_strip(data_df['spot'][i].split(' '))
	tags = list_strip(data_df['tag'][i].split(' '))
	for spot in spots:
		for tag in tags:
			# spot_tag_df[tag][spot_tag_df['spot'].isin([spot])] += 1
			spot_tag_df.loc[spot_tag_df.spot == spot, tag] += 1
			# spot_tag_df['sum'][spot_tag_df['spot'].isin([spot])] += 1
			spot_tag_df.loc[spot_tag_df.spot == spot, 'sum'] += 1
	if i % 100 == 0:
		print(i)
print(spot_tag_df)
print(spot_tag_df.sum())
# spot_tag_df.to_csv('spot_tag_count.csv',index=False)