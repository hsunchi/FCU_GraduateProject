#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from flask import Flask, request, abort
import tempfile
import os
import visionapi
import jeibatext
import best
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import cv2
import requests
import pymongo
import gridfs
import os
import gensim
import jieba
import jieba.analyse
from gensim import corpora, models, similarities, models
from gensim.models import word2vec
from keras.models import model_from_json, load_model
from keras.models import Model, Sequential
from urllib.parse import parse_qsl
import sys
import googlesheets
sys.path.append('C:\\inetpub\\wwwroot\\best.py')
sys.path.append('C:\\inetpub\\wwwroot\\jeibatext.py')
sys.path.append('C:\\inetpub\\wwwroot\\googlesheets.py')
app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')


# Channel Access Token
line_bot_api = LineBotApi('CWpm+c/5p51WzCoWeLrxSV5OLLTAUXT1gcWRABY+1TZrNoZ5suu0FGlR8ellldKCV3jrsy5FS8ZrGL0NAa3vNkdcZ5dqb1q88KEzOp/URGHYGS3ZpDaG5enKbcNSUcfVV5/m3bl1bidRYFX7OyipWAdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('c6914cf1374234448bf012aa28fe583b')

@app.route('/', methods=['GET'])
def index():
    return "Hello Flask!"

def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
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


# 處理訊息
@handler.add(PostbackEvent)
def handle_postback(event):
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client.photo
    fs = gridfs.GridFS(db, collection="images")
    backdata = dict(parse_qsl(event.postback.data))
    if backdata.get('action') == 'InputName':
        NewInputTheName(fs, backdata.get('url'))
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="請輸入講師名稱")
        )
    elif backdata.get('action') == 'ChoiceName':
        message = ChoiceName(fs, backdata.get('url'), backdata.get('name'))
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text=message)
            ]
        )
    elif backdata.get('action') == 'InputKey':
        message = NewInputTheKey(fs, backdata.get('url'))
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='請輸入關鍵字')
        )

    elif backdata.get('action') == 'ChoiceKey':
        message = ChoiceKey(fs, backdata.get('url'), backdata.get('key'))
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text=message),
                TextSendMessage(text='請幫這張照片做一些筆記吧！'+'\n'+'一張照片以一則訊息為限唷！')
            ]
        )

