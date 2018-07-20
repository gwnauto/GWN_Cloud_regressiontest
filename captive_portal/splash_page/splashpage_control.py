#coding=utf-8
#作者：曾祥卫
#时间：2018.07.10
#描述：captive portal--splash page的控制层

import time, subprocess
from data import data
from publicControl.public_control import PublicControl

class SplashPageControl(PublicControl):

    def __init__(self, s):
        #继承PublicControl类的属性和方法
        PublicControl.__init__(self, s)

    #获取已有的启动页名字对应的id
    def get_splashpage_id(self, name):
        api = self.loadApi()['portalPageList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api)
        page_lists = recvdata['data']
        for i in range(len(page_lists)):
            if name == page_lists[i]['name']:
                page_id = page_lists[i]['id']
                print "splash page's id is %d"%page_id
                return page_id