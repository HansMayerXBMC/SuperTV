#!/usr/bin/env python
# -*- coding: utf-8 -*-
# favorites.py - SuperTV - handling of favorite channels
# (C) 2012 HansMayer - http://supertv.3owl.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import urllib, urllib2, cookielib, time, USTimeZone,re,sqlite3,os,socket,gzip,StringIO,zlib,inspect,sys
from datetime import datetime, timedelta,tzinfo

try: import simplejson as json
except: import json

from epg import *

FAVORITESPATH = os.path.join(xbmcaddon.Addon(id='script.SuperTV').getAddonInfo('path'),'resources/Favorites')

class Favorites:
    def __init__(self):
        self.conn = sqlite3.connect(FAVORITESPATH)
        c=self.conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='favorites';")
        
        et=c.fetchone()
        if not et or et[0] == 0:
            c.execute('''create table favorites
            (id int, title text, links text,
            chan text, module text, thumb text)''')
            self.conn.commit()
        c.close()
        
    def add(self, item, urlList):
        c=self.conn.cursor()
        c.execute("SELECT max(id) from favorites;")
        e=c.fetchone()
        i=0
        if e and e[0]:
            i=e[0]
        links = urlList[0]
        if len(urlList[2]) > 0:
            links += ";DIV;"+";DIV;".join(urlList[2])
        chan = ''
        module = ''
        if urlList[1]:
            chan = urlList[1].chan
            module = urlList[3]
        c.execute("INSERT INTO favorites VALUES (?,?,?,?,?,?);", (i+1,item.getLabel().split(' - ')[0][3:-4],links, chan, module,urlList[4]))
        self.conn.commit()
        c.close()
    
    def remove(self,pos):
        c=self.conn.cursor()
        c.execute("SELECT id from favorites ORDER BY id LIMIT 1 OFFSET ?;", (pos,))
        i=c.fetchone()
        c.execute("DELETE from favorites WHERE id=?", i)
        self.conn.commit()
        c.close()
        
    def getList(self):
        #ID, TITLE, EPG, BACKUP, CHAN, MODULE, THUMB
        c=self.conn.cursor()
        c.execute("SELECT * from favorites ORDER BY id;")
        es=c.fetchall()
        c.close()
        urlList = []
        for e in es:
            links=e[2].split(';DIV;')
            epg = None
            if e[3] and e[4]:
                epg = EPGs[e[4]]
                epg = epg(e[3])
            if len(links) == 1:
                urlList.append([links[0], epg, [], e[4],e[5],e[1]])
            else:
                urlList.append([links[0], epg, links[1:], e[4],e[5],e[1]])
        return urlList