#coding=utf-8
#作者：曾祥卫
#时间：2018.07.13
#描述：captive portal--vouchers的业务逻辑层

import time, subprocess
from data import data
from publicControl.public_control import PublicControl
from vouchers_control import VouchersControl




class VouchersBusiness(VouchersControl):

    def __init__(self, s):
        #继承VouchersControl类的属性和方法
        VouchersControl.__init__(self, s)