import requests
from lxml import etree
import multiprocessing
import json
import pandas as pd
import time

#  旅行酒吧 台北、新北遊記
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
headers = {'user-Agent': user_agent}
def main():
    starturl = 'https://travel98.com/article?filter=journal&area=368&page='

    Time = []
    Schedule = []
    Title = []
    Article = []

    for i in range(1, 44):  # 總頁數43+1
        print('-' * 50, str(i), '-' * 50, )
        url = starturl + str(i)

        ss = requests.Session()
        res = ss.get(url, headers=headers)
        tree = etree.HTML(res.content)

        url = tree.xpath('//*[@id="article_list"]/div/a/@href')
        # print(len(url)) #確認url個數
        # print(url)

        for each_article in url:
            ss = requests.Session()
            res = ss.get(each_article, headers=headers)
            tree = etree.HTML(res.content)
            # soup = BeautifulSoup(res.content, 'html.parser')

            # 文章時間
            time = tree.xpath('//li[@class="brief_info date_icon release_date"]/text()')
            time1 = "".join(time)
            # print('time:', time1)

            # 行程規劃
            schedule = tree.xpath('//div[@class="jsl_ct"]//span/text()')
            # schedule = tree1.xpath('//span[@class="day_poi_name"]/text()')
            # print(type(schedule))
            schedule1 = "".join(schedule)  # list轉string
            # print('schedule:', schedule1)

            # 標題名稱
            title = tree.xpath('//h1[@class="article_title"]/text()')
            # print(type(title))
            title1 = "".join(title)  # list轉string
            # print(title1)
            # print('title:', title1)

            # 文章內容
            article = tree.xpath('//div[@class="article_body"]//p[@class="journal_poi_desc"]/text()')
            for a, b in enumerate(article):  # 去除空白
                article[a] = b.strip()
            article = list(filter(None, article))
            article1 = "".join(article)

            # print('article:', article1)
            # print('-' * 50)

            dict = {'Title': title1, 'Content': article1, 'Schedule': schedule1, 'Time': time1}  # 建立字典
            print(dict)

            # 加入設定之list
            Time.append(time1)
            Schedule.append(schedule1)
            Title.append(title1)
            Article.append(article1)

            # with open('./document/{}.json'.format('travel_981'), 'a+', encoding='utf-8') as f:
            #     json.dump(dict, f)
                # f.close()

    # print(len(Title))  # 查看個數
    # print(Title)  # 看list內容

    # df = pd.DataFrame({'Title': Title, 'Content': Article, 'Schedule': Schedule, 'Time': Time})  # Dataframe建立欄位及輸入
    # print(df)
    # df.to_csv('D:/guanl/Dropbox/PycharmProjects/PyETL-prac/trave98.csv', index=0, encoding='utf-8')  #  輸出csv
    # df.to_csv('E:/PycharmProjects/0Project_documwnt/travel_981.csv', index=0, encoding='utf-8-sig')  #  輸出csv
    # df.to_json('E:/PycharmProjects/0Project_documwnt/travel_98.js', orient='records', force_ascii=False)  # 輸出json

if __name__ == '__main__':
    startime = time.time()  # 紀錄開始時間
    pool = multiprocessing.Pool()  # 設定要有幾個執行緒去跑，如果沒寫數字，會自動偵測你有幾個核心，有幾個生幾個
    pool.map(main())  # 用法是 .map(你的function, 所有要丟的變數(iterable)  )  ， 執行緒會自動去接每個 iterable內的元素
    pool.close()  # 關閉pool，使它不要再接新的任務，表示餵完參數了
    pool.join()  # 等待所有執行緒完成

    print('Total time: {} s'.format(time.time() - startime))  # 列印總共花費時間