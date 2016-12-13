#!/usr/bin/python

import pywikibot
import re
from datetime import date
import datetime

########
# Changing this to 1 makes your changes live on the report page, do not set to
# live mode unless you have been approved for bot usage. Do not merge commits 
# where this is not default to 0
########
live = 0
########

def monthConvert(name):
    '''
    Takes in either the name of the month or the number of the month and returns
    the opposite. An input of str(July) would return int(7) while an input of
    int(6) would return str(June).
    Takes:   int OR string
    Returns: string OR int
    '''
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

def appendUpdates(toprint,updates,index=3,rev=True):
    '''
    Takes an iterable array and the output array and returns teh output array 
    appended with the marked up iterable array.
    '''
    for item in updates:
        if item[4] != None:
            i = 3
        else:
            i = 2
        text = '# [[Wikipedia:Good article nominations#'+item[i]+"|" \
               +item[0]+"]] ('''"+str(item[index])+"''' days)\n"
        toprint.append(text)
    return(toprint)

def dateActions(nominList,index):
    '''
    For a given list, it finds the embedded date, how many days ago that date is
    from today, and appends that number to the list. It then returns the list
    '''
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
    '''
    Sorts a given list by a given index in a sublist, largest first
    '''
    nominList.sort(key=lambda x: x[index],reverse=True)
    return(nominList)

def wikiTimeStamp():
    '''
    Returns the current time stamp in the style of wikipedia signatures.
    '''
    stamp = str(datetime.datetime.utcnow().hour).zfill(2)+':'\
    +str(datetime.datetime.utcnow().minute).zfill(2)+', '\
    +str(datetime.datetime.utcnow().day)+' '\
    +monthConvert(datetime.datetime.utcnow().month)+' '\
    +str(datetime.datetime.utcnow().year)+' (UTC)'
    return(stamp)
    
def updateSummary(section,subsection=False):
    global nomsBySection
    global subSectDict
    if subsection:
        i=4
        n = str(nomsBySection[section][i][subsection][0])
        h = str(nomsBySection[section][i][subsection][1])
        r = str(nomsBySection[section][i][subsection][2])
        s = str(nomsBySection[section][i][subsection][3])
        text = ":'''[[Wikipedia:Good article nominations#"+subsection+"|" \
               +subsection+"]]''' ("+n+")"
    else:
        n = str(nomsBySection[section][0])
        h = str(nomsBySection[section][1])
        r = str(nomsBySection[section][2])
        s = str(nomsBySection[section][3])
        text = "'''[[Wikipedia:Good article nominations#"+section+"|" \
               +section+"]]''' ("+n+")"
    if int(h)+int(r)+int(s)>0:
        text+=": "
    else:
        text+="\n"
    if int(h) > 0:
        text += '[[Image:Symbol wait.svg|15px|On Hold]] x '+h
        if int(r)>0 or int(s)>0:
            text+='; '
        else:
            text+='\n'
    if int(r) > 0:
        text += '[[Image:Searchtool.svg|15px|Under Review]] x '+r
        if int(s)>0:
            text+='; '
        else:
            text+='\n'
    if int(s) > 0:
        text += '[[Image:Symbol neutral vote.svg|15px|2nd Opinion Requested]] x '+s+'\n'
    return(text)
     
site = pywikibot.Site('en', 'wikipedia')
page = pywikibot.Page(site,'Wikipedia:Good article nominations')
fullText= page.text
fullText=fullText.split('\n')

#Compile regexes
##Finds GAN entries and returns time stamp, title, and the following line
entRegex = re.compile(
        r'\{\{GANentry.*?\|1\=(.*?)\|2=(\d+).*?(\d\d\:\d\d, \d+ .*? \d\d\d\d)'\
        +r' \(UTC\)'
    )
sctRegex = re.compile(r'==+ (.*?) (==+)')
##Finds the Wikipedia UTC Timestamp
datRegex = re.compile(r', (\d+) (.*?) (\d\d\d\d)')

entry   = []
nomin   = []
onRev   = []
onHld   = []
waitg   = []
scnOp   = []
toPrint = []

nomsBySection = {}
subSectDict = {}

