#coding=utf-8
#作者：曾祥卫
#时间：2018.05.03
#描述：Network-Clients用例集，调用clients_business

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
log = Log("clients")


data_basic = data.data_basic()
data_login = data.data_login()
data_wireless = data.data_wireless()
data_ng = data.data_networkgroup()
data_ap = data.data_AP()
data_client = data.data_Client()




class TestClients(unittest.TestCase):
    u"""测试Network-Clients的用例集(runtime:1.45h)"""
    def setUp(self):
        self.s = requests.session()
        tmp = Clients_Business(self.s)
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

    #用户数量统计
    def test_002_clients_count(self):
        u"""用户数量统计(testlinkID:1380,1381)"""
        log.debug("002")
        #修改ssid
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
        tmp = Clients_Business(self.s)
        #无线网卡连接ap
        tmp.connect_DHCP_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        #使用无线网卡ping internet 1分钟
        tmp.set_wlan_ping_internet_1min(data_basic['lan_pc'])
        #等待10分钟ap上传数据到cloud
        time.sleep(600)
        tmp.dhcp_release_wlan(data_basic["wlan_pc"])
        client_count = tmp.get_current_5mins_clients_count("1d")
        self.assertEqual(client_count, 1)

    #选择特定的ssid，显示当前AP的用户数量统计
    def test_003_one_ssid_clients_count(self):
        u"""选择特定的ssid，显示当前AP的用户数量统计(testlinkID:1382)"""
        log.debug("003")
        #获取默认ssid的id
        tmp1 = SSIDSBusiness(self.s)
        ssidid = tmp1.get_ssid_id(data_wireless['all_ssid'])
        tmp = Clients_Business(self.s)
        client_count = tmp.get_one_ssid_current_5mins_clients_count("1d", ssidid)
        self.assertEqual(client_count, 1)

    #检查2 hour的client count统计数据是否正确
    def test_004_client_count_2h(self):
        u"""检查2 hour的client count统计数据是否正确(testlinkID:1392)"""
        log.debug("004")
        tmp = Clients_Business(self.s)
        client_count = tmp.get_current_5mins_clients_count("2h")
        self.assertEqual(client_count, 1)

    #检查1 day的client count统计数据是否正确
    def test_005_client_count_1d(self):
        u"""检查1 day的client count统计数据是否正确(testlinkID:1393)"""
        log.debug("005")
        tmp = Clients_Business(self.s)
        client_count = tmp.get_current_5mins_clients_count("1d")
        self.assertEqual(client_count, 1)

    #检查2 hour的bandwidth usage统计数据是否正确
    def test_006_chart_ssid_bandwidth_2h(self):
        u"""检查2 hour的bandwidth usage统计数据是否正确(testlinkID:1401)"""
        log.debug("006")
        #修改ssid为5G
        tmp1 = SSIDSBusiness(self.s)
        #修改为5G
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_band': "5"}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)
        #AP 下载流量-10M
        tmp2 = APSBusiness(self.s)
        tmp2.run_AP_download(data_wireless['all_ssid'],
                          data_wireless['short_wpa'],
                          data_basic['wlan_pc'],
                          data_basic['lan_pc'])
        #等待6分钟
        time.sleep(360)
        tmp = Clients_Business(self.s)
        ssid_bw = tmp.check_chart_ssid_bandwidth("2h")
        self.assertTrue(ssid_bw)

    #检查1 day的bandwidth usage统计数据是否正确
    def test_007_chart_ssid_bandwidth_1d(self):
        u"""检查1 day的bandwidth usage统计数据是否正确(testlinkID:1402)"""
        log.debug("007")
        tmp = Clients_Business(self.s)
        ssid_bw = tmp.check_chart_ssid_bandwidth("1d")
        self.assertTrue(ssid_bw)

    #验证客户端状态信息正确-在线
    def test_008_status_client_online(self):
        u"""验证客户端状态信息正确-在线(testlinkID:1407-1)"""
        log.debug("008")
        tmp = Clients_Business(self.s)
        #客户端-状态，获取第一个客户端的信息
        client_info = tmp.get_first_client_info()
        client_mac = client_info['clientId']
        wlan_mac = tmp.get_wlan_mac(data_basic['wlan_pc']).upper()
        self.assertEqual(client_mac, wlan_mac)

    #验证客户端状态信息正确-离线
    def test_009_status_client_offline(self):
        u"""验证客户端状态信息正确-离线(testlinkID:1407-2)"""
        log.debug("009")
        tmp = Clients_Business(self.s)
        #断开无线
        tmp.disconnect_ap()
        time.sleep(180)
        #客户端-状态，获取客户端的总数
        client_total = tmp.get_client_total()
        self.assertEqual(client_total, 0)

    #验证客户端mac信息正确
    def test_010_client_mac(self):
        u"""验证客户端mac信息正确(testlinkID:1408)"""
        log.debug("010")

        #修改ssid改为7600
        tmp1 = SSIDSBusiness(self.s)
        #修改为5G
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_band': "5",
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp1.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)

        tmp = Clients_Business(self.s)
        tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        time.sleep(120)
        # tmp.dhcp_release_wlan(data_basic["wlan_pc"])
        # #使用用户名密码，带着cookie登录cloud，并返回响应数据
        # tmp.webLogin(data_basic['cloud_user'], data_basic['cloud_pwd'])
        #客户端-状态，获取第一个客户端的信息
        client_info = tmp.get_first_client_info()
        client_mac = client_info['clientId']
        wlan_mac = tmp.get_wlan_mac(data_basic['wlan_pc']).upper()
        self.assertEqual(client_mac, wlan_mac)

    #验证客户端ip地址信息
    def test_011_client_ip(self):
        u"""验证客户端ip地址信息(testlinkID:1410)"""
        log.debug("011")
        tmp = Clients_Business(self.s)
        #客户端-状态，获取第一个客户端的信息
        client_info = tmp.get_first_client_info()
        client_ip = client_info['ipv4']
        self.assertIn("192.168.1", client_ip)

    #实时客户端download流量统计
    def test_012_client_download(self):
        u"""实时客户端download流量统计(testlinkID:1411)"""
        log.debug("012")
        tmp = Clients_Business(self.s)
        #客户端-状态，获取第一个客户端的信息
        client_info = tmp.get_first_client_info()
        client_download = client_info['rxBytes']
        #下载流量大于5M
        self.assertGreaterEqual(client_download, (5*1024*1024))

    #实时客户端upload流量统计
    def test_013_client_upload(self):
        u"""实时客户端upload流量统计(testlinkID:1412)"""
        log.debug("013")
        #修改ssid改为7610
        tmp1 = SSIDSBusiness(self.s)
        #修改为5G
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_band': "5",
                    'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(120)

        #AP 下载流量-10M
        tmp2 = APSBusiness(self.s)
        tmp2.run_AP_upload(data_wireless['all_ssid'],
                          data_wireless['short_wpa'],
                          data_basic['wlan_pc'],
                          data_basic['lan_pc'])
        #等待6分钟
        time.sleep(360)
        tmp = Clients_Business(self.s)
        #客户端-状态，获取第一个客户端的信息
        client_info = tmp.get_first_client_info()
        client_up = client_info['txBytes']
        #上传流量大于5M
        self.assertGreaterEqual(client_up, (5*1024*1024))

    #实时客户端上下行总流量
    def test_014_client_total(self):
        u"""实时客户端上下行总流量(testlinkID:1413)"""
        log.debug("014")
        tmp = Clients_Business(self.s)
        #客户端-状态，获取第一个客户端的信息
        client_info = tmp.get_first_client_info()
        client_total = client_info['totalBytes']
        #总流量大于10M
        self.assertGreaterEqual(client_total, (10*1024*1024))

    #客户端关联的AP mac地址信息核对
    def test_015_client_associate_AP_mac(self):
        u"""客户端关联的AP mac地址信息核对(testlinkID:1415)"""
        log.debug("015")
        tmp = Clients_Business(self.s)
        #客户端-状态，获取第一个客户端的信息
        client_info = tmp.get_first_client_info()
        AP_Mac = client_info['apId']
        self.assertIn(data_ap['7610_mac'].upper(), AP_Mac)

    #切换ssid后的client流量
    def test_016_client_total_change_ssid(self):
        u"""切换ssid后的client流量(testlinkID:1414)"""
        log.debug("016")
        #新建ssid2并加入7600ap中
        tmp2 = SSIDSBusiness(self.s)
        tmp2.add_ssid(data_ap['7600_mac'], data_wireless['all_ssid']+"-2",
                     data_wireless['short_wpa'])
        time.sleep(120)
        #无线网卡连接ssid2
        tmp = Clients_Business(self.s)
        tmp.connect_WPA_AP(data_wireless['all_ssid']+"-2",
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        time.sleep(120)
        # tmp.dhcp_release_wlan(data_basic["wlan_pc"])
        #客户端-状态，获取第一个客户端的信息
        # #使用用户名密码，带着cookie登录cloud，并返回响应数据
        # tmp.webLogin(data_basic['cloud_user'], data_basic['cloud_pwd'])
        client_info = tmp.get_first_client_info()
        client_total = client_info['totalBytes']
        #总流量小于1M
        self.assertLessEqual(client_total, (1*1024*1024))

    #客户端切换连接AP后，列表中显示AP的mac地址信息要有相应的更新
    def test_017_client_change_associate_AP_mac(self):
        u"""客户端切换连接AP后，列表中显示AP的mac地址信息要有相应的更新(testlinkID:1416)"""
        log.debug("017")
        tmp = Clients_Business(self.s)
        #客户端-状态，获取第一个客户端的信息
        # tmp.connect_WPA_AP(data_wireless['all_ssid']+"-2",
        #          data_wireless['short_wpa'], data_basic["wlan_pc"])
        # time.sleep(120)
        client_info = tmp.get_first_client_info()
        AP_Mac = client_info['apId']
        self.assertIn(data_ap['7600_mac'].upper(), AP_Mac)

    #radio信息核对
    def test_018_client_radio_2g4(self):
        u"""radio信息核对-2.4G(testlinkID:1417-1)"""
        log.debug("018")
        #修改ssid2为2.4g
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_band': "2"}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid']+"-2",
                       encry_dict, data_dict)
        time.sleep(120)
        tmp = Clients_Business(self.s)
        tmp.connect_WPA_AP(data_wireless['all_ssid']+"-2",
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        time.sleep(120)
        # tmp.dhcp_release_wlan(data_basic["wlan_pc"])
        #客户端-状态，获取第一个客户端的信息
        # #使用用户名密码，带着cookie登录cloud，并返回响应数据
        # tmp.webLogin(data_basic['cloud_user'], data_basic['cloud_pwd'])
        client_info = tmp.get_first_client_info()
        channelClass = client_info['channelClass']
        self.assertEqual(channelClass, 2)

    #radio信息核对
    def test_019_client_radio_5g(self):
        u"""radio信息核对-2.4G(testlinkID:1417-2)"""
        log.debug("019")
        #修改ssid2为5g
        tmp2 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_band': "5"}
        tmp2.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid']+"-2",
                       encry_dict, data_dict)
        time.sleep(120)
        tmp = Clients_Business(self.s)
        tmp.connect_WPA_AP(data_wireless['all_ssid']+"-2",
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        time.sleep(120)
        # tmp.dhcp_release_wlan(data_basic["wlan_pc"])
        #客户端-状态，获取第一个客户端的信息
        # #使用用户名密码，带着cookie登录cloud，并返回响应数据
        # tmp.webLogin(data_basic['cloud_user'], data_basic['cloud_pwd'])
        client_info = tmp.get_first_client_info()
        channelClass = client_info['channelClass']
        self.assertEqual(channelClass, 5)

    #验证client的ssid信息
    def test_020_client_connect_ssid(self):
        u"""验证client的ssid信息(testlinkID:1418)"""
        log.debug("020")
        tmp = Clients_Business(self.s)
        # tmp.connect_WPA_AP(data_wireless['all_ssid']+"-2",
        #          data_wireless['short_wpa'], data_basic["wlan_pc"])
        # time.sleep(120)
        #客户端-状态，获取第一个客户端的信息
        client_info = tmp.get_first_client_info()
        AP_ssid = client_info['ssid']
        self.assertEqual(AP_ssid, data_wireless['all_ssid']+"-2")

    #验证client切换ssid后的ssid信息显示
    def test_021_client_change_connect_ssid(self):
        u"""验证client的ssid信息(testlinkID:1419)"""
        log.debug("021")
        #client切换ssid
        tmp = Clients_Business(self.s)
        tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        time.sleep(120)
        # tmp.dhcp_release_wlan(data_basic["wlan_pc"])
        #客户端-状态，获取第一个客户端的信息
        # #使用用户名密码，带着cookie登录cloud，并返回响应数据
        # tmp.webLogin(data_basic['cloud_user'], data_basic['cloud_pwd'])
        client_info = tmp.get_first_client_info()
        AP_ssid = client_info['ssid']
        self.assertEqual(AP_ssid, data_wireless['all_ssid'])

    #block客户端
    def test_022_block_client(self):
        u"""block客户端(testlinkID:1427)"""
        log.debug("022")
        #block 客户端
        tmp = Clients_Business(self.s)
        client_mac = tmp.get_wlan_mac(data_basic["wlan_pc"])
        tmp.set_client_block(client_mac)
        time.sleep(120)
        #获取Global Blacklist中的mac地址
        tmp2 = AccessListBusiness(self.s)
        Global_Blacklist = tmp2.get_Global_Blacklist_mac()
        #把Global Blacklist中的mac地址清空
        tmp2.set_Global_Blacklist_blank()
        self.assertIn(client_mac.upper(), Global_Blacklist)

    #设置信道，客户端连接后，信道信息核对
    def test_023_check_channel(self):
        u"""设置信道，客户端连接后，信道信息核对(testlinkID:1448)"""
        log.debug("023")
        #修改7610的5G信道为157
        tmp1 = APSBusiness(self.s)
        tmp1.edit_ap(data_ap['7610_mac'], {'ap_5g_channel': "157"})
        time.sleep(120)
        tmp = Clients_Business(self.s)
        tmp.connect_WPA_AP(data_wireless['all_ssid'],
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        time.sleep(120)
        # tmp.dhcp_release_wlan(data_basic["wlan_pc"])
        # #客户端-状态，获取第一个客户端的信息
        # #使用用户名密码，带着cookie登录cloud，并返回响应数据
        # tmp.webLogin(data_basic['cloud_user'], data_basic['cloud_pwd'])
        client_info = tmp.get_first_client_info()
        channel = client_info['channel']
        self.assertEqual(channel, 157)

    #更改client所在的ssid名称后显示
    def test_024_modify_ssid(self):
        u"""更改client所在的ssid名称后显示(testlinkID:1452)"""
        log.debug("024")
        #修改ssid2的ssid
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid': data_wireless['all_ssid']+"-3"}
        tmp1.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid']+"-2",
                       encry_dict, data_dict)
        time.sleep(120)
        tmp = Clients_Business(self.s)
        tmp.connect_WPA_AP(data_wireless['all_ssid']+"-3",
                data_wireless['short_wpa'], data_basic["wlan_pc"])
        time.sleep(120)
        # tmp.dhcp_release_wlan(data_basic["wlan_pc"])
        #客户端-状态，获取第一个客户端的信息
        # #使用用户名密码，带着cookie登录cloud，并返回响应数据
        # tmp.webLogin(data_basic['cloud_user'], data_basic['cloud_pwd'])
        client_info = tmp.get_first_client_info()
        AP_ssid = client_info['ssid']
        #删除ssid2
        tmp1.delete_ssid(data_wireless['all_ssid']+"-3")
        self.assertEqual(AP_ssid, data_wireless['all_ssid']+"-3")


    #删除ap，并恢复cloud的初始环境
    def test_025_reset_cloud(self):
        u"""删除ap，并恢复cloud的初始环境"""
        log.debug("025")
        #测试完后恢复初始环境
        #1.修改ap的ssid为GWN-Cloud
        tmp1 = SSIDSBusiness(self.s)
        tmp1.dhcp_release_wlan(data_basic['wlan_pc'])
        tmp1.disconnect_ap()
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid': "GWN-Cloud",
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
