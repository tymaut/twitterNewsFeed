import xml.etree.ElementTree as ET
import constants as CO
import sys, shutil


xmlFile = ""

def listXMLFile():
    try:
        print xmlFile
        tree = ET.parse(xmlFile)
        root = tree.getroot()
        for child in root:
            _id = child.find('id').text
            _name = child.find('name').text
            _url = child.find('url').text
            _lastRead = child.find('lastRead').text
            _lastReadDate = child.find('lastReadDate').text
            print ("\n{}\n\tid: {}\n\turl: {}\n\tLast Read: {}\n\tLast Read Date: {}\n".format(_name, _id, _url, _lastRead, _lastReadDate)).encode('utf-8')
    except Exception as e:
        print e

def command():
    print "Command? openxml,newfile,new,del,mod,list,exit"
    _in = raw_input()
    if(_in == 'new'):
        newRss()
        command()
    elif(_in == "openxml"):
       openXml()
       command()
    elif(_in == 'del'):
        delRss()
        command()
    elif(_in == 'mod'):
        modRss()
        command()
    elif(_in == "list"):
        listXMLFile()
        command()
    elif(_in == "newfile"):
        newFeedFile()
        command()
    elif(_in=="exit"):
        return
    else:
        command()

def openXml():
       print "\n name of the xml file (x.xml)"
       _fileName = raw_input()
       try:
           with open(_fileName): 
               global xmlFile
               xmlFile = _fileName
               shutil.copyfile(_fileName,"rssOrgTemp/"+_fileName+"_tmp")
               print "file %s loaded" %_fileName
       except IOError:
           print "file does not exist"

       

def newFeedFile():
    print "\n New feed file command"
    print "name of the file (xx.xml):"
    _fileName = raw_input()
    print "comment of the file"
    _comment = raw_input()
    root = ET.Element("rssList")
    tree = ET.ElementTree(root)
#    tree.Comment(_comment)
    tree.write(_fileName)
    print "File %s is created" % _fileName

def newRss():
    print "\nNew Rss command"
    while True:
        print "id?:"
        _id = raw_input()
        _array = getIds()
        print _id in _array
        if(not (_id in _array)):
            break
        else:
            print "id already exists"
    print "name?:"
    _name = raw_input()
    print "url?:"
    _url = raw_input()
    done = False
    while(not done):
        print "Will add a new RSS source with id:{}, name:{}, url:{} - yes/no?".format(_id,_name,_url)
        y_n = raw_input()
        if(y_n=="yes"):
            tree = ET.parse(xmlFile)
            root = tree.getroot()
            child = ET.SubElement(root,"rss")
            id_ = ET.SubElement(child,"id")
            name_ = ET.SubElement(child,"name")
            url_ = ET.SubElement(child,"url")
            lastRead_ = ET.SubElement(child,"lastRead")
            lastReadDate_ = ET.SubElement(child,"lastReadDate")
            id_.text = _id
            name_.text = _name
            url_.text = _url
            tree.write(xmlFile)
            done = 1
        elif(y_n == "no"):
            print "New RSS insert aborted"
            done = 1
        else:
            print "Wrong command!"
             
def getIds():
    tree = ET.parse(xmlFile)
    root = tree.getroot()
    _array = []
    for child in root:
        _array.append(child.find('id').text)
    return _array
    

def delRss():
    print "\nDelete Rss command"
    listXMLFile()
    print "id?:"
    _id = raw_input()
    done = False
    while(not done):
        print "Will delete the RSS source with id:{} - yes/no?".format(_id)
        y_n = raw_input()
        if(y_n == "yes"):
            tree = ET.parse(xmlFile)
            root = tree.getroot()
            for child in root:
                if(child.find('id').text == _id):
                    root.remove(child)
                    tree.write(xmlFile)
                    print "Rss removed..."
                    return
            print "Rss with id {} not found".format(_id)
        elif(y_n == "no"):
            done = 1
        else:
            print "Wrong command!"
            
    
    
def modRss():
    print "\nModify Rss command"
    listXMLFile()
    tree = ET.parse(xmlFile)
    root = tree.getroot()
    print "id?:"
    _id = raw_input()
    index = False
    i=0
    for child in root:
        if(child.find('id').text == _id):
            index = i
            break
        i = i+1
    child = root[index]
    
    print "id: {}\nnew id:".format(child.find('id').text)
    new_id = raw_input()
    if(len(new_id)>0):
        id_field = child.find('id')
        id_field.text = new_id
        print "id modified to ", new_id
    
    print "name: {}\nnew name:".format(child.find('name').text)
    new_name = raw_input()
    if(len(new_name)>0):
        name_field = child.find('name')
        name_field.text = new_name
        print "name modified to ", new_name

    print "url: {}\nnew url:".format(child.find('url').text)
    new_url = raw_input()
    if(len(new_url)>0):
        url_field = child.find('url')
        url_field.text = new_url
        print "url modified to ", new_url

    print "last read: {}\nnew last read: ".format(child.find('lastRead').text)
    new_lastRead = raw_input()
    if(len(new_lastRead)>1):
        lastRead_field = child.find('lastRead')
        lastRead_field.text = new_lastRead
        print "last read modified to ",new_lastRead
    elif(new_lastRead == "-"):
        lastRead_field = child.find('lastRead')
        lastRead_field.text = ""

        lastReadDate_field = child.find('lastReadDate')
        lastReadDate_field.text = ""
        print "last read and last read date removed"

    print "last read date: {}\nnew last read date:".format(child.find('lastReadDate').text)
    new_lastReadDate = raw_input()
    if(len(new_lastReadDate)>1):
        lastReadDate_field = child.find('lastReadDate')
        lastReadDate_field.text = new_lastReadDate
        print "last read date modified to " , new_lastReadDate
    elif(new_lastRead == "-"):
        lastReadDate_field = child.find('lastReadDate')
        lastReadDate_field.text = ""
        print "last read date removed"

    tree.write(xmlFile)
    
#xmlFile = sys.argv[1]
command()
    

