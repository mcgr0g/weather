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
        res = 'sever'#u'северный'
    elif 11.25 < deg <= 78.75:
        res = 'severo-vostok'#u'северо-восточный'
    elif 78.75 < deg <= 101.25:
        res = 'vostok' #u'восточный'
    elif 101.25 < deg <= 168.75:
        res = 'ugo-vostok' # u'юго-восточный'
    elif 168.75 < deg <= 191.25:
        res = 'ug' # u'южный'
    elif 191.25 < deg <= 258.75:
        res = 'ugo-vostok'# u'юго-западный'
    elif 258.75 < deg <= 281.25:
        res = 'zapad' # u'западный'
    elif 281.25 < deg <= 348.75:
        res = 'severo-zapad' # u'северо-западный'
    elif 348.75 < deg <= 360:
        res = 'sever' # u'северный'
    return res


def mail(*args):
    try:
        recipient_list = []
        for item in args:
            recipient_list.extend(item)

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)

        for addr in recipient_list:
            headers_list = [
                "From: " + EMAIL_HOST_USER,
                "Subject: " + mail_subj,
                "To: " + addr,
                "MIME-Version: 1.0",
                "Content-Type: text/plain"
            ]
            header_str = "\r\n".join(headers_list)
            mail_ready = header_str + "\r\n\r\n" + mail_body
            server.sendmail(EMAIL_HOST_USER, addr, mail_ready)

        server.quit()
        return 'success', recipient_list
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

    data_list = [
        nowDate,
        u'Now: ' + nowT,
        u'Tmax: ' + highT,
        u'Tmin: ' + lowT,
        u'Wind: ' + windSpeed,
        u'From: ' + windDirection
    ]
    data_str = "\r\n".join(data_list)
    data_ready = encode(data_str, "utf-8")
    return data_ready


mail_body = 'debugdata'
mail_subj = 'weather'

if hasattr(sys, 'real_prefix'):
    venv = 'working in venv'
else:
    venv = 'none venv'
    
d = datetime.now()

if d.time().hour == 7 and d.time().minute == 1:
    mail_body = getForecast()
    print d.strftime("%d.%m.%y %H:%M:%S"), venv, mail(to)
else:
    mail_body = getForecast()
    print d.strftime("%d.%m.%y %H:%M:%S"), venv, ' trying to send to ', mail(to)
