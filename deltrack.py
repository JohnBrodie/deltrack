#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# This prgram is Licenced under GPL, see http://www.gnu.org/copyleft/gpl.html
# Author: Felix Hummel <deltrack@felixhummel.de>
# Thanks to Camille Gallet <camillegallet@yahoo.fr> for the infoamarok script,
# from which this script borrowed a lot.
import dbus
import sys
import subprocess
import os

from urlparse import urlparse
from urllib import unquote


# Don't delete dir if it contains any of these files.
save = [".mp3", ".flac", ".wma", ".ogg"]
# Other extensions to delete with same base name.
exts = [".tqd"]

try:
    bus = dbus.SessionBus()
except:
    print "Could not connect to dbus."
    sys.exit(1)

try:
    player = dbus.Interface(bus.get_object('org.mpris.amarok', '/Player'),
              dbus_interface='org.freedesktop.MediaPlayer')
    tracklist = dbus.Interface(bus.get_object('org.mpris.amarok', '/TrackList'),
              dbus_interface='org.freedesktop.MediaPlayer')
except:
    print "Could not connect to Amarok."
    sys.exit(1)

index = tracklist.GetCurrentTrack()  # to remove track from playlist
md = player.GetMetadata()
location = md['location']  # track's url (to send track to trash)

baselist = os.path.splitext(location)
basename = baselist[0]
basext = baselist[1]
exts.append(basext)

is_last_track = tracklist.GetLength() == 1
if not is_last_track:
    player.Next()
    # handle dynamic playlists. Thanks go to Oleg K (ICQ: 367607160)
    new_index = tracklist.GetCurrentTrack()
    if new_index == index:
        tracklist.DelTrack(index-1)
    else:
        tracklist.DelTrack(index)
else:
    player.Stop()
    tracklist.DelTrack(0)

path = ''
for ext in exts: #Delete each basename+extension.
    loc = ''.join([basename, ext])
    cmdext = ['kioclient', 'move', loc, 'trash:/']
    print "Running %s" % ' '.join(cmdext)
    retcodext = subprocess.call(cmdext)
    path = urlparse(loc).path

    if retcodext == 0:
        print 'Successfully trashed "%s"' % path
    else:
        print 'Could not trash"%s"' % path

#If the dir is empty let's get rid of it, as well.
direc = os.path.split(path)[0]
direc = unquote(direc)

for f in os.listdir(direc) :
    if os.path.isdir(os.path.join(direc, f)):
        subdir = os.path.join(direc, f)
        subls = os.listdir(subdir)

        if len(subls) > 15 : # We probably don't want to delete this.
            sys.exit(0)

        for s in subls :
            if os.path.isdir(os.path.join(subdir, s)):
                sys.exit(0)
            if os.path.splitext(s)[1] in save :
                sys.exit(0)

    if os.path.splitext(f)[1] in save :
        sys.exit(0)

try: # If we made it this far, nuke the dir/subdir.
    if subdir :
        rmdir = ['kioclient', 'move', subdir, 'trash:/']
        retcodext = subprocess.call(rmdir)
        print "Removed empty subdir %s." % subdir
    rmdir = ['kioclient', 'move', direc, 'trash:/']
    retcodext = subprocess.call(rmdir)
    print "Removed empty dir %s." % direc
except OSError:
    print "Error removing %s, maybe no perms." % direc

sys.exit(0)
