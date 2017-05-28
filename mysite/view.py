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
		return HttpResponse(handler.data,content_type='application/json')