__author__ = 'petrbouchal'

outputfolder = '../output/'

def DGUKopenAndParse(apiaction,apidata):
    'Returns parsed result from API call'
    import urllib
    import urllib2
    import json
    apibase = 'http://data.gov.uk/api/3/'
    data_string = urllib.quote(json.dumps(apidata))
    rawdata = urllib2.urlopen(apibase+'action/'+apiaction,data_string)
    # print apibase+'/action/'+apiaction+data_string
    result = json.loads(rawdata.read())['result']
    return result

def GovUkOpenAndParse(baseurl,querydata):
    'Returns parsed result from API call'
    import urllib
    import urllib2
    from time import sleep
    from bs4 import BeautifulSoup
    try:
        data_string = urllib.urlencode(querydata)
        try:
            rawdata = urllib2.urlopen(baseurl+'?'+data_string)
        except urllib2.HTTPError,e:
            print('HTTP Error')
            print(e)
            print('Trying again in 10 seconds')
            sleep(10)
            try:
                rawdata = urllib2.urlopen(baseurl+'?'+data_string)
            except urllib2.HTTPError,e:
                print('Failed - HTTP Error')
                print(e)
                raise
    except TypeError:
        try:
            rawdata = urllib2.urlopen(baseurl)
        except urllib2.HTTPError,e:
            print('HTTP Error')
            print(e)
            print('Trying again in 10 seconds')
            sleep(10)
            try:
                rawdata = urllib2.urlopen(baseurl)
            except urllib2.HTTPError,e:
                print('Failed - HTTP Error')
                print(e)
                raise
    data = rawdata.read()
    result = BeautifulSoup(data,'lxml')
    return result

def LGUKFindHighest(legtype,topcount,year):
    """
    Searches for highest-numbered document on Legislation.gov.uk
    @legtype: str
    @topcount: int
    @year: int
    """
    import httplib

    solved = 0
    count = topcount
    while(solved==0):
        url = 'http://www.legislation.gov.uk/' + legtype + '/' + str(year) + '/' + str(count) + \
              '/contents/enacted/data.xml'
        c = httplib.HTTPConnection(url)
        c.request("HEAD", '')
        oldcount = count
        if c.getresponse().status > 399:
            pagefound = 0
            solved = 0
            count = oldcount/2
        else:
            pagefound = 1
            count = oldcount
            print('Fi')
        previouspagefound = pagefound

