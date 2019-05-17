#!/usr/bin/python

import pywikibot
import re
from datetime import date
from datetime import timedelta
from datetime import datetime as dt
import datetime
import logging
import sys

########
# Changing this to 1 makes your changes live on the report page, do not set to
# live mode unless you have been approved for bot usage. Do not merge commits
# where this is not default to 0
########
live = 0
########
# Version Number
########
version = '2.0.0-dev'
########
# Logging
########
if live == 1:
    logger = logging.getLogger('GANRB')
    fh = logging.FileHandler('GANRB.log')
    config_fname = './GANRB.log'
else:
    logger = logging.getLogger('GANRB.beta')
    fh = logging.FileHandler('GANRB.beta.log')
    config_fname = './GANRB_beta.log'
logger.setLevel(logging.DEBUG)
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
# create formatter and add it to the handlers
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=config_fname,
                    filemode='w')
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

entRegex = re.compile(
    r'{{GANentry.*?\|1=(.*?)\|2=(\d+).*?}}\s*(.*?) (\d\d\:\d\d, \d+ .*? \d\d\d\d) \(UTC\)'
    )
reviewRegex = re.compile(
    r'{{GAReview.*?}}\s*.*?\[\[User\:(.*?)(?:\||\]\]).*? (\d\d\:\d\d, \d+ .*? \d\d\d\d) \(UTC\)'
    )
    