'''
FOR LOOP DOCUMENTATION

The following for loop goes line by line through the nomination page. It checks 
to see: 
    If the line is a section header:
        If the line is a subsection header:
            then it updates the subsection dictionaries
        If it is not a subsection (i.e. only a section):
            then it updates the section dictionary
    Else if it is a GANEntry template:
        stores the regex output in matches
    Else if it is none of the above nor a GAReview it skips the line
It then checks (see note below):
    If it is a GAReview template:
        then it sorts the associated nomination
    Else it updates the entry data and adds it to entry and nomin

NOTE: This runs backwards. GAReview templates only come /after/ a nomination 
so a nomination line will be added to entry and nomin and the next line, if it 
is not being worked on (ie no GAReview template) then it will overwrite the 
previous nomination data. But if there is a GAReview template it is /not/ 
overwritten and is used to sort the previous nomination into the proper place 
and removes it from nomin (because it's on review)
'''
for line in fullText:
    if '==' in line: #Checks to see if section
        if '===' in line: #Checks to see if subsection
            subSectName=re.search(sctRegex,line).group(1)
            # array nums represent: 
            # [# of noms, # on hold, # on rev, # 2nd opinion]
            nomsBySection[sectName][4][subSectName]=[0,0,0,0]
            # keeps track of the indices of subsections in the data structure
            subSectDict[subSectName]=len(nomsBySection[sectName])-1
        else:
            result=re.search(sctRegex,line)
            sectName=result.group(1)
            # array nums represent: 
            # [# of noms, # on hold, # on rev, # 2nd opinion]
            nomsBySection[sectName]=[0,0,0,0,{}]
            subSectName=None
        continue
    elif 'GANentry' in line:
        matches=entRegex.search(line)
    elif 'GAReview' not in line:
        continue
    if 'GAReview' in line:
        nomin.pop()
        entryData.append(line)
        if 'on hold' in line:
            onHld.append(entryData)
        elif '2nd opinion' in line:
            scnOp.append(entryData)
        else:
            onRev.append(entryData)
    else:
        entryData=[
                    matches.group(1), # Title of the nominated article
                    matches.group(2), # Nomination number
                    sectName,         # Section name
                    subSectName,      # Subsection name
                    matches.group(3)  # Timestamp
                  ]
        entry.append(entryData)
        nomin.append(entryData)
#########################################################################
#   DATA FORMAT FOR ITEMS IN ARRAYS PRODUCED ABOVE
#   (entry,nomin,onHld,onRev,scnOp)
#       entryData[0] = Title of the nominated article
#       entryData[1] = Nomination number
#       entryData[2] = Section name
#       entryData[3] = Subsection name
#       entryData[4] = Timestamp
#       entryData[5] = The line following (not present in nomin or entry)
#########################################################################

#Get the date
today = date.today()

#Get backlog stats
noms = len(entry)
inac = len(nomin)
ohld = len(onHld)
orev = len(onRev)
scnd = len(scnOp)

rIndex = 7

#Get all unreviewed nominations older than 30 days
oldestnoms = nomin
oldestnoms = dateActions(oldestnoms,4)
topTen = []
oldestnoms=sortByKey(oldestnoms,5)
while len(topTen) < 10:
    topTen.append(oldestnoms.pop(0))

#Get all nominations older than 30 days
entry = dateActions(entry,4)
oThirty=[]
for item in entry:
    if int(item[6]) >= 30:
        oThirty.append(item)
oThirty=sortByKey(oThirty,6)

#Get the nominations ON HOLD 7 days or longer
onHld=dateActions(onHld,5)
oldOnHold=[]
for item in onHld:
    if int(item[rIndex]) >= 7:
        oldOnHold.append(item)
oldOnHold=sortByKey(oldOnHold,rIndex)

#Get the nominations ON REVIEW for 7 days or longer
onRev=dateActions(onRev,5)
oldOnRev=[]
for item in onRev:
    if int(item[rIndex]) >= 7:
        oldOnRev.append(item)
oldOnRev=sortByKey(oldOnRev,rIndex)

#Get the nominations ON SECOND OPINION for 7 days or longer
scnOp=dateActions(scnOp,5)
oldScnOp=[]
for item in scnOp:
    if int(item[rIndex]) >= 7:
        oldScnOp.append(item)
oldScnOp=sortByKey(oldScnOp,rIndex)

page = pywikibot.Page(site,'Wikipedia:Good article nominations/Report')

#Make Backlog report
backlogReport = []
for match in re.findall(r'(\d.*?\/>)',page.text):
    backlogReport.append(match+'\n')
curEntry = wikiTimeStamp()+' &ndash; '+str(noms)+' nominations outstanding; ' \
    + str(inac)+' not reviewed; [[Image:Symbol wait.svg|15px|On Hold]] x ' \
    + str(ohld)+'; [[Image:Searchtool.svg|15px|Under Review]] x '+str(orev) \
    + '; [[Image:Symbol neutral vote.svg|15px|2nd Opinion Requested]] x ' \
    + str(scnd)+'<br />'
backlogReport.insert(0,curEntry)
oldLine=backlogReport.pop()

#Make the Page
report = ['{{/top}}\n\n',
          '== Oldest nominations ==\n',
          ":''List of the oldest ten nominations that have had no activity" \
          +"(placed on hold, under review or requesting a 2nd opinion)''\n",
    ]
report = appendUpdates(report,topTen,index=5,rev=False)
report+= ['\n',
          '== Backlog report ==\n',]

for item in backlogReport:
    report.append(item)
    
report+= [":''Previous daily backlogs can be viewed at the \
          [[/Backlog archive|backlog archive]].''\n\n",
          '== Exceptions report ==\n',
          '=== Holds over 7 days old ===\n']
