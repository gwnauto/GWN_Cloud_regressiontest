#coding=utf-8
#作者：曾祥卫
#时间：2018.03.20
#描述：Network-APs-Motior用例集，调用aps_business

import unittest,time, subprocess
from access_points.aps_business import APSBusiness
from system.settings.settings_business import SettingsBusiness
from ssids.ssids_business import SSIDSBusiness
from data import data
from connect.ssh import SSH
from data.logfile import Log
import requests
log = Log("ap_monitor")



data_basic = data.data_basic()
data_login = data.data_login()
data_wireless = data.data_wireless()
data_ng = data.data_networkgroup()
data_ap = data.data_AP()
data_client = data.data_Client()

class TestAPMonitor(unittest.TestCase):
    u"""测试Network-APs-Motior的用例集(runtime:3.57h)"""
    def setUp(self):
        self.s = requests.session()
        tmp = APSBusiness(self.s)
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

    #AP channel distribution图表
    def test_002_aps_summary_channel_distribution(self):
        u"""AP channel distribution图表(testlinkID:688)"""
        log.debug("002")
        tmp = APSBusiness(self.s)
        time.sleep(180)
        #修改7600信道：2.4g-1,5g-36
        tmp.edit_ap(data_ap['7600_mac'], {"ap_2g4_channel": "1", "ap_5g_channel": "36"})
        #修改7610信道：2.4g-1,5g-161
        tmp.edit_ap(data_ap['7610_mac'], {"ap_2g4_channel": "1", "ap_5g_channel": "161"})
        #修改7600lr信道：2.4g-11,5g-40
        tmp.edit_ap(data_ap['7600lr_mac'], {"ap_2g4_channel": "11", "ap_5g_channel": "40"})
        #等待6分钟，等ap将信息上报给cloud
        time.sleep(360)
        #获取接入点-概要-AP信道分配
        chn_2g4, chn_5g = tmp.get_aps_summary_channel_distribution()
        self.assertIn(([1,2]), chn_2g4)
        self.assertIn(([11,1]), chn_2g4)
        self.assertIn(([36,1]), chn_5g)
        self.assertIn(([40,1]), chn_5g)
        self.assertIn(([161,1]), chn_5g)
        print "test AP channel distribution pass!"

    #AP在线状态饼图
    def test_003_aps_summary_onlie(self):
        u"""AP在线状态饼图(testlinkID:689)"""
        log.debug("003")
        tmp = APSBusiness(self.s)
        #获取接入点-概要-AP在线情况
        total, values, categories = tmp.get_aps_summary_online()
        self.assertEqual(total, 3)
        self.assertEqual(values[0]['value'], 1)
        self.assertEqual(values[1]['value'], 1)
        self.assertEqual(values[2]['value'], 1)
        self.assertEqual(categories[0]['value'], 3)
        self.assertEqual(categories[1]['value'], 0)
        print "test AP online summary pass!"

    #信道显示
    def test_004_aps_status_ap_channel(self):
        u"""信道显示(testlinkID:703)"""
        log.debug("004")
        tmp = APSBusiness(self.s)
        #取出ap的信道
        chn_2g4_7600, chn_5g_7600 = tmp.get_ap_status_channel('GWN7600')
        chn_2g4_7610, chn_5g_7610 = tmp.get_ap_status_channel('GWN7610')
        chn_2g4_7600lr, chn_5g_7600lr = tmp.get_ap_status_channel('GWN7600LR')
        self.assertEqual(chn_2g4_7600, 1)
        self.assertEqual(chn_5g_7600, 36)
        self.assertEqual(chn_2g4_7610, 1)
        self.assertEqual(chn_5g_7610, 161)
        self.assertEqual(chn_2g4_7600lr, 11)
        self.assertEqual(chn_5g_7600lr, 40)
        print "test AP Status ap channel pass!"

    #产品型号与mac地址显示
    def test_005_aps_status_aptype_mac(self):
        u"""产品型号与mac地址显示(testlinkID:691-2)"""
        log.debug("005")
        tmp = APSBusiness(self.s)
        #判断产品型号和对应的mac地址显示正确
        result = tmp.check_ap_status_type_mac()
        self.assertNotIn(False,result)
        print "check ap type and mac pass!"

    #AP名称显示与更改
    def test_006_aps_status_device_name_chn(self):
        u"""AP名称显示与更改-中文(testlinkID:692-1)"""
        log.debug("006")
        tmp = APSBusiness(self.s)
        #修改7610的设备名称为中文
        tmp.edit_ap(data_ap['7610_mac'], {"ap_name": data_login['chineses']})
        #判断ap名称是否正确
        result = tmp.check_ap_status_device_name("GWN7610", data_login['chineses'])
        self.assertTrue(result)
        print "check device name is chn pass!"

    #AP名称显示与更改
    def test_007_aps_status_device_name_asii(self):
        u"""AP名称显示与更改-特殊字符(testlinkID:692-2)"""
        log.debug("007")
        tmp = APSBusiness(self.s)
        #修改7610的设备名称为特殊字符
        tmp.edit_ap(data_ap['7610_mac'], {"ap_name": data_login['asii_pwd']})
        #判断ap名称是否正确
        result = tmp.check_ap_status_device_name("GWN7610", data_login['asii_pwd'])
        self.assertTrue(result)
        print "check device name is asii pass!"

    #AP名称显示与更改
    def test_008_aps_status_device_name_32bits(self):
        u"""AP名称显示与更改-32bits(testlinkID:692-3)"""
        log.debug("008")
        tmp = APSBusiness(self.s)
        #修改7610的设备名称为32bits
        tmp.edit_ap(data_ap['7610_mac'], {"ap_name": data_wireless['long_ssid']})
        #判断ap名称是否正确
        result = tmp.check_ap_status_device_name("GWN7610", data_wireless['long_ssid'])
        #修改7610的设备名称修改回autotest_7610
        tmp.edit_ap(data_ap['7610_mac'], {"ap_name": "autotest_7610"})
        self.assertTrue(result)
        print "check device name is 32bits pass!"

    #IP地址显示
    def test_009_aps_status_ip(self):
        u"""IP地址显示(testlinkID:693)"""
        log.debug("009")
        tmp = APSBusiness(self.s)
        #判断ap名称是否正确
        result_7600 = tmp.check_ap_status_ip("GWN7600", data_basic['7600_ip'])
        result_7610 = tmp.check_ap_status_ip("GWN7610", data_basic['7610_ip'])
        result_7600lr = tmp.check_ap_status_ip("GWN7600LR", data_basic['7600lr_ip'])
        self.assertTrue(result_7600)
        self.assertTrue(result_7610)
        self.assertTrue(result_7600lr)
        print "check ip displayed pass!"

    #网络断开重连，运行状态正常
    def test_010_disconnect_network(self):
        u"""网络断开重连，运行状态正常(testlinkID:694-1)--bug113856"""
        log.debug("010")
        #获取网络组的ssh密码
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        #修改7610的/etc/hosts为空--即断开网络
        tmp1 = SSH(data_basic['7610_ip'], ssh_pwd)
        tmp1.ssh_cmd(data_basic['sshUser'], "echo '' > /etc/hosts")
        time.sleep(5)
        #重启7610
        tmp1.ssh_cmd(data_basic['sshUser'], "reboot")
        time.sleep(320)
        #判断ap运行状态
        tmp = APSBusiness(self.s)
        result = tmp.check_ap_status_online("GWN7610")
        self.assertFalse(result)
        print "disconnect ap's network, check cloud run status pass!"

    #网络断开重连，运行状态正常
    def test_011_connect_network_again(self):
        u"""网络断开重连，运行状态正常(testlinkID:694-2)"""
        log.debug("011")
        #获取网络组的ssh密码
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        #修改7610的/etc/hosts为本地cloud服务器--即连接网络
        tmp1 = SSH(data_basic['7610_ip'], ssh_pwd)
        tmp1.ssh_cmd(data_basic['sshUser'],"wget http://%s/hosts"%data_basic['ap_hosts_dir'])
        time.sleep(5)
        tmp1.ssh_cmd(data_basic['sshUser'],"mv hosts /etc/hosts")
        # ssh.ssh_cmd(data_basic['sshUser'],"reboot")
        time.sleep(180)
        #判断ap运行状态
        tmp = APSBusiness(self.s)
        result = tmp.check_ap_status_online("GWN7610")
        self.assertTrue(result)
        print "connect ap's network again, check cloud run status pass!"

    #ap重连后，等待5分钟，判断cloud中ap的运行时间
    def test_012_aps_status_uptime_after_reconnect_network(self):
        u"""ap重连后，等待5分钟，判断cloud中ap的运行时间(testlinkID:698-2)"""
        log.debug("012")
        #获取网络组的ssh密码
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        tmp = APSBusiness(self.s)
        #首先等待5分钟，让ap把信息上报给cloud
        time.sleep(300)
        #判断ap的运行时间是否显示正确
        result = tmp.check_ap_status_uptime(data_basic['7610_ip'],
                    data_basic['sshUser'], ssh_pwd, "GWN7610")
        #结果小于等于5分钟，即300s为通过
        self.assertLessEqual(result, 300)
        print "check cloud ap run time after reconnect ap pass!"

    #AP重启，运行状态正常
    def test_013_reboot_ap_status(self):
        u"""AP重启，运行状态正常(testlinkID:695)"""
        log.debug("013")
        #获取网络组的ssh密码
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        #重启ap
        tmp = APSBusiness(self.s)
        tmp.reboot_router(data_basic['7600_ip'], data_basic['sshUser'],
                          ssh_pwd)
        time.sleep(210)
        result = tmp.check_ap_status_online("GWN7600")
        self.assertTrue(result)
        print "after rebooting ap, check cloud run status pass!"

    #ap重启后，等待5分钟，判断cloud中ap的运行时间
    def test_014_aps_status_uptime_after_reboot_ap(self):
        u"""ap重启后，等待5分钟，判断cloud中ap的运行时间(testlinkID:698-3)"""
        log.debug("014")
        #获取网络组的ssh密码
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        tmp = APSBusiness(self.s)
        #首先等待5分钟，让ap把信息上报给cloud
        time.sleep(300)
        #判断ap的运行时间是否显示正确
        result = tmp.check_ap_status_uptime(data_basic['7600_ip'],
                    data_basic['sshUser'], ssh_pwd, "GWN7600")
        #结果小于等于5分钟，即300s为通过
        self.assertLessEqual(result, 300)
        print "check cloud ap run time after reboot ap pass!"

    # #AP恢复出厂设置，运行状态正常
    # def test_015_aps_set_factory_status1(self):
    #     u"""AP恢复出厂设置，运行状态正常(testlinkID:697-1)--bug113856"""
    #     log.debug("015")
    #     #获取网络组的ssh密码
    #     tmp2 = SettingsBusiness(self.s)
    #     ssh_pwd = tmp2.get_ssh_pwd()
    #     tmp = APSBusiness(self.s)
    #     #将7610恢复出厂设置
    #     tmp.set_ap_factory(data_basic['7610_ip'], ssh_pwd)
    #     time.sleep(320)
    #     #判断ap是否是在出厂值状态
    #     result1 = tmp.check_ap_factory(data_basic['7610_ip'])
    #     #判断ap运行状态
    #     result2 = tmp.check_ap_status_online("GWN7610")
    #     self.assertTrue(result1)
    #     self.assertFalse(result2)
    #     print "after reseting ap, check cloud run status pass!"
    #
    # #AP恢复出厂设置，运行状态正常
    # def test_016_aps_set_factory_status2(self):
    #     u"""AP恢复出厂设置，运行状态正常(testlinkID:697-2)"""
    #     log.debug("016")
    #     #修改7610的/etc/hosts为本地cloud服务器--即连接网络
    #     tmp1 = SSH(data_basic['7610_ip'], "admin")
    #     tmp1.ssh_cmd(data_basic['sshUser'],"wget http://%s/hosts"%data_basic['ap_hosts_dir'])
    #     time.sleep(5)
    #     tmp1.ssh_cmd(data_basic['sshUser'],"mv hosts /etc/hosts")
    #     # ssh.ssh_cmd(data_basic['sshUser'],"reboot")
    #     time.sleep(180)
    #     #判断ap运行状态
    #     tmp = APSBusiness(self.s)
    #     result1 = tmp.check_ap_status_online("GWN7610")
    #     #获取网络组的ssh密码
    #     tmp2 = SettingsBusiness(self.s)
    #     ssh_pwd = tmp2.get_ssh_pwd()
    #     #判断ap的配置是否已和cloud同步
    #     ssh = SSH(data_basic['7610_ip'], ssh_pwd)
    #     result2 = ssh.ssh_cmd(data_basic['sshUser'], "uci show grandstream.ssid0.name")
    #     self.assertTrue(result1)
    #     self.assertIn('GWN-Cloud', result2)
    #     print "after reseting ap, check cloud run status pass!"

    #上传流量显示-ap-2.4g
    def test_017_aps_status_ap_2g4_upload(self):
        u"""上传流量显示-ap-2.4g(testlinkID:700-1)"""
        #首先通过修改ssid，把7610和7600lr移除ssid,并切换为2.4G only
        log.debug("017")
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid': data_wireless['all_ssid'],
                     'ssid_ssid_band': "5",
                    'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp1.edit_ssid(data_ap['7600_mac'], 'GWN-Cloud',
                       encry_dict, data_dict)
        time.sleep(60)
        #AP 上传流量统计的准确性
        tmp = APSBusiness(self.s)
        tmp.run_AP_upload(data_wireless['all_ssid'],
                          data_wireless['short_wpa'],
                          data_basic['wlan_pc'],
                          data_basic['lan_pc'])
        #等待5分钟
        time.sleep(300)
        #重新登录
        #使用用户名密码，带着cookie登录cloud，并返回响应数据
        tmp.webLogin(data_basic['cloud_user'], data_basic['cloud_pwd'])
        #获取指定ap的流量
        ap_usage, ap_upload, ap_download = tmp.get_ap_status_load("GWN7600")
        # #可接受误差在10M内
        # error = 10*1024*1024
        # #取出的结果减去50M（50M为传输的文件大小）,取绝对值
        # result = abs(ap_upload - (50*1024*1024))
        # print error, result
        # self.assertLessEqual(result, error)
        #上传流量大于5M
        self.assertGreaterEqual(ap_upload, (5*1024*1024))
        print "check cloud 2.4G ap upload pass!"

    #AP信息概览-client-上传-2.4g
    def test_018_aps_status_client_2g4_upload(self):
        u"""AP信息概览-client-上传-2.4g(testlinkID:732-1)"""
        log.debug("018")
        tmp = APSBusiness(self.s)
        client_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        client_usage, client_upload, client_download = \
            tmp.get_client_load(data_ap['7600_mac'], client_mac)
        # #可接受误差在10M内
        # error = 10*1024*1024
        # #取出的结果减去50M（50M为传输的文件大小）,取绝对值
        # result = abs(client_upload - (50*1024*1024))
        # print error, result
        # self.assertLessEqual(result, error)
        #上传流量大于5M
        self.assertGreaterEqual(client_upload, (5*1024*1024))
        print "check cloud 2.4G client upload pass!"


    #下载流量显示-ap-2.4g
    def test_019_aps_status_ap_2g4_download(self):
        u"""下载流量显示-ap-2.4g(testlinkID:701-1)"""
        log.debug("019")
        #AP 下载流量统计的准确性
        tmp = APSBusiness(self.s)
        tmp.run_AP_download(data_wireless['all_ssid'],
                          data_wireless['short_wpa'],
                          data_basic['wlan_pc'],
                          data_basic['lan_pc'])
        #等待5分钟
        time.sleep(300)
        #重新登录
        #使用用户名密码，带着cookie登录cloud，并返回响应数据
        tmp.webLogin(data_basic['cloud_user'], data_basic['cloud_pwd'])
        #获取指定ap的流量
        ap_usage, ap_upload, ap_download = tmp.get_ap_status_load("GWN7600")
        # #可接受误差在10M内
        # error = 10*1024*1024
        # #取出的结果减去50M（50M为传输的文件大小）,取绝对值
        # result = abs(ap_download - (50*1024*1024))
        # print error, result
        # self.assertLessEqual(result, error)
        #下载流量大于5M
        self.assertGreaterEqual(ap_download, (5*1024*1024))
        print "check cloud 2.4G ap download pass!"

    #AP信息概览-client-下载-2.4g
    def test_020_aps_status_client_2g4_download(self):
        u"""AP信息概览-client-下载-2.4g(testlinkID:732-2)"""
        log.debug("020")
        tmp = APSBusiness(self.s)
        client_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        client_usage, client_upload, client_download = \
            tmp.get_client_load(data_ap['7600_mac'], client_mac)
        # #可接受误差在10M内
        # error = 10*1024*1024
        # #取出的结果减去50M（50M为传输的文件大小）,取绝对值
        # result = abs(client_download - (50*1024*1024))
        # print error, result
        # self.assertLessEqual(result, error)
        #下载流量大于5M
        self.assertGreaterEqual(client_download, (5*1024*1024))
        print "check cloud 2.4G client download pass!"

    #总流量显示-ap-2.4g
    def test_021_aps_status_ap_2g4_usage(self):
        u"""总流量显示-ap-2.4g(testlinkID:699-1)"""
        log.debug("021")
        #获取指定ap的流量
        tmp = APSBusiness(self.s)
        ap_usage, ap_upload, ap_download = tmp.get_ap_status_load("GWN7600")
        # #可接受误差在20M内
        # error = 20*1024*1024
        # #取出的结果减去50M+50M（上传和下载）,取绝对值
        # result = abs(ap_usage - (100*1024*1024))
        # print error, result
        # self.assertLessEqual(result, error)
        #总流量大于10M
        self.assertGreaterEqual(ap_usage, (10*1024*1024))
        print "check cloud 2.4G ap usage pass!"

    #点击清除流量的按钮，ap->Status页面的流量会清除
    def test_022_aps_status_clear_ap(self):
        u"""点击清除流量的按钮，ap->Status页面的流量会清除(testlinkID:702)"""
        log.debug("022")
        #点击接入点-状态-清除流量
        tmp = APSBusiness(self.s)
        tmp.clear_ap_load(data_ap['7600_mac'])
        #获取指定ap的流量
        ap_usage, ap_upload, ap_download = tmp.get_ap_status_load("GWN7600")
        #可接受误差在1M内
        error = 1*1024*1024
        self.assertLessEqual(ap_usage, error)
        self.assertLessEqual(ap_upload, error)
        self.assertLessEqual(ap_upload, error)
        print "check cloud clear ap load button pass!"


    #上传流量显示-ap-5g
    def test_023_aps_status_ap_5g_upload(self):
        u"""上传流量显示-ap-5g(testlinkID:700-2)"""
        log.debug("023")
        #点击接入点-状态-清除流量
        tmp = APSBusiness(self.s)
        tmp.clear_ap_load(data_ap['7600_mac'])
        #修改ssid为5G
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_band': "5",
                     'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(60)
        #AP 上传流量统计的准确性
        tmp.run_AP_upload(data_wireless['all_ssid'],
                          data_wireless['short_wpa'],
                          data_basic['wlan_pc'],
                          data_basic['lan_pc'])
        #等待5分钟
        time.sleep(300)
        #重新登录
        #使用用户名密码，带着cookie登录cloud，并返回响应数据
        tmp.webLogin(data_basic['cloud_user'], data_basic['cloud_pwd'])
        #获取指定ap的流量
        ap_usage, ap_upload, ap_download = tmp.get_ap_status_load("GWN7610")
        # #可接受误差在40M内
        # error = 40*1024*1024
        # print error, ap_upload
        # self.assertLessEqual(error, ap_upload)
        #上传流量大于5M
        self.assertGreaterEqual(ap_upload, (5*1024*1024))
        print "check cloud 5G ap upload pass!"

    #AP信息概览-client-上传-5g
    def test_024_aps_status_client_5g_upload(self):
        u"""AP信息概览-client-上传-5g(testlinkID:732-3)"""
        log.debug("024")
        tmp = APSBusiness(self.s)
        client_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        client_usage, client_upload, client_download = \
            tmp.get_client_load(data_ap['7610_mac'], client_mac)
        # #可接受误差在15M内
        # error = 15*1024*1024
        # #取出的结果减去100M（100M为2.4g+5g上传流量总和）,取绝对值
        # result = abs(client_upload - (100*1024*1024))
        # print error, result
        # self.assertLessEqual(result, error)
        #上传流量大于5M
        self.assertGreaterEqual(client_upload, (5*1024*1024))
        print "check cloud 5G client upload pass!"


    #下载流量显示-ap-5g
    def test_025_aps_status_ap_5g_download(self):
        u"""下载流量显示-ap-5g(testlinkID:701-2)"""
        log.debug("025")
        #AP 下载流量统计的准确性
        tmp = APSBusiness(self.s)
        tmp.run_AP_download(data_wireless['all_ssid'],
                          data_wireless['short_wpa'],
                          data_basic['wlan_pc'],
                          data_basic['lan_pc'])
        #等待5分钟
        time.sleep(300)

        #重新登录
        #使用用户名密码，带着cookie登录cloud，并返回响应数据
        tmp.webLogin(data_basic['cloud_user'], data_basic['cloud_pwd'])

        #获取指定ap的流量
        ap_usage, ap_upload, ap_download = tmp.get_ap_status_load("GWN7610")
        # #可接受误差在40M内
        # error = 40*1024*1024
        # print error, ap_upload
        # self.assertLessEqual(error, ap_download )
        #下载流量大于5M
        self.assertGreaterEqual(ap_download, (5*1024*1024))
        print "check cloud 5G ap download pass!"

    #AP信息概览-client-下载-5g
    def test_026_aps_status_client_5g_download(self):
        u"""AP信息概览-client-下载-5g(testlinkID:732-4)"""
        log.debug("026")
        tmp = APSBusiness(self.s)
        client_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        client_usage, client_upload, client_download = \
            tmp.get_client_load(data_ap['7610_mac'], client_mac)
        # #可接受误差在15M内
        # error = 15*1024*1024
        # #取出的结果减去100M（100M为2.4g+5g下载流量总和）,取绝对值
        # result = abs(client_download - (100*1024*1024))
        # print error, result
        # self.assertLessEqual(result, error)
        #下载流量大于5M
        self.assertGreaterEqual(client_download, (5*1024*1024))
        print "check cloud 2.4G client download pass!"

    #总流量显示
    def test_027_aps_status_ap_5g_usage(self):
        u"""总流量显示-5G(testlinkID:699-2)"""
        log.debug("027")
        #获取指定ap的流量
        tmp = APSBusiness(self.s)
        ap_usage, ap_upload, ap_download = tmp.get_ap_status_load("GWN7610")
        # #可接受误差在80M内
        # error = 80*1024*1024
        # print error, ap_upload
        # self.assertLessEqual(error, ap_usage)
        #总流量大于10M
        self.assertGreaterEqual(ap_usage, (10*1024*1024))
        print "check cloud 5G ap usage pass!"

    #更改AP配置，usage数据不会重置
    def test_028_aps_status_usage_after_modify_ap_config(self):
        u"""更改AP配置，usage数据不会重置(testlinkID:706)"""
        log.debug("028")
        tmp = APSBusiness(self.s)
        #更改ap配置
        tmp.edit_ap(data_ap['7610_mac'],  {"ap_5g_channel": "157"})
        #获取指定ap的流量
        ap_usage, ap_upload, ap_download = tmp.get_ap_status_load("GWN7610")
        # #总流量依然保持不变，大于80M
        # self.assertLessEqual(80*1024*1024, ap_usage)
        #总流量大于10M
        self.assertGreaterEqual(ap_usage, (10*1024*1024))
        print "check ap's usage is same after modifying ap config pass!"

    #客户端数量显示
    def test_029_aps_status_clients_number(self):
        u"""客户端数量显示(testlinkID:704)"""
        log.debug("029")
        #取出ap的客户端数量
        tmp = APSBusiness(self.s)
        result_7610 = tmp.get_ap_status_clients("GWN7610")
        result_7600 = tmp.get_ap_status_clients("GWN7600")
        result_7600lr = tmp.get_ap_status_clients("GWN7600LR")
        self.assertEqual(1, result_7610)
        self.assertEqual(0, result_7600)
        self.assertEqual(0, result_7600lr)
        print "check AP Status client number display pass!"

    #可以显示AP数量
    def test_030_aps_status_display_ap_total(self):
        u"""可以显示AP数量(testlinkID:707)"""
        log.debug("030")
        #获取接入点-状态-AP总数
        tmp = APSBusiness(self.s)
        result = tmp.get_aps_status_ap_number()
        self.assertEqual(result, 3)
        print "check AP Status AP number display pass!"

    #按全MAC地址搜索设备
    def test_031_aps_status_search_all_mac(self):
        u"""按全MAC地址搜索设备(testlinkID:716)"""
        log.debug("031")
        tmp = APSBusiness(self.s)
        result = tmp.check_status_search_ap(data_ap['7610_mac'], data_ap['7610_mac'])
        self.assertTrue(result)
        print "test search all ap's mac pass!"

    #按mac地址关键字搜索设备
    def test_032_aps_status_search_part_mac(self):
        u"""按mac地址关键字搜索设备(testlinkID:717)"""
        log.debug("032")
        tmp = APSBusiness(self.s)
        #取得mac地址的后6位mac地址
        search_str = tmp.get_last_6mac(data_ap['7600lr_mac'])
        result = tmp.check_status_search_ap(search_str, data_ap['7600lr_mac'])
        self.assertTrue(result)
        print "test search part ap's mac pass!"

    #按设备name全称搜索
    def test_033_aps_status_search_all_name(self):
        u"""按设备name全称搜索(testlinkID:718)"""
        log.debug("033")
        tmp = APSBusiness(self.s)
        result = tmp.check_status_search_ap("autotest_7600", data_ap['7600_mac'])
        self.assertTrue(result)
        print "test search all ap's name pass!"

    #按设备name关键字搜索
    def test_034_aps_status_search_part_name(self):
        u"""按设备name全称搜索(testlinkID:719)"""
        log.debug("034")
        tmp = APSBusiness(self.s)
        result = tmp.check_status_search_ap("7610", data_ap['7610_mac'])
        self.assertTrue(result)
        print "test search part ap's name pass!"

    #AP信息概览页面-usage-bandwidth图表-2h
    def test_035_aps_status_chart_ap_bandwidth_2h(self):
        u"""AP信息概览页面-usage-bandwidth图表-2h(testlinkID:723-1)"""
        log.debug("035")
        tmp = APSBusiness(self.s)
        result_7600 = tmp.check_chart_ap_bandwidth("2h", data_ap['7600_mac'])
        result_7610 = tmp.check_chart_ap_bandwidth("2h", data_ap['7610_mac'])
        result_7600lr = tmp.check_chart_ap_bandwidth("2h", data_ap['7600lr_mac'])
        print result_7600, result_7610, result_7600lr
        #只有7610有流量图显示
        # self.assertFalse(result_7600)
        self.assertTrue(result_7610)
        # self.assertFalse(result_7600lr)
        print "check chart for ap bandwidth 2h pass!"

    #AP信息概览页面-usage-bandwidth图表-1d
    def test_036_aps_status_chart_ap_bandwidth_1d(self):
        u"""AP信息概览页面-usage-bandwidth图表-1d(testlinkID:723-2)"""
        log.debug("036")
        tmp = APSBusiness(self.s)
        result_7600 = tmp.check_chart_ap_bandwidth("1d", data_ap['7600_mac'])
        result_7610 = tmp.check_chart_ap_bandwidth("1d", data_ap['7610_mac'])
        result_7600lr = tmp.check_chart_ap_bandwidth("1d", data_ap['7600lr_mac'])
        print result_7600, result_7610, result_7600lr
        #只有7610有流量图显示
        # self.assertFalse(result_7600)
        self.assertTrue(result_7610)
        # self.assertFalse(result_7600lr)
        print "check chart for ap bandwidth 1d pass!"

    # #AP信息概览页面-usage-bandwidth图表-1w
    # def test_037_aps_status_chart_ap_bandwidth_1w(self):
    #     u"""AP信息概览页面-usage-bandwidth图表-1w(testlinkID:723-3)"""
    #     log.debug("037")
    #     tmp = APSBusiness(self.s)
    #     result_7600 = tmp.check_chart_ap_bandwidth("1w", data_ap['7600_mac'])
    #     result_7610 = tmp.check_chart_ap_bandwidth("1w", data_ap['7610_mac'])
    #     result_7600lr = tmp.check_chart_ap_bandwidth("1w", data_ap['7600lr_mac'])
    #     print result_7600, result_7610, result_7600lr
    #     #只有7610有流量图显示
    #     # self.assertFalse(result_7600)
    #     self.assertTrue(result_7610)
    #     # self.assertFalse(result_7600lr)
    #     print "check chart for ap bandwidth 1w pass!"
    #
    # #AP信息概览页面-usage-bandwidth图表-1m
    # def test_038_aps_status_chart_ap_bandwidth_1m(self):
    #     u"""AP信息概览页面-usage-bandwidth图表-1m(testlinkID:723-4)"""
    #     log.debug("038")
    #     tmp = APSBusiness(self.s)
    #     result_7600 = tmp.check_chart_ap_bandwidth("1m", data_ap['7600_mac'])
    #     result_7610 = tmp.check_chart_ap_bandwidth("1m", data_ap['7610_mac'])
    #     result_7600lr = tmp.check_chart_ap_bandwidth("1m", data_ap['7600lr_mac'])
    #     print result_7600, result_7610, result_7600lr
    #     #只有7610有流量图显示
    #     # self.assertFalse(result_7600)
    #     self.assertTrue(result_7610)
    #     # self.assertFalse(result_7600lr)
    #     print "check chart for ap bandwidth 1m pass!"

    #AP信息概览页面-usage-client count图表-2h
    def test_039_aps_status_chart_client_count_2h(self):
        u"""AP信息概览页面-usage-client count图表-2h(testlinkID:724-1)"""
        log.debug("039")
        tmp = APSBusiness(self.s)
        result_7600 = tmp.get_aps_status_ap_chart_client_count("2h", data_ap['7600_mac'])
        result_7610 = tmp.get_aps_status_ap_chart_client_count("2h", data_ap['7610_mac'])
        result_7600lr = tmp.get_aps_status_ap_chart_client_count("2h", data_ap['7600lr_mac'])
        print result_7600, result_7610, result_7600lr
        #只有7610有1个客户端显示
        #self.assertNotIn(1, result_7600)
        self.assertIn(1, result_7610)
        #self.assertNotIn(1, result_7600lr)
        print "check chart for client count 2h pass!"

    #AP信息概览页面-usage-client count图表-1d
    def test_040_aps_status_chart_client_count_1d(self):
        u"""AP信息概览页面-usage-client count图表-1d(testlinkID:724-2)"""
        log.debug("040")
        tmp = APSBusiness(self.s)
        result_7600 = tmp.get_aps_status_ap_chart_client_count("1d", data_ap['7600_mac'])
        result_7610 = tmp.get_aps_status_ap_chart_client_count("1d", data_ap['7610_mac'])
        result_7600lr = tmp.get_aps_status_ap_chart_client_count("1d", data_ap['7600lr_mac'])
        print result_7600, result_7610, result_7600lr
        #只有7610有1个客户端显示
        #self.assertNotIn(1, result_7600)
        self.assertIn(1, result_7610)
        #self.assertNotIn(1, result_7600lr)
        print "check chart for client count 1d pass!"

    # #AP信息概览页面-usage-client count图表-1w
    # def test_041_aps_status_chart_client_count_1w(self):
    #     u"""AP信息概览页面-usage-client count图表-1w(testlinkID:724-3)"""
    #     log.debug("041")
    #     tmp = APSBusiness(self.s)
    #     result_7600 = tmp.get_aps_status_ap_chart_client_count("1w", data_ap['7600_mac'])
    #     result_7610 = tmp.get_aps_status_ap_chart_client_count("1w", data_ap['7610_mac'])
    #     result_7600lr = tmp.get_aps_status_ap_chart_client_count("1w", data_ap['7600lr_mac'])
    #     print result_7600, result_7610, result_7600lr
    #     #只有7610有1个客户端显示
    #     #self.assertNotIn(1, result_7600)
    #     self.assertIn(1, result_7610)
    #     #self.assertNotIn(1, result_7600lr)
    #     print "check chart for client count 1w pass!"
    #
    # #AP信息概览页面-usage-client count图表-1m
    # def test_042_aps_status_chart_client_count_1m(self):
    #     u"""AP信息概览页面-usage-client count图表-1m(testlinkID:724-4)"""
    #     log.debug("042")
    #     tmp = APSBusiness(self.s)
    #     result_7600 = tmp.get_aps_status_ap_chart_client_count("1m", data_ap['7600_mac'])
    #     result_7610 = tmp.get_aps_status_ap_chart_client_count("1m", data_ap['7610_mac'])
    #     result_7600lr = tmp.get_aps_status_ap_chart_client_count("1m", data_ap['7600lr_mac'])
    #     print result_7600, result_7610, result_7600lr
    #     #只有7610有1个客户端显示
    #     #self.assertNotIn(1, result_7600)
    #     self.assertIn(1, result_7610)
    #     #self.assertNotIn(1, result_7600lr)
    #     print "check chart for client count 1m pass!"

    #AP信息概览页面-client-显示在线5gclient,client在线
    def test_043_aps_status_client_online_5g(self):
        u"""AP信息概览页面-client-显示在线5gclient,client在线(testlinkID:727-1)"""
        log.debug("043")
        tmp = APSBusiness(self.s)
        res_data = tmp.get_aps_status_clients_info(data_ap['7610_mac'])
        result = res_data['total']
        self.assertEqual(1, result)
        print "display 5G client online pass!"

    #AP信息概览页面-client-显示在线5gclient,client离线
    def test_044_aps_status_client_offline_5g(self):
        u"""AP信息概览页面-client-显示在线5gclient,client离线(testlinkID:727-2)"""
        log.debug("044")
        tmp = APSBusiness(self.s)
        #断开无线网卡
        tmp.disconnect_ap()
        time.sleep(180)
        res_data = tmp.get_aps_status_clients_info(data_ap['7610_mac'])
        result = res_data['total']
        self.assertEqual(0, result)
        print "display 5G client offline pass!"

    #AP信息概览页面-client-显示在线2.4ggclient,client在线
    def test_045_aps_status_client_online_2g4(self):
        u"""AP信息概览页面-client-显示在线2.4gclient,client在线(testlinkID:727-3)"""
        log.debug("045")
        #修改ssid为2.4g
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_band': "2",
                     'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp1.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(60)
        tmp = APSBusiness(self.s)
        #无线网卡连接ap
        tmp.connect_WPA_AP(data_wireless['all_ssid'],
                          data_wireless['short_wpa'],
                          data_basic['wlan_pc'])
        time.sleep(300)
        res_data = tmp.get_aps_status_clients_info(data_ap['7600_mac'])
        result = res_data['total']
        self.assertEqual(1, result)
        print "display 2.4G client online pass!"

    #AP信息概览页面-client-显示在线2.4gclient,client离线
    def test_046_aps_status_client_offline_2g4(self):
        u"""AP信息概览页面-client-显示在线2.4gclient,client离线(testlinkID:727-4)"""
        log.debug("046")
        tmp = APSBusiness(self.s)
        #断开无线网卡
        tmp.disconnect_ap()
        time.sleep(180)
        res_data = tmp.get_aps_status_clients_info(data_ap['7600_mac'])
        result = res_data['total']
        self.assertEqual(0, result)
        print "display 2.4G client offline pass!"

    #AP信息概览页面-client-mac地址-2.4g
    def test_047_aps_status_client_mac_2g4(self):
        u"""AP信息概览页面-client-mac地址-2.4g(testlinkID:728-1)"""
        log.debug("047")
        tmp = APSBusiness(self.s)
        #无线网卡连接ap
        tmp.connect_WPA_AP(data_wireless['all_ssid'],
                          data_wireless['short_wpa'],
                          data_basic['wlan_pc'])
        time.sleep(300)
        res_data = tmp.get_aps_status_clients_info(data_ap['7600_mac'])
        result = res_data['result'][0]['mac']
        client_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        Client_Mac =client_mac.upper()
        self.assertEqual(result, Client_Mac)
        print "display 2.4G client mac pass!"

    #AP信息概览页面-client-mac地址-5g
    def test_048_aps_status_client_mac_5g(self):
        u"""AP信息概览页面-client-mac地址-5g(testlinkID:728-2)"""
        log.debug("048")
        #修改ssid为5g
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_band': "5",
                     'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(60)
        tmp = APSBusiness(self.s)
        #无线网卡连接ap
        tmp.connect_WPA_AP(data_wireless['all_ssid'],
                          data_wireless['short_wpa'],
                          data_basic['wlan_pc'])
        time.sleep(300)
        res_data = tmp.get_aps_status_clients_info(data_ap['7610_mac'])
        result = res_data['result'][0]['mac']
        client_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        Client_Mac =client_mac.upper()
        self.assertEqual(result, Client_Mac)
        print "display 5G client mac pass!"

    #AP信息概览页面-client-ip地址
    def test_049_aps_status_client_ip(self):
        u"""AP信息概览页面-client-ip地址(testlinkID:730)"""
        log.debug("049")
        tmp = APSBusiness(self.s)
        #无线网卡连接ap
        tmp.connect_DHCP_WPA_AP(data_wireless['all_ssid'],
                          data_wireless['short_wpa'],
                          data_basic['wlan_pc'])
        time.sleep(60)
        tmp.dhcp_release_wlan_backup(data_basic['wlan_pc'])
        #重新登录
        #使用用户名密码，带着cookie登录cloud，并返回响应数据
        tmp.webLogin(data_basic['cloud_user'], data_basic['cloud_pwd'])
        res_data = tmp.get_aps_status_clients_info(data_ap['7610_mac'])
        result = res_data['result'][0]['ipv4']
        self.assertIn("192.168.1", result)
        print "display client ip pass!"

    #AP信息概览页面-client-信道-5g
    def test_050_aps_status_client_5g_channel(self):
        u"""AP信息概览页面-client-信道-5g(testlinkID:731-1)"""
        log.debug("050")
        tmp = APSBusiness(self.s)
        res_data = tmp.get_aps_status_clients_info(data_ap['7610_mac'])
        result = res_data['result'][0]['channel5g']
        self.assertEqual(157, result)
        print "display client 5g channel pass!"

    #AP信息概览页面-client-信道-2.4g
    def test_051_aps_status_client_2g4_channel(self):
        u"""AP信息概览页面-client-信道-2.4g(testlinkID:731-2)"""
        log.debug("051")
        #修改ssid为2.4g
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_band': "2",
                     'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7610_mac'].upper())}
        tmp1.edit_ssid(data_ap['7600lr_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(60)
        tmp = APSBusiness(self.s)
        #无线网卡连接ap
        tmp.connect_WPA_AP(data_wireless['all_ssid'],
                          data_wireless['short_wpa'],
                          data_basic['wlan_pc'])
        time.sleep(300)
        res_data = tmp.get_aps_status_clients_info(data_ap['7600lr_mac'])
        result = res_data['result'][0]['channel']
        self.assertEqual(11, result)
        print "display client 2.4g channel pass!"

    #AP信息概览页面-Info-基本信息
    def test_052_aps_status_ap_info(self):
        u"""AP信息概览页面-Info-基本信息(testlinkID:734)"""
        log.debug("052")
        #cloud上获取该网络组的ssh密码
        tmp1 = SettingsBusiness(self.s)
        ssh_pwd = tmp1.get_ssh_pwd()
        tmp = APSBusiness(self.s)
        result = tmp.check_ap_info(data_ap['7600lr_mac'], data_basic['7600lr_ip'],
                            data_basic['sshUser'], ssh_pwd)
        self.assertTrue(result)
        print "check cloud ap status ap's info pass!"

    #AP信息概览页面-Info-IP
    def test_053_aps_status_ap_ip(self):
        u"""AP信息概览页面-Info-IP(testlinkID:735)"""
        log.debug("053")
        tmp = APSBusiness(self.s)
        ip, ssid, clientBridgeMode = \
            tmp.get_aps_status_Info_ip_ssid_clientBridgeMode(data_ap['7600lr_mac'])
        self.assertEqual(ip, data_basic['7600lr_ip'])
        print "check cloud ap status ap's info ip pass!"

    #AP信息概览页面-Info-SSID
    def test_054_aps_status_ap_ssid(self):
        u"""AP信息概览页面-Info-SSID(testlinkID:736)"""
        log.debug("054")
        tmp = APSBusiness(self.s)
        ip, ssid, clientBridgeMode = \
            tmp.get_aps_status_Info_ip_ssid_clientBridgeMode(data_ap['7600lr_mac'])
        self.assertIn(data_wireless['all_ssid'], ssid)
        print "check cloud ap status ap's info ssid pass!"

    #AP信息概览页面-Info-clientBridgeMode
    def test_055_aps_status_ap_clientBridgeMode(self):
        u"""AP信息概览页面-Info-clientBridgeMode(testlinkID:737)"""
        log.debug("055")
        tmp = APSBusiness(self.s)
        ip, ssid, clientBridgeMode = \
            tmp.get_aps_status_Info_ip_ssid_clientBridgeMode(data_ap['7600lr_mac'])
        self.assertEqual(clientBridgeMode, -1)
        print "check cloud ap status ap's info clientBridgeMode pass!"

    #AP信息概览页面-Info-radio status, Power level-2.4g
    def test_056_aps_status_radio_status_2g4_power(self):
        u"""AP信息概览页面-Info-radio status, Power level-2.4g(testlinkID:739-1)"""
        log.debug("056")
        #cloud上获取该网络组的ssh密码
        tmp1 = SettingsBusiness(self.s)
        ssh_pwd = tmp1.get_ssh_pwd()
        tmp = APSBusiness(self.s)
        #获取接入点-状态-ap-信息-2.4g radio status
        chn, client_count, power = tmp.get_aps_status_Info_2g4_radio(data_ap['7600lr_mac'])
        #登录ap后台，取出无线发射功率值
        power_2g4 = tmp.get_ap_ssh_power("ath0", data_basic['7600lr_ip'],
                            data_basic['sshUser'], ssh_pwd)
        self.assertEqual(power, power_2g4)
        print "check cloud ap status ap's info 2.4g power pass"

    #AP信息概览页面-Info-radio status, client count-2.4g
    def test_057_aps_status_radio_status_2g4_client_count(self):
        u"""AP信息概览页面-Info-radio status, client count-2.4g(testlinkID:740-1)"""
        log.debug("057")
        tmp = APSBusiness(self.s)
        #获取接入点-状态-ap-信息-2.4g radio status
        chn, client_count, power = tmp.get_aps_status_Info_2g4_radio(data_ap['7600lr_mac'])
        self.assertEqual(client_count, "1")
        print "check cloud ap status ap's info 2.4g client count pass"

    #AP信息概览页面-Info-radio status, chn-2.4g
    def test_058_aps_status_radio_status_2g4_channel(self):
        u"""AP信息概览页面-Info-radio status, chn-2.4g(testlinkID:741-1)"""
        log.debug("058")
        tmp = APSBusiness(self.s)
        #获取接入点-状态-ap-信息-2.4g radio status
        chn, client_count, power = tmp.get_aps_status_Info_2g4_radio(data_ap['7600lr_mac'])
        self.assertEqual(chn, "11")
        print "check cloud ap status ap's info 2.4g channel pass"

    #AP信息概览页面-Info-radio status, Power level-5g
    def test_059_aps_status_radio_status_5g_power(self):
        u"""AP信息概览页面-Info-radio status, Power level-5g(testlinkID:739-2)"""
        log.debug("059")
        #修改ssid为5g
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_band': "5",
                     'removed_macs': "%s,%s"%(data_ap['7600_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(60)
        tmp = APSBusiness(self.s)
        #无线网卡连接ap
        tmp.connect_WPA_AP(data_wireless['all_ssid'],
                          data_wireless['short_wpa'],
                          data_basic['wlan_pc'])
        time.sleep(300)
        #cloud上获取该网络组的ssh密码
        tmp2 = SettingsBusiness(self.s)
        ssh_pwd = tmp2.get_ssh_pwd()
        #获取接入点-状态-ap-信息-5g radio status
        chn, client_count, power = tmp.get_aps_status_Info_5g_radio(data_ap['7610_mac'])
        #登录ap后台，取出无线发射功率值
        power_5g = tmp.get_ap_ssh_power("ath0",data_basic['7610_ip'],
                            data_basic['sshUser'], ssh_pwd)
        self.assertEqual(power, power_5g)
        print "check cloud ap status ap's info 5g power pass"

    #AP信息概览页面-Info-radio status, client count-5g
    def test_060_aps_status_radio_status_5g_client_count(self):
        u"""AP信息概览页面-Info-radio status, client count-5g(testlinkID:740-2)"""
        log.debug("060")
        tmp = APSBusiness(self.s)
        #获取接入点-状态-ap-信息-5g radio status
        chn, client_count, power = tmp.get_aps_status_Info_5g_radio(data_ap['7610_mac'])
        self.assertEqual(client_count, "1")
        print "check cloud ap status ap's info 5g client count pass"

    #AP信息概览页面-Info-radio status, chn-5g
    def test_061_aps_status_radio_status_5g_channel(self):
        u"""AP信息概览页面-Info-radio status, chn-5g(testlinkID:741-2)"""
        log.debug("061")
        tmp = APSBusiness(self.s)
        #获取接入点-状态-ap-信息-5g radio status
        chn, client_count, power = tmp.get_aps_status_Info_5g_radio(data_ap['7610_mac'])
        self.assertEqual(chn, "157")
        print "check cloud ap status ap's info 5g channel pass"

    #AP的event log页面-clients在线状态显示
    def test_062_aps_status_eventLog_online(self):
        u"""AP的event log页面-clients在线状态显示(testlinkID:742)--bug113620"""
        log.debug("062")
        tmp = APSBusiness(self.s)
        #无线网卡连接ap
        tmp.connect_WPA_AP(data_wireless['all_ssid'],
                          data_wireless['short_wpa'],
                          data_basic['wlan_pc'])
        time.sleep(360)
        client_mac, frequencyBand, details = tmp.get_aps_status_eventLog(data_ap['7610_mac'])
        self.assertEqual(1, details)
        print "check cloud ap status ap's eventlog online display pass!"

    #AP的event log页面-clients离线状态显示
    def test_063_aps_status_eventLog_offline(self):
        u"""AP的event log页面-clients离线状态显示(testlinkID:743)--bug113620"""
        log.debug("063")
        tmp = APSBusiness(self.s)
        #断开无线
        tmp.disconnect_ap()
        time.sleep(180)
        client_mac, frequencyBand, details = tmp.get_aps_status_eventLog(data_ap['7610_mac'])
        self.assertEqual(0, details)
        print "check cloud ap status ap's eventlog offline display pass!"

    #AP的event log页面-ssid配置5G：clients离线状态显示
    def test_064_aps_status_eventlog_5g_offline(self):
        u"""AP的event log页面-ssid配置5G：clients离线状态显示(testlinkID:745-1)--bug113620"""
        log.debug("064")
        tmp = APSBusiness(self.s)
        client_mac, frequencyBand, details = tmp.get_aps_status_eventLog(data_ap['7610_mac'])
        self.assertEqual(5, frequencyBand)
        self.assertEqual(0, details)
        print "check cloud ap status 5g ap's eventlog offline display pass!"

    #AP的event log页面-ssid配置5G：clients在线状态显示
    def test_065_aps_status_eventlog_5g_online(self):
        u"""AP的event log页面-ssid配置5G：clients在线状态显示(testlinkID:745-2)--bug113620"""
        log.debug("065")
        tmp = APSBusiness(self.s)
        #无线网卡连接ap
        tmp.connect_WPA_AP(data_wireless['all_ssid'],
                          data_wireless['short_wpa'],
                          data_basic['wlan_pc'])
        time.sleep(360)
        client_mac, frequencyBand, details = tmp.get_aps_status_eventLog(data_ap['7610_mac'])
        self.assertEqual(5, frequencyBand)
        self.assertEqual(1, details)
        print "check cloud ap status 5g ap's eventlog online display pass!"

    #AP的event log页面-ssid配置2.4G：clients在线状态显示
    def test_066_aps_status_eventlog_2g4_online(self):
        u"""AP的event log页面-ssid配置2.4G：clients在线状态显示(testlinkID:744-1)--bug113620"""
        log.debug("066")
        #修改ssid为2.4g
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_band': "2"}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(60)
        tmp = APSBusiness(self.s)
        #无线网卡连接ap
        tmp.connect_WPA_AP(data_wireless['all_ssid'],
                          data_wireless['short_wpa'],
                          data_basic['wlan_pc'])
        time.sleep(360)
        client_mac, frequencyBand, details = tmp.get_aps_status_eventLog(data_ap['7610_mac'])
        self.assertEqual(2, frequencyBand)
        self.assertEqual(1, details)
        print "check cloud ap status 2.4g ap's eventlog online display pass!"

    #AP的event log页面-ssid配置2.4G：clients离线状态显示
    def test_067_aps_status_eventlog_2g4_offline(self):
        u"""AP的event log页面-ssid配置2.4G：clients离线状态显示(testlinkID:744-2)--bug113620"""
        log.debug("067")
        tmp = APSBusiness(self.s)
        #断开无线
        tmp.disconnect_ap()
        time.sleep(180)
        client_mac, frequencyBand, details = tmp.get_aps_status_eventLog(data_ap['7610_mac'])
        self.assertEqual(2, frequencyBand)
        self.assertEqual(0, details)
        print "check cloud ap status 2.4g ap's eventlog offline display pass!"

    #AP的event log页面-ssid配置wpa2模式，client在线状态显示
    def test_068_aps_status_eventlog_wpa_online(self):
        u"""AP的event log页面-ssid配置wpa2模式，client在线状态显示(testlinkID:746-1)--bug113620"""
        log.debug("068")
        #修改ssid为5G
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_band': "5"}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(60)
        #无线网卡连接ap
        tmp = APSBusiness(self.s)
        tmp.connect_WPA_AP(data_wireless['all_ssid'],
                          data_wireless['short_wpa'],
                          data_basic['wlan_pc'])
        time.sleep(360)
        client_mac, frequencyBand, details = tmp.get_aps_status_eventLog(data_ap['7610_mac'])
        #获取无线网卡的mac
        wifi_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        self.assertEqual(wifi_mac.upper(), client_mac)
        self.assertEqual(1, details)
        print "check cloud ap status ap wpa2's eventlog online display pass!"

    #AP的event log页面-ssid配置wpa2模式，client离线状态显示
    def test_069_aps_status_eventlog_wpa2_offline(self):
        u"""AP的event log页面-ssid配置wpa2模式，client离线状态显示(testlinkID:746-2)--bug113620"""
        log.debug("069")
        tmp = APSBusiness(self.s)
        #断开无线
        tmp.disconnect_ap()
        time.sleep(180)
        client_mac, frequencyBand, details = tmp.get_aps_status_eventLog(data_ap['7610_mac'])
        #获取无线网卡的mac
        wifi_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        self.assertEqual(wifi_mac.upper(), client_mac)
        self.assertEqual(0, details)
        print "check cloud ap status ap wpa2's eventlog offline display pass!"

    #AP的event log页面-ssid配置wpa2_802.1x模式，client在线状态显示
    def test_070_aps_status_eventlog_wpa2_802_1x_online(self):
        u"""AP的event log页面-ssid配置wpa2_802.1x模式，client在线状态显示(testlinkID:747-1)--bug113620"""
        log.debug("070")
        #修改ssid为wpa2_802.1x模式
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                      'ssid_wpa_encryption': "0",
                      'ssid_wpa_key_mode': "1",
                      'ssid_radius_server': data_basic['radius_addr'],
                      'ssid_radius_port': "1812",
                      'ssid_radius_secret': data_basic['radius_secrect'],
                      'ssid_radius_acct_port': "1813"}
        data_dict = {'ssid_ssid_band': "5"}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(60)
        #无线网卡连接ap
        tmp = APSBusiness(self.s)
        tmp.connect_8021x_AP(data_wireless['all_ssid'],
                          data_basic['radius_usename'],
                          data_basic['radius_password'],
                          data_basic['wlan_pc'])
        time.sleep(360)
        client_mac, frequencyBand, details = tmp.get_aps_status_eventLog(data_ap['7610_mac'])
        #获取无线网卡的mac
        wifi_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        self.assertEqual(wifi_mac.upper(), client_mac)
        self.assertEqual(1, details)
        print "check cloud ap status ap wpa2 802.1x's eventlog online display pass!"

    #AP的event log页面-ssid配置wpa2_802.1x模式，client离线状态显示
    def test_071_aps_status_eventlog_wpa2_802_1x_offline(self):
        u"""AP的event log页面-ssid配置wpa2_802.1x模式，client离线状态显示(testlinkID:747-2)--bug113620"""
        log.debug("071")
        tmp = APSBusiness(self.s)
        #断开无线
        tmp.disconnect_ap()
        tmp.wlan_disable(data_basic['wlan_pc'])
        time.sleep(180)
        client_mac, frequencyBand, details = tmp.get_aps_status_eventLog(data_ap['7610_mac'])
        #获取无线网卡的mac
        tmp.wlan_enable(data_basic['wlan_pc'])
        wifi_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        self.assertEqual(wifi_mac.upper(), client_mac)
        self.assertEqual(0, details)
        print "check cloud ap status ap wpa2 802.1x's eventlog offline display pass!"

    #AP的event log页面-ssid配置wpa/wpa2_802.1x模式，client在线状态显示
    def test_072_aps_status_eventlog_wpa_wpa2_802_1x_online(self):
        u"""AP的event log页面-ssid配置wpa/wpa2_802.1x模式，client在线状态显示(testlinkID:751-1)--bug113620"""
        log.debug("072")
        #修改ssid为wpa/wpa2_802.1x模式
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                      'ssid_wpa_encryption': "0",
                      'ssid_wpa_key_mode': "1",
                      'ssid_radius_server': data_basic['radius_addr'],
                      'ssid_radius_port': "1812",
                      'ssid_radius_secret': data_basic['radius_secrect'],
                      'ssid_radius_acct_port': "1813"}
        data_dict = {'ssid_ssid_band': "5"}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(60)
        #无线网卡连接ap
        tmp = APSBusiness(self.s)
        tmp.connect_8021x_AP(data_wireless['all_ssid'],
                          data_basic['radius_usename'],
                          data_basic['radius_password'],
                          data_basic['wlan_pc'])
        time.sleep(360)
        client_mac, frequencyBand, details = tmp.get_aps_status_eventLog(data_ap['7610_mac'])
        #获取无线网卡的mac
        wifi_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        self.assertEqual(wifi_mac.upper(), client_mac)
        self.assertEqual(1, details)
        print "check cloud ap status ap wpa/wpa2 802.1x's eventlog online display pass!"

    #AP的event log页面-ssid配置wpa/wpa2_802.1x模式，client离线状态显示
    def test_073_aps_status_eventlog_wpa_wpa2_802_1x_offline(self):
        u"""AP的event log页面-ssid配置wpa/wpa2_802.1x模式，client离线状态显示(testlinkID:747-2)--bug113620"""
        log.debug("073")
        tmp = APSBusiness(self.s)
        #断开无线
        tmp.disconnect_ap()
        tmp.wlan_disable(data_basic['wlan_pc'])
        time.sleep(180)
        client_mac, frequencyBand, details = tmp.get_aps_status_eventLog(data_ap['7610_mac'])
        #获取无线网卡的mac
        tmp.wlan_enable(data_basic['wlan_pc'])
        wifi_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        self.assertEqual(wifi_mac.upper(), client_mac)
        self.assertEqual(0, details)
        print "check cloud ap status ap wpa/wpa2 802.1x's eventlog offline display pass!"

    #AP的event log页面-ssid配置wpa/wpa2模式，client在线状态显示
    def test_074_aps_status_eventlog_wpa_wpa2_online(self):
        u"""AP的event log页面-ssid配置wpa/wpa2模式，client在线状态显示(testlinkID:750-1)--bug113620"""
        log.debug("074")
        #修改ssid为wpa/wpa2模式
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "2",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_band': "5"}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(60)
        #无线网卡连接ap
        tmp = APSBusiness(self.s)
        tmp.connect_WPA_AP(data_wireless['all_ssid'],
                          data_wireless['short_wpa'],
                          data_basic['wlan_pc'])
        time.sleep(360)
        client_mac, frequencyBand, details = tmp.get_aps_status_eventLog(data_ap['7610_mac'])
        #获取无线网卡的mac
        wifi_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        self.assertEqual(wifi_mac.upper(), client_mac)
        self.assertEqual(1, details)
        print "check cloud ap status ap wpa/wpa2's eventlog online display pass!"

    #AP的event log页面-ssid配置wpa/wpa2模式，client离线状态显示
    def test_075_aps_status_eventlog_wpa_wpa2_offline(self):
        u"""AP的event log页面-ssid配置wpa/wpa2模式，client离线状态显示(testlinkID:750-2)--bug113620"""
        log.debug("075")
        tmp = APSBusiness(self.s)
        #断开无线
        tmp.disconnect_ap()
        time.sleep(180)
        client_mac, frequencyBand, details = tmp.get_aps_status_eventLog(data_ap['7610_mac'])
        #获取无线网卡的mac
        wifi_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        self.assertEqual(wifi_mac.upper(), client_mac)
        self.assertEqual(0, details)
        print "check cloud ap status ap wpa/wpa2's eventlog offline display pass!"

    #AP的event log页面-ssid配置wep-64bit模式，client在线状态显示
    def test_076_aps_status_eventlog_wep64_online(self):
        u"""AP的event log页面-ssid配置wep-64bit模式，client在线状态显示(testlinkID:748-1)--bug113620"""
        log.debug("076")
        #修改ssid为wep64模式
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "0",
                    'ssid_wep_key': data_wireless['wep64']}
        data_dict = {'ssid_ssid_band': "5"}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(60)
        #无线网卡连接ap
        tmp = APSBusiness(self.s)
        tmp.connect_WEP_AP(data_wireless['all_ssid'],
                          data_wireless['wep64'],
                          data_basic['wlan_pc'])
        time.sleep(360)
        client_mac, frequencyBand, details = tmp.get_aps_status_eventLog(data_ap['7610_mac'])
        #获取无线网卡的mac
        wifi_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        self.assertEqual(wifi_mac.upper(), client_mac)
        self.assertEqual(1, details)
        print "check cloud ap status ap wep64's eventlog online display pass!"

    #AP的event log页面-ssid配置wep-64bit模式，client离线状态显示
    def test_077_aps_status_eventlog_wep64_offline(self):
        u"""AP的event log页面-ssid配置wep-64bit模式，client离线状态显示(testlinkID:748-2)--bug113620"""
        log.debug("077")
        tmp = APSBusiness(self.s)
        #断开无线
        tmp.disconnect_ap()
        time.sleep(180)
        client_mac, frequencyBand, details = tmp.get_aps_status_eventLog(data_ap['7610_mac'])
        #获取无线网卡的mac
        wifi_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        self.assertEqual(wifi_mac.upper(), client_mac)
        self.assertEqual(0, details)
        print "check cloud ap status ap wep64's eventlog offline display pass!"

    #AP的event log页面-ssid配置wep-128bit模式，client在线状态显示
    def test_078_aps_status_eventlog_wep128_online(self):
        u"""AP的event log页面-ssid配置wep-128bit模式，client在线状态显示(testlinkID:749-1)--bug113620"""
        log.debug("078")
        #修改ssid为wep128模式
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "1",
                    'ssid_wep_key': data_wireless['wep128']}
        data_dict = {'ssid_ssid_band': "5"}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(60)
        #无线网卡连接ap
        tmp = APSBusiness(self.s)
        tmp.connect_WEP_AP(data_wireless['all_ssid'],
                          data_wireless['wep128'],
                          data_basic['wlan_pc'])
        time.sleep(360)
        client_mac, frequencyBand, details = tmp.get_aps_status_eventLog(data_ap['7610_mac'])
        #获取无线网卡的mac
        wifi_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        self.assertEqual(wifi_mac.upper(), client_mac)
        self.assertEqual(1, details)
        print "check cloud ap status ap wep128's eventlog online display pass!"

    #AP的event log页面-ssid配置wep-128bit模式，client离线状态显示
    def test_079_aps_status_eventlog_wep128_offline(self):
        u"""AP的event log页面-ssid配置wep-128bit模式，client离线状态显示(testlinkID:749-2)--bug113620"""
        log.debug("079")
        tmp = APSBusiness(self.s)
        #断开无线
        tmp.disconnect_ap()
        time.sleep(180)
        client_mac, frequencyBand, details = tmp.get_aps_status_eventLog(data_ap['7610_mac'])
        #获取无线网卡的mac
        wifi_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        self.assertEqual(wifi_mac.upper(), client_mac)
        self.assertEqual(0, details)
        print "check cloud ap status ap wep128's eventlog offline display pass!"

    #AP的event log页面-ssid配置open模式，client在线状态显示
    def test_080_aps_status_eventlog_open_online(self):
        u"""AP的event log页面-ssid配置open模式，client在线状态显示(testlinkID:752-1)--bug113620"""
        log.debug("080")
        #修改ssid为open模式
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "4"}
        data_dict = {'ssid_ssid_band': "5"}
        tmp1.edit_ssid(data_ap['7610_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(60)
        #无线网卡连接ap
        tmp = APSBusiness(self.s)
        tmp.connect_NONE_AP(data_wireless['all_ssid'],
                          data_basic['wlan_pc'])
        time.sleep(360)
        client_mac, frequencyBand, details = tmp.get_aps_status_eventLog(data_ap['7610_mac'])
        #获取无线网卡的mac
        wifi_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        self.assertEqual(wifi_mac.upper(), client_mac)
        self.assertEqual(1, details)
        print "check cloud ap status ap open's eventlog online display pass!"

    #AP的event log页面-ssid配置open模式，client离线状态显示
    def test_081_aps_status_eventlog_open_offline(self):
        u"""AP的event log页面-ssid配置open模式，client离线状态显示(testlinkID:752-2)--bug113620"""
        log.debug("081")
        tmp = APSBusiness(self.s)
        #断开无线
        tmp.disconnect_ap()
        time.sleep(180)
        client_mac, frequencyBand, details = tmp.get_aps_status_eventLog(data_ap['7610_mac'])
        #获取无线网卡的mac
        wifi_mac = tmp.get_wlan_mac(data_basic['wlan_pc'])
        self.assertEqual(wifi_mac.upper(), client_mac)
        self.assertEqual(0, details)
        print "check cloud ap status ap open's eventlog offline display pass!"

    #AP的event log页面-Tools-ping，ipv4
    def test_082_aps_status_debug_ipv4_ping(self):
        u"""AP的event log页面-Tools-ping，ipv4(testlinkID:757)"""
        log.debug("082")
        #修改ssid为wpa2-aes
        tmp1 = SSIDSBusiness(self.s)
        encry_dict = {'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': data_wireless['short_wpa']}
        data_dict = {'ssid_ssid_band': "5",
                     'removed_macs': "%s,%s"%(data_ap['7610_mac'].upper(),
                                             data_ap['7600lr_mac'].upper())}
        tmp1.edit_ssid(data_ap['7600_mac'], data_wireless['all_ssid'],
                       encry_dict, data_dict)
        time.sleep(60)
        #接入点-状态-ap信息速率页面，获取调试结果
        tmp = APSBusiness(self.s)
        result = tmp.get_aps_status_ap_debug("IPv4 Ping", data_ap['7600_mac'],
                                             "www.baidu.com")
        self.assertIn('0% packet loss', result)
        print "check cloud ap status debug ipv4 ping pass!"

    #AP的event log页面-Tools-traceroute，ipv4
    def test_083_aps_status_debug_ipv4_traceroute(self):
        u"""AP的event log页面-Tools-traceroute，ipv4(testlinkID:756)"""
        log.debug("083")
        #接入点-状态-ap信息速率页面，获取调试结果
        tmp = APSBusiness(self.s)
        result = tmp.get_aps_status_ap_debug("IPv4 Traceroute", data_ap['7600_mac'],
                                             "www.qq.com")
        self.assertIn('traceroute to www.qq.com', result)
        print "check cloud ap status debug ipv4 traceroute pass!"

    #AP的event log页面-Tools-nslookup，ipv4
    def test_084_aps_status_debug_nslookup(self):
        u"""AP的event log页面-Tools-nslookup(testlinkID:760)"""
        log.debug("084")
        #接入点-状态-ap信息速率页面，获取调试结果
        tmp = APSBusiness(self.s)
        result = tmp.get_aps_status_ap_debug("Nslookup", data_ap['7600_mac'],
                                             "www.baidu.com")
        self.assertNotIn("nslookup: can't resolve", result)
        print "check cloud ap status debug nslookup pass!"

    #删除ap，并恢复cloud的初始环境
    def test_085_reset_cloud(self):
        u"""删除ap，并恢复cloud的初始环境"""
        log.debug("085")
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
