import csv
from os import listdir
from os.path import isfile, isdir, join
import pandas as pd
import time


# 輸入list，回傳每個元素皆去掉頭尾空白的list，並去除空值
def list_strip(ori_list):
    for ll, content in enumerate(ori_list):
        ori_list[ll] = content.strip()
    ori_list = list(filter(None, ori_list))
    return ori_list


# 輸入一段PO文，回傳文章中的tag列表
def get_tag(post_text_def):
    tag_list = str(post_text_def).split('#')[1:]
    for j, tag00 in enumerate(tag_list):
        tag_list[j] = tag00.split(' ')[0].split('\n')[0].split('　')[0]
    return tag_list


# 輸入pair值的list，以字典型態回傳每個景點出現的文章ID
def pair_to_post_index(spot_in_article_list_def):
    spot_tag_index = {}
    for ll, spot_pair in spot_in_article_list_def:
        if ll not in spot_tag_index:
            spot_tag_index[ll] = [spot_pair]
        else:
            spot_tag_index[ll].append(spot_pair)
    return spot_tag_index


def main():
    # 讀取景點列表
    spot_df = pd.read_csv('bigdict_v4.csv', encoding='utf-8')
    spot_list = list_strip(spot_df['value'].values.tolist())
    print('景點數量', len(spot_list))

    # 讀取post內文
    df = pd.read_csv('sample.csv', encoding='utf-8')
    ig_text_str = df['tag_text']
    print('post篇數:', len(ig_text_str))
    
    # 將PO文內容轉成list，並針對每篇取得tag，目前是做成tag的list
    sample_list = ig_text_str.values.tolist()
    tag_list = []

    for i, post_text in enumerate(sample_list):
        each_tag_list = get_tag(post_text)
        tag_list.append(each_tag_list)


    # 比對景點list，紀錄文章編號及景點tag的pair值，因為景點的字典有問題，所以改以對欄位的方式比較保險
    spot_in_article_list = []
    for k, each_tag_list in enumerate(tag_list):
        for tag in each_tag_list:
            if tag in spot_list:
                spot_in_article_list.append((k, spot_df['key'][spot_list.index(tag)]))

    spot_index_dict = pair_to_post_index(spot_in_article_list)

    # 每篇文章的index為key值，針對每個key值的value，兩兩寫成tuple
    spot_index_list = []
    for kkk in spot_index_dict.keys():
        if len(spot_index_dict[kkk]) == 1:
            pass
        else:
            for lll, spot1 in enumerate(spot_index_dict[kkk]):
                for mmm, spot2 in enumerate(spot_index_dict[kkk][lll+1:]):
                    if spot1 > spot2:
                        spot_index_list.append(((spot2, spot1), kkk))
                    elif spot1 == spot2:
                        pass
                    else:
                        spot_index_list.append(((spot1,spot2), kkk))

    # 轉換成df，並計算每種組合出現的次數
    spot_index_df = pd.DataFrame()
    for a in spot_index_list:
        df = pd.DataFrame(data=[{'spot_pair': a[0],
                               'post_index': a[1]}],
                        columns=['spot_pair', 'post_index'])
        spot_index_df = spot_index_df.append(df, ignore_index=True)
    
    spot_index_df.groupby('spot_pair').count().sort_values(by='post_index',ascending=False).to_csv('spot_relationship.csv', encoding='utf-8')
    print(spot_index_df.groupby('spot_pair').count().sort_values(by='post_index',ascending=False))


if __name__ == '__main__':    
    start = time.time()

    main()

    end = time.time()
    spend = end - start
    hour = round(spend // 3600)
    minu = round((spend - 3600 * hour) // 60)
    sec = spend - 3600 * hour - 60 * minu
    print(f'一共花費{hour}小時{minu}分鐘{round(sec)}秒')
