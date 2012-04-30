#!/usr/bin/env python
# -*- coding: utf-8 -*-
# main.py - SuperTV - a reimplementation of the rtmpGUI
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
import urllib, urllib2, cookielib, threading
import string, os, re, time, datetime, sys, platform

try:
  from cStringIO import StringIO
except:
  from StringIO import StringIO

import xbmc, xbmcgui, xbmcaddon
__settings__   = xbmcaddon.Addon(id='script.SuperTV')

from aes import AESCtr
from epg import *
from favorites import *

try:
    try:
        raise
        import xml.etree.cElementTree as ElementTree
    except:
        from xml.etree import ElementTree
except:
    try:
        from elementtree import ElementTree
    except:
        dlg = xbmcgui.Dialog()
        dlg.ok('ElementTree missing', 'Please install the elementree addon.',
                'http://tinyurl.com/xmbc-elementtree')
        sys.exit(0)

addon = xbmcaddon.Addon()
BASE = []

ACTION_PREVIOUS_MENU = 10
ACTION_SELECT_ITEM = 7
ACTION_MOVE_LEFT = 1
ACTION_MOVE_RIGHT = 2 
ACTION_MOVE_UP = 3
ACTION_MOVE_DOWN = 4
ACTION_MENU = 7
ACTION_SHOW_INFO = 11
ACTION_PAUSE = 12
ACTION_STOP = 13
ACTION_NEXT_ITEM = 14
ACTION_PREV_ITEM = 15
ACTION_OSD = 122
ACTION_NUMBER_0 = 58
ACTION_NUMBER_1 = 59
ACTION_NUMBER_2 = 60
ACTION_NUMBER_3 = 61
ACTION_NUMBER_4 = 62
ACTION_NUMBER_5 = 63
ACTION_NUMBER_6 = 64
ACTION_NUMBER_7 = 65
ACTION_NUMBER_8 = 66
ACTION_NUMBER_9 = 67

ACTION_CONTEXTMENU = 117

def checkAutoupdateEPG():
    try:
        if os.popen('uname').read().strip() == 'Darwin':
            if not os.path.exists(os.path.expanduser('~/Library/LaunchAgents/com.xbmc.SuperTV.plist')):
                #cmd='cp "'+os.path.join(xbmcaddon.Addon(id='script.SuperTV').getAddonInfo('path'),'resources/com.xbmc.SuperTV.plist')
                #os.system(cmd+'" "'+os.path.expanduser('~/Library/LaunchAgents/')+'"')
                #os.system('launchctl load "'+os.path.expanduser('~/Library/LaunchAgents/com.xbmc.SuperTV.plist')+'"')
                pass
        elif sys.platform.startswith('win'):
            try:
                if not os.path.exists(os.path.join(xbmcaddon.Addon(id='script.SuperTV').getAddonInfo('path'),'resources/update.bat')):
                    bat = 'PATH '
                    for p in sys.path:
                        if p:
                            bat += '"%s";' % p
                    bat += '%PATH%\ncd "%s"\npython update.py' % xbmcaddon.Addon(id='script.SuperTV').getAddonInfo('path').replace('/','\\')
                    b=open(os.path.join(xbmcaddon.Addon(id='script.SuperTV').getAddonInfo('path'),'resources/update.bat'),'w')
                    b.write(bat)
                    b.close
            except:
                pass
        else:
            try:
                if not os.path.exists(os.path.join(xbmcaddon.Addon(id='script.SuperTV').getAddonInfo('path'),'resources/update.sh')):
                    b=open(os.path.join(xbmcaddon.Addon(id='script.SuperTV').getAddonInfo('path'),'resources/update.sh'),'w')
                    b.write('#!/bin/bash\r\ncd "'+xbmcaddon.Addon(id='script.SuperTV').getAddonInfo('path')+'"\r\npython update.py')
                    b.close()
            except:
                pass
    except:
        pass
t=None

