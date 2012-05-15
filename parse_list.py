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
        if tvshowtitle[1] not in tvshowlist:
            tvshowlist[tvshowtitle[1]] = {'name': tvshowtitle[1]}
            tvshowlist[tvshowtitle[1]]['episodes'] = []
            tvshowlist[tvshowtitle[1]]['year'] = ''
        if "(#" in tvshowtitle[2]:
            seasoninfo = tvshowtitle[2][tvshowtitle[2].find('(#')+1:tvshowtitle[2].find(')}')]
            season = seasoninfo[seasoninfo.find('#')+1:seasoninfo.find('.')]
            episode = seasoninfo[seasoninfo.find('.')+1:]
            tvshowlist[tvshowtitle[1]]['episodes'].append('%s-%s' % (season,episode))
        else:
            year = line.split("\t")
            tvshowlist[tvshowtitle[1]]['year'] = year[-1].rstrip()
    else:
        movietitle = line[0:line.find("(")-1]
        if movietitle not in movielist:
            movielist[movietitle] = {'name': movietitle}
            year = line.split("\t")
            movielist[movietitle]['year'] = year[-1].rstrip()

def parse_keywords(line)
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
    if counter > 15:
        parse(line)
    counter = counter + 1

for key, value in movielist.items():
    print key, value
