#coding=utf-8
#描述:本模块用来调用数据，方便测试用例来调用
#作者：曾祥卫
#时间：2017.03.10

import random
import xlrd,xlwt
from xlutils.copy import copy
import os
dirname = os.path.dirname(__file__)
PATH = os.path.join(dirname, "data.xlsx")
#PATH = './data/data.xlsx'

#取得master ap的后6位mac地址
def master_last_6mac():
    data_ap = data_AP()
    master_ap = data_ap['7610_mac']
    #小写转换为大写
    Master_ap = master_ap.upper()
    #按：号分成列表
    tmp1 = Master_ap.split(":")
    #取第4个元素到最后一个元素
    tmp2 = tmp1[3:]
    #组合成字符串
    tmp3 = ''.join(tmp2)
    return tmp3

#取得master ap的后6位mac地址
def slave1_last_6mac():
    data_ap = data_AP()
    master_ap = data_ap['7600_mac']
    #小写转换为大写
    Master_ap = master_ap.upper()
    #按：号分成列表
    tmp1 = Master_ap.split(":")
    #取第4个元素到最后一个元素
    tmp2 = tmp1[3:]
    #组合成字符串
    tmp3 = ''.join(tmp2)
    return tmp3

#描述：读取data目录下/data/data.xlsx-basic_conf
#输入：None
#输出：以字典的形式输出basic中数据
def data_basic():
    try:
        #定义一个字典
        basic = {}
        #打开文件的工作空间
        xlsFile = xlrd.open_workbook(PATH)
        #获取对应的表-basic_conf
        table = xlsFile.sheet_by_name('basic_conf')
        #获取GWN7600的管理ip
        basic['7600_ip'] = table.cell_value(2,1)
        #获取GWN7600的管理web
        basic['7600_web'] = "https://%s"%basic['7600_ip']
        #获取管理员用户名
        basic['superUser'] = table.cell_value(3,1)
        #管理员默认密码
        basic['super_defalut_pwd'] = table.cell_value(4,1)
        #管理员默认密码
        basic['super_pwd'] = table.cell_value(4,2)
        #AP的ssh用户名
        basic['sshUser'] = table.cell_value(5,1)
        #Cloud中三种管理员的帐号
        basic['Cloud_test_user'] = table.cell_value(6,1)
        #Cloud中三种管理员的密码
        basic['Cloud_test_pwd'] = table.cell_value(6,2)
        #Cloud中三种管理员的email
        basic['Cloud_test_email'] = table.cell_value(6,3)
        #测试主机IP
        basic['PC_ip'] = table.cell_value(8,1)
        #测试主机密码
        basic['PC_pwd'] = table.cell_value(9,1)
        #测试主机无线网卡接口名
        basic['wlan_pc'] = table.cell_value(10,1)
        #测试AP固件版本
        basic['version'] = table.cell_value(11,1)
        #测试AP固件旧版本
        basic['old_version'] = table.cell_value(11,2)
        #获取GWN7610的AP的管理ip
        basic['7610_ip'] = table.cell_value(12,1)
        #获取GWN7610 AP的管理web
        basic['7610_web'] = "https://%s"%basic['7610_ip']
        #获取GWN7600lr的 AP的管理ip
        basic['7600lr_ip'] = table.cell_value(13,1)
        #获取GWN7600lr的 AP的管理web
        basic['7600lr_web'] = "https://%s"%basic['7600lr_ip']
        #测试主机有线网卡接口名
        basic['lan_pc'] = table.cell_value(14,1)
        #radius服务器的地址
        basic['radius_addr'] = table.cell_value(15,1)
        #radius服务器的密钥
        basic['radius_secrect'] = table.cell_value(15,2)
        #radius服务器的用户名
        basic['radius_usename'] = table.cell_value(15,3)
        #radius服务器的密码
        basic['radius_password'] = table.cell_value(15,4)
        #radius服务器中带VID的用户名
        basic['radius_VID_usename'] = table.cell_value(16,1)
        #radius服务器中带VID的密码
        basic['radius_VID_password'] = table.cell_value(16,2)
        #7600/7600LR升级版本号
        basic['7600_new_version'] = table.cell_value(17,1)
        #7600/7600LR降级版本号
        basic['7600_old_version'] = table.cell_value(17,2)
        #7610升级版本号
        basic['7610_new_version'] = table.cell_value(18,1)
        #7610降级版本号
        basic['7610_old_version'] = table.cell_value(18,2)
        #Cloud ssh登录的ip
        basic['Cloud_ssh_ip'] = table.cell_value(19,1)
        #Cloud ssh登录的用户名
        basic['Cloud_ssh_user'] = table.cell_value(19,2)
        #Cloud ssh登录的密码
        basic['Cloud_ssh_pwd'] = table.cell_value(19,3)
        #iperf服务器地址
        basic['iperf_ip'] = table.cell_value(20,1)

        #syslog，com口log和core file存放的scp地址
        basic['scp_server'] = table.cell_value(21,1)
        #syslog，com口log和core file存放的ftp路径
        basic['scp_dir'] = table.cell_value(21,2)
        #syslog，com口log和core file存放的ftp的用户名
        basic['scp_name'] = table.cell_value(21,3)
        #syslog，com口log和core file存放的ftp的密码
        basic['scp_pwd'] = table.cell_value(21,4)
        #将ap的外网cloud指定为本地cloud的hosts文件放置路径
        basic['ap_hosts_dir'] = table.cell_value(22,1)
        #登录Cloud的域名，用户名和密码
        basic['cloud_domain'] = table.cell_value(23,1)
        basic['cloud_user'] = table.cell_value(23,2)
        basic['cloud_pwd'] = table.cell_value(23,3)
        #portal认证中的密码认证的密码
        basic['portal_pwd'] = table.cell_value(24,1)
        #portal认证中的启动页面中新建的启动页的名称
        basic['splashpage_name'] = table.cell_value(25,1)
        ##########################################
        ###以下是GWN7000的数据
        ##########################################
        #获取GWN7000的管理ip
        basic['7000_ip'] = table.cell_value(32,1)
        #获取GWN76xx的管理web
        basic['7000_web'] = "https://%s"%basic['7000_ip']
        #获取管理员用户名
        basic['7000_superUser'] = table.cell_value(33,1)
        #管理员的密码
        basic['7000_pwd'] = table.cell_value(34,1)

        #######################################
        #测试专用的firefox的profile路径
        basic['firefox_profile'] = table.cell_value(36,1)
        return basic
    except IOError,e:
        print u"文件信息错误,具体信息：\n%s"%e

