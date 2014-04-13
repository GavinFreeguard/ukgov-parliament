__author__ = 'petrbouchal'


from __future__ import unicode_literals, print_function, division
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import csv
from bs4 import BeautifulSoup
import urllib
import urllib2
import time
import datetime
from datetime import datetime
now = datetime.now()
import re
from twfy import TWFY
import json
import unicodedata

years = range(1960,2015)
dictlist = []
for year in years:
    for actno in range(1,60):
        url = 'http://www.legislation.gov.uk/ukpga/' + year + '/' + actno + '/contents/enacted/data.xml'
        try:
            response = urllib2.urlopen(url)
        except urllib2.HTTPError:
            continue
        data = response.read()
        soup = BeautifulSoup(data,'xml')
        i={}
        i['DocCat'] = soup.Metadata.PrimaryMetadata.DocumentCategory['Value']
        i['DocMainType']= soup.Metadata.PrimaryMetadata.DocumentMainType['Value']
        i['DocYear'] = soup.Metadata.PrimaryMetadata.Number['Value']
        i['DocYear'] = soup.Metadata.PrimaryMetadata.EnactmentDate['Value']
        i['DocEnactmentDate'] = soup.Metadata.PrimaryMetadata.Year['Value']
        i['NumberOfParas'] = soup.Metadata.Statistics.TotalParagraphs['Value']
        i['NumberOfBodyParas'] = soup.Metadata.Statistics.BodyParagraphs['Value']
        i['NumberOfScheduleParas'] = soup.Metadata.Statistics.ScheduleParagraphs['Value']
        dictlist.append(i)


