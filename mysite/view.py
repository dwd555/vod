#author:Joshua
#date:2017/06/06
#version:1.1.0

import logging; logging.basicConfig(level=logging.INFO)
from django.http import HttpResponse
from django.shortcuts import render
import urllib.request
from xml.parsers.expat import ParserCreate
import json

class DefaultSaxHandler(object):
	def __init__(self):
		self.data=''
	def start_element(self, name, attrs):
		# logging.info(json.dumps(attrs))
		self.data=json.dumps(attrs)
			
class SpecialSaxHandler(object):
	def __init__(self):
		self.data=''
	def start_element(self,name,attrs):
		if(name=="serviceInfo"):
			self.data=json.dumps(attrs)

def index(request):
	return render(request,'vodplay.html')

def getConfig(request):
	xml='''<?xml version="1.0" encoding="UTF-8"?><GetConfig/>'''
	reg="http://gw.vodserver.local/GetConfig"
	with urllib.request.urlopen(reg,data=xml.encode("utf-8")) as f:
		result=f.read().decode("utf-8")
		handler = DefaultSaxHandler()
		parser = ParserCreate()
		parser.StartElementHandler = handler.start_element
		parser.Parse(result)
		logging.info("alldata"+handler.data)
		return HttpResponse(handler.data,content_type='application/json')

def selectionStart(client,account,titleAssetId,serviceId):
	requestUrl="http://ns.gcable.cn/u1/SelectionStart?client="+client+"&account="+account+"&titleAssetId="+titleAssetId+"&serviceId="+serviceId
	with urllib.request.urlopen(requestUrl) as f:
		result=f.read().decode("utf-8")
		handler = DefaultSaxHandler()
		parser = ParserCreate()
		parser.StartElementHandler = handler.start_element
		parser.Parse(result)
		return json.loads(handler.data)["purchaseToken"]

def requestPlay(purchaseToken):
	requestUrl="http://192.168.1.202:8185/RequestPlay"
	xml='<?xml version="1.0" encoding="UTF-8" ?><RequestPlay purchaseToken="'+purchaseToken+'"/>'
	with urllib.request.urlopen(requestUrl,data=xml.encode("utf-8")) as f:
		result=f.read().decode("utf-8")
		handler = DefaultSaxHandler()
		parser = ParserCreate()
		parser.StartElementHandler = handler.start_element
		parser.Parse(result)
		logging.info('handler.data='+handler.data)
		# return json.loads(handler.data)["clientSessionId"]
		return handler.data

def sendPlay(clientSessionId):
	requestUrl="http://192.168.1.202:8185/Play"
	xml='<?xml version="1.0" encoding="UTF-8" ?><Play clientSessionId="'+clientSessionId+'" range="0.0-" scale="1.0"/>'
	logging.info("xml="+xml)
	with urllib.request.urlopen(requestUrl,data=xml.encode("utf-8")) as f:
		result=f.read().decode("utf-8")
		logging.info(result)
	return 'ok'

def getDanShen(client,account,titleAsstId):
	requestUrl="http://ns.gcable.cn/u1/GetItemData?client="+client+"&account="+account+"&titleAssetId="+titleAsstId
	with urllib.request.urlopen(requestUrl) as f:
		result=f.read().decode("utf-8")
		handler=SpecialSaxHandler()
		parser = ParserCreate()
		parser.StartElementHandler = handler.start_element
		parser.Parse(result)
		logging.info('handler.data='+handler.data)
		return handler.data

def getFolder(request):
	client=''
	account=''
	assetId="gd_thzq"
	folderType="0"
	xml='''<?xml version="1.0" encoding="UTF-8"?><GetConfig/>'''
	reg="http://gw.vodserver.local/GetConfig"
	with urllib.request.urlopen(reg,data=xml.encode("utf-8")) as f:
		result=f.read().decode("utf-8")
		handler = DefaultSaxHandler()
		parser = ParserCreate()
		parser.StartElementHandler = handler.start_element
		parser.Parse(result)
		logging.info("alldata"+handler.data)
		client=json.loads(handler.data)["client"]
		account=json.loads(handler.data)["account"]
	requestUrl="http://ns.gcable.cn/u1/GetFolderContents?client="+client+"&account="+account+"&assetId="+assetId+"&folderType="+folderType
	with urllib.request.urlopen(requestUrl) as f:
		result=f.read().decode("utf-8")
		return HttpResponse(result,content_type="application/xml")

def stop(request):
	clientSessionId = request.GET.get('clientSessionId')
	requestUrl="http://192.168.1.202:8185/TearDown"
	xml='<TearDown clientSessionId="'+clientSessionId+'"/>'
	with urllib.request.urlopen(requestUrl,data=xml.encode("utf-8")) as f:
		result=f.read().decode("utf-8")
		return HttpResponse(result,content_type="application/xml")

def play(request):
	client=''
	account=''
	purchaseToken=''
	clientSessionId=''
	playUrl=''
	serviceId=''
	res=''
	xml='''<?xml version="1.0" encoding="UTF-8"?><GetConfig/>'''
	reg="http://gw.vodserver.local/GetConfig"
	with urllib.request.urlopen(reg,data=xml.encode("utf-8")) as f:
		result=f.read().decode("utf-8")
		handler = DefaultSaxHandler()
		parser = ParserCreate()
		parser.StartElementHandler = handler.start_element
		parser.Parse(result)
		logging.info("alldata"+handler.data)
		client=json.loads(handler.data)["client"]
		account=json.loads(handler.data)["account"]
	serviceId=json.loads(getDanShen(client,account,"GDZX8020151009000591"))["serviceId"]
	logging.info("serviceId"+serviceId)
	purchaseToken=selectionStart(client, account,"GDZX8020151009000591",serviceId)
	logging.info("client="+client)
	logging.info("account="+account)
	logging.info("purchaseToken="+purchaseToken)
	#获取clientSessionId
	requestPlayData=requestPlay(purchaseToken)
	clientSessionId=json.loads(requestPlayData)["clientSessionId"]
	playUrl=json.loads(requestPlayData)["playUrl"]
	logging.info("clientSessionId="+clientSessionId)
	logging.info("playUrl="+playUrl)
	
	#发送play
	sendPlay(clientSessionId)	
	logging.info("sendPlay")
	res={"playUrl":playUrl,"clientSessionId":clientSessionId}
	logging.info(res)
	return HttpResponse(json.dumps(res),content_type='application/json')