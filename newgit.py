import collections
import sys
import pymongo
import gridfs
sys.path.append('C:\\Users\\ASUS\\Desktop\\wordsimilar\\readpt.py')
sys.path.append('C:\\Users\\ASUS\\Desktop\\wordsimilar\\jeibatext.py')
import readpt
from pymongo import MongoClient
import requests
import jeibatext
import jieba.analyse
import gensim
from gensim import corpora,models,similarities,models
from gensim.models import word2vec
from gensim.models import Doc2Vec 
import os, codecs
import jieba
import matplotlib.pyplot as plt

from collections import Counter
countnum = []
similarnum = []
countnum1 = []
countkeys = []
countkeys1 = []
dict = {
    "photo_url": None,
    "text":None
}

def compare(text,text2):
    avg=0
    s = []
    s1=[]
    s2=[]
    total = 0
    count = 0
 
    countkeys = jeibatext.get_word(text)
    countkeys1 = jeibatext.get_word(text2)

    for word in countkeys:
        if word in new_model.wv.vocab:
            s.append(word)
    for word1 in countkeys1:
        if word1 in new_model.wv.vocab:
            s1.append(word1)
    print('\n')


    for word in s :
        if word in new_model.wv.vocab:
            for anword in s1:
                num = new_model.wv.similarity(word,anword)
                if num > 0.7 :
                    num = num*10
                    count = count +1
                else:
                    num = num
                    count = count +1
                total = total + num
            
        else:
            print(word+"not exist")
            continue
    try:
        avg = total/count
    except:
        avg=0

    print(avg)
    print('\n')
def download_imagedb(url,x):
    
    
    dict["photo_url"]=url

    data = requests.get(dict["photo_url"], timeout=10).content
    try:
        text = read_db(url)
    except:
        text = ""
    dict["photo_url"]=url
    dict["text"]=text
    if not fs.find_one({"photo_url":dict["photo_url"]}):    #沒有重複的話就會存到mongodb裡
        fs.put(data, **dict)


    for i in x.find():
        try:
            text2 = i.text
            if text!= text2:    #避免同一張照片重複比對
                compare(text,text2)
        except:
            avg = 0
            print(avg)


def read_db(x):#user傳來的圖片
    import io
    import os
    from google.cloud import vision
    from google.cloud.vision import types
    client = vision.ImageAnnotatorClient.from_service_account_json("C:\\Users\\ASUS\\Desktop\\test data\\test-vision-api-51702e2fc41e.json")   #圖片存於本地端

    image = vision.types.Image()
	#圖片使用url
    image.source.image_uri =x
    
    response = client.text_detection(image=image)
    texts = response.text_annotations
    
    text = texts[0].description  
	#text 是圖片裡面的文字內容
    return text


client = pymongo.MongoClient(host='localhost', port=27017)
db = client.photo
fs = gridfs.GridFS(db, collection="images")
print("-----------------------------------------")
new_model = gensim.models.Word2Vec.load('C:\\Users\\ASUS\\Downloads\\20180309wiki_model\\20180309wiki_model.bin')
download_imagedb('https://cdn1.imggmi.com/uploads/2019/10/31/52905964d6e86e81693fd3ed43134102-full.jpg',fs)
   


     
