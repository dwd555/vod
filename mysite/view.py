#author:Joshua
#date:2017/06/01
#version:1.0.0

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

def play(request):
	client=''
	account=''
	purchaseToken=''
	clientSessionId=''
	playUrl=''
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
	purchaseToken=selectionStart(client, account,"GDZX8020151009000591","104001")
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
	return HttpResponse(playUrl)