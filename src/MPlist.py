'''
Created on May 7, 2012

@author: petrbouchal
'''

import time
import urllib2
import pprint

from twfy import TWFY
twfy = TWFY.TWFY('G8rDJLCXMjVNE2rc9cE9kx4J')

import json
import csv
import datetime
import re
import unicodedata
now = datetime.datetime.now()

# prepare file for writing

session_year = ''
date = now.strftime("%Y%m%d")
datemps = now.strftime('%d/%m/%Y')

sponsorsoutfile = "../output/CurrentMPs_" + session_year + '_' + date + '.csv'
csvout3 = sponsorsoutfile
    
sponsorslist = open(csvout3, 'wb')
writer3 = csv.writer(sponsorslist)
headerrow3 = ['mpid_twfy', 'mpid_grdn', 'mpname', 'mpparty', 'mpconstituency', 'constid_grdn', 'mpyearentered', 'percvote', 'winmajor', 'nextparty', 'nextpartyrank']
writer3.writerow(headerrow3)

#getmp = 'http://findyourmp.parliament.uk/api/search?q=' + sponsor1 + '&format=csv'
allmps = json.loads(twfy.api.getMPs(output='js',search='',date=datemps), 'iso-8859-1')
for mpr in allmps:
    mpid_twfy = mpr['person_id']
    print 'TWFY MP ID: ' + mpid_twfy
    getmp2 = json.loads(twfy.api.getMP(output='js',id=mpid_twfy), 'iso-8859-1')
    mpparty = getmp2[0]['party']
    mpentered = getmp2[-1]['entered_house']
    mpenteredhow = getmp2[0]['entered_reason']
    mpyearentered = mpentered[:4]
    mpconstituency = getmp2[0]['constituency']
    mpname = getmp2[0]['full_name']
    print 'Name: ' + mpname
    print 'Party: ' + mpparty
    print 'Constituency: ' + mpconstituency
    print 'Entered Parliament (date): ' + mpentered
    print 'Entered Parliament (year): ' + mpyearentered
    constnameesc = mpconstituency.replace(' ','+')
    
    constnameesc = unicodedata.normalize('NFKD', constnameesc).encode('ascii','ignore')
    
    print 'URL-friendly constituency name: ' + constnameesc
    twfyconstiturl = 'http://www.theyworkforyou.com/api/getConstituency?name='+constnameesc+'&output=js&key=' + 'G8rDJLCXMjVNE2rc9cE9kx4J'        
    try:
        twfycon = urllib2.urlopen(twfyconstiturl)
    except IOError:
        print 'URL opening failed, trying again after 5 secs...'
        time.sleep(5)
        try:
            twfycon = urllib2.urlopen(twfyconstiturl)
        except IOError:
            raw_input('Connection failed, press enter after you fix it.')
    getconstit = json.load(twfycon, 'iso-8859-1')
    print 'Fetched data from ' + twfyconstiturl
    constid_grdn = getconstit['guardian_id']
    grdn_url = 'http://www.guardian.co.uk/politics/api/constituency/' + constid_grdn +'/json'
    try:
        response = urllib2.urlopen(grdn_url)
    except IOError:
        print 'URL opening failed, trying again after 5 secs...'
        time.sleep(5)
        try:
            response = urllib2.urlopen(grdn_url)
        except IOError:
            raw_input('Connection failed, press enter after you fix it.')
    grdn_const = json.load(response)
    winmajor = grdn_const['constituency']['contests'][0]['winning-majority-as-votes']
    grdn_mp_url = grdn_const['constituency']['mp']['json-url']
    print 'Guardian Const URL: ' + grdn_url
    print 'Guardian MP URL: ' + grdn_mp_url
    try:
        grdn_mp0 = urllib2.urlopen(grdn_mp_url)
    except IOError:
        print 'URL opening failed, trying again after 5 secs...'
        time.sleep(5)
        try:
            grdn_mp0 = urllib2.urlopen(grdn_url)
        except IOError:
            raw_input('Connection failed, press enter after you fix it.')
    grdn_mp = json.load(grdn_mp0, 'iso-8859-1')
    #pprint.pprint(grdn_mp)
    #pprint.pprint(grdn_const)
    percvote = grdn_mp['person']['candidacies'][0]['votes-as-percentage']
    mpid_grdn = grdn_const['constituency']['mp']['aristotle-id']
    print 'Guardian MP ID: '+ str(mpid_grdn)
    print 'Guardian Const ID: ' + str(constid_grdn)
    print '% of vote 2010: ' + str(percvote)
    print 'Majority: ' + str(winmajor)
    nextparty = grdn_const['constituency']['marginality']['targets'][0]['name']
    nextpartyrank = grdn_const['constituency']['marginality']['targets'][0]['target']
    print 'Next party: ' + nextparty
    print 'Rank for next party: ' + str(nextpartyrank)
    print ''
    
    row3 = [mpid_twfy, mpid_grdn, mpname, mpparty, mpconstituency, constid_grdn, mpyearentered, percvote, winmajor, nextparty, nextpartyrank]
    writer3.writerow(row3)
        