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
# Version Number
########
version = '10.0-b0.1.0'

'''
Copyright (c) 2016 Wugpodes

Permission is hereby granted, free of charge, to any person obtaining a copy of 
this software and associated documentation files (the "Software"), to deal in 
the Software without restriction, including without limitation the rights to 
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
of the Software, and to permit persons to whom the Software is furnished to do 
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN 
THE SOFTWARE.
'''

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
        text = '# '+sectionLink(item[i],item[0])+" ('''"\
                +str(item[index])+"''' days)\n"
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
        text = ":'''"+sectionLink(subsection,subsection)+"''' ("+n+")"
    else:
        n = str(nomsBySection[section][0])
        h = str(nomsBySection[section][1])
        r = str(nomsBySection[section][2])
        s = str(nomsBySection[section][3])
        text = "'''"+sectionLink(section,section)+"''' ("+n+")"
        if section=='Miscellaneous':
            text+='\n'
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
        text += '[[Image:Symbol neutral vote.svg|15px|2nd Opinion Requested]]'\
                +' x '+s+'\n'
    return(text)
    
def sectionLink(section,title):
    text='[[Wikipedia:Good article nominations#'+section+'|'+title+']]'
    return(text)
    
def printData(data, index):
    rText=''
    for i in range(len(data)):
        dataPoint = str(data[i][index])
        if i < 29:
            dataPoint+=', '
        rText+=dataPoint
    return(rText)
     
site = pywikibot.Site('en', 'wikipedia')
page = pywikibot.Page(site,'Wikipedia:Good article nominations')
fullText= page.text
fullText=fullText.split('\n')

#Compile regexes
##Finds GAN entries and returns time stamp, title, and the following line
entRegex = re.compile(
        r'\{\{GANentry.*?\|1\=(.*?)\|2=(\d+)'\
        +r'(?:.*?\[\[(?:(?:U|u)ser|(?:U|u)ser talk)\:(.*?)\|.*)?'\
        +r'(?:\}\} (.*?) )?(\d\d\:\d\d, \d+ .*? \d\d\d\d) \(UTC\)'
    )
backlogRegex = re.compile(r'(\d+) (.*?) (\d\d\d\d).*?(\d+) nom.*? (\d+)'\
                          +r'(?:(?:.*?On Hold.*?x (\d+))?'\
                          +r'(?:.*?Under.*?x (\d+))?(?:.*?2nd.*?x (\d+))?)')
sctRegex = re.compile(r'==+ (.*?) (==+)')
##Finds the Wikipedia UTC Timestamp
datRegex = re.compile(r', (\d+) (.*?) (\d\d\d\d)')

entry   = []
nomin   = []
onRev   = []
onHld   = []
waitg   = []
scnOp   = []
badNoms = []
toPrint = []

nomsBySection = {}
subSectDict = {}
nomsByNominator = {}

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
    if '==' in line:
        if '===' in line:
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
        if matches.group(3) != None:
            username = matches.group(3)
        elif matches.group(3) == None and matches.group(4) != None:
            username = matches.group(4)
        else:
            badNoms.append([matches.group(1),subSectName])
            username = 'Unknown'
        if username not in nomsByNominator:
            nomsByNominator[username]=[]
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
                    matches.group(5), # Timestamp
                    username          # Nominator's name
                  ]
        entry.append(entryData)
        nomin.append(entryData)
        if subSectName != None:
            sec = subSectName
        else:
            sec = sectName
        nomsByNominator[username].append([matches.group(1),sec])
#########################################################################
#   DATA FORMAT FOR ITEMS IN ARRAYS PRODUCED ABOVE
#   (entry,nomin,onHld,onRev,scnOp)
#       entryData[0] = Title of the nominated article
#       entryData[1] = Nomination number
#       entryData[2] = Section name
#       entryData[3] = Subsection name
#       entryData[4] = Timestamp
#       entryData[5] = Nominator's name
#       entryData[6] = The line following (not present in nomin or entry)
#########################################################################

#Get the date
today = date.today()

#Get backlog stats
noms = len(entry)
inac = len(nomin)
ohld = len(onHld)
orev = len(onRev)
scnd = len(scnOp)

rIndex = 8 # index number for appended days since action

#Get all unreviewed nominations older than 30 days
oldestnoms = nomin
oldestnoms = dateActions(oldestnoms,4)
topTen = []
oldestnoms=sortByKey(oldestnoms,6)
for i in range(10):
    topTen.append(oldestnoms[i])