@handler.add(MessageEvent, message=(ImageMessage, TextMessage))
def handle_message(event):
    dict = {
        "photo_url": None,
        "photo_name":None,
        "text":None,
        "face_check":None,
        "key": None,
        "lecturer_name":None,
        "user_id":None,
        "note":None,
        "keysheet_id":None,
        "keyname_sheet":None
    }
    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
        client = pymongo.MongoClient(host='localhost', port=27017)
        db = client.photo
        fs = gridfs.GridFS(db, collection="images")
        message_content = line_bot_api.get_message_content(event.message.id)
        with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
            for chunk in message_content.iter_content():
                tf.write(chunk)
            tempfile_path = tf.name

        dist_path = tempfile_path + '.' + ext
        dist_name = os.path.basename(dist_path)   #dist_name 檔案名稱
        os.rename(tempfile_path, dist_path)
        Url = request.host_url + os.path.join('static', 'tmp', dist_name)
        if visionapi.detect_labels_url(Url): #label合不合格
            reply_label = True
        else:
            reply_label = False
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text="請重傳一張圖片必須和講座相關")
                ]
            )

        annotation = visionapi.detect_texts_url(Url) #text
        dict["photo_url"] = Url
        data = requests.get(dict["photo_url"], timeout=10).content
        face_check = best.face_detect(dist_name)
        dict["text"] = annotation
        dict["face_check"] = face_check
        dict["photo_name"] = dist_name
        dict["user_id"] = event.source.user_id

        if not fs.find_one({"photo_url":dict["photo_url"]}):    #沒有重複的話就會存到mongodb裡
            if reply_label is True:
                fs.put(data, **dict)
            else:
                os.remove('C:\\inetpub\\wwwroot\\static\\tmp\\%s' % (dist_name)) #刪掉不符合label但已經存在本機端的照片
        id_list = []  #存放資料庫裡照片的id 這樣才可以
        key_list = []
        face_list = []

        if reply_label is True:
            test = 0 #0代表沒有找到一樣的
            test_face = 0
            message = ""
            for i in fs.find():
                text2 = i.text
                photo_url2 = i.photo_url
                if Url != photo_url2:    #避免同一張照片重複比對
                    if face_check is True and i.face_check is True: #如果都有人臉
                        data = i.read()
                        outf = open('C:\\inetpub\\wwwroot\\used data\\face2.jpg', 'wb') #face2 資料庫裡的  #face是上傳的
                        outf.write(data)
                        best.face_detect2()
                        if best.verifyFace("C:\\inetpub\\wwwroot\\used data\\face2.jpg", "C:\\inetpub\\wwwroot\\used data\\face.jpg"):  #人臉比對成功
                            test = 1
                            test_face = 1
                            id_list.append(i._id) #可能用不到了
                            face_list.append(i.lecturer_name)
                            outf.close()
                        elif annotation != "" and text2 != "":       #人臉比對失敗，所以換比文字（2張都有人臉又有文字）
                            avg = best.text_compare(annotation, text2)
                            if avg > 0.6:
                                test = 1
                                key_list.append(i.key)
                                continue
                    else:
                        if annotation != "" and text2 != "":
                            avg = best.text_compare(annotation, text2)
                            if avg > 0.6:
                                test = 1
                                key_list.append(i.key)
                                continue

            if test_face == 0 and face_check is True and test == 0: #文字不相同 臉也不相同
                dict["lecturer_name"] = "input"
                dict["key"] = "input"
                big = '請輸入講師姓名'
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=big))
                best.InputTheName(fs, dict, Url, data)
            elif test == 0 and face_check is False:
                dict["key"] = "input"
                big = '請輸入關鍵字'
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=big))
                best.InputTheName(fs, dict, Url, data)
            elif test_face == 0 and face_check is True: #有問題 人臉沒有相同 文字相同時不會跳 #人臉不同 文字相同
                dict["lecturer_name"] = "input"
                big = '請輸入講師名字'
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=big))
                best.InputTheName(fs, dict, Url, data)
            elif test_face == 1:
                #測試方法:傳很多張同一個人 但名字都要取不同的試試
                l2 = list(set(face_list))
                if len(l2) == 1:
                    name1 = l2[0]
                    line_bot_api.reply_message(event.reply_token, buttons_template1(name1, Url))
                elif len(l2) == 2:
                    name1 = l2[0]
                    name2 = l2[1]
                    line_bot_api.reply_message(event.reply_token, buttons_template2(name1, name2, Url))
                else:
                    name1 = l2[0]
                    name2 = l2[1]
                    name3 = l2[2]
                    line_bot_api.reply_message(event.reply_token, buttons_template3(name1, name2, name3, Url))
            else:
                # 人臉沒有成功比對 但文字有 印關鍵字出來選
                #這裡跟上面的人名選單一樣都是要選的 也是一個固定選項是以上皆非 其他就是在KEY_LIST裡
                #一樣要不重複 可是跟上面的臉的函數要分開寫
                k2 = list(set(key_list))
                if len(k2) == 1:
                    key1 = k2[0]
                    line_bot_api.reply_message(event.reply_token, buttons_key_template1(key1, Url))
                elif len(k2) == 2:
                    key1 = k2[0]
                    key2 = k2[1]
                    line_bot_api.reply_message(event.reply_token, buttons_key_template2(key1, key2, Url))
                else:
                    key1 = k2[0]
                    key2 = k2[1]
                    key3 = k2[2]
                    line_bot_api.reply_message(event.reply_token, buttons_key_template3(key1, key2, key3, Url))       
        else:
            message = "label illegal"

    elif isinstance(event.message, TextMessage):
        client = pymongo.MongoClient(host='localhost', port=27017)
        db = client.photo
        fs = gridfs.GridFS(db, collection="images")
        # data = requests.get(dict["photo_url"], timeout=10).content
        if event.message.text == "你好":
            message = TextSendMessage(text='你好，請傳一張照片給我')
            line_bot_api.reply_message(event.reply_token, message)
        elif event.message.text == "已選擇講師": #在選單有選擇老師名字時
            test_name = 0
            if  fs.find_one({"key":"choice"}):
                for i in fs.find():
                    if i.key == "choice":
                        lady = i
                        break
                key_list = []
                for i in fs.find():
                    if(i.lecturer_name == lady.lecturer_name and lady.photo_url != i.photo_url):
                        key_list.append(i.key)
                        test_name = 1
                if test_name == 0:
                    secret = "此講師是新講師！"
                else:
                    k2=list(set(key_list))
                    if len(k2) == 1:
                        key1 = k2[0]
                        line_bot_api.reply_message(event.reply_token, buttons_all_key_template1(lady.lecturer_name, key1, lady.photo_url))
                    elif len(k2) == 2:
                        key1 = k2[0]
                        key2 = k2[1]
                        line_bot_api.reply_message(event.reply_token, buttons_all_key_template2(lady.lecturer_name, key1, key2, lady.photo_url))
                    else:
                        key1 = k2[0]
                        key2 = k2[1]
                        key3 = k2[2]
                        line_bot_api.reply_message(event.reply_token, buttons_all_key_template3(lady.lecturer_name, key1, key2, key3, lady.photo_url))
        elif event.message.text == "已選擇關鍵字": #在選單選擇關鍵字時
            return 0
        elif event.message.text == "已選擇": #選以上都不是時
            return 0
        elif event.message.text == "已選擇相關關鍵字": #在選單選擇相關關鍵字時
            return 0
        elif event.message.text == "使用教學":
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='請傳入一張圖片'),
                    TextSendMessage(text='並依照指示繼續操作'),
                    TextSendMessage(text='最後會回傳筆記共享連結')
                ]
            )
        elif event.message.text == "查詢擁有的表單":
            sheet_list = []
            test_sheet = 0
            for i in fs.find():
                if i.user_id == event.source.user_id:
                    sheet_list.append(i.keysheet_id)
                    test_sheet = 1
            if test_sheet == 1:
                st = ""
                s2 = list(set(sheet_list))
                for sheetid in s2:
                    st += "https://docs.google.com/spreadsheets/d/" +sheetid+ "/edit#gid=0" +'\n\n'
                line_bot_api.reply_message(
                    event.reply_token, [
                        TextSendMessage(text='這是你所有的表單連結'),
                        TextSendMessage(text=st)
                    ]
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token, [
                        TextSendMessage(text='目前尚未擁有任何表單'),
                    ]
                )
        elif event.message.text == "查詢關鍵字":
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='請輸入要查詢的關鍵字，第一個字請為@'),
                ]
            )
        elif event.message.text == "介紹":
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='嗨！歡迎使用「伸手拍共享筆記」'),
                    TextSendMessage(text='你只需要傳給我一張講座的照片，就可以幫你配對相關知識的討論連結'),
                ]
            )

        elif event.message.text[0] == '@':
            #查詢關鍵字寫好了
            search_key = []
            test_key = 0
            for i in fs.find():
                if i.key == event.message.text[1:]:
                    search_key.append(i.keysheet_id)
                    test_key = 1
            if test_key == 1:
                sk2 = list(set(search_key))
                sk = ""
                for keysheetid in sk2:
                    sk += "https://docs.google.com/spreadsheets/d/" +keysheetid+ "/edit#gid=0" +'\n'
                line_bot_api.reply_message(
                    event.reply_token, [
                        TextSendMessage(text='這是'+ event.message.text[1:] +'的所有表單連結'),
                        TextSendMessage(text=sk)
                    ]
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token, [
                        TextSendMessage(text='此關鍵字目前尚未擁有任何表單'),
                    ]
                )
        else:
            test_id = 0
            if fs.find_one({"lecturer_name":"input"}):
                for i in fs.find():
                    if i.lecturer_name == "input" and i.user_id == event.source.user_id:
                        lady = i
                        test_id = 1
                        break
                if test_id == 1:
                    dict["text"] = lady.text
                    dict["face_check"] = lady.face_check
                    dict["photo_name"] = lady.photo_name
                    dict["photo_url"] = lady.photo_url
                    dict["key"] = lady.key
                    dict["lecturer_name"] = event.message.text
                    dict["user_id"] = lady.user_id
                    dict["note"] = lady.note
                    dict["keysheet_id"] = lady.keysheet_id
                    dict["keyname_sheet"] = lady.keyname_sheet
                    annotation = lady.text
                    Url = lady.photo_url
                    nkjnkn = InputTheName(fs, dict, lady.photo_url)
                    key_list = []
                    test_name = 0
                    for i in fs.find():
                        if(i.lecturer_name == event.message.text and lady.photo_url != i.photo_url):
                            key_list.append(i.key)
                            test_name = 1
                    #尋找他輸入的講師名字有沒有符合的，如果有 找出那個老師所有的關鍵字名稱
                    if test_name == 0:
                        kkey_list = []
                        secret = "此講師是新講師！"
                        if lady.key == "input": #提示文字
                            nnext = "請輸入關鍵詞"
                        else:
                            for i in fs.find():
                                text2 = i.text
                                photo_url2 = i.photo_url
                                if Url != photo_url2: 
                                    if annotation != "" and text2 != "":
                                        avg = best.text_compare(annotation, text2)
                                        if avg > 0.6:
                                            test = 1
                                            kkey_list.append(i.key)
                                            continue
                            k2 = list(set(kkey_list))
                            if len(k2) == 1:
                                key1 = k2[0]
                                line_bot_api.reply_message(event.reply_token, buttons_key_template1(key1, lady.photo_url))
                            elif len(k2) == 2:
                                key1 = k2[0]
                                key2 = k2[1]
                                line_bot_api.reply_message(event.reply_token, buttons_key_template2(key1, key2, lady.photo_url))
                            else:
                                key1 = k2[0]
                                key2 = k2[1]
                                key3 = k2[2]
                                line_bot_api.reply_message(event.reply_token, buttons_key_template3(key1, key2, key3, lady.photo_url))
                    else:
                        k2 = list(set(key_list))
                        if len(k2) == 1:
                            key1 = k2[0]
                            line_bot_api.reply_message(event.reply_token, buttons_all_key_template1(event.message.text, key1, lady.photo_url))
                        elif len(k2) == 2:
                            key1 = k2[0]
                            key2 = k2[1]
                            line_bot_api.reply_message(event.reply_token, buttons_all_key_template2(event.message.text, key1, key2, lady.photo_url))
                        else:
                            key1 = k2[0]
                            key2 = k2[1]
                            key3 = k2[2]
                            line_bot_api.reply_message(event.reply_token, buttons_all_key_template3(event.message.text, key1, key2, key3, lady.photo_url))
                    line_bot_api.reply_message(
                        event.reply_token, [
                            TextSendMessage(text=secret),
                            TextSendMessage(text=nnext)
                        ])
                else:
                    line_bot_api.reply_message(
                        event.reply_token, [
                            TextSendMessage(text='你好'),
                            TextSendMessage(text='請傳一張圖片給我')
                        ]
                    )
                return 0
            elif fs.find_one({"key":"input"}):
                test_id = 0
                for i in fs.find():
                    if i.key == "input"and i.user_id == event.source.user_id:
                        lady = i
                        test_id = 1
                        break
                if test_id == 1:
                    dict["text"] = lady.text
                    dict["face_check"] = lady.face_check
                    dict["photo_name"] = lady.photo_name
                    dict["photo_url"] = lady.photo_url
                    dict["key"] = event.message.text
                    dict["lecturer_name"] = lady.lecturer_name
                    dict["user_id"] = lady.user_id
                    dict["note"] = "input"
                    dict["keysheet_id"] = lady.keysheet_id
                    dict["keyname_sheet"] = lady.keyname_sheet
                    secret = InputTheName(fs, dict, lady.photo_url)
                    secret = "成功輸入關鍵字"
                    line_bot_api.reply_message(
                        event.reply_token, [
                            TextSendMessage(text=secret),
                            TextSendMessage(text='請幫這張照片做一些筆記吧！'+'\n'+'一張照片以一則訊息為限唷！')
                        ]
                    )
                else:
                    line_bot_api.reply_message(
                        event.reply_token, [
                            TextSendMessage(text='你好'),
                            TextSendMessage(text='請傳一張圖片給我')
                        ]
                    )
                return 0
            elif fs.find_one({"note":"input"}):
                test_id = 0
                for i in fs.find():
                    if i.note == "input"and i.user_id == event.source.user_id:
                        lady = i
                        test_id = 1
                        break
                if test_id == 1:
                    now_note = ""
                    keytest = 0
                    keynametest = 0
                    keysheet_id = ""
                    keyname_sheet = ""
                    dict["text"] = lady.text
                    dict["face_check"] = lady.face_check
                    dict["photo_name"] = lady.photo_name
                    dict["photo_url"] = lady.photo_url
                    dict["key"] = lady.key
                    dict["lecturer_name"] = lady.lecturer_name
                    dict["user_id"] = lady.user_id
                    dict["note"] = event.message.text
                    now_note = event.message.text
                    for i in fs.find():
                        if lady.photo_url != i.photo_url:
                            if i.key == lady.key:
                                keysheet_id = i.keysheet_id
                                keytest = 1
                                if lady.face_check is True and lady.lecturer_name == i.lecturer_name:
                                    keyname_sheet = i.keyname_sheet
                                    keynametest = 1
                                    break

                    if keytest == 0:
                        keysheet_id = googlesheets.createSheet(lady.key, googlesheets.googlesh())
                    if keynametest == 0 and lady.face_check is True:
                        keyname_sheet = googlesheets.createSheet(lady.lecturer_name+"-"+lady.key,googlesheets.googlesh())



                    if lady.text == "" and lady.face_check is True:
                        googlesheets.insertImage(keysheet_id, lady.photo_url, "\n\n\n\n\n此圖無文字\n\n\n\n\n", lady.lecturer_name, now_note, googlesheets.googlesh())
                        googlesheets.insertImage(keyname_sheet, lady.photo_url, "\n\n\n\n\n此圖無文字\n\n\n\n\n", lady.lecturer_name, now_note, googlesheets.googlesh())
                    elif lady.face_check is True:
                        googlesheets.insertImage(keysheet_id, lady.photo_url, lady.text, lady.lecturer_name, now_note, googlesheets.googlesh())
                        googlesheets.insertImage(keyname_sheet, lady.photo_url, lady.text, lady.lecturer_name, now_note, googlesheets.googlesh())
                    elif lady.text != "" and lady.face_check is False:
                        googlesheets.insertImage(keysheet_id, lady.photo_url, lady.text, "", now_note, googlesheets.googlesh())

                    dict["keysheet_id"] = keysheet_id
                    dict["keyname_sheet"] = keyname_sheet
                    secret = InputTheName(fs, dict, lady.photo_url)
                    secret = "成功輸入筆記"
                    if lady.face_check is True:
                        line_bot_api.reply_message(
                            event.reply_token, [
                                TextSendMessage(text=secret),
                                TextSendMessage(text="https://docs.google.com/spreadsheets/d/" +keysheet_id+ "/edit#gid=0"),
                                TextSendMessage(text="https://docs.google.com/spreadsheets/d/" +keyname_sheet+ "/edit#gid=0")
                            ]
                        )
                    else:
                        line_bot_api.reply_message(
                            event.reply_token, [
                                TextSendMessage(text=secret),
                                TextSendMessage(text="https://docs.google.com/spreadsheets/d/" +keysheet_id+ "/edit#gid=0")
                            ]
                        )
                else:
                    line_bot_api.reply_message(
                        event.reply_token, [
                            TextSendMessage(text='你好'),
                            TextSendMessage(text='請傳一張圖片給我')
                        ]
                    )
                return 0
            else:
                line_bot_api.reply_message(
                    event.reply_token, [
                        TextSendMessage(text='你好'),
                        TextSendMessage(text='請傳一張圖片給我')
                    ]
                )
                return 0