#描述：读取data目录下/data/data.xlsx-login_conf
#输入：None
#输出：以字典的形式输出login中数据
def data_login():
    try:
        #定义一个字典
        data = {}
        #打开文件的工作空间
        xlsFile = xlrd.open_workbook(PATH)
        #获取对应的表-login_conf
        table = xlsFile.sheet_by_name('login_conf')
        #获取数字密码
        data['digital_pwd'] = table.cell_value(2,1)
        #获取字母密码
        data['letter_pwd'] = table.cell_value(3,1)
        #获取asii密码
        data['asii_pwd'] = table.cell_value(4,1)
        #数字字母混合
        data['digital_letter'] = table.cell_value(5,1)
        #数字和ASII码混合
        data['digital_asii'] = table.cell_value(6,1)
        #字母和ASII码混合
        data['letter_asii'] = table.cell_value(7,1)
        #数字字母asii混合
        data['digital_letter_asii'] = table.cell_value(8,1)
        super_pwd = data_basic()
        data['all'] = super_pwd['super_pwd']
        #空
        data['blank'] = table.cell_value(20,1)
        #中文
        data['chineses'] = table.cell_value(21,1)
        return data
    except IOError,e:
        print u"文件信息错误,具体信息：\n%s"%e


#描述：读取data目录下/data/data.xlsx-wireless_conf
#输入：None
#输出：以字典的形式输出wireless中数据
def data_wireless():
    try:
        #定义一个字典
        data = {}
        #打开文件的工作空间
        xlsFile = xlrd.open_workbook(PATH)
        #获取对应的表-wireless_conf
        table = xlsFile.sheet_by_name('Wireless_conf')
        #获取全数字ssid
        data['digital_ssid'] = table.cell_value(2,1)
        #获取字母ssid
        data['letter_ssid_part'] = table.cell_value(3,1)
        data['letter_ssid'] = data['letter_ssid_part']+master_last_6mac()
        #数字字母asii混合
        data['all_ssid_part'] = table.cell_value(4,1)
        data['all_ssid'] = data['all_ssid_part']+master_last_6mac()
        data['grou1_all_ssid'] = data['all_ssid_part']+slave1_last_6mac()

        #额外ssid-数字字母asii混合
        data['add_ssid'] = table.cell_value(4,2)
        #ASCII码
        data['ascii_ssid'] = table.cell_value(5,1)
        #数字和字母混合
        data['digital_letter_ssid'] = table.cell_value(6,1)
        #最短ssid
        data['short_ssid'] = table.cell_value(7,1)
        #最长ssid
        data['long_ssid'] = table.cell_value(8,1)
        #中文SSID
        data['CN_ssid'] = table.cell_value(9,1)
        #wep64加密
        data['wep64'] = table.cell_value(10,1)
        #wep64加密-10
        data['wep64-10'] = table.cell_value(10,2)
        #wep128加密
        data['wep128'] = table.cell_value(11,1)
        #wep128加密-26
        data['wep128-26'] = table.cell_value(11,2)
        #异常wep密码1
        data['abnormal1_wep'] = table.cell_value(10,3)
        #异常wep密码2
        data['abnormal2_wep'] = table.cell_value(11,3)
        #wpa最短加密
        data['short_wpa'] = table.cell_value(12,1)
        #wpa各种字符串密码
        data['all_wpa'] = table.cell_value(12,2)
        #错误的WPA密码
        #data['error_wpa'] = table.cell_value(12,3)
        #wpa最长加密
        data['long_wpa'] = table.cell_value(13,1)
        #特殊符号SSID
        data['special_ssid'] = table.cell_value(14,1)
        return data
    except IOError,e:
        print u"文件信息错误,具体信息：\n%s"%e

