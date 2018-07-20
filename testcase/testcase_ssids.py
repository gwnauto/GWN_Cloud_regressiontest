#coding=utf-8
#作者：曾祥卫
#时间：2018.04.10
#描述：Network-SSIDs-WIFI_Settings用例集，调用ssids_business

import unittest,time
from access_points.aps_business import APSBusiness
from system.settings.settings_business import SettingsBusiness
from ssids.ssids_business import SSIDSBusiness
from data import data
from connect.ssh import SSH
from data.logfile import Log
import requests
log = Log("ssids")

data_basic = data.data_basic()
data_login = data.data_login()
data_wireless = data.data_wireless()
data_ng = data.data_networkgroup()
data_ap = data.data_AP()
data_client = data.data_Client()

class TestSSIDs(unittest.TestCase):
    u"""测试Network-SSIDs的用例集(runtime:6.09h)"""
    def setUp(self):
        self.s = requests.session()
        tmp = SSIDSBusiness(self.s)
        #使用用户名密码，带着cookie登录cloud，并返回响应数据
        tmp.webLogin(data_basic['cloud_user'], data_basic['cloud_pwd'])

    #cloud添加三种型号的ap，并判断是否添加成功
    def test_001_add_3_model_aps_2_cloud(self):
        u"""cloud添加三种型号的ap，并判断是否添加成功(testlinkID:691-1)"""
        log.debug("001")
        tmp = APSBusiness(self.s)
        #描述：启用无线网卡
        tmp.wlan_enable(data_basic['wlan_pc'])
        tmp.dhcp_release_wlan(data_basic['wlan_pc'])
        #将ap复位，并将ap的hosts替换，指向本地cloud，然后将该ap添加到cloud中
        tmp.add_ap_2_local_cloud(data_basic['7610_ip'], data_ap['7610_mac'], "autotest_7610")
        tmp.add_ap_2_local_cloud(data_basic['7600_ip'], data_ap['7600_mac'], "autotest_7600")
        tmp.add_ap_2_local_cloud(data_basic['7600lr_ip'], data_ap['7600lr_mac'], "autotest_7600lr")
        #cloud上获取该网络组的ssh密码
        tmp1 = SettingsBusiness(self.s)
        ssh_pwd = tmp1.get_ssh_pwd()
        #判断ap是否已经和cloud配对上
        result1 = tmp.check_ap_pair_cloud(data_basic['7610_ip'],
                    data_basic['sshUser'], ssh_pwd)
        result2 = tmp.check_ap_pair_cloud(data_basic['7600_ip'],
                    data_basic['sshUser'], ssh_pwd)
        result3 = tmp.check_ap_pair_cloud(data_basic['7600lr_ip'],
                    data_basic['sshUser'], ssh_pwd)
        self.assertTrue(result1)
        self.assertTrue(result2)
        self.assertTrue(result3)
        print "add 3 model aps to cloud pass!"

    #验证SSID名称的输入长度限制-32
    def test_002_SSIDs_WIFISettings_ssid_name_32bit(self):
        u"""验证SSID名称的输入长度限制-32(testlinkID:1838)"""
        log.debug("002")
        #修改ssid为32位
        tmp = SSIDSBusiness(self.s)
        time.sleep(180)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid': data_wireless['long_ssid'],
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp.edit_ssid(data_ap['7610_mac'], 'GWN-Cloud',
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡连接ap
        result = tmp.connect_WPA_AP(data_wireless['long_ssid'],
                                    data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['long_ssid'], result)
        print "check ssid name is 32bits pass!"

    #验证SSID名称为数字的合法性
    def test_003_SSIDs_WIFISettings_ssid_name_digital(self):
        u"""验证SSID名称为数字的合法性(testlinkID:1839)"""
        log.debug("003")
        #修改ssid为全数字
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid': data_wireless['digital_ssid']}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['long_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡连接ap
        result = tmp.connect_WPA_AP(data_wireless['digital_ssid'],
                                    data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['digital_ssid'], result)
        print "check ssid name is all digital pass!"

    #验证SSID名称为纯英文的合法性
    def test_004_SSIDs_WIFISettings_ssid_name_letter(self):
        u"""验证SSID名称为纯英文的合法性(testlinkID:1840)"""
        log.debug("004")
        #修改ssid为全纯英文
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid': data_wireless['letter_ssid']}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['digital_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡连接ap
        result = tmp.connect_WPA_AP(data_wireless['letter_ssid'],
                                    data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['letter_ssid'], result)
        print "check ssid name is all letter pass!"

    #验证SSID名称为特殊符号的合法性
    def test_005_SSIDs_WIFISettings_ssid_name_ASCII(self):
        u"""验证SSID名称为特殊符号的合法性(testlinkID:1842)"""
        log.debug("005")
        #修改ssid为特殊符号
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid': data_wireless['ascii_ssid']}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['letter_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡连接ap
        result = tmp.connect_WPA_AP(data_wireless['ascii_ssid'],
                                    data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['ascii_ssid'], result)
        print "check ssid name is all ascii pass!"

    #验证SSID名称为混合型
    def test_006_SSIDs_WIFISettings_ssid_name_all(self):
        u"""验证SSID名称为混合型(testlinkID:1844)"""
        log.debug("006")
        #修改ssid为混合型
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid': data_wireless['all_ssid']}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['ascii_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡连接ap
        result = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                                    data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check ssid name is all mixed pass!"

    #验证关闭默认ssid的WiFi时，WiFi无法搜索得到
    def test_007_SSIDs_WIFISettings_disable_default_wifi(self):
        u"""验证关闭默认ssid的WiFi时，WiFi无法搜索得到(testlinkID:1846)"""
        log.debug("007")
        #关闭默认ssid的wifi
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_enable': "0"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡无法搜索ap
        result = tmp.ssid_scan_result(data_wireless['all_ssid'], data_basic["wlan_pc"])
        self.assertFalse(result)
        print "check disable default wifi pass!"

    #验证开启非默认ssid的WiFi时，WiFi能搜索得到
    def test_008_SSIDs_WIFISettings_enable_wifi(self):
        u"""验证开启非默认ssid的WiFi时，WiFi能搜索得到(testlinkID:1847)"""
        log.debug("008")
        #新建ssid
        tmp = SSIDSBusiness(self.s)
        tmp.add_ssid(data_ap['7610_mac'], data_wireless['all_ssid']+"-2",
                     data_wireless['short_wpa'])
        time.sleep(120)
        #无线网卡能够搜索到ap
        result = tmp.ssid_scan_result_backup(data_wireless['all_ssid']+"-2",
                    data_basic["wlan_pc"])
        self.assertTrue(result)
        print "check enable none default wifi pass!"

    #验证关闭非默认ssid的WiFi时，WiFi无法搜索得到
    def test_009_SSIDs_WIFISettings_disable_none_default_wifi(self):
        u"""验证关闭非默认ssid的WiFi时，WiFi无法搜索得到(testlinkID:1848)"""
        log.debug("009")
        #关闭非默认ssid的wifi
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_enable': "0"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid']+"-2",
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡无法搜索ap
        result = tmp.ssid_scan_result(data_wireless['all_ssid']+"-2", data_basic["wlan_pc"])
        self.assertFalse(result)
        print "check disable none default wifi pass!"

    #验证不同的ssid配置相同的vlan id值不会有错误提示
    def test_010_SSIDs_WIFISettings_same_vlanID(self):
        u"""验证不同的ssid配置相同的vlan id值不会有错误提示(testlinkID:1851)"""
        log.debug("010")
        #修改ssid2的vlanid为2，并开启ssid
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_enable': "1",
                    'ssid_vlan': "1",
                    'ssid_vlanid': "2"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid']+"-2",
                       encry_dict, data_dict)
        #新建一个新的ssid，vld也为2
        encry_dict1 = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict1 = {'ssid_enable': "1",
                    'ssid_vlan': "1",
                    'ssid_vlanid': "2"}
        tmp.add_ssid(data_ap['7610_mac'], data_wireless['all_ssid']+"-3",
                     data_wireless['short_wpa'])
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid']+"-3",
                       encry_dict1, data_dict1)
        time.sleep(120)
        #无线网卡能够搜索ap
        result1 = tmp.ssid_scan_result_backup(data_wireless['all_ssid']+"-2", data_basic["wlan_pc"])
        result2 = tmp.ssid_scan_result_backup(data_wireless['all_ssid']+"-3", data_basic["wlan_pc"])
        self.assertTrue(result1)
        self.assertTrue(result2)
        print "check setup the two same vid pass!"

    #验证加密方式为WEP-64bit模式
    def test_011_SSIDs_WIFISettings_wep64bit(self):
        u"""验证加密方式为WEP-64bit模式(testlinkID:1855)"""
        log.debug("011")
        tmp = SSIDSBusiness(self.s)
        #删除多余的ssid
        tmp.delete_ssid(data_wireless['all_ssid']+"-2")
        tmp.delete_ssid(data_wireless['all_ssid']+"-3")
        #修改ssid为wep64bit，并开启wifi
        encry_dict = {'ssid_encryption': "0",
                    'ssid_wep_key': data_wireless['wep64']}
        data_dict = {'ssid_enable': "1"
                     }
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_WEP_AP(data_wireless['all_ssid'],
                data_wireless['wep64'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check wep64bit pass!"

    #WEP-64bit终端连接SSID测试能否正常连接及上网
    def test_012_SSIDs_WIFISettings_wep64bit_access_internet(self):
        u"""WEP-64bit终端连接SSID测试能否正常连接及上网(testlinkID:1857)"""
        log.debug("012")
        tmp = SSIDSBusiness(self.s)
        #无线网卡获取ip
        tmp.dhcp_wlan(data_basic["wlan_pc"])
        #禁用有线
        tmp.wlan_disable(data_basic['lan_pc'])
        result = tmp.get_ping("180.76.76.76")
        #启用有线
        tmp.wlan_enable(data_basic['lan_pc'])
        #无线网卡释放ip
        tmp.dhcp_release_wlan(data_basic["wlan_pc"])
        self.assertEqual(0, result)
        print "wep64bit can access internet pass!"

    #验证加密方式为WEP-128bit模式
    def test_013_SSIDs_WIFISettings_wep128bit(self):
        u"""验证加密方式为WEP-128bit模式(testlinkID:1858)"""
        log.debug("013")
        tmp = SSIDSBusiness(self.s)
        #修改ssid为wep128bit，并开启wifi
        encry_dict = {'ssid_encryption': "1",
                    'ssid_wep_key': data_wireless['wep128']}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_WEP_AP(data_wireless['all_ssid'],
                data_wireless['wep128'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check wep128bit pass!"

    #WEP-128bit终端连接SSID测试能否正常连接及上网
    def test_014_SSIDs_WIFISettings_wep128bit_access_internet(self):
        u"""WEP-128bit终端连接SSID测试能否正常连接及上网(testlinkID:1860)"""
        log.debug("014")
        tmp = SSIDSBusiness(self.s)
        #无线网卡获取ip
        tmp.dhcp_wlan(data_basic["wlan_pc"])
        #禁用有线
        tmp.wlan_disable(data_basic['lan_pc'])
        result = tmp.get_ping("180.76.76.76")
        #启用有线
        tmp.wlan_enable(data_basic['lan_pc'])
        #无线网卡释放ip
        tmp.dhcp_release_wlan(data_basic["wlan_pc"])
        self.assertEqual(0, result)
        print "wep128bit can access internet pass!"

    #验证加密方式为WPA/WPA2-PSK AES模式
    def test_015_SSIDs_WIFISettings_wpa_aes(self):
        u"""验证加密方式为WPA/WPA2-PSK AES模式(testlinkID:1861)"""
        log.debug("015")
        tmp = SSIDSBusiness(self.s)
        #修改ssid为wpa-aes
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check wpa-aes pass!"

    #WPA/WPA2-PSK AES 密钥长度限制验证
    def test_016_SSIDs_WIFISettings_wpa_aes_long_pwd(self):
        u"""WPA/WPA2-PSK AES 密钥长度限制验证(testlinkID:1864)"""
        log.debug("016")
        tmp = SSIDSBusiness(self.s)
        #修改ssid为wpa-aes
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['long_wpa']}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['long_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check wpa-aes long pwd pass!"

    #WPA/WPA2-PSK AES终端连接SSID测试能否正常连接及上网
    def test_017_SSIDs_WIFISettings_wpa_aes_access_internet(self):
        u"""WPA/WPA2-PSK AES终端连接SSID测试能否正常连接及上网(testlinkID:1865)"""
        log.debug("017")
        tmp = SSIDSBusiness(self.s)
        #无线网卡获取ip
        tmp.dhcp_wlan(data_basic["wlan_pc"])
        #禁用有线
        tmp.wlan_disable(data_basic['lan_pc'])
        result = tmp.get_ping("180.76.76.76")
        #启用有线
        tmp.wlan_enable(data_basic['lan_pc'])
        #无线网卡释放ip
        tmp.dhcp_release_wlan(data_basic["wlan_pc"])
        self.assertEqual(0, result)
        print "wpa-aes can access internet pass!"

    #验证加密方式为WPA/WPA2 AES/TKIP模式
    def test_018_SSIDs_WIFISettings_wpa_tkip(self):
        u"""验证加密方式为WPA/WPA2 AES/TKIP模式(testlinkID:1866)"""
        log.debug("018")
        tmp = SSIDSBusiness(self.s)
        #修改ssid为wpa-tkip
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check wpa-tkip pass!"

    #WPA/WPA2-PSK AES/TKIP 密钥长度限制验证
    def test_019_SSIDs_WIFISettings_wpa_tkip_long_pwd(self):
        u"""WPA/WPA2-PSK AES/TKIP 密钥长度限制验证(testlinkID:1869)"""
        log.debug("019")
        tmp = SSIDSBusiness(self.s)
        #修改ssid为wpa-tkip
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['long_wpa']}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['long_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check wpa-tkip long pwd pass!"

    #WPA/WPA2-PSK AES/TKIP终端连接SSID测试能否正常连接及上网
    def test_020_SSIDs_WIFISettings_wpa_tkip_access_internet(self):
        u"""WPA/WPA2-PSK AES/TKIP终端连接SSID测试能否正常连接及上网(testlinkID:1870)"""
        log.debug("020")
        tmp = SSIDSBusiness(self.s)
        #无线网卡获取ip
        tmp.dhcp_wlan(data_basic["wlan_pc"])
        #禁用有线
        tmp.wlan_disable(data_basic['lan_pc'])
        result = tmp.get_ping("180.76.76.76")
        #启用有线
        tmp.wlan_enable(data_basic['lan_pc'])
        #无线网卡释放ip
        tmp.dhcp_release_wlan(data_basic["wlan_pc"])
        self.assertEqual(0, result)
        print "wpa-tkip can access internet pass!"

    #验证加密方式为WPA2 AES模式
    def test_021_SSIDs_WIFISettings_wpa2_aes(self):
        u"""验证加密方式为WPA2 AES模式(testlinkID:1871)"""
        log.debug("021")
        tmp = SSIDSBusiness(self.s)
        #修改ssid为wpa2-aes
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check wpa2-aes pass!"

    #WPA2-PSK AES 密钥长度限制验证
    def test_022_SSIDs_WIFISettings_wpa2_aes_long_pwd(self):
        u"""WPA2-PSK AES 密钥长度限制验证(testlinkID:1874)"""
        log.debug("022")
        tmp = SSIDSBusiness(self.s)
        #修改ssid为wpa2-aes
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['long_wpa']}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['long_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check wpa2-aes long pwd pass!"

    #WPA2-PSK AES终端连接SSID测试能否正常连接及上网
    def test_023_SSIDs_WIFISettings_wpa2_aes_access_internet(self):
        u"""WPA2-AES终端连接SSID测试能否正常连接及上网(testlinkID:1875)"""
        log.debug("023")
        tmp = SSIDSBusiness(self.s)
        #无线网卡获取ip
        tmp.dhcp_wlan(data_basic["wlan_pc"])
        #禁用有线
        tmp.wlan_disable(data_basic['lan_pc'])
        result = tmp.get_ping("180.76.76.76")
        #启用有线
        tmp.wlan_enable(data_basic['lan_pc'])
        #无线网卡释放ip
        tmp.dhcp_release_wlan(data_basic["wlan_pc"])
        self.assertEqual(0, result)
        print "wpa2-aes can access internet pass!"

    #验证加密方式为WPA2 AES/TKIP模式
    def test_024_SSIDs_WIFISettings_wpa2_tkip(self):
        u"""验证加密方式为WPA2 AES/TKIP模式(testlinkID:1876)"""
        log.debug("024")
        tmp = SSIDSBusiness(self.s)
        #修改ssid为wpa2-tkip
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check wpa2-tkip pass!"

    #WPA2 AES/TKIP密钥长度限制验证
    def test_025_SSIDs_WIFISettings_wpa2_tkip_long_pwd(self):
        u"""WPA2 AES/TKIP密钥长度限制验证(testlinkID:1879)"""
        log.debug("025")
        tmp = SSIDSBusiness(self.s)
        #修改ssid为wpa2-aes
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['long_wpa']}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['long_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check wpa2-tkip long pwd pass!"

    #WPA2-PSK AES/TKIP终端连接SSID测试能否正常连接及上网
    def test_026_SSIDs_WIFISettings_wpa2_tkip_access_internet(self):
        u"""WPA2-AES/TKIP终端连接SSID测试能否正常连接及上网(testlinkID:1880)"""
        log.debug("026")
        tmp = SSIDSBusiness(self.s)
        #无线网卡获取ip
        tmp.dhcp_wlan(data_basic["wlan_pc"])
        #禁用有线
        tmp.wlan_disable(data_basic['lan_pc'])
        result = tmp.get_ping("180.76.76.76")
        #启用有线
        tmp.wlan_enable(data_basic['lan_pc'])
        #无线网卡释放ip
        tmp.dhcp_release_wlan(data_basic["wlan_pc"])
        self.assertEqual(0, result)
        print "wpa2-tkip can access internet pass!"

    #安全模式设置为OPEN
    def test_027_SSIDs_WIFISettings_open(self):
        u"""安全模式设置为OPEN(testlinkID:1881-1)"""
        log.debug("027")
        tmp = SSIDSBusiness(self.s)
        #修改ssid为open
        encry_dict = {'ssid_encryption': "4"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_NONE_AP(data_wireless['all_ssid'],
                data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check open pass!"

    #Open终端连接SSID测试能否正常连接及上网
    def test_028_SSIDs_WIFISettings_open_access_internet(self):
        u"""Open终端连接SSID测试能否正常连接及上网(testlinkID:1881-2)"""
        log.debug("028")
        tmp = SSIDSBusiness(self.s)
        #无线网卡获取ip
        tmp.dhcp_wlan(data_basic["wlan_pc"])
        #禁用有线
        tmp.wlan_disable(data_basic['lan_pc'])
        result = tmp.get_ping("180.76.76.76")
        #启用有线
        tmp.wlan_enable(data_basic['lan_pc'])
        #无线网卡释放ip
        tmp.dhcp_release_wlan(data_basic["wlan_pc"])
        self.assertEqual(0, result)
        print "Open can access internet pass!"

    #WPA/WPA2-802.1x AES模式
    def test_029_SSIDs_WIFISettings_wpa_aes_8021x(self):
        u"""WPA/WPA2-802.1x AES模式(testlinkID:1903)"""
        log.debug("029")
        tmp = SSIDSBusiness(self.s)
        #修改ssid为WPA/WPA2-802.1x AES
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']
                      }
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_8021x_AP(data_wireless['all_ssid'],
                data_basic['radius_usename'], data_basic['radius_password'],
                data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check 802.1x wpa-aes pass!"

    #WPA/WPA2-802.1x AES/TKIP模式
    def test_030_SSIDs_WIFISettings_wpa_tkip_8021x(self):
        u"""WPA/WPA2-802.1x AES/TKIP模式(testlinkID:1904)"""
        log.debug("030")
        tmp = SSIDSBusiness(self.s)
        #修改ssid为WPA/WPA2-802.1x tkip
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']
                      }
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_8021x_AP(data_wireless['all_ssid'],
                data_basic['radius_usename'], data_basic['radius_password'],
                data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check 802.1x wpa-tkip pass!"

    #WPA2-802.1x AES模式
    def test_031_SSIDs_WIFISettings_wpa2_aes_8021x(self):
        u"""WPA2-802.1x AES/TKIP模式(testlinkID:1905)"""
        log.debug("031")
        tmp = SSIDSBusiness(self.s)
        #修改ssid为WPA2-802.1x aes
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']
                      }
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_8021x_AP(data_wireless['all_ssid'],
                data_basic['radius_usename'], data_basic['radius_password'],
                data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check 802.1x wpa2-aes pass!"

    #WPA2-802.1x AES/TKIP模式
    def test_032_SSIDs_WIFISettings_wpa2_tkip_8021x(self):
        u"""WPA2-802.1x AES/TKIP模式(testlinkID:1906)"""
        log.debug("032")
        tmp = SSIDSBusiness(self.s)
        #修改ssid为WPA2-802.1x tkip
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']
                      }
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_8021x_AP(data_wireless['all_ssid'],
                data_basic['radius_usename'], data_basic['radius_password'],
                data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check 802.1x wpa2-tkip pass!"

    #测试radius 服务器地址是IP的时候，终端连接认证上网
    def test_033_SSIDs_WIFISettings_raduis_IP_access_internet(self):
        u"""测试radius 服务器地址是IP的时候，终端连接认证上网(testlinkID:1907)"""
        log.debug("033")
        tmp = SSIDSBusiness(self.s)
        #无线网卡获取ip
        tmp.dhcp_wlan(data_basic["wlan_pc"])
        #禁用有线
        tmp.wlan_disable(data_basic['lan_pc'])
        result = tmp.get_ping("180.76.76.76")
        #启用有线
        tmp.wlan_enable(data_basic['lan_pc'])
        #无线网卡释放ip
        tmp.dhcp_release_wlan(data_basic["wlan_pc"])
        self.assertEqual(0, result)
        print "raduis server is IP can access internet pass!"

    #验证频段选择为Dual-Band默认情况时，网络连接正常
    def test_034_SSIDs_WIFISettings_dual_band(self):
        u"""验证频段选择为Dual-Band默认情况时，网络连接正常(testlinkID:1909)"""
        log.debug("034")
        tmp = SSIDSBusiness(self.s)
        #加密改为wpa2-aes
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check dual-band pass!"

    #验证频段选择为2.4G时，网络连接正常
    def test_035_SSIDs_WIFISettings_2g4(self):
        u"""验证频段选择为2.4G时，网络连接正常(testlinkID:1910)"""
        log.debug("035")
        tmp = SSIDSBusiness(self.s)
        #修改为2.4G
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_band': "2"}
        tmp.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check 2.4G pass!"

    #验证wep-64bit + 2.4G，网络连接正常
    def test_036_SSIDs_WIFISettings_2g4_wep64bit(self):
        u"""验证wep-64bit + 2.4G，网络连接正常(testlinkID:1911)"""
        log.debug("036")
        tmp = SSIDSBusiness(self.s)
        #修改ssid为wep64bit
        encry_dict = {'ssid_encryption': "0",
                    'ssid_wep_key': data_wireless['wep64']}
        tmp.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_WEP_AP(data_wireless['all_ssid'],
                data_wireless['wep64'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check wep64bit + 2.4G pass!"

    #验证wep-128bit + 2.4G，网络连接正常
    def test_037_SSIDs_WIFISettings_2g4_wep128bit(self):
        u"""验证wep-128bit + 2.4G，网络连接正常(testlinkID:1912)"""
        log.debug("037")
        tmp = SSIDSBusiness(self.s)
        #修改ssid为wep128bit
        encry_dict = {'ssid_encryption': "1",
                    'ssid_wep_key': data_wireless['wep128']}
        tmp.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_WEP_AP(data_wireless['all_ssid'],
                data_wireless['wep128'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check wep128bit + 2.4G pass!"

    #验证WPA\WAP2 + 2.4G，网络连接正常
    def test_038_SSIDs_WIFISettings_2g4_wpa(self):
        u"""验证WPA\WAP2 + 2.4G，网络连接正常(testlinkID:1913)"""
        log.debug("038")
        tmp = SSIDSBusiness(self.s)
        #修改ssid为wpa
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        tmp.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check wpa + 2.4G pass!"

    #验证WAP2 + 2.4G，网络连接正常
    def test_039_SSIDs_WIFISettings_2g4_wpa2(self):
        u"""验证WAP2 + 2.4G，网络连接正常(testlinkID:1914)"""
        log.debug("039")
        tmp = SSIDSBusiness(self.s)
        #修改ssid为wpa2
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        tmp.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check wpa2 + 2.4G pass!"

    #验证OPEN + 2.4G，网络连接正常
    def test_040_SSIDs_WIFISettings_2g4_open(self):
        u"""验证OPEN + 2.4G，网络连接正常(testlinkID:1915)"""
        log.debug("040")
        tmp = SSIDSBusiness(self.s)
        #修改ssid为open
        encry_dict = {'ssid_encryption': "4"}
        tmp.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_NONE_AP(data_wireless['all_ssid'],
                data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check OPEN + 2.4G pass!"

    #验证频段选择为5G时，网络连接正常
    def test_041_SSIDs_WIFISettings_5g(self):
        u"""验证频段选择为5G时，网络连接正常(testlinkID:1916)"""
        log.debug("041")
        tmp = SSIDSBusiness(self.s)
        #修改为5G
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_band': "5"}
        tmp.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check 5G pass!"

    #验证wep-64bit + 5G，网络连接正常
    def test_042_SSIDs_WIFISettings_5g_wep64bit(self):
        u"""验证wep-64bit + 5G，网络连接正常(testlinkID:1917)"""
        log.debug("042")
        tmp = SSIDSBusiness(self.s)
        #修改ssid为wep64bit
        encry_dict = {'ssid_encryption': "0",
                    'ssid_wep_key': data_wireless['wep64']}
        tmp.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_WEP_AP(data_wireless['all_ssid'],
                data_wireless['wep64'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check wep64bit + 5G pass!"

    #验证wep-128bit + 5G，网络连接正常
    def test_043_SSIDs_WIFISettings_5g_wep128bit(self):
        u"""验证wep-128bit + 5G，网络连接正常(testlinkID:1918)"""
        log.debug("043")
        tmp = SSIDSBusiness(self.s)
        #修改ssid为wep128bit
        encry_dict = {'ssid_encryption': "1",
                    'ssid_wep_key': data_wireless['wep128']}
        tmp.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_WEP_AP(data_wireless['all_ssid'],
                data_wireless['wep128'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check wep128bit + 5G pass!"

    #验证WPA\WAP2 + 5G，网络连接正常
    def test_044_SSIDs_WIFISettings_5g_wpa(self):
        u"""验证WPA\WAP2 + 5G，网络连接正常(testlinkID:1919)"""
        log.debug("044")
        tmp = SSIDSBusiness(self.s)
        #修改ssid为wpa
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        tmp.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check wpa + 5G pass!"

    #验证WAP2 + 5G，网络连接正常
    def test_045_SSIDs_WIFISettings_5g_wpa2(self):
        u"""验证WAP2 + 5G，网络连接正常(testlinkID:1920)"""
        log.debug("045")
        tmp = SSIDSBusiness(self.s)
        #修改ssid为wpa2
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        tmp.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check wpa2 + 5G pass!"

    #验证OPEN + 5G，网络连接正常
    def test_046_SSIDs_WIFISettings_5g_open(self):
        u"""验证OPEN + 5G，网络连接正常(testlinkID:1921)"""
        log.debug("046")
        tmp = SSIDSBusiness(self.s)
        #修改ssid为open
        encry_dict = {'ssid_encryption': "4"}
        tmp.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_NONE_AP(data_wireless['all_ssid'],
                data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)
        print "check OPEN + 5G pass!"

    #验证开启隐藏SSID后，用电脑或者手机进行扫描不能发现该SSID
    def test_047_SSIDs_WIFISettings_hidden_ssid(self):
        u"""验证开启隐藏SSID后，用电脑或者手机进行扫描不能发现该SSID(testlinkID:1922)"""
        log.debug("047")
        tmp = SSIDSBusiness(self.s)
        #修改为dual_band,wpa2-aes,hidden-ssid
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_band': "",
                     'ssid_ssid_hidden': "1",
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡无法扫描到ap
        result = tmp.ssid_scan_result(data_wireless['all_ssid'],
                data_basic["wlan_pc"])
        self.assertFalse(result)
        print "check hidden ssid pass!"

    #验证关闭隐藏SSID后，能用电脑或者手机扫描出该SSID
    def test_048_SSIDs_WIFISettings_disable_hidden_ssid(self):
        u"""验证关闭隐藏SSID后，能用电脑或者手机扫描出该SSID(testlinkID:1923)"""
        log.debug("048")
        tmp = SSIDSBusiness(self.s)
        #修改为dual_band,wpa2-aes,hidden-ssid
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_hidden': "0"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡能够扫描到ap
        result = tmp.ssid_scan_result_backup(data_wireless['all_ssid'],
                data_basic["wlan_pc"])
        self.assertTrue(result)
        print "check disable hidden ssid pass!"

    #验证填写客户端限制范围值
    def test_049_SSIDs_WIFISettings_client_limit(self):
        u"""验证填写客户端限制范围值(testlinkID:1924)"""
        log.debug("049")
        tmp = SSIDSBusiness(self.s)
        #填写客户端限制范围值-50
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_wifi_client_limit': "50"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath0.maxsta")
        result2 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath1.maxsta")
        self.assertIn('50', result1)
        self.assertIn('50', result2)
        print "check client limit pass!"

    #验证频段采用Dual-Band时，实际上客户端限制的数值应该为填写的两倍
    def test_050_SSIDs_WIFISettings_client_limit_dual_band(self):
        u"""验证频段采用Dual-Band时，实际上客户端限制的数值应该为填写的两倍(testlinkID:1927)"""
        log.debug("050")
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath0.maxsta")
        result2 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath1.maxsta")
        self.assertIn('50', result1)
        self.assertIn('50', result2)
        print "check dual-band client limit pass!"

    #验证频段采用2.4G时，客户端限制数与填写的数值一致
    def test_051_SSIDs_WIFISettings_client_limit_2g4(self):
        u"""验证频段采用2.4G时，客户端限制数与填写的数值一致(testlinkID:1928)"""
        log.debug("051")
        #ssid修改为2.4G
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_band': "2",
                     'ssid_wifi_client_limit': "50"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath0.maxsta")
        result2 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath1.maxsta")
        self.assertIn('50', result1)
        self.assertNotIn('50', result2)
        print "check 2.4G client limit pass!"

    #验证频段采用5G时，客户端限制数与填写的数值一致
    def test_052_SSIDs_WIFISettings_client_limit_5g(self):
        u"""验证频段采用5G时，客户端限制数与填写的数值一致(testlinkID:1929)"""
        log.debug("052")
        #ssid修改为5G
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_band': "5",
                     'ssid_wifi_client_limit': "50"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath0.maxsta")
        result2 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath1.maxsta")
        self.assertIn('50', result1)
        self.assertNotIn('50', result2)
        print "check 5G client limit pass!"

    #验证采用wep-64bit加密方式，客户端限制功能生效
    def test_053_SSIDs_WIFISettings_client_limit_wep64bit(self):
        u"""验证采用wep-64bit加密方式，客户端限制功能生效(testlinkID:1930)"""
        log.debug("053")
        tmp = SSIDSBusiness(self.s)
        #修改为dual-band,wep64,
        encry_dict = {'ssid_encryption': "0",
                    'ssid_wep_key': data_wireless['wep64']}
        data_dict = {'ssid_ssid_band': "",
                     'ssid_wifi_client_limit': "50"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
         #无线网卡连接
        result1 = tmp.connect_WEP_AP(data_wireless['all_ssid'],
                data_wireless['wep64'], data_basic["wlan_pc"])
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result2 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath0.maxsta")
        result3 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath1.maxsta")
        self.assertIn(data_wireless['all_ssid'], result1)
        self.assertIn('50', result2)
        self.assertIn('50', result3)
        print "check wep64bit + client limit pass!"

    #验证采用wep-128bit加密方式，客户端限制功能生效
    def test_054_SSIDs_WIFISettings_client_limit_wep128bit(self):
        u"""验证采用wep-128bit加密方式，客户端限制功能生效(testlinkID:1931)"""
        log.debug("054")
        tmp = SSIDSBusiness(self.s)
        #修改为wep128,
        encry_dict = {'ssid_encryption': "1",
                    'ssid_wep_key': data_wireless['wep128']}
        data_dict = {'ssid_wifi_client_limit': "50"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
         #无线网卡连接
        result1 = tmp.connect_WEP_AP(data_wireless['all_ssid'],
                data_wireless['wep128'], data_basic["wlan_pc"])
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result2 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath0.maxsta")
        result3 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath1.maxsta")
        self.assertIn(data_wireless['all_ssid'], result1)
        self.assertIn('50', result2)
        self.assertIn('50', result3)
        print "check wep128bit + client limit pass!"

    #验证采用wpa\wpa2 AES加密方式，客户端限制功能生效
    def test_055_SSIDs_WIFISettings_client_limit_wpa_aes(self):
        u"""验证采用wpa\wpa2 AES加密方式，客户端限制功能生效(testlinkID:1932)"""
        log.debug("055")
        tmp = SSIDSBusiness(self.s)
        #修改为wpa-aes
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_wifi_client_limit': "50"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
         #无线网卡连接
        result1 = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result2 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath0.maxsta")
        result3 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath1.maxsta")
        self.assertIn(data_wireless['all_ssid'], result1)
        self.assertIn('50', result2)
        self.assertIn('50', result3)
        print "check wpa-aes + client limit pass!"

    #验证采用wpa\wpa2 TKIP加密方式，客户端限制功能生效
    def test_056_SSIDs_WIFISettings_client_limit_wpa_tkip(self):
        u"""验证采用wpa\wpa2 TKIP加密方式，客户端限制功能生效(testlinkID:1933)"""
        log.debug("056")
        tmp = SSIDSBusiness(self.s)
        #修改为wpa-tkip
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_wifi_client_limit': "50"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
         #无线网卡连接
        result1 = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result2 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath0.maxsta")
        result3 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath1.maxsta")
        self.assertIn(data_wireless['all_ssid'], result1)
        self.assertIn('50', result2)
        self.assertIn('50', result3)
        print "check wpa-tkip + client limit pass!"

    #验证采用WPA2 AES加密方式，客户端限制功能生效
    def test_057_SSIDs_WIFISettings_client_limit_wpa2_aes(self):
        u"""验证采用WPA2 AES加密方式，客户端限制功能生效(testlinkID:1934)"""
        log.debug("057")
        tmp = SSIDSBusiness(self.s)
        #修改为wpa2-aes
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_wifi_client_limit': "50"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
         #无线网卡连接
        result1 = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result2 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath0.maxsta")
        result3 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath1.maxsta")
        self.assertIn(data_wireless['all_ssid'], result1)
        self.assertIn('50', result2)
        self.assertIn('50', result3)
        print "check wpa2-aes + client limit pass!"

    #验证采用WPA2 TKIP加密方式，客户端限制功能生效
    def test_058_SSIDs_WIFISettings_client_limit_wpa2_tkip(self):
        u"""验证采用WPA2 TKIP加密方式，客户端限制功能生效(testlinkID:1935)"""
        log.debug("058")
        tmp = SSIDSBusiness(self.s)
        #修改为wpa2-tkip
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "1",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_wifi_client_limit': "50"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
         #无线网卡连接
        result1 = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result2 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath0.maxsta")
        result3 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath1.maxsta")
        self.assertIn(data_wireless['all_ssid'], result1)
        self.assertIn('50', result2)
        self.assertIn('50', result3)
        print "check wpa2-tkip + client limit pass!"

    #验证加密方式为Open，客户端限制功能生效
    def test_059_SSIDs_WIFISettings_client_limit_open(self):
        u"""验证加密方式为Open，客户端限制功能生效(testlinkID:1936)"""
        log.debug("059")
        tmp = SSIDSBusiness(self.s)
        #修改为open
        encry_dict = {'ssid_encryption': "4"}
        data_dict = {'ssid_wifi_client_limit': "50"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡连接
        result1 = tmp.connect_NONE_AP(data_wireless['all_ssid'],
                data_basic["wlan_pc"])
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result2 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath0.maxsta")
        result3 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath1.maxsta")
        self.assertIn(data_wireless['all_ssid'], result1)
        self.assertIn('50', result2)
        self.assertIn('50', result3)
        print "check open + client limit pass!"

    #验证重启后，Wireless Client Limit功能没有失效
    def test_060_SSIDs_WIFISettings_client_limit_open(self):
        u"""验证重启后，Wireless Client Limit功能没有失效(testlinkID:1945)"""
        log.debug("060")
        #重启7610
        tmp1 = APSBusiness(self.s)
        tmp1.reboot_one_ap(data_ap['7610_mac'])
        time.sleep(360)
        #无线网卡连接
        result1 = tmp1.connect_NONE_AP(data_wireless['all_ssid'],
                data_basic["wlan_pc"])
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result2 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath0.maxsta")
        result3 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath1.maxsta")
        self.assertIn(data_wireless['all_ssid'], result1)
        self.assertIn('50', result2)
        self.assertIn('50', result3)
        print "check reboot ap client limit pass!"

    #验证开启client isolation功能，选择无线模式，功能生效
    def test_061_SSIDs_WIFISettings_client_isolation_radio(self):
        u"""验证开启client isolation功能，选择无线模式，功能生效(testlinkID:1946)"""
        log.debug("061")
        #修改为wpa2-aes,并去掉client limit.开启client isolation-radio
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "radio",
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600_mac'].upper())}
        tmp.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7600lr_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result2 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        self.assertIn("1", result1)
        self.assertIn("radio", result2)
        print "check isolation radio, test pass!"

    #无线终端访问网络
    def test_062_SSIDs_WIFISettings_client_isolation_radio_access_internet(self):
        u"""无线终端访问网络(testlinkID:1953)"""
        log.debug("062")
        tmp = SSIDSBusiness(self.s)
        #无线网卡连接
        tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        #检查客户端隔离的结果
        result1, result2 = tmp.check_isolation()
        self.assertEqual(0, result2)
        print "check isolation radio can access internet, test pass!"

    #无线终端访问AP或者网关的管理界面
    def test_063_SSIDs_WIFISettings_client_isolation_radio_access_gateway(self):
        u"""无线终端访问AP或者网关的管理界面(testlinkID:1954)"""
        log.debug("063")
        tmp = SSIDSBusiness(self.s)
        #无线网卡连接
        tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        #检查客户端隔离的结果
        result1, result2 = tmp.check_isolation()
        self.assertEqual(0, result1)
        print "check isolation radio can access internet, test pass!"

    #验证开启client isolation功能，选择因特网模式，功能生效
    def test_064_SSIDs_WIFISettings_client_isolation_internet(self):
        u"""验证开启client isolation功能，选择因特网模式，功能生效(testlinkID:1957)"""
        log.debug("064")
        #开启client isolation-gateway
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "internet"}
        tmp.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7600lr_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result2 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        self.assertIn("1", result1)
        self.assertIn("internet", result2)
        print "check isolation internet, test pass!"

    #无线终端Ping外网地址，可以Ping通
    def test_065_SSIDs_WIFISettings_client_isolation_internet_access_internet(self):
        u"""无线终端Ping外网地址，可以Ping通(testlinkID:1964)"""
        log.debug("065")
        tmp = SSIDSBusiness(self.s)
        #无线网卡连接
        tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        #检查客户端隔离的结果
        result1, result2 = tmp.check_isolation()
        self.assertEqual(0, result2)
        print "check isolation internet can access internet, test pass!"

    #无线终端Ping内网任一地址，不可以Ping通
    def test_066_SSIDs_WIFISettings_client_isolation_internet_not_access_gateway(self):
        u"""无线终端Ping内网任一地址，不可以Ping通(testlinkID:1965)--#bug110469"""
        log.debug("066")
        tmp = SSIDSBusiness(self.s)
        #无线网卡连接
        tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        #检查客户端隔离的结果
        result1, result2 = tmp.check_isolation()
        self.assertNotEqual(0, result1)
        print "check isolation internet can't access internet, test pass!"

    #验证开启client isolation功能，选择网关MAC模式，功能生效
    def test_067_SSIDs_WIFISettings_client_isolation_gateway(self):
        u"""验证开启client isolation功能，选择网关MAC模式，功能生效(testlinkID:1968)"""
        log.debug("067")
        #开启client isolation-mac
        tmp = SSIDSBusiness(self.s)
        #获取7000的mac地址
        route_mac = tmp.get_router_mac(data_basic['7000_ip'],data_basic['sshUser'],data_basic['7000_pwd'])
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "gateway_mac",
                     'ssid_gateway_mac': route_mac}
        tmp.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7600lr_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result2 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result3 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.gateway_mac")
        self.assertIn("1", result1)
        self.assertIn("gateway_mac", result2)
        self.assertIn(route_mac, result3)
        print "check isolation gateway-mac, test pass!"

    #无线终端Ping外网地址，可以Ping通
    def test_068_SSIDs_WIFISettings_client_isolation_gatewaymac_access_internet(self):
        u"""无线终端Ping外网地址，可以Ping通(testlinkID:1969-1)"""
        log.debug("068")
        tmp = SSIDSBusiness(self.s)
        #无线网卡连接
        tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        #检查客户端隔离的结果
        result1, result2 = tmp.check_isolation()
        self.assertEqual(0, result2)
        print "check isolation gateway mac can access internet, test pass!"

    #无线终端Ping内网任一地址，不可以Ping通
    def test_069_SSIDs_WIFISettings_client_isolation_gatewaymac_access_gateway(self):
        u"""无线终端Ping内网任一地址，不可以Ping通(testlinkID:1969-2)"""
        log.debug("069")
        tmp = SSIDSBusiness(self.s)
        #无线网卡连接
        tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        #检查客户端隔离的结果
        result1, result2 = tmp.check_isolation()
        self.assertEqual(0, result1)
        print "check isolation gateway mac can access internet, test pass!"

    #验证Clients isolation-gateway + wep-64bit加密模式，隔离功能生效
    def test_070_SSIDs_WIFISettings_client_isolation_gateway_wep64(self):
        u"""验证Clients isolation-gateway + wep-64bit加密模式，隔离功能生效(testlinkID:1977-1)"""
        log.debug("070")
        tmp = SSIDSBusiness(self.s)
        #获取7000的mac地址
        route_mac = tmp.get_router_mac(data_basic['7000_ip'],data_basic['sshUser'],data_basic['7000_pwd'])
        #修改ssid为wep64bit
        encry_dict = {'ssid_encryption': "0",
                    'ssid_wep_key': data_wireless['wep64']}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "gateway_mac",
                     'ssid_gateway_mac': route_mac}
        tmp.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7600lr_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result2 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result3 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.gateway_mac")
        result4 = tmp.connect_WEP_AP(data_wireless['all_ssid'], data_wireless['wep64'],
                                     data_basic["wlan_pc"])
        self.assertIn("1", result1)
        self.assertIn("gateway_mac", result2)
        self.assertIn(route_mac, result3)
        self.assertIn(data_wireless['all_ssid'], result4)
        print "check wep64bit isolation gateway-mac, test pass!"

    #验证Clients isolation-internet + wep-64bit加密模式，隔离功能生效
    def test_071_SSIDs_WIFISettings_client_isolation_internet_wep64(self):
        u"""验证Clients isolation-internet + wep-64bit加密模式，隔离功能生效(testlinkID:1977-2)"""
        log.debug("071")
        #开启client isolation-internet
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "0",
                    'ssid_wep_key': data_wireless['wep64']}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "internet"}
        tmp.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7600lr_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result2 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result4 = tmp.connect_WEP_AP(data_wireless['all_ssid'], data_wireless['wep64'],
                                     data_basic["wlan_pc"])
        self.assertIn("1", result1)
        self.assertIn("internet", result2)
        self.assertIn(data_wireless['all_ssid'], result4)
        print "check wep64bit isolation internet, test pass!"

    #验证Clients isolation-raido + wep-64bit加密模式，隔离功能生效
    def test_072_SSIDs_WIFISettings_client_isolation_raido_wep64(self):
        u"""验证Clients isolation-raido + wep-64bit加密模式，隔离功能生效(testlinkID:1977-3)"""
        log.debug("072")
        #开启client isolation-radio
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "0",
                    'ssid_wep_key': data_wireless['wep64']}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "radio"}
        tmp.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7600lr_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result2 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result4 = tmp.connect_WEP_AP(data_wireless['all_ssid'], data_wireless['wep64'],
                                     data_basic["wlan_pc"])
        self.assertIn("1", result1)
        self.assertIn("radio", result2)
        self.assertIn(data_wireless['all_ssid'], result4)
        print "check wep64bit isolation radio, test pass!"

    #验证Clients isolation-raido + wep-128bit加密模式，隔离功能生效
    def test_073_SSIDs_WIFISettings_client_isolation_raido_wep128(self):
        u"""验证Clients isolation-raido + wep-128bit加密模式，隔离功能生效(testlinkID:1978-1)"""
        log.debug("073")
        #修改为wep128
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "1",
                    'ssid_wep_key': data_wireless['wep128']}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "radio"}
        tmp.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7600lr_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result2 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result4 = tmp.connect_WEP_AP(data_wireless['all_ssid'], data_wireless['wep128'],
                                     data_basic["wlan_pc"])
        self.assertIn("1", result1)
        self.assertIn("radio", result2)
        self.assertIn(data_wireless['all_ssid'], result4)
        print "check wep128bit isolation radio, test pass!"

    #验证Clients isolation-internet + wep-128bit加密模式，隔离功能生效
    def test_074_SSIDs_WIFISettings_client_isolation_internet_wep128(self):
        u"""验证Clients isolation-internet + wep-128bit加密模式，隔离功能生效(testlinkID:1978-2)"""
        log.debug("074")
        #开启client isolation-internet
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "1",
                    'ssid_wep_key': data_wireless['wep128']}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "internet"}
        tmp.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7600lr_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result2 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result4 = tmp.connect_WEP_AP(data_wireless['all_ssid'], data_wireless['wep128'],
                                     data_basic["wlan_pc"])
        self.assertIn("1", result1)
        self.assertIn("internet", result2)
        self.assertIn(data_wireless['all_ssid'], result4)
        print "check wep128bit isolation internet, test pass!"

    #验证Clients isolation-gateway + wep-128bit加密模式，隔离功能生效
    def test_075_SSIDs_WIFISettings_client_isolation_gateway_wep128(self):
        u"""验证Clients isolation-gateway + wep-128bit加密模式，隔离功能生效(testlinkID:1978-3)"""
        log.debug("075")
        tmp = SSIDSBusiness(self.s)
        #获取7000的mac地址
        route_mac = tmp.get_router_mac(data_basic['7000_ip'],data_basic['sshUser'],data_basic['7000_pwd'])
        #开启client isolation-gateway
        encry_dict = {'ssid_encryption': "1",
                    'ssid_wep_key': data_wireless['wep128']}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "gateway_mac",
                     'ssid_gateway_mac': route_mac}
        tmp.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7600lr_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result2 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result3 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.gateway_mac")
        result4 = tmp.connect_WEP_AP(data_wireless['all_ssid'], data_wireless['wep128'],
                                     data_basic["wlan_pc"])
        self.assertIn("1", result1)
        self.assertIn("gateway_mac", result2)
        self.assertIn(route_mac, result3)
        self.assertIn(data_wireless['all_ssid'], result4)
        print "check wep128bit isolation gateway-mac, test pass!"

    #验证Clients isolation-raido + WPA\WPA2加密模式，隔离功能生效
    def test_076_SSIDs_WIFISettings_client_isolation_raido_wpa(self):
        u"""验证Clients isolation-raido + WPA\WPA2加密模式，隔离功能生效(testlinkID:1979-1)"""
        log.debug("076")
        #修改为wpa
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "radio"}
        tmp.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7600lr_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result2 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result4 = tmp.connect_WPA_AP(data_wireless['all_ssid'], data_wireless['short_wpa'],
                                     data_basic["wlan_pc"])
        self.assertIn("1", result1)
        self.assertIn("radio", result2)
        self.assertIn(data_wireless['all_ssid'], result4)
        print "check wpa isolation radio, test pass!"

    #验证Clients isolation-internet + WPA\WPA2加密模式，隔离功能生效
    def test_077_SSIDs_WIFISettings_client_isolation_internet_wpa(self):
        u"""验证Clients isolation-internet + WPA\WPA2加密模式，隔离功能生效(testlinkID:1979-2)"""
        log.debug("077")
        #开启client isolation-internet
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "internet"}
        tmp.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7600lr_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result2 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result4 = tmp.connect_WPA_AP(data_wireless['all_ssid'], data_wireless['short_wpa'],
                                     data_basic["wlan_pc"])
        self.assertIn("1", result1)
        self.assertIn("internet", result2)
        self.assertIn(data_wireless['all_ssid'], result4)
        print "check wpa isolation internet, test pass!"

    #验证Clients isolation-gateway + WPA\WPA2加密模式，隔离功能生效
    def test_078_SSIDs_WIFISettings_client_isolation_gateway_wpa(self):
        u"""验证Clients isolation-gateway + WPA\WPA2加密模式，隔离功能生效(testlinkID:1979-3)"""
        log.debug("078")
        tmp = SSIDSBusiness(self.s)
        #获取7000的mac地址
        route_mac = tmp.get_router_mac(data_basic['7000_ip'],data_basic['sshUser'],data_basic['7000_pwd'])
        #开启client isolation-gateway
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "gateway_mac",
                     'ssid_gateway_mac': route_mac}
        tmp.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7600lr_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result2 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result3 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.gateway_mac")
        result4 = tmp.connect_WPA_AP(data_wireless['all_ssid'], data_wireless['short_wpa'],
                                     data_basic["wlan_pc"])
        self.assertIn("1", result1)
        self.assertIn("gateway_mac", result2)
        self.assertIn(route_mac, result3)
        self.assertIn(data_wireless['all_ssid'], result4)
        print "check wpa isolation gateway-mac, test pass!"

    #验证Clients isolation-raido + WPA2加密模式，隔离功能生效
    def test_079_SSIDs_WIFISettings_client_isolation_raido_wpa2(self):
        u"""验证Clients isolation-raido + WPA2加密模式，隔离功能生效(testlinkID:1980-1)"""
        log.debug("079")
        #修改为wpa2
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "radio"}
        tmp.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7600lr_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result2 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result4 = tmp.connect_WPA_AP(data_wireless['all_ssid'], data_wireless['short_wpa'],
                                     data_basic["wlan_pc"])
        self.assertIn("1", result1)
        self.assertIn("radio", result2)
        self.assertIn(data_wireless['all_ssid'], result4)
        print "check wpa2 isolation radio, test pass!"

    #验证Clients isolation-internet + WPA2加密模式，隔离功能生效
    def test_080_SSIDs_WIFISettings_client_isolation_internet_wpa2(self):
        u"""验证Clients isolation-internet + WPA2加密模式，隔离功能生效(testlinkID:1980-2)"""
        log.debug("080")
        #开启client isolation-internet
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "internet"}
        tmp.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7600lr_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result2 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result4 = tmp.connect_WPA_AP(data_wireless['all_ssid'], data_wireless['short_wpa'],
                                     data_basic["wlan_pc"])
        self.assertIn("1", result1)
        self.assertIn("internet", result2)
        self.assertIn(data_wireless['all_ssid'], result4)
        print "check wpa2 isolation internet, test pass!"

    #验证Clients isolation-gateway + WPA2加密模式，隔离功能生效
    def test_081_SSIDs_WIFISettings_client_isolation_gateway_wpa2(self):
        u"""验证Clients isolation-gateway + WPA2加密模式，隔离功能生效(testlinkID:1980-3)"""
        log.debug("081")
        tmp = SSIDSBusiness(self.s)
        #获取7000的mac地址
        route_mac = tmp.get_router_mac(data_basic['7000_ip'],data_basic['sshUser'],data_basic['7000_pwd'])
        #开启client isolation-gateway
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "gateway_mac",
                     'ssid_gateway_mac': route_mac}
        tmp.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7600lr_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result2 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result3 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.gateway_mac")
        result4 = tmp.connect_WPA_AP(data_wireless['all_ssid'], data_wireless['short_wpa'],
                                     data_basic["wlan_pc"])
        self.assertIn("1", result1)
        self.assertIn("gateway_mac", result2)
        self.assertIn(route_mac, result3)
        self.assertIn(data_wireless['all_ssid'], result4)
        print "check wpa2 isolation gateway-mac, test pass!"

    #验证Clients isolation-raido + Open加密模式，隔离功能生效
    def test_082_SSIDs_WIFISettings_client_isolation_raido_open(self):
        u"""验证Clients isolation-raido + Open加密模式，隔离功能生效(testlinkID:1981-1)"""
        log.debug("082")
        #修改为open
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "4"}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "radio"}
        tmp.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7600lr_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result2 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result4 = tmp.connect_NONE_AP(data_wireless['all_ssid'], data_basic["wlan_pc"])
        self.assertIn("1", result1)
        self.assertIn("radio", result2)
        self.assertIn(data_wireless['all_ssid'], result4)
        print "check open isolation radio, test pass!"

    #验证Clients isolation-internet + Open加密模式，隔离功能生效
    def test_083_SSIDs_WIFISettings_client_isolation_internet_open(self):
        u"""验证Clients isolation-internet + Open加密模式，隔离功能生效(testlinkID:1981-2)"""
        log.debug("083")
        #开启client isolation-internet
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "4"}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "internet"}
        tmp.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7600lr_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result2 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result4 = tmp.connect_NONE_AP(data_wireless['all_ssid'], data_basic["wlan_pc"])
        self.assertIn("1", result1)
        self.assertIn("internet", result2)
        self.assertIn(data_wireless['all_ssid'], result4)
        print "check open isolation internet, test pass!"

    #验证Clients isolation-gateway + Open加密模式，隔离功能生效
    def test_084_SSIDs_WIFISettings_client_isolation_gateway_wpa2(self):
        u"""验证Clients isolation-gateway + Open加密模式，隔离功能生效(testlinkID:1981-3)"""
        log.debug("084")
        tmp = SSIDSBusiness(self.s)
        #获取7000的mac地址
        route_mac = tmp.get_router_mac(data_basic['7000_ip'],data_basic['sshUser'],data_basic['7000_pwd'])
        #开启client isolation-gateway
        encry_dict = {'ssid_encryption': "4"}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "gateway_mac",
                     'ssid_gateway_mac': route_mac}
        tmp.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7600lr_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result2 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result3 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.gateway_mac")
        result4 = tmp.connect_NONE_AP(data_wireless['all_ssid'], data_basic["wlan_pc"])
        self.assertIn("1", result1)
        self.assertIn("gateway_mac", result2)
        self.assertIn(route_mac, result3)
        self.assertIn(data_wireless['all_ssid'], result4)
        print "check open isolation gateway-mac, test pass!"

    #验证Clients isolation-raido + 2.4G频段，隔离功能生效
    def test_085_SSIDs_WIFISettings_client_isolation_raido_2g4(self):
        u"""验证Clients isolation-raido + 2.4G频段，隔离功能生效(testlinkID:1983-1)"""
        log.debug("085")
        #修改为wpa2,2.4g
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "radio",
                     'ssid_ssid_band': "2",
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result2 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result4 = tmp.connect_WPA_AP(data_wireless['all_ssid'], data_wireless['short_wpa'],
                                     data_basic["wlan_pc"])
        self.assertIn("1", result1)
        self.assertIn("radio", result2)
        self.assertIn(data_wireless['all_ssid'], result4)
        print "check 2.4g isolation radio, test pass!"

    #验证Clients isolation-internet + 2.4G频段，隔离功能生效
    def test_086_SSIDs_WIFISettings_client_isolation_internet_2g4(self):
        u"""验证Clients isolation-internet + 2.4G频段，隔离功能生效(testlinkID:1983-2)"""
        log.debug("086")
        #开启client isolation-internet
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "internet",
                     'ssid_ssid_band': "2"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result2 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result4 = tmp.connect_WPA_AP(data_wireless['all_ssid'], data_wireless['short_wpa'],
                                     data_basic["wlan_pc"])
        self.assertIn("1", result1)
        self.assertIn("internet", result2)
        self.assertIn(data_wireless['all_ssid'], result4)
        print "check 2.4g isolation internet, test pass!"

    #验证Clients isolation-gateway + 2.4G频段，隔离功能生效
    def test_087_SSIDs_WIFISettings_client_isolation_gateway_2g4(self):
        u"""验证Clients isolation-gateway + 2.4G频段，隔离功能生效(testlinkID:1983-3)"""
        log.debug("087")
        tmp = SSIDSBusiness(self.s)
        #获取7000的mac地址
        route_mac = tmp.get_router_mac(data_basic['7000_ip'],data_basic['sshUser'],data_basic['7000_pwd'])
        #开启client isolation-gateway
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "gateway_mac",
                     'ssid_gateway_mac': route_mac,
                     'ssid_ssid_band': "2"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result2 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result3 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.gateway_mac")
        result4 = tmp.connect_WPA_AP(data_wireless['all_ssid'], data_wireless['short_wpa'],
                                     data_basic["wlan_pc"])
        self.assertIn("1", result1)
        self.assertIn("gateway_mac", result2)
        self.assertIn(route_mac, result3)
        self.assertIn(data_wireless['all_ssid'], result4)
        print "check 2.4g isolation gateway-mac, test pass!"

    #验证Clients isolation-raido + 5G频段，隔离功能生效
    def test_088_SSIDs_WIFISettings_client_isolation_raido_5g(self):
        u"""验证Clients isolation-raido + 5G频段，隔离功能生效(testlinkID:1984-1)"""
        log.debug("088")
        #修改为wpa2,5g
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "radio",
                     'ssid_ssid_band': "5"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result2 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result4 = tmp.connect_WPA_AP(data_wireless['all_ssid'], data_wireless['short_wpa'],
                                     data_basic["wlan_pc"])
        self.assertIn("1", result1)
        self.assertIn("radio", result2)
        self.assertIn(data_wireless['all_ssid'], result4)
        print "check 5g isolation radio, test pass!"

    #验证Clients isolation-internet + 5G频段，隔离功能生效
    def test_089_SSIDs_WIFISettings_client_isolation_internet_5g(self):
        u"""验证Clients isolation-internet + 5G频段，隔离功能生效(testlinkID:1984-2)"""
        log.debug("089")
        #开启client isolation-internet
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "internet",
                     'ssid_ssid_band': "5"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result2 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result4 = tmp.connect_WPA_AP(data_wireless['all_ssid'], data_wireless['short_wpa'],
                                     data_basic["wlan_pc"])
        self.assertIn("1", result1)
        self.assertIn("internet", result2)
        self.assertIn(data_wireless['all_ssid'], result4)
        print "check 5g isolation internet, test pass!"

    #验证Clients isolation-gateway + 5G频段，隔离功能生效
    def test_090_SSIDs_WIFISettings_client_isolation_gateway_5g(self):
        u"""验证Clients isolation-gateway + 5G频段，隔离功能生效(testlinkID:1984-3)"""
        log.debug("090")
        tmp = SSIDSBusiness(self.s)
        #获取7000的mac地址
        route_mac = tmp.get_router_mac(data_basic['7000_ip'],data_basic['sshUser'],data_basic['7000_pwd'])
        #开启client isolation-gateway
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "gateway_mac",
                     'ssid_gateway_mac': route_mac,
                     'ssid_ssid_band': "5"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result2 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result3 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.gateway_mac")
        result4 = tmp.connect_WPA_AP(data_wireless['all_ssid'], data_wireless['short_wpa'],
                                     data_basic["wlan_pc"])
        self.assertIn("1", result1)
        self.assertIn("gateway_mac", result2)
        self.assertIn(route_mac, result3)
        self.assertIn(data_wireless['all_ssid'], result4)
        print "check 5g isolation gateway-mac, test pass!"

    #验证Clients isolation-raido  + client limit，隔离功能生效
    def test_091_SSIDs_WIFISettings_client_isolation_radio_client_limit(self):
        u"""验证Clients isolation-raido  + client limit，隔离功能生效(testlinkID:1986-1)"""
        log.debug("091")
        tmp = SSIDSBusiness(self.s)
        #填写客户端限制范围值-50
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_band': "",
                    'ssid_isolation': "1",
                    'ssid_isolation_mode': "radio",
                    'ssid_wifi_client_limit': "50",
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())
                     }
        tmp.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7600_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath0.maxsta")
        result2 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath1.maxsta")
        result3 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result4 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result5 = tmp.connect_WPA_AP(data_wireless['all_ssid'], data_wireless['short_wpa'],
                                     data_basic["wlan_pc"])
        self.assertIn('50', result1)
        self.assertIn('50', result2)
        self.assertIn("1", result3)
        self.assertIn("radio", result4)
        self.assertIn(data_wireless['all_ssid'], result5)
        print "check Clients isolation-raido  + client limit pass!"

    #验证Clients isolation--internet  + client limit，隔离功能生效
    def test_092_SSIDs_WIFISettings_client_isolation_internet_client_limit(self):
        u"""验证Clients isolation--internet  + client limit，隔离功能生效(testlinkID:1986-2)"""
        log.debug("092")
        tmp = SSIDSBusiness(self.s)
        #填写客户端限制范围值-50
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "internet",
                     'ssid_wifi_client_limit': "50"}
        tmp.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7600_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath0.maxsta")
        result2 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath1.maxsta")
        result3 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result4 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result5 = tmp.connect_WPA_AP(data_wireless['all_ssid'], data_wireless['short_wpa'],
                                     data_basic["wlan_pc"])
        self.assertIn('50', result1)
        self.assertIn('50', result2)
        self.assertIn("1", result3)
        self.assertIn("internet", result4)
        self.assertIn(data_wireless['all_ssid'], result5)
        print "check Clients isolation-internet  + client limit pass!"

    #验证Clients isolation--gateway  + client limit，隔离功能生效
    def test_093_SSIDs_WIFISettings_client_isolation_gateway_client_limit(self):
        u"""验证Clients isolation--gateway  + client limit，隔离功能生效(testlinkID:1986-3)"""
        log.debug("093")
        tmp = SSIDSBusiness(self.s)
        #获取7000的mac地址
        route_mac = tmp.get_router_mac(data_basic['7000_ip'],data_basic['sshUser'],data_basic['7000_pwd'])
        #填写客户端限制范围值-50
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "gateway_mac",
                     'ssid_gateway_mac': route_mac,
                     'ssid_wifi_client_limit': "50"}
        tmp.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7600_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath0.maxsta")
        result2 = ssh.ssh_cmd(data_basic['sshUser'], "uci show wireless.ath1.maxsta")
        result3 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result4 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result5 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.gateway_mac")
        result6 = tmp.connect_WPA_AP(data_wireless['all_ssid'], data_wireless['short_wpa'],
                                     data_basic["wlan_pc"])
        self.assertIn('50', result1)
        self.assertIn('50', result2)
        self.assertIn("1", result3)
        self.assertIn("gateway_mac", result4)
        self.assertIn(route_mac, result5)
        self.assertIn(data_wireless['all_ssid'], result6)
        print "check Clients isolation-gateway  + client limit pass!"

    #验证Clients isolation-raido  + vlan id，隔离功能生效
    def test_094_SSIDs_WIFISettings_client_isolation_radio_vlan(self):
        u"""验证Clients isolation-raido  + vlan id，隔离功能生效(testlinkID:1987-1)"""
        log.debug("094")
        tmp = SSIDSBusiness(self.s)
        #修改vid为2
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "radio",
                     'ssid_vlan': "1",
                    'ssid_vlanid': "2",
                     'ssid_wifi_client_limit': "",
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result2 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result3 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.vlan")
        result4 = tmp.connect_WPA_AP(data_wireless['all_ssid'], data_wireless['short_wpa'],
                                     data_basic["wlan_pc"])
        self.assertIn("1", result1)
        self.assertIn("radio", result2)
        self.assertIn("2", result3)
        self.assertIn(data_wireless['all_ssid'], result4)
        print "check isolation radio+ vid, test pass!"

    #验证Clients isolation-internet  + vlan id，隔离功能生效
    def test_095_SSIDs_WIFISettings_client_isolation_internet_vlan(self):
        u"""验证Clients isolation-internet  + vlan id，隔离功能生效(testlinkID:1987-2)"""
        log.debug("095")
        #开启client isolation-internet
        tmp = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "internet",
                     'ssid_vlan': "1",
                    'ssid_vlanid': "2"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result2 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result3 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.vlan")
        result4 = tmp.connect_WPA_AP(data_wireless['all_ssid'], data_wireless['short_wpa'],
                                     data_basic["wlan_pc"])
        self.assertIn("1", result1)
        self.assertIn("internet", result2)
        self.assertIn("2", result3)
        self.assertIn(data_wireless['all_ssid'], result4)
        print "check isolation internet+ vid, test pass!"

    #验证Clients isolation-gateway + vlan id，隔离功能生效
    def test_096_SSIDs_WIFISettings_client_isolation_gateway_vlan(self):
        u"""验证Clients isolation-gateway + vlan id，隔离功能生效(testlinkID:1987-3)"""
        log.debug("096")
        tmp = SSIDSBusiness(self.s)
        #获取7000的mac地址
        route_mac = tmp.get_router_mac(data_basic['7000_ip'],data_basic['sshUser'],data_basic['7000_pwd'])
        #开启client isolation-gateway
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_isolation': "1",
                     'ssid_isolation_mode': "gateway_mac",
                     'ssid_gateway_mac': route_mac,
                     'ssid_vlan': "1",
                    'ssid_vlanid': "2"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result2 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result3 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.gateway_mac")
        result5 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.vlan")
        result4 = tmp.connect_WPA_AP(data_wireless['all_ssid'], data_wireless['short_wpa'],
                                     data_basic["wlan_pc"])
        self.assertIn("1", result1)
        self.assertIn("gateway_mac", result2)
        self.assertIn(route_mac, result3)
        self.assertIn("2", result5)
        self.assertIn(data_wireless['all_ssid'], result4)
        print "check isolation gateway-mac+ vid, test pass!"

    #验证重启设备，clients isolation功能不会失效
    def test_097_SSIDs_WIFISettings_client_isolation_radio_reboot(self):
        u"""验证重启设备，clients isolation功能不会失效(testlinkID:1990)"""
        log.debug("097")
        tmp = SSIDSBusiness(self.s)
        #修改为isolation-radio
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_vlan': "0",
                    'ssid_isolation': "1",
                    'ssid_isolation_mode': "radio"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #重启设备
        tmp1 = APSBusiness(self.s)
        tmp1.reboot_one_ap(data_ap['7610_mac'])
        time.sleep(360)
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7610_ip'], ssh_pwd)
        result1 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation")
        result2 = ssh.ssh_cmd(data_basic['sshUser'],"uci show grandstream.ssid0.isolation_mode")
        result4 = tmp.connect_WPA_AP(data_wireless['all_ssid'], data_wireless['short_wpa'],
                                     data_basic["wlan_pc"])
        self.assertIn("1", result1)
        self.assertIn("radio", result2)
        self.assertIn(data_wireless['all_ssid'], result4)
        print "after rebooting ap, check isolation radio, test pass!"

    #验证开启RSSI后，弹出输入选项，填入相应值-1，功能生效
    def test_098_SSIDs_WIFISettings_rssi_1(self):
        u"""验证开启RSSI后，弹出输入选项，填入相应值-1，功能生效(testlinkID:1991-1)"""
        log.debug("098")
        tmp = SSIDSBusiness(self.s)
        #修改为rssi为-1
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_isolation': "0",
                    'ssid_rssi_enable': "1",
                    'ssid_rssi': "-1"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡连接
        tmp.connect_WPA_AP_backup(data_wireless['all_ssid'], data_wireless['short_wpa'],
                                     data_basic["wlan_pc"])
        #在2分钟内每隔2秒检查无线网卡是否一直保持和ap连接
        result = tmp.check_wifi_client_connected_allthetime(data_basic['wlan_pc'])
        self.assertIn("Not connected.\n", result)
        print "check min rssi is -1 validity,test pass!"

    #验证开启RSSI后，弹出输入选项，填入相应值-94，功能生效
    def test_099_SSIDs_WIFISettings_rssi_94(self):
        u"""验证开启RSSI后，弹出输入选项，填入相应值-94，功能生效(testlinkID:1991-2)"""
        log.debug("099")
        tmp = SSIDSBusiness(self.s)
        #修改为rssi为-1
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_rssi_enable': "1",
                     'ssid_rssi': "-94"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡连接
        tmp.connect_WPA_AP(data_wireless['all_ssid'], data_wireless['short_wpa'],
                                     data_basic["wlan_pc"])
        #在2分钟内每隔2秒检查无线网卡是否一直保持和ap连接
        result = tmp.check_wifi_client_connected_allthetime(data_basic['wlan_pc'])
        self.assertNotIn("Not connected.\n", result)
        print "check min rssi is -94 validity,test pass!"

    #验证不同ssid设置该项，不相互影响
    def test_100_SSIDs_WIFISettings_rssi_different_ssid_1(self):
        u"""验证不同ssid设置该项，不相互影响-1(testlinkID:1996-1)"""
        log.debug("100")
        tmp = SSIDSBusiness(self.s)
        #新增ssid,并开启rssi为-1
        encry_dict1 = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict1 = {'ssid_rssi_enable': "1",
                     'ssid_rssi': "-1"}
        tmp.add_ssid(data_ap['7610_mac'], data_wireless['all_ssid']+"-2",
                     data_wireless['short_wpa'])
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid']+"-2",
                       encry_dict1, data_dict1)
        time.sleep(120)
        #无线网卡连接ssid0
        tmp.connect_WPA_AP(data_wireless['all_ssid'], data_wireless['short_wpa'],
                                     data_basic["wlan_pc"])
        #在2分钟内每隔2秒检查无线网卡是否一直保持和ap连接
        result0 = tmp.check_wifi_client_connected_allthetime(data_basic['wlan_pc'])

        #无线网卡连接ssid1
        tmp.connect_WPA_AP_backup(data_wireless['all_ssid']+"-2", data_wireless['short_wpa'],
                                     data_basic["wlan_pc"])
        #在2分钟内每隔2秒检查无线网卡是否一直保持和ap连接
        result1 = tmp.check_wifi_client_connected_allthetime(data_basic['wlan_pc'])
        self.assertNotIn("Not connected.\n", result0)
        self.assertIn("Not connected.\n", result1)
        print "check different ssid's rssi can't been effect, test pass!"

    #验证不同ssid设置该项，不相互影响
    def test_101_SSIDs_WIFISettings_rssi_different_ssid_2(self):
        u"""验证不同ssid设置该项，不相互影响-2(testlinkID:1996-2)"""
        log.debug("101")
        tmp = SSIDSBusiness(self.s)
        #修改ssid0的rssi为-1
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_rssi_enable': "1",
                     'ssid_rssi': "-1"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #修改ssid1的rssi为-94
        encry_dict1 = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict1 = {'ssid_rssi_enable': "1",
                     'ssid_rssi': "-94"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid']+"-2",
                       encry_dict1, data_dict1)
        time.sleep(120)
        #无线网卡连接ssid0
        tmp.connect_WPA_AP_backup(data_wireless['all_ssid'], data_wireless['short_wpa'],
                                     data_basic["wlan_pc"])
        #在2分钟内每隔2秒检查无线网卡是否一直保持和ap连接
        result0 = tmp.check_wifi_client_connected_allthetime(data_basic['wlan_pc'])

        #无线网卡连接ssid1
        tmp.connect_WPA_AP(data_wireless['all_ssid']+"-2", data_wireless['short_wpa'],
                                     data_basic["wlan_pc"])
        #在2分钟内每隔2秒检查无线网卡是否一直保持和ap连接
        result1 = tmp.check_wifi_client_connected_allthetime(data_basic['wlan_pc'])
        #删除多余的ssid
        tmp.delete_ssid(data_wireless['all_ssid']+"-2")
        #关闭ssid0的rssi
        data_dict2 = {'ssid_rssi_enable': "0"}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict2)
        time.sleep(120)
        self.assertIn("Not connected.\n", result0)
        self.assertNotIn("Not connected.\n", result1)
        print "check different ssid's rssi can't been effect, test pass!"

    #点击For the Last ，2小时，一天，一周，一个月，测试是否能正常点击，以及统计图是否有变化
    def test_102_SSIDs_summary_client_count(self):
        u"""点击For the Last ，2小时，一天，一周，一个月，测试是否能正常点击，以及统计图是否有变化-客户端数量-1(testlinkID:1802-1)"""
        log.debug("102")
        tmp = SSIDSBusiness(self.s)
        #获取2小时，一天，一周，一个月的客户端图，并检查有无变化
        result = tmp.check_ssids_summary_distribution_client_count()
        self.assertTrue(result)
        print "check SSIDs summary client count chart, test pass!"

    #点击For the Last ，2小时，一天，一周，一个月，测试是否能正常点击，以及统计图是否有变化
    def test_103_SSIDs_summary_bandwidth(self):
        u"""点击For the Last ，2小时，一天，一周，一个月，测试是否能正常点击，以及统计图是否有变化-客户端数量-1(testlinkID:1802-1)"""
        log.debug("103")
        tmp = SSIDSBusiness(self.s)
        #获取2小时，一天，一周，一个月的速率图，并检查有无变化
        result = tmp.check_ssids_summary_distribution_bandwidth()
        self.assertTrue(result)
        print "check SSIDs summary bandwidth chart, test pass!"

    #更改SSID名称，检查统计图上的SSID是否也随之更新
    def test_104_SSIDs_summary_ssid0_name(self):
        u"""更改SSID名称，检查统计图上的SSID是否也随之更新(testlinkID:1814)"""
        log.debug("104")
        tmp = SSIDSBusiness(self.s)
        #SSIDs-概要页面，获取ssid0的名称
        result = tmp.get_ssids_summary_ssid0_name()
        self.assertEqual(data_wireless['all_ssid'], result)
        print "check SSID summary ssid name when deploy ssid'name, test pass!"

    #验证已添加设备列表中，无AP时，ssid无法正常使用
    def test_105_SSIDs_Devices_membership_no_ap(self):
        u"""验证已添加设备列表中，无AP时，ssid无法正常使用(testlinkID:2000)"""
        log.debug("105")
        tmp = SSIDSBusiness(self.s)
        #cloud增加ssid,不添加ap
        tmp.add_ssid_no_ap(data_wireless['all_ssid']+"-2", data_wireless['short_wpa'])
        time.sleep(60)
        #无线网卡无法扫描到ap
        result = tmp.ssid_scan_result(data_wireless['all_ssid']+"-2", data_basic["wlan_pc"])
        #删除新建的ssid
        tmp.delete_ssid(data_wireless['all_ssid']+"-2")
        self.assertFalse(result)
        print "check devices membership have not ap, test pass!"

    #验证已添加设备列表中，有一个AP时，ssid能正常使用
    def test_106_SSIDs_Devices_membership_one_ap(self):
        u"""验证已添加设备列表中，有一个AP时，ssid能正常使用(testlinkID:2001)"""
        log.debug("106")
        tmp = SSIDSBusiness(self.s)
        #无线网卡能够扫描到默认ap的ssid
        result = tmp.ssid_scan_result_backup(data_wireless['all_ssid'], data_basic["wlan_pc"])
        self.assertTrue(result)
        print "check devices membership have one ap, test pass!"

    #验证已添加设备列表中，有多个AP时，ssid能正常使用
    def test_107_SSIDs_Devices_membership_many_ap(self):
        u"""验证已添加设备列表中，有多个AP时，ssid能正常使用(testlinkID:2002,2005)"""
        log.debug("107")
        tmp = SSIDSBusiness(self.s)
        #ssid0加入到三个ap中
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'membership_macs': "%s,%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper(),
                                             data_ap['7610_mac'].upper())}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡能够扫描到默认ap的ssid
        result = tmp.ssid_scan_result_backup(data_wireless['all_ssid'], data_basic["wlan_pc"])
        self.assertTrue(result)
        print "check devices membership have one ap, test pass!"

    #验证将AP从已添加设备列表中移除时（列表中还有其他ap），设备MAC地址会出现在可添加设备列表中，WiFi无异常
    def test_108_SSIDs_Devices_membership_remove_ap(self):
        u"""验证将AP从已添加设备列表中移除时（列表中还有其他ap），设备MAC地址会出现在可添加设备列表中，WiFi无异常(testlinkID:2003,2004)"""
        log.debug("108")
        tmp = SSIDSBusiness(self.s)
        #ssid0剔除2个个ap中
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #获取ssids中membership的已添加的设备
        result1 = tmp.get_available_device(data_wireless['all_ssid'])
        #无线网卡能够扫描到默认ap的ssid
        result2 = tmp.ssid_scan_result_backup(data_wireless['all_ssid'], data_basic["wlan_pc"])
        self.assertNotIn(data_ap['7600_mac'].upper(), result1)
        self.assertNotIn(data_ap['7600lr_mac'].upper(), result1)
        self.assertIn(data_ap['7610_mac'].upper(), result1)
        self.assertTrue(result2)
        print "check devices membership remove ap, test pass!"

    #验证AP-offline后，AP不会从列表中消失
    def test_109_SSIDs_Devices_membership_offlineap_ap_not_disapper(self):
        u"""验证AP-offline后，AP不会从列表中消失(testlinkID:2007)"""
        log.debug("109")
        #重7610
        tmp1 = APSBusiness(self.s)
        tmp1.reboot_one_ap(data_ap['7610_mac'])
        time.sleep(90)
        #获取ssids中membership的已添加的设备
        tmp = SSIDSBusiness(self.s)
        result1 = tmp.get_available_device(data_wireless['all_ssid'])
        self.assertIn(data_ap['7610_mac'].upper(), result1)

    #验证删除AP配对后，AP会从列表中消失
    def test_110_SSIDs_Devices_membership_delete_ap_disapper(self):
        u"""验证删除AP配对后，AP会从列表中消失(testlinkID:2006)"""
        log.debug("110")
        #删除7610
        tmp1 = APSBusiness(self.s)
        tmp1.delete_ap(data_ap['7610_mac'])
        time.sleep(360)
        #获取ssids中membership的已添加的设备
        tmp = SSIDSBusiness(self.s)
        result1 = tmp.get_available_device(data_wireless['all_ssid'])
        self.assertNotIn(data_ap['7610_mac'].upper(), result1)

    #验证刚配对的AP会自动加入默认开启的ssid已添加设备列表中
    def test_111_SSIDs_Devices_membership_delete_ap_disapper(self):
        u"""验证刚配对的AP会自动加入默认开启的ssid已添加设备列表中(testlinkID:1999)"""
        log.debug("111")
        tmp1 = APSBusiness(self.s)
        #将ap复位，并将ap的hosts替换，指向本地cloud，然后将该ap添加到cloud中
        tmp1.add_ap_2_local_cloud(data_basic['7610_ip'], data_ap['7610_mac'], "autotest_7610")
        #获取ssids中membership的已添加的设备
        tmp = SSIDSBusiness(self.s)
        result1 = tmp.get_available_device(data_wireless['all_ssid'])
        self.assertIn(data_ap['7610_mac'].upper(), result1)

    #验证AP总数统计与列表里的数量一致
    def test_112_SSIDs_Devices_membership_device_number(self):
        u"""验证AP总数统计与列表里的数量一致(testlinkID:2008)"""
        log.debug("112")
        #获取ap总数
        tmp1 = APSBusiness(self.s)
        ap_info = tmp1.get_configure_ap_info()
        ap_number = len(ap_info)
        print "ap number is %s"%ap_number
        #获取ssids中membership的ap总数量
        tmp = SSIDSBusiness(self.s)
        list_number = tmp.get_device_number(data_wireless['all_ssid'])
        self.assertEqual(ap_number, list_number)

    #验证一个AP在两个列表中多次切换，AP状态正常，系统正常
    def test_113_SSIDs_Devices_membership_device_number(self):
        u"""验证一个AP在两个列表中多次切换，AP状态正常，系统正常(testlinkID:2009)"""
        log.debug("113")
        tmp = SSIDSBusiness(self.s)
        #无线网卡能够扫描到默认ap的ssid
        result1 = tmp.ssid_scan_result_backup(data_wireless['all_ssid'], data_basic["wlan_pc"])
        #ssid0剔除7610
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'removed_macs': "%s"%data_ap['7610_mac'].upper()}
        tmp.edit_ssid("", data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡不能扫描到默认ap的ssid
        result2 = tmp.ssid_scan_result(data_wireless['all_ssid'], data_basic["wlan_pc"])
        #ssid0再加入7610
        data_dict1 = {}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict1)
        time.sleep(120)
        #无线网卡能够扫描到默认ap的ssid
        result3 = tmp.ssid_scan_result_backup(data_wireless['all_ssid'], data_basic["wlan_pc"])
        self.assertTrue(result1)
        self.assertFalse(result2)
        self.assertTrue(result3)

    #验证多个AP在两个列表中多次切换，AP状态正常，系统正常
    def test_114_SSIDs_Devices_membership_device_number(self):
        u"""验证多个AP在两个列表中多次切换，AP状态正常，系统正常(testlinkID:2010)"""
        log.debug("114")
        tmp = SSIDSBusiness(self.s)
        #ssid0加入7610，7600,7600lr
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'membership_macs': "%s,%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper(),
                                             data_ap['7610_mac'].upper())}
        tmp.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡能够扫描到默认ap的ssid
        result1 = tmp.ssid_scan_result_backup(data_wireless['all_ssid'], data_basic["wlan_pc"])
        #ssid0再剔除7610，7600,7600lr
        data_dict1 = {'removed_macs': "%s,%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper(),
                                             data_ap['7610_mac'].upper())}
        tmp.edit_ssid("", data_wireless['all_ssid'],
                       encry_dict, data_dict1)
        time.sleep(120)
        #无线网卡不能扫描到默认ap的ssid
        result2 = tmp.ssid_scan_result(data_wireless['all_ssid'], data_basic["wlan_pc"])
        self.assertTrue(result1)
        self.assertFalse(result2)

    #删除ap，并恢复cloud的初始环境
    def test_115_reset_cloud(self):
        u"""删除ap，并恢复cloud的初始环境"""
        log.debug("115")
        #测试完后恢复初始环境
        #1.修改ap的ssid为GWN-Cloud
        tmp1 = SSIDSBusiness(self.s)
        tmp1.dhcp_release_wlan(data_basic['wlan_pc'])
        tmp1.disconnect_ap()
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_vlan': "0",
                     'ssid_isolation': "0",
                     'ssid_rssi_enable': "0",
                    'ssid_ssid': "GWN-Cloud",
                    'ssid_ssid_band': ""}
        tmp1.edit_ssid("", data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #删除三个ap
        tmp = APSBusiness(self.s)
        tmp.delete_ap(data_ap['7610_mac'])
        tmp.delete_ap(data_ap['7600_mac'])
        tmp.delete_ap(data_ap['7600lr_mac'])
        time.sleep(360)










    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
