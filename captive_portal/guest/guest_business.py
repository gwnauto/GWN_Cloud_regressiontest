#coding=utf-8
#作者：曾祥卫
#时间：2018.07.19
#描述：captive portal--guest的业务逻辑层

from guest_control import GuestControl

class GuestBusiness(GuestControl):

    def __init__(self, s):
        #继承GuestControl类的属性和方法
        GuestControl.__init__(self, s)


    #检查特定访客的信息是否正确
    def check_client_info(self, client_mac, ap_mac, ssid, authType, portal_stats):
        #获取特定访客的所有信息
        client_info = self.get_guest_info(client_mac)
        #连接ap 的mac地址是否正确
        result_ap_mac = client_info['apId']
        #连接ap 的ssid是否正确
        result_ssid = client_info['ssid']
        #连接ap 的认证方式是否正确
        result_authType = client_info['authType']
        #认证状态
        result_portal_stats = client_info['portalStats']
        print(result_ap_mac,result_ssid,result_authType,result_portal_stats)
        result = (ap_mac.upper() in result_ap_mac) and (ssid == result_ssid)  and \
                (result_authType == authType) and (result_portal_stats == portal_stats)
        return result
