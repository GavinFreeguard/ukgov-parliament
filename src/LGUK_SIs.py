from __future__ import unicode_literals, print_function, division
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

__author__ = 'petrbouchal'

from bs4 import BeautifulSoup
import urllib2
from lib_general import WriteDict, FilenameWithTimestamp
from lib_UKParl import LGUKFindHighest

years = range(1988,2015)
uksiurls = []
for year in years:
    for uksino in range(1,3300):
        uksiurl = 'http://www.legislation.gov.uk/uksi/' + str(year) + '/' + str(uksino) + '/contents/enacted/data.xml'
        uksiurls.append(uksiurl)

dictlist = []
for url in uksiurls:
    print(url)
    try:
        response = urllib2.urlopen(url)
    except urllib2.HTTPError:
        print('Not found')
        continue
    data = response.read()
    soup = BeautifulSoup(data,'xml')
    try:
        test = soup.Metadata.Identifier
    except AttributeError:
        print('Not available')
        continue
    i={}
    i['DocCat'] = soup.Metadata.PrimaryMetadata.DocumentCategory['Value']
    i['DocMainType']= soup.Metadata.SecondaryMetadata.DocumentMainType['Value']
    i['DocYear'] = soup.Metadata.SecondaryMetadata.Number['Value']
    i['DocYear'] = soup.Metadata.SecondaryMetadata.Made['Date']
    i['DocEnactmentDate'] = soup.Metadata.SecondaryMetadata.Year['Value']
    i['NumberOfParas'] = soup.Metadata.Statistics.TotalParagraphs['Value']
    i['NumberOfBodyParas'] = soup.Metadata.Statistics.BodyParagraphs['Value']
    i['NumberOfScheduleParas'] = soup.Metadata.Statistics.ScheduleParagraphs['Value']
    dictlist.append(i)
WriteDict(FilenameWithTimestamp('../output/AllActs','csv'),dictlist)