def buttons_template1(name1, url):
    buttons_template = TemplateSendMessage(
        alt_text='請選擇講師',
        template=ButtonsTemplate(
            title='下列哪個才是正確的講師？',
            text='請選擇此講座的講師',
            actions=[
                PostbackTemplateAction(
                    label=name1,
                    text='已選擇講師',
                    data='name='+ name1 +'&action=ChoiceName&url='+url
                ),
                PostbackTemplateAction(
                    label='以上都不是',
                    text='已選擇',
                    data='name=input&action=InputName&url='+url
                )
            ]
        )
    )
    return buttons_template
def buttons_template2(name1, name2, url):
    buttons_template = TemplateSendMessage(
        alt_text='請選擇講師',
        template=ButtonsTemplate(
            title='下列哪個才是正確的講師？',
            text='請選擇此講座的講師',
            actions=[
                PostbackTemplateAction(
                    label=name1,
                    text='已選擇講師',
                    data= 'name='+ name1 +'&action=ChoiceName&url='+url
                ),
                PostbackTemplateAction(
                    label=name2,
                    text='已選擇講師',
                    data='name='+ name2 +'&action=ChoiceName&url='+url
                ),
                PostbackTemplateAction(
                    label='以上都不是',
                    text='已選擇',
                    data='name=input&action=InputName&url='+url
                )
            ]
        )
    )
    return buttons_template
