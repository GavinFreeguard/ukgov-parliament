'''
Created on May 5, 2012

@author: petrbouchal
'''
from twfy import TWFY
twfy = TWFY.TWFY('G8rDJLCXMjVNE2rc9cE9kx4J')

import json

debate_list = json.loads(twfy.api.getDebates(output='js',date='01/08/2011',type='commons'), 'iso-8859-1')
print debate_list

results = {}

#Count the number of MPs for each party.
for mp in mp_list:
    party =  mp['party']
    if party in results.keys():
        results[party] += 1
    else:
        results[party] = 1
        
total_seats = float(sum(results.values()))

#Print the results.
for k, v in results.iteritems():
    print k, ' = ', (v/total_seats)*100, '%'




