#coding=utf-8
#作者：曾祥卫
#时间：2018.05.31
#描述：Network-Access Control-Time Policy用例集，调用TimePolcy_business

import unittest, time, subprocess
from access_points.aps_business import APSBusiness
from system.settings.settings_business import SettingsBusiness
from ssids.ssids_business import SSIDSBusiness
from clients.clients_business import Clients_Business
from access_control.access_list.accesslist_business import AccessListBusiness
from access_control.time_policy.timepolicy_business import TimePolicyBusiness
from data import data
from connect.ssh import SSH
from data.logfile import Log
import requests
log = Log("timepolicy")


data_basic = data.data_basic()
data_login = data.data_login()
data_wireless = data.data_wireless()
data_ng = data.data_networkgroup()
data_ap = data.data_AP()
data_client = data.data_Client()




class TestTimePolicy(unittest.TestCase):
    u"""测试Network-Access Control-Time Policy的用例集(runtime:*h)"""
    def setUp(self):
        self.s = requests.session()
        tmp = TimePolicyBusiness(self.s)
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

    #Connection Time单位选择m（分钟）功能测试(Enable勾选)
    def test_002_check_connection_m_time_function(self):
        u"""Connection Time单位选择m（分钟）功能测试(Enable勾选)(testlink_ID:1589)"""
        log.debug("002")
        #新建一个策略time policy1,连接时间2分钟，重置时间每天23点
        tmp = TimePolicyBusiness(self.s)
        #断开无线网卡的连接
        tmp.disconnect_ap()
        data_dict = {'status': 1,
                    'reconnectType': 1,
                     'resetDay': 1,
                     'resetHour': "23",
                     'hour': "24",
                     'resetTimeType': "AM",
                     'timezone': "Etc/GMT",
                     'connectionTimeMap': {'d': "0", 'h': "0", 'm': "2"},
                     'connectionTimeoutMap': {'d': "", 'h': "", 'm': ""}
                     }
        tmp.add_timepolicy("time policy1", data_dict)
        #获取时间策略的id
        timepolicy_id = tmp.get_timepolicy_id("time policy1")

        #修改ssid1的ssid，并开启时间策略，并选择time policy1
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict1 = {'ssid_ssid': data_wireless['all_ssid'],
                    'ssid_timed_client_policy': "%s"%timepolicy_id,
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp1.edit_ssid(data_ap['7600_mac'], 'GWN-Cloud',
                       encry_dict, data_dict1)
        time.sleep(120)

        #先修改ap的系统时间为01:00:00
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7600_ip'], ssh_pwd)
        ssh.ssh_cmd(data_basic['sshUser'], "date -s 01:00:00")
        #无线网卡连接
        tmp1.connect_DHCP_WPA_AP(data_wireless['all_ssid'],
            data_wireless['short_wpa'], data_basic['wlan_pc'])
        #等待3分钟
        time.sleep(240)
        #判断AP是否依然连接
        result = subprocess.check_output("iw dev %s link"%data_basic['wlan_pc'], shell=True)
        print result
        tmp1.dhcp_release_wlan(data_basic['wlan_pc'])
        #断开无线网卡的连接
        tmp.disconnect_ap()
        #释放被禁的客户端
        client_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        tmp.release_restrict_mac(client_mac)
        time.sleep(60)
        self.assertIn("Not connected.", result)

    #Connection Time单位选择h功能测试（Enabled勾选）
    def test_003_check_connection_time_h_function(self):
        u"""Connection Time单位选择h功能测试（Enabled勾选）(testlink_ID:1500)"""
        log.debug("003")
        tmp = TimePolicyBusiness(self.s)
        # #断开无线网卡的连接
        # tmp.disconnect_ap()
        # #释放被禁的客户端
        # client_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        # tmp.release_restrict_mac(client_mac)
        # time.sleep(60)
        #新增策略time policy2,连接时间5h，重置时间每天23点
        data_dict = {'status': 1,
                    'reconnectType': 1,
                     'resetDay': 1,
                     'resetHour': "23",
                     'hour': "24",
                     'resetTimeType': "AM",
                     'timezone': "Etc/GMT",
                     'connectionTimeMap': {'d': "0", 'h': "5", 'm': "0"},
                     'connectionTimeoutMap': {'d': "", 'h': "", 'm': ""}
                     }
        tmp.add_timepolicy("time policy2", data_dict)
        #获取时间策略的id
        timepolicy_id = tmp.get_timepolicy_id("time policy2")

        #修改ssid1的ssid，并开启时间策略，并选择time policy2
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict1 = {'ssid_timed_client_policy': "%s"%timepolicy_id}
        tmp1.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict1)
        time.sleep(120)
        #先修改ap的系统时间为01:00:00
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7600_ip'], ssh_pwd)
        ssh.ssh_cmd(data_basic['sshUser'], "date -s 01:00:00")
        #无线网卡连接
        tmp.connect_DHCP_WPA_AP(data_wireless['all_ssid'],
            data_wireless['short_wpa'], data_basic['wlan_pc'])
        #再修改ap的系统时间为06:00:00
        ssh.ssh_cmd(data_basic['sshUser'], "date -s 06:00:00")
        #等待3分钟
        time.sleep(180)
        #判断AP是否依然连接
        result = subprocess.check_output("iw dev %s link"%data_basic['wlan_pc'], shell=True)
        print result
        #释放无线网卡的ip
        tmp.dhcp_release_wlan(data_basic['wlan_pc'])
        #断开无线网卡的连接
        tmp.disconnect_ap()
        #释放被禁的客户端
        client_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        tmp.release_restrict_mac(client_mac)
        time.sleep(60)
        self.assertIn("Not connected.", result)

    #Connection Time单位选择d功能测试（Enabled勾选）
    def test_004_check_connection_time_d_function(self):
        u"""Connection Time单位选择d功能测试（Enabled勾选）(testlink_ID:1501)"""
        log.debug("004")
        tmp = TimePolicyBusiness(self.s)
        # #断开无线网卡的连接
        # tmp.disconnect_ap()
        # #释放被禁的客户端
        # client_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        # tmp.release_restrict_mac(client_mac)
        # time.sleep(60)

        #新增策略time policy3,连接时间1d，重置时间每周周一的23点
        data_dict = {'status': 1,
                    'reconnectType': 2,
                     'resetDay': 1,
                     'resetHour': "23",
                     'hour': "24",
                     'resetTimeType': "AM",
                     'timezone': "Etc/GMT",
                     'connectionTimeMap': {'d': "1", 'h': "0", 'm': "0"},
                     'connectionTimeoutMap': {'d': "", 'h': "", 'm': ""}
                     }
        tmp.add_timepolicy("time policy3", data_dict)
        #获取时间策略的id
        timepolicy_id = tmp.get_timepolicy_id("time policy3")
        #修改ssid1的ssid，并开启时间策略，并选择time policy3
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict1 = {'ssid_timed_client_policy': "%s"%timepolicy_id}
        tmp1.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict1)
        time.sleep(120)

        #先修改ap的系统时间为2018-08-08 10:00:00
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        ssh = SSH(data_basic['7600_ip'], ssh_pwd)
        ssh.ssh_cmd(data_basic['sshUser'], "date 201808081000")
        #无线网卡连接
        tmp.connect_DHCP_WPA_AP(data_wireless['all_ssid'],
            data_wireless['short_wpa'], data_basic['wlan_pc'])
        #再修改ap的系统时间为2018-08-09 10:00:00
        ssh.ssh_cmd(data_basic['sshUser'], "date 201808091000")
        #等待3分钟
        time.sleep(180)
        #判断AP是否依然连接
        result = subprocess.check_output("iw dev %s link"%data_basic['wlan_pc'], shell=True)
        print result
        #释放无线网卡的ip
        tmp.dhcp_release_wlan(data_basic['wlan_pc'])
        #断开无线网卡的连接
        tmp.disconnect_ap()
        #释放被禁的客户端
        client_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        tmp.release_restrict_mac(client_mac)
        time.sleep(60)
        self.assertIn("Not connected.", result)













    #删除ap，并恢复cloud的初始环境
    def test_075_reset_cloud(self):
        u"""删除ap，并恢复cloud的初始环境"""
        log.debug("075")
        #删除ssid2
        tmp1 = SSIDSBusiness(self.s)
        tmp1.dhcp_release_wlan(data_basic['wlan_pc'])
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
                     'ssid_ssid_band': ""}
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
