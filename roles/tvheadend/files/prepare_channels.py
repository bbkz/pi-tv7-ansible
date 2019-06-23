#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# author bbk <bbk@nocloud.ch>

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

# - creates tv7 channels m3u playlist with channel numbers
# - downloads logos from init7

import sys
import os
import urllib
#from urllib.request import urlopen
import urllib.request
import json
import base64
from lxml import etree as ET
import csv
import argparse
from configobj import ConfigObj
import logging

## Set up the command-line options (parameters)
parser = argparse.ArgumentParser(description='prepare and update channels')
parser.add_argument("-c", "--config", help="Use custom config file location. (instead of prepare_channels.conf)", default='prepare_channels.conf', dest="config_file", metavar="CONFIG_FILE")
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
    url_data = config['url_data']
    url_playlist = config['url_playlist']
    logo_path = config['logo_path']
    playlist_path = config['playlist_path']
except Exception as e:
    logging.error("[-] prepare_channels.py: -> there was a error loading the config file")
    logging.error('[-] ', exc_info=1)
    sys.exit(1)

# Create folders
try:
    os.makedirs(logo_path, exist_ok=True)
except Exception as e:
    logging.error("[-] prepare_channels.py: os.mkdir() -> could create logo folder")
    logging.error('[-] ', exc_info=1)
    sys.exit(1)
try:
    os.makedirs(os.path.dirname(playlist_path), exist_ok=True)
except Exception as e:
    logging.error("[-] prepare_channels.py: os.mkdir() -> could create playlist folder")
    logging.error('[-] ', exc_info=1)
    sys.exit(1)

# channel data with logo from json
usock = urllib.request.urlopen(url_data)
jsonData = usock.read()
usock.close()
init7_data = json.loads(jsonData.decode('utf-8'))
if(init7_data == None):
    init7_data = []

# playlist data with streaming url
usock = urllib.request.urlopen(url_playlist)
src_playlist = usock.readlines()
usock.close()

# initialize channel playlist file
tv7playlist = open(playlist_path, 'w')
tv7playlist.write("#EXTM3U\n")

# parse the json data / each channel as item
# result from init7 url channel string
channel = 1
for item in init7_data:
    name = item.get("name")
    #tv7_name = name.encode('utf-8')
    logging.info("[*] processing "+name+"...")

    # extract logo from json string
    slogo = item.get("logo").split(',')
    logo = base64.b64decode(slogo[1])
    country = item.get("country")
    language = item.get("language")
    replay = item.get("replay")
    hd = item.get("hd")

    #channel_logo = str(path_logos) + "/" + str(name.replace(" ","_")) +'.png'
    channel_logo = str(logo_path) + "/" + str(channel) +'.png'
    channel_logo_url = "file://" + os.path.abspath(channel_logo)

    # write logos into files
    f = open(channel_logo, 'wb')
    f.write(logo)
    f.close()

    # write playlist file
    lineno = 0
    for pl_item in src_playlist:
        if pl_item.decode('utf-8').endswith(name+"\n"):
            # tvh-chnum m3u-name tvg-logo logo tvg-id tvh-epg tvh-tags group-title tvg-name
            tv7playlist.write("#EXTINF:-1 tvh-chnum=\""+str(channel)+"\" tvg-id=\""+name+"\" tvg-logo=\""+channel_logo_url+"\" tvh-tags=\""+country + "|"+language+"\","+name+"\n")
            tv7playlist.write(src_playlist[lineno+1].decode('utf-8'))
            logging.info("[*] "+str(name)+" added to playlist")
        lineno += 1

    channel += 1
    logging.info("[✓] "+name+" done")
