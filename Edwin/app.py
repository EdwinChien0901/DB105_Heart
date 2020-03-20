from confluent_kafka import Producer
import redis
import sys, datetime
import os, cv2
import util
import numpy as np
import requests
import urllib
from io import BytesIO
import random

path1 = os.getcwd()
print(path1)
# 引用Web Server套件
from flask import Flask, request, abort

# 從linebot 套件包裡引用 LineBotApi 與 WebhookHandler 類別
from linebot import (
    LineBotApi, WebhookHandler
)

# 引用無效簽章錯誤
from linebot.exceptions import (
    InvalidSignatureError
)

# 載入json處理套件
import json

# 載入基礎設定檔
secretFileContentJson=json.load(open(r"./static/line_secret_key",'r',encoding='utf8'))
#server_url=secretFileContentJson.get("server_url")

# 設定Server啟用細節
app = Flask(__name__,static_url_path = "/material" , static_folder = r"./static/material/")

#("token:", secretFileContentJson.get("channel_access_token"))
#print("key:", secretFileContentJson.get("secret_key"))
#print("server:", secretFileContentJson.get("server_url"))
# 生成實體物件
line_bot_api = LineBotApi(secretFileContentJson.get("channel_access_token"))
handler = WebhookHandler(secretFileContentJson.get("secret_key"))
ques_url = secretFileContentJson.get("ques_url")

# 啟動server對外接口，使Line能丟消息進來
@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 引用會用到的套件
from linebot.models import (
    ImagemapSendMessage, TextSendMessage, ImageSendMessage, LocationSendMessage, FlexSendMessage, VideoSendMessage,
    ButtonsTemplate, CarouselTemplate, ConfirmTemplate, ImageCarouselTemplate
)

#from linebot.models.template import (
#    ButtonsTemplate, CarouselTemplate, ConfirmTemplate, ImageCarouselTemplate
#)

from linebot.models.template import *

