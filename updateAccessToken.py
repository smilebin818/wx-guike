#!/usr/bin/python
#-*- coding: utf-8 -*-

"""
Update AccessToken.
"""

import urllib
import json

tokenFile = "AccessToken"

sAppId = "wx8ccdd6bb1cccd4cc"
secret = "ndaZ0pZD1AYp7bYGMt8b0ppj9iChbYShPSdAhN-5SUfewiWmUlwkNPG9-9G5KsYw"

def updateAccessToken():
    url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={0}&corpsecret={1}".format(sAppId, secret)

    web = urllib.urlopen(url)
    ret = json.loads(web.read())
    access_token = ret["access_token"]

    # write token to local file
    fw = open(tokenFile, "wb")
    fw.write(access_token)
    fw.close()

    return access_token

if __name__ == '__main__':
    updateAccessToken();

    try:
        raw_input()
    except:
        pass


