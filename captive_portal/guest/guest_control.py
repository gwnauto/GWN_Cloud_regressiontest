#coding=utf-8
#作者：曾祥卫
#时间：2018.07.19
#描述：captive portal--guest的控制层

from publicControl.public_control import PublicControl

class GuestControl(PublicControl):

    def __init__(self, s):
        #继承PublicControl类的属性和方法
        PublicControl.__init__(self, s)

    #获取特定访客的所有信息
    def get_guest_info(self, client_mac):
        api = self.loadApi()['portalMonitorList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'pageNum':1,
                                            'pageSize':10})
        result = recvdata['data']['result']
        client_info = [n for n in result if n['clientId'] == client_mac.upper()]
        #print client_info
        return client_info[0]