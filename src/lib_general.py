__author__ = 'petrbouchal'
outputfolder = '../output/'


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


def FilenameWithTimestamp(filename,extension):
    """
    Returns filename with timestamp
    @filename: str
    @extension:str
    """
    from datetime import datetime
    now = datetime.now()
    now_string = now.strftime("%Y%m%d_%H%M%S")
    outname = filename + '_' + now_string + '.' + extension
    return outname


def SavePrettyJSON(JSONobject,filename):
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