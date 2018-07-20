#coding=utf-8
#作者：曾祥卫
#时间：2018.07.19
#描述：captive portal--summary的业务逻辑层

from captive_portal.summary.summary_control import SummaryControl

class SummaryBusiness(SummaryControl):

    def __init__(self, s):
        #继承SummaryControl类的属性和方法
        SummaryControl.__init__(self, s)
