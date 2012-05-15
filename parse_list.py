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

def parse_movies(line):
    if line[:1] == "\"":
        tvshowtitle = line.split("\"")
        # Parse all the details here
        if "(#" in tvshowtitle[2]:
            seasoninfo = tvshowtitle[2][tvshowtitle[2].find('(#')+1:tvshowtitle[2].find(')}')]
            season = seasoninfo[seasoninfo.find('#')+1:seasoninfo.find('.')]
            episode = seasoninfo[seasoninfo.find('.')+1:]

        year = line.split("\t")[-1].rstrip()
        imdbkey = tvshowtitle[2][tvshowtitle[2].find('(')+1:tvshowtitle[2].find(')')]        
        fullkey = tvshowtitle[1]+"=="+imdbkey

        if fullkey not in tvshowlist:
            if "/" in year:
                special = year.split("/")[1]
            else:
                special = "NULL"
            tvshowlist[fullkey] = {'name': tvshowtitle[1]}
            tvshowlist[fullkey]['episodes'] = []
            tvshowlist[fullkey]['year'] = year
            tvshowlist[fullkey]['special'] = special
        if fullkey in tvshowlist and "(#" in tvshowtitle[2]:
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
        if "/" in year:        
            specialarr.append(year.split("/"))[1]
        if "SUSPEND" in movieinfo[1]:
            special = "SUSPEND"
            specialarr.append(special)
        if ") (" in movieinfo[1]:
            if len(special) > 0:
                special = movieinfo[1].split(") (")[1].split(")")[0]+"=="+special
            else:
                special = movieinfo[1].split(") (")[1].split(")")[0]
            specialarr.append(special)
        if len(special) > 0:
            fullkey = fullkey+"=="+special

        if fullkey not in movielist:
            movielist[fullkey] = {'name': movietitle}
            movielist[fullkey]['year'] = year
            movielist[fullkey]['special'] = specialarr
        else:
            print "Duplicate Movie found!"+movietitle+" === "+imdbkey+" === "+special

counter = 1
for line in fileinput.input(['/opt/imdb_lists/movies.list']):
    if counter > 15 and "-----" not in line:
        parse_movies(line)
    counter = counter + 1

for key, value in movielist.items():
    cursor.execute("insert into movies values(default,\"%s\",%s,0,\"%s\")" % (value['name'],value['year'],','.join(value['special'])))

dbconn.commit()
dbconn.close()
