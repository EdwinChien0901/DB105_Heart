import time
from os import listdir
from os.path import isfile, isdir, join
from pic_similarity import pic_compare
from multiprocessing import Pool

if __name__ == '__main__':
    path = "./ig_download"
    files = listdir(path)  # 取得所有檔案與子目錄名稱
    dir_list = []
    for f in files:
        if isdir(r'./ig_download/{}'.format(f)):
            # print("資料夾：", f)
            dir_list.append(f)
        elif isfile(r'./ig_download/{}'.format(f)):
            print("檔案：", f)
    # print(dir_list)

    start = time.time()

    pool = Pool()  # 設定要有幾個執行緒去跑，如果裡面沒寫數字，就會自動偵測你有幾個核心，有幾個生幾個，(用學校的應該會很快)
    pool.map(pic_compare, dir_list)  # 用法是 .map(  你的function  ,  所有要丟的參數(iterable)  )  ， 執行緒會自動去接每個 iterable內的元素
    pool.close()  # 關閉pool，使它不要再接新的任務，表示餵完參數了
    pool.join()  # 等待所有執行緒完成

    print('Complete!!!!!!!!!!')
    end = time.time()
    spend = end - start
    hour = round(spend // 3600)
    minu = round((spend - 3600 * hour) // 60)
    sec = spend - 3600 * hour - 60 * minu
    print(f'一共花費{hour}小時{minu}分鐘{round(sec)}秒')