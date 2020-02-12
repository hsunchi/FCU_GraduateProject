from flask import Flask, request, abort
import tempfile
import os
from google.cloud import vision
from google.cloud.vision import types



client = vision.ImageAnnotatorClient.from_service_account_json("C:\\inetpub\\wwwroot\\test-vision-api-257df9c44873.json")

def detect_labels_url(url):
    image = vision.types.Image()
    image.source.image_uri = url
    resp = client.label_detection(image=image)
    labels = resp.label_annotations
    # result = ""
    # for label in labels:
    #     result += '\n' + label.description
    lab=[]
    for label in labels:
        lab.append(label.description)
    for i in lab:
        if i=='Orator' or  i=='Professor' or  i=='Projection Screen' or  i=='Presentation' or  i=='Lecture' or i=='Newscaster' or i=='Screen' or i=='Display Device':
            return True
    return True

def detect_texts_url(url):
    image = vision.types.Image()
    image.source.image_uri = url
    resp = client.text_detection(image=image)
    texts = resp.text_annotations
    try:
        text = texts[0].description
    except:
        text = ""
    return text


