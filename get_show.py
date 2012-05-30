#!/usr/bin/python
#
#    add logging for files that are missing , s03e04 could not download etc
#    
#
import MySQLdb
import urllib
from elementtree.ElementTree import parse, XML, fromstring, tostring
import xml.parsers.expat
import re
import paramiko
import sys
import argparse
import subprocess
import ConfigParser

config = ConfigParser.SafeConfigParser()
config.read('config.cfg')

parser = argparse.ArgumentParser(description='Update or download specific torrents.')
parser.add_argument('-a', action="store", dest="action")
parser.add_argument('-l', action="store_true", default=False, dest="lookup")
parser.add_argument('-y', action="store", dest="mediayear")
parser.add_argument('-n', action="store", dest="medianame")
parser.add_argument('-i', action="store", dest="mediaid")
parser.add_argument('-s', action="store", dest="season")
parser.add_argument('-e', action="store", dest="episode") 
results = parser.parse_args()

dbhost = config.get('mysqlminiimdb','server')
dbuser = config.get('mysqlminiimdb','user')
dbpasswd = config.get('mysqlminiimdb','password')
dbdb = config.get('mysqlminiimdb','db')

dbconn = MySQLdb.connect (host = dbhost, user = dbuser, passwd = dbpasswd, db = dbdb)
cursor = dbconn.cursor ()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
host = config.get('seedbox','server')
user = config.get('seedbox','user')
passwd = config.get('seedbox','pass')
ssh.connect(host, username=user,password=passwd)

watchdir = config.get('seedbox','watchdir')
tmpdir = config.get('seedbox','tmpdir')

def torinfo_movie(rssurl,movie):
    try:
        try:
            xml = parse(urllib.urlopen(rssurl)).getroot()
        except:
            rssurl = rssurl.replace('%20720p', 'dvd')
            xml = parse(urllib.urlopen(rssurl)).getroot()
        hreflist = xml.getiterator('enclosure')
        titlelist = xml.getiterator('title')
        #count = 0
        #hrefctr = len(hreflist)
        #while (count < hrefctr):
        hrefret = hreflist[0].attrib['url']
        title = titlelist[1].text
        title = title.lower()
            #titlematch = "%s-" % searcher
            #if titlematch not in title:
            #    break
            #else:
            #    count = count + 1
        html = urllib.urlopen(hrefret).read()
        match = re.search('https://torcache.net/(.+?).torrent', html)
        if match:
            endfile = match.group(1)
            endfile = "http://torrage.com/%s.torrent" % endfile
        else:
            match = re.search('btih(.+?)&', html)
            match = match.group(1)[1:]
            if match:
                endfile = match
                endfile = "http://torrage.com/%s.torrent" % endfile
            else:
                endfile = "no match"
        return (hrefret,title,endfile)
    except BaseException:
        print searcher
        #t, v, tb = sys.exc_info()
        #print "exception on line", tb.tb_lineno, t, v, rssurl
        return ("no-url","no-title","no-file")


def torinfo_update(rssurl,show):
    xml = parse(urllib.urlopen(rssurl)).getroot()
    hreflist = xml.getiterator('enclosure')
    for href in hreflist:
        hrefret = href.attrib['url']
    titlelist = xml.getiterator('title')
    for title in titlelist:
        title = title.text
        title = title.lower()
        if "[720]" in title:
            title = title.strip("[720]")
            titleparts = title.partition("%s " % show)
            series = titleparts[2].strip()
            season = int(series[1:3])
            episode = int(series[4:6])    
        
    return (hrefret,season,episode)        

def torinfo_episode(rssurl,show,searcher):
    try:
        try:
            xml = parse(urllib.urlopen(rssurl)).getroot()
        except:
            rssurl = rssurl.replace('%20720p', '')
            xml = parse(urllib.urlopen(rssurl)).getroot()
        hreflist = xml.getiterator('enclosure')
        titlelist = xml.getiterator('title')
        #count = 0
        #hrefctr = len(hreflist)
        #while (count < hrefctr):
        hrefret = hreflist[0].attrib['url']
        title = titlelist[1].text
        title = title.lower()
            #titlematch = "%s-" % searcher
            #if titlematch not in title:
            #    break            
            #else:
            #    count = count + 1
        html = urllib.urlopen(hrefret).read()
        match = re.search('https://torcache.net/(.+?).torrent', html)
        if match:
            endfile = match.group(1)
            endfile = "http://torrage.com/%s.torrent" % endfile
        else:
            match = re.search('btih(.+?)&', html)
            match = match.group(1)[1:]
            if match:
                endfile = match
                endfile = "http://torrage.com/%s.torrent" % endfile
            else:
                endfile = "no match"
        return (hrefret,title,endfile) 
    except BaseException:    
        print searcher
        #t, v, tb = sys.exc_info()
        #print "exception on line", tb.tb_lineno, t, v, rssurl
        return ("no-url","no-title","no-file")

