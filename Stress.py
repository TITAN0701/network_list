from lib.Common import *
from pathlib import Path
import datetime

import pytest

import api.Console as Console
import api.Misc as Misc
import api.TR as TR
import api.WebApp as WebApp

import module.Reset_Device as Reset_Device
import module.Device_Console as Device_Console
import module.Device_Web as Device_Web
import module.Device_TR69 as Device_TR69
import module.Device_Config as Device_Config


@allure.feature("Environment Setup")
class TestEnv:

    @allure.title("Environment Setup")
    @allure.severity("Blocker")
    def test_case(self):

        Misc.ACTS_Dummy_Response("PASS", "Write DUT_Info.txt")
        with open("DUT_Info.txt", "w") as f_info:
            f_info.write("Model Name: " + VAR("$model_name") + "\n")
            f_info.write("Project: " + VAR("$project_base") + "\n")
            f_info.write("FW Version: " + VAR("$fw_version") + "\n")

        Misc.Time_Sync()

        Misc.ACTS_Dummy_Response("PASS", "Reset device")
        Reset_Device.Reset_Device(reset_device="YES", config_connection="YES", setup_device_wan="NO") 

        Misc.ACTS_Dummy_Response("PASS", "Upgrade firmware by GUI")
        objDeviceWeb = Device_Web.Device_Web(VAR("$web_url"))
        objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))
        file_path = VAR("$tool_path") + "firmware/ras.bin"
        objDeviceWeb.Setup_FW_Upgrade(file_path=file_path)
        Misc.Wait(10)
        objDeviceWeb.Web_CloseWebSite()

        Misc.Wait(120)
        objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"), retry_times=5)

        Misc.ACTS_Dummy_Response("PASS", "Check firmware version by GUI")
        objDeviceWeb.Setup_CardPage_SysInfo(fw_version=VAR("$fw_version"))
        objDeviceWeb.Web_Logout()

        Misc.ACTS_Dummy_Response("PASS", "Reset device and setup WAN")
        Reset_Device.Reset_Device(reset_device="YES", config_connection="NO", setup_device_wan="YES")

        Misc.ACTS_Dummy_Response("PASS", "Check IP route by console")
        objDeviceConsole = Device_Console.Device_Console("DUT", VAR("$console_username"), VAR("$console_password"), second_Lv_command= VAR("$second_shell_command"), second_Lv_password= VAR("$second_shell_password"))
        Console.CI_Cmd_Scan("ip route", 30, [("default via", "172.202.77.1")])

        # Misc.ACTS_Dummy_Response("PASS", "Download device config file from GUI")
        # objDeviceConfig = Device_Config.Device_Config(VAR("$model_name"))
        # objDeviceConfig.Delete_Config_File()
        # objDeviceWeb.Web_Login(VAR("$admin_username"),VAR("$admin_password"))
        # objDeviceWeb.Web_Click_Menu("Maintenance", "Backup_Restore")
        # WebApp.WebDrv_Click("id", "backup_config_backup_btn")
        # Misc.Wait(15)
        # objDeviceConfig.Copy_Config_File(target_path=VAR("$tool_path") + "config/RoMEdAY224")
        # objDeviceConfig.Copy_Config_File(target_path=VAR("$tool_path") + "config/CoNFIg1229")
        # objDeviceConfig.Set_WiFi(config_path=VAR("$tool_path") + "config/RoMEdAY224", Main_SSID="rom-d-test-0")
        # objDeviceConfig.Set_WiFi(config_path=VAR("$tool_path") + "config/CoNFIg1229", Main_SSID="rom-d-test-0")
        # objDeviceWeb.Web_Logout()

        Misc.ACTS_Dummy_Response("PASS", "Modify IPv6 configuration in NAT_WKS")
        if VAR("$first_etherwan_interface") != "None":
            objDeviceConsole.Get_Interface_Mac(VAR("$first_etherwan_interface"), "WAN_MAC")
        else:
            objDeviceConsole.Get_Interface_Mac(VAR("$first_ponwan_interface"), "WAN_MAC")
        WAN_MAC = VAR("WAN_MAC")
        Console.NAT_IPv6_Config(WAN_MAC)
        
        Misc.ACTS_Dummy_Response("PASS", "Reboot all WKS")
        Console.Use_Device_WKS_Login("Shell_LAN1", "ExpectSSH", "root", "1234", "LAN1_WKS")
        Console.CI_Cmd_More([("reboot", 5)])
        Console.Use_Device_WKS_Login("Shell_LAN2", "ExpectSSH", "root", "1234", "LAN2_WKS")
        Console.CI_Cmd_More([("reboot", 5)])
        Console.Use_Device_WKS_Login("Shell_DMZ", "ExpectSSH", "root", "1234", "DMZ_WKS")
        Console.CI_Cmd_More([("reboot", 5)])
        Console.Use_Device_WKS_Login("Shell_WAN", "ExpectSSH", "root", "1234", "WAN_WKS")
        Console.CI_Cmd_More([("reboot", 5)])
        Console.Retry_WKS_Ping("LAN1_WKS", "eth1", "172.202.77.1", 10, count=5)

        Console.Use_Device_WKS_Login("Shell_LAN1", "ExpectSSH", "root", "1234", "LAN1_WKS")
        Console.CI_Cmd_More([("dhclient -v -6 eth1", 2), ("dhclient -v eth1", 2)])
        Console.Use_Device_WKS_Login("Shell_LAN2", "ExpectSSH", "root", "1234", "LAN2_WKS")
        Console.CI_Cmd_More([("dhclient -v -6 eth1", 2), ("dhclient -v eth1", 2)])
        Console.Use_Device_WKS_Login("Shell_DMZ", "ExpectSSH", "root", "1234", "DMZ_WKS")
        Console.CI_Cmd_More([("dhclient -v -6 eth1", 2), ("dhclient -v eth1", 2)])

        Console.Check_WKS_Ping("LAN1_WKS", "eth1", "172.202.77.1", "PASS")
        Console.Check_WKS_Ping("LAN1_WKS", "eth1", "168.95.1.1", "Don't Care")
        Console.Check_WKS_Ping("LAN2_WKS", "eth1", "172.202.77.1", "PASS")
        Console.Check_WKS_Ping("LAN2_WKS", "eth1", "168.95.1.1", "Don't Care")
        Console.Check_WKS_Ping("DMZ_WKS", "eth1", "172.202.77.1", "PASS")
        Console.Check_WKS_Ping("DMZ_WKS", "eth1", "168.95.1.1", "Don't Care")

        objDeviceConsole.Check_IPv6_Connection()

