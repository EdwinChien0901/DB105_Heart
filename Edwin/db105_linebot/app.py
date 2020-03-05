from confluent_kafka import Producer
import redis
import sys, datetime
import os
import util

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

print("token:", secretFileContentJson.get("channel_access_token"))
print("key:", secretFileContentJson.get("secret_key"))
print("server:", secretFileContentJson.get("server_url"))
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
        print("jsonStr:", jsonStr)
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
    # 讀取並轉換
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
@handler.add(MessageEvent,message=TextMessage)
def process_text_message(event):
    # 讀取本地檔案，並轉譯成消息
    result_message_array =[]
    if event.message.text in os.listdir(r'./static/material'):
        replyJsonPath = r"./static/material/{0}/reply.json".format(event.message.text)
        result_message_array = detect_json_array_to_new_message_array(replyJsonPath)

        # 發送
        line_bot_api.reply_message(
            event.reply_token,
            result_message_array
        )
    elif event.message.text in util.getSiteList():
        prod = util.getProducer()
        # 步驟3. 指定想要發佈訊息的topic名稱
        topicName = 'test1'
        util.sendKafkaMsg(topicName, event.message.text, event.reply_token)

        re = util.getRedis()
        tnow = datetime.datetime.now()

        value = re.get(event.reply_token)
        try:
            while value == None:
                value = re.get(event.reply_token)

                diff = (datetime.datetime.now() - tnow).total_seconds()
                print("seconds:", diff)
                assert diff < 30, "over time error"
        except AssertionError as error:
            print(error)
            return

        print(value)

        siteList = value.split(",")
        print("siteList:", siteList)
        replyMsg = util.getTemplateJson();
        for i, site in enumerate(siteList):
            replyMsg = replyMsg.replace("site{}".format(i + 1), site)

        print("replyMsg:", replyMsg)
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage.new_from_json_dict(json.loads(replyMsg))
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage.new_from_json_dict(json.loads(util.getUseMenuJson()))
        )


from urllib.parse import parse_qs

@handler.add(PostbackEvent)
def process_postback_event(event):
    result_message_array = []
    replyJsonPath = r"./static/material/{0}/reply.json".format(event.postback.data)
    print("replyJsonPath:", replyJsonPath)

    if event.postback.data == "question":
        result_message_array = getQuestionnaireReply(event.reply_token, replyJsonPath)

        line_bot_api.reply_message(
            event.reply_token,
            result_message_array
        )

        re = util.getRedis()
        tnow = datetime.datetime.now()

        value = re.get(event.reply_token)
        try:
            while value == None:
                value = re.get(event.reply_token)

                diff = (datetime.datetime.now() - tnow).total_seconds()
                print("seconds:", diff)
                assert diff < 30, "over time error"
        except AssertionError as error:
            print(error)
            return

        print(value)

        siteList = value.split(",")
        print("siteList:", siteList)
        replyMsg = util.getTemplateJson()
        for i, site in enumerate(siteList):
            replyMsg = replyMsg.replace("site{}".format(i + 1), site)

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