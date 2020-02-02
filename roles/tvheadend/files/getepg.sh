#!/bin/bash

# download the latest epg and import it into tvh
# this is ment to be run as a cronjob

cd $(dirname "$0")
if [ ! -d data/epg/archive ]; then
  mkdir -p data/epg/archive
fi
HTSHOME=$(getent passwd hts | awk -F: '{ print $6 }')
SOURCES="https://github.com/mathewmeconry/TV7_EPG_Data/raw/master/tv7_epg.xml.gz"
>data/epg/grab_xmltv.log

oldfiles=$(data/epg/*.gz 2> /dev/null | wc -l)
if [ "$oldfiles" != "0" ]; then
  mv data/epg/*.gz data/epg/archive
fi

echo "Remove archived files older than 7 days..."
find data/epg/archive/* -mtime +7 -delete >> data/epg/grab_xmltv.log

echo "Download starting..." >> data/epg/grab_xmltv.log
echo "Time: $(date)" >> data/epg/grab_xmltv.log

if [ ! -z ${SOURCES+x} ]; then
  for SOURCE in $SOURCES; do
    FILENAME=$(echo $SOURCE |cut -d "/" -f4- |sed 's/\//_/g')
    wget $SOURCE -O data/epg/$FILENAME -nv -a data/epg/grab_xmltv.log
    zcat data/epg/$FILENAME | socat - UNIX-CONNECT:$HTSHOME/.hts/tvheadend/epggrab/xmltv.sock
    echo "" >> data/epg/grab_xmltv.log
  done
else
  echo "No tar.gz sources defined" >> data/epg/grab_xmltv.log
fi

echo "Time: $(date)" >> data/epg/grab_xmltv.log
echo "EPG Updated finished." >> data/epg/grab_xmltv.log
