import os
import time
import gridfs
import pymongo
import requests
import urllib.parse
import numpy as np
import urllib.request
import matplotlib.pyplot as plt
from PIL import Image
from pymongo import MongoClient
from keras.preprocessing import image
from keras.models import model_from_json, load_model
from keras.models import Model, Sequential
from keras.applications.imagenet_utils import preprocess_input
from keras.preprocessing.image import load_img, save_img, img_to_array
from keras.layers import Input, Convolution2D, ZeroPadding2D, MaxPooling2D, Flatten, Dense, Dropout, Activation

dict ={
    "photo_url" : None
}

def put_image2db(url):
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client.photo
    fs = gridfs.GridFS(db, collection="images") 
    data = requests.get(url, timeout=10).content
    fs.put(data)

def comparedb(url):
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client.photo
    fs = gridfs.GridFS(db, collection="images")

    for grid_out in fs.find():
        data = grid_out.read()
        outf = open('1.jpg','wb')
        outf.write(data)
        verifyFace(url,"1.jpg")
        outf.close()

    dict['photo_url'] = url
    data = requests.get(dict["photo_url"], timeout=10).content
    # print(dict['photo_url'])

    if not fs.find_one({"photo_url":dict["photo_url"]}):
        fs.put(data, **dict)

def download_imageurl(url):
    filename = url.split('/')[-1]
    r = requests.get(url, allow_redirects=True)     
    open(filename, 'wb').write(r.content)    
    return filename

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
    img1_representation = vgg_face_descriptor.predict(preprocess_image('C:/Users/easyl/Desktop/Project/%s' % (download_imageurl(img1))))[0,:]
    img2_representation = vgg_face_descriptor.predict(preprocess_image('C:/Users/easyl/Desktop/Project/%s' % (img2)))[0,:]
    
    cosine_similarity = findCosineSimilarity(img1_representation, img2_representation)
    euclidean_distance = findEuclideanDistance(img1_representation, img2_representation)
    
    print("Cosine similarity: ",cosine_similarity)
    print("Euclidean distance: ",euclidean_distance)
    
    if(cosine_similarity > 0.8):
        print("they are same person")
    else:
        print("they are not same person")
    
    f = plt.figure()
    f.add_subplot(1,2, 1)
    plt.imshow(image.load_img('C:/Users/easyl/Desktop/Project/%s' % (download_imageurl(img1))))
    plt.xticks([]); plt.yticks([])
    f.add_subplot(1,2, 2)
    plt.imshow(image.load_img('C:/Users/easyl/Desktop/Project/%s' % (img2)))
    plt.xticks([]); plt.yticks([])
    plt.show(block=True)
    print("-----------------------------------------")


model = load_model('model.h5')
model.load_weights('vgg_face_weights.h5')
vgg_face_descriptor = Model(inputs=model.layers[0].input, outputs=model.layers[-2].output)

comparedb("https://cdn1.imggmi.com/uploads/2019/10/23/3633b9c0a6514d23146c35242b5fbf42-full.jpg")
# verifyFace("https://cdn1.imggmi.com/uploads/2019/10/14/4e7c952adec6c35c6f440418a65de7ed-full.jpg", "https://cdn1.imggmi.com/uploads/2019/10/14/cc36fe171be2e62c3ce730a6ac9e17c4-full.jpg")

# 
# https://cdn1.imggmi.com/uploads/2019/10/22/63e1d380caaa5eea714a7b1119fe90b6-full.jpg