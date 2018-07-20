#coding=utf-8
#作者：曾祥卫
#时间：2018.05.31
#描述：cloud 接入控制-时间策略的业务逻辑层


import time
from data import data
from timepolicy_control import TimePolicyControl
from connect.ssh import SSH
from ssids.ssids_business import SSIDSBusiness



class TimePolicyBusiness(TimePolicyControl):

    def __init__(self, s):
        #继承TimePolicyControl类的属性和方法
        TimePolicyControl.__init__(self, s)