def update_show():
    cursor.execute ("select name,idshow from shows where follow is true")
    shows = cursor.fetchall()
    for show in shows:
        showname = show[0]
        idshow = show[1]
        show_safe = showname.replace(" ","-").lower()
        showurl = 'http://www.dailytvtorrents.org/rss/show/%s?onlynew=yes&only=720&items=1' % show_safe
        (dl_url,dl_season,dl_episode) = torinfo_update(showurl,showname.lower())
        # for show get current season and episode
        cursor.execute("select season,max(episode) from episodes where idshow=%s and season = (select max(season) from episodes where idshow = %s) and have is true" % (idshow,idshow))
        showinfo = cursor.fetchone()
        (show_season,show_episode) = showinfo
        if dl_season >= show_season:
            if dl_episode > show_episode:
                stdin, stdout, stderr = ssh.exec_command("wget -P %s -c %s" % (watchdir,dl_url))

def get_episode(season,showname,theepisode):
    episode = "%02d" % (int(theepisode))
    season = "%02d" % (int(season))
    searchterm = "%s S%sE%s 720p" % (showname,season,episode)
    episodename = "S%sE%s" % (season,episode)
    searchterm = searchterm.replace(' ','%20')
    episodeurl = "http://kat.ph/search/%s/?rss=1&field=seeders&sorder=desc" % searchterm
    torinfo = torinfo_episode(episodeurl,showname.lower(),episodename.lower())
    url = torinfo[2].rstrip()
    return url    

def get_season(season,showname,theepisode):
    # rss fun
    if theepisode == "all":
        cursor.execute("select episode from episodes where idshow = %s and season = %s order by episode asc" % (showid,season))
        episodelist = cursor.fetchall()
        urllist = []
        for episode in episodelist:
            episode = "%02d" % (int(episode[0]))
            season = "%02d" % (int(season))
            searchterm = "%s S%sE%s 720p" % (showname,season,episode)
            episodename = "S%sE%s" % (season,episode)
            searchterm = searchterm.replace(' ','%20')
            episodeurl = "http://kat.ph/search/%s/?rss=1&field=seeders&sorder=desc" % searchterm
            torinfo = torinfo_episode(episodeurl,showname.lower(),episodename.lower())
            urllist.append(torinfo[2].rstrip())
        return urllist
    else:
        urllist = get_episode(season,showname,theepisode)
        return urllist

def get_show(showid,showname,getseason,getepisode):
    if getseason == "all":
        cursor.execute("select distinct(season) from episodes where idshow = %s" % showid)
        seasonlist = cursor.fetchall()
    else:
        seasonlist = [getseason]
    for season in seasonlist:
        if getepisode == "all":
            torurl = get_season(season[0],showname,"all")
        else:
            torurltmp = get_season(season[0],showname,getepisode)
            torurl = [torurltmp]
        epcount = 0
        for tor in torurl:
            filename = "%s Season %s FN %s" % (showname,season[0],epcount)
            filename = filename.replace(' ','-')
            stdin, stdout, stderr = ssh.exec_command("wget -O %s/%s.tar.gz -c %s" % (tmpdir,filename,tor))
            epcount = epcount + 1
    try:
        stdin, stdout, stderr = ssh.exec_command("find %s -type f -name '*.tar.gz' | xargs -I {} gunzip {}" % tmpdir)
        stdin, stdout, stderr = ssh.exec_command("find %s -type f -name '*.tar' | xargs -I {} mv {} {}.torrent" % tmpdir)
        stdin, stdout, stderr = ssh.exec_command("rm %s/*.tar.gz" % tmpdir)    
        stdinfin, stdoutfin, stderrfin = ssh.exec_command("ls %s | while read -r file; do mv %s/$file %s/$file; sleep 5; done" % (tmpdir,tmpdir,watchdir))
    except:
        print "Had some errors on the seedbox."

def get_movie(moviename):
    searchterm = "%s 720p" % moviename
    searchterm = searchterm.replace(' ','%20')
    movieurl = "http://kat.ph/search/%s/?rss=1&field=seeders&sorder=desc" % searchterm
    try:
        torinfo = torinfo_movie(movieurl,moviename.lower())
        url = torinfo[2].rstrip()
        filename = moviename.replace(' ','-')
        try:
            stdin, stdout, stderr = ssh.exec_command("wget -O %s/%s.tar.gz -c %s" % (tmpdir,filename,url))
            stdin, stdout, stderr = ssh.exec_command("find %s -type f -name '*.tar.gz' | xargs -I {} gunzip {}" % tmpdir)
            stdin, stdout, stderr = ssh.exec_command("find %s -type f -name '*.tar' | xargs -I {} mv {} {}.torrent" % tmpdir)
            stdin, stdout, stderr = ssh.exec_command("rm %s/*.tar.gz" % tmpdir)
            stdinfin, stdoutfin, stderrfin = ssh.exec_command("ls %s | while read -r file; do mv %s/$file %s/$file; sleep 5; done" % (tmpdir,tmpdir,watchdir))
        except:
            print "Had some seedbox errors."
            print stderr.readlines()
            print stferrfin.readlines()
    except:
        print "Really couldn't find Torrent."