def filmOnKeepAliveF():
    global t
    global phpsessid
    if t:
        t.cancel()
    a=downloadSocket('filmon.com',80).fetch('GET /ajax/keepAlive HTTP/1.1\r\nHost: www.filmon.com\r\nCookie: disable-edgecast=1\r\nConnection: close\r\n\r\n').replace('Something','Something else')
    t = threading.Timer(30.0, filmOnKeepAliveF)
    t.start()

phpsessid = None
filmOnKeepAlive = threading.Timer(0,None)

def filmOnUpdate(link):
    chanid=link.split(' ')[0].split('?')[0].split('live')[1]
    quality=link.split(' ')[1].split('=')[1].split('.')[1]
    global phpsessid
    
    phpsessid=downloadSocket('www.filmon.com',80).fetch('GET /ajax/getChannelInfo HTTP/1.1\r\nHost: www.filmon.com\r\nConnection:close\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.151 Safari/535.19\r\n\r\n').split('PHPSESSID=')[1].split(";")[0]
    filmOnKeepAlive = threading.Timer(30.0, filmOnKeepAliveF)
    filmOnKeepAlive.start()
    
    headers=[('Origin','http://www.filmon.com'),('Referer','http://www.filmon.com/tv/htmlmain/'),('X-Requested-With','XMLHttpRequest'),('Accept','application/json, text/javascript, */*'),('Connection','keep-alive'),('Cookie','disable-edgecast=1; viewed_site_version_cookie=html;PHPSESSID='+phpsessid+";")]
    a=getURL('http://www.filmon.com/ajax/getChannelInfo', post=urllib.urlencode({'channel_id':chanid, 'quality':quality}),headers=headers,ct=True)
    return json.loads(a)[0]['serverURL']+' playpath='+json.loads(a)[0]['streamName']+" app=live/"+json.loads(a)[0]['serverURL'].split('/')[-1]+" "+" ".join(link.split(' ')[2:])
    
def update45ESToken(link):
    playpath=re.findall('playpath=(?P<playpath>.*?) ',link)[0]
    rtmplink = link.split(' ')[0]
    directo=AESCtr().encrypt(getURL('http://servicios.telecinco.es/tokenizer/clock.php')+";"+playpath+";0;0", "xo85kT+QHz3fRMcHMXp9cA", 256)
    data=getURL('http://servicios.telecinco.es/tokenizer/tk3.php',post=urllib.urlencode({'id':playpath,'startTime':'0','directo':directo,'endTime':'endTime'}))
    print data
    xdata = ElementTree.XML(data)
    #return link.replace('playpath='+playpath, 'playpath='+ElementTree.parse(StringIO(data)).getroot().findtext('file'))
    return link.replace('playpath='+playpath, 'playpath='+xdata.findtext('file')).replace(rtmplink, xdata.findtext('stream'))

