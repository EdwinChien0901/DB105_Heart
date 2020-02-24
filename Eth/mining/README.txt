000.csv 
	一開始的訓練集，開頭的con, tag在輸出檔案testresult.csv裡是第一行(全部0)，但tagnamepertext.csv不受影響

1~5.csv
	測試集們
combinetest.py
	主程式
tagnamepertext.csv
	記錄地點的輸出檔，一行表示一段文字中提到，並且有在大字典裡的地點。
	有些空白的行是因為沒有檢測到相符合的地點。
testresult.csv
	稀疏矩陣，每一橫列代表一段文章中出現的標籤(1為有，0為無)，每一直排代表一個標籤的出現與否(1為有，0為無)
travel98_1、xuite_1
	文章原檔