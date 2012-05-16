#!/usr/bin/python
import os
import MySQLdb
import ConfigParser

config = ConfigParser.SafeConfigParser()
config.read('config.cfg')

def get_directory_structure(rootdir):
    dir = {}
    rootdir = rootdir.rstrip(os.sep)
    start = rootdir.rfind(os.sep) + 1
    for path, dirs, files in os.walk(rootdir):
        folders = path[start:].split(os.sep)
        subdir = dict.fromkeys(files)
        parent = reduce(dict.get, folders[:-1], dir)
        parent[folders[-1]] = subdir
    return dir

dbhost = config.get('mysqlmedia','server')
dbuser = config.get('mysqlmedia','user')
dbpasswd = config.get('mysqlmedia','password')
dbdb = config.get('mysqlmedia','db')

dbconn = MySQLdb.connect (host = dbhost, user = dbuser, passwd = dbpasswd, db = dbdb)
cursor = dbconn.cursor ()

showdir = config.get('folders','shows')
moviedir = config.get('folders','movies')
showdict = get_directory_structure(showdir)
moviedict = get_directory_structure(moviedir)

for folderkey in showdict:
    for showkey in showdict[folderkey]:
        cursor.execute ("select idshow from shows where name = \"%s\"" % showkey)
        retrow = cursor.fetchone ()
	if not retrow:
            print "retrow emtpy %s" % showkey
	    cursor.execute ("insert into shows values(default,\"%s\",NULL,0)" % showkey)
        cursor.execute ("select idshow from shows where idshow = LAST_INSERT_ID()")
        idshow = retrow[0]
        for seasonkey in showdict[folderkey][showkey]:
            seasonstr = seasonkey.partition(' ')
            seasonnum = seasonstr[2]
            for episodekey in showdict[folderkey][showkey][seasonkey]:
                episodestr = episodekey.partition('- s')
                episodenum = episodestr[2]
                episodenum = episodenum[3:]
                episodenum = episodenum.partition('.')
                episodenum = episodenum[0]
                if "-" in episodenum:
                    episodenummult = episodenum.partition('-')
                    episodenum1 = episodenummult[0]
                    episodenum2 = episodenummult[2]
                    episodenum2 = episodenum2[1:]
                    cursor.execute ("insert ignore into episodes values(default,%s,%s,%s)" % (idshow,seasonnum,episodenum1))
                    cursor.execute ("insert ignore into episodes values(default,%s,%s,%s)" % (idshow,seasonnum,episodenum2))    
                else:
                    cursor.execute ("insert ignore into episodes values(default,%s,%s,%s)" % (idshow,seasonnum,episodenum))
for folderkey in moviedict:
    for moviekey in moviedict[folderkey]:
        (moviename,split,movieyear) = moviekey.partition(' (')
        movieyear = movieyear.replace(')','')
        movieyear = int(movieyear)
        cursor.execute ("insert ignore into movies values(default,\"%s\",%s,NULL)" % (moviename,movieyear))
