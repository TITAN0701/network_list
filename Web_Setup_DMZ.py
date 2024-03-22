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

class Web_Setup_DMZ:
    def __init__(self, lineNum=''):
        pass
        
    def Setup_DMZ(self,
                  obj_menu,
                  dmz_ip_addr,       
                  lineNum=''):
        
        """
        Set the Server ip address 

        Arguments:
            [Server_Address](string)                   : Set the DMZ server ip
        """
        all_args = locals()
        stepTitle = lineNum + "Web_Setup_DMZ.Setup_DMZ(" +  ", " 
        if dmz_ip_addr != "":
            stepTitle = stepTitle + "dmz_ip_addr=" + dmz_ip_addr + ", "

        for key, value in all_args.items():
            if key != "self" and key != "lineNum" and key != "obj_menu":
                value = str(value)
                if len(value) > 0:
                    stepTitle = stepTitle + key + "=" + value + ", "
            
        stepTitle = stepTitle + ")"
        with allure.step(stepTitle):
            obj_menu.Click_Menu("Network Setting", "NAT", "tab_Network_NAT_DMZ_Tab")
            Misc.Wait(2)
            
            # Setting DMZ service
            if dmz_ip_addr != "":
                ip_setting = dmz_ip_addr.split(".")
                WebApp.WebDrv_Set_Value("id","a_dmz_addr_1", "255")
                WebApp.WebDrv_Set_Value("id","a_dmz_addr_1", ip_setting[0])
                WebApp.WebDrv_Set_Value("id","a_dmz_addr_2", "255")
                WebApp.WebDrv_Set_Value("id","a_dmz_addr_2", ip_setting[1])
                WebApp.WebDrv_Set_Value("id","a_dmz_addr_3", "255")
                WebApp.WebDrv_Set_Value("id","a_dmz_addr_3", ip_setting[2])
                WebApp.WebDrv_Set_Value("id","a_dmz_addr_4", "255")
                WebApp.WebDrv_Set_Value("id","a_dmz_addr_4", ip_setting[3])
                
            WebApp.WebDrv_Click("id","Network_NAT_DMZ_ApplyBtn", timeout= 3)
            WebApp.WebDrv_Wait_Device_Loading("xpath", "//div[@class=\"loader-spinner\"]")
            Misc.Wait(3)