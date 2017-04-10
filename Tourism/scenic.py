#!/usr/bin/env python
# coding=utf-8
from httpmock import requestByGet,requestByPost
from bs4 import BeautifulSoup as soup
from urllib import request as urlre
from bs4.element import NavigableString
import os
import re 
import json
import csv
import threading
from queue import Queue
import random
import time

class User(threading.Thread):
    def __init__(self,que):
        threading.Thread.__init__(self)
        self.daemon = False
        self.queue = que
    def run(self):
        destfile=open(self.name+'userpois.csv','wt',encoding='utf-8')
        writer = csv.DictWriter(destfile,dialect='excel',fieldnames=['uid','poi_href','poi_id','name','star','content','datetime','description','pics','tel','site','time','traffic','ticket','opentime','location','insides'])
        writer.writeheader()
        try:
            while True:
                if self.queue.empty():
                    break
                uid = self.queue.get()
                print(self.name+' '+uid)
                getUsersThread(writer,uid)
        finally:
            destfile.close()

def getUsersThreads():
    file=open('leftusers.txt','rt',encoding='utf-8')

    que = Queue()
    for user in file.readlines():
        que.put(user.replace('\n',''), True, None)
    threads = [User(que) for x in range(15)]
    for t in threads:
        t.start()


def getUsersThread(writer,uid):
    url=getAbsPath('/home/ajax_review.php')
    offset=0
    hasmore=True
    while hasmore:
        data=geneUserData(uid,offset)
        data=requestByGet(url,isJson=True,data=data)['data'];
        hasmore=data['hasmore']=='true'
        data=data['html']
        dom=loadDom(data)
        for node in dom.find_all(class_=re.compile('poi-item')):
            dic=dict()
            dic['uid']=uid
            dic['poi_href']=findByClass(node,'cover').find('a')['href']
            dic['poi_id']=extractNum(dic['poi_href'])
            dic['name']=getValue(findByClass(node,'title'))
            dic['star']=findByClass(node,'rating')['data-star']
            dic['content']=getValue(findByClass(node,'poi-rev _j_comment'))
            dic['datetime']=getValue(findByClass(node,'time'))
            getPoiDescription(dic['poi_href'],dic)
            writer.writerow(dic)
            offset=offset+40



         

def loadDom(html):
    return soup(html,'html.parser')

def extractNum(content,index=1):
    return extractData(r'(\d+)',content,1)

def extractData(regex, content, index=1):  
    r = '0'  
    p = re.compile(regex)  
    m = p.search(content)  
    if m:  
        r = m.group(index)  
    return r  

def getAbsPath(path):
    return 'http://www.mafengwo.cn'+path

def filter(str):
    return str.strip(' \n ').replace('\n',' ')

def filterOverview(tag):
    return tag.has_attr('data-anchor') and tag['data-ahchor']=='overview'
def getValue(node):
    if node:
        return filter(node.text)
    return ''

def findByClass(node,cls):
    if node:
        return node.find(class_=cls)
    return None

def getOverview(node,dic):

    subnode=findByClass(node,'row row-picture row-bg')#图片数量
    dic['pics']=getPics(subnode)

    subnode=findByClass(node,'mod mod-detail')#详细信息
    getDetails(subnode,dic)

    subnode=findByClass(node,'mod mod-location')#位置信息
    dic['location']=getLocation(subnode)

    subnode=subnode.find(id=True)
    getAround(subnode)

    subnode=findByClass(node,'mod mod-innerScenic')#内部景点
    dic['insides']=getInsides(subnode)

def getAround(node):
    if node:
        params=node['data-params']
        id=json.loads(params)['poi_id']
        data={'params':params}
        url=getAbsPath('/poi/__pagelet__/pagelet/poiLocationApi')
        data=requestByGet(url,isJson=True,data=data)['data']['html']
        dom=loadDom(data)

        file=open('around.csv','a',encoding='utf-8')
        
        writer=None
        try:
            for node in dom.find_all('li'):
                dic=dict()
                dic['id']=id
                dic['aid']=node['data-id']
                dic['aname']=node['data-name']
                dic['atype']=node['data-type']
                dic['dist']=getValue(node.find('span'))
                if writer==None:
                    writer=getCsvWriter(file,dic.keys())
                writer.writerow(dic)
        finally:
            file.close()


def getUsers():
    file=open('leftusers.txt','rt',encoding='utf-8')
    destfile=open('userpois.csv','wt',encoding='utf-8')

    try:
        writer=None
        url=getAbsPath('/home/ajax_review.php')
        users=list(file.readlines())
        
        for user in users:
            uid=extractNum(user)
            print('user ',user)
            offset=0
            hasmore=True
            while hasmore:
                data=geneUserData(uid,offset)
                data=requestByGet(url,isJson=True,data=data)['data'];
                hasmore=data['hasmore']=='true'
                data=data['html']
                dom=loadDom(data)
                for node in dom.find_all(class_=re.compile('poi-item')):
                    dic=dict()
                    dic['uid']=uid
                    dic['poi_href']=findByClass(node,'cover').find('a')['href']
                    dic['poi_id']=extractNum(dic['poi_href'])
                    dic['name']=getValue(findByClass(node,'title'))
                    dic['star']=findByClass(node,'rating')['data-star']
                    dic['content']=getValue(findByClass(node,'poi-rev _j_comment'))
                    dic['datetime']=getValue(findByClass(node,'time'))
                    getPoiDescription(dic['poi_href'],dic)

                    if writer==None:
                        writer=getCsvWriter(destfile,dic.keys())
                    writer.writerow(dic)
                offset=offset+40
    finally:
        file.close()
        destfile.close()


