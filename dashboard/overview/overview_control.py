#coding=utf-8
#作者：曾祥卫
#时间：2018.06.14
#描述：cloud监控面板-概览的控制层


import time
from data import data
from publicControl.public_control import PublicControl




class OverViewControl(PublicControl):

    def __init__(self, s):
        #继承PublicControl类的属性和方法
        PublicControl.__init__(self, s)

    #获取监控面板-概览-AP总数
    def get_overview_ap_count(self):
        api = self.loadApi()['chartAp']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'menu': 0})
        result = recvdata['data']['total']
        print(result)
        return result

        #获取监控面板-概览-AP总数
    def get_network_overview_ap_count(self):
        api = self.loadApi()['chartAp']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'menu': 9})
        result = recvdata['data']['total']
        print(result)
        return result

    #这个接口可以抓到但目前没有用
    #获取监控面板--概览--ap总数
    def get_overview_ap_sum(self):
        api = self.loadApi()['topApList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api,{'menu': 0})
        result = recvdata['data']['total']
        print(result)
        return result

    #获取监控面板-概览-在线和离线AP数
    def get_overview_ap_online_offline_count(self):
        api = self.loadApi()['chartAp']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'menu': 0})
        results = recvdata['data']['categories']
        for result in results:
            if result['name'] == "online":
                online_ap_count = result['value']
            else:
                offline_ap_count = result['value']
        print(online_ap_count, offline_ap_count)
        return online_ap_count, offline_ap_count

    #进入某个network-概览-在线离线ap数
    def get_network_overview_ap_online_offline_count(self):
        api = self.loadApi()['chartAp']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'menu': 9})
        results = recvdata['data']['categories']
        for result in results:
            if result['name'] == "online":
                online_ap_count = result['value']
            else:
                offline_ap_count = result['value']
        print(online_ap_count, offline_ap_count)
        return online_ap_count, offline_ap_count


    #获取监控面板-概览-客户端总数
    def get_overview_client_count(self):
        api = self.loadApi()['chartClient']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'menu': 0})
        result = recvdata['data']['total']
        print(result)
        return result

    #获取监控面板-概览-客户端详细信息(数量)
    def get_overview_client_count_detail(self,menu=0):
        api = self.loadApi()['chartClient']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'menu': menu})
        result = recvdata['data']['categories']
        print(result)
        return result

    #获取network-概览-客户端总数
    def get_network_overview_client_count(self,menu=0):
        api = self.loadApi()['chartClient']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'menu': 9})
        result = recvdata['data']['total']
        print(result)
        return result

    #获取监控面板-概览-2.4G和5G客户端数
    def get_overview_client_online_offline_count(self,menu=0):
        api = self.loadApi()['chartClient']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'menu': menu})
        results = recvdata['data']['categories']
        for result in results:
            if result['name'] == "2.4G":
                g24_client_count = result['value']
            else:
                g5_client_count = result['value']
        print(g24_client_count, g5_client_count)
        return g24_client_count, g5_client_count

    #获取监控面板-概览-客户端数量，返回最后一条客户端在线数量
    def get_overview_last_clientcount(self, time,menu=0):
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
        recvdata = request.apiRequest(api, {'menu': menu, 'type': type})
        clientcount = recvdata['data']['clientCounts'][-1]
        return clientcount


    #获取监控面板-概览-速率，获取上传下载的bandwidth
    def get_overview_bandwidth(self, time,menu=0):
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
        recvdata = request.apiRequest(api, {'menu': menu, 'type': type})
        rx_bd = recvdata['data']['rxBandwidth']
        tx_bd = recvdata['data']['txBandwidth']
        return rx_bd, tx_bd

    #获取监控面板-概览-Top Aps，第一个ap的信息
    def get_overview_top_aps(self, time,menu=0):
        #确定time选择的类型
        if time == "2h":
            type = 0
        elif time == "1d":
            type = 1
        elif time == "1w":
            type = 2
        elif time == "1m":
            type = 3
        api = self.loadApi()['topApList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'menu': menu, 'type': type})
        ap_info = recvdata['data']['result'][0]
        return ap_info


    #获取监控面板-概览-Top Aps
    def get_overview_top_aps_info(self,time,menu=0):
        #确定time选择的类型
        if time == "2h":
            type = 0
        elif time == "1d":
            type = 1
        elif time == "1w":
            type = 2
        elif time == "1m":
            type = 3
        api = self.loadApi()['topApList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'menu': menu, 'type': type})
        ap_info = recvdata['data']['result']
        return ap_info

    #获取监控面板-概览-Top Clients，client的所有信息
    def get_overview_top_clients(self,time,menu=0):
        #确定time选择的类型
        if time == "2h":
            type = 0
        elif time == "1d":
            type = 1
        elif time == "1w":
            type = 2
        elif time == "1m":
            type = 3
        api = self.loadApi()['topClientList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'menu': menu, 'type': type})
        clients_info = recvdata['data']['result']
        return clients_info
        # mac = recvdata['data']['result'][0]['mac']
        # print(mac)
        # return mac

    #获取监控面板-概览-Top SSIDs，第一个SSID的name
    def get_overview_top_ssids(self, time,menu=0):
        #确定time选择的类型
        if time == "2h":
            type = 0
        elif time == "1d":
            type = 1
        elif time == "1w":
            type = 2
        elif time == "1m":
            type = 3
        api = self.loadApi()['topSsidList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'menu': menu, 'type': type})
        ssid_name = recvdata['data']['result'][0]['name']
        print(ssid_name)
        return ssid_name

    #获取监控面板-概览-Top SSIDs，第一个SSID的name
    def get_overview_top_ssids_info(self,time,menu=0):
        #确定time选择的类型
        if time == "2h":
            type = 0
        elif time == "1d":
            type = 1
        elif time == "1w":
            type = 2
        elif time == "1m":
            type = 3
        api = self.loadApi()['topSsidList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'menu': menu, 'type': type})
        ssid_detail = recvdata['data']['result']
        return ssid_detail

