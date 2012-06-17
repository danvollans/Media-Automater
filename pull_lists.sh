#!/bin/bash
LISTDIR=/opt/imdb_lists
wget -P $LISTDIR ftp://ftp.fu-berlin.de/pub/misc/movies/database/movies.list.gz
gunzip $LISTDIR/movies.list.gz
