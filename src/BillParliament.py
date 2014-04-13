'''
Created on May 5, 2012

@author: petrbouchal
'''

from __future__ import unicode_literals, print_function, division
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import csv
import re
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
import httplib
from lib_UKParl import WriteDict

twfy = TWFY.TWFY('G8rDJLCXMjVNE2rc9cE9kx4J')


# SESSION PARAMETERS
current_session = "2013-14"
# use first command-line argument as search term, if available
if len(sys.argv) > 1:
    session_years = [sys.argv[1]]
else:
    session_years = ["2013-14","2012-13","2010-12", "2009-10", "2008-09", "2007-08"] #2007-08 is the earliest for which the scraper works. Year after dash needs to have two digits.
# note: TWFY won't return the right MP through getMP if that MP is not in office at present, but will return all MPs through getMPs and/or getPerson at a certain time
# in the past, from which you can then pick up the desired MP. Then you need to take care to get the right constituency from getMP given the point in time, and take the guardian 
# constituency ID from there if possible

# perhaps you need to specify a last election date with each session and pick the right entry for a given person based on this?

# no idea how this is done (searching within JSON values instead of parameters)

# also should have a way of dealing with by-election ideally

# PREPARE FILES AND HEADERS

datetimestring = now.strftime("%Y%m%d_%H%M%S")

billsoutfile = "../output/billsUK_" + datetimestring + '.csv'
stagesoutfile = "../output/billsUK_stages_" + datetimestring + '.csv'

csvout1 = billsoutfile
csvout2 = stagesoutfile

MPs = []
Lords = []

billslist = open(csvout1, 'wb')
writer1 = csv.writer(billslist)
headerrow1 = ['Session', 'BillURL', 'DateAccessed', 'BillName', 'BillType', 'BillCat', 'UKPB_Bill',
              'UKPB_Act', 'RoyalAssent', 'RoyalAssentDate', 'LastChange', 'Stage', 'NumberofStages',
              'FirstStageDate', 'LastStageDate', 'FirsStageName', 'LastStageName', 'Sponsor1', 'Sponsor2',
              'Sponsor1Inst', 'Sponsor2Inst', 'Agent', 'Promoter', 'LatestStg-BillPage', 'LatestStgDate-Billpage',
              'NextStg-Billpage', 'NextStgDate-Billpage', 'BillTxtLnk1', 'BillTxtLnk2', 'BillTxtDate', 'BillTxtTitle',
              'LatestNews', 'Summary', 'mpnameuseful', 'mpid_twfy', 'mpid_grdn', 'mpparty', 'mpmajority', 'mpentered',
              'mpyearentered', 'mpconstituency', 'constid_grdn', 'mpmatch','NumParagraphsTotal','NumParagraphsBody',
              'NumParagraphsSchedules','LegGovUkLink','DocYear','DocMainType','DocEnactmentDate','DocCat','ActNameLGUK']
writer1.writerow(headerrow1)

stagefile = open(csvout2, 'wb')
writer2 = csv.writer(stagefile)
headerrow2 = ['BillURL', 'SessionYr', 'BillName', 'BillCat', 'UKPB_Bill', 'UKPB_Act', 'RoyalAssent',
              'RoyalAssentDate', 'StageName', 'StageDate', 'StageNumber', 'NumberofStages', 'firststage',
              'firststagedate', 'StageLink']
writer2.writerow(headerrow2)

# LOOP THROUGH SESSIONS

