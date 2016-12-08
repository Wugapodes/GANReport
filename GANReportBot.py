#!/usr/bin/python

import pywikibot
import re
from datetime import date
import datetime

def monthConvert(name):
    if type(name) is str:
        if name == "January": return 1
        elif name == "February": return 2
        elif name == "March": return 3
        elif name == "April": return 4
        elif name == "May": return 5
        elif name == "June": return 6
        elif name == "July": return 7
        elif name == "August": return 8
        elif name == "September": return 9
        elif name == "October": return 10
        elif name == "November": return 11
        elif name == "December": return 12
        else: raise ValueError
    elif type(name) is int:
        if name == 1:return('January')
        elif name == 2:return('February')
        elif name == 3:return('March')
        elif name == 4:return('April')
        elif name == 5:return('May')
        elif name == 6:return('June')
        elif name == 7:return('July')
        elif name == 8:return('August')
        elif name == 9:return('September')
        elif name == 10:return('October')
        elif name == 11: return('November')
        elif name == 12: return('December')
        else: raise ValueError

def appendUpdates(toprint,updates,index=2):
    for item in updates:
        text = '# [['+item[0]+"]] ('''"+str(item[index])+"''' days)\n"
        toprint.append(text)
    return(toprint)

def dateActions(nominList,index):
    for item in nominList:
        iMatch = datRegex.search(item[index])
        day = int(iMatch.group(1))
        month = monthConvert(str(iMatch.group(2)))
        year = int(iMatch.group(3))
        d0 = date(year, month, day)
        delta = today-d0
        item.append(delta.days)
        #print(delta.days,'days')
    return(nominList)

def sortByKey(nominList,index):
    nominList.sort(key=lambda x: x[index],reverse=True)
    return(nominList)

def wikiTimeStamp():
    stamp = str(datetime.datetime.utcnow().hour)+        ':'+str(datetime.datetime.utcnow().minute).zfill(2)+        ', '+        str(datetime.datetime.utcnow().day)+        ' '+        monthConvert(datetime.datetime.utcnow().month)+        ' '+        str(datetime.datetime.utcnow().year)
    return(stamp)

#with open('/data/project/ganreportbot/pywikibot/limit.txt','r') as f:
#    counter = int(f.read().rstrip())
#if counter >= 7:
#    exit()

site = pywikibot.Site('en', 'wikipedia')
page = pywikibot.Page(site,'Wikipedia:Good article nominations')

#Compile regexes
##Finds GAN entries and returns time stamp, title, and the following line
entRegex = re.compile(r'\{\{GANnomin.*?\|1\=(.*?)\|.*?(\d\d\:\d\d, \d+ .*? \d\d\d\d) \(UTC\)\n(.*)\n')
##Finds the Wikipedia UTC Timestamp
datRegex = re.compile(r', (\d+) (.*?) (\d\d\d\d)')

entry   = []
nomin   = []
onRev   = []
onHld   = []
waitg   = []
scnOp   = []
toPrint = []

#Find the Nomination entries and then sort them into on hold, 2nd opinion, or on revivew
for match in entRegex.findall(page.text):
    entry.append([match[0],match[1]])
    if 'GAReview' in match[2]:
        if 'on hold' in match[2]:
            onHld.append([match[0],match[1],match[2]])
        elif '2nd opinion' in match[2]:
            scnOp.append([match[0],match[1],match[2]])
        else:
            onRev.append([match[0],match[1],match[2]])
    else:
        nomin.append([match[0],match[1]])

#Get the date
today = date.today()

#Get backlog stats
noms = len(entry)
inac = len(nomin)
ohld = len(onHld)
orev = len(onRev)
scnd = len(scnOp)

#Get all nominations older than 30 days
entry = dateActions(entry,1)
topTen = []
entry=sortByKey(entry,2)
while len(topTen) < 10:
    topTen.append(entry.pop(0))

