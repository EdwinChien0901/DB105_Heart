import os
import numpy as np
from keras.applications.vgg16 import VGG16
from keras.applications.vgg16 import preprocess_input
from keras.preprocessing import image


# 相似矩陣的計算
def cosine_similarity(featuresvector):
    # 與自己的轉置矩陣(T)做內積運算(dot)
    sim = featuresvector.dot(featuresvector.T)
    if not isinstance(sim, np.ndarray):
        sim = sim.toarray()
    # np.diagonal取對角線 np.sqrt取平方根
    norms = np.array([np.sqrt(np.diagonal(sim))])
    return (sim / norms / norms.T)


# 輸入地區名稱，以及需要比較的檔案名稱
def pic_compare(area_name, image_path):
    # 自 vgg16TestPic 目錄找出所有 JPEG 檔案
    images_filename_list = []
    images_data_tuple = []
    images_filename_list.append(image_path)
    images_data_tuple = np.expand_dims(image.img_to_array(image.load_img(image_path, target_size=(224, 224))), axis=0)

    pic_folder_path = './target_picture/'
    target_pic_list = os.listdir(pic_folder_path)
    # print(target_pic_list)
    for img_name in target_pic_list:
        if img_name.endswith(".jpg"):
            if img_name.startswith(area_name):
                img = image.load_img(r'./{}/'.format(pic_folder_path) + img_name, target_size=(224, 224))
                images_filename_list.append(img_name)
                x = image.img_to_array(img)
                x = np.expand_dims(x, axis=0)

                if len(images_data_tuple) == 0:
                    images_data_tuple = x
                else:
                    images_data_tuple = np.concatenate((images_data_tuple, x))
    if len(images_filename_list) == 1:
        return False
    # 轉圖片為VGG的格式
    images_data_tuple = preprocess_input(images_data_tuple)
    # include_top=False，表示只計算出特徵, 不使用最後3層的全連接層(不使用原來的分類器)
    model = VGG16(weights='imagenet', include_top=False)
    # 預測出特徵
    features = model.predict(images_data_tuple)
    # 計算特徵向量
    featuresVector = features.reshape(len(images_filename_list), 7 * 7 * 512)
    # 計算相似矩陣
    sim = cosine_similarity(featuresVector)
    result = sim[0].tolist()
    result.sort(reverse=True)
    # print(result)
    return True if result[1] > 0.4 else False


# 需要輸入地區名稱，還有檔案路徑
# 地區目前有 '雙北' '基隆市' '桃園市' '宜蘭縣' 四種
if __name__ == '__main__':
    ans = pic_compare('宜蘭縣', './sample3.jpg')
    print(ans)