def buttons_template3(name1, name2, name3, url):
    buttons_template = TemplateSendMessage(
        alt_text='請選擇講師',
        template=ButtonsTemplate(
            title='下列哪個才是正確的講師？',
            text='請選擇此講座的講師',
            actions=[
                PostbackTemplateAction(
                    label=name1,
                    text='已選擇講師',
                    data='name='+ name1 +'&action=ChoiceName&url='+url
                ),
                PostbackTemplateAction(
                    label=name2,
                    text='已選擇講師',
                    data='name='+ name2 +'&action=ChoiceName&url='+url
                ),
                PostbackTemplateAction(
                    label=name3,
                    text='已選擇講師',
                    data='name='+ name3 +'&action=ChoiceName&url='+url
                ),
                PostbackTemplateAction(
                    label='以上都不是',
                    text='已選擇',
                    data='name=input&action=InputNamet&url='+url
                )
            ]
        )
    )
    return buttons_template
def buttons_key_template1(key1, url):
    buttons_template = TemplateSendMessage(
        alt_text='請選擇關鍵字',
        template=ButtonsTemplate(
            title='下列哪個才是正確的關鍵字？',
            text='請選擇此投影片的關鍵字',
            actions=[
                PostbackTemplateAction(
                    label=key1,
                    text='已選擇關鍵字',
                    data='key='+ key1 +'&action=ChoiceKey&url='+url
                ),
                PostbackTemplateAction(
                    label='以上都不是',
                    text='已選擇',
                    data='key=input&action=InputKey&url='+url
                )
            ]
        )
    )
    return buttons_template
