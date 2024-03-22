import pytest
import allure
from pytest import assume
import lib.globalvar

from lib.Common import *

import api.Console as Console
import api.Misc as Misc
import api.TR as TR
import api.WebApp as WebApp
import module.Web.Web_Menu as Web_Menu

from lib.WebAppClass.CWebDrv import CWebDrv

class Web_Setup_uPnP:
    def __init__(self, lineNum=''):
        pass
        
    def Setup_uPnP(self,
                  obj_menu,
                  UPnP='',
                  upnpnat='',    
                  lineNum=''):
        """
        Enable or Disable UPnP or UPnP-NAT-T function

        Arguments:
            [UPnP](string)                     : 'yes', 'no'.  Enable/Disable uPnP state
            [upnpnat](string)                  : 'yes', 'no'.  Enable/Disable uPnP NAT-T state
            
        """  
        all_args = locals()
        stepTitle = lineNum + "Web_Setup_uPnP.Setup_uPnP("
        for key, value in all_args.items():
            if key != "self" and key != "lineNum" and key != "obj_menu":
                value = str(value)
                if len(value) > 0:
                    stepTitle = stepTitle + key + "=" + value + ", "                     
                            
        stepTitle = stepTitle + ")" 
        with allure.step(stepTitle):
            obj_menu.Click_Menu("Network Setting", "Home_Networking", "tab_Network_Home_Networking_UPnP_Tab")
            if UPnP.lower() == "yes":
                WebApp.WebDrv_Click("xpath",'//label[@id=\"upnp_enable_radio\"][@class=\"switch  \"]/span', timeout=10, pass_fail="Don't Care")
            elif UPnP.lower() == "no" :
                WebApp.WebDrv_Click("xpath",'//label[@id=\"upnp_enable_radio\"][@class=\"switch active \"]/span', timeout=10, pass_fail="Don't Care")
            Misc.Wait(3)

            if upnpnat.lower() == "yes":
                WebApp.WebDrv_Click("xpath",'//label[@id=\"upnp_natt_enable_radio\"][@class=\"switch  \"]/span', timeout=10, pass_fail="Don't Care")
            elif upnpnat.lower() == "no" :
                WebApp.WebDrv_Click("xpath",'//label[@id=\"upnp_natt_enable_radio\"][@class=\"switch active \"]/span', timeout=10, pass_fail="Don't Care")
            Misc.Wait(3)

            WebApp.WebDrv_Click("id","upnp_apply", 5)
            WebApp.WebDrv_Wait_Device_Loading("xpath", "//div[@class=\"loader-spinner\"]", 10)
                   