import sys
import pymongo
import gridfs
import cv2
sys.path.append('C:\\inetpub\\wwwroot\\jeibatext.py')
sys.path.append('C:\\inetpub\\wwwroot\\model.py')

from pymongo import MongoClient
import requests
import jeibatext
import jieba.analyse
import gensim
from gensim import corpora,models,similarities,models
from gensim.models import word2vec 
import os, codecs
import jieba
import matplotlib.pyplot as plt
import os
import model
import time
import urllib.parse
import numpy as np
import urllib.request
from PIL import Image
from keras.preprocessing import image
from keras.models import model_from_json, load_model
from keras.models import Model, Sequential
from keras.applications.imagenet_utils import preprocess_input
from keras.preprocessing.image import load_img, save_img, img_to_array
from keras.layers import Input, Convolution2D, ZeroPadding2D, MaxPooling2D, Flatten, Dense, Dropout, Activation
from collections import Counter
countnum = []
similarnum = []
countnum1 = []
countkeys = []
countkeys1 = []
dict = {
    "photo_url": None,
    "photo_name":None,
    "text":None,
    "face_check":None,
    "key": None,
    "lecturer_name":None
}

def text_compare(text,text2):
    avg=0
    s = []
    s1=[]
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
        for anword in s1:
            num = new_model.wv.similarity(word,anword)
            if num > 0.7 :
                num = num*10
                count = count +1
            else:
                count = count +1
            total = total + num
            
        
    try:
        avg = total/count
    except:
        avg=0

    #print(avg)
    #print('\n')
    return avg
#沒有相符，比對要求之key值

def InputTheName(x,dict,url,data):   #新增資料庫資料
    # return "fuck"
    for i in x.find():
        if i.photo_url == url :
            file_id = i._id
    x.delete(file_id)

    x.put(data, **dict)
    return "fuck"               


def preprocess_image(image_path):
    img = load_img(image_path, target_size=(224, 224))
    img = img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = preprocess_input(img)
    return img

def findCosineSimilarity(source_representation, test_representation):
    a = np.matmul(np.transpose(source_representation), test_representation)
    b = np.sum(np.multiply(source_representation, source_representation))
    c = np.sum(np.multiply(test_representation, test_representation))
    return (a / (np.sqrt(b) * np.sqrt(c)))

def findEuclideanDistance(source_representation, test_representation):
    euclidean_distance = source_representation - test_representation
    euclidean_distance = np.sum(np.multiply(euclidean_distance, euclidean_distance))
    euclidean_distance = np.sqrt(euclidean_distance)
    return euclidean_distance

def verifyFace(img1, img2):
    img1_representation = model.vgg_face_descriptor.predict(preprocess_image(img1))[0,:]
    img2_representation = model.vgg_face_descriptor.predict(preprocess_image('%s' % (img2)))[0,:]
    #img2_representation = model.vgg_face_descriptor.predict(preprocess_image('C:\\Users\\ASUS\\Desktop\\wordsimilar\\%s' % (download_imageurl(img2))))[0,:]
    
    cosine_similarity = findCosineSimilarity(img1_representation, img2_representation)
    euclidean_distance = findEuclideanDistance(img1_representation, img2_representation)
    
    print("Cosine similarity: ",cosine_similarity)
    print("Euclidean distance: ",euclidean_distance)
    
    if(cosine_similarity > 0.65):
        return True
    else:
        return False
    

    # print("-----------------------------------------")



def face_detect(dist_name):
 
    image = cv2.imread('C:\\inetpub\\wwwroot\\static\\tmp\\%s' % (dist_name))

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    count = 0

    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=3,
        minSize=(50, 50)
    )
    for (x, y, w, h) in faces:
        count = count + 1
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
        image1 = gray[y:y + h, x:x + w]
        image2 = cv2.resize(image1, (256,256), interpolation=cv2.INTER_CUBIC)
        cv2.imwrite('C:\\inetpub\\wwwroot\\used data\\face.jpg', image2)
        return True

    return False
def face_detect2():
    
    image = cv2.imread('C:\\inetpub\\wwwroot\\used data\\face2.jpg')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    count = 0
    
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=3,
        minSize=(50, 50)
    )
    for (x, y, w, h) in faces:
        count = count + 1
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
        image1 = gray[y:y + h, x:x + w]
        image2 = cv2.resize(image1, (256,256), interpolation=cv2.INTER_CUBIC)
        cv2.imwrite('C:\\inetpub\\wwwroot\\used data\\face2.jpg', image2)

# client = pymongo.MongoClient(host='localhost', port=27017)
# db = client.photo
# fs = gridfs.GridFS(db, collection="images")
print("-----------------------------------------")
new_model = gensim.models.Word2Vec.load('C:\\inetpub\\wwwroot\\20180309wiki_model.bin')
