import collections
import sys
sys.path.append('C:\\inetpub\\wwwroot\\readpt.py')
import readpt
import jieba
from gensim import corpora,models,similarities,models
import os, codecs
import jieba
from collections import Counter
stopWords=[]

with open('C:\\inetpub\\wwwroot\\stopWords.txt', 'r',encoding="utf-8") as file:
    for data in file.readlines():
        data = data.strip()
        stopWords.append(data)

#回傳陣列(詞)
def get_word(txt):
    countkeys = []
    setkeys=[]
    jieba.load_userdict('C:\\inetpub\\wwwroot\\dict.txt.big')
    key = jieba.analyse.extract_tags(txt, topK=5, withWeight=False, allowPOS=())
    seg_list = jieba.cut_for_search(txt)
    #doc_list = list(filter(lambda a: a not in stopWords and a != '\n', seg_list))
    doc_list = list(filter(lambda a: a not in stopWords and a != '\n', key))
    c = Counter()
    for x in doc_list:
        if len(x)>1 and x != '\r\n':
            c[x] += 1
    
    
    sorted(c) 	
    b = Counter(c).most_common(1)
    #print(b)
    for (k,v) in c.most_common(100):
        countkeys.append(k)
        
    setkeys=list(set(countkeys))
    return setkeys
