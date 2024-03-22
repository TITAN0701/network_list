from lib.Common import *
from pathlib import Path
import datetime

import api.Console as Console
import api.Misc as Misc
import api.TR as TR
import api.WebApp as WebApp

import module.Reset_Device as Reset_Device
import module.Device_Console as Device_Console
import module.Device_Web as Device_Web
import module.Device_TR69 as Device_TR69
import module.Device_Config as Device_Config

@allure.feature("WAP Function (Extender_OPAL)")
class TestWAPFunction:

    @allure.title("OPAL-36876 Verify upgrade and downgrade firmware from the previous beta version to this bet")
    @allure.severity("Critical")
    def test_case(self):

        # Change DUT function setting(EX : Wireless 2.4G/5G, Account password, Time, TR069 page.....).
        Misc.ACTS_Dummy_Response("PASS","Setup Wireless 2.4G/5G")
        objDeviceWeb = Device_Web.Device_Web(VAR("$web_url"))
        objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))

        objDeviceWeb.Setup_Mesh("false")
        WebApp.WebDrv_Click("id","tab_Wireless_General_Tab")
        Misc.Wait(5)
        
        objDeviceWeb.Setup_Wireless(band='2.4GHz',bf_same_on_24_5G='false', name= '2.4Gssid', security_mode= 'WPA3-Personal-Transition', password= '!Aa12345')
        objDeviceWeb.Setup_Wireless(band='5GHz', name= '5Gssid', security_mode= 'WPA3-Personal-Transition', password= '!Aa12345')

        Misc.ACTS_Dummy_Response("PASS","Setup 2.4G more AP")
        WebApp.WebDrv_Click("id","tab_Wireless_Guest_Tab")
        WebApp.WebDrv_List_Select("id","wifi_guest_band","text","2.4GHz")
        WebApp.WebDrv_Click("id","Network_Wireless_Guest_Edit1")
        WebApp.WebDrv_Click("xpath","/html/body/div/div/div[5]/div/div[2]/div[2]/div/div[1]/div/div/label")
        
        WebApp.WebDrv_Set_Value("id","wifi_ssid_0110moreap0110","guest1_24G_check")
        WebApp.WebDrv_Click("xpath","/html/body/div/div/div[5]/div/div[2]/div[2]/div/div[11]/div[3]/div[3]/label")
        WebApp.WebDrv_Set_Value("id","wifi_wpa_psk_0110moreap0110","!Aa12345")
        WebApp.WebDrv_Click("id","Network_Wireless_APEdit_ApplyBtn")
        WebApp.WebDrv_Wait_Device_Loading("xpath","//div[@class=\"loader-spinner\"]", timeout= 20)
        Misc.Wait(20)

        Misc.ACTS_Dummy_Response("PASS","Setup 5G more AP")
        WebApp.WebDrv_Click("id","tab_Wireless_Guest_Tab")
        WebApp.WebDrv_List_Select("id","wifi_guest_band","text","5GHz")
        WebApp.WebDrv_Click("id","Network_Wireless_Guest_Edit1")
        WebApp.WebDrv_Click("xpath","/html/body/div/div/div[5]/div/div[2]/div[2]/div/div[1]/div/div/label")
        
        WebApp.WebDrv_Set_Value("id","wifi_ssid_0110moreap0110","guest1_5G_check")
        WebApp.WebDrv_Click("xpath","/html/body/div/div/div[5]/div/div[2]/div[2]/div/div[11]/div[3]/div[3]/label")
        WebApp.WebDrv_Set_Value("id","wifi_wpa_psk_0110moreap0110","!Aa12345")
        WebApp.WebDrv_Click("id","Network_Wireless_APEdit_ApplyBtn")
        WebApp.WebDrv_Wait_Device_Loading("xpath","//div[@class=\"loader-spinner\"]", timeout= 20)
        Misc.Wait(20)

        Misc.ACTS_Dummy_Response("PASS","Setup Account password")
        objDeviceWeb.Setup_User_Account(index= "-1", name= "Test_zyxel", enable="yes", password= "+Smile1111")

        Misc.ACTS_Dummy_Response("PASS","Setup Time")
        objDeviceWeb.Setup_Time(first_addr='Other', addr1='time.windows.com', time_zone='CST-8-2')

        Misc.ACTS_Dummy_Response("PASS","Setup TR069")
        objDeviceWeb.Setup_ACS_URL("true", "true", ip_protocol= "auto", acs_url=VAR("$acs_url_domain"))

        #####################################################################################################################

        # Make sure all service 2.4G/5G/ LAN, IPTV, TR069 work well.
        Misc.ACTS_Dummy_Response("PASS","Check wifi setting")
        objDeviceWeb.Check_WiFi_Setting(band= "2.4GHz",exp_name= "2.4Gssid",exp_password= "!Aa12345")
        objDeviceWeb.Check_WiFi_Setting(band= "5Ghz",exp_name= "5Gssid",exp_password= "!Aa12345")

        Misc.ACTS_Dummy_Response("PASS","Check More AP setting")
        objDeviceWeb.Check_More_AP(band= "2.4GHz", index= "1", exp_active= "true", exp_ssid= "guest1_24G_check", exp_password= "!Aa12345")
        objDeviceWeb.Check_More_AP(band= "5Ghz", index= "1", exp_active= "true", exp_ssid= "guest1_5G_check", exp_password= "!Aa12345")

        Misc.ACTS_Dummy_Response("PASS","Check Account setting")
        objDeviceWeb.Web_Click_Menu("Maintenance","User_Account")
        WebApp.WebDrv_Check_Text("xpath","//*[@id='Maintenance_UserAccount_Table']/tbody/tr[2]/td[3]","Test_zyxel")
        objDeviceWeb.Web_Logout()

        objDeviceWeb.Setup_Login_Change_Password("Test_zyxel","+Smile1111","@Zyxel1111")
        objDeviceWeb.Web_Logout()


        Misc.ACTS_Dummy_Response("PASS","Check Time setting")
        objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))
        objDeviceWeb.Web_Click_Menu("Maintenance","Time")
        WebApp.WebDrv_Check_Value("id","serveraddr1","time.windows.com")
        WebApp.WebDrv_Check_Value("id","mtenTimeZone","CST-8-2")

        Misc.ACTS_Dummy_Response("PASS","Check TR069 can work well")
        objDeviceTR69 = Device_TR69.Device_TR69(VAR("$cpe_id"))
        if VAR("$data_model") == "TR181":
            parameters = {
                "Device.ManagementServer.URL":VAR("$acs_url_domain")
            }
        else:
            parameters = {
                "InternetGatewayDevice.ManagementServer.URL":VAR("$acs_url_domain")
            } 

        if VAR("$first_etherwan_interface") != "None":
            interface_ip = VAR("$first_etherwan_interface")
        else:
            interface_ip = VAR("$first_ponwan_interface")

        objDeviceConsole = Device_Console.Device_Console("DUT", VAR("$console_username"), VAR("$console_password"))
        objDeviceConsole.Get_Interface_IP(interface_ip, "WAN_v4_IP")
        ipv4 = VAR("WAN_v4_IP")

        objDeviceWeb.Setup_ACS_URL(ip_protocol="ipv4")
        objDeviceWeb.Web_Click_Menu("connect","")
        
        connecturl = f'http://{ipv4}:7547'
        objDeviceWeb.Check_ACS_URL(exp_ip_protocol=VAR("WAN_v4_IP"), exp_connection_request_authentication="true", exp_connection_request_url=connecturl)
        objDeviceTR69.GetParameterValues(parameters)
        objDeviceTR69.Check_CPE_Event_Code(["6 CONNECTION REQUEST"])

        objDeviceWeb.Web_Logout()

        #####################################################################################################################
        # To check DUT config after config Restore and get br0 interface
        objDeviceConsole = Device_Console.Device_Console("DUT", VAR("$console_username"), VAR("$console_password"), second_Lv_command=VAR("$second_shell_command"), second_Lv_password=VAR("$second_shell_password"))
        
        Misc.ACTS_Dummy_Response("PASS","Get old image sequence")
        objDeviceConsole.Console_Login(VAR("$console_username"), VAR("$console_password"), second_Lv_command= VAR("$second_shell_command"), second_Lv_password= VAR("$second_shell_password")) 
        objDeviceConsole.Get_Image_Seq_Number("old_seq_number")

        Misc.ACTS_Dummy_Response("PASS","Get DUT Interface IP")
        objDeviceConsole.Get_Interface_IP(VAR("$lan_interface"))

        # Firmware downgrade from the this version to previous beta version via GUI.
        Misc.ACTS_Dummy_Response("PASS","Firmware downgrade from the this version to previous beta version via GUI")
        objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))
        objDeviceWeb.Setup_FW_Upgrade("D:/opal_auto/0_Pytest/Tools/firmware/ras-0.bin","no")
        Misc.Wait(200)
        # Console.CI_Wait_String(200,"1905 starting")
        WebApp.WebDrv_CloseWebSite()

        Misc.ACTS_Dummy_Response("PASS","Get new image sequence")
        objDeviceConsole.Console_Login(VAR("$console_username"), VAR("$console_password"), second_Lv_command= VAR("$second_shell_command"), second_Lv_password= VAR("$second_shell_password")) 
        objDeviceConsole.Get_Image_Seq_Number("new_seq_number")

        if VAR("new_seq_number") > VAR("old_seq_number"):
            Misc.ACTS_Dummy_Response("PASS","FW upgrade success")
        else:
            Misc.ACTS_Dummy_Response("FAIL","FW upgarde failed. Old image sequence number="+str(VAR("old_seq_number"))+","+"new image sequence number="+str(VAR("new_seq_number")))
        
        Misc.Wait(30)

        #####################################################################################################################

         # To check DUT config after config Restore 
        objDeviceConsole = Device_Console.Device_Console("DUT", VAR("$console_username"), VAR("$console_password"), second_Lv_command=VAR("$second_shell_command"), second_Lv_password=VAR("$second_shell_password"))
        
        Misc.ACTS_Dummy_Response("PASS","Get old image sequence")
        objDeviceConsole.Console_Login(VAR("$console_username"), VAR("$console_password"), second_Lv_command= VAR("$second_shell_command"), second_Lv_password= VAR("$second_shell_password")) 
        objDeviceConsole.Get_Image_Seq_Number("old_seq_number")

        Misc.ACTS_Dummy_Response("PASS","Get DUT Interface IP")
        objDeviceConsole.Get_Interface_IP(VAR("$lan_interface"))

        objDeviceWeb = Device_Web.Device_Web(VAR("$web_url"))
        objDeviceWeb.Web_Login(VAR("$supervisor_username"),VAR("$supervisor_password"))

        # Firmware upgrade from the previous beta version to this version via GUI.
        Misc.ACTS_Dummy_Response("PASS","Firmware upgrade from the previous beta version to this version via GUI.")
        objDeviceWeb.Setup_FW_Upgrade("D:/opal_auto/0_Pytest/Tools/firmware/ras.bin","no")
        Misc.Wait(200)
        # Console.CI_Wait_String(200,"1905 starting")
        WebApp.WebDrv_CloseWebSite()

        Misc.ACTS_Dummy_Response("PASS","Get new image sequence")
        objDeviceConsole.Console_Login(VAR("$console_username"), VAR("$console_password"), second_Lv_command= VAR("$second_shell_command"), second_Lv_password= VAR("$second_shell_password")) 
        objDeviceConsole.Get_Image_Seq_Number("new_seq_number")

        if VAR("new_seq_number") > VAR("old_seq_number"):
            Misc.ACTS_Dummy_Response("PASS","FW upgrade success")
        else:
            Misc.ACTS_Dummy_Response("FAIL","FW upgarde failed. Old image sequence number="+str(VAR("old_seq_number"))+","+"new image sequence number="+str(VAR("new_seq_number")))
        
        Misc.Wait(30)

    