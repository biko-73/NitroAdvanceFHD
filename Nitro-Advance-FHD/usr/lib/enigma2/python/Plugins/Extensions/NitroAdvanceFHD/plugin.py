#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

#This plugin is free software, you are allowed to
#modify it (if you keep the license),
#but you are not allowed to distribute/publish
#it without source code (this version and your modifications).
#This means you also have to distribute
#source code of your modifications.

# for localized messages
from .__init__ import _
from enigma import eTimer, getDesktop
from Components.ActionMap import ActionMap
from Tools.Directories import *
from Components.config import *
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Plugins.Plugin import PluginDescriptor
from Screens.SkinSelector import SkinSelector
from Screens.InputBox import InputBox
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Tools.LoadPixmap import LoadPixmap
from Tools import Notifications
from Tools.Notifications import AddPopup
from os import listdir, remove, rename, system, path, symlink, chdir, makedirs, mkdir
from os import path as os_path, remove as os_remove
import requests
import shutil
import re, os

from six.moves.urllib.request import urlretrieve
from .compat import compat_urlopen, compat_Request, compat_URLError, PY3

cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')

reswidth = getDesktop(0).size().width()

config.plugins.NitroAdvanceFHD = ConfigSubsection()
config.plugins.NitroAdvanceFHD.refreshInterval = ConfigNumber(default=10)
config.plugins.NitroAdvanceFHD.woeid = ConfigNumber(default = 638242)
config.plugins.NitroAdvanceFHD.degreetype = ConfigSelection(default="Celsius", choices = [
                                ("Celsius", _("Celsius")),
                                ("Fahrenheit", _("Fahrenheit"))
                                ])
config.plugins.NitroAdvanceFHD.city = ConfigText(default="Manama", visible_width = 250, fixed_size = False)
config.plugins.NitroAdvanceFHD.weather_location = ConfigText(default="bh-BH", visible_width = 250, fixed_size = False)

REDC = '\033[31m'
ENDC = '\033[m'

def cprint(text):
    print(REDC + text + ENDC)

def removeunicode(data):
    try:
        try:
                data = data.encode('utf', 'ignore')
        except:
                pass
        data = data.decode('unicode_escape').encode('ascii', 'replace').replace('?', '').strip()
    except:
        pass
    return data

def trace_error():
    import sys
    import traceback
    try:
        traceback.print_exc(file=sys.stdout)
        traceback.print_exc(file=open('/tmp/NitroAdvanceFHD.log', 'a'))
    except:
        pass

def logdata(label_name = '', data = None):
    try:
        data=str(data)
        fp = open('/tmp/NitroAdvanceFHD.log', 'a')
        fp.write( str(label_name) + ': ' + data+"\n")
        fp.close()
    except:
        trace_error()
        pass

def Plugins(**kwargs):
    return [PluginDescriptor(name=_("NitroAdvanceFHD Config tool"), description=_("NitroAdvanceFHD (Skin by Kaleem_Club)"), where = [PluginDescriptor.WHERE_PLUGINMENU],
    icon="plugin.png", fnc=main)]

def main(session, **kwargs):
    if config.skin.primary_skin.value == "NitroAdvanceFHD/skin.xml":
        session.open(NitroAdvanceFHD_Config)
    else:
        AddPopup(_('Please activate NitroAdvanceFHD Skin before run the Config Plugin'), type=MessageBox.TYPE_ERROR, timeout=10)
        return []

