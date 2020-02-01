#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import urllib
#from urllib.request import urlopen
import urllib.request
from lxml import etree as ET
import argparse
from configobj import ConfigObj
import logging
import re

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
    url_playlist = config['tv7_url']
    playlist_path = config['tv7_playlist']
except Exception as e:
    logging.error("[-] tv7-channels.py: -> there was a error loading the config file")
    logging.error('[-] ', exc_info=1)
    sys.exit(1)

# Create folders
try:
    os.makedirs(os.path.dirname(playlist_path), exist_ok=True)
except Exception as e:
    logging.error("[-] tv7-channels.py: os.mkdir() -> could create playlist folder")
    logging.error('[-] ', exc_info=1)
    sys.exit(1)

# playlist data with streaming url
usock = urllib.request.urlopen(url_playlist)
src_playlist = usock.readlines()
usock.close()

# initialize channel playlist file
tv7playlist = open(playlist_path, 'w')
tv7playlist.write("#EXTM3U\n")

channel = 1
lineno = 0
# parse playlist file
for line in src_playlist:
    if line.decode('utf-8').startswith("#EXTINF"):
        # get rid of #EXTINF...
        pattern = re.compile(r'\s(.*=.*)')
        metaline = pattern.findall(line.decode('utf-8'))
        # split each metadata and separate extinf ",[name]" at the end of the line
        #pattern = re.compile(r'\s(?=.*=)|(?<=,)\s')
        pattern = re.compile(r'\s(?=.*=)|,\s')
        metastrings = pattern.split(metaline[0])
        logging.debug("[*] processing line "+line.decode('utf-8')+"...")
        metadata = {}
        # tvg-logo tvg-name group-title
        for metastring in metastrings:
            logging.debug("[*] processing metadata "+str(metastring)+"...")
            data = metastring.split('=')
            if len(data) == 2:
                metadata[data[0]] = data[1]
            else: # it must be the name
                metadata['name'] = data[0]

        # write new playlist
        language = metadata.get("group-title")
        name = metadata.get("name")
        logo = metadata.get("tvg-logo")

        # tvh-chnum channel-id m3u-name tvg-logo logo tvg-id tvh-epg tvh-tags group-title tvg-name
        tv7playlist.write("#EXTINF:-1 tvh-chnum=\""+str(channel)+"\" channel-id=\""+str(channel)+"\" tvg-id=\""+name+"\" tvg-logo="+logo+" tvh-tags="+language+", "+name+"\n")
        tv7playlist.write(src_playlist[lineno+1].decode('utf-8'))
        logging.info("[*] "+str(name)+" added to playlist")

        channel += 1
        logging.info("[✓] "+name+" done")

    lineno += 1
