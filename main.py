import feedparser 
import xml.etree.ElementTree as ET
import networkManager as NM 
import threading, time
import constants as CO
from datetime import datetime
from pytz import timezone 
import sys

rssList = sys.argv[1]
maxFeedAtATime= int(sys.argv[3])#CO.maxFeedAtATime #5
updateFreq =  int(sys.argv[2])
historyFile = sys.argv[4]
try:
    hashtag = "#" + sys.argv[5]
except Exception as e:
    hasthag = ""
timeZone = CO.timeZone#"Europe/Stockholm"
timeFormat = CO.timeFormat#"%D %H:%M %Z%z"
publishBefore = CO.publishBefore
publishAfter = CO.publishAfter

def writeToHistory(_id): 
    try:
        with open(historyFile,"a") as myFile:
            myFile.write(_id + "\n")
        return 1
    except Exception as e:
        print "!!! writeToHistory error: %s" % e
        return False
    return False

def checkFromHistory(_id):
    try:
        with open(historyFile, "r") as myFile:
            for line in myFile:
                temp = line[:-1]
                if(_id == temp):
                    return 1
    except Exception as e:
        print "!!! readFromHistory error: %s" % e
        return False
    return False

def findRssInfo(_id):
#returns rss info from rssList file
    tree = ET.parse(rssList)
    root = tree.getroot()
    for child in root:
        this_id = child.find('id').text
        if(this_id == _id):
            return child
    return None

def findFeedInfo(_id,_feedId):
#gets the information a feed
    rssFeed = getRssXml(_id)
    if(rssFeed == None):
        return None
    found=False
    foundi = 0
    i=0
    while(i<maxFeedAtATime and not found):
        if(rssFeed.entries[i].id == _feedId):
            found = 1
            foundi=i
        else:
            i=i+1
    if(found):
        result = [rssFeed.entries[foundi].id, rssFeed.feed.title, rssFeed.entries[foundi].title, rssFeed.entries[foundi].link]#, rssFeed.entries[foundi].published]
        return result
    return None
    

def getRssXml(_id):
#returns the rss feed from rss url 
    child = findRssInfo(_id)
    if(child == None):
        return  None
    url = child.find('url').text
    d = feedparser.parse(url)
    if(d != None and len(d)>0 ):
        return d
    return None



def updateLastReadFeed(_id,idToBeUpdated):
    tree = ET.parse(rssList)
    root = tree.getroot()
    now = datetime.now(timezone(timeZone)).strftime(timeFormat)
    for child in root:
        this_id = child.find('id').text
        if(this_id == _id):
            field = child.find('lastRead')
            field.text = idToBeUpdated
            field2 = child.find('lastReadDate')
            field2.text = now
            break
    tree.write(rssList)
    print "Updated Last Read: " + child.find('name').text + " at " + now + " - " + idToBeUpdated
    return 1


def getLastNewFeedId(_id,startPosition):
#gets the last feed id starting from startPosition
    d = getRssXml(_id)
    return d.entries[startPosition]['id']

def getNextUnreadFeed(_id):
#returns id of the first unread feed
#returns None if there is no unread 
    d = getRssXml(_id)
    _lastReadId = getLastReadId(_id)
    i=0
    found = False
    prevId = None;
    lastId = None;
    result = 0
    while(not(found) and i<maxFeedAtATime):
        prevId = lastId; 
        lastId = d.entries[i]['id']
        i=i+1
        if(lastId == _lastReadId):
            found = 1
            if(i==1):
                result = 0
                break
            else:
                result = prevId
                break
    if(found):
        if(not checkFromHistory(result)): #check if result has been pushed
            return result
        else:
            return 0
    if(not checkFromHistory(lastId)): #check if lastId has been pushed
        return lastId
    else:
        return 0
    
def getLastReadId(_id):
#gets the last read feed id from rss storage xml
    result = None
    child = findRssInfo(_id)
    lastRead = child.find('lastRead').text
    result = lastRead
    return result

def fetchFeedInfo(_id,_feedId):
    result = []
    feedInfo = findFeedInfo(_id,_feedId)
    if(feedInfo == None):
        return None
    name = feedInfo[1]
    title = feedInfo[2]
    url = feedInfo[3]
