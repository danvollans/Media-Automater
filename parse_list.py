#!/usr/bin/python
#-*- coding: utf-8 -*-

#
#  Need to finish parse_keywords, fix years and movie title (year).  also when looping through dict make sure to add counter to see if we've gotten to the ===== line yet.  then merge the two dicts
#

import fileinput

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
            tvshowlist[fullkey] = {'name': tvshowtitle[1]}
            tvshowlist[fullkey]['episodes'] = []
            tvshowlist[fullkey]['year'] = year
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
        if fullkey not in movielist:
            movielist[fullkey] = {'name': movietitle}
            movielist[fullkey]['year'] = year
        else:
            if "SUSPEND" in movieinfo[1]:
                special = "SUSPEND"
            else:
                special = movieinfo[1].split(") (")[1].split(")")[0]
            fullkey = fullkey+"=="+special
            if fullkey not in movielist:
                movielist[fullkey] = {'name': movietitle}
                movielist[fullkey]['year'] = year
            else:
                # Jeez we're desperate here
                print "Duplicate Movie found!"+movietitle+" === "+imdbkey

def parse_keywords(line):
    if line[:1] == "\"":
        tvshowtitle = line.split("\"")
        if tvshowtitle[1] not in tvshowlist:
            tvshowlist[tvshowtitle[1]] = {'name': tvshowtitle[1]}
            tvshowlist[tvshowtitle[1]]['year'] = year
            tvshowlist[tvshowtitle[1]]['keywords'] = []
        else:
            keywords = tvshowtitle[2].split("\t")
            keyword = keywords[-1].rstrip()
            tvshowlist[tvshowtitle[1]]['keywords'].append(keyword)
    else:
        movietitle = line[0:line.find("(")-1]
        if movietitle not in movielist:
            movielist[movietitle] = {'name': movietitle}
            movielist[movietitle]['year'] = year
            movielist[movietitle]['keywords'] = []
        else:
            keywords = line.split("\t")
            keyword = keywords[-1].rstrip()
            movielist[movietitle]['keywords'].append(keyword)

counter = 1
for line in fileinput.input(['/opt/imdb_lists/movies.list']):
    if counter > 15 and "-----" not in line:
        parse_movies(line)
    counter = counter + 1

for key, value in movielist.items():
    print key
