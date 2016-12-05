
# coding: utf-8

# In[181]:

import pywikibot
import re
from datetime import date
import datetime


# In[195]:

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


# In[158]:

def appendUpdates(toprint,updates):
    for item in updates:
        text = '# [['+item[0]+"]] ('''"+str(item[2])+"''' days)"
        toprint.append(text)
    return(toprint)


# In[159]:

site = pywikibot.Site('en', 'wikipedia')
page = pywikibot.Page(site,'Wikipedia:Good article nominations')


# In[160]:

entRegex = re.compile(r'\{\{GANentry.*?\|1\=(.*?)\|.*?(\d\d\:\d\d, \d+ .*? \d\d\d\d) \(UTC\)\n(.*)\n')
datRegex = re.compile(r', (\d+) (.*?) (\d\d\d\d)')


# In[161]:

entry   = []
onRev   = []
onHld   = []
waitg   = []
scnOp   = []
oThirty = []
toPrint = []


# In[162]:

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


# In[163]:

today = date.today()


# In[164]:

for item in entry:
    iMatch = datRegex.search(item[1])
    day = int(iMatch.group(1))
    month = int(monthConvert(iMatch.group(2)))
    year = int(iMatch.group(3))
    d0 = date(year, month, day)
    delta = today-d0
    item.append(delta.days)
    print(delta.days,'days')


# In[165]:

for item in entry:
    if int(item[2]) >= 30:
        oThirty.append(item)


# In[166]:

oThirty.sort(key=lambda x: x[2],reverse=True)


# In[167]:

page = pywikibot.Page(site,'Wikipedia:Good article nominations/Report')


# In[168]:

x=page.text.split('\n')


# In[169]:

passed = 0


# In[170]:

for line in x:
    if '=== Old nominations ===' not in line and passed == 0:
        toPrint.append(line)
    elif '=== Old nominations ===' in line:
        passed=1
        toPrint.append(line)
        toPrint.append(":''All nominations that were added 30 days ago or longer, regardless of other activity.''")
        toPrint=appendUpdates(toPrint,oThirty)
    elif '===' in line and passed == 1:
        passed = 2
        toPrint.append(line)
    elif passed == 1:
        continue
    elif passed == 2:
        toPrint.append(line)


# In[204]:

toPrint.pop()
toPrint.append('<!-- Partially updated at '+
               str(datetime.datetime.utcnow().hour)+':'+str(datetime.datetime.utcnow().minute)+', '+str(datetime.datetime.utcnow().day)+' '+monthConvert(datetime.datetime.utcnow().month)+' '+str(datetime.datetime.utcnow().year)+
              ' by WugBot-->')


# In[205]:

toPrint

