#coding=utf-8
#作者：曾祥卫
#时间：2018.07.10
#描述：captive portal--policy list的业务逻辑层
from policylist_control import PolicyListControl


class PolicyListBusiness(PolicyListControl):

    def __init__(self, s):
        #继承PolicyListControl类的属性和方法
        PolicyListControl.__init__(self, s)