def buttons_key_template2(key1, key2, url):
    buttons_template = TemplateSendMessage(
        alt_text='請選擇關鍵字',
        template=ButtonsTemplate(
            title='下列哪個才是正確的關鍵字？',
            text='請選擇此投影片的關鍵字',
            actions=[
                PostbackTemplateAction(
                    label=key1,
                    text='已選擇關鍵字',
                    data='key='+ key1 +'&action=ChoiceKey&url='+url
                ),
                PostbackTemplateAction(
                    label=key2,
                    text='已選擇關鍵字',
                    data='key='+ key2 +'&action=ChoiceKey&url='+url
                ),
                PostbackTemplateAction(
                    label='以上都不是',
                    text='已選擇',
                    data='key=input&action=InputKey&url='+url
                )
            ]
        )
    )
    return buttons_template
def buttons_key_template3(key1, key2, key3, url):
    buttons_template = TemplateSendMessage(
        alt_text='請選擇關鍵字',
        template=ButtonsTemplate(
            title='下列哪個才是正確的關鍵字？',
            text='請選擇此投影片的關鍵字',
            actions=[
                PostbackTemplateAction(
                    label=key1,
                    text='已選擇關鍵字',
                    data='key='+ key1 +'&action=ChoiceKey&url='+url
                ),
                PostbackTemplateAction(
                    label=key2,
                    text='已選擇關鍵字',
                    data='key='+ key2 +'&action=ChoiceKey&url='+url
                ),
                PostbackTemplateAction(
                    label=key3,
                    text='已選擇關鍵字',
                    data='key='+ key3 +'&action=ChoiceKey&url='+url
                ),
                PostbackTemplateAction(
                    label='以上都不是',
                    text='已選擇',
                    data='key=input&action=InputKey&url='+url
                )
            ]
        )
    )
    return buttons_template

