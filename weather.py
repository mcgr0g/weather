#! /usr/bin/env python
# -*- coding: utf8 -*-
"""
hello word script
it get weather forecast from yahoo and send it to email list
"""
import json
import smtplib
import urllib
import sys
import warnings
from codecs import encode
from genericpath import isfile
from os.path import dirname, abspath, join
from datetime import datetime

#---private data-------------
EMAIL_HOST = 'lolhost.ru'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'server@domain.com'
EMAIL_HOST_PASS = 'easy'
MAIL_H = 7
MAIL_M = 1

TO = ['user1@gmail.com', 'user2@mail.ru']
#---end private data--------

CUR_DIR = dirname(abspath(__file__))
if isfile(join(CUR_DIR, 'settings_local.py')):
    try:
        from settings_local import *
    except Exception, E:
        warnings.warn("Fail import local settings [%s]: %s" % (type(E), E))
        sys.exit(1)

if isfile(join(CUR_DIR, 'settings_production.py')):
    try:
        from settings_production import *
    except Exception as E:
        warnings.warn("Fail import production settings [%s]: %s" % (type(E), E))
        sys.exit(1)


def roza_vetrov(deg):
    """
    convert direction in float to human readable format
    """
    res = ''
    if 0 <= deg <= 11.25:
        res = 'sever'  # u"северный"
    elif 11.25 < deg <= 78.75:
        res = 'severo-vostok'  # u"северо-восточный"
    elif 78.75 < deg <= 101.25:
        res = 'vostok'  # u"восточный"
    elif 101.25 < deg <= 168.75:
        res = 'ugo-vostok'  # u"юго-восточный"
    elif 168.75 < deg <= 191.25:
        res = 'ug'  # u"южный"
    elif 191.25 < deg <= 258.75:
        res = 'ugo-vostok'  # u"юго-западный"
    elif 258.75 < deg <= 281.25:
        res = 'zapad'  # u"западный"
    elif 281.25 < deg <= 348.75:
        res = 'severo-zapad'  # u"северо-западный"
    elif 348.75 < deg <= 360:
        res = 'sever'  # u"северный"
    return res


def mail(*args):
    """
    usual mail function from stackowerflow
    """
    try:
        recipient_list = []
        for item in args:
            recipient_list.extend(item)

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASS)

        for addr in recipient_list:
            headers_list = [
                "From: " + EMAIL_HOST_USER,
                "Subject: " + MAIL_SUBJ,
                "To: " + addr,
                "MIME-Version: 1.0",
                "Content-Type: text/plain"
            ]
            header_str = "\r\n".join(headers_list)
            mail_ready = header_str + "\r\n\r\n" + MAIL_BODY
            server.sendmail(EMAIL_HOST_USER, addr, mail_ready)

        server.quit()
        return 'success', recipient_list
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise


YAHOO_URL = 'http://query.yahooapis.com/v1/public/yql'
YAHOO_WOEID = '24553418'  # Novosibirsk
# for another city visit http://location.yahoo.com/locationmgt/"


def get_forecast():
    """
    func return forecast from yahoo site for the city id equal YAHOO_WOEID
    """
    query = """\
    SELECT * FROM weather.forecast WHERE woeid="%s" and u="c"
    """ % YAHOO_WOEID
    yahoo_params = {'q': query, 'format': "json"}
    params = urllib.urlencode(yahoo_params)
    yahoo_response = urllib.urlopen(YAHOO_URL + '?' + params)
    data = json.load(yahoo_response)
    yahoo_response.close()
    return data


def convert_forecast():
    """
    returns forecast ready to past into mail body
    """
    data = get_forecast()

    res = data['query']['results']['channel']['item']

    now_date = res['condition']['date']
    now_t = res['condition']['temp']

    today = res['forecast'][0]
    high_t = today['high']
    low_t = today['low']

    wind = data['query']['results']['channel']['wind']
    wind_direction = roza_vetrov(int(wind['direction']))
    wind_speed = wind['speed']

    data_list = [
        now_date,
        u'Now: ' + now_t,
        u'Tmax: ' + high_t,
        u'Tmin: ' + low_t,
        u'Wind: ' + wind_speed,
        u'From: ' + wind_direction
    ]
    data_str = "\r\n".join(data_list)
    data_ready = encode(data_str, "utf-8")
    return data_ready


MAIL_BODY = 'debugdata'
MAIL_SUBJ = 'weather'


def sandbox():
    """
    chek if main script work at virtualenv
    """
    if hasattr(sys, 'real_prefix'):
        venv = 'working in venv'
    else:
        venv = 'none venv'
    return venv


NOW = datetime.now()
STATS = NOW.strftime("%d.%m.%y %H:%M:%S") + ' ' + sandbox()

if NOW.time().hour == MAIL_H and NOW.time().minute == MAIL_M:
    MAIL_BODY = convert_forecast()
    print STATS, mail(TO)
else:
    print STATS, ' try send to ', TO
