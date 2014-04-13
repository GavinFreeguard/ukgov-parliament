__author__ = 'petrbouchal'

import urllib2
url = raw_input('Url')
print(urllib2.urlopen(url + '.com').read())