for session_year in session_years:
    print('Session: ' + session_year)
    urlbase = "http://services.parliament.uk/"

    if session_year == current_session:
        session_appendix = "bills/"
    else:
        session_appendix = "bills/" + session_year + ".html"

    urldat = urlbase + session_appendix

    # LOAD BILLS LIST
    try:
        response = urllib2.urlopen(urldat)
    except urllib2.HTTPError:
        print('URL opening failed, trying again after 5 secs...')
        time.sleep(5)
        try:
            response = urllib2.urlopen(urldat)
        except urllib2.HTTPError:
            raw_input('Connection failed, press enter after you fix it.')

    html0 = response.read()
    soup = BeautifulSoup(html0, "lxml")

    trpat = re.compile("tr[12]+")

    # LOOP THROUGH BILLS

    rows = soup.find_all('tr', trpat)

    for child in rows:
        middle = child.find_all("td", "middle")
        stage = middle[0].contents[1]['title']
        lastchange = middle[1].string
        billitem = child.find_all("td", "bill-item-description")
        billname = billitem[0].find('a').string.strip()
        print(billname + ', session ' + session_year)
        urlstub = billitem[0].find('a')['href']
        billurl = urlbase + urllib.quote(urlstub)
        print(billurl)

        # RETRIEVE BILL PAGE

        try:
            response = urllib2.urlopen(billurl)
        except urllib2.HTTPError:
            print('URL opening failed, trying again after 5 secs...')
            time.sleep(5)
            try:
                response = urllib2.urlopen(billurl)
            except urllib2.HTTPError:
                raw_input('Connection failed, press enter after you fix it.')

        # LOAD BILL PAGE              
        html = response.read()
        billsoup = BeautifulSoup(html)

        # FIND BASIC PARTS

        billagents = billsoup.find("dl", "bill-agents")
        try:
            billagent = billagents.find_all(["dd", "dt"])
        except AttributeError:
            continue
        typeofbill = billagent[1].string

        # DETERMINE TYPE OF BILL

        billcat = "O"
        if re.search('Government', typeofbill) != None:
            billcat = "G"
            UKPB_bill = 'Yes'
        if (re.search('Private', typeofbill) !=None) & (re.search('Member', typeofbill) !=None):
            billcat = "PMB-C"
            UKPB_bill = 'Yes'
        if (re.search('Private', typeofbill) !=None) & (re.search('Member', typeofbill) !=None) & (re.search('Lords', typeofbill) !=None):
            billcat = "PMB-L"
            UKPB_bill = 'Yes'
        if re.search('Private Bill', typeofbill) !=None:
            billcat = "PB"
            UKPB_bill = 'No'
        print(typeofbill + ', ' + billcat)

        sponsor1 = 'NA'
        sponsor2 = 'NA'
        sponsor1inst = 'NA'
        sponsor2inst = 'NA'
        parlagent = 'NA'
        promotedby = 'NA'

        # DETERMINE BILL AGENTS AND SPONSORS

        if len(billagent) > 2:
            if (billagent[3].name == "dd") & (billagent[2].contents[0] != "Parliamentary agents:"):
                sponsor1 = billagent[3].contents[0].strip()
                if billagent[3].find('a'):
                    sponsor1inst = billagent[3].find('a').contents[0].strip()
                else:
                    sponsor1inst = "NA"

            if (billagent[3].name == "dd") & (billagent[2].contents[0] != "Parliamentary agents:") & (billagent[2].contents[0]=="Sponsors:"):
                sponsor2 = billagent[4].contents[0].strip()
                if billagent[4].find('a'):
                    sponsor2inst = billagent[4].find('a').contents[0].strip()
                else:
                    sponsor2inst = "NA"
            else:
                sponsor2 = 'NA'
                sponsor2inst = 'NA'

            if (billagent[2].name == "dt") & (billagent[2].contents[0] == "Parliamentary agents:"):
                parlagent = billagent[3].find('a').contents[0].strip()
                promotedby = billagent[5].contents[0].strip()
                if len(billagent) > 6:
                    petiperiod = billagent[7].contents[0].strip()
                else:
                    petiperiod = 'NA'
            else:
                parlagent = 'NA'
                promotedby = 'NA'
                petiperiod = 'NA'
        else:
            sponsor1 = 'NA'
            sponsor2 = 'NA'
            sponsor1inst = 'NA'
            sponsor2inst = 'NA'
            parlagent = 'NA'
            promotedby = 'NA'
            petiperiod = 'NA'

        # DETERMINE BILL'S LAST EVENT

        if billsoup.find("div","last-event"):
            lastbox = billsoup.find("div","last-event")
            if lastbox.find_all('img'):
                lateststagename = lastbox.find_all('img')[-1]['title']
            else:
                lateststagename = lastbox.find_all('li')[-1].a.string
            lateststagedate = lastbox.find_all('li')[-1].contents[-1].split('|')[1].strip()
        else:
            lateststagename = 'Unknown'
            lateststagedate = 'Unknown'
        if lateststagename == 'Royal Assent':
            RoyalAssent = 'Yes'
            RoyalAssentDate = lateststagedate
        else:
            RoyalAssent = 'No'
            RoyalAssentDate = 'NA'

        if (RoyalAssent == 'Yes') & (UKPB_bill == 'Yes'):
            UKPB_Act = 'Yes'
        else:
            UKPB_Act = 'No'

        # GET BILL SUMMARY AND LINKS TO FILES
        summarybox = billsoup.find("div",id="bill-summary-all")

        if summarybox.find("td","bill-item-description"):
            billink1 = summarybox.find("td","bill-item-description").a['href']
            billfiletitle = summarybox.find("td","bill-item-description").a.string
            billinkdate = summarybox.find("td","bill-item-date").contents[0]
            if summarybox.find('td','bill-item-description').span:
                if summarybox.find('td','bill-item-description').span.a:
                    billink2 = summarybox.find('td','bill-item-description').span.a['href']
                else:
                    billink2 = 'NA'
            else:
                billink2 = 'NA'
        else:
            billink2 = 'NA'
            billink1 = 'NA'
            billinkdate = 'NA'
            billfiletitle = 'NA'

        # GET BILL LATEST NEWS

        latestnews = summarybox.find_all('h2')[1].next_sibling.strip()
        summary = ''
        for sibling in summarybox.find_all('h2')[2].next_siblings:
            summary = summary + ' ' + repr(sibling).replace('\n',' ').replace('\r',' ').strip()
            summary = summary.replace('\r',' ').replace('\r',' ')
            summary = re.sub('<.+?>', ' ', summary, re.IGNORECASE)

        # GET BILL NEXT EVENT

        if billsoup.find("div","next-event"):
            nextbox = billsoup.find("div","next-event")
            nextstagename = nextbox.find_all('img')[-1]['title']
            nextstagedate = nextbox.find_all('li')[-1].contents[-1].split('|')[1].strip()
        else:
            nextstagename = 'NA'
            nextstagedate = 'NA'

        # FOR MEMBERS BILLS, GET INFO ON MEMBER

        if billcat == 'PMB-C':

            # make it searchable - generic replacements
            mpnameuseful = sponsor1.replace('Mr ', '').replace('Dr ', '').replace('Dame ','').\
                replace('Sir ','').replace('Ms ','').replace('Mrs ','').replace('Miss ','').\
                replace('Ms. ','').replace('Mrs. ','').replace('Mr. ','').replace('Dr. ','')

            # MP-specific replacements
            mpnameuseful = mpnameuseful.replace('Mctaggart', 'Mactaggart').replace('Jeffrey M.','Jeffrey M')
            mpnameuseful = mpnameuseful.replace('Steve Baker','Steven Baker').replace('Nic ', 'Nicholas ').\
                replace('Chris Leslie', 'Christopher Leslie').replace('Steve McCabe','Stephen McCabe')
            mpnameuseful = re.sub('Th.+?r.+?se','Therese', mpnameuseful,re.UNICODE)
            getmp1 = json.loads(twfy.api.getMPs(output='js',search=mpnameuseful), 'iso-8859-1')

            # mark duplicates
            if len(getmp1) > 1:
                duplicatesfound = True
                mpproblem = 'DuplicateFound'
                mpparty = 'NA'
                mpentered = 'NA'
                mpmaj = 'NA'
                mpconstituency = 'NA'
                mpid_twfy = 'NA'
                mpid_grdn = 'NA'
                constid_grdn = 'NA'

            # mark not found
            elif len(getmp1) < 1:
                MPnotfound = True
                mpproblem = 'MPNotFound'
                mpparty = 'NA'
                mpentered = 'NA'
                mpyearentered = 'NA'
                mpmaj = 'NA'
                mpconstituency = 'NA'
                mpid_twfy = 'NA'
                mpid_grdn = 'NA'
                constid_grdn = 'NA'

            # otherwise look for MP in TWFY database
            else:
                MPnotfound = False
                duplicatesfound = False
                mpproblem = 'OK'
            for mpr in getmp1:
                mpid_twfy = mpr['person_id']
                print('TWFY MP ID: ' + mpid_twfy)
                getmp2 = json.loads(twfy.api.getMP(output='js',id=mpid_twfy), 'iso-8859-1')
                mpparty = getmp2[0]['party']
                mpentered = getmp2[-1]['entered_house']
                mpyearentered = mpentered[:4]
                mpenteredhow = getmp2[0]['entered_reason']
                mpconstituency = getmp2[0]['constituency']
                print('Name (as searched): '+ mpnameuseful)
                print('Party: ' + mpparty)
                print('Constituency: ' + mpconstituency)
                print('Entered house (year): ' + str(mpyearentered))
                constnameesc = mpconstituency.replace(' ','+')
                constnameesc = unicodedata.normalize('NFKD', constnameesc).encode('ascii','ignore')
                twfyconstiturl = 'http://www.theyworkforyou.com/api/getConstituency?name='+constnameesc+'&output=js&key=' + 'G8rDJLCXMjVNE2rc9cE9kx4J'
                try:
                    twfycon = urllib2.urlopen(twfyconstiturl)
                except urllib2.HTTPError:
                    print('URL opening failed, trying again after 5 secs...')
                    time.sleep(5)
                    try:
                        twfycon = urllib2.urlopen(twfyconstiturl)
                    except urllib2.HTTPError:
                        raw_input('Connection failed, press enter after you fix it.')

                getconstit = json.load(twfycon, 'iso-8859-1')
                constid_grdn = getconstit['guardian_id']
                grdn_url = 'http://www.theguardian.com/politics/api/constituency/' + constid_grdn +'/json'
                try:
                    response = urllib2.urlopen(grdn_url)
                except Exception:
                    print('URL opening failed, trying again after 5 secs...')
                    time.sleep(5)
                    try:
                        response = urllib2.urlopen(grdn_url)
                    except urllib2.HTTPError:
                        raw_input('Connection failed, press enter after you fix it.')
                grdn_const = json.load(response)
                mpid_grdn = grdn_const['constituency']['mp']['aristotle-id']
                mpmaj = grdn_const['constituency']['contests'][0]['winning-majority-as-votes']
                print('Guardian MP ID: ' + str(mpid_grdn))
                print('Guardian Constit ID: ' + str(constid_grdn))
                print('Majority: ' + str(mpmaj))

        else:
            mpnameuseful = 'NA'
            mpid_twfy = 'NA'
            mpid_grdn = 'NA'
            mpconstituency = 'NA'
            constid_grdn = 'NA'
            mpproblem = 'NA'
            mpentered = 'NA'
            mpyearentered = 'NA'
            mpparty = 'NA'
            mpmaj = 'NA'


        # GET STAGES PAGE
        stagesurl = billurl.replace('.html','') + '/stages.html'
        try:
            response = urllib2.urlopen(stagesurl)
        except urllib2.HTTPError:
            print('URL opening failed, trying again after 5 secs...')
            time.sleep(5)
            try:
                response = urllib2.urlopen(stagesurl)
            except urllib2.HTTPError:
                raw_input('Tried again, didnt work, waiting for input')

        # LOAD STAGES PAGE
        html2 = response.read()
        stagesoup = BeautifulSoup(html2)
        srows = stagesoup.find_all('tr', trpat)

        stagenumber = 0
        numberofstages = len(srows)
        billduration = 0

        # LOOP THROUGH STAGES & WRITE DATA
        for child in srows:
            rowno =+ 1
            stagerow = child.find_all("td")
            stagename = stagerow[0].contents[1]['title']
            stagedate = stagerow[2].string.strip()
            #stagedate = datetime.strptime(stagedate, '%d.%m.%Y')
            billitem = child.find_all("td", "bill-item-description")
            if billitem[0].find('a'):
                stagelink = billitem[0].find('a')['href'].strip()
            else:
                stagelink = "NA"
            stagenumber = stagenumber + 1

            if stagenumber == 1:
                firststage = "Yes"
                laststage = 'No'
                firststagedate = stagedate
                firststagedatewrite = stagedate
                laststagedate = 'NA'
                laststagename = 'NA'
                laststagedatewrite = 'NA'
                firststagename = stagename
                #stageduration = 0
                stagedates = [stagedate]

            if stagenumber == numberofstages:
                laststage = "Yes"
                firststage = 'No'
                laststagedate = stagedate
                laststagename = stagename
                laststagedatewrite = stagedate
                #stageduration = (stagedate - stagedates[-1])
                stagedates = stagedates.append(stagedate)

            else:
                firststage = 'No'
                laststage = 'No'
                #stageduration = (stagedate - stagedates[-1])

            # this arrangement makes it much easier to calculate time elapsed between events recorded in different rows               
            row2 = [billurl, session_year, billname, billcat, UKPB_bill, UKPB_Act, RoyalAssent, RoyalAssentDate,
                    stagename, stagedate, stagenumber, numberofstages, firststagename, firststagedatewrite, stagelink]
            #writer2.writerow(row2)
            #row2sall = row2sall.append(row2)
            #for line in row2sall:
            writer2.writerow(row2)

        # For bills that received Royal Assent, find length from Legislation.Gov.Uk
        if (RoyalAssent=='Yes'):
            if billcat == 'PB': # for private bills, set the type to UK Local Act
                typeLGUK = 'ukla'
            else:
                typeLGUK = 'ukpga' # for others set it to UK Public General Act
            print('This bill received Royal Assent')
            if (billfiletitle != 'NA') & (billfiletitle is not None):
                actname = re.sub(r'[\s]{1}[c]{1}[\.]{1}[\s]?[\w]*$','',billfiletitle)
                actnumMatchObject = re.search(r'[c]{1}[\.]{1}[\s]?[\d]*$',billfiletitle)
                if actnumMatchObject is not None: # if extraction worked, clean up match to get just the number
                    actnum = actnumMatchObject.group().replace('c.','').strip()
                else:
                    actnum = 'NA'
            else: # if there's no act name, use edited bill name
                actname = billname.replace(' [HL]','')
                actnum = 'NA'
            actnameLGUK = urllib.quote(actname)
            if actnum != 'NA': # if act number has been found, use it
                acturl = 'http://www.legislation.gov.uk/id?type=' + typeLGUK + '&number=' + actnum + \
                         '&year=' + RoyalAssentDate[6:10]
            else: # otherwise use act name
                acturl = 'http://www.legislation.gov.uk/id?type=' + typeLGUK + '&title=' + actnameLGUK + \
                         '&year=' + RoyalAssentDate[6:10]
            print(acturl)

            # find the final URL returned by legislation.gov.uk in response to search query
            # CATCH EXCEPTIONS AND ALLOW INPUT TO RETRY WITH BETTER PARAMETERS
            try:
                urlLGUK = urllib2.urlopen(acturl).geturl() + '/data.xml'
            except urllib2.HTTPError, e: # for HTTP Errors
                if e.code == 404: # for 404 errors, prompt for new search term
                    actnameLGUK = raw_input('No act found with this search from legislation.gov.uk. Enter new search term.')
                    newactnameLGUK = urllib2.quote(actnameLGUK)
                    try: # try searching with new term
                        acturl = 'http://www.legislation.gov.uk/id?type=' + typeLGUK + '&title=' + newactnameLGUK + \
                                 '&year=' + RoyalAssentDate[6:10]
                    except HTTPError, e: # if search with new term returns 'Multiple Options', prompt for URL
                        if e.code==300:
                            newurl = raw_input('Multiple choices available - insert final URL to use.')
                            urlLGUK = urllib2.urlopen(newurl).geturl() + '/data.xml'
                        if e.code==404: # if search with new term returns 404, prompt for URL
                            newurl = raw_input('Search with new term returned nothing. Enter final URL')
                            urlLGUK = urllib2.urlopen(newurl).geturl() + '/data.xml'
                if e.code == 300: # if original search returns 'Multiple options', prompt for URL
                    print(acturl)
                    newurl = raw_input('Multiple choices available - insert final URL to use.')
                    urlLGUK = urllib2.urlopen(newurl).geturl() + '/data.xml'

            # use this final URL to get XML data for that piece of legislation
            print(urlLGUK)
            try:
                response = urllib2.urlopen(urlLGUK)
            except urllib2.HTTPError:
                time.sleep(5)
                try:
                    response = urllib2.urlopen(urlLGUK)
                except urllib2.HTTPError:
                    raw_input('Connection failed. Press enter once you\'ve fixed it')
                    response = urllib2.urlopen(urlLGUK)
            # parse
            xmlLGUK = response.read()
            xmlsoup = BeautifulSoup(xmlLGUK,'xml')
            # get stats from inside XML
            numParas = xmlsoup.Metadata.Statistics.TotalParagraphs['Value']
            numBodyParas = xmlsoup.Metadata.Statistics.BodyParagraphs['Value']
            numScheduleParas = xmlsoup.Metadata.Statistics.ScheduleParagraphs['Value']
            DocCat = xmlsoup.Metadata.PrimaryMetadata.DocumentClassification.DocumentCategory['Value']
            DocMainType = xmlsoup.Metadata.PrimaryMetadata.DocumentClassification.DocumentMainType['Value']
            DocYear = xmlsoup.Metadata.PrimaryMetadata.Year['Value']
            DocEnactmentDate = xmlsoup.Metadata.PrimaryMetadata.EnactmentDate['Date']
            LGUKurl = urlLGUK
            ActName = xmlsoup.Metadata.title.text
        else:
            acturl = 'NA'
            numParas = 'NA'
            numBodyParas = 'NA'
            numScheduleParas = 'NA'
            DocCat = 'NA'
            DocEnactmentDate = 'NA'
            DocMainType = 'NA'
            DocYear = 'NA'
            LGUKurl = 'NA'
            ActName = 'NA'

        # WRITE BILL DATA
        row1 = [session_year, billurl, datetimestring, billname, typeofbill, billcat, UKPB_bill, UKPB_Act,
                RoyalAssent, RoyalAssentDate, lastchange, stage, numberofstages, firststagedate, laststagedate,
                firststagename, laststagename, sponsor1, sponsor2, sponsor1inst, sponsor2inst, parlagent, promotedby,
                lateststagename, lateststagedate, nextstagename, nextstagedate, billink1, billink2, billinkdate,
                billfiletitle, latestnews, summary, mpnameuseful, mpid_twfy, mpid_grdn, mpparty, mpmaj, mpentered,
                mpyearentered, mpconstituency, constid_grdn, mpproblem, numParas,numBodyParas,numScheduleParas,LGUKurl,
                DocYear,DocMainType,DocEnactmentDate,DocCat,ActName]
        writer1.writerow(row1)


        if billcat == 'PMB-C':
            MPs.append(sponsor1)
        elif billcat == 'PMB-L':
            Lords.append(sponsor1)
        print(' ')
        # note Guardian API key: 3zf84h96ezvzhfwrtw65nf2m