def collectComment():
    try:
        file=open('comments.csv','w',encoding='utf-8')
        writer =None

        while True:  
            lock.acquire() 
            item=comDic.popitem()
            lock.release() 

            scenic=item[0]
            params=item[1]
            id=json.loads(params)['poi_id']
            print(scenic,' ',id)

            url=getAbsPath('/poi/__pagelet__/pagelet/poiCommentListApi')

            pagecount = -1
            pagenum = 1
        
            while True:
                print('Comment page ' + str(pagenum))
                data=geneCommentPageData(params,pagenum)
                html = requestByGet(url,isJson=True,data=data)['data']['html']
                dom = loadDom(html)
                if pagecount < 0:#首次请求
                    pagecount = getPageCount(dom)
                    getCommentDevide(dom,dic)

                for comment in dom.find_all('li',class_='rev-item comment-item clearfix'):
                    com = getCommentDetails(comment,id)
                    if(writer == None):
                        writer = getCsvWriter(file,list(com.keys()))
                    writer.writerow(com)
                pagenum = pagenum + 1
                if(pagenum > pagecount):
                    break
        
            
    finally:
        file.close()

        

def getCommentDetails(node,id):
    dic=dict()
    dic['poiid']=id
    dic['like']=getLikeNum(findByClass(node,'useful-num'))#点赞数

    subnode=findByClass(node,'name')
    dic['user']=getValue(subnode)
    dic['userhref']=subnode['href']

    subnode=findByClass(node,re.compile('s-star'))
    dic['star']=extractNum(subnode['class'][1])

    subnode=findByClass(node,'rev-img')
    dic['haspic']=subnode!=None

    dic['isGold']=findByClass(node,'icon-goldComment')!=None

    dic['content']=getValue(findByClass(node,'rev-txt'))
    dic['time']=getValue(findByClass(node,'time'))

    return dic

def getLikeNum(node):
    return getValue(node)

def getComms():
    file=open('scenics.csv','rt',encoding='utf-8')

    for line in file:
        id=line.split(',')[10]
        if id=='id':
            continue
        getCommentById(id)

def getCommentById(id):
    url=getAbsPath('/poi/__pagelet__/pagelet/poiCommentListApi')

    pagecount=-1
    pagenum=1

    file=open('comments.csv','a',encoding='utf-8')
    writer =None
    try:
        while True:
            print('Comment page '+str(pagenum))
            data=geneCommData(id,pagenum)
            html=requestByGet(url,isJson=True,data=data)['data']['html']
            dom=loadDom(html)

            if pagecount<0:
                pagecount=getPageCount(dom)

    
      
            for comment in dom.find_all('li',class_='rev-item comment-item clearfix'):
                com=getCommentDetails(comment,id)
                if(writer==None):
                    writer=getCsvWriter(file,list(com.keys()))
                writer.writerow(com)

            pagenum=pagenum+1
            if(pagenum>pagecount):
                break
    finally:
        file.close()

def getComments(node,dic):
    if node:
        params=node.find('div')['data-params']
        
        id=json.loads(params)['poi_id']
        dic['id']=id
        url=getAbsPath('/poi/__pagelet__/pagelet/poiCommentListApi')
        
        pagecount=-1
        pagenum=1
        
        file=open('comments.csv','a',encoding='utf-8')
        #writer =None
        try:
            while True:
                #print('Comment page '+str(pagenum))
                data=geneCommentPageData(params,pagenum)
                html=requestByGet(url,isJson=True,data=data)['data']['html']
                dom=loadDom(html)

                if pagecount<0:#首次请求
                    #pagecount=getPageCount(dom)
                    getCommentDevide(dom,dic)
                break

            
      
                #for comment in dom.find_all('li',class_='rev-item comment-item clearfix'):
                #    com=getCommentDetails(comment,id)
                #    if(writer==None):
                #        writer=getCsvWriter(file,list(com.keys()))
                #    writer.writerow(com)

                pagenum=pagenum+1
                if(pagenum>pagecount):
                    break
        finally:
            file.close()


