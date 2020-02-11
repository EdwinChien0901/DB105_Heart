import os
import shutil
import time
import numpy as np
from keras.applications.vgg16 import VGG16
from keras.applications.vgg16 import preprocess_input
from keras.preprocessing import image


# 相似矩陣的計算
# 將test2目錄內的每一張jpg取出其特徵向量，並相互比較，利用 cosine 函數計算兩張照片特徵向量的角度，越接近 1，表示越相似

def cosine_similarity(featuresvector):
    # 與自己的轉置矩陣(T)做內積運算(dot)
    sim = featuresvector.dot(featuresvector.T)
    if not isinstance(sim, np.ndarray):
        sim = sim.toarray()
    # np.diagonal取對角線 np.sqrt取平方根
    norms = np.array([np.sqrt(np.diagonal(sim))])
    return (sim / norms / norms.T)


def pic_compare(tagname):
    # 自 vgg16TestPic 目錄找出所有 JPEG 檔案
    print('-----正在開始找出{}的目標圖片-----'.format(tagname))
    images_filename_list = []
    images_data_tuple = []

    pic_folder_path = r'.\ig_download\{}'.format(tagname)
    for img_path in os.listdir(pic_folder_path):
        if img_path.endswith(".jpg"):
            img = image.load_img(r'./{}/'.format(pic_folder_path) + img_path, target_size=(224, 224))
            images_filename_list.append(img_path)
            x = image.img_to_array(img)
            x = np.expand_dims(x, axis=0)

            if len(images_data_tuple) == 0:
                images_data_tuple = x
            else:
                images_data_tuple = np.concatenate((images_data_tuple, x))

    # 轉圖片為VGG的格式
    images_data_tuple = preprocess_input(images_data_tuple)
    # include_top=False，表示只計算出特徵, 不使用最後3層的全連接層(不使用原來的分類器)
    model = VGG16(weights='imagenet', include_top=False)
    # 顯示出模型摘要
    # model.summary()

    # 預測出特徵
    features = model.predict(images_data_tuple)

    # 計算特徵向量
    featuresVector = features.reshape(len(images_filename_list), 7 * 7 * 512)

    # 計算相似矩陣
    sim = cosine_similarity(featuresVector)
    # print(sim) #印出所有照片之間的特徵值, 越接近1.0, 照片越相近
    # print(len(sim))
    score_list = []
    for score2 in sim:
        score = score2.tolist()
        each_score = list(filter(lambda x: 0.9 > x > 0.4, score))
        each_score.sort(reverse=True)
        each_score_sum = sum(each_score[:5])  # / len(bb[:5])
        score_list.append(each_score_sum)

    # print(score_list)
    # print(len(score_list))
    # 找出最大值檔案的位置
    # print(score_list.index(max(score_list)))
    # 最大值檔案的檔名
    # print(images_filename_list[score_list.index(max(score_list))])

    shutil.copyfile(r'.\ig_download\{}\{}'.format(tagname, images_filename_list[score_list.index(max(score_list))]),r'./target_picture/{}.jpg'.format(tagname))
    print('-----已經完成找出{}的目標圖片-----'.format(tagname))

if __name__ == '__main__':
    start = time.time()
    pic_compare('正濱漁港')
    print('Complete!!!!!!!!!!')
    end = time.time()
    spend = end - start
    hour = round(spend // 3600)
    minu = round((spend - 3600 * hour) // 60)
    sec = spend - 3600 * hour - 60 * minu
    print(f'一共花費{hour}小時{minu}分鐘{round(sec)}秒')