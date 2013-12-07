#! /usr/bin/env python
# -*- coding: utf8 -*-
import smtplib, urllib, json, sys
from codecs import encode
from genericpath import isfile
from os.path import dirname, abspath, join
from datetime import datetime

#---private data-------------
EMAIL_HOST = 'lolhost.ru'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'server@domain.com'
EMAIL_HOST_PASSWORD = 'easy'

to = ['user1@gmail.com', 'user2@mail.ru']
#---end private data--------

CUR_DIR = dirname(abspath(__file__))
if isfile(join(CUR_DIR, 'local_settings.py')):
    try:
        from local_settings import *
    except Exception, e:
        import os, warnings
        warnings.warn("Unable import local settings [%s]: %s" % (type(e), e))
        sys.exit(1)


def rozaVetrov(deg):
    res = ''
    if 0 <= deg <= 11.25:
        res = u'северный'
    elif 11.25 < deg <= 78.75:
        res = u'северо-восточный'
    elif 78.75 < deg <= 101.25:
        res = u'восточный'
    elif 101.25 < deg <= 168.75:
        res = u'юго-восточный'
    elif 168.75 < deg <= 191.25:
        res = u'южный'
    elif 191.25 < deg <= 258.75:
        res = u'юго-западный'
    elif 258.75 < deg <= 281.25:
        res = u'западный'
    elif 281.25 < deg <= 348.75:
        res = u'северо-западный'
    elif 348.75 < deg <= 360:
        res = u'северный'
    return res


def mail(*args):
    body = """From: server <%s>\nTo: %s\nSubject: %s\n\n%s""" % (EMAIL_HOST_USER, ", ".join(to), subject, msg_body)
    try:
        RECIPIENT = []
        for item in args:
            RECIPIENT.extend(item)
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        server.sendmail(EMAIL_HOST_USER, RECIPIENT, body)
        server.quit()
        return 'success', RECIPIENT
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise


yahooUrl = 'http://query.yahooapis.com/v1/public/yql'
query = ''
yahooParams = {'q': query, 'format': "json"}

yahooWOEID = '24553418'  # it s Novosibirsk WOEID, for another city visit http://location.yahoo.com/locationmgt/"
query = 'SELECT * FROM weather.forecast WHERE woeid="%s" and u="c"' % yahooWOEID
yahooParams['q'] = query
params = urllib.urlencode(yahooParams)


def getForecast():
    yahooResponse = urllib.urlopen(yahooUrl + '?' + params)
    data = json.load(yahooResponse)
    yahooResponse.close()
    
    res = data['query']['results']['channel']['item']

    nowDate = res['condition']['date']
    nowT = res['condition']['temp']

    today = res['forecast'][0]
    highT = today['high']
    lowT = today['low']

    wind = data['query']['results']['channel']['wind']
    windDirection = rozaVetrov(int(wind['direction']))
    windSpeed = wind['speed']

    message = nowDate + u'\nЗа бортом: ' + nowT + u'C\nТмакс=' + highT + u'\nТмин=' + lowT + u'\nВетер=' + windSpeed + u' км/ч\nДует: ' + windDirection
    message_data = encode(message, "utf-8")
    return message_data


msg_body = 'debugdata'
subject = 'weather'

if hasattr(sys, 'real_prefix'):
    venv = 'working in venv'
else:
    venv = 'none venv'
    
d = datetime.now()

if d.time().hour == 7 and d.time().minute == 1:
    msg_body = getForecast()
    #print venv
    print d.strftime("%d.%m.%y %H:%M:%S"), mail(to)