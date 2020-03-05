import pandas as pd
import math

def list_strip(ori_list):
    for ll, content in enumerate(ori_list):
        ori_list[ll] = content.strip()
    ori_list = list(filter(None, ori_list))
    return ori_list

def similar(aa, bb):
	if sum(aa) * sum(bb):
		up = 0
		downa = 0
		downb = 0
		for i, a in enumerate(aa):
			if  aa[i] or bb[i]:
				up += aa[i] * bb[i]
				downa += aa[i] ** 2
				downb += bb[i] ** 2
		simi = up / ((downa ** 0.5 )*(downb ** 0.5))
		return simi
	else:
		return 0


# 讀取所有tag
tag_list = []
with open('tags_v3', 'r', encoding='utf-8') as file:
        tag_list.append(file.read())

tag_list = list_strip(tag_list[0].split(' '))
print('共有{}個標籤'.format(len(tag_list)))

spot_tag_df = pd.read_csv('spot_tag_count.csv')
# print(spot_tag_df)
# print(spot_tag_df['spot'])
# print(spot_tag_df.sum())
# print(spot_tag_df['sum'].value_counts())

# --計算每個景點本身tag的權重--
# 先建立空值矩陣
weight_df = spot_tag_df.iloc[:,:len(tag_list)+1]
for tag in tag_list:
	weight_df[tag] = 0
# weight_df['sum'] = 0
# print(weight_df.sum())

# 計算權重(這邊需要調整)
for i, spot in enumerate(weight_df['spot']):
	if i % 100 == 0:
		print(i)
	if spot_tag_df.at[i, 'sum'] != 0:
		# weight_df.loc[i, 'sum'] = 1
		for tag in tag_list:
			if spot_tag_df.at[i, tag] != 0:
				weight_df.loc[i, tag] = spot_tag_df.loc[i, tag] / spot_tag_df.loc[i, 'sum'] * math.log(spot_tag_df.loc[i, 'sum'])
print(weight_df)

# --用餘弦相似性計算景點之間是否相似--
# 建立景點x景點矩陣
spot_relation_df = pd.read_csv('spot_list.csv',header = None)
spot_relation_df.columns = ['spot']

for spot in spot_relation_df['spot']:
	spot_relation_df[spot] = ''

# print(spot_relation_df)


for j in range(len(spot_relation_df['spot'])):
	for k in range(len(spot_relation_df['spot'])):
		if j != k:
			aa = weight_df.loc[j,:].values.tolist()[1:]
			bb = weight_df.loc[k,:].values.tolist()[1:]
			spot_relation_df.iloc[j, k+1] = similar(aa,bb)
	print(j)
	spot_relation_df.info(memory_usage="deep")

spot_relation_df.to_csv('spot_matrix.csv',index=False)

