import collections
import sys
sys.path.append('C:\\Users\\ASUS\\Desktop\\wordsimilar\\readpt.py')
sys.path.append('C:\\Users\\ASUS\\Desktop\\wordsimilar\\jeibatext.py')
import readpt
import jeibatext
import jieba.analyse
import gensim
from gensim import corpora,models,similarities,models
from gensim.models import word2vec
from gensim.models import Doc2Vec 
import os, codecs
import jieba
from collections import Counter
countnum = []
similarnum = []
countnum1 = []
countkeys = []
countkeys1 = []

avg=0
s = []
s1=[]
s2=[]
total = 0
count = 0
new_model = gensim.models.Word2Vec.load('C:\\Users\\ASUS\\Downloads\\20180309wiki_model\\20180309wiki_model.bin')
doc0 = readpt.read('C:\\Users\\ASUS\\Desktop\\test data\\des\\city (4).jpg')
#doc0 = readpt.read("https://bnextmedia.s3.hicloud.net.tw/image/album/2017-08/img-1502423734-83598@900.png")
doc1 = readpt.read('C:\\Users\\ASUS\\Desktop\\test data\\Ar\\Architecture1.jpg')
#doc1 = readpt.read("http://juang.bst.ntu.edu.tw/Lab520/images/powerpoint00.jpg")
countnum = jeibatext.get_wordsadnum(doc0) #所有斷詞計算其出現的次數
countkeys = jeibatext.get_word(doc0)  

countnum1 = jeibatext.get_wordsadnum(doc1) #所有斷詞計算其出現的次數
countkeys1 = jeibatext.get_word(doc1) 




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

avg = total/count

print(avg)  
print('\n')
	
jeibatext.download_image("https://bnextmedia.s3.hicloud.net.tw/image/album/2017-08/img-1502423734-83598@900.png")
print('\n')





     