#描述：读取data目录下/data/data.xlsx-networkgroup_conf
#输入：None
#输出：以字典的形式输出networkgroup中数据
def data_networkgroup():
    try:
        #定义一个字典
        data = {}
        #打开文件的工作空间
        xlsFile = xlrd.open_workbook(PATH)
        #获取对应的表-networkgroup_conf
        table = xlsFile.sheet_by_name('networkgroup_conf')
        #获取网络组名前缀
        data['NG2_name'] = table.cell_value(2,1)
        #获取网络组的ssid前缀
        data['NG2_ssid'] = table.cell_value(3,1)
        #获取32位网络组名
        data['NG_name32'] = table.cell_value(4,1)
        #获取40位网络组名
        data['NG_name40'] = table.cell_value(5,1)
        #获取最小VLAN ID
        data['min_VID'] = table.cell_value(6,1)
        #获取最大VLAN ID
        data['max_VID'] = table.cell_value(7,1)
        #获取小于最小VLAN ID
        data['out_min'] = table.cell_value(8,1)
        #获取大于最大VLAN ID
        data['out_max'] = table.cell_value(9,1)
        #获取所有的VID
        data["all_VID"] = table.col_values(1)[6:10]

        #获取网络组-编辑-wifi页面-id1
        data["wifi_pagedown_id1"] = table.cell_value(32,1)
        #获取网络组-编辑-wifi页面-id2
        data["wifi_pagedown_id2"] = table.cell_value(33,1)
        #获取网络组-编辑-wifi页面-id3
        data["wifi_pagedown_id3"] = table.cell_value(37,1)
        #获取网络组-编辑-基本页面-id1
        data["basic_pagedown_id1"] = table.cell_value(34,1)
        #获取网络组-编辑-基本页面-id2
        data["basic_pagedown_id2"] = table.cell_value(35,1)
        #获取网络组-编辑-基本页面-id3
        data["basic_pagedown_id3"] = table.cell_value(36,1)

        #获取ssid-编辑-wifi页面-id1
        data["ssid_wifi_pagedown_id1"] = table.cell_value(42,1)
        #获取额外ssid-编辑-wifi页面-id2
        data["ssid_wifi_pagedown_id2"] = table.cell_value(43,1)
        #获取额外ssid-编辑-wifi页面-id3
        data["ssid_wifi_pagedown_id3"] = table.cell_value(44,1)
        #获取额外ssid-编辑-wifi页面-id4
        data["ssid_wifi_pagedown_id4"] = table.cell_value(45,1)
        #获取额外ssid-编辑-wifi页面-id5
        data["ssid_wifi_pagedown_id5"] = table.cell_value(46,1)
        return data
    except IOError,e:
        print u"文件信息错误,具体信息：\n%s"%e

