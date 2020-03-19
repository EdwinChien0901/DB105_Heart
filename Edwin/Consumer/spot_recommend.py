import pandas as pd

# 輸入景點名稱，如果有在列表當中的話，回傳前五推薦的景點
# 若是輸入的內容不再景點列表中，則回傳空值
def spotRecommend(placename):
	spot_matrix_df = pd.read_csv('spot_matrix.csv')
	if placename in spot_matrix_df['spot'].values.tolist():
		spot_matrix_df = spot_matrix_df.sort_values(by=placename, ascending=False)
		return spot_matrix_df['spot'][:5].values.tolist()
	else:
		return None

if __name__ == '__main__':
	place = '後火車站商圈'
	recommend_list = spotRecommend(place)
	print(recommend_list)