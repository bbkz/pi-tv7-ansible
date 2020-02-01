#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from lxml import etree as ET
import csv
import argparse
from configobj import ConfigObj
import logging

## Set up the command-line options (parameters)
parser = argparse.ArgumentParser(description='prepare and update channels')
parser.add_argument("-c", "--config", help="Use custom config file location. (instead of channels.conf)", default='channels.conf', dest="config_file", metavar="CONFIG_FILE")
parser.add_argument("-d", "--debug", help="show debug informations", default=False, action="store_true", dest="show_debug")

## Parse the parameters from command-line (options)
options = parser.parse_args()

# logging class / debug informations
if options.show_debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('requests').setLevel(logging.CRITICAL)

# loading config file
try:
    config = ConfigObj(options.config_file)
    path_logos = config['logo_path']
    playlist_path = config['webradio_playlist']
    webradio_csv = config['webradio_csv']
except Exception as e:
    logging.error("[-] webradio-channels.py: -> there was a error loading the config file")
    logging.error('[-] ', exc_info=1)
    sys.exit(1)

# ffmpeg command for tvheadend
# %(name)s = Name / %(url)s = url, they have to be filled with a dict("name":"RadioStation" "url":"http://....")
ffmpeg_command = 'pipe://ffmpeg -loglevel fatal -i %(url)s -vn -acodec aac -flags +global_header -strict -2 -metadata service_provider=mychannels -metadata service_name=%(name)s -f mpegts -mpegts_service_type digital_radio pipe:1'

# create channel playlist file
myplaylist = open(str(playlist_path), 'w')
myplaylist.write("#EXTM3U\n")

# get the channels
# parse the csv file
# the first element in the csv is the name the second the url
# the filename of the logo has to be the same as the name and png
mycsv_fhandler = open(webradio_csv,"r")
mycsv = csv.reader(mycsv_fhandler, delimiter=',')
# get the channel data from csv
channel = 500
for row in mycsv:
    name = row[0]
    url = row[1]
    myurl = str(ffmpeg_command % locals())
    channel_logo_url = "file://" + path_logos + "/" + name + ".png"

    # add channels to the playlist file
    # tvh-chnum channel-id m3u-name tvg-logo logo tvg-id tvh-epg tvh-tags group-title tvg-name
    myplaylist.write("#EXTINF:-1 tvh-chnum=\""+str(channel)+"\" channel-id=\""+str(channel)+"\" tvg-id=\""+name+"\" tvg-logo=\""+channel_logo_url+"\", "+name+"\n")
    myplaylist.write(myurl+"\n")

    channel += 1
mycsv_fhandler.close()
