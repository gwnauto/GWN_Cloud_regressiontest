#coding=utf-8
#作者：曾祥卫
#时间：2018.07.11
#描述：captive portal的业务层


from captiveportal_control import CPControl
from ssids.ssids_business import SSIDSBusiness
from connect.ssh import SSH
from data import data
import time


data_basic = data.data_basic()

class CPBusiness(CPControl):

    def __init__(self, s):
        #继承CPControl类的属性和方法
        CPControl.__init__(self, s)

    #portal测试的准备工作
    def portal_test_ready(self,url,eth,ssid,wlan,wifi_encryption,password=None):
        #无线网卡释放ip地址
        self.dhcp_release_wlan(wlan)
        #禁用有线网卡
        self.wlan_disable(eth)
        time.sleep(30)
        #使用无线网卡连接ssid
        self.client_connect_ssid(ssid, wlan, wifi_encryption, password)
        #再次禁用有线网卡--防止无线网卡的多次连接时会重启全部网络导致有限网卡再次开启
        self.wlan_disable(eth)
        #循环三次检查无线网卡是否能够上网
        for i in range(3):
            #无线网卡释放ip地址
            self.dhcp_release_wlan(wlan)
            #无线网卡再次获取ip地址
            self.dhcp_wlan(wlan)
            self.move_resolv()
            #如果不能访问网络
            tmp = self.get_ping(url.strip("https").strip("://"))
            if tmp == 0 :
                break
            else:
                print "check wlan card can access internet or not,again."

    #portal测试的清理工作
    def portal_test_finish(self, wlan, eth):
        #无线网卡释放ip地址
        self.dhcp_release_wlan(wlan)
        #断开无线连接
        self.disconnect_ap()
        #启用有线网卡
        self.wlan_enable(eth)


    #使用无线客户端访问web页面，判断是否跳转到portal页面
    def check_jump_portal(self,url,eth,ssid,wlan,wifi_encryption,password=None):
        #portal测试的准备工作
        self.portal_test_ready(url,eth,ssid,wlan,wifi_encryption,password)
        #访问web页面，判断是否会跳转到portal页面
        result = self.check_redirect_portal(url)
        #portal测试的清理工作
        self.portal_test_finish(wlan, eth)
        print result
        return result

    #使用无线客户端访问web页面,并通过免费认证
    def check_NoAuth_portal(self,url,eth,ssid,wlan,wifi_encryption,\
                            title,password=None):
        #portal测试的准备工作
        self.portal_test_ready(url,eth,ssid,wlan,wifi_encryption,password)
        #使用免费认证通过认证
        resCode_NoAuth, resBody_NoAuth = self.set_NoAuth_access_portal(url)
        #判断认证是否通过
        result1 = self.check_access_portal(resCode_NoAuth, resBody_NoAuth)
        #判断访问外部web主页，并确定能改打开
        result2 = self.check_open_external_web(url, title)
        #portal测试的清理工作
        self.portal_test_finish(wlan, eth)
        print result1, result2
        return result1, result2

    #使用无线客户端访问web页面,并通过密码认证
    def check_PWDAuth_portal(self,url,eth,ssid,wlan,wifi_encryption,\
                             login_password,title,password=None):
        #portal测试的准备工作
        self.portal_test_ready(url,eth,ssid,wlan,wifi_encryption,password)
        #使用密码认证通过认证
        resCode_PWDAuth, resBody_PWDAuth = self.set_PWDAuth_access_portal(url,login_password)
        #判断认证是否通过
        result1 = self.check_access_portal(resCode_PWDAuth, resBody_PWDAuth)
        #判断访问外部web主页，并确定能改打开
        result2 = self.check_open_external_web(url, title)
        #portal测试的清理工作
        self.portal_test_finish(wlan, eth)
        print result1, result2
        return result1, result2

    #使用无线客户端访问web页面,并通过帐号认证
    def check_RadiusAuth_portal(self,url,eth,ssid,wlan,wifi_encryption,\
                             login_user,login_password,title,password=None):
        #portal测试的准备工作
        self.portal_test_ready(url,eth,ssid,wlan,wifi_encryption,password)
        #使用帐号认证通过认证
        resCode_RadiusAuth, resBody_RadiusAuth = self.set_RadiusAuth_access_portal(url,\
                                            login_user,login_password)
        #判断认证是否通过
        result1 = self.check_access_portal(resCode_RadiusAuth, resBody_RadiusAuth)
        #判断访问外部web主页，并确定能改打开
        result2 = self.check_open_external_web(url, title)
        #portal测试的清理工作
        self.portal_test_finish(wlan, eth)
        print result1, result2
        return result1, result2

    #使用无线客户端访问web页面,并通过微信认证
    def check_WeChatAuth_portal(self,url,eth,ssid,wlan,wifi_encryption,\
                             title,password=None):
        #portal测试的准备工作
        self.portal_test_ready(url,eth,ssid,wlan,wifi_encryption,password)
        #使用微信认证通过认证
        resCode_WeChatAuth, resBody_WeChatAuth = self.set_WeChatAuth_access_portal(url)
        #判断认证是否通过
        result1 = self.check_access_portal(resCode_WeChatAuth, resBody_WeChatAuth)
        #判断访问外部web主页，并确定能改打开
        result2 = self.check_open_external_web(url, title)
        #portal测试的清理工作
        self.portal_test_finish(wlan, eth)
        print result1, result2
        return result1, result2

    #使用无线客户端访问web页面,并通过凭据认证
    def check_VouchersAuth_portal(self,url,eth,ssid,wlan,wifi_encryption,\
                             title, Voucher_password, password=None):
        #portal测试的准备工作
        self.portal_test_ready(url,eth,ssid,wlan,wifi_encryption,password)
        #使用凭据认证通过认证
        resCode_VouchersAuth, resBody_VouchersAuth = \
            self.set_VouchersAuth_access_portal(url, Voucher_password)
        #判断认证是否通过
        result1 = self.check_access_portal(resCode_VouchersAuth, resBody_VouchersAuth)
        #判断访问外部web主页，并确定能改打开
        result2 = self.check_open_external_web(url, title)
         #portal测试的清理工作
        self.portal_test_finish(wlan, eth)
        print result1, result2
        return result1, result2

