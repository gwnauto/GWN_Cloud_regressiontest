#coding=utf-8
#作者：曾祥卫
#时间：2018.07.19
#描述：captive portal--summary的控制层

from publicControl.public_control import PublicControl

class SummaryControl(PublicControl):

    def __init__(self, s):
        #继承PublicControl类的属性和方法
        PublicControl.__init__(self, s)

    #获取强制网络门户-概要-新增访客会话，返回最后一条客户端在线数量
    def get_portal_summary_GuestNewSession(self, time):
        #确定time选择的类型
        if time == "2h":
            type = 0
        elif time == "1d":
            type = 1
        elif time == "1w":
            type = 2
        elif time == "1m":
            type = 3
        api = self.loadApi()['portalSummaryGuest']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'ssidId': "all_ssid", 'type': type})
        clientcount = recvdata['data']['clientCounts'][-1]
        print("clientcount is {}".format(clientcount))
        return clientcount

    #获取访客认证会话中所有通过认证的方式
    def get_portal_summary_GuestSessionByAuthentication(self, time):
        #确定time选择的类型
        if time == "2h":
            type = 0
        elif time == "1d":
            type = 1
        elif time == "1w":
            type = 2
        elif time == "1m":
            type = 3
        api = self.loadApi()['portalSummaryRatio']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'ssidId': "all_ssid", 'type': type})
        categories = recvdata['data']['authTypeRatio']['categories']
        auth_categorie = [n['name'] for n in categories]
        return auth_categorie

    #获取访客SSID会话
    def get_portal_summary_GuestSessionBySSID(self):
        api = self.loadApi()['ssidIdList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api)
        result = recvdata['data']['result']
        ssids = [n['label'] for n in result]
        return ssids