#Get unactioned nominations older than 30 days
nomin = dateActions(nomin,1)
oThirty=[]
for item in nomin:
    if int(item[2]) >= 30:
        oThirty.append(item)
oThirty=sortByKey(oThirty,2)

#Get the nominations ON HOLD 7 days or longer
onHld=dateActions(onHld,2)
oldOnHold=[]
for item in onHld:
    if int(item[3]) >= 7:
        oldOnHold.append(item)
oldOnHold=sortByKey(oldOnHold,3)

#Get the nominations ON REVIEW for 7 days or longer
onRev=dateActions(onRev,2)
oldOnRev=[]
for item in onRev:
    if int(item[3]) >= 7:
        oldOnRev.append(item)
oldOnRev=sortByKey(oldOnRev,3)


# In[602]:

#Get the nominations ON SECOND OPINION for 7 days or longer
scnOp=dateActions(scnOp,2)
oldScnOp=[]
for item in scnOp:
    if int(item[3]) >= 7:
        oldScnOp.append(item)
oldScnOp=sortByKey(oldScnOp,3)

page = pywikibot.Page(site,'Wikipedia:Good article nominations/Report')

#Make Backlog report
backlogReport = []
for match in re.findall(r'(\d.*?\/>)',page.text):
    backlogReport.append(match.group(0))
curEntry = wikiTimeStamp()+' &ndash; '+str(noms)+' nominations outstanding; ' \
    + str(inac)+' not reviewed; [[Image:Symbol wait.svg|15px|On Hold]] x ' \
    + str(ohld)+'; [[Image:Searchtool.svg|15px|Under Review]] x '+str(orev) \
    + '; [[Image:Symbol neutral vote.svg|15px|2nd Opinion Requested]] x ' \
    + str(scnd)+'<br />'
backlogReport.insert(0,curEntry)
backlogReport.pop()

#Make the Page
report = ['{{/top}}\n\n',
          '== Oldest nominations ==\n',
          ":''List of the oldest ten nominations that have had no activity \
          (placed on hold, under review or requesting a 2nd opinion)''\n",
    ]
report = appendUpdates(report,topTen,index=2)
report+= ['\n',
          '== Backlog report ==\n',]

for item in backlogReport:
    report.append(item)
    
report+= [":''Previous daily backlogs can be viewed at the \
          [[/Backlog archive|backlog archive]].''\n\n",
          '== Exceptions report ==\n',
          '=== Holds over 7 days old ===\n']
report=appendUpdates(report,oldOnHold,index=3)
report+=[
        '\n',
        '=== Old reviews ===\n',
        ":''Nominations that have been marked under review for 7 days or longer.'''\n"
    ]
report=appendUpdates(report,oldOnRev,3)
report+=[
    '\n',
    '=== Old requests for 2nd opinion ===\n',
    ":''Nominations that have been marked requesting a second opinion for 7 days or longer.''\n"
]
report=appendUpdates(report,oldScnOp,3)
report+=[
    '\n',
    '=== Old nominations ===\n',
    ":''All nominations that were added 30 days ago or longer, regardless of other activity.''\n"
]
report=appendUpdates(report,oThirty,2)

#Get unchanged portions of the page and organize the page
passed = 0
toPrint+=report
toPrint.append('<!-- The above sections updated at '+wikiTimeStamp()+' by \
    WugBot -->\n')
x=page.text.split('\n')
for line in x:
    if 'The above sections updated at' in line:
        passed=1
        toPrint.append(line+'\n')
    elif passed==1:
        toPrint.append(line+'\n')
    else:
        continue

#Write the page
page = pywikibot.Page(site,'User:Wugapodes/GANReportBotTest')
page.text=''.join(toPrint)
page.save('Testing expanded reporting')
#page.save('Updating exceptions report')
print(wikiTimeStamp())

#with open('/data/project/ganreportbot/pywikibot/limit.txt','w') as f:
#    f.write(counter+1)