@allure.feature("Stress")
class TestStress:

    @allure.title("UTP-5131  Power on/off to reboot CPE for 50 times with 1G LAN port (Power off time = 2 seconds)")
    @allure.severity("Blocker")
    def test_case(self):

        objDeviceWeb = Device_Web.Device_Web(VAR("$web_url"))
        objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))

        Misc.ACTS_Dummy_Response("PASS", "Start SIP server on NAT_WKS")
        Console.Use_Device_WKS_Login("WKS_Shell_NAT", "SSH", "root", "1234", address="NAT")
        Console.CI_Cmd_More([("/usr/local/sbin/opensipsctl start", 10)])
        Console.CI_Cmd_More([("opensipsctl start", 10)])
        Misc.Wait(5)
                    
        # set SIP server status
        Console.CI_Cmd_More([("ps aux|grep opensip", 10)])
        Misc.Wait(5)
        Console.CI_Cmd_More([("exit", 10)])
        Misc.Wait(5)

        # Set SIP Account
        Misc.ACTS_Dummy_Response("PASS", "Check SIP Setup")
        objDeviceWeb.Setup_SIP_Account(bf_delete=False, index="1", enable="yes", sip_account_num="12345", sip_username="12345", sip_password="12345")
        Misc.Wait(20)

        # Set SIP Service Provider
        objDeviceWeb.Setup_SIP_Service_Provider(bf_delete=False, index="1", enable="yes", sip_service_provider_name=VAR("$default_gateway"), 
                                                sip_proxy_server_address=VAR("$default_gateway"), sip_registrar_server_address=VAR("$default_gateway"),
                                                sip_service_domain=VAR("$default_gateway"))
        
        objDeviceWeb.Web_Click_Menu("VoIP", "SIP", "tab_VoIP_SIPAccount_Tab")
        WebApp.WebDrv_Click("id","VoIP_SIPAccount_Edit1")
        WebApp.WebDrv_Check_Value("id","SIP_Account_number",chkVaule="12345", full_match= True)
        WebApp.WebDrv_Check_Value("id","SIP_Account_auth_username",chkVaule="12345", full_match= True)
        WebApp.WebDrv_Check_Value("id","SIP_Account_auth_password",chkVaule="********", full_match= True)
        WebApp.WebDrv_Click("id","SIP_Account_CancelBtn")
        WebApp.WebDrv_Wait_Device_Loading("xpath", "//div[@class=\"loader-spinner\"]")

        objDeviceWeb.Web_Logout()

        # reboot 50 thimes
        for i in range(1, 51):
            # Power off and power on 2s
            Misc.ACTS_Dummy_Response("PASS","Reboot power switch "+ str(i) +" times")
            Misc.Setup_Power_Switch("SW_1","Off")
            Misc.Wait(2)
            Misc.Setup_Power_Switch("SW_1","On")
            Misc.Wait(180)

            Misc.ACTS_Dummy_Response("PASS", "Check DUT still can connect ")
            Console.Use_Device_WKS_Login("Shell_LAN1", "ExpectSSH", "root", "1234", "LAN1_WKS")
            Console.Retry_WKS_Ping("LAN1_WKS", "eth1", ["www.hinet.net", "168.95.1.1", "172.202.77.1"])

                    
            objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))        
            objDeviceWeb.Web_Click_Menu("VoIP", "SIP", "tab_VoIP_SIPAccount_Tab")
            WebApp.WebDrv_Click("id","VoIP_SIPAccount_Edit1")
            WebApp.WebDrv_Check_Value("id","SIP_Account_number",chkVaule="12345", full_match= True)
            WebApp.WebDrv_Check_Value("id","SIP_Account_auth_username",chkVaule="12345", full_match= True)
            WebApp.WebDrv_Check_Value("id","SIP_Account_auth_password",chkVaule="********", full_match= True)
            WebApp.WebDrv_Click("id","SIP_Account_CancelBtn")
            WebApp.WebDrv_Wait_Device_Loading("xpath", "//div[@class=\"loader-spinner\"]")

            Misc.ACTS_Dummy_Response("PASS", "Check registration status")
            objDeviceWeb.Web_Click_Menu("System Monitor", "VoIP_Status")
            WebApp.WebDrv_Check_Text("xpath", '//*[@id="SystemMonitor_VoIPStatus_Table1"]/tbody/tr[1]/td[3]', "Registered", "PASS", True)
            objDeviceWeb.Web_Logout()

                    

    @allure.title("UTP-5130 Power on/off to reboot CPE for 50 times (Extend Power off time to 3 minutes)")
    @allure.severity("Blocker")
    def test_case(self):

        objDeviceWeb = Device_Web.Device_Web(VAR("$web_url"))
        objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))

        Misc.ACTS_Dummy_Response("PASS", "Start SIP server on NAT_WKS")
        Console.Use_Device_WKS_Login("WKS_Shell_NAT", "SSH", "root", "1234", address="NAT")
        Console.CI_Cmd_More([("/usr/local/sbin/opensipsctl start", 10)])
        Console.CI_Cmd_More([("opensipsctl start", 10)])
        Misc.Wait(5)
                    
        # set SIP server status
        Console.CI_Cmd_More([("ps aux|grep opensip", 10)])
        Misc.Wait(5)
        Console.CI_Cmd_More([("exit", 10)])
        Misc.Wait(5)

        # Set SIP Account
        Misc.ACTS_Dummy_Response("PASS", "Check SIP Setup")
        objDeviceWeb.Setup_SIP_Account(bf_delete=False, index="1", enable="yes", sip_account_num="12345", sip_username="12345", sip_password="12345")
        Misc.Wait(20)

        # Set SIP Service Provider
        objDeviceWeb.Setup_SIP_Service_Provider(bf_delete=False, index="1", enable="yes", sip_service_provider_name=VAR("$default_gateway"), 
                                                sip_proxy_server_address=VAR("$default_gateway"), sip_registrar_server_address=VAR("$default_gateway"),
                                                sip_service_domain=VAR("$default_gateway"))
        
        objDeviceWeb.Web_Click_Menu("VoIP", "SIP", "tab_VoIP_SIPAccount_Tab")
        WebApp.WebDrv_Click("id","VoIP_SIPAccount_Edit1")
        WebApp.WebDrv_Check_Value("id","SIP_Account_number",chkVaule="12345", full_match= True)
        WebApp.WebDrv_Check_Value("id","SIP_Account_auth_username",chkVaule="12345", full_match= True)
        WebApp.WebDrv_Check_Value("id","SIP_Account_auth_password",chkVaule="********", full_match= True)
        WebApp.WebDrv_Click("id","SIP_Account_CancelBtn")
        WebApp.WebDrv_Wait_Device_Loading("xpath", "//div[@class=\"loader-spinner\"]")

        objDeviceWeb.Web_Logout()

        # reboot 50 thimes
        for i in range(1, 51):
            # Power off and power on 3 min
            Misc.ACTS_Dummy_Response("PASS","Reboot power switch "+ str(i) +" times")
            Misc.Setup_Power_Switch("SW_1","Off")
            Misc.Wait(180)
            Misc.Setup_Power_Switch("SW_1","On")
            Misc.Wait(180)

            Misc.ACTS_Dummy_Response("PASS", "Check DUT still can connect ")
            Console.Use_Device_WKS_Login("Shell_LAN1", "ExpectSSH", "root", "1234", "LAN1_WKS")
            Console.Retry_WKS_Ping("LAN1_WKS", "eth1", ["www.hinet.net", "168.95.1.1", "172.202.77.1"])
                    
            objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))        
            objDeviceWeb.Web_Click_Menu("VoIP", "SIP", "tab_VoIP_SIPAccount_Tab")
            WebApp.WebDrv_Click("id","VoIP_SIPAccount_Edit1")
            WebApp.WebDrv_Check_Value("id","SIP_Account_number",chkVaule="12345", full_match= True)
            WebApp.WebDrv_Check_Value("id","SIP_Account_auth_username",chkVaule="12345", full_match= True)
            WebApp.WebDrv_Check_Value("id","SIP_Account_auth_password",chkVaule="********", full_match= True)
            WebApp.WebDrv_Click("id","SIP_Account_CancelBtn")
            WebApp.WebDrv_Wait_Device_Loading("xpath", "//div[@class=\"loader-spinner\"]")

            Misc.ACTS_Dummy_Response("PASS", "Check registration status")
            objDeviceWeb.Web_Click_Menu("System Monitor", "VoIP_Status")
            WebApp.WebDrv_Check_Text("xpath", '//*[@id="SystemMonitor_VoIPStatus_Table1"]/tbody/tr[1]/td[3]', "Registered", "PASS", True)
            objDeviceWeb.Web_Logout()

    @allure.title("UTP-5163 Upgrade from GUI by automation for 50 times")
    @allure.severity("Blocker")
    def test_case(self):

        # check all WAN IP was up (get wan ip)
        if VAR("$first_etherwan_interface") != "None":
            wan = "ETHERNET"
            interface_ip = VAR("$first_etherwan_interface")
        else:
            wan = "PON"
            interface_ip = VAR("$first_ponwan_interface")

        Misc.ACTS_Dummy_Response("PASS", "Get CPE WAN IP")
        objDeviceConsole = Device_Console.Device_Console("DUT", VAR("$console_username"), VAR("$console_password"), second_Lv_command= VAR("$second_shell_command"), second_Lv_password= VAR("$second_shell_password"))
        objDeviceConsole.Get_Interface_IP(interface_ip, "WAN_v4_IP")

        # Modify basic setting 2.4G/5G WLAN SSID/password, VoIP setting(can register successfully), IPTV.
        Misc.ACTS_Dummy_Response("PASS", "Start SIP server on NAT_WKS")
        Console.Use_Device_WKS_Login("WKS_Shell_NAT", "ExpectSSH", "root", "1234", address="NAT")
        Console.CI_Cmd_More([("/usr/local/sbin/opensipsctl start", 10)])
        Console.CI_Cmd_More([("opensipsctl start", 10)])
        Misc.Wait(5)
                    
        Console.CI_Cmd_More([("ps aux|grep opensip", 10)])
        Misc.Wait(5)
        Console.CI_Cmd_More([("exit", 10)])
        Misc.Wait(5)

        objDeviceWeb = Device_Web.Device_Web(VAR("$web_url"))
        objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))

        Misc.ACTS_Dummy_Response("PASS", "Setup Voip")
        objDeviceWeb.Setup_SIP_Account(bf_delete=False, index="1", enable="yes", sip_account_num="12345", sip_username="12345", sip_password="12345")
        Misc.Wait(20)

        objDeviceWeb.Setup_SIP_Service_Provider(bf_delete=False, index="1", enable="yes", sip_service_provider_name=VAR("$default_gateway"), 
                                                sip_proxy_server_address=VAR("$default_gateway"), sip_registrar_server_address=VAR("$default_gateway"),
                                                sip_service_domain=VAR("$default_gateway"))

        objDeviceWeb.Setup_Mesh("false")
        
        Misc.ACTS_Dummy_Response("PASS","Setup 2.4/5GHz WLAN SSID/PSK")
        objDeviceWeb.Setup_Wireless(band= "2.4GHz", bf_same_on_24_5G='false', name= "SSID_2.4G", security_mode= "WPA3-Personal-Transition", password= "Test12345678@")
        Misc.Wait(10)

        # objDeviceWeb.Setup_Wireless(band= '5GHz', bf_same_on_24_5G='false', name= 'SSID_5G', security_mode= 'WPA3-Personal-Transition', password= 'Test12345678@')
        # Misc.Wait(10)

        objDeviceWeb.Check_WiFi_Setting(band = "2.4GHz", exp_name = "SSID_2.4G", exp_password = "Test12345678@")
        # objDeviceWeb.Check_WiFi_Setting(band= "5GHz", exp_name = "SSID_5G", exp_password = "Test12345678@")

        # check out setting success for 2.4/5GHz wlan, sip (first check)
        objDeviceWeb.Web_Click_Menu("VoIP", "SIP", "tab_VoIP_SIPAccount_Tab")
        WebApp.WebDrv_Click("id","VoIP_SIPAccount_Edit1")
        WebApp.WebDrv_Check_Value("id","SIP_Account_number",chkVaule="12345", full_match= True)
        WebApp.WebDrv_Check_Value("id","SIP_Account_auth_username",chkVaule="12345", full_match= True)
        WebApp.WebDrv_Check_Value("id","SIP_Account_auth_password",chkVaule="********", full_match= True)
        WebApp.WebDrv_Click("id","SIP_Account_CancelBtn")
        WebApp.WebDrv_Wait_Device_Loading("xpath", "//div[@class=\"loader-spinner\"]")

        # check out VoIP register status `successfully`.
        Misc.ACTS_Dummy_Response("PASS", "Check registration status")
        objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))
        objDeviceWeb.Web_Click_Menu("System Monitor", "VoIP_Status")
        WebApp.WebDrv_Check_Text("xpath", '//*[@id="SystemMonitor_VoIPStatus_Table1"]/tbody/tr[1]/td[3]', "Registered", "PASS", True)

        objDeviceWeb.Web_Logout()

        # GUI do FW upgrade/downgrade (Field side or FCS <> formal FW).
        # beta version to beta dummy version 25 times
        for i in range(1, 26):
            Misc.ACTS_Dummy_Response("PASS","FW upgrade "+ str(i) +" times")

            objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))
            objDeviceWeb.Setup_FW_Upgrade("D:/opal_auto/0_Pytest/Tools/firmware/ras-dummy.bin", "no")
            Misc.Wait(200)

            # check out setting success for 2.4/5GHz wlan, Voip (second check)
            objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))
            
            objDeviceWeb.Check_WiFi_Setting(band = "2.4GHz", exp_name = "SSID_2.4G", exp_password = "Test12345678@")
            # objDeviceWeb.Check_WiFi_Setting(band= "5GHz", exp_name = "SSID_5G", exp_password = "Test12345678@")

            objDeviceWeb.Web_Click_Menu("VoIP", "SIP", "tab_VoIP_SIPAccount_Tab")
            WebApp.WebDrv_Click("id","VoIP_SIPAccount_Edit1")
            WebApp.WebDrv_Check_Value("id","SIP_Account_number",chkVaule="12345", full_match= True)
            WebApp.WebDrv_Check_Value("id","SIP_Account_auth_username",chkVaule="12345", full_match= True)
            WebApp.WebDrv_Check_Value("id","SIP_Account_auth_password",chkVaule="********", full_match= True)
            WebApp.WebDrv_Click("id","SIP_Account_CancelBtn")
            WebApp.WebDrv_Wait_Device_Loading("xpath", "//div[@class=\"loader-spinner\"]")

            Misc.ACTS_Dummy_Response("PASS", "Check registration status")
            objDeviceWeb.Web_Click_Menu("System Monitor", "VoIP_Status")
            WebApp.WebDrv_Check_Text("xpath", '//*[@id="SystemMonitor_VoIPStatus_Table1"]/tbody/tr[1]/td[3]', "Registered", "PASS", True)
            objDeviceWeb.Web_Logout()


            objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))
            x = WebApp.WebDrv_Check_Text("id","card_sysinfo_fwversion", VAR("$fw_ras-dummy_version"), full_match= True)

            # Get device image sequence number
            objDeviceConsole = Device_Console.Device_Console("DUT", VAR("$console_username"), VAR("$console_password"), second_Lv_command=VAR("$second_shell_command"), second_Lv_password=VAR("$second_shell_password"))
            objDeviceConsole.Get_Image_Seq_Number("old_seq_number")

            if x is True:
                Misc.ACTS_Dummy_Response("PASS","DUT FW FCS upgrade to beta")
                objDeviceWeb.Setup_FW_Upgrade("D:/opal_auto/0_Pytest/Tools/firmware/ras.bin", "no")
                Misc.Wait(200)
            else:
                Misc.ACTS_Dummy_Response("FAIL","DUT FW FCS can't upgrade to beta success")

            WebApp.WebDrv_CloseWebSite()

            # Get device image sequence number
            objDeviceConsole.Console_Login(VAR("$console_username"), VAR("$console_password"), second_Lv_command= VAR("$second_shell_command"), second_Lv_password= VAR("$second_shell_password")) 
            objDeviceConsole.Get_Image_Seq_Number("new_seq_number")
            
            # After upgrade, check out FW has been upgrade successfully
            if VAR("new_seq_number") > VAR("old_seq_number"):
                Misc.ACTS_Dummy_Response("PASS","FW upgrade success")
            else:
                Misc.ACTS_Dummy_Response("FAIL", "FW upgarde failed. Old image sequence number=" + str(VAR("old_seq_number")) + "," + "new image sequence number=" + str(VAR("new_seq_number")))
            

            # check out setting success for 2.4/5GHz wlan, Voip (second check)
            objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))
            
            objDeviceWeb.Check_WiFi_Setting(band = "2.4GHz", exp_name = "SSID_2.4G", exp_password = "Test12345678@")
            # objDeviceWeb.Check_WiFi_Setting(band= "5GHz", exp_name = "SSID_5G", exp_password = "Test12345678@")

            objDeviceWeb.Web_Click_Menu("VoIP", "SIP", "tab_VoIP_SIPAccount_Tab")
            WebApp.WebDrv_Click("id","VoIP_SIPAccount_Edit1")
            WebApp.WebDrv_Check_Value("id","SIP_Account_number",chkVaule="12345", full_match= True)
            WebApp.WebDrv_Check_Value("id","SIP_Account_auth_username",chkVaule="12345", full_match= True)
            WebApp.WebDrv_Check_Value("id","SIP_Account_auth_password",chkVaule="********", full_match= True)
            WebApp.WebDrv_Click("id","SIP_Account_CancelBtn")
            WebApp.WebDrv_Wait_Device_Loading("xpath", "//div[@class=\"loader-spinner\"]")

            Misc.ACTS_Dummy_Response("PASS", "Check registration status")
            objDeviceWeb.Web_Click_Menu("System Monitor", "VoIP_Status")
            WebApp.WebDrv_Check_Text("xpath", '//*[@id="SystemMonitor_VoIPStatus_Table1"]/tbody/tr[1]/td[3]', "Registered", "PASS", True)
            objDeviceWeb.Web_Logout()

            # Do ping to internet.
            Misc.ACTS_Dummy_Response("PASS", "Check DUT still can connect ")
            Console.Use_Device_WKS_Login("Shell_LAN1", "ExpectSSH", "root", "1234", "LAN1_WKS")
            Console.Retry_WKS_Ping("LAN1_WKS", "eth1", ["www.hinet.net", "168.95.1.1", "172.202.77.1"])


        ###############################################################################################################################################
        # GUI do FW upgrade/downgrade (Field side or FCS <> formal FW).
        # last FCS version to beta version 25 times
        for i in range(1, 26):
            Misc.ACTS_Dummy_Response("PASS","FW upgrade "+ str(i) +" times")

            objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))
            objDeviceWeb.Setup_FW_Upgrade("D:/opal_auto/0_Pytest/Tools/firmware/ras-c0.bin", "no")
            Misc.Wait(200)

            objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))
            
            objDeviceWeb.Check_WiFi_Setting(band = "2.4GHz", exp_name = "SSID_2.4G", exp_password = "Test12345678@")
            # objDeviceWeb.Check_WiFi_Setting(band= "5GHz", exp_name = "SSID_5G", exp_password = "Test12345678@")

            objDeviceWeb.Web_Click_Menu("VoIP", "SIP", "tab_VoIP_SIPAccount_Tab")
            WebApp.WebDrv_Click("id","VoIP_SIPAccount_Edit1")
            WebApp.WebDrv_Check_Value("id","SIP_Account_number",chkVaule="12345", full_match= True)
            WebApp.WebDrv_Check_Value("id","SIP_Account_auth_username",chkVaule="12345", full_match= True)
            WebApp.WebDrv_Check_Value("id","SIP_Account_auth_password",chkVaule="********", full_match= True)
            WebApp.WebDrv_Click("id","SIP_Account_CancelBtn")
            WebApp.WebDrv_Wait_Device_Loading("xpath", "//div[@class=\"loader-spinner\"]")

            # check out VoIP register status `successfully`.
            Misc.ACTS_Dummy_Response("PASS", "Check registration status")
            objDeviceWeb.Web_Click_Menu("System Monitor", "VoIP_Status")
            WebApp.WebDrv_Check_Text("xpath", '//*[@id="SystemMonitor_VoIPStatus_Table1"]/tbody/tr[1]/td[3]', "Registered", "PASS", True)
            objDeviceWeb.Web_Logout()


            objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))
            x = WebApp.WebDrv_Check_Text("id","card_sysinfo_fwversion", VAR("$fw_ras-c0_version"), full_match= True)

            # Get device image sequence number
            objDeviceConsole = Device_Console.Device_Console("DUT", VAR("$console_username"), VAR("$console_password"), second_Lv_command=VAR("$second_shell_command"), second_Lv_password=VAR("$second_shell_password"))
            objDeviceConsole.Get_Image_Seq_Number("old_seq_number")

            if x is True:
                Misc.ACTS_Dummy_Response("PASS","DUT FW FCS upgrade to beta")
                objDeviceWeb.Setup_FW_Upgrade("D:/opal_auto/0_Pytest/Tools/firmware/ras.bin", "no")
                Misc.Wait(200)
            else:
                Misc.ACTS_Dummy_Response("FAIL","DUT FW FCS can't upgrade to beta success")

            # Get device image sequence number
            objDeviceConsole.Console_Login(VAR("$console_username"), VAR("$console_password"), second_Lv_command= VAR("$second_shell_command"), second_Lv_password= VAR("$second_shell_password")) 
            objDeviceConsole.Get_Image_Seq_Number("new_seq_number")
            
            # After upgrade, check out FW has been upgrade successfully
            if VAR("new_seq_number") > VAR("old_seq_number"):
                Misc.ACTS_Dummy_Response("PASS","FW upgrade success")
            else:
                Misc.ACTS_Dummy_Response("FAIL", "FW upgarde failed. Old image sequence number=" + str(VAR("old_seq_number")) + "," + "new image sequence number=" + str(VAR("new_seq_number")))

            WebApp.WebDrv_CloseWebSite()    

            # check out setting success for 2.4/5GHz wlan, Voip (second check)
            objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))
            
            objDeviceWeb.Check_WiFi_Setting(band = "2.4GHz", exp_name = "SSID_2.4G", exp_password = "Test12345678@")
            # objDeviceWeb.Check_WiFi_Setting(band= "5GHz", exp_name = "SSID_5G", exp_password = "Test12345678@")

            objDeviceWeb.Web_Click_Menu("VoIP", "SIP", "tab_VoIP_SIPAccount_Tab")
            WebApp.WebDrv_Click("id","VoIP_SIPAccount_Edit1")
            WebApp.WebDrv_Check_Value("id","SIP_Account_number",chkVaule="12345", full_match= True)
            WebApp.WebDrv_Check_Value("id","SIP_Account_auth_username",chkVaule="12345", full_match= True)
            WebApp.WebDrv_Check_Value("id","SIP_Account_auth_password",chkVaule="********", full_match= True)
            WebApp.WebDrv_Click("id","SIP_Account_CancelBtn")
            WebApp.WebDrv_Wait_Device_Loading("xpath", "//div[@class=\"loader-spinner\"]")

            # check out VoIP register status `successfully`.
            Misc.ACTS_Dummy_Response("PASS", "Check registration status")
            objDeviceWeb.Web_Click_Menu("System Monitor", "VoIP_Status")
            WebApp.WebDrv_Check_Text("xpath", '//*[@id="SystemMonitor_VoIPStatus_Table1"]/tbody/tr[1]/td[3]', "Registered", "PASS", True)
            objDeviceWeb.Web_Logout()

            # Do ping to internet.
            Misc.ACTS_Dummy_Response("PASS", "Check DUT still can connect ")
            Console.Use_Device_WKS_Login("Shell_LAN1", "ExpectSSH", "root", "1234", "LAN1_WKS")
            Console.Retry_WKS_Ping("LAN1_WKS", "eth1", ["www.hinet.net", "168.95.1.1", "172.202.77.1"])



    @allure.title("UTP-5166 Upgrade/downgrade FW from FCS/Field FW via ACS server for 50 times")
    @allure.severity("Blocker")
    def test_case(self):

        Misc.ACTS_Dummy_Response("PASS", "Reset device")
        Reset_Device.Reset_Device(reset_device="YES", config_connection="NO", setup_device_wan="YES") 

        # check all WAN IP was up (get wan ip)
        if VAR("$first_etherwan_interface") != "None":
            wan = "ETHERNET"
            interface_ip = VAR("$first_etherwan_interface")
        else:
            wan = "PON"
            interface_ip = VAR("$first_ponwan_interface")

        Misc.ACTS_Dummy_Response("PASS", "Get CPE WAN IP")
        objDeviceConsole = Device_Console.Device_Console("DUT", VAR("$console_username"), VAR("$console_password"), second_Lv_command= VAR("$second_shell_command"), second_Lv_password= VAR("$second_shell_password"))
        objDeviceConsole.Get_Interface_IP(interface_ip, "WAN_v4_IP")
        
        # # Set up DUT and connect to ACS server
        objDeviceTR69 = Device_TR69.Device_TR69(VAR("$cpe_id"))
        objDeviceTR69.Delete_CPE()
        objDeviceTR69.Setup_TR069(username=VAR("$console_username"), password=VAR("$console_password"), acs_url=VAR("$acs_url_v4"), second_Lv_command=VAR("$second_shell_command"), second_Lv_password=VAR("$second_shell_password"))
        objDeviceTR69.Wait_for_CPE_Online()

        #  Modify baisc setting. 2.4G/5G WLAN SSID/password, VoIP seeting(can register successfully), IPTV.
        Misc.ACTS_Dummy_Response("PASS", "Start SIP server on NAT_WKS")
        Console.Use_Device_WKS_Login("WKS_Shell_NAT", "SSH", "root", "1234", address="NAT")
        Console.CI_Cmd_More([("/usr/local/sbin/opensipsctl start", 10)])
        Console.CI_Cmd_More([("opensipsctl start", 10)])
        Misc.Wait(5)
                    
        Console.CI_Cmd_More([("ps aux|grep opensip", 10)])
        Misc.Wait(5)
        Console.CI_Cmd_More([("exit", 10)])
        Misc.Wait(5)

        objDeviceWeb = Device_Web.Device_Web(VAR("$web_url"))
        objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))

        Misc.ACTS_Dummy_Response("PASS", "Setup Voip")
        objDeviceWeb.Setup_SIP_Account(bf_delete=False, index="1", enable="yes", sip_account_num="12345", sip_username="12345", sip_password="12345")
        Misc.Wait(20)

        objDeviceWeb.Setup_SIP_Service_Provider(bf_delete=False, index="1", enable="yes", sip_service_provider_name=VAR("$default_gateway"), 
                                                sip_proxy_server_address=VAR("$default_gateway"), sip_registrar_server_address=VAR("$default_gateway"),
                                                sip_service_domain=VAR("$default_gateway"))
        
        objDeviceWeb.Setup_Mesh("false")
        
        Misc.ACTS_Dummy_Response("PASS","Setup 2.4/5GHz WLAN SSID/PSK")
        objDeviceWeb.Setup_Wireless(band= "2.4GHz", bf_same_on_24_5G='false', name= "SSID22_2.4G", security_mode= "WPA3-Personal-Transition", password= "Test123456@")
        Misc.Wait(10)

        # objDeviceWeb.Setup_Wireless(band= "5GHz", bf_same_on_24_5G='false', name= "SSID22_5G", security_mode= "WPA3-Personal-Transition", password= "Test123456@")
        # Misc.Wait(10)

        objDeviceWeb.Check_WiFi_Setting(band = "2.4GHz", exp_name = "SSID22_2.4G", exp_password = "Test123456@")
        # objDeviceWeb.Check_WiFi_Setting(band= "5GHz", exp_name = "SSID22_5G", exp_password = "Test123456@")
        
        # check out setting should be kept (first check)
        objDeviceWeb.Web_Click_Menu("VoIP", "SIP", "tab_VoIP_SIPAccount_Tab")
        WebApp.WebDrv_Click("id","VoIP_SIPAccount_Edit1")
        WebApp.WebDrv_Check_Value("id","SIP_Account_number",chkVaule="12345", full_match= True)
        WebApp.WebDrv_Check_Value("id","SIP_Account_auth_username",chkVaule="12345", full_match= True)
        WebApp.WebDrv_Check_Value("id","SIP_Account_auth_password",chkVaule="********", full_match= True)
        WebApp.WebDrv_Click("id","SIP_Account_CancelBtn")
        WebApp.WebDrv_Wait_Device_Loading("xpath", "//div[@class=\"loader-spinner\"]")

        objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))
        objDeviceWeb.Web_Click_Menu("System Monitor", "VoIP_Status")
        WebApp.WebDrv_Check_Text("xpath", '//*[@id="SystemMonitor_VoIPStatus_Table1"]/tbody/tr[1]/td[3]', "Registered", "PASS", True)
        objDeviceWeb.Web_Logout()

        # ACS server do FW upgrade/downgrade (Field side or FCS <> formal FW).
        for i in range(1, 51):
            # Get device image sequence number
            objDeviceConsole = Device_Console.Device_Console("DUT", VAR("$console_username"), VAR("$console_password"), second_Lv_command=VAR("$second_shell_command"), second_Lv_password=VAR("$second_shell_password"))
            objDeviceConsole.Get_Image_Seq_Number("old_seq_number")

            Misc.ACTS_Dummy_Response("PASS","FW upgrade "+ str(i) +" times")
            objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))
            objDeviceWeb.Setup_FW_Upgrade(VAR("$tool_path")+"firmware/ras-c0.bin")
            Misc.Wait(200)

            objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))
            x = WebApp.WebDrv_Check_Text("id","card_sysinfo_fwversion", VAR("$fw_ras-c0_version"), full_match= True)
            if x is True :
                Misc.ACTS_Dummy_Response("PASS","ACS FW FCS upgrade to beta")
                objDeviceTR69.Download(f'{VAR("$tool_path")}firmware/ras.bin', "ras.bin", file_type="firmware", file_server_ipv4_or_ipv6="ipv4")

            else:
                Misc.ACTS_Dummy_Response("FAIL","DUT FW FCS can't upgrade to beta success")
            
            objDeviceWeb.Web_Logout()

            # Get device image sequence number
            objDeviceConsole.Console_Login(VAR("$console_username"), VAR("$console_password"), second_Lv_command= VAR("$second_shell_command"), second_Lv_password= VAR("$second_shell_password")) 
            objDeviceConsole.Get_Image_Seq_Number("new_seq_number")
        
            # After upgrade, check out FW has been upgrade successfully
            if VAR("new_seq_number") > VAR("old_seq_number"):
                Misc.ACTS_Dummy_Response("PASS","FW upgrade success")
            else:
                Misc.ACTS_Dummy_Response("FAIL", "FW upgarde failed. Old image sequence number=" + str(VAR("old_seq_number")) + "," + "new image sequence number=" + str(VAR("new_seq_number")))

            # check out setting should be kept (second check)
            objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))

            objDeviceWeb.Check_WiFi_Setting(band = "2.4GHz", exp_name = "SSID22_2.4G", exp_password = "Test123456@")
            # objDeviceWeb.Check_WiFi_Setting(band= "5GHz", exp_name = "SSID22_5G", exp_password = "Test123456@")
    

            objDeviceWeb.Web_Click_Menu("VoIP", "SIP", "tab_VoIP_SIPAccount_Tab")
            WebApp.WebDrv_Click("id","VoIP_SIPAccount_Edit1")
            WebApp.WebDrv_Check_Value("id","SIP_Account_number",chkVaule="12345", full_match= True)
            WebApp.WebDrv_Check_Value("id","SIP_Account_auth_username",chkVaule="12345", full_match= True)
            WebApp.WebDrv_Check_Value("id","SIP_Account_auth_password",chkVaule="********", full_match= True)
            WebApp.WebDrv_Click("id","SIP_Account_CancelBtn")
            WebApp.WebDrv_Wait_Device_Loading("xpath", "//div[@class=\"loader-spinner\"]")
            objDeviceWeb.Web_Logout()

            # check out VoIP register status `successfully`.
            Misc.ACTS_Dummy_Response("PASS", "Check registration status")
            objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))
            objDeviceWeb.Web_Click_Menu("System Monitor", "VoIP_Status")
            WebApp.WebDrv_Check_Text("xpath", '//*[@id="SystemMonitor_VoIPStatus_Table1"]/tbody/tr[1]/td[3]', "Registered", "PASS", True)
            objDeviceWeb.Web_Logout()

            # Do ping to internet.
            Misc.ACTS_Dummy_Response("PASS", "Check DUT still can connect ")
            Console.Use_Device_WKS_Login("Shell_LAN1", "ExpectSSH", "root", "1234", "LAN1_WKS")
            Console.Retry_WKS_Ping("LAN1_WKS", "eth1", ["www.hinet.net", "168.95.1.1", "172.202.77.1"])

    

    @allure.title("UTP-5165 Upgrade Dummy FW from ACS server for 50 times.(ACS wtih domain name)")
    @allure.severity("Blocker")
    def test_case(self):

        Misc.ACTS_Dummy_Response("PASS", "Reset device")
        Reset_Device.Reset_Device(reset_device="YES", config_connection="NO", setup_device_wan="NO") 

        # check all WAN IP was up (get wan ip)
        if VAR("$first_etherwan_interface") != "None":
            wan = "ETHERNET"
            interface_ip = VAR("$first_etherwan_interface")
        else:
            wan = "PON"
            interface_ip = VAR("$first_ponwan_interface")

        Misc.ACTS_Dummy_Response("PASS", "Get CPE WAN IP")
        objDeviceConsole = Device_Console.Device_Console("DUT", VAR("$console_username"), VAR("$console_password"), second_Lv_command= VAR("$second_shell_command"), second_Lv_password= VAR("$second_shell_password"))
        objDeviceConsole.Get_Interface_IP(interface_ip, "WAN_v4_IP")

        # Set up DUT and connect to ACS server
        objDeviceTR69 = Device_TR69.Device_TR69(VAR("$cpe_id"))
        objDeviceTR69.Delete_CPE()
        objDeviceTR69.Setup_TR069(username=VAR("$console_username"), password=VAR("$console_password"), acs_url=VAR("$acs_url_domain"), second_Lv_command=VAR("$second_shell_command"), second_Lv_password=VAR("$second_shell_password"))
        objDeviceTR69.Wait_for_CPE_Online()


        #  Modify baisc setting. 2.4G/5G WLAN SSID/password, VoIP seeting(can register successfully), IPTV.
        Misc.ACTS_Dummy_Response("PASS", "Start SIP server on NAT_WKS")
        Console.Use_Device_WKS_Login("WKS_Shell_NAT", "SSH", "root", "1234", address="NAT")
        Console.CI_Cmd_More([("/usr/local/sbin/opensipsctl start", 10)])
        Console.CI_Cmd_More([("opensipsctl start", 10)])
        Misc.Wait(5)
                    
        Console.CI_Cmd_More([("ps aux|grep opensip", 10)])
        Misc.Wait(5)
        Console.CI_Cmd_More([("exit", 10)])
        Misc.Wait(5)

        objDeviceWeb = Device_Web.Device_Web(VAR("$web_url"))
        objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))

        Misc.ACTS_Dummy_Response("PASS", "Setup Voip")
        objDeviceWeb.Setup_SIP_Account(bf_delete=False, index="1", enable="yes", sip_account_num="12345", sip_username="12345", sip_password="12345")
        Misc.Wait(20)

        objDeviceWeb.Setup_SIP_Service_Provider(bf_delete=False, index="1", enable="yes", sip_service_provider_name=VAR("$default_gateway"), 
                                                sip_proxy_server_address=VAR("$default_gateway"), sip_registrar_server_address=VAR("$default_gateway"),
                                                sip_service_domain=VAR("$default_gateway"))
        
        objDeviceWeb.Setup_Mesh("false")
        
        Misc.ACTS_Dummy_Response("PASS","Setup 2.4/5GHz WLAN SSID/PSK")
        objDeviceWeb.Setup_Wireless(band= "2.4GHz", bf_same_on_24_5G='false', name= "SSID2233_2.4G", security_mode= "WPA3-Personal-Transition", password= "Test1234@")
        Misc.Wait(10)

        # objDeviceWeb.Setup_Wireless(band= "5GHz", bf_same_on_24_5G='false', name= "SSID2233_5G", security_mode= "WPA3-Personal-Transition", password= "Test1234@")
        # Misc.Wait(10)

        objDeviceWeb.Check_WiFi_Setting(band = "2.4GHz", exp_name = "SSID2233_2.4G", exp_password = "Test1234@")
        # objDeviceWeb.Check_WiFi_Setting(band= "5GHz", exp_name = "SSID2233_5G", exp_password = "Test1234@")
        
        # check out setting should be kept (first check)
        objDeviceWeb.Web_Click_Menu("VoIP", "SIP", "tab_VoIP_SIPAccount_Tab")
        WebApp.WebDrv_Click("id","VoIP_SIPAccount_Edit1")
        WebApp.WebDrv_Check_Value("id","SIP_Account_number",chkVaule="12345", full_match= True)
        WebApp.WebDrv_Check_Value("id","SIP_Account_auth_username",chkVaule="12345", full_match= True)
        WebApp.WebDrv_Check_Value("id","SIP_Account_auth_password",chkVaule="********", full_match= True)
        WebApp.WebDrv_Click("id","SIP_Account_CancelBtn")
        WebApp.WebDrv_Wait_Device_Loading("xpath", "//div[@class=\"loader-spinner\"]")

        # check out VoIP register status `successfully`.
        Misc.ACTS_Dummy_Response("PASS", "Check registration status")
        objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))
        objDeviceWeb.Web_Click_Menu("System Monitor", "VoIP_Status")
        WebApp.WebDrv_Check_Text("xpath", '//*[@id="SystemMonitor_VoIPStatus_Table1"]/tbody/tr[1]/td[3]', "Registered", "PASS", True)
        objDeviceWeb.Web_Logout()

        # ACS server do FW upgrade (formal <> dummy FW).
        for i in range(1, 51):
            Misc.ACTS_Dummy_Response("PASS","FW upgrade "+ str(i) +" times")

            # Get device image sequence number
            objDeviceConsole = Device_Console.Device_Console("DUT", VAR("$console_username"), VAR("$console_password"), second_Lv_command=VAR("$second_shell_command"), second_Lv_password=VAR("$second_shell_password"))
            objDeviceConsole.Get_Image_Seq_Number("old_seq_number")
            
            # upgrade to  formal fw 
            objDeviceTR69.Download(f'{VAR("$tool_path")}firmware/ras.bin', "ras.bin", file_type="firmware", file_server_ipv4_or_ipv6="ipv4")

            objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))
            x = WebApp.WebDrv_Check_Text("id","card_sysinfo_fwversion", VAR("$fw_version"), full_match= True)
            if x is True :
                Misc.ACTS_Dummy_Response("PASS","ACS FW formal upgrade to dummy FW")
                objDeviceTR69.Download(f'{VAR("$tool_path")}firmware/ras-dummy.bin', "ras-dummy.bin", file_type="firmware", file_server_ipv4_or_ipv6="ipv4")

            else:
                Misc.ACTS_Dummy_Response("FAIL","DUT FW FCS can't upgrade to dummy FW success")

            objDeviceWeb.Web_Logout()

            # Get device image sequence number
            objDeviceConsole.Console_Login(VAR("$console_username"), VAR("$console_password"), second_Lv_command= VAR("$second_shell_command"), second_Lv_password= VAR("$second_shell_password")) 
            objDeviceConsole.Get_Image_Seq_Number("new_seq_number")
        
            # After upgrade, check out FW has been upgrade successfully
            if VAR("new_seq_number") > VAR("old_seq_number"):
                Misc.ACTS_Dummy_Response("PASS","FW upgrade success")
            else:
                Misc.ACTS_Dummy_Response("FAIL", "FW upgarde failed. Old image sequence number=" + str(VAR("old_seq_number")) + "," + "new image sequence number=" + str(VAR("new_seq_number")))

            # check out setting should be kept (second check)
            objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))

            objDeviceWeb.Check_WiFi_Setting(band = "2.4GHz", exp_name = "SSID2233_2.4G", exp_password = "Test1234@")
            # objDeviceWeb.Check_WiFi_Setting(band= "5GHz", exp_name = "SSID2233_5G", exp_password = "Test1234@")

            objDeviceWeb.Web_Click_Menu("VoIP", "SIP", "tab_VoIP_SIPAccount_Tab")
            WebApp.WebDrv_Click("id","VoIP_SIPAccount_Edit1")
            WebApp.WebDrv_Check_Value("id","SIP_Account_number",chkVaule="12345", full_match= True)
            WebApp.WebDrv_Check_Value("id","SIP_Account_auth_username",chkVaule="12345", full_match= True)
            WebApp.WebDrv_Check_Value("id","SIP_Account_auth_password",chkVaule="********", full_match= True)
            WebApp.WebDrv_Click("id","SIP_Account_CancelBtn")
            WebApp.WebDrv_Wait_Device_Loading("xpath", "//div[@class=\"loader-spinner\"]")
            objDeviceWeb.Web_Logout()

            # check out VoIP register status `successfully`.
            Misc.ACTS_Dummy_Response("PASS", "Check registration status")
            objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))
            objDeviceWeb.Web_Click_Menu("System Monitor", "VoIP_Status")
            WebApp.WebDrv_Check_Text("xpath", '//*[@id="SystemMonitor_VoIPStatus_Table1"]/tbody/tr[1]/td[3]', "Registered", "PASS", True)
            objDeviceWeb.Web_Logout()

            # Do ping to internet.
            Misc.ACTS_Dummy_Response("PASS", "Check DUT still can connect ")
            Console.Use_Device_WKS_Login("Shell_LAN1", "ExpectSSH", "root", "1234", "LAN1_WKS")
            Console.Retry_WKS_Ping("LAN1_WKS", "eth1", ["www.hinet.net", "168.95.1.1", "172.202.77.1"])
        

    @allure.title("UTP-5167 TR69 provision customer setting after reset to default for 50 times")
    @allure.severity("Blocker")
    def test_case(self): 

        Misc.ACTS_Dummy_Response("PASS", "Reset device")
        Reset_Device.Reset_Device(reset_device="YES", config_connection="NO", setup_device_wan="NO") 

        # Request RD provide the special FW that modifyied ACS URL, Certificate, Firewall rule can auto connect to Auto station ACS server.
        # DUT can auto connect to ACS server every time.(0 BOOTSTRAP, 1 BOOT, 4 Value Chang)
        objDeviceTR69 = Device_TR69.Device_TR69(VAR("$cpe_id"))

        Misc.ACTS_Dummy_Response("PASS", "Setup ACS URL")
        objDeviceTR69.Delete_CPE()
        objDeviceTR69.Setup_TR069(username=VAR("$console_username"), password=VAR("$console_password"), acs_url=VAR("$acs_url_v4"), second_Lv_command=VAR("$second_shell_command"), second_Lv_password=VAR("$second_shell_password"))
        objDeviceTR69.Wait_for_CPE_Online()

        Misc.ACTS_Dummy_Response("PASS", "Check the first Inform with Event Code")
        objDeviceTR69.Check_CPE_Event_Code(["0 BOOTSTRAP", "1 BOOT"])

        Console.Use_Device_WKS_Login("WKS_Shell_NAT", "SSH", "root", "1234", address="NAT")
        Console.CI_Cmd_More([("/usr/local/sbin/opensipsctl start", 10)])
        Console.CI_Cmd_More([("opensipsctl start", 10)])
        Misc.Wait(5)
                    
        Console.CI_Cmd_More([("ps aux|grep opensip", 10)])
        Misc.Wait(5)
        Console.CI_Cmd_More([("exit", 10)])
        Misc.Wait(5)

        Misc.ACTS_Dummy_Response("PASS", "ACS Setup Voip")
        if VAR("$data_model") == "TR181":
            parameters = {
                "Device.Services.VoiceService.1.VoiceProfile.1.Enable":"Enabled",
                "Device.Services.VoiceService.1.VoiceProfile.1.Line.1.DirectoryNumber": 12345,
                "Device.Services.VoiceService.1.VoiceProfile.1.Line.1.SIP.AuthUserName": 12345,
                "Device.Services.VoiceService.1.VoiceProfile.1.Line.1.SIP.AuthPassword": 12345,
                "Device.Services.VoiceService.1.VoiceProfile.1.Line.1.Enable": "Enabled",
                "Device.Services.VoiceService.1.VoiceProfile.1.Name": VAR("$default_gateway"),
                "Device.Services.VoiceService.1.VoiceProfile.1.SIP.ProxyServer": VAR("$default_gateway"),
                "Device.Services.VoiceService.1.VoiceProfile.1.SIP.RegistrarServer": VAR("$default_gateway"),
                "Device.Services.VoiceService.1.VoiceProfile.1.SIP.UserAgentDomain": VAR("$default_gateway")
            }
        else:
            parameters = {
                "InternetGatewayDevice.Services.VoiceService.1.VoiceProfile.1.Enable": "Enabled",
                "InternetGatewayDevice.Services.VoiceService.1.VoiceProfile.1.Line.1.DirectoryNumber": 12345,
                "InternetGatewayDevice.Services.VoiceService.1.VoiceProfile.1.Line.1.SIP.AuthUserName": 12345,
                "InternetGatewayDevice.Services.VoiceService.1.VoiceProfile.1.Line.1.SIP.AuthPassword": 12345,
                "InternetGatewayDevice.Services.VoiceService.1.VoiceProfile.1.Line.1.Enable": "Enabled",
                "InternetGatewayDevice.Services.VoiceService.1.VoiceProfile.1.Name": VAR("$default_gateway"),
                "InternetGatewayDevice.Services.VoiceService.1.VoiceProfile.1.SIP.ProxyServer": VAR("$default_gateway"),
                "InternetGatewayDevice.Services.VoiceService.1.VoiceProfile.1.SIP.RegistrarServer": VAR("$default_gateway"),
                "InternetGatewayDevice.Services.VoiceService.1.VoiceProfile.1.SIP.UserAgentDomain": VAR("$default_gateway")
            }

        objDeviceTR69.SetParameterValues(parameters)
        Misc.Wait(4)

        Misc.ACTS_Dummy_Response("PASS", "Save Rom-D")
        objDeviceWeb = Device_Web.Device_Web(VAR("$web_url"))
        objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))
        objDeviceWeb.Web_Click_Menu("Maintenance","Backup_Restore","tab_Maintenance_Backup_ROMD_Tab")
        WebApp.WebDrv_Click("id","romd_save_btn")
        WebApp.WebDrv_Wait_Device_Loading("xpath", "//div[@class=\"loader-spinner\"]")
        objDeviceWeb.Web_Logout()

        # Connect LAN PC, WiFi client to 2.4G/ 5G.
        Misc.ACTS_Dummy_Response("PASS", "Connect LAN PC, must ping PASS.")
        Console.Use_Device_WKS_Login("Shell_LAN1", "ExpectSSH", "root", "1234", "LAN1_WKS")
        Console.Retry_WKS_Ping("LAN1_WKS", "eth1", ["www.hinet.net", "168.95.1.1", "172.202.77.1"])

        # Repeat Reset to default and auto provision 50 times.
        for i in range(1, 51):
            # Do reset to default from DUT.
            Misc.ACTS_Dummy_Response("PASS"," Repeat Reset to default and auto provision "+ str(i) +" times")
            
            objDeviceWeb = Device_Web.Device_Web(VAR("$web_url"))
            objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))
            objDeviceWeb.Web_Click_Menu("Maintenance","Backup_Restore","tab_Maintenance_Backup_BackupRestore_Tab")
            WebApp.WebDrv_Click("id","reset_config_reset_btn")
            WebApp.WebDrv_Click("id","alertOKBtn")
            WebApp.WebDrv_Wait_Device_Loading("xpath", "//div[@class=\"loader-spinner\"]")
            Misc.Wait(200)
            
            objDeviceWeb.Web_CloseWebSite()

            # After boot up, DUT should auto connect to ACS server.
            Reset_Device.Reset_Device(reset_device="NO", config_connection="YES", setup_device_wan="NO")
            Misc.ACTS_Dummy_Response("PASS"," Check CPE can Connection Request")
            
            objDeviceTR69 = Device_TR69.Device_TR69(VAR("$cpe_id"))
            if VAR("$data_model") == "TR181":
                parameters = {
                    "Device.DeviceInfo.SerialNumber": VAR("$cpe_id")
            }
            else:
                parameters = {
                    "InternetGatewayDevice.DeviceInfo.SerialNumber": VAR("$cpe_id") 
            }

            objDeviceTR69.GetParameterValues(parameters)

            objDeviceTR69.Check_CPE_Event_Code(["6 CONNECTION REQUEST"])
            Misc.Wait(60)

            # Then ACS Server provision customer setting. (skip)


            # Check out all SPV was successfully.
            Misc.ACTS_Dummy_Response("PASS"," Check all SPV was successfully")
            
            objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))
            objDeviceWeb.Web_Click_Menu("VoIP", "SIP", "tab_VoIP_SIPAccount_Tab")
            WebApp.WebDrv_Click("id","VoIP_SIPAccount_Edit1")
            WebApp.WebDrv_Check_Value("id","SIP_Account_number",chkVaule="12345", full_match= True)
            WebApp.WebDrv_Check_Value("id","SIP_Account_auth_username",chkVaule="12345", full_match= True)
            WebApp.WebDrv_Check_Value("id","SIP_Account_auth_password",chkVaule="********", full_match= True)
            WebApp.WebDrv_Click("id","SIP_Account_CancelBtn")
            WebApp.WebDrv_Wait_Device_Loading("xpath", "//div[@class=\"loader-spinner\"]")

            Misc.ACTS_Dummy_Response("PASS", "Check registration status")
            objDeviceWeb.Web_Click_Menu("System Monitor", "VoIP_Status")
            WebApp.WebDrv_Check_Text("xpath", '//*[@id="SystemMonitor_VoIPStatus_Table1"]/tbody/tr[1]/td[3]', "Registered", "PASS", True)
            objDeviceWeb.Web_Logout()
            

    @allure.title("UTP-6849 Unplug/ plug Physical link for 100 times per multi CO (interval 10s)")
    @allure.severity("Blocker")
    def test_case(self):

        # (If your GPON project support multi OLT connection, you must select two OLT to test: "Brazil: ALU and Huawei OLT")
        # Select DUT connect to priority OLT: ALU.
        Misc.ACTS_Dummy_Response("PASS", "Reset device")
        Reset_Device.Reset_Device(reset_device="YES", config_connection="NO", setup_device_wan="YES") 

        if VAR("$first_etherwan_interface") != "None":
            wan = "ETHERNET"
            interface_ip = VAR("$first_etherwan_interface")
        else:
            wan = "PON"
            interface_ip = VAR("$first_ponwan_interface")

        
        Misc.ACTS_Dummy_Response("PASS", "Get CPE WAN IP")
        objDeviceConsole = Device_Console.Device_Console("DUT", VAR("$console_username"), VAR("$console_password"), second_Lv_command= VAR("$second_shell_command"), second_Lv_password= VAR("$second_shell_password"))
        objDeviceConsole.Get_Interface_IP(interface_ip, "WAN_v4_IP")

        # Set up DUT and connect to ACS server.
        objDeviceTR69 = Device_TR69.Device_TR69(VAR("$cpe_id"))
        objDeviceTR69.Delete_CPE()
        objDeviceTR69.Setup_TR069(username=VAR("$console_username"), password=VAR("$console_password"), acs_url=VAR("$acs_url_domain"), second_Lv_command=VAR("$second_shell_command"), second_Lv_password=VAR("$second_shell_password"))
        # objDeviceTR69.Wait_for_CPE_Online()

        # Modify basic setting. 2.4G/5G WLAN SSID/password, VoIP setting(can register successfully), IPTV.
        Misc.ACTS_Dummy_Response("PASS", "Start SIP server on NAT_WKS")
        Console.Use_Device_WKS_Login("WKS_Shell_NAT", "SSH", "root", "1234", address="NAT")
        Console.CI_Cmd_More([("/usr/local/sbin/opensipsctl start", 10)])
        Console.CI_Cmd_More([("opensipsctl start", 10)])
        Misc.Wait(5)
                    
        Console.CI_Cmd_More([("ps aux|grep opensip", 10)])
        Misc.Wait(5)
        Console.CI_Cmd_More([("exit", 10)])
        Misc.Wait(5)

        objDeviceWeb = Device_Web.Device_Web(VAR("$web_url"))
        objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))

        Misc.ACTS_Dummy_Response("PASS", "Setup Voip")
        objDeviceWeb.Setup_SIP_Account(bf_delete=False, index="1", enable="yes", sip_account_num="12345", sip_username="12345", sip_password="12345")
        Misc.Wait(20)

        objDeviceWeb.Setup_SIP_Service_Provider(bf_delete=False, index="1", enable="yes", sip_service_provider_name=VAR("$default_gateway"), 
                                                sip_proxy_server_address=VAR("$default_gateway"), sip_registrar_server_address=VAR("$default_gateway"),
                                                sip_service_domain=VAR("$default_gateway"))
        
        # c. check out VoIP register status `Registered`.
        Misc.ACTS_Dummy_Response("PASS", "Check registration status")
        objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))
        objDeviceWeb.Web_Click_Menu("System Monitor", "VoIP_Status")
        WebApp.WebDrv_Check_Text("xpath", '//*[@id="SystemMonitor_VoIPStatus_Table1"]/tbody/tr[1]/td[3]', "Registered", "PASS", True)
        
        objDeviceWeb.Setup_Mesh("false")
        
        Misc.ACTS_Dummy_Response("PASS","Setup 2.4/5GHz WLAN SSID/PSK")
        objDeviceWeb.Setup_Wireless(band= "2.4GHz", bf_same_on_24_5G='false', name= "SSID2244_2.4G", security_mode= "WPA3-Personal-Transition", password= "Test1234111@")
        Misc.Wait(10)

        # objDeviceWeb.Setup_Wireless(band= '5GHz', bf_same_on_24_5G='false', name= 'SSID2244_5G', security_mode= 'WPA3-Personal-Transition', password= 'Test1234111@')
        # Misc.Wait(10)

        objDeviceWeb.Web_Logout()
        

        # Repeat Step3~4 100 times.
        for i in range(1, 101):
            # step.3 Auto station do physical link down/up interval 10s.
            Misc.ACTS_Dummy_Response("PASS","Do physical link down/up "+ str(i) +" times")
            Misc.Enable_NIC("WAN", "Disable")
            Misc.Wait(10)
            Misc.Enable_NIC("WAN", "Enable")
            Misc.Wait(180)

            # step.4 After one cycle(link down/up), check out below point:
            #  a. LAN IPTV can play MOD. (skip)

            #  b. do ping to internet.
            Misc.ACTS_Dummy_Response("PASS", "Check DUT still can connect ")
            Console.Use_Device_WKS_Login("Shell_LAN1", "ExpectSSH", "root", "1234", "LAN1_WKS")
            Console.Retry_WKS_Ping("LAN1_WKS", "eth1", ["www.hinet.net", "168.95.1.1", "172.202.77.1"])

            # Connect DUT to secondary OLT: Huawei and Repeat Step3~4 50 times. (skip)
    

    @allure.title("UTP-36054 Unplug/ plug Physical link for 100 times per multi CO (interval 1min)")
    @allure.severity("Blocker")
    def test_case(self):

        # (If your GPON project support multi OLT connection, you must select two OLT to test: "Brazil: ALU and Huawei OLT")
        # Select DUT connect to priority OLT: ALU.
        Misc.ACTS_Dummy_Response("PASS", "Reset device")
        Reset_Device.Reset_Device(reset_device="YES", config_connection="NO", setup_device_wan="YES") 

        # d. check all WAN IP was up.
        if VAR("$first_etherwan_interface") != "None":
            wan = "ETHERNET"
            interface_ip = VAR("$first_etherwan_interface")
        else:
            wan = "PON"
            interface_ip = VAR("$first_ponwan_interface")


        Misc.ACTS_Dummy_Response("PASS", "Get CPE WAN IP")
        objDeviceConsole = Device_Console.Device_Console("DUT", VAR("$console_username"), VAR("$console_password"), second_Lv_command= VAR("$second_shell_command"), second_Lv_password= VAR("$second_shell_password"))
        objDeviceConsole.Get_Interface_IP(interface_ip, "WAN_v4_IP")

        # Set up DUT and connect to ACS server.
        objDeviceTR69 = Device_TR69.Device_TR69(VAR("$cpe_id"))
        objDeviceTR69.Delete_CPE()
        objDeviceTR69.Setup_TR069(username=VAR("$console_username"), password=VAR("$console_password"), acs_url=VAR("$acs_url_domain"), second_Lv_command=VAR("$second_shell_command"), second_Lv_password=VAR("$second_shell_password"))
        # objDeviceTR69.Wait_for_CPE_Online()

        # Modify basic setting. 2.4G/5G WLAN SSID/password, VoIP setting(can register successfully), IPTV.
        Misc.ACTS_Dummy_Response("PASS", "Start SIP server on NAT_WKS")
        Console.Use_Device_WKS_Login("WKS_Shell_NAT", "SSH", "root", "1234", address="NAT")
        Console.CI_Cmd_More([("/usr/local/sbin/opensipsctl start", 10)])
        Console.CI_Cmd_More([("opensipsctl start", 10)])
        Misc.Wait(5)
                    
        Console.CI_Cmd_More([("ps aux|grep opensip", 10)])
        Misc.Wait(5)
        Console.CI_Cmd_More([("exit", 10)])
        Misc.Wait(5)

        objDeviceWeb = Device_Web.Device_Web(VAR("$web_url"))
        objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))

        Misc.ACTS_Dummy_Response("PASS", "Setup Voip")
        objDeviceWeb.Setup_SIP_Account(bf_delete=False, index="1", enable="yes", sip_account_num="12345", sip_username="12345", sip_password="12345")
        Misc.Wait(20)

        objDeviceWeb.Setup_SIP_Service_Provider(bf_delete=False, index="1", enable="yes", sip_service_provider_name=VAR("$default_gateway"), 
                                                sip_proxy_server_address=VAR("$default_gateway"), sip_registrar_server_address=VAR("$default_gateway"),
                                                sip_service_domain=VAR("$default_gateway"))
        
        # c. check out VoIP register status `Registered`.
        Misc.ACTS_Dummy_Response("PASS", "Check registration status")

        objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))
        objDeviceWeb.Web_Click_Menu("System Monitor", "VoIP_Status")
        WebApp.WebDrv_Check_Text("xpath", '//*[@id="SystemMonitor_VoIPStatus_Table1"]/tbody/tr[1]/td[3]', "Registered", "PASS", True)

        objDeviceWeb.Setup_Mesh("false")
        
        Misc.ACTS_Dummy_Response("PASS","Setup 2.4/5GHz WLAN SSID/PSK")
        objDeviceWeb.Setup_Wireless(band= "2.4GHz", bf_same_on_24_5G='false', name= "SSID2255_2.4G", security_mode= "WPA3-Personal-Transition", password= "Test1234333@")
        Misc.Wait(10)

        # objDeviceWeb.Setup_Wireless(band= '5GHz', bf_same_on_24_5G='false', name= 'SSID2255_5G', security_mode= 'WPA3-Personal-Transition', password= 'Test1234333@')
        # Misc.Wait(10)
        
        objDeviceWeb.Check_WiFi_Setting(band = "2.4GHz", exp_name = "SSID2255_2.4G", exp_password = "Test1234333@")
        # objDeviceWeb.Check_WiFi_Setting(band= "5GHz", exp_name = "SSID2255_5G", exp_password = "Test1234333@")

        objDeviceWeb.Web_Logout()

        # Repeat Step3~4 100 times.
        for i in range(1, 101):
            # step.3 Auto station do physical link down/up interval 1min.
            Misc.ACTS_Dummy_Response("PASS","Reboot power switch "+ str(i) +" times")
            Misc.Enable_NIC("WAN", "Disable")
            Misc.Wait(60)
            Misc.Enable_NIC("WAN", "Enable")
            Misc.Wait(180)

            # step.4 After one cycle(link down/up), check out below point:
            #  a. LAN IPTV can play MOD. (skip)

            #  b. do ping to internet.
            Misc.ACTS_Dummy_Response("PASS", "Check DUT still can connect ")
            Console.Use_Device_WKS_Login("Shell_LAN1", "ExpectSSH", "root", "1234", "LAN1_WKS")
            Console.Retry_WKS_Ping("LAN1_WKS", "eth1", ["www.hinet.net", "168.95.1.1", "172.202.77.1"])

            # Connect DUT to secondary OLT: Huawei and Repeat Step3~4 50 times. (skip)