#描述：读取data目录下/data/data.xlsx-AP_conf
#输入：None
#输出：以字典的形式输出AP中数据
def data_AP():
    try:
        #定义一个字典
        data = {}
        #打开文件的工作空间
        xlsFile = xlrd.open_workbook(PATH)
        #获取对应的表-basic_conf
        table1 = xlsFile.sheet_by_name('basic_conf')
        #获取7600 ap的mac地址
        data['7600_mac'] = table1.cell_value(2,2).lower().strip(" ")
        #获取7610 ap的mac地址
        data['7610_mac'] = table1.cell_value(12,2).lower().strip(" ")
        #获取7600lr ap的mac地址
        data['7600lr_mac'] = table1.cell_value(13,2).lower().strip(" ")

        #获取对应的表-networkgroup_conf
        table = xlsFile.sheet_by_name('AP_conf')

        #7610的功率期望值
        #2.4G,11信道，ap stream1的发射功率期望值
        data['7610_2g4_stream1_powers'] = table.row_values(2)[1:4]
        #2.4G,11信道，slave ap stream2的发射功率期望值
        data['7610_2g4_stream2_powers'] = table.row_values(3)[1:4]
        #2.4G,11信道，slave ap stream3的发射功率期望值
        data['7610_2g4_stream3_powers'] = table.row_values(4)[1:4]
        #5G,11信道，slave ap stream1的发射功率期望值
        data['7610_5g_stream1_powers'] = table.row_values(6)[1:4]
        #5G,11信道，slave ap stream2的发射功率期望值
        data['7610_5g_stream2_powers'] = table.row_values(7)[1:4]
        #5G,11信道，slave ap stream3的发射功率期望值
        data['7610_5g_stream3_powers'] = table.row_values(8)[1:4]

        #7600的功率期望值
        #2.4G,11信道，ap stream1的发射功率期望值
        data['7600_2g4_stream1_powers'] = table.row_values(2)[6:9]
        #2.4G,11信道，slave ap stream2的发射功率期望值
        data['7600_2g4_stream2_powers'] = table.row_values(3)[6:9]
        #5G,11信道，slave ap stream1的发射功率期望值
        data['7600_5g_stream1_powers'] = table.row_values(6)[6:9]
        #5G,11信道，slave ap stream2的发射功率期望值
        data['7600_5g_stream2_powers'] = table.row_values(7)[6:9]

        #7600lr的功率期望值
        #2.4G,11信道，ap stream1的发射功率期望值
        data['7600lr_2g4_stream1_powers'] = table.row_values(2)[11:14]
        #2.4G,11信道，slave ap stream2的发射功率期望值
        data['7600lr_2g4_stream2_powers'] = table.row_values(3)[11:14]
        #5G,11信道，slave ap stream1的发射功率期望值
        data['7600lr_5g_stream1_powers'] = table.row_values(6)[11:14]
        #5G,11信道，slave ap stream2的发射功率期望值
        data['7600lr_5g_stream2_powers'] = table.row_values(7)[11:14]



        #获取自定义功率值--高
        data['high_power'] = table.cell_value(11,1)
        #获取自定义功率值--中
        data['medium_power'] = table.cell_value(11,2)
        #获取自定义功率值--低
        data['lower_power'] = table.cell_value(11,3)
        #获取自定义功率值--所有值
        data['custom_powers'] = table.row_values(11)[1:4]
        #获取最小自定义功率值
        data['min_power'] = table.cell_value(12,1)
        #获取最大自定义功率值
        data['max_power'] = table.cell_value(13,1)
        #获取小于最小自定义功率值
        data['less_min_powers'] = table.row_values(14)[1:3]
        #获取大于最大自定义功率值
        data['more_max_powers'] = table.row_values(15)[1:3]
        #获取特殊字符的自定义功率值
        data['letter_power'] = table.cell_value(16,1)
        #测试各空间流时选取的自定义功率值
        data['stream_powers'] = table.row_values(17)[1:7]

        #指定固定ip地址
        data['fixed_ip'] = table.cell_value(31,1)
        #指定固定ip的子网掩码
        data['fixed_netmask'] = table.cell_value(32,1)
        #不合法的固定ip地址
        data['validity_fixed_ip'] = table.cell_value(31,2)
        #指定固定ip的子网掩码2
        data['fixed_netmask2'] = table.cell_value(32,3)
        #更多ip地址
        data['fixed_ip1'] = table.cell_value(31,3)
        #不合法的固定ip的子网掩码
        data['validity_fixed_netmask'] = table.cell_value(32,2)
        #获取设备名称（大小写字母）
        data['letter_device_name'] = table.cell_value(33,1)
        #获取设备名称（纯数字）
        data['digital_device_name'] = table.cell_value(34,1)
        #获取设备名称（大小写字符+纯数字）
        data['all_device_name'] = table.cell_value(35,1)
        #上海交大ipv6_1
        data["SH_ipv6_1"] = table.cell_value(36,1)
        #上海交大ipv6_1
        data["SH_ipv6_2"] = table.cell_value(37,1)
        #北邮ipv6_1
        data["BY_ipv6_1"] = table.cell_value(38,1)
        #北邮ipv6_2
        data["BY_ipv6_2"] = table.cell_value(39,1)

        #获取接入点-编辑-配置页面-id1
        data["config_pagedown_id1"] = table.cell_value(51,1)
        return data
    except IOError,e:
        print u"文件信息错误,具体信息：\n%s"%e