def buttons_all_key_template1(name, key1, url):
    buttons_template = TemplateSendMessage(
        alt_text='所有關鍵字',
        template=ButtonsTemplate(
            title='下列為' + name + '講師所有講座的關鍵字',
            text='請選擇與此張相片相關的關鍵字',
            actions=[
                PostbackTemplateAction(
                    label=key1,
                    text='已選擇相關關鍵字',
                    data='key='+ key1 +'&action=ChoiceKey&url='+url
                ),
                PostbackTemplateAction(
                    label='以上都不是',
                    text='已選擇',
                    data='key=input&action=InputKey&url='+url
                )
            ]
        )
    )
    return buttons_template
def buttons_all_key_template2(name, key1, key2, url):
    buttons_template = TemplateSendMessage(
        alt_text='所有關鍵字',
        template=ButtonsTemplate(
            title='下列為' + name + '講師所有講座的關鍵字',
            text='請選擇與此張相片相關的關鍵字',
            actions=[
                PostbackTemplateAction(
                    label=key1,
                    text='已選擇相關關鍵字',
                    data='key='+ key1 +'&action=ChoiceKey&url='+url
                ),
                PostbackTemplateAction(
                    label=key2,
                    text='已選擇相關關鍵字',
                    data='key='+ key2 +'&action=ChoiceKey&url='+url
                ),
                PostbackTemplateAction(
                    label='以上都不是',
                    text='已選擇相關關鍵字',
                    data='key=input&action=InputKey&url='+url
                )
            ]
        )
    )
    return buttons_template