#    pubDate = feedInfo[4]
    result = [_id,_feedId, name, title, url]#, pubDate]
    return result


def createTwitterMessage(_id,_feedId):
    result=fetchFeedInfo(_id,_feedId)
    if(result == None):
        return False
    shortener = NM.ShortenURL()
    short = shortener.Shorten(result[4])
    if(short == None):
        short = result[4]
    title = result[3][0:(140-3-len(result[2]+short + hashtag))]
    message = hashtag+" "+result[2]+":"+result[3] + " " + short
    NM.pushToTwitter(message)
    return 1


def pushNewFeed(_id):
#finds the oldest unread feed and sends it to NM
#updates the latest read feed 
#returns true if it updates, 1 if can't for whatever reason
    lastRead = getLastReadId(_id)
    newestFeedId = getLastNewFeedId(_id,0)
    pushed = checkFromHistory(_id)
    if(lastRead == None or len(lastRead)==0):
        print "no last read feed found, updating with latest"
        updateLastReadFeed(_id,newestFeedId)
        return False
    else:
        nextUnreadFeed = getNextUnreadFeed(_id)
        if(nextUnreadFeed != None):
            if(nextUnreadFeed == 0):
                print "No new feed found..." 
                return False
            else:
                result = createTwitterMessage(_id,nextUnreadFeed)
                if(result):
                    print "pushed:"+nextUnreadFeed 
                    updateLastReadFeed(_id,nextUnreadFeed)
                    writeToHistory(nextUnreadFeed)
                    return 1
                else:
                    print "push fail:"+nextUnreadFeed
                    return False
        else:
            print "Error in getting the next unread feed... Updating with the latest feed"
            updateLastReadFeed(_id,newestFeedId)
            return False
    return False


def manageFeed(_id,iterative=False):
    result = pushNewFeed(_id)
    if(result and iterative):
        manageFeed(_id,iterative)
    return


def fetchRssFeeds():
    now = datetime.now(timezone(timeZone))
    todayStart = now.replace(hour=publishAfter[0], minute=publishAfter[1], second = 0)
    todayEnd = now.replace(hour = publishBefore[0], minute = publishBefore[1], second = 0)
    if(not (now < todayEnd and now > todayStart)):
        wait = (todayStart - now)/60
        print "Out of publish time. Next publsih in %s minutes" % wait
        return
    print "RSS Check Started:", datetime.now(timezone(timeZone)).strftime(timeFormat)

    tree = ET.parse(rssList)
    root = tree.getroot()
    for child in root:
        _id = child.find('id').text
        _url = child.find('url').text
        _name= child.find('name').text
        _lastRead = child.find('lastRead').text
        manageFeed(_id)
    print "RSS Check Finished"
    return

class Task( threading.Thread ):
    def __init__( self, action, loopdelay, initdelay ):
        self._action = action
        self._loopdelay = loopdelay
        self._initdelay = initdelay
        self._running = 1
        threading.Thread.__init__( self )

    def __repr__( self ):
        print "aaa"
        return '%s %s %s' % (
            self._action, self._loopdelay, self._initdelay )

    def run( self ):
        if self._initdelay:
            time.sleep( self._initdelay )
        self._runtime = time.time()
        while self._running:
            try:
                start = time.time()
                self._action()
                self._runtime += self._loopdelay
                time.sleep( self._runtime - start )
            except Exception as ex:
                print "Exception in taskrun:", ex

    def stop( self ):
        self._running = 0


class Scheduler:
    def __init__( self ):
        self._tasks = []
        
    def __repr__( self ):
        rep = ''
        for task in self._tasks:
            rep += '%s\n' % `task`
        return rep
        
    def AddTask( self, action, loopdelay, initdelay = 0 ):
        task = Task( action, loopdelay, initdelay )
        self._tasks.append( task )
    
    def StartAllTasks( self ):
        for task in self._tasks:
            task.start()
    
    def StopAllTasks( self ):
        for task in self._tasks:
            print 'Stopping task', task
            task.stop()
            task.join()
            print 'Stopped'


def startScheduledTasks():
    s = Scheduler()
    s.AddTask(fetchRssFeeds, updateFreq, 0)
    s.StartAllTasks()
#    raw_input()
#    s.StopAllTasks()

startScheduledTasks()