#描述：读取data目录下/data/data.xlsx-Client_conf
#输入：None
#输出：以字典的形式输出Client中数据
def data_Client():
    try:
        #定义一个字典
        data = {}
        #打开文件的工作空间
        xlsFile = xlrd.open_workbook(PATH)
        #获取对应的表-networkgroup_conf
        table = xlsFile.sheet_by_name('Client_conf')

        #以下是client的数据
        #获取英文+数字的客户端名
        data['letter_digital_name'] = table.cell_value(2,1)
        #获取数字的客户端名
        data['digital_name'] = table.cell_value(3,1)
        #获取字母的客户端名
        data['letter_name'] = table.cell_value(4,1)
        #获取前缀为---的客户端名
        data['err_name1'] = table.cell_value(5,1)
        #获取前缀为___的客户端名
        data['err_name2'] = table.cell_value(6,1)

        #格式错误的mac地址
        data['err_format_mac'] = table.cell_value(8,1)
        #中文的mac地址
        data['chn_mac'] = table.cell_value(9,1)
        #特殊字符的mac地址
        data['special_mac'] = table.cell_value(10,1)


        #以下是clientaccess的数据
        #列表名称
        data['list_name'] = table.cell_value(31,1)
        return data
    except IOError,e:
        print u"文件信息错误,具体信息：\n%s"%e

#描述：读取data目录下/data/data.xlsx-navbar_conf
#输入：None
#输出：以字典的形式输出navbar中数据
def data_navbar():
    try:
        #定义一个字典
        data = {}
        #打开文件的工作空间
        xlsFile = xlrd.open_workbook(PATH)
        #获取对应的表-networkgroup_conf
        table = xlsFile.sheet_by_name('navbar_conf')
        #获取不存在的内容字符串
        data['inexistence_info'] = table.cell_value(2,1)

        return data
    except IOError,e:
        print u"文件信息错误,具体信息：\n%s"%e

