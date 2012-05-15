#!/usr/bin/python
#-*- coding: utf-8 -*-

import fileinput
import MySQLdb
import ConfigParser

config = ConfigParser.SafeConfigParser()
config.read('config.cfg')

dbhost = config.get('mysqlminiimdb','server')
dbuser = config.get('mysqlminiimdb','user')
dbpasswd = config.get('mysqlminiimdb','password')
dbdb = config.get('mysqlminiimdb','db')

dbconn = MySQLdb.connect (host = dbhost, user = dbuser, passwd = dbpasswd, db = dbdb)
cursor = dbconn.cursor ()

tvshowlist=dict()
movielist=dict()
tvshowkeywordlist=dict()
moviekeywordlist=dict()

def update_movies(moviehash):
    for key, value in moviehash.items():
        cursor.execute ("""
                INSERT INTO movies (idmovie, name, year, have, special)
                VALUES
                    (default, %(name)s, %(year)s, 0, %(special)s) ON DUPLICATE KEY UPDATE idmovie=idmovie
            """, value)

def update_tvshows(tvshowhash):



def parse_movies(line):
    if line[:1] == "\"":
        tvshowtitle = line[1:line.find("\" (")]
        tvshowinfo = line.split("\"")
        # Parse all the details here
        if "(#" in tvshowinfo[2]:
            seasoninfo = tvshowinfo[2][tvshowinfo[2].find('(#')+1:tvshowinfo[2].find(')}')]
            season = seasoninfo[seasoninfo.find('#')+1:seasoninfo.find('.')]
            episode = seasoninfo[seasoninfo.find('.')+1:]

        year = line.split("\t")[-1].rstrip()
        imdbkey = tvshowinfo[2][tvshowinfo[2].find('(')+1:tvshowinfo[2].find(')')]        
        fullkey = tvshowtitle+"=="+imdbkey
        special = ""
        specialarr = []
       
        if "/" in tvshowinfo[2].split(")")[0]:
            specialarr.append(tvshowinfo[2].split("/")[1].split(")")[0])
        if "SUSPEND" in tvshowinfo[2]:
            special = "SUSPEND"
            specialarr.append(special)
        if len(special) > 0:
            fullkey = fullkey+"=="+special

        if fullkey not in tvshowlist:
            tvshowlist[fullkey] = {'name': tvshowtitle}
            tvshowlist[fullkey]['episodes'] = []
            tvshowlist[fullkey]['year'] = year
            tvshowlist[fullkey]['special'] = ",".join(specialarr)
        if fullkey in tvshowlist and "(#" in tvshowinfo[2]:
            tvshowlist[fullkey]['episodes'].append(season+"-"+episode)
    else:
        year = line.split("\t")[-1].rstrip()
        if "shot" in year or "fragment" in year:
            year = line.split("\t")[-2].rstrip()
        if "-" in year:
            year = year.split("-")[0].replace("(","")
        if year not in line.split("\t")[0]:
            infotmp = line.split("\t")[0]
            year = infotmp[infotmp.find("(")+1:infotmp.find(")")]
        yeartag = "("+year.split("-")[0]
        movieinfo = line.split(yeartag)
        movietitle = movieinfo[0][:-1]
        imdbkey = yeartag+movieinfo[1].split(")")[0]
        imdbkey = imdbkey[1:]
        fullkey = movietitle+"=="+imdbkey
        specialarr = []
        special = ""
        if "/" in movieinfo[1].split(")")[0]:        
            specialarr.append(movieinfo[1].split("/")[1].split(")")[0])
        if "SUSPEND" in movieinfo[1]:
            special = "SUSPEND"
            specialarr.append(special)
        if ") (" in movieinfo[1]:
            specialtmp = movieinfo[1].split(") (")[1].split(")")[0]
            if len(special) > 0:
                special = special+"=="+"("+specialtmp+")"
            else:
                special = "("+specialtmp+")"
            specialarr.append("("+specialtmp+")")
        if len(special) > 0:
            fullkey = fullkey+"=="+special

        if fullkey not in movielist:
            movielist[fullkey] = {'name': movietitle}
            movielist[fullkey]['year'] = year
            movielist[fullkey]['special'] = ','.join(specialarr)
        else:
            print "Duplicate Movie found!"+movietitle+" === "+imdbkey+" === "+special

counter = 1
for line in fileinput.input(['/opt/imdb_lists/movies.list']):
    if counter > 15 and "-----" not in line:
        parse_movies(line)
    counter = counter + 1

#update_movies(movielist)

dbconn.commit()
dbconn.close()