def buttons_all_key_template3(name, key1, key2, key3, url):
    buttons_template = TemplateSendMessage(
        alt_text='所有關鍵字',
        template=ButtonsTemplate(
            title='下列為' + name + '講師所有講座的關鍵字',
            text='請選擇與此張相片相關的關鍵字',
            actions=[
                PostbackTemplateAction(
                    label=key1,
                    text='已選擇相關關鍵字',
                    data='key='+ key1 +'&action=ChoiceKey&url='+url
                ),
                PostbackTemplateAction(
                    label=key2,
                    text='已選擇相關關鍵字',
                    data='key='+ key2 +'&action=ChoiceKey&url='+url
                ),
                PostbackTemplateAction(
                    label=key3,
                    text='已選擇相關關鍵字',
                    data='key='+ key3 +'&action=ChoiceKey&url='+url
                ),
                PostbackTemplateAction(
                    label='以上都不是',
                    text='已選擇',
                    data='key=input&action=InputKey&url='+url
                )
            ]
        )
    )
    return buttons_template
def InputTheName(x, dict, url):   #新增資料庫資料
    for i in x.find():
        if i.photo_url == url:
            file_id = i._id
            data = i.read()
    x.delete(file_id)
    x.put(data, **dict)
    return "所有關鍵詞:"   #這個回傳的訊息要修改