'''
Copyright (c) 2019 Wugpodes

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

class NomPage:
    ##Finds GAN entries and returns time stamp, title, and the following line
    def __init__(self,text):
        global live
        if live == 1:
            self.logger = logging.getLogger('GANRB.NomPage')
        else:
            self.logger = logging.getLogger('GANRB.beta.NomPage')
        self.logger.info("Initializing NomPage object")
        self.raw_text = text
        self.text = text.split("\n")
        self.section = []
        self.stats = {
            'noms' : 0,
            'inac' : 0,
            'ohld' : 0,
            'orev' : 0,
            'scnd' : 0,
        }

    def parse(self,text=None, organize=True, noms=True):
        log = self.logger
        log.info("Parsing nomination page")
        if text == None:
            text = self.text
        for line in text:
            log.debug(line)
            if '==' in line:  # If line is a (sub-)section heading...
                line = line.strip()
                if '===' in line:  # If line is a subsection heading...
                    log.info("Subsection found: "+line.strip('=').strip())
                    subsec = SubSection(line.strip('=').strip(),c_sec)
                    self.section[-1].subsections.append(subsec)
                else: # If line is a section heading...
                    log.info("Section found: "+line.strip('=').strip())
                    sec = Section(line.strip('=').strip())
                    self.section.append(sec)
                c_sec = self.section[-1]
                continue
            elif 'GANentry' in line:  # If line is a GA nom...
                c_sub = c_sec.subsections[-1]
                matches=entRegex.search(line)
                entry = Entry(matches,line,c_sub.name)
                c_sub.entries.append(entry)
            elif 'GAReview' in line:  # If a review template...
                c_entry = c_sec.subsections[-1].entries[-1]
                if 'on hold' in line:
                    c_entry.add_review('H',line)
                elif '2nd opinion' in line:
                    c_entry.add_review('2',line)
                else: # Otherwise it's under review.
                    c_entry.add_review('R',line)
        if organize:
            self.organize_noms()
        if noms:
            try:
                self.nominator_stats()
            except AttributeError as e:
                log.error("Cannot get nominator stats without" \
                                + "organizing nominations")

    def organize_noms(self):
        log = self.logger
        log.info("Organizing nominations")
        noms = []
        badnoms = []
        for sec in self.section:
            for subsec in sec.subsections:
                for entry in subsec.entries:
                    if not entry.bad:
                        noms.append(entry)
                    else:
                        badnoms.append(entry)
        noms.sort(key=lambda x: x.timestamp)
        unrev = [x for x in noms if x.status == None]
        unrev.sort(key=lambda x: x.timestamp)
        self.stats['noms'] = len(noms)
        self.stats['inac'] = len(unrev)
        self.stats['ohld'] = len([x for x in noms if x.status == 'H'])
        self.stats['orev'] = len([x for x in noms if x.status == 'R'])
        self.stats['scnd'] = len([x for x in noms if x.status == '2'])
        cut = dt.utcnow() - timedelta(30)
        overThirty = [x for x in noms if x.timestamp < cut]
        oldestnoms = [x for x in unrev if x.timestamp < cut]
        oldestnoms.sort(key=lambda x: x.timestamp)
        oldestTen = oldestnoms[:10]
        cut = dt.utcnow() - timedelta(7)
        oldHolds = [x for x in noms if x.r_timestamp < cut and x.status == 'H']
        oldRevs = [x for x in noms if x.r_timestamp < cut and x.status == 'R']
        oldScnd = [x for x in noms if x.r_timestamp < cut and x.status == '2']
        self.nominations = noms  # All nominations regardless of activity.
        self.unreviewed = unrev  # Nominations not under review.
        self.overThirty = overThirty # All nominations older than 30 days
        self.oldestTen = oldestTen # The ten oldest unreviewed nomination
        self.oldUnreviewed = oldestnoms # Unreviewed nominations over 30 days.
        self.oldOnHold = oldHolds
        self.oldReviews = oldRevs
        self.oldSecondOp = oldScnd
        self.badNoms = badnoms

    def nominator_stats(self):
        """Assumes self.organize_noms() has already been run."""
        log = self.logger
        log.info("Calculating nominator stats")
        nominations = self.nominations
        nominators = {}
        nom_list = []
        for entry in nominations:
            nom = entry.nominator
            if nom not in nominators:
                nominators[nom] = Nominator(nom)
            n_obj = nominators[nom]
            n_obj.add(entry)
        self.nominators = nominators

    def write_report(self):
        global version
        log = self.logger
        report = "{{/top}}\n\n"
        log.debug("Writing oldest ten")
        oldestTen = self.print_oldest_ten()
        log.debug("Writing report")
        backlog_report = self.print_backlog_report()
        er_sec = "\n== Exceptions report ==\n"
        log.debug("Writing exceptions report")
        oldHolds = self.print_oldHolds()
        oldRevs = self.print_oldReviews()
        oldScnd = self.print_oldSecond()
        oldest = self.print_oldest()
        badnoms = self.print_badnoms()
        multinoms = self.print_noms()
        sum_sec = "\n== Summary ==\n"
        log.debug("Writing summary")
        summary = self.print_section_summary()
        log.debug("Concatenating reports")
        report = report + oldestTen + backlog_report + er_sec + oldHolds 
        report = report + oldRevs + oldScnd + oldest + badnoms + multinoms  
        report = report + sum_sec + summary + '<!-- Updated at '
        report = report + wikiTimeStamp()+' by WugBot v'+version+' -->\n'
        return(report)

    def print_oldest_ten(self):
        oldest = self.oldestTen
        print_list = [
            '== Oldest nominations ==',
            "''List of the oldest ten nominations that have had no activity ",
            "(placed on hold, under review or requesting a 2nd opinion)''"
            ] + [x.link() for x in oldest]
        return('\n'.join(print_list))

    def print_backlog_report(self):
        projectPath = '/data/project/ganreportbot/pywikibot/'
        global live
        if live == 1:
            back_fname = 'backlog_report.txt'
        else:
            back_fname = 'beta_backlog_report.txt'
        ts = wikiTimeStamp()
        noms = self.stats['noms']
        inac = self.stats['inac']
        ohld = self.stats['ohld']
        orev = self.stats['orev']
        scnd = self.stats['scnd']
        log = self.logger
        newline = ts+' &ndash; '+str(noms)+' nominations outstanding; ' \
            + str(inac) + ' not reviewed; ' \
            + '[[Image:Symbol wait.svg|15px|On Hold]] x ' + str(ohld) + '; '\
            +'[[Image:Searchtool.svg|15px|Under Review]] x '+str(orev) \
            + '; [[Image:Symbol neutral vote.svg|15px|2nd Opinion ' \
            + 'Requested]] x ' + str(scnd) + '<br />'
        with open(projectPath+back_fname,'r') as f:
            backlog = [line.strip() for line in f]
        self.oldLine = backlog.pop()
        backlog.insert(0,newline)
        backlog = [
            '\n== Backlog report ==',
            "\n".join(backlog),  # backlog[1]
            ":''Previous daily backlogs can be viewed at the " + \
            "[[/Backlog archive|backlog archive]].''"
        ]
        with open(projectPath+back_fname,'w') as f:
            log.info("Writing backlog report to file")
            f.write(backlog[1])
        return('\n'.join(backlog))

    def print_oldHolds(self):
        print_list = [
            '\n=== Holds over 7 days old ==='
        ] + [x.link(r=True) for x in sorted(self.oldOnHold, key=lambda y: y.r_timestamp)]
        return('\n'.join(print_list))

    def print_oldReviews(self):
        print_list = [
            '\n=== Old reviews ===',
            ":''Nominations that have been marked under review for 7 days or "\
            +"longer.''",
        ] + [x.link(r=True) for x in sorted(self.oldReviews, key=lambda y: y.r_timestamp)]
        return('\n'.join(print_list))

    def print_oldSecond(self):
        print_list = [
            '\n=== Old requests for 2nd opinion ===',
            ":''Nominations that have been marked requesting a second opinion" \
            +" for 7 days or longer.''"
        ] + [x.link(r=True) for x in sorted(self.oldSecondOp, key=lambda y: y.r_timestamp)]
        return('\n'.join(print_list))

    def print_oldest(self):
        print_list = [
            '\n=== Old nominations ===\n',
            ":''All nominations that were added 30 days ago or longer, "\
            +"regardless of other activity.''",
        ] + [x.link(image=True) for x in sorted(self.overThirty, key=lambda y: y.timestamp)]
        return('\n'.join(print_list))

    def print_badnoms(self):
        n_bad = len(self.badNoms)
        if n_bad < 1:
            subhead = ""
        elif n_bad > 1:
            subhead = ":''There are currently "+str(n_bad)\
            +" malformed nominations.''"
        else:
            subhead = ":''There is currently 1 malformed nomination.''"
        print_list = [
            '\n=== Malformed nominations ===',
            subhead,
        ] + [x.badlink for x in self.badNoms]
        return('\n'.join(print_list))

    def print_noms(self,cutoff=3):
        nominators = self.nominators
        nom_list = []
        for v in list(nominators.values()):
            if len(v.entries) >= cutoff:
                nom_list.append(v)
        nom_list.sort(key=lambda nominator: len(nominator.entries),reverse=True)
        nom_list = [x.print_noms() for x in nom_list]
        head = "\n=== Nominators with multiple nominations ==="
        print_list = [
            head,
            "\n".join(nom_list)
        ]
        return("\n".join(print_list))

    def print_section_summary(self):
        sections = self.section
        print_list = []
        for sec in sections:
            print_list.append(sec.summary())
        return("\n".join(print_list))


class Section:
    sctRegex = re.compile(r'==+ (.*?) (==+)')
    def __init__(self,name):
        global live
        if live == 1:
            self.logger = logging.getLogger('GANRB.Section')
        else:
            self.logger = logging.getLogger('GANRB.beta.Section')
        self.name = name
        self.logger.info("Initializing Section object for "+name)
        self.subsections = []

    def link(self, image = False, text = None, num = 0):
        """I may be wrong, but I'm pretty sure there's no reason for There
        to be a nomination in a super section, so it just defaults to zero.
        I should probably ask someone about that though.
        """
        if text == None:
            link = str(self)
        else:
            sec = self.name
            link = '[[Wikipedia:Good article nominations#'+sec+'|'+text+']]'
        number = num
        string = link + " " + str(number)
        return(string)
        
    def summary(self):
        subsections = self.subsections
        n = sum([len(x.entries) for x in subsections])
        text = "'''"+self.link(num="")+"''' ("+str(n)+")"
        for subsec in subsections:
            text = text + "\n" + subsec.summary()
        return(text)

    def __str__(self):
        s = self.name
        return('[[Wikipedia:Good article nominations#' + s + '|' + s + ']]')


class SubSection(Section):
    def __init__(self, name, section):
        Section.__init__(self,name)
        self.entries = []
        self.section = section

    def link(self, image = False, text = None):
        ####  This still needs modification so it actually creates the format
        ####    seen on the report pages.
        if text == None:
            link = str(self)
        else:
            sec = self.subsection
            link = '[[Wikipedia:Good article nominations#'+sec+'|'+text+']]'
        return(link)
        
    def summary(self):
        entries = self.entries
        nHld = len([x for x in entries if x.status == 'H'])
        nRev = len([x for x in entries if x.status == 'R'])
        nScn = len([x for x in entries if x.status == '2'])
        HldImg = '[[Image:Symbol wait.svg|15px|On Hold]]'
        RevImg = '[[Image:Searchtool.svg|15px|Under Review]]'
        ScnImg = '[[Image:Symbol neutral vote.svg|15px|2nd Opinion Requested]]'
        out = ":'''"+self.link()+"''' ("+str(len(entries))+")"
        if nHld > 0:
            out = out + ": "+HldImg+" x "+str(nHld)
        if nRev > 0:
            sep = "; "
            if nHld == 0:
                sep = ": "
            out = out+sep+RevImg+" x "+str(nRev)
        if nScn > 0:
            sep = "; "
            if (nHld == 0) and (nRev == 0):
                sep = ": "
            out = out+sep+ScnImg+" x "+str(nScn)
        return(out)

    def __str__(self):
        s = self.name
        return('[[Wikipedia:Good article nominations#' + s + '|' + s + ']]')


class Entry:
    def __init__(self,matches,line,subsection):
        """
        Attributes:

        self.text, str
        self.status, bool or None
        self.subsection, userinput
        self.bad, bool
        self.badlink, str or None
        self.title, str or None
        self.timestamp, datetime.datetime instance or None
        self.nominator, str
        self.number, int
        """
        global live
        if live == 1:
            self.logger = logging.getLogger('GANRB.Entry')
        else:
            self.logger = logging.getLogger('GANRB.beta.Entry')
        log = self.logger
        log.debug("Initializing Entry object")
        self.text = line
        self._matches = matches
        self.status = None
        self.subsection = subsection
        self.bad = False
        self.badlink = None
        subsSectName = subsection #subsection.name
        
        log.debug("Getting title")
        try:
            title = matches.group(1)
        except:
            log.warning("Unable to get title")
            log.debug(line)
            self.bad = True
            title = None
        self.title = title
        log.debug(title)
        
        log.debug("Getting timestamp")
        try:
            t = matches.group(4)
            time = wiki2datetime(t)
            l = True
        except:
            log.warning("Unable to get timestamp")
            log.debug(line)
            self.bad = True
            time = None
            l = False
        self.timestamp = time
        log.debug(time)
        
        log.debug("Getting username")
        try:
            username = self.getUsername(matches.group(3))
        except Exception as e:
            log.warning("Unable to get username")
            self.bad = True
            log.debug(line)
            username = None
        self.nominator = username
        log.debug(username)
        
        log.debug("Getting review number")
        try:
            review_num = matches.group(2)
        except:
            log.warning("Unable to get review number")
            self.bad = True
            log.debug(line)
            review_num = 1
        self.get_badLink()
        self.number = review_num
        log.debug(review_num)
        self.r_timestamp = dt.utcnow()
        
    def get_badLink(self):
        if self.title != None:
            title = self.title
        else:
            title = "Unknown nomination"
        self.badlink = self.link(length=False,text=title)

    def getUsername(self, text):
        log = self.logger
        log.debug(text)
        if '[[User' in text:
            name = re.search(r'\[\[User.*?:(.*?)(?:\||\]\])',text).group(1)
            return(name)
        else:
            raise ValueError('Could not get username.')

    def link(self, image = False, length = True, text = None, num=True, r=False):
        if text == None:
            link = str(self)
        else:
            sec = self.subsection
            link = '[[Wikipedia:Good article nominations#'+sec+'|'+text+']]'
        if length:
            if r:
                days = str((dt.utcnow() - self.r_timestamp).days)
            else:
                days = str((dt.utcnow() - self.timestamp).days)
        status = self.status
        if status == None or not image:
            img = ''
        elif status == 'H':
            img = '[[Image:Symbol wait.svg|15px|On Hold]] '
        elif status == 'R':
            img = '[[Image:Searchtool.svg|15px|Under Review]] '
        elif status == '2':
            img = '[[Image:Symbol neutral vote.svg|15px|2nd Opinion Requested]] '
        if num:
            string = '# '+img+link
        else:
            string = img+link
        if length:
            string = string+" ('''"+days+"''' days)"
        return(string)
        
    def add_review(self,status,line):
        log = self.logger
        log.info("Adding review")
        self.status = status
        matches = reviewRegex.search(line)
        try:
            t = matches.group(2)
            time = wiki2datetime(t)
            self.r_timestamp = time
        except:
            log.warning("Cannot get review time")
            self.bad = True
            log.debug(line)
            self.r_timestamp = dt.utcnow()

    def __str__(self):
        sec = self.subsection
        n = self.title
        return('[[Wikipedia:Good article nominations#'+sec+'|'+n+']]')


class Nominator():
    def __init__(self, name):
        self.username = name
        self.entries = []

    def add(self,content,index=0):
        self.entries.insert(index,content)

    def print_noms(self):
        n_noms = 0
        link_list = []
        for entry in self.entries:
            n_noms += 1
            link_list.append(str(entry))
        head = "'''" + self.username + "''' (" + str(n_noms) + ")"
        nomlist = ":" + ", ".join(link_list)
        return("\n".join([head,nomlist]))

def wiki2datetime(wikistamp):
    time, date = wikistamp.split(', ')
    hour, minute = time.split(':')
    day, month, year = date.split(' ')
    month = monthConvert(month)
    dtVals = [int(year), int(month), int(day), int(hour), int(minute)]
    dt = datetime.datetime(*dtVals)
    return(dt)

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

def checkArgs(arg):
    pass
        
def save_pages(site,report,oldLine,oldTen):
    global live
    if live == 1:
        log = logging.getLogger('GANRB')
    else:
        log = logging.getLogger('GANRB.beta')
    log.info("Saving page")
    log.debug("live == "+str(live))
    logging.info("Loading report page")
    try:
        page = pywikibot.Page(site,'Wikipedia:Good article nominations/Report')
    except:
        log.critical("Could not load report page!")
    # Determine if the bot should write to a live page or the test page. Defaults to
    #     test page. Value of -1 tests backlog update (not standard because the file
    #     size is very big).
    if live == 0:
        log.info("Live set to 0, no pages written")
        pass
    elif live == 1:
        log.info("Saving Report")
        page.text=report
        try:
            page.save('Updating exceptions report, WugBot v'+version)
        except:
            log.critical("Could not save to report page!")
        log.info("Saving backlog archive")
        try:
            page = pywikibot.Page(site,'Wikipedia:Good article nominations/' \
                                        +'Report/Backlog archive')
        except:
            log.critical("Could not load backlog archive")
        page.text+='\n'+oldLine
        page.save('Update of GAN report backlog, WugBot v'+version)
    else:
        logging.info("Writing to test page")
        page = pywikibot.Page(site,'User:Wugapodes/GANReportBotTest')
        page.text=report
        page.save('Testing WugBot v'+version)

    # Update the transcluded list of the 5 oldest noms
    log.info("Updating oldest 5 list")
    links = []
    for ent in oldTen:
        links.append(ent.link(length=False,num=False))
    pText = '\n&bull; '.join(links[:5])
    pText+='\n<!-- If you clear an item from backlog and want to update ' \
                    +'the list before the bot next runs, here are the next ' \
                    +'5 oldest nominations:\n&bull; '
    pText+= '\n&bull; '.join(links[5:])
    pText+= '\n-->'
    if live == 0:
        pass
    elif live == 1:
        page = pywikibot.Page(site,'Wikipedia:Good article nominations/backlog/items')
        page.text = pText
        page.save('Updating list of oldest noms. WugBot v%s' % version)
    else:
        log.debug('Writing to items test page')
        page = pywikibot.Page(site,'User:Wugapodes/GANReportBotTest/items')
        page.text = pText
        page.save('Testing WugBot v%s' % version)
    log.info("Finished at "+str(wikiTimeStamp()))

def main():
    global live
    if live == 1:
        log = logging.getLogger('GANRB.main')
    else:
        log = logging.getLogger('GANRB.beta.main')
    log.info("Starting run")
    log.info("### Starting new run ###")
    log.info("GANReportBot version %s" % version)
    log.debug("live is set to %s" % live)
    site = pywikibot.Site('en', 'wikipedia')
    page = pywikibot.Page(site,'Wikipedia:Good article nominations')
    nomPage = NomPage(page.text)
    nomPage.parse()
    report = nomPage.write_report()
    oldLine = nomPage.oldLine
    oldTen = nomPage.oldestTen
    save_pages(site,report,oldLine,oldTen)
    

if __name__ == "__main__":
    main()
    for i in range(1,len(sys.argv)):
        checkArgs(sys.argv[i])
