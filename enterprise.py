#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cgi import parse_qs, escape
from encrypt.WXBizMsgCrypt import WXBizMsgCrypt
from pypinyin import pinyin, lazy_pinyin
from tools.getCommit import getCommit
from tools.getWeather import getWeather

import xml.etree.cElementTree as ET

import os, re, time, sys, threading
import urllib, urllib2
import threading
import datetime
import json
import requests

import sendMsg

# disable warnings
import warnings
warnings.filterwarnings("ignore")

sToken          = "2cmKkKbDegnuXuQS"
sEncodingAESKey = "2XBlppT6Hubc1z8jHgeAMQQnav9TrSmbWoOWKEgyTke"
sAppId          = "wx8ccdd6bb1cccd4cc"

# {0}: ToUserName
# {1}: FromUserName
# {2}: CreateTime
# {3}: Content
text_T = "\
<xml>\
<ToUserName><![CDATA[yanbin818]]></ToUserName>\
<FromUserName><![CDATA[wx1c77202393c1c41d]]></FromUserName>\
<CreateTime>1348831860</CreateTime>\
<MsgType><![CDATA[text]]></MsgType>\
<Content><![CDATA[{0}]]></Content>\
</xml>\
"

class AsyncSend(threading.Thread):
    def __init__(self, fromuser_name):
        threading.Thread.__init__(self)
        self.fromuser_name = fromuser_name

    def run(self):
        today = str(datetime.date.today()) # something like: 2014-11-10
        sendContent = getCommit("https://github.com/zhanglintc?tab=contributions&from={0}".format(today))
        sendMsg.sendMsg(
            content = sendContent,
            touser = self.fromuser_name,
        )

def tuling(text):
    url = "http://www.tuling123.com/openapi/api?key=77aa5b955fcab122b096f2c2dd8434c8&info={0}".format(text)
    content = urllib2.urlopen(url)
    content = json.loads(content.read())

    return content["text"]

def simsimi(text):
    text = urllib.quote(text.encode("utf-8"))
    url = "http://simsimi.com/getRealtimeReq?uuid=lsUq8qBErrxTthxXH5rqbcnMLEyvkPu9uI3dDsC9lW9&lc=ch&ft=1&reqText={0}".format(text)
    content = urllib2.urlopen(url)
    content = json.loads(content.read())

    return content.get("respSentence", "尚不支持...").encode("utf-8")

def getRequestBody(environ):
    # the environment variable CONTENT_LENGTH may be empty or missing
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))

    except (ValueError):
        request_body_size = 0

    # When the method is POST the query string will be sent
    # in the HTTP request body which is passed by the WSGI server
    # in the file like wsgi.input environment variable.
    request_body = environ['wsgi.input'].read(request_body_size)

    return request_body

def verifyCallbackMode(environ):
    d = parse_qs(environ['QUERY_STRING'])

    wx = WXBizMsgCrypt(sToken, sEncodingAESKey, sAppId)
    ret, sReplyEchoStr = wx.VerifyURL(d["msg_signature"][0], d["timestamp"][0], d["nonce"][0], d["echostr"][0])

    return sReplyEchoStr

class updateSend(threading.Thread):
    def __init__(self, fromuser_name, category):
        threading.Thread.__init__(self)
        self.fromuser_name = fromuser_name
        self.category = category

    def run(self):
        time_s = time.time()
        os.system("cd /home/yanbin/{0} && git pull".format(self.category))
        time_e = time.time()

        elapse = round(time_e - time_s, 3)
        sendContent = "{0} has updated at:\n{1}\nusing {2}s".format(self.category, time.ctime(), elapse)
        sendMsg.sendMsg(
            content = sendContent,
            touser = self.fromuser_name,
        )

def restart_server(restart_file_name):
    os.system("cd /home/yanbin/wx-guike_enterprise/ && python {0}.py &".format(restart_file_name))

def application(environ, start_response):
    # response content
    start_response('200 OK', [('Content-Type', 'text/html')])

    wx = WXBizMsgCrypt(sToken, sEncodingAESKey, sAppId)
    d = parse_qs(environ['QUERY_STRING'])

    # always restart Mmrz at start
    # restart_server()

    # set up weixin callback mode
    if "echostr" in environ['QUERY_STRING']:
        return verifyCallbackMode(environ)

    request_body = getRequestBody(environ)
    ret, xml_content = wx.DecryptMsg(request_body, d["msg_signature"][0], d["timestamp"][0], d["nonce"][0])
    xml_tree = ET.fromstring(xml_content)

    touser_name   = xml_tree.find("ToUserName").text
    fromuser_name = xml_tree.find("FromUserName").text
    create_time   = xml_tree.find("CreateTime").text
    msg_type      = xml_tree.find("MsgType").text
    agent_ID      = xml_tree.find("AgentID").text
    # content_text  = xml_tree.find("Content").text
    # event         = xml_tree.find("Event").text
    # event_key     = xml_tree.find("EventKey").text

    if agent_ID == "1":
        if msg_type == "event":
            event_key = xml_tree.find("EventKey").text

            # 轨刻：获取数据
            if event_key == "V1001_PULL_LATEST_DB":

                return ""
            # 轨刻：更新服务
            elif event_key == "V1002_PULL_LATEST_VERSION":

                ups = updateSend(fromuser_name, "wx-guike_server")
                ups.start()

                ret, message = wx.EncryptMsg(text_T.format("Updating wx-guike_server, please wait..."), d["nonce"][0])

                return message

            # 轨刻：重启服务
            elif event_key == "V1003_RESTART":

                restart_server("guikeServer_restart")

                ret, message = wx.EncryptMsg(text_T.format("restart guikeServer:7820, OK"), d["nonce"][0])

                return message

            # 重庆微地铁：获取数据
            elif event_key == "V2001_PULL_LATEST_DB":

                return ""
            # 重庆微地铁：更新服务
            elif event_key == "V2002_PULL_LATEST_VERSION":

                ups = updateSend(fromuser_name, "wx-cqwdt")
                ups.start()

                ret, message = wx.EncryptMsg(text_T.format("Updating wx-cqwdt, please wait..."), d["nonce"][0])

                return message

            # 重庆微地铁：重启服务
            elif event_key == "V2003_RESTART":

                restart_server("cqwdt_restart")

                ret, message = wx.EncryptMsg(text_T.format("restart cqwdt:7818, OK"), d["nonce"][0])

                return message
        else:
            content_text  = xml_tree.find("Content").text
            ret, message = wx.EncryptMsg(text_T.format(tuling(content_text)), d["nonce"][0])
            return message

    # return a null string
    return ""

def main():
    pass

if __name__ == '__main__':
    main()