class ChannelList(xbmcgui.WindowXMLDialog):
    overlay = None
    urls = []
    mode = 0
    src = 0
    languages = []
    listitems = []
    lang = 0
    progLock = False
    def listSources(self):
        self.mode = 0
        if self.getListSize() > 0:
            self.clearList()
        self.addItem('..')
        if len(Favorites().getList()) > 0:
            self.addItem('Favorites')
        for s in BASE:
            listitem = xbmcgui.ListItem(label=s[1])
            self.addItem(listitem)
        xbmc.executebuiltin("Container.SetViewMode(50)")

    def listChannels(self, src):
        self.mode = 1
        self.src = src
        if self.getListSize() > 0:
            self.clearList()
        prog = xbmcgui.DialogProgress()
        prog.create('Loading channels',"")
        xml=getURL(BASE[src][0],None)
        #tree = ElementTree.XML(xml)
        tree = ElementTree.parse(StringIO(xml)).getroot()

        streams = tree.findall('channel')
        self.languages = [('..',"DetaultTVShows.png")]
        for stream in streams:
            language = stream.findtext('name').strip().title()
            if not language in self.languages and language.find('Link down') == -1:
                self.languages.append((language,stream.findtext('thumbnail', "DefaultTVShows.png").strip()))


        if len(self.languages) < 3:
            prog.close()
            self.listLinks()
            return
        inum=0
        for l in self.languages:
            listitem = xbmcgui.ListItem(label=l[0],iconImage=l[1])
            self.addItem(listitem)
            prog.update(int((inum/float(len(self.languages)-1))*100.0),l[0])
            inum += 1
        prog.close()
    
    def listLinks(self,lang=1):
        self.mode = 2
        self.lang = lang
        if self.getListSize() > 0:
            self.clearList()
        self.urls = ['..']
        self.listitems = ['..']
        xml=getURL(BASE[self.src][0],None)
        #tree = ElementTree.XML(xml)
        tree = ElementTree.parse(StringIO(xml)).getroot()

        streams = tree.findall('channel')[lang-1].findall('items')[0].findall('item')
        hasEPG=False

        self.progLock = True
        prog = xbmcgui.DialogProgress()
        prog.create('Loading channel',"")
        inum=0
        for stream in streams:
            urlitem = ['',None,[],'','']
            title = '[B]'+stream.findtext('title')+'[/B]'
            desc = title
            epgid=stream.findtext('epgid')
            if epgid:
                ep=epgid.split(":")
                if ep[0] in EPGs.keys():
    				e=EPGs[ep[0]](ep[1])
    				hasEPG = True
    				desc = ""
    				urlitem[1] = e
    				epg=e.getEntries()
    				i=len(epg)
    				for e in epg:
    				    if (__settings__.getSetting("show24h") == 'false'):
    				        desc += e[1].strftime("%I:%M")+'-'+e[2].strftime("%I:%M")+":\n"+e[0]+u"\n\n"
    				    else:
    				        desc += e[1].strftime("%H:%M")+'-'+e[2].strftime("%H:%M")+":\n"+e[0]+u"\n\n"
    				if len(epg) > 0:
    				    title +=' - '+epg[0][0]
            rtmplink = stream.findtext('link').strip()
            if rtmplink[:4] == 'rtmp':
                if stream.findtext('playpath'):
                    rtmplink += ' playpath='+stream.findtext('playpath').strip()
                if stream.findtext('swfUrl'):
                    rtmplink += ' swfurl='+stream.findtext('swfUrl').strip()
                if stream.findtext('pageUrl'):
                    rtmplink += ' pageurl='+stream.findtext('pageUrl').strip()
                if stream.findtext('proxy'):
                    rtmplink += ' socks='+stream.findtext('proxy').strip()
                if stream.findtext('advanced','').find('live=') == -1 and rtmplink.find('mms://') == -1 and rtmplink.find('mmsh://') == -1 and rtmplink.find('http://') != 0:
                    rtmplink += ' live=1 buffer=50000000 '
                rtmplink += ' '+stream.findtext('advanced','').replace('-v','').replace('live=1','').replace('live=true','')
                if (__settings__.getSetting("has_updated_librtmp") == 'true'):
                    rtmplink = rtmplink.replace('-x ',"swfsize=").replace('-w ','swfhash=').replace('-T ','token=')
            logo=stream.findtext('thumbnail', "DefaultTVShows.png").strip()
            urlitem[4] = logo
            item=xbmcgui.ListItem(title, desc, iconImage=logo)
            infolabels = { "title": title, "Plot": desc, "plotoutline": desc, "tvshowtitle": title, "originaltitle": title}
            item.setInfo( type="movies", infoLabels=infolabels )
            item.setProperty('IsPlayable', 'true')
            item.setProperty('Plot', desc)
            #xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content='movies' )
            if stream.findtext('swfUrl') == 'http://www.filmon.com/tv/modules/FilmOnTV/files/flashapp/filmon/FilmonPlayer.swf?v=f':
                rtmplink = "filmon|"+rtmplink
            if stream.findtext('swfUrl') == 'http://static1.tele-cinco.net/comun/swf/playerCuatro.swf':
                rtmplink = "telecinco|"+rtmplink
            urlitem[0] = rtmplink
            self.urls.append(urlitem)
            self.listitems.append(item)
            #print xbmc.executebuiltin("Container.SetContent(movies)")
            self.setProperty('content','movies')
            #print xbmc.executebuiltin("Container.Content()")
            xbmc.executebuiltin("Container.SetViewMode(503)")
            prog.update(int((inum/float(len(streams)-1))*100.0),title)
            inum += 1

        self.progLock = False
        prog.close()
        for i in self.listitems:
            self.addItem(i)

            
    def listLanguages(self, src):
        self.mode = 1
        self.src = src
        if self.getListSize() > 0:
            self.clearList()
        xml=getURL(BASE[src][0],None)
        #tree = ElementTree.XML(xml)
        tree = ElementTree.parse(StringIO(xml)).getroot()

        if len(tree.findall('channel')) > 0:
            self.listChannels(src)
            return
        streams = tree.findall('stream')
        self.languages = ['..']
        for stream in streams:
            language = stream.findtext('language').strip().title()
            if not language in self.languages and language.find('Link down') == -1:
                self.languages.append(language)

        self.languages = list(set(self.languages))
        self.languages.sort()

        if len(self.languages) < 3:
            self.listVideos()
            self.setFocusId(503)
            return

        for l in self.languages:
            listitem = xbmcgui.ListItem(label=l)
            self.addItem(listitem)

    def listVideos(self,lang=1):
        self.mode = 2
        self.lang = lang
        if self.getListSize() > 0:
            self.clearList()
        self.urls = ['..']
        self.listitems = ['..']
        xml=getURL(BASE[self.src][0],None)
        #tree = ElementTree.XML(xml)
        tree = ElementTree.parse(StringIO(xml)).getroot()

        if len(tree.findall('channel')) > 0:
            self.listLinks(lang)
            return
        streams = tree.findall('stream')
        hasEPG=False
        newS=[]
        for stream in streams:
            language = stream.findtext('language').strip().title()
            if language == self.languages[lang] and language.find('Link down') == -1:
                newS.append(stream)
        self.progLock = True
        prog = xbmcgui.DialogProgress()
        prog.create('Loading streams'," "," "," ")
        inum = 0
        for stream in newS:
            urlitem = ['',None,[],'','']
            title = '[B]'+stream.findtext('title')+'[/B]'
            desc = title
            epgid=stream.findtext('epgid')
            if epgid:
                ep=epgid.split(":")
                if ep[0] in EPGs.keys():
    				urlitem[3] = ep[0]
    				e=EPGs[ep[0]](ep[1])
    				hasEPG = True
    				desc = ""
    				urlitem[1] = e
    				epg=e.getEntries()
    				i=len(epg)
    				for e in epg:
    				    if (__settings__.getSetting("show24h") == 'false'):
    				        desc += e[1].strftime("%I:%M")+'-'+e[2].strftime("%I:%M")+":\n"+e[0]+u"\n\n"
    				    else:
    				        desc += e[1].strftime("%H:%M")+'-'+e[2].strftime("%H:%M")+":\n"+e[0]+u"\n\n"
    				if len(epg) > 0:
    				    title +=' - '+epg[0][0]
            
            rtmplink = stream.findtext('link').strip()
            if rtmplink[:4] == 'rtmp':
                if stream.findtext('playpath'):
                    rtmplink += ' playpath='+stream.findtext('playpath').strip()
                if stream.findtext('swfUrl'):
                    rtmplink += ' swfurl='+stream.findtext('swfUrl').strip()
                if stream.findtext('pageUrl'):
                    rtmplink += ' pageurl='+stream.findtext('pageUrl').strip()
                if stream.findtext('proxy'):
                    rtmplink += ' socks='+stream.findtext('proxy').strip()
                if stream.findtext('advanced','').find('live=') == -1 and rtmplink.find('mms://') == -1 and rtmplink.find('mmsh://') == -1 and rtmplink.find('http://') != 0:
                    rtmplink += ' live=1 buffer=50000000 '
                rtmplink += ' '+stream.findtext('advanced','').replace('-v','').replace('live=1','').replace('live=true','')
                if (__settings__.getSetting("has_updated_librtmp") == 'true'):
                    rtmplink = rtmplink.replace('-x ',"swfsize=").replace('-w ','swfhash=').replace('-T ','token=')
                if stream.findtext('swfUrl') == 'http://www.filmon.com/tv/modules/FilmOnTV/files/flashapp/filmon/FilmonPlayer.swf?v=f':
                    rtmplink = "filmon|"+rtmplink
                if stream.findtext('swfUrl') == 'http://static1.tele-cinco.net/comun/swf/playerCuatro.swf':
                    rtmplink = "telecinco|"+rtmplink
            urlitem[0] = rtmplink.strip()
            tmp =[]
            for s in stream.findall('backup'):
                rtmplink = s.findtext('link').strip()
                if rtmplink[:4] == 'rtmp':
                    if s.findtext('playpath'):
                        rtmplink += ' playpath='+s.findtext('playpath').strip()
                    if s.findtext('swfUrl'):
                        rtmplink += ' swfurl='+s.findtext('swfUrl').strip()
                    if s.findtext('pageUrl'):
                        rtmplink += ' pageurl='+s.findtext('pageUrl').strip()
                    if s.findtext('proxy'):
                        rtmplink += ' socks='+s.findtext('proxy').strip()
                    if stream.findtext('advanced','').find('live=') == -1 and rtmplink.find('mms://') == -1 and rtmplink.find('mmsh://') == -1 and rtmplink.find('http://') != 0:
                        rtmplink += ' live=1 buffer=50000000 '
                    rtmplink += ' '+stream.findtext('advanced','').replace('-v','').replace('live=1','').replace('live=true','')
                    if (__settings__.getSetting("has_updated_librtmp") == 'true'):
                        rtmplink = rtmplink.replace('-x ',"swfsize=").replace('-w ','swfhash=').replace('-T ','token=')
                
                    if s.findtext('swfUrl') == 'http://www.filmon.com/tv/modules/FilmOnTV/files/flashapp/filmon/FilmonPlayer.swf?v=f':
                        rtmplink = "filmon|"+rtmplink
                    if s.findtext('swfUrl') == 'http://static1.tele-cinco.net/comun/swf/playerCuatro.swf':
                        rtmplink = "telecinco|"+rtmplink
                tmp.append(rtmplink.strip())
            urlitem[2] = tmp
                    
            logo=stream.findtext('logourl', "DefaultTVShows.png")
            urlitem[4] = logo
            item=xbmcgui.ListItem(title, desc, iconImage=logo)
            infolabels = { "title": title, "Plot": desc, "plotoutline": desc, "tvshowtitle": title, "originaltitle": title}
            item.setInfo( type="movies", infoLabels=infolabels )
            item.setProperty('IsPlayable', 'true')
            item.setProperty('Plot', desc)
            #xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content='movies' )

            self.urls.append(urlitem)
            #self.addItem(item)
            self.listitems.append(item)
            #print xbmc.executebuiltin("Container.SetContent(movies)")
            self.setProperty('content','movies')
            #print xbmc.executebuiltin("Container.Content()")
            xbmc.executebuiltin("Container.SetViewMode(503)")
            if len(newS) > 1:
                prog.update(int((inum/float(len(newS)-1))*100.0),title)
            else:
                prog.update(100,title)
            inum += 1
        
        prog.close()
        self.progLock = False
        for i in self.listitems:
            self.addItem(i)
            
    def listFavorites(self):
        if self.getListSize() > 0:
            self.clearList()
        xbmc.executebuiltin("Container.SetViewMode(503)")
        self.urls=['..']+Favorites().getList()
        self.listitems = ['..']
        self.addItem('..')
        for i in self.urls[1:]:
            desc = ''
            title = i[-1]
            if i[1]:
                epg=i[1].getEntries()
                for e in epg:
                    if (__settings__.getSetting("show24h") == 'false'):
                        desc += e[1].strftime("%I:%M")+'-'+e[2].strftime("%I:%M")+":\n"+e[0]+u"\n\n"
                    else:
                        desc += e[1].strftime("%H:%M")+'-'+e[2].strftime("%H:%M")+":\n"+e[0]+u"\n\n"
                if len(epg) > 0:
                    title +=' - '+epg[0][0]
            item=xbmcgui.ListItem(title, desc, iconImage=i[-2])
            infolabels = { "title": title, "Plot": desc, "plotoutline": desc, "tvshowtitle": title, "originaltitle": title}
            item.setInfo( type="movies", infoLabels=infolabels )
            item.setProperty('IsPlayable', 'true')
            item.setProperty('Plot', desc)
            self.listitems.append(item)
            self.addItem(item)
        self.mode = 3
        xbmc.executebuiltin("Container.SetViewMode(503)")
        
    
    def onAction(self, action):
        action = action.getId() 
        if self.progLock:
            return

        if action == 7 or action == 100:
            if self.mode == 0:
                if self.getCurrentListPosition() == 0:
                    if not self.overlay.player.isPlaying():
                        self.overlay.close()
                    self.close()
                elif self.getCurrentListPosition() == 1 and len(Favorites().getList()) > 0:
                    self.listFavorites()
                    self.setFocusId(503)
                else:
                    if len(Favorites().getList()) > 0:
                        self.listLanguages(self.getCurrentListPosition()-2)
                    else:
                        self.listLanguages(self.getCurrentListPosition()-1)
                    self.setFocusId(503)
            elif self.mode == 1:
                if self.getCurrentListPosition() == 0:
                    self.listSources()
                else:
                    self.listVideos(self.getCurrentListPosition())
                    self.setFocusId(503)
            elif self.mode > 1:
                if self.getCurrentListPosition() == 0:
                    self.curpos = 0
                    if len(self.languages) < 3 or self.mode == 3:
                        self.listSources()
                    else:
                        self.listLanguages(self.src)
                        self.setFocusId(503)
                else:
                    self.curpos = self.getCurrentListPosition()
                    self.overlay.playURL(self.urls[self.getCurrentListPosition()])
                
                        
        elif action == ACTION_PREVIOUS_MENU:
            if self.mode == 2:
                if len(self.languages) > 2:
                    self.listLanguages(self.src)
                    self.setFocusId(503)
                else:
                    self.listSources()
                xbmc.executebuiltin("Container.SetViewMode(50)")
            elif self.mode == 3:
                self.listSources()
                xbmc.executebuiltin("Container.SetViewMode(50)")
            elif self.mode == 1:
                self.listSources()
            elif not self.overlay.player.isPlaying():
                self.overlay.close()
                self.close()
            elif self.mode == 0:
                if xbmc.getCondVisibility('Player.ShowInfo'):
                    xbmc.executehttpapi("SendKey(0xF049)")
                self.close()
        elif action == ACTION_SHOW_INFO:
            if self.mode == 2:
                epgWindow = EPGWindow('MyTVNav.xml',addon.getAddonInfo('path'),'DefaultSkin')
                ep = self.urls[self.getCurrentListPosition()][1].getEntries(20)
                for e in ep:
                    if (__settings__.getSetting("show24h") == 'false'):
                        title = e[1].strftime("%I:%M")+'-'+e[2].strftime("%I:%M")+': '+e[0]
                    else:
                        title = e[1].strftime("%H:%M")+'-'+e[2].strftime("%H:%M")+': '+e[0]
                    listitem = xbmcgui.ListItem(title,iconImage=e[4])
                    listitem.setProperty('Plot',e[3])
                    listitem.setProperty('EPG','1')
                    epgWindow.addItem(listitem)
                epgWindow.doModal()
        elif (action == ACTION_NUMBER_2 or action == ACTION_CONTEXTMENU or action == 117) and self.mode > 1:
            d=xbmcgui.Dialog()
            l = ['Show EPG']
            offset = 0
            if not self.urls[self.getCurrentListPosition()][1]:
                l = []
                offset = 1
            if self.mode == 2:
                l.append('Add to favorites')
            else:
                l.append('Remove from favorites')
            l.append('Report broken channel')    
                
            i=0
            for s in self.urls[self.getCurrentListPosition()][2]:
                l.append('Play backup stream #'+str(i+1))
                i += 1
            l.append('Cancel')
            d=d.select('Menu',l)
            d=d+offset
            if d == len(l) - 1 + offset or d == -1:
                return
            elif d == 0:
                epgWindow = EPGWindow('MyTVNav.xml',addon.getAddonInfo('path'),'DefaultSkin')
                ep = self.urls[self.getCurrentListPosition()][1].getEntries(20)
                for e in ep:
                    if (__settings__.getSetting("show24h") == 'false'):
                        title = e[1].strftime("%I:%M")+'-'+e[2].strftime("%I:%M")+': '+e[0]
                    else:
                        title = e[1].strftime("%H:%M")+'-'+e[2].strftime("%H:%M")+': '+e[0]
                    listitem = xbmcgui.ListItem(title,iconImage=e[4])
                    if e[3]:
                        listitem.setProperty('Plot',e[3])
                    listitem.setProperty('EPG','1')
                    epgWindow.addItem(listitem)
                epgWindow.doModal()
            elif d == 1 and self.mode == 2:
                #Add to favorites
                f=Favorites()
                f.add(self.getListItem(self.getCurrentListPosition()),self.urls[self.getCurrentListPosition()])
                d=xbmcgui.Dialog()
                d.ok("Channel added","The channel has been favorite listed.")
            elif d == 1 and self.mode == 3:
                #Remove from favorites
                f=Favorites()
                f.remove(self.getCurrentListPosition()-1)
                d=xbmcgui.Dialog()
                d.ok("Channel removed","The channel has been favorite removed from the favorites.")
                if len(Favorites().getList()) > 0:
                    self.listFavorites()
                else:
                    self.listSources()
            elif d == 2:
                channel = self.getListItem(self.getCurrentListPosition()).getLabel().split(']')[1][:-3]
                resp = int(getURL('http://supertv.3owl.com/API/brokenchannels.php?channel='+urllib.quote(channel)+'&country='+urllib.quote(BASE[self.src][1])).split('\r\n')[0])
                d=xbmcgui.Dialog()
                if resp == 0:
                    d.ok("Channel reported","The channel was successfully reported as broken.")
                elif resp == 1:
                    d.ok("Channel reported","The channel was reported already and should be","working again soon.")
                elif resp == 2:
                    d.ok("Channel not always online","This channel is not online 24/7.","Please check back later.")
                else:
                    d.ok("Error while reporting channel", "An error occured while reporting the channel, please try again.")
            else:
                self.curpos = self.getCurrentListPosition()
                self.overlay.playURL(self.urls[self.getCurrentListPosition()],d-3)
                

