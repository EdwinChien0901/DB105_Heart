import pandas as pd

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

# 讀取測試結果，替換欄位
MNB_df = pd.read_csv('result_MNB.csv')
BNB_df = pd.read_csv('result_BNB.csv')
CLF_df = pd.read_csv('result_CLF.csv')

MNB_df.columns = tag_list
BNB_df.columns = tag_list
CLF_df.columns = tag_list

df_list = ['MNB_df', 'BNB_df', 'CLF_df']


correct_df = pd.read_csv('result_correct.csv')
# print(correct_df)
tmp = '{}_result'.format(df_list[0])

# 計算每個模型的準確率、accurary等，計算TP、TN、FP、FN
MNB_df_result = pd.DataFrame()
BNB_df_result = pd.DataFrame()
CLF_df_result = pd.DataFrame()


df_result_list = [MNB_df_result, BNB_df_result, CLF_df_result]
for ddd in df_result_list:
    ddd['col'] = ['TP', 'FP', 'FN', 'TN', 'Total']
    for tag in tag_list:
        ddd[tag] = 0


for i, df_name in enumerate(df_list):
    for tag in tag_list:
        TP = 0; FP = 0; FN = 0; TN = 0; count = 0 
        for j, aa in enumerate(correct_df['公園']):
            if correct_df[tag][j] == 1:
                if eval(df_name)[tag][j] == 1:
                    TP += 1
                else:
                    FP += 1
            else:
                if eval(df_name)[tag][j] == 1:
                    FN += 1
                else:
                    TN += 1
        count = TP + FP + FN + TN
        # print(df_name)
        # print('TP: {}、 FP: {}、 FN: {}、 TN: {}、 Total: {}'.format(TP, FP, FN, TN, count))
        df_result_list[i].loc['TP',tag] = TP
        df_result_list[i].loc['FP',tag] = FP
        df_result_list[i].loc['FN',tag] = FN
        df_result_list[i].loc['TN',tag] = TN
        df_result_list[i].loc['count',tag] = count

MNB_df_result.to_csv('MNB_df_result.csv')
BNB_df_result.to_csv('BNB_df_result.csv')
CLF_df_result.to_csv('CLF_df_result.csv')