def NewInputTheName(x, url):   #新增沒有選擇到後的資料庫資料
    dict = {
        "photo_url": None,
        "photo_name":None,
        "text":None,
        "face_check":None,
        "key": None,
        "lecturer_name":None,
        "user_id":None,
        "note":None,
        "keysheet_id":None,
        "keyname_sheet":None
    }
    for i in x.find():
        if i.photo_url == url:
            lady = i
            break
    dict["text"] = lady.text
    dict["face_check"] = lady.face_check
    dict["photo_name"] = lady.photo_name
    dict["photo_url"] = url
    dict["key"] = "input"
    dict["lecturer_name"] = "input"
    dict["user_id"] = lady.user_id
    dict["note"] = lady.note
    dict["keysheet_id"] = lady.keysheet_id
    dict["keyname_sheet"] = lady.keyname_sheet
    for i in x.find():
        if i.photo_url == url:
            file_id = i._id
            data = i.read()
    x.delete(file_id)
    x.put(data, **dict)
    return "已更新講師名字"

def ChoiceName(x, url, name):   #新增選擇到後的資料庫資料
    dict = {
        "photo_url": None,
        "photo_name":None,
        "text":None,
        "face_check":None,
        "key": None,
        "lecturer_name":None,
        "user_id":None,
        "note":None,
        "keysheet_id":None,
        "keyname_sheet":None
    }
    for i in x.find():
        if i.photo_url == url:
            lady = i
            break
    dict["text"] = lady.text
    dict["face_check"] = lady.face_check
    dict["photo_name"] = lady.photo_name
    dict["photo_url"] = url
    dict["key"] = 'choice'
    dict["lecturer_name"] = name
    dict["user_id"] = lady.user_id
    dict["note"] = lady.note
    dict["keysheet_id"] = lady.keysheet_id
    dict["keyname_sheet"] = lady.keyname_sheet
    for i in x.find():
        if i.photo_url == url:
            file_id = i._id
            data = i.read()
    x.delete(file_id)
    x.put(data, **dict)
    return "已更新講師名字"
def NewInputTheKey(x, url): #新增沒有選擇到後的資料庫資料
    dict = {
        "photo_url": None,
        "photo_name":None,
        "text":None,
        "face_check":None,
        "key": None,
        "lecturer_name":None,
        "user_id":None,
        "note":None,
        "keysheet_id":None,
        "keyname_sheet":None
    }
    for i in x.find():
        if i.photo_url == url:
            lady = i
            break
    dict["text"] = lady.text
    dict["face_check"] = lady.face_check
    dict["photo_name"] = lady.photo_name
    dict["photo_url"] = url
    dict["key"] = "input"
    dict["lecturer_name"] = lady.lecturer_name
    dict["user_id"] = lady.user_id
    dict["note"] = "input"
    dict["keysheet_id"] = lady.keysheet_id
    dict["keyname_sheet"] = lady.keyname_sheet
    for i in x.find():
        if i.photo_url == url:
            file_id = i._id
            data = i.read()
    x.delete(file_id)
    x.put(data, **dict)
    return "已更新關鍵字" 
def ChoiceKey(x, url, key):   #新增選擇到後的資料庫資料
    dict = {
        "photo_url": None,
        "photo_name":None,
        "text":None,
        "face_check":None,
        "key": None,
        "lecturer_name":None,
        "user_id":None,
        "note":None,
        "keysheet_id":None,
        "keyname_sheet":None
    }
    for i in x.find():
        if i.photo_url == url:
            lady = i
            break
    dict["text"] = lady.text
    dict["face_check"] = lady.face_check
    dict["photo_name"] = lady.photo_name
    dict["photo_url"] = url
    dict["key"] = key
    dict["lecturer_name"] = lady.lecturer_name
    dict["user_id"] = lady.user_id
    dict["note"] = "input"
    dict["keysheet_id"] = lady.keysheet_id
    dict["keyname_sheet"] = lady.keyname_sheet
    for i in x.find():
        if i.photo_url == url:
            file_id = i._id
            data = i.read()
    x.delete(file_id)
    x.put(data, **dict)
    return "已更新關鍵字"


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    make_static_tmp_dir()
    app.run(host='0.0.0.0', port=port)