def getCommentDevide(node,dic):
    subnode=findByClass(node,'mhd mhd-large')

    dic['totalcomm']=extractNum(getValue(subnode))

    tags=[]
    subnode=findByClass(node,'review-nav')
    for child in subnode.find_all('li'):
        cls=child.find('span')['class'][0]
        a=child.find('a')
        if(cls=='divide'):
            category=getValue(a.find('span'))
            count=getValue(findByClass(a,'num'))
            count=extractNum(count)

            if category=='有图':
                dic['piccomm']=count
            if category=='好评':
                dic['goodcomm']=count
            if category=='差评':
               dic['badcomm']=count
            if category=='中评':
               dic['midcomm']=count
            if category=='金牌点评':
               dic['goldcomm']=count
        else:
            tag=getValue(a)
            tags.append(tag)
    dic['tag']='|'.join(tags)
       
def getPics(node):
    try:
        if node:
            return int(extractNum(filter(node.find('span').text)))
        return 0
    except Exception as err:
        return 0

def getLocation(node):
    if node:
        return getValue(findByClass(node,'sub'))
    return ''

def getInsides(node):
    list=[]
    if node:
        subnode=node.find_all('li')
        for child in subnode:
            list.append(getValue(child.find('h3')))
        return '|'.join(list)
    return ''

def getDetails(node,dic):
    if node:
        #dic['summary']=getValue(findByClass(node,'summary'))#概况
        subnode=findByClass(node,'baseinfo clearfix')
        getBaseinfos(subnode,dic)#电话、网站、时间等

        dic['traffic']=''
        dic['ticket']=''
        dic['opentime']=''
        subnode=node.find_all('dl')
        for child in subnode:
            if(getValue(child.find('dt'))=='交通'):#交通
                dic['traffic']=getValue(child.find('dd'))
            if(getValue(child.find('dt'))=='门票'):#门票
                dic['ticket']=getValue(child.find('dd'))
            if(getValue(child.find('dt'))=='开放时间'):#开放时间
                dic['opentime']=getValue(child.find('dd'))



def getSummary(node):
    return getValue(node)

def getBaseinfos(node,dic):
    if node:
        subnode=findByClass(node,'tel')#电话
        dic['tel']=getValue(findByClass(subnode,'content'))

        subnode=findByClass(node,'item-site')#网站
        dic['site']=getValue(findByClass(subnode,'content'))

        subnode=findByClass(node,'item-time')#花费时间
        dic['time']=getValue(findByClass(subnode,'content'))
        

def getDetail(url):
    dic = dict()
    
    url=getAbsPath(url)
    html=requestByGet(url)
    dom=loadDom(html)

    node = dom.find(attrs={'data-anchor':'overview'})
    getOverview(node,dic)
    
    node=dom.find(attrs={'data-anchor':'commentlist'})

    getComments(node,dic)


    return dic

def getPoiDescription(url,dic):
    url=getAbsPath(url)
    html=requestByGet(url)
    dom=loadDom(html)
    dic['description']=getValue(findByClass(dom,'summary'))
    if(dic['description']!=''):
        node = dom.find(attrs={'data-anchor':'overview'})
        getOverview(node,dic)

def getScenics(url):
    url = getAbsPath(url)
    
    pagecount=-1
    pagenum=1
    writer=None
    file=open('scenics.csv','w',encoding='utf-8')
    try:

        while True:
            print('Scenic page '+str(pagenum))

            data = geneSecnicPageData(pagenum)
            data=requestByPost(url,isJson=True,data=data)['data']

            if pagecount<0:
                pagecount=getPageCount(loadDom(data['page']))

            dom=loadDom(data['list'])
      
            for scenic in dom.find_all('li'):
                name=scenic.find_all('h3')[0].text
                print(name)

                
                href=scenic.a['href']
                detail=getDetail(href)
                detail['name']=name
                if writer==None:
                    writer=getCsvWriter(file,list(detail.keys()))
                writer.writerow(detail)
            pagenum=pagenum+1
            if(pagenum>pagecount):
                break
    finally:
        file.close()

def geneSecnicPageData(pagenum):
    return {"sAct":"KMdd_StructWebAjax|GetPoisByTag",
                       "iMddid":"10133",
                       "iTagId":"0" ,
                       "iPage":pagenum }
def geneCommentPageData(params,pagenum):
    params=json.loads(params)
    if pagenum>1:
        params['page']=pagenum
        params['just_comment']=1
        

    
    return {'params':json.dumps(params)}

def geneCommData(id,pagenum):
    dic=dict()
    dic['poi_id']=id

    if pagenum>1:
        dic['page']=pagenum
        dic['just_comment']=1
    return {'params':json.dumps(dic)}

def geneUserData(uid,offset):
    data={
        'act':'loadList',
        'offset':offset,
        'limit':40,
        'uid':uid
        }
    return data

def getPageCount(dom):
    node=dom.find(class_='m-pagination')
    if node:
        return int(node.find('span',class_='count').find('span').text)
    return 1

    
def getCsvWriter(file,headers):
    writer = csv.DictWriter(file,dialect='excel',fieldnames=headers)
    writer.writeheader()
    return writer


def getReview(uid):
    url=getAbsPath('/home/ajax_review.php')
    data={'act':'loadList',
          'filter':0,
          'offset':0,
          'limit':500,
          'uid':uid,
          'sort':1}
    data=requestByGet(url,isJson=True,data=data)
