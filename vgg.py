import requests
import numpy as np
import urllib.request
from PIL import Image
import matplotlib.pyplot as plt
from keras.preprocessing import image
from keras.models import model_from_json
from keras.models import Model, Sequential
from keras.applications.imagenet_utils import preprocess_input
from keras.preprocessing.image import load_img, save_img, img_to_array
from keras.layers import Input, Convolution2D, ZeroPadding2D, MaxPooling2D, Flatten, Dense, Dropout, Activation

model = Sequential()
model.add(ZeroPadding2D((1,1),input_shape=(224,224, 3)))    # 周圍各一單位都加0，使卷積後的圖維持相同大小，輸入3張224*224，Output Shape = (226,226,3)
model.add(Convolution2D(64, (3, 3), activation='relu'))     # 因Filter為64，所以產生64張圖，Output Shape = (224,224,64)。Param = (3*3*3+1)*64 = 1792
model.add(ZeroPadding2D((1,1)))                             # Output Shape = (226,226,64)
model.add(Convolution2D(64, (3, 3), activation='relu'))     # Output Shape = (224,224,64)，Param = (3*3*64+1)*64 = 36928
model.add(MaxPooling2D((2,2), strides=(2,2)))               # Output Shape = (112,112,64)

model.add(ZeroPadding2D((1,1)))                             # Output Shape = (114,114,64)
model.add(Convolution2D(128, (3, 3), activation='relu'))    # Output Shape = (112,112,128)，Param = (3*3*64+1)*128 = 73856
model.add(ZeroPadding2D((1,1)))                             # Output Shape = (114,114,128)
model.add(Convolution2D(128, (3, 3), activation='relu'))    # Output Shape = (112,112,128)，Param = (3*3*128+1)*128 = 147584
model.add(MaxPooling2D((2,2), strides=(2,2)))               # Output Shape = (56,56,128)

model.add(ZeroPadding2D((1,1)))                             # Output Shape = (58,58,128)
model.add(Convolution2D(256, (3, 3), activation='relu'))    # Output Shape = (56,56,256)，Param = (3*3*128+1)*256 = 295168
model.add(ZeroPadding2D((1,1)))                             # Output Shape = (58,58,256)
model.add(Convolution2D(256, (3, 3), activation='relu'))    # Output Shape = (56,56,256)，Param = (3*3*256+1)*256 = 590080
model.add(ZeroPadding2D((1,1)))                             # Output Shape = (58,58,256)
model.add(Convolution2D(256, (3, 3), activation='relu'))    # Output Shape = (56,56,256)，Param = (3*3*256+1)*256 = 590080
model.add(MaxPooling2D((2,2), strides=(2,2)))               # Output Shape = (28,28,256)

model.add(ZeroPadding2D((1,1)))                             # Output Shape = (30,30,256)
model.add(Convolution2D(512, (3, 3), activation='relu'))    # Output Shape = (28,28,512)，Param = (3*3*256+1)*512 = 1180160
model.add(ZeroPadding2D((1,1)))                             # Output Shape = (30,30,512)
model.add(Convolution2D(512, (3, 3), activation='relu'))    # Output Shape = (28,28,512)，Param = (3*3*512+1)*512 = 2359808
model.add(ZeroPadding2D((1,1)))                             # Output Shape = (30,30,512)
model.add(Convolution2D(512, (3, 3), activation='relu'))    # Output Shape = (28,28,512)，Param = (3*3*512+1)*512 = 2359808
model.add(MaxPooling2D((2,2), strides=(2,2)))               # Output Shape = (14,14,512)

model.add(ZeroPadding2D((1,1)))                             # Output Shape = (16,16,512)
model.add(Convolution2D(512, (3, 3), activation='relu'))    # Output Shape = (14,14,512)，Param = (3*3*512+1)*512 = 2359808
model.add(ZeroPadding2D((1,1)))                             # Output Shape = (16,16,512)
model.add(Convolution2D(512, (3, 3), activation='relu'))    # Output Shape = (14,14,512)，Param = (3*3*512+1)*512 = 2359808
model.add(ZeroPadding2D((1,1)))                             # Output Shape = (16,16,512)
model.add(Convolution2D(512, (3, 3), activation='relu'))    # Output Shape = (14,14,512)，Param = (3*3*512+1)*512 = 2359808
model.add(MaxPooling2D((2,2), strides=(2,2)))               # Output Shape = (7,7,512)

model.add(Convolution2D(4096, (7, 7), activation='relu'))   # Output Shape = (1,1,4096)，Param = (7*7*512+1)*4096 = 102764544
model.add(Dropout(0.5))                                     # Output Shape = (1,1,4096)
model.add(Convolution2D(4096, (1, 1), activation='relu'))   # Output Shape = (1,1,4096)，Param = (1*1*4096+1)*4096 = 16781312
model.add(Dropout(0.5))                                     # Output Shape = (1,1,4096)
model.add(Convolution2D(2622, (1, 1)))                      # Output Shape = (1,1,2622)，Param = (1*1*4096+1)*2622 = 10742334
model.add(Flatten())
model.add(Activation('softmax'))

# print(model.summary())

model.load_weights('vgg_face_weights.h5')

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

vgg_face_descriptor = Model(inputs=model.layers[0].input, outputs=model.layers[-2].output)

epsilon = 0.80

def verifyFace(img1, img2):
    img1_representation = vgg_face_descriptor.predict(preprocess_image('C:/Users/easyl/Desktop/Project/%s' % (download_image(img1))))[0,:]
    img2_representation = vgg_face_descriptor.predict(preprocess_image('C:/Users/easyl/Desktop/Project/%s' % (download_image(img2))))[0,:]
    
    cosine_similarity = findCosineSimilarity(img1_representation, img2_representation)
    euclidean_distance = findEuclideanDistance(img1_representation, img2_representation)
    
    print("Cosine similarity: ",cosine_similarity)
    print("Euclidean distance: ",euclidean_distance)
    
    if(cosine_similarity > epsilon):
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

verifyFace("https://cdn1.imggmi.com/uploads/2019/9/26/410734a643b04fb4d0591cfbf61f4ae0-full.jpg", "https://cdn1.imggmi.com/uploads/2019/9/26/7a3aabd424161caa901c92032ac18cf6-full.jpg")