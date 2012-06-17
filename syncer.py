#!/usr/bin/python
# Syncer program
#
import MySQLdb
import paramiko
import subprocess
import os
import sys
import ConfigParser
import time

config = ConfigParser.SafeConfigParser()
config.read('config.cfg')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
host = config.get('seedbox','server')
user = config.get('seedbox','user')
passwd = config.get('seedbox','pass')
ssh.connect(host, username=user,password=passwd)

dbhost = config.get('mysqlminiimdb','server')
dbuser = config.get('mysqlminiimdb','user')
dbpasswd = config.get('mysqlminiimdb','password')
dbdb = config.get('mysqlminiimdb','db')

dbconn = MySQLdb.connect (host = dbhost, user = dbuser, passwd = dbpasswd, db = dbdb)
cursor = dbconn.cursor ()

moviedir = '/mnt/media/Movies/'
showsdir = '/mnt/media/TV Shows/'
finishpath = '/home/flipperbaby/finished/'

def acquire(filetype,filepath,fileid,dlid,filename):
    # get extension
    garbage, extension = os.path.splitext(filepath)
    if filetype == "movies":
        # get the year for the movie
        cursor.execute("""select year from movies where idmovie = %s""" % fileid)
        year = cursor.fetchone()[0]
        dlpath = filepath.split(finishpath)[1]
        # make remote dir for movie name
        argsmkdir = ['mkdir', '%s%s (%s)' % (moviedir,filename,year)]
        mkdir = subprocess.Popen(argsmkdir)
        # update the database 
        cursor.execute("""update downloads set downloading = b'1' where iddownload = %s""" % dlid)
        dbconn.commit()
        argsaria = ['aria2c', '-j', '16', '-s', '50', '-x', '16', '--dir=%s%s (%s)' % (moviedir,filename,year), '--out=%s (%s)%s' % (filename,year,extension), '--check-certificate=false', 'https://%s:%s@cereal.whatbox.ca/private/%s/finished/%s' % (user,passwd,user,dlpath)]
        aria = subprocess.Popen(argsaria).wait()
        if aria == 0:
            # update both database tables
            cursor.execute("""delete from downloads where iddownload = %s""" % dlid)
            cursor.execute("""update movies set have = b'1' where idmovie = %s""" % fileid)
        else :
            cursor.execute("""update downloads set downloading = b'0' where iddownload = %s""" % dlid)
            dbconn.commit()
    else:
        dlpath = filepath.split(finishpath)[1]
        # Get the actual Show Name
        cursor.execute("""select shows.name from downloads,episodes,shows where downloads.iddownload = %s and downloads.fkid = episodes.idepisode and episodes.idshow = shows.idshow""" % dlid)
        showname = cursor.fetchone()[0]
        showname.replace('&','and')
        # Check if TV Show / Season directories already exist
        # Get the season for the episode
        cursor.execute("""select episodes.season,episodes.episode from episodes,shows where episodes.idepisode = %s""" % fileid)
        season = cursor.fetchone()[0]
        seasonpad = "%02d" % (season)
        episode = cursor.fetchone()[1]
        episodepad = "%02d" % (episode)
        argsmkdir = ['mkdir', '-p', '%s%s/Season %s/' % (showsdir,showname,season)]
        mkdir = subprocess.Popen(argsmkdir)
        # update the database
        cursor.execute("""update downloads set downloading = b'1' where iddownload = %s""" % dlid)
        dbconn.commit()
        argsaria = ['aria2c', '-j', '16', '-s', '50', '-x', '16', '--dir=%s%s/Season %s/' % (showsdir,showname,season), '--out=%s - s%se%s%s' % (showname,seasonpad,episodepad,extension), '--check-certificate=false', 'https://%s:%s@cereal.whatbox.ca/private/%s/finished/%s' % (user,passwd,user,dlpath)]
        aria = subprocess.Popen(argsaria).wait()
        if aria == 0:
            # update both database tables
            cursor.execute("""delete from downloads where iddownload = %s""" % dlid)
            cursor.execute("""update episodes set have = b'1' where idepisode = %s""" % fileid)
        else :
            cursor.execute("""update downloads set downloading = b'0' where iddownload = %s""" % dlid)
            dbconn.commit()

def getfiles():
    filetypes = ['.mkv','.avi','.mp4','3gp']
    stdin, stdout, stderr = ssh.exec_command("find /home/flipperbaby/finished -maxdepth 2 -type f | sed -n '2,${p;}'")
    files = []
    for filepath in stdout.readlines():
        filepath = filepath.rstrip()
        if any(x in filepath for x in filetypes):
            files.append(filepath)
    return files

def extractrars():
    stdin, stdout, stderr = ssh.exec_command("find /home/flipperbaby/finished -maxdepth 2 -name *.rar | xargs -L1 -I{} unrar e {}")
    while not stdout.channel.closed or not stderr.channel.closed:
        time.sleep(10)

# get a list of current downloading torrents
cursor.execute("""select iddownload,type,fkid,tags from downloads where downloading is not true""")
downloads = cursor.fetchall()

# extract remote rars
extractrars()

# get a list of current finished torrents
files = getfiles()

for download in downloads:
    # check to see if tags are in array
    filetype = download[1]
    tag = download[3]
    fileid = download[2]
    dlid = download[0]
    finished = 0
    match = [s for s in files if tag.lower() in s.lower()]
    if match:
        finished = 1
    else:
        tag = tag.replace(' ', '.')
        match = [s for s in files if tag.lower() in s.lower()]
        if match:
            finished = 1
        else:
            tag = tag.replace('.', '-')
            match = [s for s in files if tag.lower() in s.lower()]
            if match:
                finished = 1
    if finished > 0 and match:
        acquire(filetype,match[0],fileid,dlid,tag)

dbconn.commit()

