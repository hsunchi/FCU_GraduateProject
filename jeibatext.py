import collections
import sys
sys.path.append('C:\\Users\\ASUS\\Desktop\\wordsimilar\\readpt.py')
import readpt
import jieba
from gensim import corpora,models,similarities,models
import os, codecs
import jieba
from collections import Counter
import requests
import urllib.request
stopWords=[]

with open('C:\\Users\\ASUS\\Desktop\\wordsimilar\\stopWords.txt', 'r') as file:
    for data in file.readlines():
        data = data.strip()
        stopWords.append(data)

#回傳陣列(詞與出現數量)
def get_wordsadnum(txt):
    jieba.load_userdict('C:\\Users\\ASUS\\Desktop\\wordsimilar\\dict.big')
    key = jieba.analyse.extract_tags(txt, topK=20, withWeight=False, allowPOS=())  
    seg_list = jieba.cut(txt,cut_all=False)
    print(seg_list)
    #doc_list = list(filter(lambda a: a not in stopWords and a != '\n', seg_list))
    keyremainderWords = list(filter(lambda a: a not in stopWords and a != '\n',key))
    c = Counter()
    for x in keyremainderWords:
        if len(x)>1 and x != '\r\n':
            c[x] += 1
    #print('常用词频度统计结果')	
    sorted(c) 	
    b = Counter(c).most_common(1)
    #print(b)
   # for (k,v) in c.most_common(10):
        #print('%s%s %s  %d' % ('  '*(5-len(k)), k, '*'*int(v/3), v))
    return c		
    #return countkeys

#回傳陣列(詞)
#提取關鍵詞
def get_word(txt):
    countkeys = []
    setkeys=[]
    jieba.load_userdict('C:\\Users\\ASUS\\Desktop\\wordsimilar\\dict.big')
    key = jieba.analyse.extract_tags(txt, topK=20, withWeight=False, allowPOS=())  #提取關鍵字
    seg_list = jieba.cut_for_search(txt)                                           #利用jeiba 做斷詞
    doc_list = list(filter(lambda a: a not in stopWords and a != '\n', key)) 
    c = Counter()
	#計算詞所出現的次數
    for x in doc_list:
        if len(x)>1 and x != '\r\n':
            c[x] += 1
    
    sorted(c) 	
	#將每個詞加入倒countkeys的陣列裡
    for (k,v) in c.most_common(100):
        countkeys.append(k)
        #print('%s%s %s  %d' % ('  '*(5-len(k)), k, '*'*int(v/3), v))
    setkeys=list(set(countkeys))
    #print(countkeys)
    return setkeys

#提取所有詞
def get_all_word(txt):
    countkeys = []
    setkeys=[]
    jieba.load_userdict('C:\\Users\\ASUS\\Desktop\\wordsimilar\\dict.big')
    seg_list = jieba.cut_for_search(txt)
    #doc_list = list(filter(lambda a: a not in stopWords and a != '\n', seg_list))
    doc_list = list(filter(lambda a: a not in stopWords and a != '\n', seg_list))
    c = Counter()
    for x in doc_list:
        if len(x)>1 and x != '\r\n':
            c[x] += 1
    #print('常用词频度统计结果')
    
    sorted(c) 	
    b = Counter(c).most_common(1)
    #print(b)
    for (k,v) in c.most_common(100):
        countkeys.append(k)
        #print('%s%s %s  %d' % ('  '*(5-len(k)), k, '*'*int(v/3), v))
    setkeys=list(set(countkeys))
    #print(countkeys)
    return setkeys

def download_image(url):
    filename = url.split('/')[-1]   # 以斜線分割保留最後一段
    r = requests.get(url, allow_redirects=True)     # 向http請求，取得url裡的資料
    open(filename, 'wb').write(r.content)    #將url的資料寫入
    return filename
	
