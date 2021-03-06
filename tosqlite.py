#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
import feedparser
import os
import sys
import sqlite3
import urllib2
import time
import socket
import speedparser
import cchardet as chardet
#request = urllib2.Request("http://blog.csdn.net/rss.html?type=Home&channel=")
#request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 5.1; rv:24.0) Gecko/20130619 Firefox/24.0')
#print urllib2.urlopen(request).read()
#f = speedparser.parse('http://cnbeta.feedsportal.com/c/34306/f/624776/index.rss')
#f = speedparser.parse('http://blog.csdn.net/rss.html?type=Home&channel=')
def isextist(link,publisher):
    text=os.path.split( os.path.realpath( sys.argv[0] ) )[0]
    text=text+"/db/reader.db"
    con = sqlite3.connect(text)
    cur = con.cursor()
    cur.execute("select * from reader where link=(?) and publisherid=(?)",(link,publisher))
    if (len(cur.fetchall())==0):
        cur.close()
        con.close()
        return 1
    else:
        cur.close()
        con.close()
        return 0
    
def add(http,publisherid):
    total=0
    try:
        request = urllib2.Request(http)
        print 'ok'
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0')
        readhttp=urllib2.urlopen(request,timeout=10).read()
    except:
        return 0
    
    chard=chardet.detect(readhttp)
    if (chard['encoding']== u'GB18030'):
        fp= feedparser.parse(readhttp)
        print 'by feedparser'
    else:
        fp= speedparser.parse(readhttp,clean_html=False)
        print 'by speedparser'
    #print '     OK'
    
    #print '     OK'
    text=os.path.split( os.path.realpath( sys.argv[0] ) )[0]
    text=text+"/db/reader.db"
    con = sqlite3.connect(text)
    con.text_factory=str
    cur = con.cursor()
    try:
        cur.execute('CREATE TABLE reader(id integer primary key autoincrement,title,link,description,content,time,publisherid)')        
    except:
            {}
    index=0
    #print fp.entries
    for entry in fp.entries:
                try:
                    t=entry.published
                except:	
                    try:	
                        t=entry.updated
                    except:
                        t=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
                        print  "error"
                title=entry.title
                link=entry.link
                try:
                    description=entry.description
                except:
                    description=''
                try:
                    content=entry.content[0]['value']
                except:
                    content=''
                
                if (isextist(link,publisherid)) :
                    con.execute('insert into reader(title,link,description,content,time,publisherid) values(?,?,?,?,?,?)',(title,link,description,content,t,publisherid))
                    print entry.title
                    total=total+1
                    con.commit()
                index=index+1
            

    cur.close()
    con.close()
    return total

def compact_sqlite3_db():
    try:
        text=os.path.split( os.path.realpath( sys.argv[0] ) )[0]
        text=text+"/db/reader.db"
        conn = sqlite3.connect(text)
        conn.execute("VACUUM")
        conn.close()
        return True
    except:
        return False
