# pi-tv7-ansible

This ansible playbook is ment to setup a raspberry >pi2 for tv7 (init7). The idea is to take a fresh raspbian lite installation and run the playbook to have a fully working tv7 player.

## Todo

* Add a storage for timeshift (pause) functionality, i don't know yet what is a good idea to do so:
    * NFS automounts, i use this and it works fine
    * Plugged in USB disk, not tested
* Add webradio channels

## Installation

1. Get a PI and a network cable
1. Download the "Raspbian Stretch Lite" image and install it according to:
    * https://www.raspberrypi.org/downloads/raspbian/
1. Install ansible on your admin computer
1. Download this ansible playbook
1. Give ssh access to the pi from your admin computer
1. Play it

### Configure ansible playbook

* Edit the file ```production```; replace ```your_pi``` with ether the ip address of your pi or the dns name.

### Install ansible on your admin computer

The following can be used on a ubuntu installation:

```
sudo apt-add-repository --yes --update ppa:ansible/ansible
sudo apt-get install ansible
```

### Pre-configure the pi (hostname/ssh access)

Set a new hostname for your pi:

```
sudo hostnamectl set-hostname your_pi
```

Edit/Add the following file/folder containing your ssh public key:

```
.ssh/authorized_keys
```

### Run ansible

```
ansible-playbook -i production site.yml
```

## Components

### kodi

kodi is used as the player and user interface and will be pre-configured to use the tvheadend pvr addon, which is providing the channel list and the epg (electronic program guide).

* It installs kodi and the pvr addon.
* It adds a service to autostart kodi as a standalone app.
* It increases the GPU memory to work with the playout

### tvheadend

tvheadend will make the connection to the init7 stream and provide it in your network as a stream which will work over wi-fi as well, packed with epg (program data) and channel logo.

In this case here we just install and configure it alongside of kodi.

The webinterface runs on http://your_pi:9981, the username and password is "admin".

### scripts

#### prepare_channels.py

This script is getting the latest tv7 playlist and downloads the logos. We need to prepare our own playlist because for tvheadend to be setup automatically it requires a channel number to be set in the playlist.

#### getepg.sh

This script is downloading the epg from https://github.com/mathewmeconry/TV7_EPG_Data and import it into tvheadend.

The epg data is gathered with the scripts of https://github.com/mathewmeconry/TV7_EPG_Parser but as these require at least python version 3.6 and raspbian is providing 3.5, we cannot use the scripts directly.
