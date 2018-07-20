#coding=utf-8
#作者：曾祥卫
#时间：2018.03.19
#描述：cloud SSIDs的控制层


import time
from data import data
from publicControl.public_control import PublicControl



class SSIDSControl(PublicControl):

    def __init__(self, s):
        #继承PublicControl类的属性和方法
        PublicControl.__init__(self, s)

    ######################################################################
    #######以下是配置页面的方法##############################################
    #根据ssid来获取对应的id--ssids--配置页面
    def get_ssid_id(self, ssid):
        api = self.loadApi()['ssidList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api)
        ssid_lists = recvdata['data']['result']
        for i in range(len(ssid_lists)):
            if ssid == ssid_lists[i]['ssid']:
                ssid_id = ssid_lists[i]['id']
                print "ssid's id is %d"%ssid_id
                return ssid_id

    #ssids--配置页面，获取对应ssid在该页面的显示信息
    #输出：返回的是一个dict
    def get_ssid_info(self, ssid):
        api = self.loadApi()['ssidList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api)
        ssid_lists = recvdata['data']['result']
        for i in range(len(ssid_lists)):
            if ssid == ssid_lists[i]['ssid']:
                return ssid_lists[i]





    #cloud增加ssid:默认加密为wpa2-psk-aes--必须要有ssid，加密，membership_macs,,ssid_bintval,ssid_dtim_period
    def add_ssid(self, ap_mac, ssid, pwd):
        #ap的mac转换为大写
        MAC = ap_mac.upper()
        api = self.loadApi()['ssidEdit']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api,
                    {'membership_macs': "%s"%MAC,
                    'ssid_ssid': "%s"%ssid,
                    'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': "%s"%pwd,
                    'ssid_bintval':"100",
                    'ssid_dtim_period':"1"})
        return recvdata

    #cloud增加ssid,不添加ap:默认加密为wpa2-psk-aes--必须要有ssid，加密,,ssid_bintval,ssid_dtim_period
    def add_ssid_no_ap(self, ssid, pwd):
        api = self.loadApi()['ssidEdit']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api,
                    {'ssid_ssid': "%s"%ssid,
                    'ssid_encryption': "3",
                    'ssid_wpa_encryption': "0",
                    'ssid_wpa_key_mode': "0",
                    'ssid_wpa_key': "%s"%pwd,
                    'ssid_bintval':"100",
                    'ssid_dtim_period':"1"})
        return recvdata

    #cloud编辑ap--参数必须要带id，加密，membership_macs,ssid_bintval,ssid_dtim_period
    #输入：1.encry_dict：加密的字典参数，dict形式，eg.wpa2-psk-aes{'ssid_encryption': "3",
                    #'ssid_wpa_encryption': "0",
                    #'ssid_wpa_key_mode': "0",
                    #'ssid_wpa_key': 12345678}
            # data_dict:需要修改的参数，dict形式，eg. {'ssid_ssid_band': "2"}，
            # 或{'ssid_ssid_band': "5",'ssid_wpa_key': "88888888",
            # 'ssid_encryption': "3",
            #     'ssid_wpa_encryption': "0",
            #     'ssid_wpa_key_mode': "0"}等
    def edit_ssid(self, ap_mac, ssid, encry_dict,data_dict={}):
        #ap的mac转换为大写
        MAC = ap_mac.upper()
        #根据ssid来获取对应的id
        ssid_id = self.get_ssid_id(ssid)
        #配置替换
        dict1 = self.replaceConfig({'id': ssid_id,
                    'membership_macs': "%s"%MAC,
                    'ssid_bintval':"100",
                    'ssid_dtim_period':"1"}, encry_dict)
        dict2 = self.replaceConfig(dict1, data_dict)
        api = self.loadApi()['ssidEdit']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, dict2)
        return recvdata

    # def edit_ssid_no_ap(self, ssid, encry_dict,data_dict):
    #     #根据ssid来获取对应的id
    #     ssid_id = self.get_ssid_id(ssid)
    #     #配置替换
    #     dict1 = self.replaceConfig({'id': ssid_id,
    #                 'ssid_bintval':"100",
    #                 'ssid_dtim_period':"1"}, encry_dict)
    #     dict2 = self.replaceConfig(dict1, data_dict)
    #     api = self.loadApi()['ssidEdit']
    #     request = PublicControl()
    #     recvdata = request.apiRequest(api, dict2)
    #     return recvdata

    #cloud删除ssid
    def delete_ssid(self, ssid):
        #根据ssid来获取对应的id
        ssid_id = self.get_ssid_id(ssid)
        api = self.loadApi()['ssidDelete']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api,{'id': ssid_id})
        return recvdata

    #获取ssids中membership的已添加的设备
    def get_available_device(self, ssid):
        ssid_id = self.get_ssid_id(ssid)
        api = self.loadApi()['ssidMembershipItem']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api,{'id': ssid_id})
        results = recvdata['data']['available']
        result = []
        for i in range(len(results)):
            result.append(results[i]['key'])
        print result
        return result

    #获取ssids中membership的ap总数量
    def get_device_number(self, ssid):
        ssid_id = self.get_ssid_id(ssid)
        api = self.loadApi()['ssidMembershipItem']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api,{'id': ssid_id})
        results = recvdata['data']['result']
        result = len(results)
        print result
        return result

    ######################################################################
    #######以下是概要页面的方法##############################################
    #SSIDs-概要页面，获取客户端数量
    def get_ssids_summary_distribution_client_count(self, time):
        #确定time选择的类型
        if time == "2h":
            type = 0
        elif time == "1d":
            type = 1
        elif time == "1w":
            type = 2
        elif time == "1m":
            type = 3
        api = self.loadApi()['ssidClientsCount']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'type': type,
                                            'ssidId': "all_ssid",
                                            'menu': 2})
        clientcounts = recvdata['data']['ssid'][0]['count']
        print clientcounts
        return clientcounts

    #SSIDs-概要页面，获取速率
    def get_ssids_summary_distribution_bandwidth(self, time):
        #确定time选择的类型
        if time == "2h":
            type = 0
        elif time == "1d":
            type = 1
        elif time == "1w":
            type = 2
        elif time == "1m":
            type = 3
        api = self.loadApi()['ssidBandwidth']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'type': type,
                                            'ssidId': "all_ssid"})
        bd = recvdata['data']['bandwidth'][0]
        return bd

    #SSIDs-概要页面，获取ssid0的名称
    def get_ssids_summary_ssid0_name(self):
        api = self.loadApi()['ssidIdList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api)
        ssid0_name = recvdata['data']['result'][0]['label']
        print ssid0_name
        return ssid0_name