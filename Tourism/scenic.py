#!/usr/bin/env python
# coding=utf-8
from httpmock import requestByGet,requestByPost
from bs4 import BeautifulSoup as soup
from urllib import request as urlre
from bs4.element import NavigableString
import os
import re 
import json


def loadDom(html):
    return soup(html,'html.parser')
def getAbsPath(path):
    return 'http://www.mafengwo.cn'+path
def getDetail(url):
    url=

def getScenics(url):
    url = getAbsPath('/ajax/router.php')
    data = {"sAct":"KMdd_StructWebAjax|GetPoisByTag",
                       "iMddid":"10133",
                       "iTagId":"0" ,
                       "iPage":"1" }
                         
                         
                         
    data = requestByPost(url,isJson=True,data=data)['data']['list']
    dom=loadDom(data)
    for scenic in dom.find_all('li'):
        name=scenic.find_all('h3')[0].text
        href=scenic.a['href']
    
    

    
    