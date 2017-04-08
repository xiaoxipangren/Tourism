#!/usr/bin/env python
# coding=utf-8

import requests
import json
import random

def geneHeader():
    user_agent = ["Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36","Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50","Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50","Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1","Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"]  
  
    headers = {  
    'User-Agent':  user_agent[random.randint(0,4)],  
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',  
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',  
    'Accept-Encoding': 'gzip, deflate, br',  
    'Cookie': '',  
    'Connection': 'keep-alive',  
    'Pragma': 'no-cache',  
    'Cache-Control': 'no-cache'  
    }  

    return headers

def requestByGet(url,isJson=False,params=None):
    header = geneHeader()
    r = requests.get(url,headers=header,params=params)
    if(isJson):
        return r.json()
    else:
        return r.text

def requestByPost(url,isJson=False,data=None):
    header = geneHeader()
    r = requests.post(url,headers=header,data=data)
    if(isJson):
        return r.json()
    else:
        return r.text