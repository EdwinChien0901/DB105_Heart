這個資料夾的程式主要為產生景點間關聯性矩陣的各步驟

使用到的素材檔案分別為:
all.csv          痞克邦網誌
xuite_1.txt      隨意窩網誌
bigdict_new.csv  旅遊景點列表
tags_v3          景點特徵分類列表
tag_list.csv     判斷特徵分類的依據

---01.ETL_data.py---
主要將所有素材檔案轉換成dataframe的格式，並存成csv供後續使用
也稍微篩選了一下網誌的內容，將字數較少沒意義的網誌去除

---02.find_spot.py---
針對每一篇網誌，找尋是否有提到列表中的景點，並新增景點的欄位至dataframe中

---03.auto_tag.py---
針對每一篇網誌，找尋是否有提到特徵列表的關鍵字，
如果有的話就將對應的標籤新增至dataframe的tag欄位中
最後存取包含"網誌"、"景點"、"標籤"三個欄位的dataframe進csv裡面

---04.spot_to_tag.py---
將景點以及標籤獨立出來，並單獨計算每個景點出現時，該篇網誌獲得那些標籤。
以景點為單位計算其獲得的各個不同標籤數量。

---05.spot_matrix.py---
首先計算每個景點，其所拿到的各個標籤所占比例，接著建立景點x景點的方形矩陣，
利用標籤的所佔比例，倆倆進行餘弦相似性的計算，最後產出以tag分類為基礎的景點間關聯性矩陣。