def setVolumeDiff(volume):
    setvolume_query = '{"jsonrpc": "2.0", "method": "Application.GetProperties", "params": { "properties": [ "volume"] }, "id": 1}'
    vol=json.loads(xbmc.executeJSONRPC (setvolume_query))['result']['volume']+volume
    xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Application.SetVolume", "params": { "volume": ' +str(vol) + '}, "id": 1}')
 
willClose = False
class StreamPlayer(xbmc.Player):
    chanlist = None
    overlay = None
    def onPlayBackStopped(self):
        global willClose
        global t
        if t:
            t.cancel()
        self.overlay.close()
        if not willClose:
            self.overlay.curPlaying = []
            self.overlay.chanlist.doModal()
    def onPlayBackEnded(self):
        global t
        global willClose
        if t:
            t.cancel()
        self.overlay.close()
        if not willClose:
            self.overlay.curPlaying = []
            self.overlay.chanlist.doModal()
        
class EPGWindow(xbmcgui.WindowXMLDialog):
    def onAction(self,action):
        try: 
            action = int(action)
        except:
            action = action.getId()
            
        if action == ACTION_SHOW_INFO:
            if xbmc.getCondVisibility('Player.ShowInfo'):
                xbmc.executehttpapi("SendKey(0xF049)")
        elif action != ACTION_MOVE_UP and action != ACTION_MOVE_DOWN:
            self.close()
        
        