#描述：读取data目录下/data/data.xlsx-TimeZone_conf
#输入：None
#输出：以字典的形式输出TimeZone中数据
def data_timezone():
    try:
        #定义一个字典
        data = {}
        #打开文件的工作空间
        xlsFile = xlrd.open_workbook(PATH)
        #获取对应的表-TimeZone_conf
        table = xlsFile.sheet_by_name('TimeZone_conf')
        #获取时区列表
        data['timezone_list'] = table.col_values(0)[2:94]
        #获取时区对应的字符串
        data['timezone_str'] = table.col_values(1)[2:94]

        return data
    except IOError,e:
        print u"文件信息错误,具体信息：\n%s"%e


#描述：读取data目录下/data/data.xlsx-countrycode_conf
#输入：None
#输出：以列表的形式输出countrycode_conf中数据
def data_countrycode():
    try:
        #定义一个列表
        data = {}
        #打开文件的工作空间
        xlsFile = xlrd.open_workbook(PATH)
        #获取对应的表-countrycode_conf
        table = xlsFile.sheet_by_name('countrycode_conf')
        #获取国家名称
        data['country'] = table.col_values(0)[2:119]
        #获取国家代码
        data['ctycode'] = table.col_values(1)[2:119]
        #获取2.4G发射功率
        data['rate_2g'] = table.col_values(2)[2:119]
        #获取5G发射功率1
        data['rate_5g_band1'] = table.col_values(3)[2:119]
        #获取5G发射功率2
        data['rate_5g_band2'] = table.col_values(4)[2:119]
        return data
    except IOError,e:
        print u"文件信息错误,具体信息：\n%s"%e






#设置excel表的单元格样式
#输入：bold:是否粗写
def set_style(bold=False):
    style = xlwt.XFStyle() # 初始化样式
    font = xlwt.Font() # 为样式创建字体
    font.name = 'Times New Roman' # 'Times New Roman'
    font.bold = bold
    font.color_index = 4
    font.height = 220
    style.font = font
    return style

#创建excel
#输入：excel_name:excel表格名称;row_m:第m次要输入的结果（为列表）
def create_excel(excel_name,row0):
    #创建工作簿
    f = xlwt.Workbook()
    #创建sheet1
    sheet1 = f.add_sheet('sheet1',cell_overwrite_ok=True)
    #生成第一行
    for i in range(len(row0)):
        sheet1.write(0,i,row0[i],set_style(True))
    # row0 = [u'次数',u'配对',u'解除配对']
    f.save('%s.xls'%excel_name) #保存文件
    print "create excel successfully!"



#追加写excel-增加一行
#输入：excel_name:excel表格名称;row_m:第m次要输入的结果（为列表）
def add_excel_row(excel_name,row_m):
    #用xlrd提供的方法打开文件的工作空间
    f = xlrd.open_workbook('%s.xls'%excel_name)
    #用xlrd提供的方法获得现在已有的行数
    rows = f.sheets()[0].nrows
    #用xlutils提供的copy方法将xlrd的对象转化为xlwt的对象
    excel = copy(f)
    #用xlwt对象的方法获得要操作的sheet
    table = excel.get_sheet(0)
    #生成第m行
    table.write(rows,0,rows,set_style())
    for i in range(len(row_m)):
        table.write(rows,i+1,row_m[i],set_style())

    excel.save('%s.xls'%excel_name) #保存文件
    print "add to write excel successfully!"

#追加写excel-增加某个坐标的内容
#输入：excel_name:excel表格名称;row_n:写入第几行;column_n:写入第几列;content:写入的内容(字符串)
def add_excel_content(excel_name,row_n,column_n,content):
    #用xlrd提供的方法打开文件的工作空间
    f = xlrd.open_workbook('%s.xls'%excel_name)
    #用xlutils提供的copy方法将xlrd的对象转化为xlwt的对象
    excel = copy(f)
    #用xlwt对象的方法获得要操作的sheet
    table = excel.get_sheet(0)
    #生成第n行
    table.write(row_n,column_n,content,set_style())
    excel.save('%s.xls'%excel_name) #保存文件
    print "add to write excel successfully!"