if results.action == "update":
    update_show()
    print "Shows updated."

if results.action == "show" and results.lookup is True and results.medianame:
    showname = results.medianame
    print "Looking up information for TV Show %s..." % showname
    cursor.execute("""select shows.idshow,shows.name,shows.year,shows.special,count(distinct season) as season from shows,episodes where lower(name) = lower("%s") and shows.idshow = episodes.idshow group by idshow""" % showname)
    information = cursor.fetchall()
    col1max = col2max = col3max = col4max = col5max = 0
    biginfoarr = []
    for record in information:
        idshow = str(record[0])
        name = str(record[1])
        year = str(record[2])
        special = str(record[3])
        seasons = str(record[4])
        if col1max < len(idshow): 
            col1max = len(idshow)
        if col2max < len(name):
            col2max= len(name)
        if col3max < len(year):
            col3max = len(year)
        if col4max < len(seasons):
            col4max = len(seasons)
        if col5max < len(special):
            col5max = len(seasons)
        infoarr = [idshow,name,year,seasons,special]
        biginfoarr.append(infoarr)
    print "\nID\t".expandtabs(col1max+6)+"Name\t".expandtabs(col2max+8)+"Year(s)\t".expandtabs(col3max+11)+"Seasons\t".expandtabs(col4max+11)+"Special"
    for info in biginfoarr:
        print info[0]+"\t".expandtabs(col1max+6-len(info[0]))+info[1]+"\t".expandtabs(col2max+8-len(info[1]))+info[2]+"\t".expandtabs(col3max+11-len(info[2]))+info[3]+"\t".expandtabs(col4max+11-len(info[3]))+info[4]

if results.action == "show" and results.lookup is False and results.mediaid and results.medianame:
    showid = results.mediaid
    showname = results.medianame
    if results.season:
        season = results.season
        if results.episode:
            episode = results.episode
            cursor.execute("select idepisode from episodes where idshow = %s and season = %s and episode = %s and have is true" % (showid,season,episode))
            idepisode = cursor.fetchone()
            if not idepisode:
                print "Getting %s season %s episode %s..." % (showname,season,episode)
                get_show(showid,showname,season,episode)
            else:
                print "Already had %s season %s episode %s..." % (showname,season,episode)
        else:
            print "Getting %s season %s..." % (showname,season)
            get_show(showid,showname,season,"all")
    else:
        print "Getting %s ALL SEASONS" % showname
        get_show(showid,showname,"all","all")

if results.action == "movie" and results.lookup is True and results.medianame:
    moviename = results.medianame
    movieyear = ""
    if results.mediayear:
        movieyear = " and year = \"%s\"" % results.mediayear
    print "Looking up information for Movie %s..." % moviename
    cursor.execute("""select idmovie,name,year,special from movies where lower(name) = lower("%s")%s""" % (moviename,movieyear))
    information = cursor.fetchall()
    col1max = col2max = col3max = col4max = 0
    biginfoarr = []
    for record in information:
        idmovie = str(record[0])
        name = str(record[1])
        year = str(record[2])
        special = str(record[3])
        if col1max < len(idmovie):
            col1max = len(idmovie)
        if col2max < len(name):
            col2max= len(name)
        if col3max < len(year):
            col3max = len(year)
        if col4max < len(special):
            col4max = len(special)
        infoarr = [idmovie,name,year,special]
        biginfoarr.append(infoarr)
    print "\nID\t".expandtabs(col1max+6)+"Name\t".expandtabs(col2max+8)+"Year(s)\t".expandtabs(col4max+11)+"Special"
    for info in biginfoarr:
        print info[0]+"\t".expandtabs(col1max+6-len(info[0]))+info[1]+"\t".expandtabs(col2max+8-len(info[1]))+info[2]+"\t".expandtabs(col3max+11-len(info[2]))+info[3]

if results.action == "movie" and results.lookup is False and results.mediaid and results.medianame:
    movieid = results.mediaid
    moviename = results.medianame
    cursor.execute("select idmovie from movies where idmovie = %s and have is true" % movieid)
    indb = cursor.fetchone()
    if not indb:
        print "Getting %s" % moviename
        get_movie(moviename)
    else:
        print "Already had %s with id %s" % (moviename,movieid)

