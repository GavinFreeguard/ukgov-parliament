from __future__ import unicode_literals, print_function, division
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

__author__ = 'petrbouchal'

from bs4 import BeautifulSoup
import urllib2
from lib_general import WriteDict, FilenameWithTimestamp

years = range(2010,2015)
acturls = []
uksiurls = []
for year in years:
    for actno in range(1,60):
        acturl = 'http://www.legislation.gov.uk/ukpga/' + str(year) + '/' + str(actno) + '/contents/enacted/data.xml'
        acturls.append(acturl)

urls = acturls + uksiurls
urls = acturls
urls = uksiurls

dictlist = []
for url in acturls:
    print(url)
    try:
        response = urllib2.urlopen(url)
    except urllib2.HTTPError:
        print('Not found')
        continue
    data = response.read()
    soup = BeautifulSoup(data,'xml')
    try:
        test = soup.Metadata.PrimaryMetadata.DocumentCategory['Value']
    except AttributeError:
        print('Not available')
        continue
    i={}
    i['DocCat'] = soup.Metadata.PrimaryMetadata.DocumentCategory['Value']
    i['DocMainType']= soup.Metadata.PrimaryMetadata.DocumentMainType['Value']
    i['DocYear'] = soup.Metadata.PrimaryMetadata.Number['Value']
    i['DocYear'] = soup.Metadata.PrimaryMetadata.EnactmentDate['Date']
    i['DocEnactmentDate'] = soup.Metadata.PrimaryMetadata.Year['Value']
    i['NumberOfParas'] = soup.Metadata.Statistics.TotalParagraphs['Value']
    i['NumberOfBodyParas'] = soup.Metadata.Statistics.BodyParagraphs['Value']
    i['NumberOfScheduleParas'] = soup.Metadata.Statistics.ScheduleParagraphs['Value']
    dictlist.append(i)
WriteDict(FilenameWithTimestamp('../output/AllActs','csv'),dictlist)