class Main(xbmcgui.WindowDialog):
    curPlaying=[]
    player=StreamPlayer()
    chanlist=ChannelList('MyTVNav.xml',addon.getAddonInfo('path'), 'DefaultSkin')
    def __init__(self):
        super(xbmcgui.WindowDialog, self).__init__()
        self.player.chanlist = self.chanlist
        self.chanlist.overlay = self
        self.player.overlay = self
        self.chanlist.listSources()
        self.chanlist.doModal()
        
    def playURL(self, url, backup=-1):
        global filmOnKeepAlive
        filmOnKeepAlive.cancel()
        if not self.player.isPlaying or (not self.curPlaying or self.curPlaying != url):
            self.curPlaying = url
            if backup > -1:
                url = [url[2][backup]]
                self.curPlaying[0] = url
            print url
            if url[0].split('|')[0] == 'filmon':
                newurl = filmOnUpdate('|'.join(url[0].split('|')[1:]))
            elif url[0].split('|')[0] == 'telecinco':
                newurl = update45ESToken('|'.join(url[0].split('|')[1:]))
            else:
                newurl = url[0]
            self.player.play(newurl)
        self.chanlist.close()
        self.doModal()
        
    def onAction(self, action):
        try: 
            action = int(action)
            if action == 7:
                return
        except:
            action = action.getId()
        
        if action == ACTION_PREVIOUS_MENU or action == 122 or action == 13:
            global willClose
            willClose = True
            self.player.stop()
            self.chanlist.close()
            self.close()
        elif action == ACTION_MOVE_LEFT:
            setVolumeDiff(-5)
        elif action == ACTION_MOVE_RIGHT:
            setVolumeDiff(5)
        elif action in [ACTION_MOVE_UP,ACTION_MOVE_DOWN]:
            self.chanlist.doModal()
        elif action == ACTION_NUMBER_1:
            self.close()
            xbmc.executehttpapi("SendKey(0xF05A)")
            self.doModal()
        elif action == ACTION_SHOW_INFO or action == ACTION_CONTEXTMENU:
            if xbmc.getCondVisibility('Player.ShowInfo'):
                self.close()
                xbmc.executehttpapi("SendKey(0xF049)")
                self.doModal()
            d=xbmcgui.Dialog()
            l = ['Show EPG']
            offset = 0
            if not self.curPlaying[1]:
                l = []
                offset = 1
            l.append('Change aspect ratio')
            i=0
            for s in self.curPlaying[2]:
                l.append('Play backup stream #'+str(i+1))
                i += 1
            l.append('Exit')
            l.append('Cancel')
            d=d.select('Menu',l)
            d=d+offset
            if d == len(l) - 1 + offset or d == -1:
                return
            elif d == len(l) - 2:
                willClose = True
                self.player.stop()
                self.chanlist.close()
                self.close()
            elif d == 0:
                epgWindow = EPGWindow('MyTVNav.xml',addon.getAddonInfo('path'),'DefaultSkin')
                ep = self.curPlaying[1].getEntries(20)
                for e in ep:
                    if (__settings__.getSetting("show24h") == 'false'):
                        title = e[1].strftime("%I:%M")+'-'+e[2].strftime("%I:%M")+': '+e[0]
                    else:
                        title = e[1].strftime("%H:%M")+'-'+e[2].strftime("%H:%M")+': '+e[0]
                    listitem = xbmcgui.ListItem(title,iconImage=e[4])
                    listitem.setProperty('Plot',e[3])
                    listitem.setProperty('EPG','1')
                    epgWindow.addItem(listitem)
                epgWindow.doModal()
            elif d == 1:
                self.close()
                xbmc.executehttpapi("SendKey(0xF05A)")
                self.doModal()
            else:
                self.playURL(self.curPlaying,d-2)

def main(b):
    global BASE
    BASE = b
    checkAutoupdateEPG()
    Main()