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
import module.Device_Web as Device_Web


from lib.WebAppClass.CWebDrv import CWebDrv

class Web_FW_Upgrade:
    def __init__(self, lineNum=''):
        pass

    def Setup_FW_Upgrade(self,
                        obj_menu,
                        file_path,
                        reset_type='',
                        lineNum=''):
        """
        Firmwre upgrade on Gui setting, can choose one function to update device.

        Arguments:
            [file_path](string)                               : Write the Local file Path ex. 'C:/Users/zyact/Downloads/V570ACDZ3b1.bin'

            [reset_type](string)                              : 'no', 'full_reset', 'partial_reset'  , setting FULL Reset or Partial Reset or (no)Default setting.

        Example:
            Setup_FW_Upgrade(file_path= "C:/Users/zyact/Downloads/V570ACDZ3b1.bin", reset_type='no')
            Setup_FW_Upgrade(file_path= "C:/Users/zyact/Downloads/V570ACDZ3b1.bin", reset_type='full_reset')
            Setup_FW_Upgrade(file_path= "C:/Users/zyact/Downloads/V570ACDZ3b1.bin", reset_type='partial_reset')
            Setup_FW_Upgrade(file_path= "C:/Users/zyact/Downloads/V570ACDZ3b1.bin")
        """

        all_args = locals()
        stepTitle = lineNum + "Web_FW_Upgrade.Setup_FW_Upgrade("

        if file_path != "":
            stepTitle = stepTitle + "file_path =" + file_path + ", "  

        for key, value in all_args.items():
            if key != "self" and key != "lineNum" and key != "obj_menu":
                value = str(value)
                if len(value) > 0:
                    stepTitle = stepTitle + key + "=" + value + ", "
                               
                            
        stepTitle = stepTitle + ")"
        with allure.step(stepTitle):
            obj_menu.Click_Menu("Maintenance","Firmware_Upgrade")
            Misc.Wait(2)
            # ckeck gui login fw upgrade
            # WebApp.WebDrv_Check_Text("id","Maintenance_FirmwareUpgrade",chkText= "Firmware Upgrade", timeout= 10)

            # choose the fw reset button (reset all setting, reset all expect mesh setting)

            if reset_type != "":
                if reset_type.lower() == "no":
                        WebApp.WebDrv_Click("xpath", "//label[@id=\"reset_label\"][@class=\"custom-control custom-checkbox active \"]",timeout =3, pass_fail= "Don't Care")
                        WebApp.WebDrv_Click("xpath","//label[@id=\"partialreset_label\"][@class=\"custom-control custom-checkbox active \"]",timeout =3, pass_fail= "Don't Care")
                                                     
                elif reset_type.lower() == "full_reset":
                    Misc.ACTS_Dummy_Response("PASS"," Reset All Settings After Firmware Upgrade.")
                    WebApp.WebDrv_Click("xpath", "//label[@id=\"reset_label\"][@class=\"custom-control custom-checkbox  \"]",timeout =3, pass_fail= "Don't Care")

                elif reset_type.lower() == "partial_reset":
                    Misc.ACTS_Dummy_Response("PASS"," Reset All Settings Except Mesh After Firmware Upgrade.")
                    WebApp.WebDrv_Click("xpath","//label[@id=\"partialreset_label\"][@class=\"custom-control custom-checkbox  \"]",timeout =3, pass_fail= "Don't Care")

            # upgrade device fw and set fw file
            if file_path != "":
                WebApp.WebDrv_Set_Value("id","filename", file_path)
                WebApp.WebDrv_Click("id","upload_btn")
                Misc.Wait(10)
            