def isInteger(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def downloadFile(url, filePath):
    try:
            urlretrieve(url, filePath)
            return True
            req = compat_Request(url)
            response = compat_urlopen(req)      
            cprint("response.read",response.read())
            output = open(filePath, 'wb')
            output.write(response.read())
            output.close()
            response.close()
            return True
    except compat_URLError as e:
            trace_error()
            if hasattr(e, 'code'):
                cprint('We failed with error code - %s.' % e.code)
            elif hasattr(e, 'reason'):
                cprint('We failed to reach a server.')
                cprint('Reason: %s' % e.reason)
    return False

def readurl(url):
    try:
            req = compat_Request(url)
            response = compat_urlopen(req)
            data = response.read()
            response.close()
            cprint("[data %s]" % data)
            return data
    except compat_URLError as e:
            if hasattr(e, 'code'):
                cprint('We failed with error code - %s.' % e.code)
            elif hasattr(e, 'reason'):
                cprint('We failed to reach a server.')
                cprint('Reason: %s' % e.reason)

def getcities(weather_location):
    import requests,re
    S = requests.Session()
    url = (b"http://www.geonames.org/advanced-search.html?q=&country=%s&featureClass=P&startRow=".decode("utf-8")) % str(weather_location.upper())
    pages = range(0, 1501, 50) ## change 2001 as page you want
    try:
        cities=[]
        for page in pages:
                ##Change the startRow in the URL
                url_2 = url.replace("startRow=","startRow="+str(page))
                request = requests.get(url_2)
                if request.status_code == 200:
                        data = S.get(url_2, verify=False).content.decode('ascii', 'ignore')
                        blocks = str(data).split('alt="P">')
                        blocks.pop(0)
                        for block in blocks:
                                regx='''<a href="(.*?)">.*?</a>'''
                                href = re.findall(regx, block)[0]
                                if not PY3:
                                	cityName = os.path.split(href)[1].replace(".html","").replace("-"," ").lstrip(' ')
                                else:
                                	cityName = os.path.split(href)[1].replace(".html","").replace("-","_").lstrip(' ')
                                cities.append(cityName)
                        cities.sort()
    except Exception as error:
                cprint('excepyion',str(error))
                trace_error()
    cities.sort()
    return cities

class WeatherLocationChoiceList(Screen):
        skin = """
                <screen name="WeatherLocationChoiceList" position="center,center" size="1280,720" title="Location list" >
                        <widget source="Title" render="Label" position="70,47" size="950,43" font="Regular;35" transparent="1" />
                        <widget name="choicelist" position="70,115" size="700,480" scrollbarMode="showOnDemand" scrollbarWidth="6" transparent="1" />
                        <eLabel position=" 55,675" size="290, 5" zPosition="-10" backgroundColor="red" />
                        <eLabel position="350,675" size="290, 5" zPosition="-10" backgroundColor="green" />
                        <eLabel position="645,675" size="290, 5" zPosition="-10" backgroundColor="yellow" />
                        <eLabel position="940,675" size="290, 5" zPosition="-10" backgroundColor="blue" />
                        <widget name="key_red" position="70,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="foreground" transparent="1" />
                        <widget name="key_green" position="365,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="foreground" transparent="1" />
                </screen>
                """

        def __init__(self, session, country):
                self.session = session
                self.country = country
                list = []
                Screen.__init__(self, session)
                self.title = _(country)
                self["choicelist"] = MenuList(list)
                self["key_red"] = Label(_("Cancel"))
                self["key_green"] = Label(_("Add city"))
                self["myActionMap"] = ActionMap(["SetupActions", "ColorActions"],
                {
                        "ok": self.keyOk,
                        "green": self.add_city,
                        "cancel": self.keyCancel,
                        "red": self.keyCancel,
                }, -1)           
                self.timer = eTimer()
                try:
                        self.timer.callback.append(self.createChoiceList)
                except:
                        self.timer_conn = self.timer.timeout.connect(self.createChoiceList)
                self.timer.start(5, False)

        def createChoiceList(self):
                self.timer.stop()
                clist = []
                clist = getcities(self.country)
                self["choicelist"].l.setList(clist)

        def control_xml(self, result, retval, extra_args):
                if retval != 0:
                        self.write_none()

        def write_none(self):
                with open('/tmp/NitroAdvanceFHDmsn.xml', 'w') as noneweather:
                        noneweather.write('None')
                noneweather.close()

        def get_xmlfile(self, weather_city, weather_location):
                degreetype = config.plugins.NitroAdvanceFHD.degreetype.value
                weather_city = removeunicode(weather_city)
                weather_city = weather_city.decode("utf-8")
                url = 'http://weather.service.msn.com/data.aspx?weadegreetype=%s&culture=%s&weasearchstr=%s&src=outlook' % (degreetype, weather_location, weather_city)
                file_name ='/tmp/NitroAdvanceFHDmsn.xml'
                try:
                       ret = downloadFile(url, file_name)
                       return ret
                except Exception as error:
                       trace_error()
                       return False

        def add_city(self):
                 self.session.openWithCallback(self.cityCallback, InputBox, title=_("Please enter a name of the city"), text="cityname", maxSize=False, visible_width =250)

        def cityCallback(self,city=None):
                try:
                        if os_path.exists('/tmp/NitroAdvanceFHDmsn.xml'):
                                os_remove('/tmp/NitroAdvanceFHDmsn.xml')
                        returnValue = self["choicelist"].l.getCurrentSelection()
                        countryCode=self.country.lower()+"-"+self.country.upper()
                        if self.get_xmlfile(returnValue,countryCode)==False:
                                self.session.open(MessageBox, _("Sorry, your city != available1."),MessageBox.TYPE_ERROR)
                                return 
                        if not fileExists('/tmp/NitroAdvanceFHDmsn.xml'):
                                self.write_none()
                                self.session.open(MessageBox, _("Sorry, your city != available2."),MessageBox.TYPE_ERROR)
                                return None
                        if returnValue != None:
                                self.close(returnValue)
                        else:
                                self.keyCancel()
                except Exception as error:
                        trace_error()

        def keyOk(self):
                try:
                        if os_path.exists('/tmp/NitroAdvanceFHDmsn.xml'):
                                os_remove('/tmp/NitroAdvanceFHDmsn.xml')
                        returnValue = self["choicelist"].l.getCurrentSelection()
                        countryCode = self.country.lower() + "-" + self.country.upper()
                        if self.get_xmlfile(returnValue,countryCode)==False:
                                self.session.open(MessageBox, _("Sorry, your city != available."),MessageBox.TYPE_ERROR)
                                return 
                        if not fileExists('/tmp/NitroAdvanceFHDmsn.xml'):
                                self.write_none()
                                self.session.open(MessageBox, _("Sorry, your city != available."),MessageBox.TYPE_ERROR)
                                return None
                        if returnValue != None:
                                self.close(returnValue)
                        else:
                                self.keyCancel()
                except Exception as error:
                        trace_error()

        def keyCancel(self):
                self.close(None)


class NitroAdvanceFHD_Config(Screen, ConfigListScreen):

    skin = """
            <screen name="NitroAdvanceFHD_Config" position="center,center" size="1300,700" title="NitroAdvanceFHD Setup">
                    <ePixmap position="-1,0" size="1300,700" pixmap="NitroAdvanceFHD/construct/backgrounds/background-window-title.png" alphatest="blend" zPosition="-50" />
                    <widget name="config" position="25,58" size="775,502" font="Regular;34" itemHeight="45" enableWrapAround="1" transparent="1"/>
                    <widget name="Picture" position="660,50" size="600,400" alphatest="on" />
                    <ePixmap pixmap="NitroAdvanceFHD/buttons/red45x45.png" position="20,650" size="45,45" alphatest="blend" />
                    <ePixmap pixmap="NitroAdvanceFHD/buttons/green45x45.png" position="315,650" size="45,45" alphatest="blend" />
                    <ePixmap pixmap="NitroAdvanceFHD/buttons/yellow45x45.png" position="610,650" size="45,45" alphatest="blend" />
                    <ePixmap pixmap="NitroAdvanceFHD/buttons/blue45x45.png" position="905,650" size="45,45" alphatest="blend" />
                    <widget render="Label" source="key_red" position="65,650" size="250,45" zPosition="1" font="Regular;30" halign="center" valign="center" backgroundColor="background" transparent="1" foregroundColor="foreground" />
                    <widget name="key_green" position="360,650" size="250,45" zPosition="1" font="Regular;30" halign="center" valign="center" backgroundColor="background" transparent="1" foregroundColor="foreground" />
                    <widget name="key_yellow" position="655,650" size="250,45" zPosition="1" font="Regular;30" halign="center" valign="center" backgroundColor="background" transparent="1" foregroundColor="foreground" />
                    <widget render="Label" source="key_blue" position="950,650" size="250,45" zPosition="1" font="Regular;30" halign="center" valign="center" backgroundColor="background" transparent="1" foregroundColor="foreground" />
                    <ePixmap pixmap="NitroAdvanceFHD/mn.png" position="1223,655" size="60,30" zPosition="10" transparent="0" />
                    <eLabel text="Weather Setup .... Press Ok Button to get to the weather plugin" position="729,481" size="470,140" font="Regular;36" backgroundColor="background" transparent="1" valign="top" foregroundColor="foreground" zPosition="2" />
            </screen>
    """

    def __init__(self, session, args = 0):
        self.session = session
        self.changed_screens = False
        Screen.__init__(self, session)

        self.start_skin = config.skin.primary_skin.value
        if self.start_skin != "skin.xml":
        	self.getInitConfig()

        self.list = []
        ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)
        self.configChanged = False
        self["key_red"] = Label(_("Cancel"))
        self["key_green"] = Label(_("OK"))
        self["key_yellow"] = Label()
        self["key_blue"] = Label(_("About"))
        self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
                {
                        "green": self.keyGreen,
                        "red": self.cancel,
                        "yellow": self.keyYellow,
                        "blue": self.about,
                        "cancel": self.cancel,
                        "ok": self.keyOk,
                }, -2)

        self["Picture"] = Pixmap()

        if not self.selectionChanged in self["config"].onSelectionChanged:
            self["config"].onSelectionChanged.append(self.selectionChanged)
        self.createConfigList()
        if self.start_skin == "skin.xml":
            self.onLayoutFinish.append(self.openSkinSelectorDelayed)
        else:
            self.createConfigList()

    def getInitConfig(self):

        global cur_skin

        self.title = _("%s Setup" % cur_skin)
        self.skin_base_dir = "/usr/share/enigma2/%s/" % cur_skin
        cprint("self.skin_base_dir=%s, skin=%s, currentSkin=%s" % (self.skin_base_dir, config.skin.primary_skin.value, cur_skin))

        self.default_font_file = "font_Original.xml"
        self.default_color_file = "color_Original.xml"
        self.default_interface_file = "interface_Original.xml"

        self.color_file = "skin_user_color.xml"
        self.interface_file = "skin_user_interface.xml"

        # color
        current, choices = self.getSettings(self.default_color_file, self.color_file)
        self.NitroAdvanceFHD_color = NoSave(ConfigSelection(default=current, choices = choices))
        # interface
        current, choices = self.getSettings(self.default_interface_file, self.interface_file)
        self.NitroAdvanceFHD_interface = NoSave(ConfigSelection(default=current, choices = choices))
        # myatile
        myatile_active = self.getmyAtileState()
        self.NitroAdvanceFHD_active = NoSave(ConfigYesNo(default=myatile_active))
        self.NitroAdvanceFHD_fake_entry = NoSave(ConfigNothing())

    def getSettings(self, default_file, user_file):
        # default setting
        default = ("default", _("Default"))

        # search typ
        styp = default_file.replace('_Original.xml', '')
        search_str = '%s_' % styp

        # possible setting
        choices = []
        files = listdir(self.skin_base_dir)
        if path.exists(self.skin_base_dir + 'allScreens/%s/' % styp):
            files += listdir(self.skin_base_dir + 'allScreens/%s/' % styp)
        for f in sorted(files, key=str.lower):
            if f.endswith('.xml') and f.startswith(search_str):
                friendly_name = f.replace(search_str, "").replace(".xml", "").replace("_", " ")
                if path.exists(self.skin_base_dir + 'allScreens/%s/%s' %(styp, f)):
                    choices.append((self.skin_base_dir + 'allScreens/%s/%s' %(styp, f), friendly_name))
                else:
                    choices.append((self.skin_base_dir + f, friendly_name))
        choices.append(default)

        # current setting
        myfile = self.skin_base_dir + user_file
        current = ''
        if not path.exists(myfile):
            if path.exists(self.skin_base_dir + default_file):
                if path.islink(myfile):
                    remove(myfile)
                chdir(self.skin_base_dir)
                symlink(default_file, user_file)
            elif path.exists(self.skin_base_dir + 'allScreens/%s/%s' % (styp, default_file)):
                if path.islink(myfile):
                    remove(myfile)
                chdir(self.skin_base_dir)
                symlink(self.skin_base_dir + 'allScreens/%s/%s' %(styp, default_file), user_file)
            else:
                current = None
        if current is None:
            current = default
        else:
            filename = path.realpath(myfile)
            friendly_name = path.basename(filename).replace(search_str, "").replace(".xml", "").replace("_", " ")
            current = (filename, friendly_name)

        return current[0], choices

        #SELECTED Skins folder - We use different folder name (more meaningfull) for selections
        if path.exists(self.skin_base_dir + "mySkin_off"):
        	if not path.exists(self.skin_base_dir + "NitroAdvanceFHD_Selections"):
        		chdir(self.skin_base_dir)
        		try:
        			rename("mySkin_off", "NitroAdvanceFHD_Selections")
        		except:
        			pass

    def createConfigList(self):
        self.set_color = getConfigListEntry(_("Color:"), self.NitroAdvanceFHD_color)
        self.set_interface = getConfigListEntry(_("Interface:"), self.NitroAdvanceFHD_interface)
        self.set_myatile = getConfigListEntry(_("Enable %s pro:") % cur_skin, self.NitroAdvanceFHD_active)
        self.set_new_skin = getConfigListEntry(_("Change skin"), ConfigNothing())
        self.set_degreetype = getConfigListEntry(_("Temperature Unit:"), config.plugins.NitroAdvanceFHD.degreetype)
        self.set_city = getConfigListEntry(_("Location #press OK to change:"), config.plugins.NitroAdvanceFHD.city)
        self.LackOfFile = ''
        self.list = []
        self.list.append(self.set_myatile)
        if len(self.NitroAdvanceFHD_color.choices)>1:
            self.list.append(self.set_color)
        if len(self.NitroAdvanceFHD_interface.choices)>1:
            self.list.append(self.set_interface)
        self.list.append(self.set_new_skin)
        self.list.append(self.set_degreetype)
        self.list.append(self.set_city)
        self["config"].list = self.list
        self["config"].l.setList(self.list)
        if self.NitroAdvanceFHD_active.value:
            self["key_yellow"].setText("%s pro" % cur_skin)
        else:
            self["key_yellow"].setText("")

    def changedEntry(self):
        self.configChanged = True 
        if self["config"].getCurrent() == self.set_color:
            self.setPicture(self.NitroAdvanceFHD_color.value)
        elif self["config"].getCurrent() == self.set_interface:
            self.setPicture(self.NitroAdvanceFHD_interface.value)
        elif self["config"].getCurrent() == self.set_myatile:
            if self.NitroAdvanceFHD_active.value:
                self["key_yellow"].setText("%s pro" % cur_skin)
            else:
                self["key_yellow"].setText("")
            self.createConfigList()

    def selectionChanged(self):
        if self["config"].getCurrent() == self.set_color:
            self.setPicture(self.NitroAdvanceFHD_color.value)
        elif self["config"].getCurrent() == self.set_interface:
            self.setPicture(self.NitroAdvanceFHD_interface.value)
        else:
            self["Picture"].hide()

    def cancel(self):
        if self["config"].isChanged():
            self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Really close without saving settings?"), MessageBox.TYPE_YESNO, default = False)
        else:
            for x in self["config"].list:
                x[1].cancel()
            if self.changed_screens:
                self.restartGUI()
            else:
                self.close()

    def cancelConfirm(self, result):
        if result == None or result == False:
            print("[%s]: Cancel confirmed." % cur_skin)
        else:
            print("[%s]: Cancel confirmed. Config changes will be lost." % cur_skin)
            for x in self["config"].list:
                	x[1].cancel()
            self.close()

    def getmyAtileState(self):
        chdir(self.skin_base_dir)
        if path.exists("mySkin"):
            return True
        else:
            return False

    def setPicture(self, f):
        pic = f.split('/')[-1].replace(".xml", ".png")
        preview = self.skin_base_dir + "preview/preview_" + pic
        if path.exists(preview):
            self["Picture"].instance.setPixmapFromFile(preview)
            self["Picture"].show()
        else:
            self["Picture"].hide()

    def keyYellow(self):
        if self.NitroAdvanceFHD_active.value:
            self.session.openWithCallback(self.NitroAdvanceFHDScreenCB, NitroAdvanceFHDScreens)
        else:
            self["config"].setCurrentIndex(0)

    def keyOk(self):
        sel =  self["config"].getCurrent()
        if sel != None and sel == self.set_city:
            countriesFile = resolveFilename(SCOPE_PLUGINS, 'Extensions/NitroAdvanceFHD/countries')
            countries = open(countriesFile).readlines()
            clist = []
            for country in countries:
                countryCode,countryName=country.split(",")
                clist.append((countryName,countryCode))
            from Screens.ChoiceBox import ChoiceBox
            self.session.openWithCallback(self.choicesback, ChoiceBox, _('select your country'), clist)
        elif sel != None and sel == self.set_new_skin:
            self.openSkinSelector()
        else:
            self.keyGreen()

    def choicesback(self, select):
        if select:
            self.country = select[1]
            config.plugins.NitroAdvanceFHD.weather_location.value = self.country.lower() + "-" + self.country.upper()
            config.plugins.NitroAdvanceFHD.weather_location.save()
            self.session.openWithCallback(self.citiesback, WeatherLocationChoiceList, self.country)
                    
    def citiesback(self,select):
        if select:
            weather_city = select
            weather_city.capitalize() 
            config.plugins.NitroAdvanceFHD.city.setValue(weather_city)
            self.createConfigList()

    def openSkinSelector(self):
        self.session.openWithCallback(self.skinChanged, SkinSelector)

    def openSkinSelectorDelayed(self):
        self.delaytimer = eTimer()
        self.delaytimer.callback.append(self.openSkinSelector)
        self.delaytimer.start(200, True)

    def skinChanged(self, ret = None):
        global cur_skin
        cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
        if cur_skin == "skin.xml":
            self.restartGUI()
        else:
            self.getInitConfig()
            self.createConfigList()

    def keyGreen(self):
        if self["config"].isChanged():
            for x in self["config"].list:
                	x[1].save()
            chdir(self.skin_base_dir)
            # color
            self.makeSettings(self.NitroAdvanceFHD_color, self.color_file)
            # interface
            self.makeSettings(self.NitroAdvanceFHD_interface, self.interface_file)
            #Pro SCREENS
            if not path.exists("mySkin_off"):
                mkdir("mySkin_off")
                print("makedir mySkin_off")
            if self.NitroAdvanceFHD_active.value:
                if not path.exists("mySkin") and path.exists("mySkin_off"):
                    symlink("mySkin_off", "mySkin")
            else:
                if path.exists("mySkin"):
                    if path.exists("mySkin_off"):
                        if path.islink("mySkin"):
                            remove("mySkin")
                        else:
                            shutil.rmtree("mySkin")
                    else:
                        rename("mySkin", "mySkin_off")
            self.update_user_skin()
            self.restartGUI()
        elif  config.skin.primary_skin.value != self.start_skin:
            self.update_user_skin()
            self.restartGUI()
        else:
            if self.changed_screens:
                self.update_user_skin()
                self.restartGUI()
            else:
                self.close()

    def makeSettings(self, config_entry, user_file):
        if path.exists(user_file):
            remove(user_file)
        if path.islink(user_file):
            remove(user_file)
        if config_entry.value != 'default':
            symlink(config_entry.value, user_file)

    def NitroAdvanceFHDScreenCB(self):
        self.changed_screens = True
        self["config"].setCurrentIndex(0)

    def restartGUI(self):
        myMessage = ''
        if self.LackOfFile != '':
            cprint("missing components: %s" % self.LackOfFile)
            myMessage += _("Missing components found: %s\n\n") % self.LackOfFile
            myMessage += _("Skin will NOT work properly!!!\n\n")
        restartbox = self.session.openWithCallback(self.restartGUIcb, MessageBox, _("Restart necessary, restart GUI now?"), MessageBox.TYPE_YESNO)
        restartbox.setTitle(_("Message"))

    def about(self):
        self.session.open(NitroAdvanceFHD_About)

    def restartGUIcb(self, answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()

    def update_user_skin(self):
        global cur_skin
        user_skin_file = resolveFilename(SCOPE_CONFIG, 'skin_user_' + cur_skin + '.xml')
        if path.exists(user_skin_file):
            remove(user_skin_file)
        cprint("update_user_skin.self.NitroAdvanceFHD_active.value")
        user_skin = ""
        if path.exists(self.skin_base_dir + self.color_file):
            user_skin = user_skin + self.readXMLfile(self.skin_base_dir + self.color_file, 'ALLSECTIONS')
        if path.exists(self.skin_base_dir + self.interface_file):
            user_skin = user_skin + self.readXMLfile(self.skin_base_dir + self.interface_file, 'ALLSECTIONS')
        if path.exists(self.skin_base_dir + 'mySkin'):
            for f in listdir(self.skin_base_dir + "mySkin/"):
                user_skin = user_skin + self.readXMLfile(self.skin_base_dir + "mySkin/" + f, 'screen')
        if user_skin != '':
            user_skin = "<skin>\n" + user_skin
            user_skin = user_skin + "</skin>\n"
            with open(user_skin_file, "w") as myFile:
                cprint("update_user_skin.self.NitroAdvanceFHD_active.value write myFile")
                myFile.write(user_skin)
                myFile.flush()
                myFile.close()
        #checking if all renderers converters are in system
        self.checkComponent(user_skin, 'render', resolveFilename(SCOPE_PLUGINS, '../Components/Renderer/') )
        self.checkComponent(user_skin, 'Convert', resolveFilename(SCOPE_PLUGINS, '../Components/Converter/') )
        self.checkComponent(user_skin, 'pixmap', resolveFilename(SCOPE_SKIN, '') )
               
    def checkComponent(self, myContent, look4Component, myPath): #look4Component=render|
        def updateLackOfFile(name, mySeparator =', '):
                cprint("Missing component found:%s\n" % name)
                if self.LackOfFile == '':
                        self.LackOfFile = name
                else:
                        self.LackOfFile += mySeparator + name
            
        r=re.findall( r' %s="([a-zA-Z0-9_/\.]+)" ' % look4Component, myContent )
        r=list(set(r)) #remove duplicates, no need to check for the same component several times

        cprint("Found %s:\n" % (look4Component))
        print(r)
        if r:
                for myComponent in set(r):
                        if look4Component == 'pixmap':
                                if myComponent.startswith('/'):
                                        if not path.exists(myComponent):
                                                updateLackOfFile(myComponent, '\n')
                                else:
                                        if not path.exists(myPath + myComponent):
                                                updateLackOfFile(myComponent)
                        else:
                                if not path.exists(myPath + myComponent + ".pyo") and not path.exists(myPath + myComponent + ".py") and not path.exists(myPath + myComponent + ".pyc"):
                                        updateLackOfFile(myComponent)
        return
    
    def readXMLfile(self, XMLfilename, XMLsection): #sections:ALLSECTIONS|fonts|
        myPath=path.realpath(XMLfilename)
        if not path.exists(myPath):
                remove(XMLfilename)
                return ''
        filecontent = ''
        if XMLsection == 'ALLSECTIONS':
                sectionmarker = True
        else:
                sectionmarker = False
        with open (XMLfilename, "r") as myFile:
                for line in myFile:
                        if line.find('<skin>') >= 0 or line.find('</skin>') >= 0:
                                continue
                        if line.find('<%s' %XMLsection) >= 0 and sectionmarker == False:
                                sectionmarker = True
                        elif line.find('</%s>' %XMLsection) >= 0 and sectionmarker == True:
                                sectionmarker = False
                                filecontent = filecontent + line
                        if sectionmarker == True:
                                filecontent = filecontent + line
                myFile.close()
        return filecontent

class NitroAdvanceFHD_About(Screen):

    def __init__(self, session, args = 0):
        self.session = session
        Screen.__init__(self, session)
        self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
                {
                        "cancel": self.cancel,
                        "ok": self.keyOk,
                }, -2)

    def keyOk(self):
        self.close()

    def cancel(self):
        self.close()