def detect_json_array_to_new_message_array(fileName):
    # 開啟檔案，轉成json
    with open(fileName, "r", encoding="utf-8") as f:
        jsonArray = json.load(f)

    # 解析json
    returnArray = []
    for jsonObject in jsonArray:

        # 讀取其用來判斷的元件
        message_type = jsonObject.get('type')

        # 轉換
        if message_type == 'text':
            returnArray.append(TextSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'imagemap':
            returnArray.append(ImagemapSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'template':
            returnArray.append(TemplateSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'image':
            returnArray.append(ImageSendMessage.new_from_json_dict(jsonObject))
        #elif message_type == 'sticker':
        #    returnArray.append(StickerSendMessage.new_from_json_dict(jsonObject))
        #elif message_type == 'audio':
        #    returnArray.append(AudioSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'location':
            returnArray.append(LocationSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'flex':
            returnArray.append(FlexSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'video':
            returnArray.append(FlexSendMessage.new_from_json_dict(jsonObject))

    return returnArray

def getQuestionnaireReply(reToken, fileName):
    # 開啟檔案，轉成json
    with open(fileName, "r", encoding="utf-8") as fi:
        #print(fi.read())
        #print(type(fi.read()))
        jsonStr = fi.read()
        jsonStr = jsonStr.replace("{url}", "{0}?linebottoken={1}".format(ques_url, reToken))
        ##jsonStr = fi.read().replace("{url}", "{0}?linebottoken={1}".format(ques_url, reToken))
        #("jsonStr:", jsonStr)
        jsonArray = json.loads(jsonStr)

    # 解析json
    returnArray = []
    for jsonObject in jsonArray:
        returnArray.append(TextSendMessage.new_from_json_dict(jsonObject))

    return returnArray

# 引用套件
from linebot.models import (
    FollowEvent
)

# 關注事件處理
@handler.add(FollowEvent)
def process_follow_event(event):
    #註冊follower
    user_profile = line_bot_api.get_profile(event.source.user_id)
    # print("user_profile:", user_profile)
    #util.insertUserInfo(json.loads(json.dumps(vars(user_profile), sort_keys=True)))
    #util.sendKafkaMsg("followUser", json.loads(json.dumps(vars(user_profile), sort_keys=True)), event.reply_token)
    #util.sendKafkaMsg("followUser", user_profile, event.reply_token)
    util.sendKafkaMsg("ftest", user_profile, event.reply_token)
    #傳送訊息
    result_message_array = []
    replyJsonPath = r"./static/material/follow/reply.json"
    result_message_array = detect_json_array_to_new_message_array(replyJsonPath)

    # 消息發送
    line_bot_api.reply_message(
        event.reply_token,
        result_message_array
    )

# 引用套件
from linebot.models import (
    MessageEvent, TextMessage, PostbackEvent
)

# 文字消息處理
#@handler.add(MessageEvent,message=TextMessage)
@handler.add(MessageEvent)
def process_text_message(event):
    #print("message:", event.message)
    #print("type:", event.message.type)
    # 取出消息內User的資料
    user_profile = line_bot_api.get_profile(event.source.user_id)
    #print("user_profile:", user_profile)
    userName = json.loads(json.dumps(vars(user_profile),sort_keys=True))["display_name"]
    # 讀取圖片檔做影像辨視
    if event.message.type == "image":
        message_content = line_bot_api.get_message_content(event.message.id)
        with open("./{0}.jpg".format(event.reply_token), 'wb') as fd:
            for chunk in message_content.iter_content():
                fd.write(chunk)

        img1 = cv2.imread("./{0}.jpg".format(event.reply_token), 1)
        retval, buffer = cv2.imencode('.jpg', img1)
        img1_bytes = np.array(buffer).tostring()

        #print("token:", event.reply_token)
        util.setRedisImg(event.reply_token, img1_bytes)

        topicName = 'picsimilarity'
        cityName = util.redisGetData("{0}-Photo".format(userName))
        util.sendKafkaMsg(topicName, cityName, event.reply_token)

        tnow = datetime.datetime.now()

        isLock = util.redisGetData("{0}-pic".format(event.reply_token))
        print("isLock:", isLock)
        try:
            while isLock == None:
                # value = re.get(event.reply_token)
                isLock = util.redisGetData("{0}-pic".format(event.reply_token))
                diff = (datetime.datetime.now() - tnow).total_seconds()
                #print("seconds:", diff)
                assert diff < 30, "over time error"
        except AssertionError as error:
            print(error)
            return

        if isLock == "False":
            replyJsonPath = r"./static/material/PicLock/reply.json"
        else:
            replyJsonPath = r"./static/material/PicUnLock/reply.json"

        result_message_array = detect_json_array_to_new_message_array(replyJsonPath)

        # 發送
        line_bot_api.reply_message(
                event.reply_token,
                result_message_array
        )
        #file = util.getRedisImg(event.reply_token)
        #print("file:", file)
    else:
        #讀取文字訊息
        result_message_array = []
        if event.message.text in os.listdir(r'./static/material'):
            replyJsonPath = r"./static/material/{0}/reply.json".format(event.message.text)
            result_message_array = detect_json_array_to_new_message_array(replyJsonPath)

            # 發送
            line_bot_api.reply_message(
                event.reply_token,
                result_message_array
            )
        elif event.message.text in util.getSiteList():
            #prod = util.getProducer()
            # 步驟3. 指定想要發佈訊息的topic名稱
            topicName = 'recommendation'
            util.sendKafkaMsg(topicName, event.message.text, event.reply_token)

            #re = util.getRedis()
            tnow = datetime.datetime.now()

            siteList = util.redisLRange(event.reply_token, 0, -1)
            print("siteList:", siteList)
            try:
                while len(siteList) < 4:
                    #value = re.get(event.reply_token)
                    siteList = util.redisLRange(event.reply_token, 0, -1)
                    diff = (datetime.datetime.now() - tnow).total_seconds()
                    print("seconds:", diff)
                    assert diff < 30, "over time error"
            except AssertionError as error:
                print(error)
                return

            print(siteList)
            #value = ["金瓜石, 正濱漁港, 阿根納遺址, 龍磐步道", "小人國主題樂園,慈湖陵寢,石門水壩,小烏來天空步道", "龜山島,太平山國家森林遊樂區,羅東夜市,冬山河親水公園"]
            #siteList = value[random.randint(0,3)].split(",")
            #print("siteList:", siteList)
            #replyMsg = util.getTemplateJson();
            replyJsonPath = r"./static/material/re-site/reply.json"
            with open(replyJsonPath, 'r', encoding="utf-8") as f:
                replyMsg = f.read()

            sitesList = util.getSiteList()
            urlList = util.getUrlList()

            for i, r in enumerate(siteList):
                replyMsg = replyMsg.replace("site{}".format(i + 1), r)
                try:
                    replyMsg = replyMsg.replace("http://{}".format(i + 1), urlList[sitesList.index(r)])
                except:
                    print("recommendation:index out of range")

            print("replyMsg:", replyMsg)
            line_bot_api.reply_message(
                event.reply_token,
                TemplateSendMessage.new_from_json_dict(json.loads(replyMsg))
            )

            elkDoc = {}
            elkDoc["UserName"] = userName
            elkDoc["Place"] = event.message.text
            elkDoc["Recommedation"] = siteList
            elkDoc["DateTime"] = datetime.datetime.now()
            util.insertELK("rsite", elkDoc)
        else:
            return
            # line_bot_api.reply_message(
            #    event.reply_token,
            #    TextSendMessage.new_from_json_dict(json.loads(util.getUseMenuJson()))
            # )

#@handler.add(MessageEvent,message=ImageSendMessage)
#def process_image_message(event):
#    print("https://api.line.me/v2/bot/message/{0}/content".format(event.message.id))

from urllib.parse import parse_qs

# 引入相關套件
from linebot.models import (
    MessageAction, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    QuickReply, QuickReplyButton
)

@handler.add(PostbackEvent)
def process_postback_event(event):
    result_message_array = []
    replyJsonPath = r"./static/material/{0}/reply.json".format(event.postback.data)
    #print("replyJsonPath:", replyJsonPath)
    #print("answer:", event.postback.data.find(":::Q"))
    user_profile = line_bot_api.get_profile(event.source.user_id)
    #print("user_profile:", type(json.dumps(vars(user_profile),sort_keys=True)))
    userName = json.loads(json.dumps(vars(user_profile),sort_keys=True))["display_name"]
    cityMapping = {"TPE":"雙北", "KL":"基隆市", "IL":"宜蘭縣", "TY":"桃園市"}
    if event.postback.data == "question":
        replyJsonPath = r"./static/material/Question1/reply.json"
        result_message_array = detect_json_array_to_new_message_array(replyJsonPath)
        line_bot_api.reply_message(
            event.reply_token,
            result_message_array
        )
    elif event.postback.data.find(":::Q") >= 1:
        idx = event.postback.data[5:6]
        #print("idx:", idx)
        #if idx == "5":
        if idx == "4":
            #print("return result")
            timestamp = datetime.datetime.now().strftime("%Y%m%d")
            answer = event.postback.data[9:]
            key = "{0}-{1}".format(userName, timestamp)
            try:
                util.redisLPush(key, answer)

                allAnswer = util.redisLRange(key, 0, -1)
                # print("allAnswer:", allAnswer)
                doc = {}
                score = 0
                for an in allAnswer:
                    score += 1
                    doc[util.answerMapping[score - 1][an]] = score
                util.sendKafkaMsg("questionaire", doc, key)

                elkDoc = {}
                elkDoc["key"] = key
                elkDoc["UserName"] = userName
                elkDoc["DateTime"] = datetime.datetime.now()
                mappingList = util.getMappingList()
                for i, an in enumerate(allAnswer):
                    elkDoc["item{0}".format(i + 1)] = mappingList[i][an]

                util.insertELK("questionaire-2", elkDoc)
            except Exception as e:
                print(e)
            finally:
               #把redis資料清空
               util.redisLPopAll(key)
        else:
            timestamp = datetime.datetime.now().strftime("%Y%m%d")
            answer = event.postback.data[9:]
            util.redisLPush("{0}-{1}".format(userName, timestamp), answer)

            replyJsonPath = r"./static/material/Question{0}/reply.json".format(int(idx) + 1)
            result_message_array = detect_json_array_to_new_message_array(replyJsonPath)
            line_bot_api.reply_message(
                event.reply_token,
                result_message_array
            )
    elif event.postback.data.find(":::R") >= 1:
        areaList = ["臺北市", "新北市","基隆市","宜蘭縣","桃園市"]
        idx = int(event.postback.data[5:6])
        #print("idx:", idx)
        siteList = util.getSiteListByArea(areaList[idx])
        urlList = util.getUrlList()
        randomlist = random.sample([x for x in range(len(siteList))], 5)
        # print("randomlist:", randomlist)
        replyJsonPath = r"./static/material/recommedation/reply.json"
        with open(replyJsonPath, 'r', encoding="utf-8") as f:
            replyMsg = f.read()

        # print("replyMsg:", replyMsg)
        for i, r in enumerate(randomlist):
            replyMsg = replyMsg.replace("site{}".format(i + 1), siteList[r])
            try:
                replyMsg = replyMsg.replace("http://{}".format(i + 1), urlList[r])
            except:
                print("index out of range")

        # print("replyMsg:", replyMsg)
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage.new_from_json_dict(json.loads(replyMsg))
        )

    elif event.postback.data.find("Photo") > 1:
        ## 點擊後，切換至照片相簿選擇
        cameraRollQRB = QuickReplyButton(
            action=CameraRollAction(label="選擇照片")
        )

        quickReplyList = QuickReply(
            items=[cameraRollQRB]
        )
        key = "{0}-Photo".format(userName)
        util.redisDelKey(key)
        city = event.postback.data.split("_")[0]
        util.redisSetData(key, cityMapping[city])

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='選擇照片', quick_reply=quickReplyList)
        )
    elif event.postback.data.find("Camera") > 1:
        ## CameraAction
        cameraQuickReplyButton = QuickReplyButton(
            action=CameraAction(label="拍照")
        )
        quickReplyList = QuickReply(
            items=[cameraQuickReplyButton]
        )

        key = "{0}-Photo".format(userName)
        util.redisDelKey(key)
        city = event.postback.data.split("_")[0]
        util.redisSetData(key, cityMapping[city])

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='拍照上傳', quick_reply=quickReplyList)
        )
    elif  event.postback.data == "recommedation":
        siteList = util.getSiteList()
        urlList = util.getUrlList()
        #randomlist = random.sample([x for x in range(1000)], 5)
        #print("randomlist:", randomlist)
        with open(replyJsonPath, 'r', encoding="utf-8") as f:
            replyMsg = f.read()

        timestamp = datetime.datetime.now().strftime("%Y%m%d")
        key = "{0}-{1}-re".format(userName, timestamp)

        if util.getRedis(True).exists(key):
            reSite = util.redisLRange(key, 0, -1)

            # print("reSite:", reSite)
            # for i, r in enumerate(randomlist):
            for i, r in enumerate(reSite):
                # replyMsg = replyMsg.replace("site{}".format(i + 1), siteList[r])
                # replyMsg = replyMsg.replace("http://{}".format(i + 1), urlList[r])
                replyMsg = replyMsg.replace("site{}".format(i + 1), r)
                try:
                    if urlList[siteList.index(r)] == "":
                        assert("url is empty")
                    replyMsg = replyMsg.replace("http://{}".format(i + 1), urlList[siteList.index(r)])
                except:
                    print("index out of range")

            print("replyMsg:", replyMsg)
            line_bot_api.reply_message(
                event.reply_token,
                TemplateSendMessage.new_from_json_dict(json.loads(replyMsg))
            )
        else:
            replyJsonPath = r"./static/material/Question1/reply.json"
            result_message_array = detect_json_array_to_new_message_array(replyJsonPath)
            line_bot_api.reply_message(
                event.reply_token,
                result_message_array
            )
    elif event.postback.data == "hotsite":
        areaList = ["臺北市", "新北市", "基隆市", "宜蘭縣", "桃園市"]
        placeDic = {"新北市": ["九份老街", "野柳地質公園", "淡水老街", "猴硐車站", "紅毛城", "鶯歌老街", "金瓜寮魚蕨步道", "朱銘美術館", "烏來風景區", "福隆海水浴場"],
                    "臺北市": ["士林官邸", "饒河街觀光夜市", "北投圖書館", "國立故宮博物院", "中正紀念堂", "台北101", "軍艦岩親山步道", "陽明山夜景", "四四南村", "關渡碼頭",
                            "士林觀光夜市"],
                    "基隆市": ["和平島", "基隆廟口", "情人湖濱海大道", "阿根納造船廠", "白米甕砲台", "正濱漁港", "潮境公園", "劉銘傳隧道",
                            "八斗子公園", "大武崙砲台"],
                    "桃園市": ["小烏來天空步道", "石門水庫", "大溪老街", "拉拉山巨木群", "角板山行館", "東眼山森林遊樂區", "巴陵古道生態園區", "中原夜市", "小人國",
                            "馬祖新村眷村文創園區"],
                    "宜蘭縣": ["金車咖啡城堡", "外澳沙灘", "蘭陽博物館", "礁溪溫泉", "望龍埤", "福山植物園", "羅東夜市", "太平山森林遊樂區", "東澳灣‧粉鳥林漁港",
                            "幾米主題廣場"]}
        siteList = util.getSiteList()
        urlList = util.getUrlList()

        with open(replyJsonPath, 'r', encoding="utf-8") as f:
            replyMsg = f.read()

        idx = 1
        for area in areaList:
            for i in range(3):
                r = placeDic[area][i]
                print(r)
                if idx == 1:
                    replyMsg = replyMsg.replace("siteA", r)
                    replyMsg = replyMsg.replace("https://A", urlList[siteList.index(r)])
                elif idx == 2:
                    replyMsg = replyMsg.replace("siteB", r)
                    replyMsg = replyMsg.replace("https://B", urlList[siteList.index(r)])
                else:
                    replyMsg = replyMsg.replace("site{}".format(idx), r)
                    replyMsg = replyMsg.replace("https://{}".format(idx), urlList[siteList.index(r)])
                idx += 1

        print("replyMsg:", replyMsg)
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage.new_from_json_dict(json.loads(replyMsg))
        )

    else:
        result_message_array = detect_json_array_to_new_message_array(replyJsonPath)
        line_bot_api.reply_message(
            event.reply_token,
            result_message_array
        )


if __name__ == "__main__":
    app.run(host='0.0.0.0')
    #app.run(host='0.0.0.0', port=os.environ['PORT'])