report=appendUpdates(report,oldOnHold,rIndex)
report+=[
        '\n',
        '=== Old reviews ===\n',
        ":''Nominations that have been marked under review for 7 days or "\
        +"longer.''\n"
    ]
report=appendUpdates(report,oldOnRev,rIndex)
report+=[
    '\n',
    '=== Old requests for 2nd opinion ===\n',
    ":''Nominations that have been marked requesting a second opinion for 7 "\
    +"days or longer.''\n"
]
report=appendUpdates(report,oldScnOp,rIndex)
report+=[
    '\n',
    '=== Old nominations ===\n',
    ":''All nominations that were added 30 days ago or longer, regardless of "\
    +"other activity.''\n"
]
for item in oThirty:
    if item[4] != None:
        j = 3
    else:
        j = 2
    if any(item[0] in i for i in onHld):
        text = '# [[Image:Symbol wait.svg|15px|On Hold]] [[Wikipedia:Good '\
               +'article nominations#'+item[j]+"|"+item[0]+"]] ('''"\
               +str(item[6])+"''' days)\n"
    elif any(item[0] in i for i in onRev):
        text = '# [[Image:Searchtool.svg|15px|Under Review]] [[Wikipedia:Good '\
               +'article nominations#'+item[j]+"|"+item[0]+"]] ('''"\
               +str(item[6])+"''' days)\n"
    elif any(item[0] in i for i in scnOp):
        text = '# [[Image:Symbol neutral vote.svg|15px|2nd Opinion Requested]]'\
                +'[[Wikipedia:Good article nominations#'+item[j]+"|"+item[0]\
                +"]] ('''"+str(item[6])+"''' days)\n"
    else:
        text = '# [[Wikipedia:Good article nominations#'+item[j]+"|"+item[0]\
                +"]] ('''"+str(item[6])+"''' days)\n"
    report.append(text)

# Counts up all the noms, holds, reviews, and 2nd opinions in each section and
#   iterates the counter in the nomsBySection datastructure
for item in entry:
    if item[2] in nomsBySection and item[3] == None:
        nomsBySection[item[2]][0]+=1
        if any(item[0] in i for i in onHld):
            nomsBySection[item[2]][1]+=1
        elif any(item[0] in i for i in onRev):
            nomsBySection[item[2]][2]+=1
        elif any(item[0] in i for i in scnOp):
            nomsBySection[item[2]][1]+=1
    elif item[3] in subSectDict:
        index=4
        nomsBySection[item[2]][index][item[3]][0]+=1
        if any(item[0] in i for i in onHld):
            nomsBySection[item[2]][index][item[3]][1]+=1
        elif any(item[0] in i for i in onRev):
            nomsBySection[item[2]][index][item[3]][2]+=1
        elif any(item[0] in i for i in scnOp):
            nomsBySection[item[2]][index][item[3]][3]+=1
    else:
        print(item)
        raise TypeError('Nominations must have a section or subsection')

# Creates the summary report by iterating over the nomsBySection data structure
sectionNameList=[]
subsectionDict={}
for key in nomsBySection:
    sectionNameList.append(key)
    subsectionList=[]
    for subkey in nomsBySection[key][4]:
        subsectionList.append(subkey)
    if subsectionList != []:
        subsectionList.sort()
    subsectionDict[key]=subsectionList
summary = []
sectionNameList.sort()
for section in sectionNameList:
    summary.append(updateSummary(section))
    if subsectionDict[section] != [] :
        for subsection in subsectionDict[section]:
            summary.append(updateSummary(section,subsection))

#Get unchanged portions of the page and organize the page
passed = 0
toPrint+=report
toPrint.append('<!-- The above sections updated at '+wikiTimeStamp()+' by' \
    +' WugBot -->\n')
x=page.text.split('\n')
for line in x:
    if 'The above sections updated at' in line:
        passed=1
    elif passed==1 and '= Summary =' not in line:
        toPrint.append(line+'\n')
    elif '= Summary =' in line:
        toPrint.append('<!-- The following sections updated at '\
                       +wikiTimeStamp()+' by'+' WugBot -->\n')
        toPrint.append('== Summary==\n')
        toPrint+=summary
        passed=2
    else:
        continue

# Determine if the bot should write to a live page or the test page. Defaults to 
#     test page. Value of -1 tests backlog update (not standard because the file
#     size is very big).
if live == 1:
    page.text=''.join(toPrint)
    page.save('Updating exceptions report')
    page = pywikibot.Page(site,'Wikipedia:Good article nominations/Report/'\
                                +'Backlog archive')
    page.text+='<br />\n'
    page.text+=oldLine
    page.save('Update of GAN report backlog')
else:
    page = pywikibot.Page(site,'User:Wugapodes/GANReportBotTest')
    page.text=''.join(toPrint)
    page.save('Testing expanded reporting')
    if live==-1:
        page = pywikibot.Page(site,'User:Wugapodes/GANReportBotTest/'\
                                    +'Backlog archive')
        testText=page.text
        page.text=testText
        page.save('Testing backlog report updating')
    
print(wikiTimeStamp())