#Get all nominations older than 30 days
entry = dateActions(entry,4)
oThirty=[]
for item in entry:
    if int(item[7]) >= 30:
        oThirty.append(item)
oThirty=sortByKey(oThirty,7)

#Get the nominations ON HOLD 7 days or longer
onHld=dateActions(onHld,rIndex-2)
oldOnHold=[]
for item in onHld:
    if int(item[rIndex]) >= 7:
        oldOnHold.append(item)
oldOnHold=sortByKey(oldOnHold,rIndex)

#Get the nominations ON REVIEW for 7 days or longer
onRev=dateActions(onRev,rIndex-2)
oldOnRev=[]
for item in onRev:
    if int(item[rIndex]) >= 7:
        oldOnRev.append(item)
oldOnRev=sortByKey(oldOnRev,rIndex)

#Get the nominations ON SECOND OPINION for 7 days or longer
scnOp=dateActions(scnOp,rIndex-2)
oldScnOp=[]
for item in scnOp:
    if int(item[rIndex]) >= 7:
        oldScnOp.append(item)
oldScnOp=sortByKey(oldScnOp,rIndex)

#Load report page (must be here because backlog report requires it be loaded)
page = pywikibot.Page(site,'Wikipedia:Good article nominations/Report')
archive = pywikibot.Page(site,'Wikipedia:Good article nominations/Report/'\
                              +'Backlog archive')

#Make Backlog report
backlogReport = []
for match in re.findall(r'(\d.*?\/>)',page.text):
    backlogReport.append(match+'\n')
curEntry = wikiTimeStamp()+' &ndash; '+str(noms)+' nominations outstanding; ' \
    + str(inac)+' not reviewed; [[Image:Symbol wait.svg|15px|On Hold]] x ' \
    + str(ohld)+'; [[Image:Searchtool.svg|15px|Under Review]] x '+str(orev) \
    + '; [[Image:Symbol neutral vote.svg|15px|2nd Opinion Requested]] x ' \
    + str(scnd)+'<br />\n'
backlogReport.insert(0,curEntry)
oldLine=backlogReport.pop()

#Make Backlog Chart
backlogEntry = archive.text.split('\n')
backlogEntry.reverse()
bklgData = backlogReport + backlogEntry[0:30-len(backlogReport)]
dayData=[]
i=0
for day in bklgData:
    dayMatch = backlogRegex.search(day)
    dayData.append([])
    for j in range(1,8):
        dayData[i].append(dayMatch.group(j))
    i+=1
chartOutput='<div style="float: right;">\n{{Graph:Chart|width=600|height=200|'\
             +'legend=Legend|type=line|xType=date|x='
for i in range(len(dayData)):
    dayStamp = ' '.join([dayData[i][0],dayData[i][1],dayData[i][2]])
    if i < 29:
        dayStamp+=', '
    chartOutput+=dayStamp
chartOutput+='|y1Title=Nominations Outstanding|y1='
chartOutput+=printData(dayData,3)
chartOutput+='}}\n'
chartOutput += '{{Graph:Chart|width=600|height=200|legend=Legend|'\
                +'type=stackedrect|xType=date|x='
for i in range(len(dayData)):
    dayStamp = ' '.join([dayData[i][0],dayData[i][1],dayData[i][2]])
    if i < 29:
        dayStamp+=', '
    chartOutput+=dayStamp
chartOutput+='|y1Title=Unreviewed|y1='
chartOutput+=printData(dayData,4)
chartOutput+='|y2Title=On Hold|y2='
chartOutput+=printData(dayData,5)
chartOutput+='|y3Title=On Review|y3='
chartOutput+=printData(dayData,6)
chartOutput+='|y4Title=Second Opinion|y4='
chartOutput+=printData(dayData,5)
chartOutput+='}}\n</div>\n'

#################
# Make the Page
#################

# Write Oldest nominations
report = ['{{/top}}\n\n',
          '== Oldest nominations ==\n',
          ":''List of the oldest ten nominations that have had no activity" \
          +"(placed on hold, under review or requesting a 2nd opinion)''\n",
    ]
report = appendUpdates(report,topTen,index=6,rev=False)
report+= ['\n',
          '== Backlog report ==\n',]
#Write chart
report.append(chartOutput)
# Write backlog report
for item in backlogReport:
    report.append(item)
report.append(":''Previous daily backlogs can be viewed at the" \
              +"[[/Backlog archive|backlog archive]].''\n\n")
# Write the exceptions report
#   Write reviews on hold for over 7 days       
report+= ['== Exceptions report ==\n',
          '=== Holds over 7 days old ===\n']
