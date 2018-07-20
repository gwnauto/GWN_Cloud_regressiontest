#coding=utf-8
#作者：曾祥卫
#时间：2018.07.11
#描述：captive portal的控制层


import time, subprocess, logging, re, traceback
from data import data
from publicControl.public_control import PublicControl
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

data_basic = data.data_basic()


class CPControl(PublicControl):

    def __init__(self, s):
        #继承PublicControl类的属性和方法
        PublicControl.__init__(self, s)

    #无线网卡通过各种加密方式连接ssid
    #输入：wifi_encryption：ssid的加密方式
    def client_connect_ssid(self, ssid, wlan, wifi_encryption, password=None):
        if wifi_encryption == "open":
            self.connect_NONE_AP(ssid,wlan)
        elif wifi_encryption == "wep":
            self.connect_WEP_AP(ssid,password,wlan)
        elif wifi_encryption == "wpa":
            self.connect_WPA_AP(ssid,password,wlan)
        elif wifi_encryption == "wpa_hiddenssid":
            self.connect_WPA_hiddenssid_AP(ssid,password,wlan)
        elif wifi_encryption == "802.1x":
            self.connect_8021x_AP(ssid,data_basic['radius_usename'],
                data_basic['radius_password'],wlan)

    #访问外部web页面，返回响应码和响应体
    def access_external_web(self, url):
        try:
            if "https" in url:
                r = self.s.get(url, allow_redirects=False, verify=False)
            else:
                r = self.s.get(url, allow_redirects=False)
            resCode = r.status_code
            resBody = r.content
            #print "resBody is {}".format(resBody)
            return resCode, resBody
        except Exception as e:
            logging.error("Send http request fail! %s" % traceback.format_exc())
            return False

    #访问外部web页面，返回响应码和跳转的url
    def access_external_web_get_redirect(self, url):
        #访问外部web页面，返回响应码和响应体
        resCode, resBody = self.access_external_web(url)
        #使用正则表达式来取出跳转的url
        redirect_url = re.findall(r"redirURL = '(.+?)';", resBody)
        redirectUrl = redirect_url[0]
        print "redirect_url is {}".format(redirectUrl)
        print resCode, redirectUrl
        return resCode, redirectUrl

    #访问web页面，判断响应状态码和跳转的url是否跳转到portal页面
    def check_redirect_portal(self, url):
        #访问外部web页面，返回响应码和跳转的url
        resCode, redirectUrl = self.access_external_web_get_redirect(url)
        #判断响应码和跳转的url是否正确
        if (resCode == 200) and ("cwp.gwn.cloud" in redirectUrl):
            return True
        else:
            return False

    #使用免费认证通过认证
    def set_NoAuth_access_portal(self, url):
        #访问外部web页面，返回响应码和跳转的url
        resCode, redirectUrl = self.access_external_web_get_redirect(url)
        headers = {'Content-Type': 'application/json'}
        headers['Referer'] = redirectUrl
        portal_url = "http://cwp.gwn.cloud:8080/GsUserAuth.cgi"
        payload = {'GsUserAuthMethod': 0}
        r = self.s.post(portal_url, headers=headers, data=payload, allow_redirects=False)
        resCode_NoAuth = r.status_code
        resBody_NoAuth = r.json()
        print resCode_NoAuth, resBody_NoAuth
        return resCode_NoAuth, resBody_NoAuth

    #使用密码认证通过认证
    def set_PWDAuth_access_portal(self, url, login_password):
        #访问外部web页面，返回响应码和跳转的url
        resCode, redirectUrl = self.access_external_web_get_redirect(url)
        headers = {'Content-Type': 'application/json'}
        headers['Referer'] = redirectUrl
        portal_url = "http://cwp.gwn.cloud:8080/GsUserAuth.cgi"
        payload = {'GsUserAuthMethod': 13,
                   'GsUserRealReqUrl': "http%3A%2F%2Fwww.baidu.com",
                   'GsUserAuthPassword': login_password}
        r = self.s.post(portal_url, headers=headers, data=payload, allow_redirects=False)
        resCode_PWDAuth = r.status_code
        resBody_PWDAuth = r.json()
        print resCode_PWDAuth, resBody_PWDAuth
        return resCode_PWDAuth, resBody_PWDAuth

    #使用帐号认证通过认证
    def set_RadiusAuth_access_portal(self, url, login_user, login_password):
        #访问外部web页面，返回响应码和跳转的url
        resCode, redirectUrl = self.access_external_web_get_redirect(url)
        headers = {'Content-Type': 'application/json'}
        headers['Referer'] = redirectUrl
        portal_url = "http://cwp.gwn.cloud:8080/GsUserAuth.cgi"
        payload = {'GsUserAuthMethod': 1,
                   'GsUserRealReqUrl': "http%3A%2F%2Fwww.baidu.com",
                   'GsUserAuthName': login_user,
                   'GsUserAuthPassword': login_password}
        r = self.s.post(portal_url, headers=headers, data=payload, allow_redirects=False)
        resCode_RadiusAuth = r.status_code
        resBody_RadiusAuth = r.json()
        print resCode_RadiusAuth, resBody_RadiusAuth
        return resCode_RadiusAuth, resBody_RadiusAuth

    #使用微信认证通过认证
    def set_WeChatAuth_access_portal(self, url):
        #访问外部web页面，返回响应码和跳转的url
        resCode, redirectUrl = self.access_external_web_get_redirect(url)
        headers = {'Content-Type': 'application/json'}
        headers['Referer'] = redirectUrl
        headers['User-Agent'] = "WeChat/6.7.1.36 CFNetwork/902.2 Darwin/17.7.0"
        portal_url = "http://cwp.gwn.cloud:8080/GsUserAuth.cgi"
        # params = {'GsUserAuthMethod':2,
        #           'openId':'o7hZDvy0wOajngfqVhtuwjqIgnlQ',
        #           'tid':'440100010001416da55737c520e739286eded618b33709136920c9e44e29',
        #           'extend':"",
        #           'timestamp':'1532055593',
        #           'sign':'945a4c99d93822787fcb720f6b420e12'}
        params = {'GsUserAuthMethod':2,
                  'openId':'o7hZDvy0wOajngfqVhtuwjqIgnlQ'}
        r = self.s.get(portal_url, headers=headers, params=params, allow_redirects=False)
        resCode_WeChatAuth = r.status_code
        resBody_WeChatAuth = r.json()
        print resCode_WeChatAuth, resBody_WeChatAuth
        return resCode_WeChatAuth, resBody_WeChatAuth

    #使用微信认证通过认证--假的,微信认证前放行？
    def set_WeChatAuth_access_portal_backup(self, url):
        #访问外部web页面，返回响应码和跳转的url
        resCode, redirectUrl = self.access_external_web_get_redirect(url)
        headers = {'Content-Type': 'application/json'}
        headers['Referer'] = redirectUrl
        portal_url = "http://cwp.gwn.cloud:8080/GsUserAuth.cgi"
        params = {'GsUserAuthMethod': 100}
        r = self.s.get(portal_url, headers=headers, params=params, allow_redirects=False)
        resCode_WeChatAuth = r.status_code
        resBody_WeChatAuth = r.json()
        print resCode_WeChatAuth, resBody_WeChatAuth
        return resCode_WeChatAuth, resBody_WeChatAuth

    #使用凭据认证通过认证
    def set_VouchersAuth_access_portal(self, url, Voucher_password):
        #访问外部web页面，返回响应码和跳转的url
        resCode, redirectUrl = self.access_external_web_get_redirect(url)
        headers = {'Content-Type': 'application/json'}
        headers['Referer'] = redirectUrl
        portal_url = "http://cwp.gwn.cloud:8080/GsUserAuth.cgi"
        payload = {'GsUserAuthMethod': 12,
                   'GsUserRealReqUrl': "http%3A%2F%2Fwww.baidu.com",
                   'GsUserAuthPassword': Voucher_password}
        r = self.s.post(portal_url, headers=headers, data=payload, allow_redirects=False)
        resCode_VouchersAuth = r.status_code
        resBody_VouchersAuth = r.json()
        print resCode_VouchersAuth, resBody_VouchersAuth
        return resCode_VouchersAuth, resBody_VouchersAuth

    #使用facebook认证通过认证--假的,认证前放行？
    def set_FaceBookAuth_access_portal(self, url):
        #访问外部web页面，返回响应码和跳转的url
        resCode, redirectUrl = self.access_external_web_get_redirect(url)
        headers = {'Content-Type': 'application/json'}
        headers['Referer'] = redirectUrl
        portal_url = "http://cwp.gwn.cloud:8080/GsUserAuth.cgi"
        params = {'GsUserAuthMethod': 99}
        r = self.s.get(portal_url, headers=headers, params=params, allow_redirects=False)
        resCode_FaceBookAuth = r.status_code
        resBody_FaceBookAuth = r.json()
        print resCode_FaceBookAuth, resBody_FaceBookAuth
        return resCode_FaceBookAuth, resBody_FaceBookAuth

    #使用tiwtter认证通过认证--假的,认证前放行？
    def set_TiwtterAuth_access_portal(self, url):
        #访问外部web页面，返回响应码和跳转的url
        resCode, redirectUrl = self.access_external_web_get_redirect(url)
        headers = {'Content-Type': 'application/json'}
        headers['Referer'] = redirectUrl
        portal_url = "http://cwp.gwn.cloud:8080/GsUserAuth.cgi"
        params = {'GsUserAuthMethod': 101}
        r = self.s.get(portal_url, headers=headers, params=params, allow_redirects=False)
        resCode_TiwtterAuth = r.status_code
        resBody_TiwtterAuth = r.json()
        print resCode_TiwtterAuth, resBody_TiwtterAuth
        return resCode_TiwtterAuth, resBody_TiwtterAuth


    #判断认证是否通过
    def check_access_portal(self, resCode, resBody):
        if (resCode == 200) and (resBody['result'] == 1):
            return True
        else:
            return False

    #判断访问外部web主页，并确定能改打开
    def check_open_external_web(self, url, title):
        #访问外部web页面，返回响应码和响应体
        resCode, resBody = self.access_external_web(url)
        ResBody = resBody.decode('gbk')
        #print ResBody
        #使用正则表达式来取出title是否正确
        current_titles = re.findall(r"<title>(.+?)</title>", ResBody)
        current_title = current_titles[0]
        print resCode, current_title
        #判断响应码和title是否正确
        if (resCode == 200) and (current_title == title):
            return True
        else:
            return False

    # #判断访问外部web主页，并确定能改打开
    # def check_open_external_web_backup(self, url, title):
    #     if "https" in url:
    #         r = self.s.get(url, allow_redirects=False, verify=False)
    #     else:
    #         r = self.s.get(url, allow_redirects=False)
    #     resCode = r.status_code
    #     resBody = r.text.encode('utf-8')
    #     #使用正则表达式来取出title是否正确
    #     current_titles = re.findall(r"<title>(.+?)</title>", resBody)
    #     current_title = current_titles[0]
    #     print "current_title is {}".format(current_title)
    #     print resCode, current_title
    #     #判断响应码和title是否正确
    #     if (resCode == 200) and (current_title == title):
    #         return True
    #     else:
    #         return False
