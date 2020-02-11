import time
import requests
from ig_tag_go import tag_main
from multiprocessing import Pool

url_base = 'https://www.instagram.com/explore/tags/'
uri = 'https://www.instagram.com/graphql/query/?query_hash=90cba7a4c91000cf16207e4f3bee2fa2&variables=%7B%22tag_name%22%3A%22{tag_name}%22%2C%22first%22%3A7%2C%22after%22%3A%22{cursor}%3D%3D%22%7D'

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
}

ss = requests.session()


if __name__ == '__main__':
    spot_list = ['九份','淡水','台北101','八德落羽松','石門水庫','正濱漁港','野柳女王頭','羅東夜市']
    start = time.time()

    pool = Pool()  # 設定要有幾個執行緒去跑，如果裡面沒寫數字，就會自動偵測你有幾個核心，有幾個生幾個，(用學校的應該會很快)
    pool.map(tag_main, spot_list)  # 用法是 .map(  你的function  ,  所有要丟的參數(iterable)  )  ， 執行緒會自動去接每個 iterable內的元素
    pool.close()  # 關閉pool，使它不要再接新的任務，表示餵完參數了
    pool.join()  # 等待所有執行緒完成

    print('Complete!!!!!!!!!!')
    end = time.time()
    spend = end - start
    hour = round(spend // 3600)
    minu = round((spend - 3600 * hour) // 60)
    sec = spend - 3600 * hour - 60 * minu
    print(f'一共花費{hour}小時{minu}分鐘{round(sec)}秒')