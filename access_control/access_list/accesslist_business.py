#coding=utf-8
#作者：曾祥卫
#时间：2018.05.22
#描述：cloud 接入控制-接入列表的业务逻辑层


import time
from data import data
from accesslist_control import AccessListControl
from connect.ssh import SSH
from ssids.ssids_business import SSIDSBusiness



class AccessListBusiness(AccessListControl):

    def __init__(self, s):
        #继承AccessListControl类的属性和方法
        AccessListControl.__init__(self, s)

    #检查ap后台中，Global Blacklist是否有对应mac地址
    def check_Global_Blacklist_cli(self, host, user, pwd, mac):
        mac_tmp = mac.lower()
        ssh = SSH(host, pwd)
        result = ssh.ssh_cmd(user, "uci show wireless.global.client_ban")
        if mac_tmp in result:
            return True
        else:
            return False

    #检查ap后台中，Blacklist是否生效
    def check_Blacklist_cli(self, host, user, pwd, mac):
        mac_tmp = mac.lower()
        ssh = SSH(host, pwd)
        result01 = ssh.ssh_cmd(user, "uci show wireless.ath0.macfilter")
        result02 = ssh.ssh_cmd(user, "uci show wireless.ath0.maclist")
        result11 = ssh.ssh_cmd(user, "uci show wireless.ath1.macfilter")
        result12 = ssh.ssh_cmd(user, "uci show wireless.ath1.maclist")
        if ("deny" in result01) and ("deny" in result11) and \
            (mac_tmp in result02) and (mac_tmp in result12):
            return True
        else:
            return False

    #黑名单时选择多个Access list,检查mac地址是否在cli中
    def check_manyaccesslist_blacklist(self, client_mac, ap_mac,
                wifi_ssid, wifi_pwd, host, user, ssh_pwd):
        tmp = AccessListBusiness(self.s)
        #已有一个Access list1，先编辑
        macs = []
        macs2 = []
        macs3 = []
        macs.append(client_mac)
        tmp.edit_list("Access list1", macs)
        time.sleep(60)
        #然后再添加两个list
        random_mac2 = tmp.randomMAC()
        macs2.append(random_mac2)
        random_mac3 = tmp.randomMAC()
        macs3.append(random_mac3)
        tmp.add_list("Access list2", macs2)
        time.sleep(60)
        tmp.add_list("Access list3", macs3)
        time.sleep(60)
        #获取Access list的id
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
                    'ssid_wpa_key': wifi_pwd}
        data_dict = {'ssid_mac_filtering':"2",
                     'ssid_maclist_black':["%s"%id1, "%s"%id2, "%s"%id3]}
        tmp1.edit_ssid(ap_mac, wifi_ssid,
                       encry_dict, data_dict)
        time.sleep(120)
        result1 = tmp.check_Blacklist_cli(host, user, ssh_pwd, client_mac)
        result2 = tmp.check_Blacklist_cli(host, user, ssh_pwd, random_mac2)
        result3 = tmp.check_Blacklist_cli(host, user, ssh_pwd, random_mac3)
        return result1, result2, result3

    #检查ap后台中，Whitelist是否生效
    def check_Whitelist_cli(self, host, user, pwd, mac):
        mac_tmp = mac.lower()
        ssh = SSH(host, pwd)
        result01 = ssh.ssh_cmd(user, "uci show wireless.ath0.macfilter")
        result02 = ssh.ssh_cmd(user, "uci show wireless.ath0.maclist")
        result11 = ssh.ssh_cmd(user, "uci show wireless.ath1.macfilter")
        result12 = ssh.ssh_cmd(user, "uci show wireless.ath1.maclist")
        if ("allow" in result01) and ("allow" in result11) and \
            (mac_tmp in result02) and (mac_tmp in result12):
            return True
        else:
            return False

    #白名单时选择多个Access list,检查mac地址是否在cli中
    def check_manyaccesslist_whitelist(self, client_mac, ap_mac,
                wifi_ssid, wifi_pwd, host, user, ssh_pwd):
        tmp = AccessListBusiness(self.s)
        #已有三个Access list1，先编辑
        macs = []
        macs2 = []
        macs3 = []
        macs.append(client_mac)
        tmp.edit_list("Access list1", macs)
        time.sleep(60)
        #然后再编辑其他两个list
        random_mac2 = tmp.randomMAC()
        macs2.append(random_mac2)
        random_mac3 = tmp.randomMAC()
        macs3.append(random_mac3)
        tmp.edit_list("Access list2", macs2)
        time.sleep(60)
        tmp.edit_list("Access list3", macs3)
        time.sleep(60)
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
                    'ssid_wpa_key': wifi_pwd}
        data_dict = {'ssid_mac_filtering':"1",
                     'ssid_maclist_white':["%s"%id1, "%s"%id2, "%s"%id3]}
        tmp1.edit_ssid(ap_mac, wifi_ssid,
                       encry_dict, data_dict)
        time.sleep(120)
        result1 = tmp.check_Whitelist_cli(host, user, ssh_pwd, client_mac)
        result2 = tmp.check_Whitelist_cli(host, user, ssh_pwd, random_mac2)
        result3 = tmp.check_Whitelist_cli(host, user, ssh_pwd, random_mac3)
        return result1, result2, result3