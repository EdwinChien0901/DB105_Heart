import os
import pandas as pd
import re
import json
import time
import random
import requests
from pyquery import PyQuery as pq

url_base = 'https://www.instagram.com/explore/tags/'
uri = 'https://www.instagram.com/graphql/query/?query_hash=bd33792e9f52a56ae8fa0985521d141d&variables=%7B%22tag_name%22%3A%22{tag_name}%22%2C%22first%22%3A7%2C%22after%22%3A%22{cursor}%3D%3D%22%7D'

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
}

ss = requests.session()


def get_html(url):
    try:
        response = ss.get(url, headers=headers)
        if response.status_code == 200:
            # print(response.text)
            return response.text
        else:
            print('請求網頁代碼錯誤，錯誤狀態碼：', response.status_code)
    except Exception as e:
        print("get_html",e)
        return None


def get_json(url):
    try:
        response = ss.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print('請求網頁代碼錯誤，錯誤狀態碼：', response.status_code)
    except Exception as e:
        print("get_json",e)
        time.sleep(60 + float(random.randint(1, 4000)) / 100)
        return get_json(url)


# 針對照片的網址提出請求，會回傳照片的二進位值，函式將會回傳該照片的內容，由於每張照片長得不一樣，
# 因此可以確保除非是一模一樣的圖片，否則將會得到不一樣的回傳值，並依據不同的回傳值丟入hash程式，得到不同的加密字串
def get_content(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.content
        else:
            print('照片請求錯誤，錯誤狀態碼：', response.status_code)
    except Exception as e:
        print("get_content",e)
        return None


def get_texts(html):
    tag_name = re.findall('\"name\":\"(.+)\",\"allow_following', html)[0]
    print('tag_name：' + tag_name)
    doc = pq(html)
    items = doc('script[type="text/javascript"]').items()
    for item in items:
        if item.text().strip().startswith('window._sharedData'):
            js_data = json.loads(item.text()[21:-1], encoding='utf-8')
            edges = js_data["entry_data"]["TagPage"][0]["graphql"]["hashtag"]["edge_hashtag_to_media"]["edges"]
            page_info = js_data["entry_data"]["TagPage"][0]["graphql"]["hashtag"]["edge_hashtag_to_media"]['page_info']
            cursor = page_info['end_cursor']
            flag = page_info['has_next_page']
            tag_post_data = pd.DataFrame()
            for edge in edges:
                if edge['node']['edge_media_to_caption']['edges']:
                    tag_text = edge['node']['edge_media_to_caption']['edges'][0]['node']['text']
                    post_id = edge['node']['id']
                    post_shortcode = edge['node']['shortcode']
                    owner_id = edge['node']['owner']['id']
                    df = pd.DataFrame(
                        data=[{'owner_id': owner_id,
                               'post_shortcode': post_shortcode,
                               'post_id': post_id,
                               'tag_text': tag_text}],
                        columns=['owner_id', 'post_shortcode', 'post_id', 'tag_text'])
                    tag_post_data = tag_post_data.append(df, ignore_index=True)
            print(cursor, flag)
    while flag and len(tag_post_data) < 2000:
        try:
            url = uri.format(tag_name=tag_name, cursor=cursor[:-2])
            print(url)
            js_data = get_json(url)
            # print(js_data['data']['hashtag']['edge_hashtag_to_media']['edges'][0])
            infos = js_data['data']['hashtag']['edge_hashtag_to_media']['edges']
            cursor = js_data['data']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']
            flag = js_data['data']['hashtag']['edge_hashtag_to_media']['page_info']['has_next_page']
            for info in infos:
                if info['node']['edge_media_to_caption']['edges']:
                    # print(info['node']['edge_media_to_caption'])
                    tag_text = info['node']['edge_media_to_caption']['edges'][0]['node']['text']
                    post_id = info['node']['id']
                    post_shortcode = info['node']['shortcode']
                    owner_id = info['node']['owner']['id']
                    df = pd.DataFrame(
                        data=[{'owner_id': owner_id,
                               'post_shortcode': post_shortcode,
                               'post_id': post_id,
                               'tag_text': tag_text}],
                        columns=['owner_id', 'post_shortcode', 'post_id', 'tag_text'])
                    tag_post_data = tag_post_data.append(df, ignore_index=True)
        except Exception as e:
            print('爆炸啦~~!')
            print(e)
            return tag_post_data

        print(cursor, flag)
        # time.sleep(4 + float(random.randint(1, 800))/200)    # if count > 2000, turn on
    return tag_post_data


def main(tag):
    print(tag)
    url = url_base + tag + '/'
    print(url)
    html = get_html(url)
    tag_texts = get_texts(html)
    print(len(tag_texts))
    print(type(tag_texts))

    dirpath = './ig_text_down/'
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    tag_texts.to_csv('{}/{}.csv'.format(dirpath, tag), encoding='utf-8-sig')

if __name__ == '__main__':
    tag_name = '四四南村'
    start = time.time()
    main(tag_name)
    print('Complete!!!!!!!!!!')
    end = time.time()
    spend = end - start
    hour = round(spend // 3600)
    minu = round((spend - 3600 * hour) // 60)
    sec = spend - 3600 * hour - 60 * minu
    print(f'一共花費{hour}小時{minu}分鐘{round(sec)}秒')

    # 印出session所收集到的coookies
    # print(ss.cookies)
