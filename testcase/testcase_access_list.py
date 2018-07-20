#coding=utf-8
#作者：曾祥卫
#时间：2018.05.24
#描述：Network-Access Control-Access List用例集，调用Accesslist_business

import unittest, time, subprocess
from access_points.aps_business import APSBusiness
from system.settings.settings_business import SettingsBusiness
from ssids.ssids_business import SSIDSBusiness
from clients.clients_business import Clients_Business
from access_control.access_list.accesslist_business import AccessListBusiness
from data import data
from connect.ssh import SSH
from data.logfile import Log
import requests
log = Log("accesslist")


data_basic = data.data_basic()
data_login = data.data_login()
data_wireless = data.data_wireless()
data_ng = data.data_networkgroup()
data_ap = data.data_AP()
data_client = data.data_Client()




class TestAccessList(unittest.TestCase):
    u"""测试Network-Access Control-Access List的用例集(runtime:4.37h)"""
    def setUp(self):
        self.s = requests.session()
        tmp = AccessListBusiness(self.s)
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


    #block客户端
    def test_002_block_client(self):
        u"""block客户端(testlinkID:1488)"""
        log.debug("002")
        #ssid修改，并使用client去连接
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid': data_wireless['all_ssid'],
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp1.edit_ssid(data_ap['7610_mac'], 'GWN-Cloud',
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡连接ap
        tmp1.connect_DHCP_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        #等待2分钟ap上传数据到cloud
        time.sleep(120)
        tmp1.dhcp_release_wlan_backup(data_basic["wlan_pc"])

        #block 客户端
        tmp = Clients_Business(self.s)
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        tmp.set_client_block(client_mac)
        time.sleep(120)
        tmp3 = SettingsBusiness(self.s)
        ssh_pwd = tmp3.get_ssh_pwd()
        #获取Global Blacklist中的mac地址
        tmp2 = AccessListBusiness(self.s)
        Global_Blacklist = tmp2.get_Global_Blacklist_mac()
        #检查ap后台中，Global Blacklist是否有对应mac地址
        result = tmp2.check_Global_Blacklist_cli(data_basic['7610_ip'],
                data_basic['sshUser'], ssh_pwd, client_mac)
        self.assertIn(client_mac.upper(), Global_Blacklist)
        self.assertTrue(result)

    #Blocked clients重连验证-1
    def test_003_reconnect_block_client(self):
        u"""Blocked clients重连验证-1(testlinkID:1489-1)"""
        log.debug("003")
        #client重连ap
        tmp = AccessListBusiness(self.s)
        result = tmp.connect_WPA_AP_backup(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn("Not connected.", result)

    #Blocked clients重连验证-2
    def test_004_reconnect_block_client(self):
        u"""Blocked clients重连验证-2(testlinkID:1489-2)"""
        log.debug("004")
        #新建ssid2并加入7600ap中
        tmp2 = SSIDSBusiness(self.s)
        tmp2.add_ssid(data_ap['7600_mac'], data_wireless['all_ssid']+"-2",
                     data_wireless['short_wpa'])
        time.sleep(120)
        #无线网卡连接ssid2
        tmp = Clients_Business(self.s)
        result = tmp.connect_WPA_AP_backup(data_wireless['all_ssid']+"-2",
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        # #把Global Blacklist中的mac地址清空
        tmp2 = AccessListBusiness(self.s)
        tmp2.set_Global_Blacklist_blank()
        time.sleep(120)
        self.assertIn("Not connected.", result)

    #Block 5G客户端-1
    def test_005_block_5g_client(self):
        u"""Block 5G客户端-1(testlinkID:1490-1)"""
        log.debug("005")
        #修改ssid2为5G
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_band': "5"}
        tmp1.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid']+"-2",
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡连接ap
        tmp1.connect_DHCP_WPA_AP(data_wireless['all_ssid']+"-2",
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        #等待2分钟ap上传数据到cloud
        time.sleep(120)
        tmp1.dhcp_release_wlan_backup(data_basic["wlan_pc"])

        #block 客户端
        tmp = Clients_Business(self.s)
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        tmp.set_client_block(client_mac)
        time.sleep(120)
        tmp3 = SettingsBusiness(self.s)
        ssh_pwd = tmp3.get_ssh_pwd()
        #获取Global Blacklist中的mac地址
        tmp2 = AccessListBusiness(self.s)
        Global_Blacklist = tmp2.get_Global_Blacklist_mac()
        #检查ap后台中，Global Blacklist是否有对应mac地址
        result = tmp2.check_Global_Blacklist_cli(data_basic['7600_ip'],
                data_basic['sshUser'], ssh_pwd, client_mac)
        self.assertIn(client_mac.upper(), Global_Blacklist)
        self.assertTrue(result)

    #Block 5G客户端-2
    def test_006_block_5g_client(self):
        u"""Block 5G客户端-2(testlinkID:1490-2)"""
        log.debug("006")
        tmp = Clients_Business(self.s)
        result = tmp.connect_WPA_AP_backup(data_wireless['all_ssid']+"-2",
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        # #把Global Blacklist中的mac地址清空
        tmp2 = AccessListBusiness(self.s)
        tmp2.set_Global_Blacklist_blank()
        time.sleep(120)
        self.assertIn("Not connected.", result)

    #Block 2.4G客户端-1
    def test_007_block_2g4_client(self):
        u"""Block 2.4G客户端-1(testlinkID:1491-1)"""
        log.debug("007")
        #修改ssid2为2.4G
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_band': "2"}
        tmp1.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid']+"-2",
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡连接ap
        tmp1.connect_DHCP_WPA_AP(data_wireless['all_ssid']+"-2",
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        #等待2分钟ap上传数据到cloud
        time.sleep(120)
        tmp1.dhcp_release_wlan_backup(data_basic["wlan_pc"])

        #block 客户端
        tmp = Clients_Business(self.s)
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        tmp.set_client_block(client_mac)
        time.sleep(120)
        tmp3 = SettingsBusiness(self.s)
        ssh_pwd = tmp3.get_ssh_pwd()
        #获取Global Blacklist中的mac地址
        tmp2 = AccessListBusiness(self.s)
        Global_Blacklist = tmp2.get_Global_Blacklist_mac()
        #检查ap后台中，Global Blacklist是否有对应mac地址
        result = tmp2.check_Global_Blacklist_cli(data_basic['7600_ip'],
                data_basic['sshUser'], ssh_pwd, client_mac)
        self.assertIn(client_mac.upper(), Global_Blacklist)
        self.assertTrue(result)

    #Block 2.4G客户端-2
    def test_008_block_2g4_client(self):
        u"""Block 2.4G客户端-2(testlinkID:1491-2)"""
        log.debug("008")
        tmp = Clients_Business(self.s)
        result = tmp.connect_WPA_AP_backup(data_wireless['all_ssid']+"-2",
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        # #把Global Blacklist中的mac地址清空
        tmp2 = AccessListBusiness(self.s)
        tmp2.set_Global_Blacklist_blank()
        time.sleep(120)
        self.assertIn("Not connected.", result)

    #检查Global Blacklist中的MAC地址统计
    def test_009_check_Global_Blacklist_macCount(self):
        u"""检查Global Blacklist中的MAC地址统计(testlinkID:1493)"""
        log.debug("009")
        #Global Blacklist中添加10个mac地址
        tmp = AccessListBusiness(self.s)
        #10个随机mac，添加到macs的list中
        macs = []
        for i in range(10):
            macs.append(tmp.randomMAC())
        tmp.edit_Global_Blacklist_mac(macs)
        time.sleep(120)
        #获取Global Blacklist中的mac地址的统计数量
        macCount = tmp.get_Global_Blacklist_macCount()
        self.assertEqual(macCount, 10)

    #手动添加MAC地址到Global Blacklist
    def test_010_manual_add_clientmac_Global_Blacklist(self):
        u"""手动添加MAC地址到Global Blacklist(testlinkID:1494)"""
        log.debug("010")
        #手动添加mac地址到Global Blacklist
        tmp = AccessListBusiness(self.s)
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        macs = []
        macs.append(client_mac)
        tmp.edit_Global_Blacklist_mac(macs)
        time.sleep(240)
        #获取Global Blacklist中的mac地址
        Global_Blacklist = tmp.get_Global_Blacklist_mac()
        # #获取ssh密码
        # tmp3 = SettingsBusiness(self.s)
        # ssh_pwd = tmp3.get_ssh_pwd()
        # #检查ap后台中，Global Blacklist是否有对应mac地址
        # result = tmp.check_Global_Blacklist_cli(data_basic['7600_ip'],
        #         data_basic['sshUser'], ssh_pwd, client_mac)
        self.assertIn(client_mac.upper(), Global_Blacklist)
        # self.assertTrue(result)

    #被手动添加到Global Blacklist中的Client重连验证
    def test_011_manualmac_reconnect(self):
        u"""被手动添加到Global Blacklist中的Client重连验证(testlinkID:1495)"""
        log.debug("011")
        #修改ssid2为dual-band
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_band': ""}
        tmp1.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid']+"-2",
                       encry_dict, data_dict)
        time.sleep(120)
        result = tmp1.connect_WPA_AP_backup(data_wireless['all_ssid']+"-2",
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn("Not connected.", result)

    #添加多条MAC地址到Global Blacklist-1
    def test_012_check_Global_Blacklist_manymac(self):
        u"""添加多条MAC地址到Global Blacklist-1(testlinkID:1496-1)"""
        log.debug("012")
        #Global Blacklist中添加10个mac地址
        tmp = AccessListBusiness(self.s)
        #第一条为client的mac
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        macs = []
        macs.append(client_mac)
        #后面9个随机mac，添加到macs的list中
        for i in range(9):
            macs.append(tmp.randomMAC())
        tmp.edit_Global_Blacklist_mac(macs)
        time.sleep(120)
        #获取Global Blacklist中的mac地址
        Global_Blacklist = tmp.get_Global_Blacklist_mac()
        #获取ssh密码
        # tmp3 = SettingsBusiness(self.s)
        # ssh_pwd = tmp3.get_ssh_pwd()
        # #检查ap后台中，Global Blacklist是否有对应mac地址
        # result = tmp.check_Global_Blacklist_cli(data_basic['7600_ip'],
        #         data_basic['sshUser'], ssh_pwd, client_mac)
        self.assertIn(client_mac.upper(), Global_Blacklist)
        # self.assertTrue(result)

    #添加多条MAC地址到Global Blacklist-2
    def test_013_check_Global_Blacklist_manymac(self):
        u"""添加多条MAC地址到Global Blacklist-2(testlinkID:1496-2)"""
        log.debug("013")
        tmp = AccessListBusiness(self.s)
        result = tmp.connect_WPA_AP_backup(data_wireless['all_ssid']+"-2",
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn("Not connected.", result)

    #添加两个相同的MAC地址到Global Blacklist，只会显示一条
    def test_014_check_Global_Blacklist_samemac(self):
        u"""添加两个相同的MAC地址到Global Blacklist，只会显示一条(testlinkID:1497)"""
        log.debug("014")
        #Global Blacklist中添加两个相同的mac地址
        tmp = AccessListBusiness(self.s)
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        macs = []
        for i in range(2):
            macs.append(client_mac)
        tmp.edit_Global_Blacklist_mac(macs)
        time.sleep(120)
        #获取Global Blacklist中的mac地址的统计数量
        macCount = tmp.get_Global_Blacklist_macCount()
        self.assertEqual(macCount, 1)

    #手动添加MAC地址后检查Global Blacklist中的MAC地址的统计
    def test_015_check_manualmac_Global_Blacklist_macCount(self):
        u"""手动添加MAC地址后检查Global Blacklist中的MAC地址的统计(testlinkID:1498)"""
        log.debug("015")
        #Global Blacklist中添加10个mac地址
        tmp = AccessListBusiness(self.s)
        #10个随机mac，添加到macs的list中
        macs = []
        for i in range(10):
            macs.append(tmp.randomMAC())
        tmp.edit_Global_Blacklist_mac(macs)
        time.sleep(120)
        #获取Global Blacklist中的mac地址的统计数量
        macCount = tmp.get_Global_Blacklist_macCount()
        self.assertEqual(macCount, 10)

    #重启后检查Global Blacklist是否生效
    def test_016_check_reboot_Global_Blacklist(self):
        u"""重启后检查Global Blacklist是否生效(testlinkID:1499)"""
        log.debug("016")
        #手动添加mac地址到Global Blacklist
        tmp = AccessListBusiness(self.s)
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        macs = []
        macs.append(client_mac)
        tmp.edit_Global_Blacklist_mac(macs)
        time.sleep(120)
        #重启7600
        tmp1 = APSBusiness(self.s)
        tmp1.reboot_one_ap(data_ap['7600_mac'])
        time.sleep(420)
        #获取Global Blacklist中的mac地址
        Global_Blacklist = tmp.get_Global_Blacklist_mac()
        result = tmp.connect_WPA_AP_backup(data_wireless['all_ssid']+"-2",
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn("Not connected.", result)
        self.assertIn(client_mac.upper(), Global_Blacklist)

    #删除Global Blacklist中的终端
    def test_017_delete_Global_Blacklist_mac(self):
        u"""删除Global Blacklist中的终端(testlinkID:1501)"""
        log.debug("017")
        #删除Global Blacklist中client的mac地址
        tmp = AccessListBusiness(self.s)
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        tmp.set_Global_Blacklist_blank()
        time.sleep(120)
        #获取Global Blacklist中的mac地址
        Global_Blacklist = tmp.get_Global_Blacklist_mac()
        #获取ssh密码
        tmp3 = SettingsBusiness(self.s)
        ssh_pwd = tmp3.get_ssh_pwd()
        #检查ap后台中，Global Blacklist是否有对应mac地址
        result = tmp.check_Global_Blacklist_cli(data_basic['7600_ip'],
                data_basic['sshUser'], ssh_pwd, client_mac)
        self.assertNotIn(client_mac.upper(), Global_Blacklist)
        self.assertFalse(result)

    #被删除的终端的重连验证
    def test_018_reconnect_client_after_delete_mac(self):
        u"""被删除的终端的重连验证(testlinkID:1502)"""
        log.debug("018")
        tmp = AccessListBusiness(self.s)
        result = tmp.connect_WPA_AP(data_wireless['all_ssid']+"-2",
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid']+"-2", result)

    #验证默认情况下MAC Filter为关闭
    def test_019_MAC_Filter_default_status(self):
        u"""被删除的终端的重连验证(testlinkID:1503)"""
        log.debug("019")
        tmp1 = SSIDSBusiness(self.s)
        #分别获取两个ssid的mac filter的状态
        ssid1_info = tmp1.get_ssid_info(data_wireless['all_ssid'])
        mac_filter1 = ssid1_info['macFiltering']
        ssid2_info = tmp1.get_ssid_info(data_wireless['all_ssid']+"-2")
        mac_filter2 = ssid2_info['macFiltering']
        self.assertEqual(mac_filter1, "0")
        self.assertEqual(mac_filter2, "0")

    #添加新的List
    def test_020_add_new_list(self):
        u"""添加新的List(testlinkID:1505)"""
        log.debug("020")
        #新增list
        tmp = AccessListBusiness(self.s)
        random_mac = tmp.randomMAC()
        macs = []
        macs.append(random_mac)
        tmp.add_list("Access list1", macs)
        time.sleep(60)
        #检查页面上是否有新建list
        list_info = tmp.get_list_info("Access list1")
        self.assertEqual(list_info['name'], "Access list1")

    #删除Access list
    def test_021_delete_new_list(self):
        u"""删除Access list(testlinkID:1506)"""
        log.debug("021")
        #删除新增的list
        tmp = AccessListBusiness(self.s)
        tmp.delete_list("Access list1")
        time.sleep(60)
        #检查页面上是否有新建list
        list_info = tmp.get_list_info("Access list1")
        self.assertEqual(list_info, None)

    #添加两个相同的MAC地址到Access list
    def test_022_check_Accesslist_samemac(self):
        u"""添加两个相同的MAC地址到Access list(testlinkID:1510)"""
        log.debug("022")
        #新增list,添加两个相同的mac地址
        tmp = AccessListBusiness(self.s)
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        macs = []
        for i in range(2):
            macs.append(client_mac)
        tmp.add_list("Access list1", macs)
        time.sleep(60)
        #获取Access list中的mac地址的统计数量
        macCount = tmp.get_list_info("Access list1")['macCount']
        self.assertEqual(macCount, 1)

    #添加空的list
    def test_023_addnewlist_blankmac(self):
        u"""添加空的list(testlinkID:1511)"""
        log.debug("023")
        #新增list
        tmp = AccessListBusiness(self.s)
        macs = []
        tmp.add_list("Access list2", macs)
        time.sleep(60)
        #检查页面上是否有新建list
        list_info = tmp.get_list_info("Access list2")
        #删除Access list2
        tmp.delete_list("Access list2")
        time.sleep(60)
        self.assertEqual(list_info['name'], "Access list2")

    #Access list应用于黑名单-1检查cli配置
    def test_024_apply_Access_list_blacklist(self):
        u"""Access list应用于黑名单-1检查cli配置(testlinkID:1515-1)"""
        log.debug("024")
        #首先需要获取Access list1的id--ssid页面中选择access list是通过id
        tmp = AccessListBusiness(self.s)
        #获取Access list1的id
        list_info = tmp.get_list_info("Access list1")
        id1 = list_info['id']

        #然后在修改ssid1为黑名单
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_mac_filtering':"2",
                     'ssid_maclist_black':["%s"%id1]}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp3 = SettingsBusiness(self.s)
        ssh_pwd = tmp3.get_ssh_pwd()
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        #检查ap后台中，Blacklist是否生效
        result = tmp.check_Blacklist_cli(data_basic['7610_ip'],
                data_basic['sshUser'], ssh_pwd, client_mac)
        self.assertTrue(result)

    #Access list应用于黑名单-2该client不能连上
    def test_025_apply_Access_list_blacklist(self):
        u"""Access list应用于黑名单-2该client不能连上(testlinkID:1515-2)"""
        log.debug("025")
        tmp = AccessListBusiness(self.s)
        result = tmp.connect_WPA_AP_backup(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn("Not connected.", result)

    #Access list应用于黑名单-3其他client不能连上
    def test_026_apply_Access_list_blacklist(self):
        u"""Access list应用于黑名单-3其他client不能连上(testlinkID:1515-3)"""
        log.debug("026")
        #修改Access list1为其他client
        tmp = AccessListBusiness(self.s)
        random_mac = tmp.randomMAC()
        macs = []
        macs.append(random_mac)
        tmp.edit_list("Access list1", macs)
        time.sleep(120)
        #使用其他client去连接，能连接上
        result = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)

    #应用黑名单后再添加MAC地址-1
    def test_027_add_mac_after_apply_blacklist(self):
        u"""应用黑名单后再添加MAC地址-1(testlinkID:1516-1)"""
        log.debug("027")
        #Access list添加client mac
        #修改Access list1为其他client
        tmp = AccessListBusiness(self.s)
        random_mac = tmp.randomMAC()
        macs = []
        macs.append(random_mac)
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        macs.append(client_mac)
        tmp.edit_list("Access list1", macs)
        time.sleep(120)
        tmp3 = SettingsBusiness(self.s)
        ssh_pwd = tmp3.get_ssh_pwd()
        #检查ap后台中，Blacklist是否生效
        result1 = tmp.check_Blacklist_cli(data_basic['7610_ip'],
                data_basic['sshUser'], ssh_pwd, client_mac)
        result2 = tmp.check_Blacklist_cli(data_basic['7610_ip'],
                data_basic['sshUser'], ssh_pwd, random_mac)
        self.assertTrue(result1)
        self.assertTrue(result2)

    #应用黑名单后再添加MAC地址-2
    def test_028_add_mac_after_apply_blacklist(self):
        u"""应用黑名单后再添加MAC地址-2(testlinkID:1516-2)"""
        log.debug("028")
        tmp = AccessListBusiness(self.s)
        result = tmp.connect_WPA_AP_backup(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn("Not connected.", result)

    #黑名单时选择多个Access list
    def test_029_manyaccesslist_blacklist(self):
        u"""黑名单时选择多个Access list(testlinkID:1517)"""
        log.debug("029")
        tmp3 = SettingsBusiness(self.s)
        ssh_pwd = tmp3.get_ssh_pwd()
        client_mac = tmp3.get_wlan_mac(data_basic["wlan_pc"])
        tmp = AccessListBusiness(self.s)
        result1, result2, result3 = tmp.check_manyaccesslist_blacklist(client_mac,
                data_ap['7610_mac'], data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic['7610_ip'],
                data_basic['sshUser'], ssh_pwd)
        self.assertTrue(result1)
        self.assertTrue(result2)
        self.assertTrue(result3)

    #黑名单从一个List修改为另一个list
    def test_030_change_accesslist(self):
        u"""黑名单从一个List修改为另一个list(testlinkID:1518)"""
        log.debug("030")
        #先only access list1
        #首先需要获取Access list1的id--ssid页面中选择access list是通过id
        tmp = AccessListBusiness(self.s)
        #获取Access list1的id
        list_info = tmp.get_list_info("Access list1")
        id1 = list_info['id']

        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_mac_filtering':"2",
                     'ssid_maclist_black':["%s"%id1]}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        result1 = tmp.connect_WPA_AP_backup(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        #再only access list2
        #获取Access list1的id
        list_info = tmp.get_list_info("Access list2")
        id2 = list_info['id']
        data_dict2 = {'ssid_mac_filtering':"2",
                     'ssid_maclist_black':["%s"%id2]}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict2)
        time.sleep(120)
        result2 = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn("Not connected.", result1)
        self.assertIn(data_wireless['all_ssid'], result2)

    #应用黑名单后从list中删除指定MAC地址
    def test_031_delete_mac_after_apply_blacklist(self):
        u"""应用黑名单后从list中删除指定MAC地址(testlinkID:1519)"""
        log.debug("031")
        #先only access list1
        #首先需要获取Access list1的id--ssid页面中选择access list是通过id
        tmp = AccessListBusiness(self.s)
        #获取Access list1的id
        list_info = tmp.get_list_info("Access list1")
        id1 = list_info['id']

        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_mac_filtering':"2",
                     'ssid_maclist_black':["%s"%id1]}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)

        #然后删除Access list1中的mac
        tmp.edit_list("Access list1", [])
        time.sleep(120)

        result1 = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        tmp3 = SettingsBusiness(self.s)
        ssh_pwd = tmp3.get_ssh_pwd()
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        #检查ap后台中，Blacklist是否生效
        result2 = tmp.check_Blacklist_cli(data_basic['7610_ip'],
                data_basic['sshUser'], ssh_pwd, client_mac)
        self.assertIn(data_wireless['all_ssid'], result1)
        self.assertFalse(result2)

    #重启后检查黑名单/白名单是否生效
    def test_032_check_reboot_ap_blacklist(self):
        u"""重启后检查黑名单/白名单是否生效(testlinkID:1520)"""
        log.debug("032")
        #access list1添加client mac地址
        tmp = AccessListBusiness(self.s)
        macs = []
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        macs.append(client_mac)
        tmp.edit_list("Access list1", macs)
        time.sleep(60)
        #重启7610
        tmp1 = APSBusiness(self.s)
        tmp1.reboot_one_ap(data_ap['7610_mac'])
        time.sleep(420)

        tmp3 = SettingsBusiness(self.s)
        ssh_pwd = tmp3.get_ssh_pwd()
        #检查ap后台中，Blacklist是否生效
        result1 = tmp.check_Blacklist_cli(data_basic['7610_ip'],
                data_basic['sshUser'], ssh_pwd, client_mac)
        #client连不上
        result2 = tmp.connect_WPA_AP_backup(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertTrue(result1)
        self.assertIn("Not connected.", result2)

    #Access list应用于白名单-1检查cli配置
    def test_033_apply_Access_list_whitelist(self):
        u"""Access list应用于白名单-1检查cli配置(testlinkID:1521-1)"""
        log.debug("033")
        #首先需要获取Access list1的id--ssid页面中选择access list是通过id
        tmp = AccessListBusiness(self.s)
        #获取Access list1的id
        list_info = tmp.get_list_info("Access list1")
        id1 = list_info['id']

        #然后在修改ssid1为白名单
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_mac_filtering':"1",
                     'ssid_maclist_white':["%s"%id1]}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        tmp3 = SettingsBusiness(self.s)
        ssh_pwd = tmp3.get_ssh_pwd()
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        #检查ap后台中，whitelist是否生效
        result = tmp.check_Whitelist_cli(data_basic['7610_ip'],
                data_basic['sshUser'], ssh_pwd, client_mac)
        self.assertTrue(result)

    #Access list应用于白名单-2该client能够连上
    def test_034_apply_Access_list_whitelist(self):
        u"""Access list应用于白名单-2该client能够连上(testlinkID:1521-2)"""
        log.debug("034")
        tmp = AccessListBusiness(self.s)
        result = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)

    #Access list应用于白名单-3其他client能够连上
    def test_035_apply_Access_list_whitelist(self):
        u"""Access list应用于白名单-3其他client能够连上(testlinkID:1521-3)"""
        log.debug("035")
        #修改Access list1为其他client
        tmp = AccessListBusiness(self.s)
        random_mac = tmp.randomMAC()
        macs = []
        macs.append(random_mac)
        tmp.edit_list("Access list1", macs)
        time.sleep(120)
        #使用其他client去连接，不能连接上
        result = tmp.connect_WPA_AP_backup(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn("Not connected.", result)

    #应用白名单后再添加MAC地址-1
    def test_036_add_mac_after_apply_whitelist(self):
        u"""应用白名单后再添加MAC地址-1(testlinkID:1522-1)"""
        log.debug("036")
        #Access list添加client mac
        #修改Access list1为其他client
        tmp = AccessListBusiness(self.s)
        random_mac = tmp.randomMAC()
        macs = []
        macs.append(random_mac)
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        macs.append(client_mac)
        tmp.edit_list("Access list1", macs)
        time.sleep(120)
        tmp3 = SettingsBusiness(self.s)
        ssh_pwd = tmp3.get_ssh_pwd()
        #检查ap后台中，whitelist是否生效
        result1 = tmp.check_Whitelist_cli(data_basic['7610_ip'],
                data_basic['sshUser'], ssh_pwd, client_mac)
        result2 = tmp.check_Whitelist_cli(data_basic['7610_ip'],
                data_basic['sshUser'], ssh_pwd, random_mac)
        self.assertTrue(result1)
        self.assertTrue(result2)

    #应用白名单后再添加MAC地址-2
    def test_037_add_mac_after_apply_whitelist(self):
        u"""应用白名单后再添加MAC地址-2(testlinkID:1522-2)"""
        log.debug("037")
        tmp = AccessListBusiness(self.s)
        result = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)

    #白名单时选择多个Access list
    def test_038_manyaccesslist_whitelist(self):
        u"""白名单时选择多个Access list(testlinkID:1523)"""
        log.debug("038")
        tmp3 = SettingsBusiness(self.s)
        ssh_pwd = tmp3.get_ssh_pwd()
        client_mac = tmp3.get_wlan_mac(data_basic["wlan_pc"])
        tmp = AccessListBusiness(self.s)
        result1, result2, result3 = tmp.check_manyaccesslist_whitelist(client_mac,
                data_ap['7610_mac'], data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic['7610_ip'],
                data_basic['sshUser'], ssh_pwd)
        self.assertTrue(result1)
        self.assertTrue(result2)
        self.assertTrue(result3)

    #应用白名单后从list中删除指定MAC地址
    def test_039_delete_mac_after_apply_whitelist(self):
        u"""应用白名单后从list中删除指定MAC地址(testlinkID:1524，1525)"""
        log.debug("039")
        #先only access list1
        #首先需要获取Access list1的id--ssid页面中选择access list是通过id
        tmp = AccessListBusiness(self.s)
        #获取Access list1的id
        list_info = tmp.get_list_info("Access list1")
        id1 = list_info['id']

        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_mac_filtering':"1",
                     'ssid_maclist_white':["%s"%id1]}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)

        #然后删除Access list1中的mac
        tmp.edit_list("Access list1", [])
        time.sleep(120)

        result1 = tmp.connect_WPA_AP_backup(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        tmp3 = SettingsBusiness(self.s)
        ssh_pwd = tmp3.get_ssh_pwd()
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        #检查ap后台中，Whitelist是否生效
        result2 = tmp.check_Whitelist_cli(data_basic['7610_ip'],
                data_basic['sshUser'], ssh_pwd, client_mac)
        self.assertIn("Not connected.", result1)
        self.assertFalse(result2)

    #检查多个access list中有重复的MAC地址时应用情况-1
    def test_040_manylist_have_same_mac(self):
        u"""检查多个access list中有重复的MAC地址时应用情况-1(testlinkID:1527-1)"""
        log.debug("040")
        #修改Access list
        tmp = AccessListBusiness(self.s)
        macs = []
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        macs.append(client_mac)
        tmp.edit_list("Access list1", macs)
        time.sleep(120)
        tmp.edit_list("Access list2", macs)
        time.sleep(120)
        #首先需要获取Access list1的id--ssid页面中选择access list是通过id
        #获取Access list1,2的id
        list_info = tmp.get_list_info("Access list1")
        id1 = list_info['id']
        list_info = tmp.get_list_info("Access list2")
        id2 = list_info['id']
        #两个list都应用于黑名单
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_mac_filtering':"2",
                     'ssid_maclist_black':["%s"%id1, "%s"%id2]}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        result1 = tmp.connect_WPA_AP_backup(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        tmp3 = SettingsBusiness(self.s)
        ssh_pwd = tmp3.get_ssh_pwd()
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        #检查ap后台中，Blacklist是否生效
        result2 = tmp.check_Blacklist_cli(data_basic['7610_ip'],
                data_basic['sshUser'], ssh_pwd, client_mac)
        self.assertIn("Not connected.", result1)
        self.assertTrue(result2)

    #检查多个access list中有重复的MAC地址时应用情况-2
    def test_041_manylist_have_same_mac(self):
        u"""检查多个access list中有重复的MAC地址时应用情况-2(testlinkID:1527-2)"""
        log.debug("041")
        #首先需要获取Access list1的id--ssid页面中选择access list是通过id
        #获取Access list1,2的id
        tmp = AccessListBusiness(self.s)
        list_info = tmp.get_list_info("Access list1")
        id1 = list_info['id']
        list_info = tmp.get_list_info("Access list2")
        id2 = list_info['id']
        #两个list都应用于白名单
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_mac_filtering':"1",
                     'ssid_maclist_white':["%s"%id1, "%s"%id2]}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        result1 = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        tmp3 = SettingsBusiness(self.s)
        ssh_pwd = tmp3.get_ssh_pwd()
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        #检查ap后台中，Whitelist是否生效
        result2 = tmp.check_Whitelist_cli(data_basic['7610_ip'],
                data_basic['sshUser'], ssh_pwd, client_mac)
        self.assertIn(data_wireless['all_ssid'], result1)
        self.assertTrue(result2)

    #白名单与Global Blacklist包含同一个MAC地址时的使用情况
    def test_042_Global_Blacklist_Whitelist_have_same_mac(self):
        u"""白名单与Global Blacklist包含同一个MAC地址时的使用情况(testlinkID:1528)"""
        log.debug("042")
        tmp = AccessListBusiness(self.s)
        #Global Blacklist中添加client mac
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        macs = []
        macs.append(client_mac)
        tmp.edit_Global_Blacklist_mac(macs)
        time.sleep(120)
        #首先需要获取Access list1的id--ssid页面中选择access list是通过id
        #获取Access list1的id
        list_info = tmp.get_list_info("Access list1")
        id1 = list_info['id']
        #Access list1都应用于白名单
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_mac_filtering':"1",
                     'ssid_maclist_white':["%s"%id1]}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        result1 = tmp.connect_WPA_AP_backup(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        tmp3 = SettingsBusiness(self.s)
        ssh_pwd = tmp3.get_ssh_pwd()
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        #检查ap后台中，Whitelist是否生效
        result2 = tmp.check_Whitelist_cli(data_basic['7610_ip'],
                data_basic['sshUser'], ssh_pwd, client_mac)
        self.assertIn("Not connected.", result1)
        self.assertFalse(result2)

    #将客户端的mac地址从global black list中添加或者删除，不影响白名单的使用
    def test_043_Global_Blacklist_delete_mac_check_Whitelist(self):
        u"""将客户端的mac地址从global black list中添加或者删除，不影响白名单的使用(testlinkID:1529)"""
        log.debug("043")
        #删除Global_Blacklist中的mac地址
        tmp = AccessListBusiness(self.s)
        tmp.set_Global_Blacklist_blank()
        time.sleep(120)
        result1 = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result1)

    #将客户端的mac地址从global black list中添加或者删除，不影响黑名单的使用
    def test_044_Global_Blacklist_delete_mac_check_Blacklist(self):
        u"""将客户端的mac地址从global black list中添加或者删除，不影响黑名单的使用(testlinkID:1530)"""
        log.debug("044")
        tmp = AccessListBusiness(self.s)
        #Global Blacklist中添加client mac
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        macs = []
        macs.append(client_mac)
        tmp.edit_Global_Blacklist_mac(macs)
        time.sleep(120)
        #首先需要获取Access list1的id--ssid页面中选择access list是通过id
        #获取Access list1的id
        list_info = tmp.get_list_info("Access list1")
        id1 = list_info['id']
        #Access list1都应用于黑名单
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_mac_filtering':"2",
                     'ssid_maclist_black':["%s"%id1]}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #再删除Global_Blacklist中的mac地址
        tmp.set_Global_Blacklist_blank()
        time.sleep(120)
        result1 = tmp.connect_WPA_AP_backup(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn("Not connected.", result1)

    #Disable MAC Filtering-1
    def test_045_disable_mac_filter(self):
        u"""Disable MAC Filtering-1(testlinkID:1531-1)"""
        log.debug("045")
        #access list2用在ssid2的白名单中
        tmp = AccessListBusiness(self.s)
        list_info = tmp.get_list_info("Access list2")
        id2 = list_info['id']
         #Access list2都应用ssid2的白名单
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_mac_filtering':"1",
                     'ssid_maclist_white':["%s"%id2]}
        tmp1.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid']+"-2",
                       encry_dict, data_dict)
        time.sleep(120)
        result1 = tmp.connect_WPA_AP_backup(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        result2 = tmp.connect_WPA_AP(data_wireless['all_ssid']+"-2",
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn("Not connected.", result1)
        self.assertIn(data_wireless['all_ssid']+"-2", result2)

    #Disable MAC Filtering-2
    def test_046_disable_mac_filter(self):
        u"""Disable MAC Filtering-2(testlinkID:1531-2)"""
        log.debug("046")
        #ssid1,ssid2都disable mac filter
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_mac_filtering':"0"}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        tmp1.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid']+"-2",
                       encry_dict, data_dict)
        time.sleep(120)
        result1 = tmp1.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        result2 = tmp1.connect_WPA_AP(data_wireless['all_ssid']+"-2",
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result1)
        self.assertIn(data_wireless['all_ssid']+"-2", result2)

    #验证开启白名单，选择多个列表，非列表的mac地址无法接入网络
    def test_047_check_mac_not_in_whitemanylist(self):
        u"""验证开启白名单，选择多个列表，非列表的mac地址无法接入网络(testlinkID:1532)"""
        log.debug("047")
        #list1,list2,list3都改为随机mac
        tmp = AccessListBusiness(self.s)
        for i in range(3):
            tmp.edit_list("Access list%s"%(i+1), [tmp.randomMAC()])
        time.sleep(120)
        #ssid1改为白名单，并选择这三个list
        #获取Access list的id
        list_info = tmp.get_list_info("Access list1")
        id1 = list_info['id']
        list_info = tmp.get_list_info("Access list2")
        id2 = list_info['id']
        list_info = tmp.get_list_info("Access list3")
        id3 = list_info['id']
        #然后在修改ssid1为白名单
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_mac_filtering':"1",
                     'ssid_maclist_white':["%s"%id1, "%s"%id2, "%s"%id3]}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #验证非列表的mac地址无法接入网络
        result1 = tmp.connect_WPA_AP_backup(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn("Not connected.", result1)

    #验证不同ssid同时开启白名单，互不影响
    def test_048_defferent_ssid_open_whitelist(self):
        u"""验证不同ssid同时开启白名单，互不影响(testlinkID:1533)"""
        log.debug("048")
        #修改list1,加入client的mac
        tmp = AccessListBusiness(self.s)
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        tmp.edit_list("Access list1", [client_mac])
        list_info = tmp.get_list_info("Access list1")
        id1 = list_info['id']
        list_info = tmp.get_list_info("Access list2")
        id2 = list_info['id']
        #ssid1，ssid2都开启白名单，ssid选择list1,ssid2选择list2
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict1 = {'ssid_mac_filtering':"1",
                     'ssid_maclist_white':["%s"%id1]}
        data_dict2 = {'ssid_mac_filtering':"1",
                     'ssid_maclist_white':["%s"%id2]}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict1)
        tmp1.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid']+"-2",
                       encry_dict, data_dict2)
        time.sleep(120)
        result1 = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        result2 = tmp.connect_WPA_AP_backup(data_wireless['all_ssid']+"-2",
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result1)
        self.assertIn("Not connected.", result2)

    #验证开启黑名单后，选择多个列表，列表里的mac地址不能接入网络
    def test_049_check_mac_in_blackmanylist(self):
        u"""验证开启黑名单后，选择多个列表，列表里的mac地址不能接入网络(testlinkID:1534)"""
        log.debug("049")
        #ssid1改为黑名单，并选择这三个list
        #获取Access list的id
        tmp = AccessListBusiness(self.s)
        list_info = tmp.get_list_info("Access list1")
        id1 = list_info['id']
        list_info = tmp.get_list_info("Access list2")
        id2 = list_info['id']
        list_info = tmp.get_list_info("Access list3")
        id3 = list_info['id']
        #然后在修改ssid1为黑名单
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_mac_filtering':"2",
                     'ssid_maclist_black':["%s"%id1, "%s"%id2, "%s"%id3]}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #验证非列表的mac地址无法接入网络
        result1 = tmp.connect_WPA_AP_backup(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn("Not connected.", result1)

    #验证不同ssid同时开启黑名单，互不影响
    def test_050_defferent_ssid_open_blacklist(self):
        u"""验证不同ssid同时开启黑名单，互不影响(testlinkID:1535)"""
        log.debug("050")
        #获取两个list的id
        tmp = AccessListBusiness(self.s)
        list_info = tmp.get_list_info("Access list1")
        id1 = list_info['id']
        list_info = tmp.get_list_info("Access list2")
        id2 = list_info['id']
        #ssid1，ssid2都开启黑名单，ssid选择list1,ssid2选择list2
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict1 = {'ssid_mac_filtering':"2",
                     'ssid_maclist_black':["%s"%id1]}
        data_dict2 = {'ssid_mac_filtering':"2",
                     'ssid_maclist_black':["%s"%id2]}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict1)
        tmp1.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid']+"-2",
                       encry_dict, data_dict2)
        time.sleep(120)
        result1 = tmp.connect_WPA_AP_backup(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        result2 = tmp.connect_WPA_AP(data_wireless['all_ssid']+"-2",
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn("Not connected.", result1)
        self.assertIn(data_wireless['all_ssid']+"-2", result2)

    #验证一个ssid开启白名单，另一个ssid开启黑名单，两个ssid互不影响
    def test_051_onessidwhite_onessidblack(self):
        u"""验证一个ssid开启白名单，另一个ssid开启黑名单，两个ssid互不影响(testlinkID:1536)"""
        log.debug("051")
        #获取两个list的id
        tmp = AccessListBusiness(self.s)
        list_info = tmp.get_list_info("Access list1")
        id1 = list_info['id']
        #ssid1开启白名单，ssid2开启黑名单，两个ssid都选择list1
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict1 = {'ssid_mac_filtering':"1",
                     'ssid_maclist_white':["%s"%id1]}
        data_dict2 = {'ssid_mac_filtering':"2",
                     'ssid_maclist_black':["%s"%id1]}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict1)
        tmp1.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid']+"-2",
                       encry_dict, data_dict2)
        time.sleep(120)
        result1 = tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        result2 = tmp.connect_WPA_AP_backup(data_wireless['all_ssid']+"-2",
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result1)
        self.assertIn("Not connected.", result2)

    #带vlan的ssid黑名单应用情况
    def test_052_vlan_blacklist(self):
        u"""带vlan的ssid黑名单应用情况(testlinkID:1537)"""
        log.debug("052")
        #获取list的id
        tmp = AccessListBusiness(self.s)
        list_info = tmp.get_list_info("Access list1")
        id1 = list_info['id']
        #修改ssid2为vlan2,开启黑名单
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_vlan':"1",
                     'ssid_vlanid':"2",
                     'ssid_mac_filtering':"2",
                     'ssid_maclist_black':["%s"%id1]}
        tmp1.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid']+"-2",
                       encry_dict, data_dict)
        time.sleep(120)
        result = tmp.connect_WPA_AP_backup(data_wireless['all_ssid']+"-2",
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn("Not connected.", result)

    #带vlan的ssid白名单应用情况
    def test_053_vlan_whitelist(self):
        u"""带vlan的ssid白名单应用情况(testlinkID:1538)"""
        log.debug("053")
        #获取list的id
        tmp = AccessListBusiness(self.s)
        list_info = tmp.get_list_info("Access list1")
        id1 = list_info['id']
        #修改ssid2为vlan2,开启白名单
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_vlan':"1",
                     'ssid_vlanid':"2",
                     'ssid_mac_filtering':"1",
                     'ssid_maclist_white':["%s"%id1]}
        tmp1.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid']+"-2",
                       encry_dict, data_dict)
        time.sleep(120)
        result = tmp.connect_WPA_AP(data_wireless['all_ssid']+"-2",
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid']+"-2", result)

    #多个AP的Global Blacklist应用情况
    def test_054_manyap_Global_Blacklist(self):
        u"""多个AP的Global Blacklist应用情况(testlinkID:1540)"""
        log.debug("054")
        #Global_Blacklist中加入client mac
        tmp = AccessListBusiness(self.s)
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        tmp.edit_Global_Blacklist_mac([client_mac])
        time.sleep(120)
        #关闭ssid2的mac filter,并加入7600,7600LR
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_vlan':"1",
                     'ssid_vlanid':"2",
                     'ssid_mac_filtering':"0",
                     'membership_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp1.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid']+"-2",
                       encry_dict, data_dict)
        time.sleep(120)
        result = tmp.connect_WPA_AP_backup(data_wireless['all_ssid']+"-2",
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn("Not connected.", result)

    #多个AP的黑名单应用情况-1
    def test_055_manyap_Blacklist(self):
        u"""多个AP的黑名单应用情况-1(testlinkID:1541-1)--bug"""
        log.debug("055")
        #清空Global_Blacklist
        tmp = AccessListBusiness(self.s)
        tmp.set_Global_Blacklist_blank()
        time.sleep(120)
        #获取list的id
        list_info = tmp.get_list_info("Access list1")
        id1 = list_info['id']
        #ssid2中加入带client的blacklist-list1
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_vlan':"1",
                     'ssid_vlanid':"2",
                     'ssid_mac_filtering':"2",
                     'ssid_maclist_black':["%s"%id1],
                     'membership_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp1.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid']+"-2",
                       encry_dict, data_dict)
        time.sleep(120)
        result = tmp.connect_WPA_AP_backup(data_wireless['all_ssid']+"-2",
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn("Not connected.", result)

    #多个AP的黑名单应用情况-2
    def test_056_manyap_Blacklist(self):
        u"""多个AP的黑名单应用情况-2(testlinkID:1541-2)"""
        log.debug("056")
        tmp = AccessListBusiness(self.s)
        list_info = tmp.get_list_info("Access list2")
        id2 = list_info['id']
        #ssid2中加入不带client的blacklist-list2
        time.sleep(120)
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_vlan':"1",
                     'ssid_vlanid':"2",
                     'ssid_mac_filtering':"2",
                     'ssid_maclist_black':["%s"%id2],
                     'membership_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp1.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid']+"-2",
                       encry_dict, data_dict)
        time.sleep(120)
        result = tmp.connect_WPA_AP(data_wireless['all_ssid']+"-2",
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid']+"-2", result)

    #多个AP的白名单应用情况-1
    def test_057_manyap_whitelist(self):
        u"""多个AP的白名单应用情况-1(testlinkID:1542-1)"""
        log.debug("057")
        tmp = AccessListBusiness(self.s)
        #获取list的id
        list_info = tmp.get_list_info("Access list1")
        id1 = list_info['id']
        #ssid2中加入带client的whitelist-list1
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_vlan':"1",
                     'ssid_vlanid':"2",
                     'ssid_mac_filtering':"1",
                     'ssid_maclist_white':["%s"%id1],
                     'membership_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp1.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid']+"-2",
                       encry_dict, data_dict)
        time.sleep(120)
        result = tmp.connect_WPA_AP(data_wireless['all_ssid']+"-2",
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid']+"-2", result)

    #多个AP的白名单应用情况-2
    def test_058_manyap_Whitelist(self):
        u"""多个AP的白名单应用情况-2(testlinkID:1542-2)"""
        log.debug("058")
        tmp = AccessListBusiness(self.s)
        list_info = tmp.get_list_info("Access list2")
        id2 = list_info['id']
        #ssid2中加入不带client的whitelist-list2
        time.sleep(120)
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_vlan':"1",
                     'ssid_vlanid':"2",
                     'ssid_mac_filtering':"1",
                     'ssid_maclist_white':["%s"%id2],
                     'membership_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp1.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid']+"-2",
                       encry_dict, data_dict)
        time.sleep(120)
        result = tmp.connect_WPA_AP_backup(data_wireless['all_ssid']+"-2",
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn("Not connected.", result)

    #多个AP应用多个Access list
    def test_059_manyap_Blacklist(self):
        u"""多个AP应用多个Access list-1(testlinkID:1543-1)"""
        log.debug("059")
        tmp = AccessListBusiness(self.s)
        #获取list的id
        list_info1 = tmp.get_list_info("Access list1")
        id1 = list_info1['id']
        list_info2 = tmp.get_list_info("Access list2")
        id2 = list_info2['id']
        #ssid2中加入list1,2,blacklist
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_vlan':"1",
                     'ssid_vlanid':"2",
                     'ssid_mac_filtering':"2",
                     'ssid_maclist_black':["%s"%id1, "%s"%id2],
                     'membership_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp1.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid']+"-2",
                       encry_dict, data_dict)
        time.sleep(120)
        tmp3 = SettingsBusiness(self.s)
        ssh_pwd = tmp3.get_ssh_pwd()
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        result1 = tmp.check_Blacklist_cli(data_basic['7600_ip'],
                data_basic['sshUser'], ssh_pwd, client_mac)
        result2 = tmp.check_Blacklist_cli(data_basic['7600lr_ip'],
                data_basic['sshUser'], ssh_pwd, client_mac)
        self.assertTrue(result1)
        self.assertTrue(result2)

    #多个AP应用多个Access list
    def test_060_manyap_Blacklist(self):
        u"""多个AP应用多个Access list-2(testlinkID:1543-2)"""
        log.debug("060")
        tmp = AccessListBusiness(self.s)
        #获取list的id
        list_info1 = tmp.get_list_info("Access list1")
        id1 = list_info1['id']
        list_info2 = tmp.get_list_info("Access list2")
        id2 = list_info2['id']
        #ssid2中加入list1,2,whitelist
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_vlan':"1",
                     'ssid_vlanid':"2",
                     'ssid_mac_filtering':"1",
                     'ssid_maclist_white':["%s"%id1, "%s"%id2],
                     'membership_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp1.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid']+"-2",
                       encry_dict, data_dict)
        time.sleep(120)
        tmp3 = SettingsBusiness(self.s)
        ssh_pwd = tmp3.get_ssh_pwd()
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        result1 = tmp.check_Whitelist_cli(data_basic['7600_ip'],
                data_basic['sshUser'], ssh_pwd, client_mac)
        result2 = tmp.check_Whitelist_cli(data_basic['7600lr_ip'],
                data_basic['sshUser'], ssh_pwd, client_mac)
        self.assertTrue(result1)
        self.assertTrue(result2)

    #删除block client所在的ap,查看client被block的情况是否同步到该network的所有ssid
    def test_061_delete_blockap_check_other_ssid(self):
        u"""删除block client所在的ap,查看client被block的情况是否同步到该network的所有ssid(testlinkID:1544)"""
        log.debug("061")
        #先将两个ssid的mac filter都禁用
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict1 = {'ssid_mac_filtering':"0"}
        data_dict2 = {'ssid_mac_filtering':"0",
                     'ssid_vlan':"1",
                     'ssid_vlanid':"2",
                     'membership_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict1)
        tmp1.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid']+"-2",
                       encry_dict, data_dict2)
        time.sleep(120)
        #无线网卡连接ssid1
        tmp1.connect_DHCP_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        time.sleep(120)
        tmp1.dhcp_release_wlan_backup(data_basic["wlan_pc"])
        #block 客户端
        tmp2 = Clients_Business(self.s)
        client_mac = tmp2.get_wlan_mac(data_basic["wlan_pc"])
        tmp2.set_client_block(client_mac)
        time.sleep(120)
        #删除ssid1中的ap，即7610
        data_dict3 = {'removed_macs': "%s"%(data_ap['7610_mac'].upper())}
        tmp1.edit_ssid("", data_wireless['all_ssid'],
                       encry_dict, data_dict3)
        time.sleep(120)
        #无线网卡无法连接ssid2
        result = tmp2.connect_WPA_AP_backup(data_wireless['all_ssid']+"-2",
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn("Not connected.", result)


    #被某个ssid设置黑名单的客户端连接到其它ssid的情况
    def test_062_mac_in_blacklist_connect_other_ssid(self):
        u"""被某个ssid设置黑名单的客户端连接到其它ssid的情况(testlinkID:1546)"""
        log.debug("062")
        #清空Global_Blacklist
        tmp = AccessListBusiness(self.s)
        tmp.set_Global_Blacklist_blank()
        time.sleep(120)
        #获取list的id
        list_info = tmp.get_list_info("Access list1")
        id1 = list_info['id']
        #ssid1中加入带client的blacklist-list1
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_mac_filtering':"2",
                     'ssid_maclist_black':["%s"%id1],
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡无法连接ssid2
        result = tmp.connect_WPA_AP(data_wireless['all_ssid']+"-2",
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid']+"-2", result)

    #WEP加密时黑白名单应用情况-1
    def test_063_wep_blacklist(self):
        u"""WEP加密时黑白名单应用情况-1(testlinkID:1553-1)"""
        log.debug("063")
        #获取list的id
        tmp = AccessListBusiness(self.s)
        list_info = tmp.get_list_info("Access list1")
        id1 = list_info['id']
        #修改ssid1为wep加密-blacklist
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "0",
                    'ssid_wep_key': data_wireless['wep64']}
        data_dict = {'ssid_mac_filtering':"2",
                     'ssid_maclist_black':["%s"%id1]}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_WEP_AP_backup(data_wireless['all_ssid'],
                data_wireless['wep64'], data_basic["wlan_pc"])
        self.assertIn("Not connected.", result)

    #WEP加密时黑白名单应用情况-2
    def test_064_wep_whitelist(self):
        u"""WEP加密时黑白名单应用情况-2(testlinkID:1553-2)"""
        log.debug("064")
        #获取list的id
        tmp = AccessListBusiness(self.s)
        list_info = tmp.get_list_info("Access list1")
        id1 = list_info['id']
        #修改ssid1为wep加密-whitelist
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "0",
                    'ssid_wep_key': data_wireless['wep64']}
        data_dict = {'ssid_mac_filtering':"1",
                     'ssid_maclist_white':["%s"%id1]}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_WEP_AP(data_wireless['all_ssid'],
                data_wireless['wep64'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)

    #WEP加密时黑白名单应用情况-3
    def test_065_wep_blacklist(self):
        u"""WEP加密时黑白名单应用情况-3(testlinkID:1553-3)"""
        log.debug("065")
        #获取list的id
        tmp = AccessListBusiness(self.s)
        list_info = tmp.get_list_info("Access list2")
        id2 = list_info['id']
        #修改ssid1为wep加密-blacklist
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "0",
                    'ssid_wep_key': data_wireless['wep64']}
        data_dict = {'ssid_mac_filtering':"2",
                     'ssid_maclist_black':["%s"%id2]}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_WEP_AP(data_wireless['all_ssid'],
                data_wireless['wep64'], data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)

    #WEP加密时黑白名单应用情况-4
    def test_066_wep_whitelist(self):
        u"""WEP加密时黑白名单应用情况-4(testlinkID:1553-4)"""
        log.debug("066")
        #获取list的id
        tmp = AccessListBusiness(self.s)
        list_info = tmp.get_list_info("Access list2")
        id2 = list_info['id']
        #修改ssid1为wep加密-whitelist
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "0",
                    'ssid_wep_key': data_wireless['wep64']}
        data_dict = {'ssid_mac_filtering':"1",
                     'ssid_maclist_white':["%s"%id2]}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_WEP_AP_backup(data_wireless['all_ssid'],
                data_wireless['wep64'], data_basic["wlan_pc"])
        self.assertIn("Not connected.", result)

    #Open加密方式时黑白名单应用情况-1
    def test_067_open_blacklist(self):
        u"""Open加密方式时黑白名单应用情况-1(testlinkID:1554-1)"""
        log.debug("067")
        #获取list的id
        tmp = AccessListBusiness(self.s)
        list_info = tmp.get_list_info("Access list1")
        id1 = list_info['id']
        #修改ssid1为open加密-blacklist
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "4"}
        data_dict = {'ssid_mac_filtering':"2",
                     'ssid_maclist_black':["%s"%id1]}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_NONE_AP_backup(data_wireless['all_ssid'],
                data_basic["wlan_pc"])
        self.assertIn("Not connected.", result)

    #Open加密方式时黑白名单应用情况-2
    def test_068_open_whitelist(self):
        u"""Open加密方式时黑白名单应用情况-2(testlinkID:1554-2)"""
        log.debug("068")
        #获取list的id
        tmp = AccessListBusiness(self.s)
        list_info = tmp.get_list_info("Access list1")
        id1 = list_info['id']
        #修改ssid1为open加密-whitelist
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "4"}
        data_dict = {'ssid_mac_filtering':"1",
                     'ssid_maclist_white':["%s"%id1]}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_NONE_AP(data_wireless['all_ssid'],
                data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)

    #open加密时黑白名单应用情况-3
    def test_069_open_blacklist(self):
        u"""open加密时黑白名单应用情况-3(testlinkID:1554-3)"""
        log.debug("069")
        #获取list的id
        tmp = AccessListBusiness(self.s)
        list_info = tmp.get_list_info("Access list2")
        id2 = list_info['id']
        #修改ssid1为open加密-blacklist
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "4"}
        data_dict = {'ssid_mac_filtering':"2",
                     'ssid_maclist_black':["%s"%id2]}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_NONE_AP(data_wireless['all_ssid'],
                data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)

    #open加密时黑白名单应用情况-4
    def test_070_open_whitelist(self):
        u"""open加密时黑白名单应用情况-4(testlinkID:1554-4)"""
        log.debug("070")
        #获取list的id
        tmp = AccessListBusiness(self.s)
        list_info = tmp.get_list_info("Access list2")
        id2 = list_info['id']
        #修改ssid1为open加密-whitelist
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "4"}
        data_dict = {'ssid_mac_filtering':"1",
                     'ssid_maclist_white':["%s"%id2]}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_NONE_AP_backup(data_wireless['all_ssid'],
                data_basic["wlan_pc"])
        self.assertIn("Not connected.", result)

    #802.1X加密方式时黑白名单应用情况-1
    def test_071_8021x_blacklist(self):
        u"""802.1X加密方式时黑白名单应用情况-1(testlinkID:1556-1)"""
        log.debug("071")
        #获取list的id
        tmp = AccessListBusiness(self.s)
        list_info = tmp.get_list_info("Access list1")
        id1 = list_info['id']
        #修改ssid1为802.1x加密-blacklist
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']
                      }
        data_dict = {'ssid_mac_filtering':"2",
                     'ssid_maclist_black':["%s"%id1]}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_8021x_AP_backup(data_wireless['all_ssid'],
                data_basic['radius_usename'], data_basic['radius_password'],
                data_basic["wlan_pc"])
        self.assertIn("Not connected.", result)

    #802.1X加密方式时黑白名单应用情况-2
    def test_072_8021x_whitelist(self):
        u"""802.1X加密方式时黑白名单应用情况-2(testlinkID:1556-2)"""
        log.debug("072")
        #获取list的id
        tmp = AccessListBusiness(self.s)
        list_info = tmp.get_list_info("Access list1")
        id1 = list_info['id']
        #修改ssid1为802.1x加密-whitelist
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']
                      }
        data_dict = {'ssid_mac_filtering':"1",
                     'ssid_maclist_white':["%s"%id1]}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_8021x_AP(data_wireless['all_ssid'],
                data_basic['radius_usename'], data_basic['radius_password'],
                data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)

    #802.1X加密方式时黑白名单应用情况-3
    def test_073_8021x_blacklist(self):
        u"""802.1X加密方式时黑白名单应用情况-3(testlinkID:1556-3)"""
        log.debug("073")
        #获取list的id
        tmp = AccessListBusiness(self.s)
        list_info = tmp.get_list_info("Access list2")
        id2 = list_info['id']
        #修改ssid1为802.1x加密-blacklist
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']
                      }
        data_dict = {'ssid_mac_filtering':"2",
                     'ssid_maclist_black':["%s"%id2]}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_8021x_AP(data_wireless['all_ssid'],
                data_basic['radius_usename'], data_basic['radius_password'],
                data_basic["wlan_pc"])
        self.assertIn(data_wireless['all_ssid'], result)

    #802.1X加密方式时黑白名单应用情况-4
    def test_074_8021x_whitelist(self):
        u"""802.1X加密方式时黑白名单应用情况-4(testlinkID:1556-4)"""
        log.debug("070")
        #获取list的id
        tmp = AccessListBusiness(self.s)
        list_info = tmp.get_list_info("Access list2")
        id2 = list_info['id']
        #修改ssid1为802.1x加密-whitelist
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "1",
                    'ssid_radius_acct_port': "1813",
                    'ssid_radius_port': "1812",
                    'ssid_radius_secret': data_basic['radius_secrect'],
                    'ssid_radius_server': data_basic['radius_addr']
                      }
        data_dict = {'ssid_mac_filtering':"1",
                     'ssid_maclist_white':["%s"%id2]}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #无线网卡连接
        result = tmp.connect_8021x_AP_backup(data_wireless['all_ssid'],
                data_basic['radius_usename'], data_basic['radius_password'],
                data_basic["wlan_pc"])
        self.assertIn("Not connected.", result)

    #删除ap，并恢复cloud的初始环境
    def test_075_reset_cloud(self):
        u"""删除ap，并恢复cloud的初始环境"""
        log.debug("075")
        #删除ssid2
        tmp1 = SSIDSBusiness(self.s)
        tmp1.dhcp_release_wlan_backup(data_basic['wlan_pc'])
        tmp1.disconnect_ap()
        tmp1.delete_ssid(data_wireless['all_ssid']+"-2")
        time.sleep(120)
        #测试完后恢复初始环境
        #1.修改ap的ssid为GWN-Cloud
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid': "GWN-Cloud",
                     'ssid_ssid_band': "",
                     'ssid_mac_filtering':"0"}
        tmp1.edit_ssid("", data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #删除多有access list
        tmp2 = AccessListBusiness(self.s)
        tmp2.delete_list("Access list1")
        tmp2.delete_list("Access list2")
        tmp2.delete_list("Access list3")
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
