
# coding: utf-8

# In[588]:

import pywikibot
import re
from datetime import date
import datetime


# In[589]:

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


# In[590]:

def appendUpdates(toprint,updates,index=2):
    for item in updates:
        text = '# [['+item[0]+"]] ('''"+str(item[index])+"''' days)\n"
        toprint.append(text)
    return(toprint)


# In[591]:

def dateActions(entryList,index):
    for item in entryList:
        iMatch = datRegex.search(item[index])
        day = int(iMatch.group(1))
        month = int(monthConvert(iMatch.group(2)))
        year = int(iMatch.group(3))
        d0 = date(year, month, day)
        delta = today-d0
        item.append(delta.days)
        #print(delta.days,'days')
    return(entryList)


# In[592]:

def sortByKey(entryList,index):
    entryList.sort(key=lambda x: x[index],reverse=True)
    return(entryList)


# In[593]:

def wikiTimeStamp():
    stamp = str(datetime.datetime.utcnow().hour)+        ':'+str(datetime.datetime.utcnow().minute)+        ', '+        str(datetime.datetime.utcnow().day)+        ' '+        monthConvert(datetime.datetime.utcnow().month)+        ' '+        str(datetime.datetime.utcnow().year)
    return(stamp)


# In[594]:

site = pywikibot.Site('en', 'wikipedia')
page = pywikibot.Page(site,'Wikipedia:Good article nominations')


# In[595]:

#Compile regexes
##Finds GAN entries and returns time stamp, title, and the following line
entRegex = re.compile(r'\{\{GANentry.*?\|1\=(.*?)\|.*?(\d\d\:\d\d, \d+ .*? \d\d\d\d) \(UTC\)\n(.*)\n')
##Finds the Wikipedia UTC Timestamp
datRegex = re.compile(r', (\d+) (.*?) (\d\d\d\d)')


# In[596]:

entry   = []
onRev   = []
onHld   = []
waitg   = []
scnOp   = []
toPrint = []


# In[597]:

#Find the Nomination entries and then sort them into on hold, 2nd opinion, or on revivew
for match in entRegex.findall(page.text):
    if 'GAReview' in match[2]:
        if 'on hold' in match[2]:
            onHld.append([match[0],match[1],match[2]])
        elif '2nd opinion' in match[2]:
            scnOp.append([match[0],match[1],match[2]])
        else:
            onRev.append([match[0],match[1],match[2]])
    else:
        entry.append([match[0],match[1]])


# In[598]:

#Get the date
today = date.today()


# In[599]:

#Get nominations older than 30 days
entry = dateActions(entry,1)
oThirty=[]
for item in entry:
    if int(item[2]) >= 30:
        oThirty.append(item)
oThirty=sortByKey(oThirty,2)


# In[600]:

#Get the nominations ON HOLD 7 days or longer
onHld=dateActions(onHld,2)
oldOnHold=[]
for item in onHld:
    if int(item[3]) >= 7:
        oldOnHold.append(item)
oldOnHold=sortByKey(oldOnHold,3)


# In[601]:

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


# In[603]:

#Make the Page
report = ['== Exceptions report ==\n',
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


# In[604]:

page = pywikibot.Page(site,'Wikipedia:Good article nominations/Report')
x=page.text.split('\n')


# In[605]:

passed = 0


# In[606]:

for line in x:
    if '== Exceptions report ==' not in line and passed == 0:
        toPrint.append(line+'\n')
    elif '== Exceptions report ==' in line:
        passed=1
        toPrint.append('<!-- The below sections updated at '+wikiTimeStamp()+' by WugBot -->')
        toPrint+=report
        toPrint.append('<!-- The above sections updated at '+wikiTimeStamp()+' by WugBot -->')
    elif '=== Malformed nominations ===' in line and passed == 1:
        passed = 2
        toPrint.append(line+'\n')
    elif passed == 1:
        continue
    elif passed == 2:
        toPrint.append(line+'\n')


# In[607]:

page = pywikibot.Page(site,'User:Wugapodes/GANReportBotTest')
page.text=''.join(toPrint)
page.save(summary='Testing Bot in own userspace. See [[WP:BRFA]] for comments.')


# In[ ]:



