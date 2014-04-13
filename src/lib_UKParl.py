__author__ = 'petrbouchal'

__author__ = 'bouchalp'

outputfolder = '../output/'

def SavePretty(JSONobject,filename):
    "Saves content of JSON as pretty-printed text"
    from pprint import pprint
    filepath = outputfolder + filename + '.json'
    dataconn=open(filepath,'w+')
    pprint(JSONobject,dataconn)
    dataconn.close()

def SaveFile(url,filename, fileext):
    import urllib2
    from time import sleep
    from urllib2 import HTTPError
    filepath = outputfolder + filename + '.' + fileext
    try:
        data = urllib2.urlopen(url)
    except HTTPError,e:
        print ('HTTP Error')
        print(e)
        print('Trying again in 10 seconds...')
        sleep(10)
        try:
            data = urllib2.urlopen(url)
        except HTTPError, e:
            print('Failed - HTTP Error')
            print(e)
            raise
    dataread = data.read()
    dataconn = open(filepath,'w+')
    dataconn.write(dataread)
    dataconn.flush()
    dataconn.close()

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

def WriteDict(filepath,listofdicts):
    """
    Writes dictionary to file in filepath
    @type filepath: str
    @param filepath:
    @param listofdicts: list of dictionaries
    """
    import csv
    with open(filepath, 'w+') as orgfile:
        orgwriter = csv.DictWriter(orgfile, fieldnames=listofdicts[0].keys())
        orgwriter.writeheader()
        orgwriter.writerows(listofdicts)
    result = True
    return result