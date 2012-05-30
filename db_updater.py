#!/usr/bin/python
import os
import MySQLdb
import ConfigParser
import subprocess
import argparse

config = ConfigParser.SafeConfigParser()
config.read('config.cfg')

parser = argparse.ArgumentParser(description='Update the database to reflect movies and tv shows.')
parser.add_argument('-i', action="store_true", default=False, dest="interactive")
commands = parser.parse_args()

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

dbhost = config.get('mysqlminiimdb','server')
dbuser = config.get('mysqlminiimdb','user')
dbpasswd = config.get('mysqlminiimdb','password')
dbdb = config.get('mysqlminiimdb','db')

dbconn = MySQLdb.connect (host = dbhost, user = dbuser, passwd = dbpasswd, db = dbdb)
cursor = dbconn.cursor ()

showdir = config.get('folders','shows')
moviedir = config.get('folders','movies')
showdict = get_directory_structure(showdir)
moviedict = get_directory_structure(moviedir)

for folderkey in showdict:
    for showkey in showdict[folderkey]:
        cursor.execute ("select idshow from shows where name = \"%s\"" % showkey)
        retrow = cursor.fetchall()
        if not retrow:
            print "No show with the name %s in database." % showkey
            continue
        if len(retrow) > 1 and commands.interactive:
            print "There were multiple possible shows with the name %s" % showkey
            args = ['python', 'get_show.py', '-a', 'show', '-l', '-n', showkey]
            showlist = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            stdout,stderr = showlist.communicate()
            print stdout
            results = stdout.splitlines()
            possibleshows = []
            count = 3
            while count < len(results):
                possibleshows.append(results[count].split(" ")[0])
                count = count + 1
            print "Please enter a ShowID from the list below:\n",possibleshows,"\n"
            continue
        idshow = retrow[0][0]
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
                    cursor.execute ("update episodes set have = 1 where idshow = %s and season = %s and episode = %s" % (idshow,seasonnum,episodenum1))
#                    print "Episode Added for show %s season %s episode %s" % (idshow,seasonnum,episodenum1)
                    cursor.execute ("update episodes set have = 1 where idshow = %s and season = %s and episode = %s" % (idshow,seasonnum,episodenum2))
#                    print "Episode Added for show %s season %s episode %s" % (idshow,seasonnum,episodenum2)
                else:
                    cursor.execute ("update episodes set have = 1 where idshow = %s and season = %s and episode = %s" % (idshow,seasonnum,episodenum))
#                    print "Episode Added for show %s season %s episode %s" % (idshow,seasonnum,episodenum)
for folderkey in moviedict:
    for moviekey in moviedict[folderkey]:
        (moviename,split,movieyear) = moviekey.partition(' (')
        movieyear = movieyear.replace(')','')
        movieyear = int(movieyear)
        cursor.execute ("""select idmovie from movies where name = "%s" and year = "%s" and special not like "%%(VG)%%" """, (moviename,movieyear))
        movieretrow = cursor.fetchall()
        if not movieretrow:
            print "No movie with the name %s in database." % moviename
            continue
        if len(retrow) > 1 and commands.interactive:
            print "There were multiple possible movies with the name %s and year %s" % (moviename,movieyear)
            args = ['python', 'get_show.py', '-a', 'movie', '-l', '-n', moviename, '-y', movieyear]
            movielist = Popen(args).wait()
            continue
        idmovie = movieretrow[0][0]    
        cursor.execute ("update movies set have = 1 where idmovie = %s" % idmovie)
#        print "Movie added %s - (%s)" % (moviename,movieyear)