class NitroAdvanceFHDScreens(Screen):

    skin = """
            <screen name="NitroAdvanceFHDScreens" position="center,center" size="1280,720" title="NitroAdvanceFHD Setup">
                    <widget source="Title" render="Label" position="70,47" size="950,43" font="Regular;35" transparent="1" />
                    <widget source="menu" render="Listbox" position="70,115" size="700,480" scrollbarMode="showOnDemand" scrollbarWidth="6" scrollbarSliderBorderWidth="1" enableWrapAround="1" transparent="1">
                            <convert type="TemplatedMultiContent">
                                    {"template":
                                            [
                                                    MultiContentEntryPixmapAlphaTest(pos = (2, 2), size = (25, 24), png = 2),
                                                    MultiContentEntryText(pos = (35, 4), size = (500, 24), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 1),
                                            ],
                                            "fonts": [gFont("Regular", 22),gFont("Regular", 16)],
                                            "itemHeight": 30
                                    }
                            </convert>
                    </widget>
                    <widget name="Picture" position="808,342" size="400,225" alphatest="on" />
                    <eLabel position=" 55,675" size="290, 5" zPosition="-10" backgroundColor="red" />
                    <eLabel position="350,675" size="290, 5" zPosition="-10" backgroundColor="green" />
                    <widget source="key_red" render="Label" position="70,635" size="260,25" zPosition="1" font="Regular;20" halign="left" transparent="1" />
                    <widget source="key_green" render="Label" position="365,635" size="260,25" zPosition="1" font="Regular;20" halign="left" transparent="1" />
            </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session

        global cur_skin
        self.is_atile = False
        if cur_skin == 'NitroAdvanceFHD':
            self.is_atile = True

        self.title = _("%s additional screens") % cur_skin
        try:
            self["title"]=StaticText(self.title)
        except:
            print('self["title"] was not found in skin')

        self["key_red"] = StaticText(_("Exit"))
        self["key_green"] = StaticText(_("on"))
        self["Picture"] = Pixmap()
        menu_list = []
        self["menu"] = List(menu_list)
        self["shortcuts"] = ActionMap(["SetupActions", "ColorActions", "DirectionActions"],
        {
                "ok": self.runMenuEntry,
                "cancel": self.keyCancel,
                "red": self.keyCancel,
                "green": self.runMenuEntry,
        }, -2)

        self.skin_base_dir = "/usr/share/enigma2/%s/" % cur_skin
        self.screen_dir = "allScreens"
        self.skinparts_dir = "skinparts"
        self.file_dir = "mySkin_off"
        my_path = resolveFilename(SCOPE_SKIN, "%s/icons/lock_on.png" % cur_skin)
        if not path.exists(my_path):
            my_path = resolveFilename(SCOPE_SKIN, "skin_default/icons/lock_on.png")
        self.enabled_pic = LoadPixmap(cached = True, path = my_path)
        my_path = resolveFilename(SCOPE_SKIN, "%s/icons/lock_off.png" % cur_skin)
        if not path.exists(my_path):
            my_path = resolveFilename(SCOPE_SKIN, "skin_default/icons/lock_off.png")
        self.disabled_pic = LoadPixmap(cached = True, path = my_path)

        if not self.selectionChanged in self["menu"].onSelectionChanged:
            self["menu"].onSelectionChanged.append(self.selectionChanged)

        self.onLayoutFinish.append(self.createMenuList)

    def selectionChanged(self):
        sel = self["menu"].getCurrent()
        if sel is not None:
            self.setPicture(sel[0])
            if sel[2] == self.enabled_pic:
                self["key_green"].setText(_("off"))
            elif sel[2] == self.disabled_pic:
                self["key_green"].setText(_("on"))

    def createMenuList(self):
        chdir(self.skin_base_dir)
        f_list = []
        dir_path = self.skin_base_dir + self.screen_dir
        if not path.exists(dir_path):
            makedirs(dir_path)
        dir_skinparts_path = self.skin_base_dir + self.skinparts_dir
        if not path.exists(dir_skinparts_path):
            makedirs(dir_skinparts_path)
        file_dir_path = self.skin_base_dir + self.file_dir
        if not path.exists(file_dir_path):
            makedirs(file_dir_path)
        dir_global_skinparts = resolveFilename(SCOPE_SKIN, "skinparts")
        if path.exists(dir_global_skinparts):
            for pack in listdir(dir_global_skinparts):
                if path.isdir(dir_global_skinparts + "/" + pack):
                    for f in listdir(dir_global_skinparts + "/" + pack):
                        if path.exists(dir_global_skinparts + "/" + pack + "/" + f + "/" + f + "_Atile.xml"):
                            if not path.exists(dir_path + "/skin_" + f + ".xml"):
                                symlink(dir_global_skinparts + "/" + pack + "/" + f + "/" + f + "_Atile.xml", dir_path + "/skin_" + f + ".xml")
                            if not path.exists(dir_skinparts_path + "/" + f):
                                symlink(dir_global_skinparts + "/" + pack + "/" + f, dir_skinparts_path + "/" + f)
        list_dir = sorted(listdir(dir_path), key=str.lower)
        for f in list_dir:
            if f.endswith('.xml') and f.startswith('skin_'):
                if (not path.islink(dir_path + "/" + f)) or os.path.exists(os.readlink(dir_path + "/" + f)):
                    friendly_name = f.replace("skin_", "")
                    friendly_name = friendly_name.replace(".xml", "")
                    friendly_name = friendly_name.replace("_", " ")
                    linked_file = file_dir_path + "/" + f
                    if path.exists(linked_file):
                        if path.islink(linked_file):
                            pic = self.enabled_pic
                        else:
                            remove(linked_file)
                            symlink(dir_path + "/" + f, file_dir_path + "/" + f)
                            pic = self.enabled_pic
                    else:
                        pic = self.disabled_pic
                    f_list.append((f, friendly_name, pic))
                else:
                    if path.islink(dir_path + "/" + f):
                        remove(dir_path + "/" + f)
        menu_list = [ ]
        for entry in f_list:
            menu_list.append((entry[0], entry[1], entry[2]))
        self["menu"].updateList(menu_list)
        self.selectionChanged()

    def setPicture(self, f):
        pic = f.replace(".xml", ".png")
        preview = self.skin_base_dir + "preview/preview_" + pic
        if path.exists(preview):
            self["Picture"].instance.setPixmapFromFile(preview)
            self["Picture"].show()
        else:
            self["Picture"].hide()

    def keyCancel(self):
        self.close()

    def runMenuEntry(self):
        sel = self["menu"].getCurrent()
        if sel is not None:
            if sel[2] == self.enabled_pic:
                remove(self.skin_base_dir + self.file_dir + "/" + sel[0])
            elif sel[2] == self.disabled_pic:
                symlink(self.skin_base_dir + self.screen_dir + "/" + sel[0], self.skin_base_dir + self.file_dir + "/" + sel[0])
            self.createMenuList()
