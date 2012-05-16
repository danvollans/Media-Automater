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
parser.add_argument('-n', action="store", dest="medianame")
parser.add_argument('-i', action="store", dest="mediaid")
parser.add_argument('-s', action="store", dest="season")
parser.add_argument('-e', action="store", dest="episode") 
results = parser.parse_args()

args = ['python', 'db_updater.py']
dbupdate = subprocess.Popen(args).wait()

dbhost = config.get('mysqlmedia','server')
dbuser = config.get('mysqlmedia','user')
dbpasswd = config.get('mysqlmedia','password')
dbdb = config.get('mysqlmedia','db')

dbhost2 = config.get('mysqlimdb','server')
dbuser2 = config.get('mysqlimdb','user')
dbpasswd2 = config.get('mysqlimdb','password')
dbdb2 = config.get('mysqlimdb','db')

dbhost3 = config.get('mysqlminiimdb','server')
dbuser3 = config.get('mysqlminiimdb','user')
dbpasswd3 = config.get('mysqlminiimdb','password')
dbdb3 = config.get('mysqlminiimdb','db')

dbconn = MySQLdb.connect (host = dbhost, user = dbuser, passwd = dbpasswd, db = dbdb)
cursor = dbconn.cursor ()

dbconn2 = MySQLdb.connect (host = dbhost2, user = dbuser2, passwd = dbpasswd2, db = dbdb2)
cursor2 = dbconn2.cursor ()

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
    cursor3.execute ("select name,idshow from shows where follow is true")
    shows = cursor3.fetchall() 
    for show in shows:
        showname = show[0]
        idshow = show[1]
        show_safe = showname.replace(" ","-").lower()
        showurl = 'http://www.dailytvtorrents.org/rss/show/%s?onlynew=yes&only=720&items=1' % show_safe
        (dl_url,dl_season,dl_episode) = torinfo_update(showurl,showname.lower())
        # for show get current season and episode
        cursor3.execute("select season,max(episode) from episodes where idshow=%s and season = (select max(season) from episodes where idshow = %s)" % (idshow,idshow))
        showinfo = cursor3.fetchone()
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
        cursor2.execute("select episode_nr from title where episode_of_id=%s and season_nr=%s order by episode_nr asc" % (showid,season))
        episodelist = cursor2.fetchall()
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
        cursor2.execute("select distinct(season_nr) from title where episode_of_id = %s and season_nr is not null" % showid)
        seasonlist = cursor2.fetchall()
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
if results.action == "show":
    showid = results.mediaid
    showname = results.medianame
    if results.season:
        season = results.season
        if results.episode:
            episode = results.episode
            cursor.execute("select episodes.idshow from episodes,shows where shows.idshow=episodes.idshow and shows.name=\"%s\" and episodes.season=%s and episodes.number=%s;" % (showname,season,episode))
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

if results.action == "movie":
    movieid = results.mediaid
    moviename = results.medianame
    cursor.execute("select idmovie from movies where imdb_id = %s" % movieid)
    indb = cursor.fetchone()
    if not indb:
        print "Getting %s" % moviename
	get_movie(moviename)
    else:
	print "Already had %s with id %s" % (moviename,movieid)		
