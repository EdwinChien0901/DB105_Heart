import csv
import pandas as pd


# input為每一格皆為str形式的dataframe，回傳同樣也是str形式的dataframe
def findSpot(test_df):
	test_df['spot'] = ''
	spot_df = pd.read_csv('spot_list.csv',header = None)
	spot_df.columns = ['spot']
	for i, article in enumerate(test_df['con']):
		for j, spot in enumerate(spot_df['spot']):
			if spot in test_df['con'][i]:
				test_df['spot'][i] += spot
				test_df['spot'][i] += ' '
		if i % 100 == 0:
			print(i)
	return test_df


if __name__ == '__main__':
	# 讀取景點字典
	# test_df = pd.read_table('xuite_1.txt')
	test_df = pd.read_csv('combine.csv')
	print(test_df)
	# test_df.columns = ['con']
	# QQ = findSpot(test_df.iloc[:300,])
	QQ = findSpot(test_df)
	# print(QQ.iloc[:10,])
	QQ.to_csv('con_spot.csv',index=False)