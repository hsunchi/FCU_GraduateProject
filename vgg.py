import requests
import numpy as np
import urllib.request
from PIL import Image
import matplotlib.pyplot as plt
from keras.preprocessing import image
from keras.models import model_from_json, load_model
from keras.models import Model, Sequential
from keras.applications.imagenet_utils import preprocess_input
from keras.preprocessing.image import load_img, save_img, img_to_array
from keras.layers import Input, Convolution2D, ZeroPadding2D, MaxPooling2D, Flatten, Dense, Dropout, Activation

def download_image(url):
    filename = url.split('/')[-1]   # 以斜線分割保留最後一段
    r = requests.get(url, allow_redirects=True)     # 向http請求，取得url裡的資料
    open(filename, 'wb').write(r.content)    #將url的資料寫入
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
    img1_representation = vgg_face_descriptor.predict(preprocess_image('C:/Users/easyl/Desktop/Project/%s' % (download_image(img1))))[0,:]
    img2_representation = vgg_face_descriptor.predict(preprocess_image('C:/Users/easyl/Desktop/Project/%s' % (download_image(img2))))[0,:]
    
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
    plt.imshow(image.load_img('C:/Users/easyl/Desktop/Project/%s' % (download_image(img1))))
    plt.xticks([]); plt.yticks([])
    f.add_subplot(1,2, 2)
    plt.imshow(image.load_img('C:/Users/easyl/Desktop/Project/%s' % (download_image(img2))))
    plt.xticks([]); plt.yticks([])
    plt.show(block=True)
    print("-----------------------------------------")


model = load_model('model.h5')
model.load_weights('vgg_face_weights.h5')
vgg_face_descriptor = Model(inputs=model.layers[0].input, outputs=model.layers[-2].output)

verifyFace("https://cdn1.imggmi.com/uploads/2019/9/26/410734a643b04fb4d0591cfbf61f4ae0-full.jpg", "https://cdn1.imggmi.com/uploads/2019/9/26/7a3aabd424161caa901c92032ac18cf6-full.jpg")