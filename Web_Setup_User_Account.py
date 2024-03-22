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

class Web_Setup_User_Account:
    def __init__(self, lineNum=''):
        self.account_btn_1 = {"1": "acc_editBtn0",
                              "2": "acc_editBtn1",
                              "3": "acc_editBtn2",
                              "4": "acc_editBtn3",
                              }

        self.account_btn_2 = {"1": "acc_deleteBtn0",
                              "2": "acc_deleteBtn1",
                              "3": "acc_deleteBtn2",
                              "4": "acc_deleteBtn3",
                              }

    def Add_New_Entry(self, name, lineNum=''):
        WebApp.WebDrv_Click("id", "adduser", 5)
        WebApp.WebDrv_Wait_Device_Loading("xpath", "//div[@class=\"loader-spinner\"]")
        Misc.Wait(2) 
        WebApp.WebDrv_Set_Value("id", "accountName", name)

    def Setup_User_Account(self,
                           obj_menu,
                           bf_delete='',
                           index='',
                           name='',
                           enable='',
                           old_password='',
                           password='',
                           group='',
                           retry_time='',
                           idle_time='',
                           lock_period='',
                           remote_privilege='',
                           allow_to_add_account='',
                           lineNum=''):

        """
            {bf_delete}                     : {Yes}, {No}. To delete (or not) the entry which be specificed by {index}
            {index}                         : -1, to add a new user account entry, or 1, 2, 3, ...n to edit or delete this entry
            {name}                          : Account name 
            {enable}                        : {Yes}, {No}. To active/deactive the user account
            {old_password}                  : Old password
            {password}                      : New password
            {group}                         : {Administrator}, {User}
            {retry_time}                    : {0} ~ {5}. Retry times
            {idle_time}                     : {1} ~ {60} minutes. Idle timeout
            {lock_period}                   : {5} ~ {90} minutes. Lock period
            {remote_privilege}              : {LAN|WAN|LAN_WAN}. Remote access privilege
        """

        all_args = locals()
        stepTitle = lineNum + "Web_Setup_User_Account.Setup_User_Account("
        for key, value in all_args.items():
            if key != "self" and key != "lineNum" and key != "obj_menu":
                value = str(value)
                if len(value) > 0:
                    stepTitle = stepTitle + key + "=" + value + ", "                     

        stepTitle = stepTitle + ")" 
        with allure.step(stepTitle):

            if allow_to_add_account != "":
                self.check_add_icon(allow_to_add_account)
                return

            obj_menu.Click_Menu("Maintenance", "User_Account")

            if index == "-1":
                # Exit if add user icon is not found
                res = self.check_add_icon("Setup_User_Account")
                if res is not True:
                    return

                self.Add_New_Entry(name)
            elif bf_delete.lower() == "yes":
                delete_btn = self.account_btn_2[index]
                WebApp.WebDrv_Click("id", delete_btn)
                Misc.Wait(2)
                WebApp.WebDrv_Click("id", "alertOKBtn")
                WebApp.WebDrv_Wait_Device_Loading("xpath", "//div[@class=\"loader-spinner\"]")
            else:
                edit_btn = self.account_btn_1[index]
                WebApp.WebDrv_Click("id", edit_btn)
                Misc.Wait(2)
                WebApp.WebDrv_Wait_Device_Loading("xpath", "//div[@class=\"loader-spinner\"]")

            if enable.lower() == "yes":
                pass
            elif enable.lower() == "no":
                pass

            if old_password != '':
                old_password = self.password_process(old_password)
                WebApp.WebDrv_Set_Value("id", "oldPasswd", old_password)

            if password != '':
                password = self.password_process(password)
                WebApp.WebDrv_Set_Value("id", "newPasswd", password)
                WebApp.WebDrv_Set_Value("id", "verifyNewpassword", password)

            if retry_time != '':
                WebApp.WebDrv_Set_Value("id", "retryTime", retry_time)

            if idle_time != '':
                WebApp.WebDrv_Set_Value("id", "idleTime", idle_time)

            if lock_period != '':
                WebApp.WebDrv_Set_Value("id", "lockTime", lock_period)

            if group != '':
                group = self.group_process(group)
                WebApp.WebDrv_List_Select("id", "accountGroupName", "text", group)

            if remote_privilege != '':
                if remote_privilege.upper() == 'LAN':
                    WebApp.WebDrv_Click("id", "lan_access")
                elif remote_privilege.upper() == 'WAN':
                    WebApp.WebDrv_Click("id", "wan_access")
                elif remote_privilege.upper() == 'LAN_WAN':
                    WebApp.WebDrv_Click("id", "lan_wan_access")                    

            if bf_delete.lower() == "":
                WebApp.WebDrv_Click("id", "button_Panel_iduserAccount_1_0")
                WebApp.WebDrv_Wait_Device_Loading("xpath", "//div[@class=\"loader-spinner\"]")

    def check_add_icon(self, varname):
        lib.globalvar.set_value(varname, True)
        return True

    def group_process(self, group):
        return group

    def password_process(self, password):
        return password


class Web_Setup_User_Account_Odido(Web_Setup_User_Account):
    def check_add_icon(self, varname):
        res = WebApp.WebDrv_Find_Element("id", "adduser", 5)
        lib.globalvar.set_value(varname, res)

        if res is not True:
            Misc.ACTS_Dummy_Response("PASS", "This account not allow to add user account")
        return res

class Web_Setup_User_Account_TT(Web_Setup_User_Account):
    def group_process(self, group):
        if group == "User":
            return "Administrator"
        else:
            return group

    def password_process(self, password):
        password = password.replace("123456", "134679")
        password = password.replace("12345", "13467")
        password = password.replace("1234", "1357")
        password = password.replace("123", "135")
        password = password.replace("111", "134")

        return password