report=appendUpdates(report,oldOnHold,rIndex)
# Write nominations marked on review for over 7 days
report+=['\n',
        '=== Old reviews ===\n',
        ":''Nominations that have been marked under review for 7 days or "\
        +"longer.''\n"
    ]
report=appendUpdates(report,oldOnRev,rIndex)
# Write requests for second opinion older than 7 days
report+=[
    '\n',
    '=== Old requests for 2nd opinion ===\n',
    ":''Nominations that have been marked requesting a second opinion for 7 "\
    +"days or longer.''\n"
]
report=appendUpdates(report,oldScnOp,rIndex)
#Write all nominations older than one month
report+=[
    '\n',
    '=== Old nominations ===\n',
    ":''All nominations that were added 30 days ago or longer, regardless of "\
    +"other activity.''\n"
]
for item in oThirty:
    if item[4] != None: # If there is a subsection
        j = 3           #   use it
    else:               # otherwise
        j = 2           #   use section name
    # Add icons if nomination is on hold, review, etc
    if any(item[0] in i for i in onHld):
        text = '# [[Image:Symbol wait.svg|15px|On Hold]] '\
                +sectionLink(item[j],item[0])+" ('''"\
                +str(item[rIndex])+"''' days)\n"
    elif any(item[0] in i for i in onRev):
        text = '# [[Image:Searchtool.svg|15px|Under Review]] '\
                +sectionLink(item[j],item[0])+" ('''"\
                +str(item[rIndex])+"''' days)\n"
    elif any(item[0] in i for i in scnOp):
        text = '# [[Image:Symbol neutral vote.svg|15px|2nd Opinion Requested]]'\
                +sectionLink(item[j],item[0])+" ('''"\
                +str(item[rIndex])+"''' days)\n"
    else:
        text = '# '+sectionLink(item[j],item[0])+" ('''"\
                +str(item[rIndex-1])+"''' days)\n"
    report.append(text)

# Malformed Noms
report.append('=== Malformed nominations ===\n')
if len(badNoms) < 1:
    report.append('None\n')
else:
    if len(badNoms) > 1:
        report.append(":''There are currently "+str(len(badNoms))\
                      +" malformed nominations''\n")
    elif len(badNoms) == 1:
        report.append(":''There is currently 1 malformed nomination''\n")
    for item in badNoms:
        text= '# '+sectionLink(item[1],item[0])+"\n"
        report.append(text)

# Counts and outputs nominators with multiple nominations
report.append('=== Nominators with multiple nominations ===\n')
multipleNomsOut = []
mnOutput = []
for user in nomsByNominator:
    if len(nomsByNominator[user]) > 1:
        multipleNomsOut.append([
            user,
            len(nomsByNominator[user]),nomsByNominator[user]
        ])
        line = ';'+user+' ('+str(len(nomsByNominator[user]))+')\n'
nomsSort = sortByKey(multipleNomsOut,1)
for item in nomsSort:
    line = ';'+item[0]+' ('+str(item[1])+')'
    mnOutput.append(line)
    line = ':'
    counter=0
    for mnNom in item[2]:
        if counter != 0:
            line+=', '
        line += sectionLink(mnNom[1],mnNom[0])
        counter+=1
    line+='\n'
    mnOutput.append(line)
report += mnOutput
        
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
# Writes the summary report
report.append('== Summary ==\n')
report+=summary
            
# A relic of the old way, in memoriam WugBot-v0.0
toPrint=report
# Sign it
toPrint.append('<!-- Updated at '+wikiTimeStamp()+' by' \
    +' WugBot v'+version+' -->\n')

# Determine if the bot should write to a live page or the test page. Defaults to 
#     test page. Value of -1 tests backlog update (not standard because the file
#     size is very big).
if live == 1:
    page.text=''.join(toPrint)
    page.save('Updating exceptions report, WugBot v'+version)
    page = pywikibot.Page(site,'Wikipedia:Good article nominations/Report/'\
                                +'Backlog archive')
    page.text+=oldLine
    page.save('Update of GAN report backlog, WugBot v'+version)
else:
    page = pywikibot.Page(site,'User:Wugapodes/GANReportBotTest')
    page.text=''.join(toPrint)
    if live == 2:
    	message='Daily test of beta version. Output of v'+version
    else:
    	message='Testing expanded reporting'
    page.save(message)
    if live==-1:
        page = pywikibot.Page(site,
            'User:Wugapodes/GANReportBotTest/Backlog archive')
        testText=page.text
        page.text=testText
        page.save('Testing backlog report updating')
    
print(wikiTimeStamp())
