# 自動幫網誌貼標籤的程式，將會輸入網誌的dataframe，回傳等長的dataframe，內容為每一篇網誌裡面的tag
import pandas as pd

# 給def一字串，自動找尋裡面的tag，回傳以空格分隔的字串
def autoTag(article):
	tt = ''
	tag_df = pd.read_csv('tag_list.csv', header=0)
	for i, text in enumerate(tag_df['text']):
		if text.strip() in article:
			if len(tt) > 0:
				tt += ' '
				tt += tag_df['tag'][i].strip()
			else:
				tt = tag_df['tag'][i].strip()
	return tt

if __name__ == '__main__':
	# df = pd.read_csv('combine.csv')
	df = pd.read_csv('con_spot.csv')
	df['tag'] = ''
	for i, article in enumerate(df['con']):
		# print(len(df['con'][i]))
		df['tag'][i] = autoTag(df['con'][i])
	print(df)
	# df.to_csv('xuite_tagged.csv',index=False)
	df.to_csv('con_spot_tag.csv', index = False)
	# main()