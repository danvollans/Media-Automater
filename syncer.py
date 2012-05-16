#!/usr/bin/python
# Syncer program
#
import MySQLdb
import paramiko
import subprocess
import os
import sys
import ConfigParser

config = ConfigParser.SafeConfigParser()
config.read('config.cfg')


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
host = config.get('seedbox','server')
user = config.get('seedbox','user')
passwd = config.get('seedbox','pass')
ssh.connect(host, username=user,password=passwd)

def syncremote():
    stdindir, stdoutdir, stderrdir = ssh.exec_command("find /home/flipperbaby/finished -maxdepth 1 -type d | sed -n '2,${p;}'")
    for dirname in stdoutdir.readlines():
        dirnamefull = dirname.rstrip()
        dirname = dirname.partition('/home/flipperbaby/finished/')
        dirname = dirname[2].rstrip()
        dirnameclean = dirname.replace('~','-')
        args = ['mkdir', '/mnt/hgfs/Media/Unsorted/%s' % dirnameclean]
        mkdir = subprocess.Popen(args)
        stdinfile, stdoutfile, stderrfile = ssh.exec_command("find \"/home/flipperbaby/finished/%s\" -type f" % dirname)
        dirretarr = []
        for filename in stdoutfile.readlines():
            # now do some parsing
            filename = filename.partition('/home/flipperbaby/')
            filename = filename[2].rstrip()
            args = ['aria2c', '-j', '16', '-s', '50', '-x', '16', '--dir=/mnt/hgfs/Media/Unsorted/%s' % dirnameclean, '--check-certificate=false', 'https://%s:%s@flipperbaby.cereal.whatbox.ca/%s' % (user,passwd,filename)]
            for arg in args:
                print "%s " % arg
            download = subprocess.Popen(args).wait()
            dirretarr.append(download)
            if download != 0:
                print "File had error: %s" % filename
                print "Command was: %s" % args
        if 1 in dirretarr or not dirretarr:
            print "Directory had error:P %s" % dirname
        else:
            stdindirmv, stdoutdirmv, stderrdirmv = ssh.exec_command("mv \"%s\" /home/flipperbaby/moved" % dirnamefull)
            print "Directory moved: %s\n" % dirname

    stdinind, stdoutind, stderrind = ssh.exec_command("find /home/flipperbaby/finished -maxdepth 1 -type f")
    for indfile in stdoutind.readlines():
        indfilefull = indfile.rstrip()
        indfile = indfile.partition('/home/flipperbaby/')
        indfile = indfile[2].rstrip()
        indargs = ['aria2c', '-j', '16', '-s', '50', '-x', '16', '--dir=/mnt/hgfs/Media/Unsorted', '--check-certificate=false', 'https://%s:%s@flipperbaby.cereal.whatbox.ca/%s' % (user,passwd,indfile)]
        inddownload = subprocess.Popen(indargs).wait()
        if inddownload != 0:
            print "File had error: %s" % indfile
            print "Command was: %s\n" % indargs
        else:
            stdinfilemv, stdoutfilemv, stderrfilemv = ssh.exec_command("mv %s /home/flipperbaby/moved" % indfilefull)
            print "File moved: %s\n" % indfile
    ssh.close()
def mover():
    fileList = []
    mediadir = '/mnt/hgfs/Media/Unsorted'
    rootdir = mediadir
    for root, subFolders, files in os.walk(rootdir):
        if "rename_src" in root or "rename_fin" in root:
            continue
        for filen in files:
            fileext = filen[-3:]
            if fileext in ['avi', 'dat', 'mp4', 'mkv', 'vob']:
                fileList.append(os.path.join(root,filen))
    for media in fileList:
        media = media.rstrip()
        mediaargs = ['mv', media, '%s/rename_src/' % mediadir]
        mediamv = subprocess.Popen(mediaargs).wait()

def renamed_mover():
    renamedir = '/mnt/hgfs/Media/Unsorted/rename_fin'
    moviedir = '/mnt/hgfs/Media/Movies/'
    for movie ,subFolders, files in os.walk(renamedir):
        movie = movie.rstrip()
        if movie == "/mnt/hgfs/Media/Unsorted/rename_fin":
            continue
        movieargs = ['mv','%s' % movie, moviedir]
        movielist = subprocess.Popen(movieargs).wait()
    
    tvdir = '/mnt/hgfs/Media/TV Shows'
    for episode in os.listdir(renamedir):
        (showname,split,series) = episode.partition(' - s')
        (season,split,number) = series.partition('e')
        mkdirargs = ['mkdir', '%s/%s' % (tvdir,showname)]
        mkdir = subprocess.Popen(mkdirargs).wait()
        mkdirargs2 = ['mkdir', '%s/%s/Season %s' % (tvdir,showname,int(season))]
        mkdir2 = subprocess.Popen(mkdirargs2).wait()
        showargs = ['mv','%s/%s' % (renamedir,episode), '%s/%s/Season %s/' % (tvdir,showname,int(season))]
        showlist = subprocess.Popen(showargs).wait()

syncremote()
mover()
renamed_mover()
