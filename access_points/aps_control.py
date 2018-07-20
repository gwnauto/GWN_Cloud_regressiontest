#coding=utf-8
#作者：曾祥卫
#时间：2018.03.19
#描述：cloud接入点的控制层


import time
from data import data
from publicControl.public_control import PublicControl




class APSControl(PublicControl):

    def __init__(self, s):
        #继承PublicControl类的属性和方法
        PublicControl.__init__(self, s)

    ######################################################################
    #######以下是概要页面的方法##############################################
    #获取接入点-概要-AP信道分配
    #输出结果为两个列表，如：
    #chn_2g4：
    #[[1, 2], [2, 0], [3, 0], [4, 0], [5, 0], [6, 1], [7, 0],
    # [8, 0], [9, 0], [10, 0], [11, 0], [12, 0], [13, 0], [14, 0]]
    #chn_5g：
    #[[36, 2], [40, 0], [44, 0], [48, 0], [52, 0], [56, 0],
    # [60, 0], [64, 0], [100, 0], [104, 0], [108, 0], [112, 0],
    # [116, 0], [120, 0], [124, 0], [128, 0], [132, 0], [136, 0], [140, 0], [149, 0], [153, 1], [157, 0], [161, 0], [165, 0]]
    def get_aps_summary_channel_distribution(self):
        api = self.loadApi()['apChannel']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api)
        chn_2g4 = recvdata['data'][0]
        chn_5g = recvdata['data'][1]
        print chn_2g4, chn_5g
        return chn_2g4, chn_5g

    #获取接入点-概要-AP在线情况
    #输出：eg.total:3(整型)，
    # values：[{"name":"GWN7600","value":1},{"name":"GWN7600LR","value":1},
    # {"name":"GWN7610","value":1}]
    # categories：[{"name":"online","value":3},{"name":"offline","value":0}]
    def get_aps_summary_online(self):
        api = self.loadApi()['apSummary']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api)
        total = recvdata['data']['total']
        values = recvdata['data']['values']
        categories = recvdata['data']['categories']
        print total, values, categories
        return total, values, categories


    ######################################################################
    #######以下是状态页面的方法##############################################
    #获取接入点-状态-AP总数
    def get_aps_status_ap_number(self):
        api = self.loadApi()['apStatusList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'filter': {'showType': "all"},
                                            'pageNum':1,
                                            'pageSize':10})
        result = recvdata['data']['total']
        print result
        return result

    #获取接入点-状态-状态列表
    def get_aps_status_list(self):
        api = self.loadApi()['apStatusList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'filter': {'showType': "all"},
                                            'pageNum':1,
                                            'pageSize':10})
        result = recvdata['data']['result']
        print result
        return result

    #点击接入点-状态-清除流量
    def clear_ap_load(self,ap_mac):
        AP_MAC = ap_mac.upper()
        api = self.loadApi()['apClear']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'mac': AP_MAC})
        return recvdata

    #接入点-状态-搜索
    def status_search_ap(self,search_str):
        api = self.loadApi()['apStatusList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'search': search_str,
                                            'filter': {'showType': "all"},
                                            'pageNum':1,
                                            'pageSize':10})
        result = recvdata['data']['result']
        return result

    #接入点-状态-ap信息速率页面，获取上传下载的bandwidth
    def get_aps_status_chart_ap_bandwidth(self, time, ap_mac):
        AP_MAC = ap_mac.upper()
        #确定time选择的类型
        if time == "2h":
            type = 0
        elif time == "1d":
            type = 1
        elif time == "1w":
            type = 2
        elif time == "1m":
            type = 3
        api = self.loadApi()['chartBandUsage']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'type': type,
                                            'ssidId': "all_ssid",
                                            'menu': 1,
                                            'mac': AP_MAC})
        rx_bd = recvdata['data']['rxBandwidth']
        tx_bd = recvdata['data']['txBandwidth']
        return rx_bd, tx_bd

    #接入点-状态-ap信息速率页面，获取客户端数量
    def get_aps_status_ap_chart_client_count(self, time, ap_mac):
        AP_MAC = ap_mac.upper()
        #确定time选择的类型
        if time == "2h":
            type = 0
        elif time == "1d":
            type = 1
        elif time == "1w":
            type = 2
        elif time == "1m":
            type = 3
        api = self.loadApi()['chartClientsCount']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'type': type,
                                            'ssidId': "all_ssid",
                                            'menu': 1,
                                            'mac': AP_MAC})
        clientcounts = recvdata['data']['clientCounts']
        return clientcounts

    #获取接入点-状态-ap-当前客户端的信息
    def get_aps_status_clients_info(self,ap_mac):
        AP_MAC = ap_mac.upper()
        api = self.loadApi()['apClient']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api,{'pageNum': 1,
                                            'pageSize': 10,
                                            'savedPageNum': "apDetailClientListPageNum",
                                            'mac': AP_MAC})
        result = recvdata['data']
        print result
        return result

    #获取接入点-状态-ap-信息
    def get_aps_status_Info(self, ap_mac):
        AP_MAC = ap_mac.upper()
        api = self.loadApi()['apInfo']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'mac': AP_MAC})
        results = recvdata['data']['result']
        for result in results:
            #MAC
            if result['key'] == 'mac':
                MAC = result['value']
            #产品型号
            if result['key'] == 'apType':
                aptype = result['value']
            #PN
            if result['key'] == 'partNumber':
                PN = result['value']
            #引导程序
            if result['key'] == 'bootVersion':
                bootversion = result['value']
            #固件版本
            if result['key'] == 'firmwareVersion':
                FWversion = result['value']
        return MAC, aptype, PN, bootversion, FWversion

    #获取接入点-状态-ap-信息-ip,ssid,clientBridgeMode
    def get_aps_status_Info_ip_ssid_clientBridgeMode(self, ap_mac):
        AP_MAC = ap_mac.upper()
        api = self.loadApi()['apInfo']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'mac': AP_MAC})
        results = recvdata['data']['result']
        for result in results:
            #ip
            if result['key'] == 'ip':
                ip = result['value']
            if result['key'] == 'ssid':
                ssid = result['value']
            if result['key'] == 'clientBridgeMode':
                clientBridgeMode = result['value']
        return ip, ssid, clientBridgeMode

    #获取接入点-状态-ap-信息-2.4g radio status
    def get_aps_status_Info_2g4_radio(self,ap_mac):
        AP_MAC = ap_mac.upper()
        api = self.loadApi()['apInfo']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'mac': AP_MAC})
        results = recvdata['data']['result']
        for result in results:

            if result['key'] == 'g24':
                for r in result['value']:
                    #信道
                    if r['key'] == 'channel':
                        chn = r['value']
                    #客户端数量
                    if r['key'] == 'clients':
                        client_count = r['value']
                    #无线功率
                    if r['key'] == 'power':
                        power = r['value']
        return chn, client_count, power

    #获取接入点-状态-ap-信息-5g radio status
    def get_aps_status_Info_5g_radio(self,ap_mac):
        AP_MAC = ap_mac.upper()
        api = self.loadApi()['apInfo']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'mac': AP_MAC})
        results = recvdata['data']['result']
        for result in results:

            if result['key'] == 'g5':
                for r in result['value']:
                    #信道
                    if r['key'] == 'channel':
                        chn = r['value']
                    #客户端数量
                    if r['key'] == 'clients':
                        client_count = r['value']
                    #无线功率
                    if r['key'] == 'power':
                        power = r['value']
        return chn, client_count, power

    #获取接入点-状态-ap-事件日志-返回最后一条日志信息
    def get_aps_status_eventLog(self,ap_mac):
        AP_MAC = ap_mac.upper()
        api = self.loadApi()['apEventLog']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api,{'pageNum': 1,
                                            'pageSize': 10,
                                            'savedPageNum': "apDetailEventLogPageNum",
                                            'mac': AP_MAC})
        result = recvdata['data']['result'][0]
        client_mac = result['clientMac']
        frequencyBand = int(result['frequencyBand'])
        details = int(result['details'])#在线状态
        print client_mac, frequencyBand, details
        return client_mac, frequencyBand, details

    #接入点-状态-ap信息速率页面，获取调试结果
    def get_aps_status_ap_debug(self, tool, ap_mac, host):
        AP_MAC = ap_mac.upper()
        #确定tool选择的类型
        if tool == "IPv4 Ping":
            t = 0
        elif tool == "IPv6 Ping":
            t = 1
        elif tool == "IPv4 Traceroute":
            t = 2
        elif tool == "IPv6 Traceroute":
            t = 3
        elif tool == "Nslookup":
            t = 4
        api = self.loadApi()['debugForm']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'tool': t,
                                            'target': host,
                                            'mac': AP_MAC})
        clientcounts = recvdata['data']
        return clientcounts



    ######################################################################
    #######以下是配置页面的方法##############################################
    #cloud增加ap
    def add_ap(self, mac, pwd, name):
        '''
        添加AP
        :param mac: AP's mac
                password: AP's passwork in erp system
                name: AP' name，可为空
        :return:响应body--dict
        '''
        #mac转化为大写并去冒号
        MAC1 = mac.upper()
        MAC2 = self.mac_drop(MAC1)
        api = self.loadApi()['apAdd']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'mac': "%s"%MAC2, 'password': "%s"%pwd, 'name': "%s"%name})
        return recvdata


    #cloud删除ap
    def delete_ap(self, mac):
        '''
        删除AP
        :param mac:移动的AP的mac,批量删除时，用','分开，eg.'00:0b:82:af:d2:70,00:0b:82:af:d2:a0'
        :return:响应body--dict
        '''
        MAC1 = mac.upper()
        api = self.loadApi()['apDelete']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'mac': "%s"%MAC1})
        return recvdata

    #cloud删除ap
    def delete_many_ap(self, mac1, mac2):
        '''
        删除AP
        :param mac:移动的AP的mac,批量删除时，用','分开，eg.'00:0b:82:af:d2:70,00:0b:82:af:d2:a0'
        :return:响应body--dict
        '''
        MAC1 = mac1.upper()
        MAC2 = mac2.upper()
        api = self.loadApi()['apDelete']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'mac': "%s,%s"%(MAC1, MAC2)})
        return recvdata

    #cloud编辑AP
    #输入：edit_data:修改的数据，如1个数据[{'Fixed IP': 0}]或多个数据[{'Fixed IP': 0},{'Band Steering': 3}]
    def edit_ap(self, mac, data_dict):
        '''
            编辑AP
            :param: ap's mac.
                    data_dict:需要修改的参数，dict形式，eg. {"ap_2g4_channel": "3"}
        '''
        #mac转化为小写并去冒号
        mac1 = mac.lower()
        mac2 = self.mac_drop(mac1)
        #配置替换
        dict1 = self.replaceConfig({'ap_mac': "%s"%mac2}, data_dict)
        api = self.loadApi()['apConfig']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, dict1)
        time.sleep(10)
        return recvdata

    #按照设备类型进行过滤
    def configure_filter_ap(self, aptype):
        api = self.loadApi()['apConfigList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'pageNum': 1,
                                            'pageSize': 10,
                                            'filter': {'deviceType': aptype}
                                                })
        results = recvdata['data']['result']
        return results

    #按照设备进系搜索
    def configure_search_ap(self, search_str):
        api = self.loadApi()['apConfigList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'pageNum': 1,
                                            'pageSize': 10,
                                            'search': search_str
                                                })
        results = recvdata['data']['result']
        return results

    #设备类型过滤后再搜索
    def configure_filter_search_ap(self, aptype, search_str):
        api = self.loadApi()['apConfigList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'pageNum': 1,
                                            'pageSize': 10,
                                            'filter': {'deviceType': aptype},
                                            'search': search_str
                                                })
        results = recvdata['data']['result']
        return results

    #获取配置页面的ap信息
    def get_configure_ap_info(self):
        api = self.loadApi()['apConfigList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'pageNum': 1,
                                            'pageSize': 10
                                                })
        results = recvdata['data']['result']
        return results

    #点击定位键
    def click_locate(self, ap_mac):
        AP_MAC = ap_mac.upper()
        api = self.loadApi()['apLocate']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'mac': AP_MAC})
        return recvdata

    #重启单个ap
    def reboot_one_ap(self, ap_mac):
        AP_MAC = ap_mac.upper()
        api = self.loadApi()['apReboot']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'mac': AP_MAC})
        return recvdata

    #重启三个ap
    def reboot_many_aps(self, ap_mac1, ap_mac2, ap_mac3):
        AP_MAC1 = ap_mac1.upper()
        AP_MAC2 = ap_mac2.upper()
        AP_MAC3 = ap_mac3.upper()
        api = self.loadApi()['apReboot']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'mac': "%s,%s,%s"%(AP_MAC1, AP_MAC2, AP_MAC3)})
        return recvdata

    #批量移动ap
    #输入：aps_mac:"%s,%s,%s"%(AP_MAC1, AP_MAC2, AP_MAC3)
    #     network_id:网络组id
    def move_aps(self, aps_mac, network_id):
        api = self.loadApi()['apMove']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'mac': aps_mac,
                                            'networkId': network_id})
        return recvdata






