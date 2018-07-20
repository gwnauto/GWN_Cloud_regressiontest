#coding=utf-8
#作者：曾祥卫
#时间：2018.03.19
#描述：cloud接入点的业务层


from aps_control import APSControl
from connect.ssh import SSH
from data import data
import time, subprocess

data_basic = data.data_basic()
data_ap = data.data_AP()

class APSBusiness(APSControl):

    def __init__(self, s):
        #继承APSControl类的属性和方法
        APSControl.__init__(self, s)

    ######################################################################
    #######以下是状态页面的方法##############################################

    #判断产品型号和对应的mac地址显示正确
    def check_ap_status_type_mac(self):
        result = []
        #获取接入点-状态-状态列表
        tmps = self.get_aps_status_list()
        for tmp in tmps:
            if tmp['apType'] == 'GWN7600':
                if tmp['mac'] == data_ap['7600_mac'].upper():
                    result.append(True)
                else:
                    result.append(False)

            if tmp['apType'] == 'GWN7610':
                if tmp['mac'] == data_ap['7610_mac'].upper():
                    result.append(True)
                else:
                    result.append(False)

            if tmp['apType'] == 'GWN7600LR':
                if tmp['mac'] == data_ap['7600lr_mac'].upper():
                    result.append(True)
                else:
                    result.append(False)
        print result
        return result

    #判断ap名称是否正确
    def check_ap_status_device_name(self, aptype, device_name):
        #获取接入点-状态-状态列表
        tmps = self.get_aps_status_list()
        for tmp in tmps:
            if tmp['apType'] == aptype:
                if tmp['name'] == device_name:
                    return True
        return False

    #判断ap ip是否正确
    def check_ap_status_ip(self, aptype, ap_ip):
        #获取接入点-状态-状态列表
        tmps = self.get_aps_status_list()
        for tmp in tmps:
            if tmp['apType'] == aptype:
                if tmp['ip'] == ap_ip:
                    return True
        return False

    #判断ap运行状态
    def check_ap_status_online(self, aptype):
        #获取接入点-状态-状态列表
        tmps = self.get_aps_status_list()
        for tmp in tmps:
            if tmp['apType'] == aptype:
                if tmp['status'] == 1:
                    return True
        return False

    #取出ap运行时间
    def get_ap_status_uptime(self, aptype):
        #获取接入点-状态-状态列表
        tmps = self.get_aps_status_list()
        for tmp in tmps:
            if tmp['apType'] == aptype:
                result = tmp['upTime']
                print result
                return result

    #登录ap后台，取ap运行时间的字符串
    def get_ap_ssh_uptime(self,host, user, pwd):
        ssh = SSH(host, pwd)
        uptime = ssh.ssh_cmd(user,"uptime")
        tmp = uptime.split("up ")[1].split(" min")[0]
        result = int(tmp)*60
        print result
        return result

    #判断ap的运行时间是否显示正确
    def check_ap_status_uptime(self, host, user, pwd, aptype):
        #登录ap后台，取ap运行时间的字符串
        ssh_uptime = self.get_ap_ssh_uptime(host, user, pwd)
        #取出cloud中ap运行时间
        cloud_uptime = self.get_ap_status_uptime(aptype)
        #取两者的差值
        result = ssh_uptime - cloud_uptime
        print result
        return result


    #AP 下载流量统计的准确性-50M
    def run_AP_download_backup(self,ssid,password,wlan,lan):
        #无线网卡连接master ap
        self.connect_DHCP_WPA_AP(ssid,password,wlan)
        #禁用有线网卡
        self.wlan_disable(lan)
        i =0
        while i<3:
            tmp = self.get_ping(data_basic['iperf_ip'])
            if tmp == 0:
                #描述：使用iperf3进行下载
                tmp1 = subprocess.call("iperf3 -c %s -n 50M -R"%data_basic['iperf_ip'],shell=True)
                print tmp1
                break
            else:
                self.wlan_enable(lan)
                self.dhcp_release_wlan(wlan)
                self.dhcp_wlan(wlan)
                self.wlan_disable(lan)
                print "run iperf3 fail,try %s again!"%(i+1)
                i = i+1
                continue
        #启用有线网卡
        self.wlan_enable(lan)
        #使无线网卡释放IP地址
        self.dhcp_release_wlan(wlan)
        # #断开无线
        # self.disconnect_ap()

    #AP 上传流量统计的准确性-50M
    def run_AP_upload_backup(self,ssid,password,wlan,lan):
        #无线网卡连接master ap
        self.connect_DHCP_WPA_AP(ssid,password,wlan)
        #禁用有线网卡
        self.wlan_disable(lan)
        i =0
        while i<3:
            tmp = self.get_ping(data_basic['iperf_ip'])
            if tmp == 0:
                #描述：使用iperf3进行上传
                tmp1 = subprocess.call("iperf3 -c %s -n 50M"%data_basic['iperf_ip'],shell=True)
                print tmp1
                break
            else:
                self.wlan_enable(lan)
                self.dhcp_release_wlan(wlan)
                self.dhcp_wlan(wlan)
                self.wlan_disable(lan)
                print "run iperf3 fail,try %s again!"%(i+1)
                i = i+1
                continue
        #启用有线网卡
        self.wlan_enable(lan)
        #使无线网卡释放IP地址
        self.dhcp_release_wlan(wlan)
        # #断开无线
        # self.disconnect_ap()

    #AP 下载流量统计的准确性-10M
    def run_AP_download(self,ssid,password,wlan,lan):
        #无线网卡连接master ap
        self.connect_DHCP_WPA_AP(ssid,password,wlan)
        #禁用有线网卡
        self.wlan_disable(lan)
        i =0
        while i<3:
            tmp = self.get_ping(data_basic['iperf_ip'])
            if tmp == 0:
                #描述：使用iperf3进行下载
                tmp1 = subprocess.call("iperf3 -c %s -n 10M -R"%data_basic['iperf_ip'],shell=True)
                print tmp1
                break
            else:
                self.wlan_enable(lan)
                self.dhcp_release_wlan(wlan)
                self.dhcp_wlan(wlan)
                self.wlan_disable(lan)
                print "run iperf3 fail,try %s again!"%(i+1)
                i = i+1
                continue
        #启用有线网卡
        self.wlan_enable(lan)
        #使无线网卡释放IP地址
        self.dhcp_release_wlan(wlan)
        # #断开无线
        # self.disconnect_ap()

    #AP 上传流量统计的准确性-10M
    def run_AP_upload(self,ssid,password,wlan,lan):
        #无线网卡连接master ap
        self.connect_DHCP_WPA_AP(ssid,password,wlan)
        #禁用有线网卡
        self.wlan_disable(lan)
        i =0
        while i<3:
            tmp = self.get_ping(data_basic['iperf_ip'])
            if tmp == 0:
                #描述：使用iperf3进行上传
                tmp1 = subprocess.call("iperf3 -c %s -n 10M"%data_basic['iperf_ip'],shell=True)
                print tmp1
                break
            else:
                self.wlan_enable(lan)
                self.dhcp_release_wlan(wlan)
                self.dhcp_wlan(wlan)
                self.wlan_disable(lan)
                print "run iperf3 fail,try %s again!"%(i+1)
                i = i+1
                continue
        #启用有线网卡
        self.wlan_enable(lan)
        #使无线网卡释放IP地址
        self.dhcp_release_wlan(wlan)
        # #断开无线
        # self.disconnect_ap()

    #取出ap的流量
    def get_ap_status_load(self, aptype):
        #获取接入点-状态-状态列表
        tmps = self.get_aps_status_list()
        for tmp in tmps:
            if tmp['apType'] == aptype:
                ap_usage = tmp['usage']
                ap_upload = tmp['upload']
                ap_download = tmp['download']
                print ap_usage, ap_upload, ap_download
                return ap_usage, ap_upload, ap_download

    #取出ap的客户端数量
    def get_ap_status_clients(self, aptype):
        #获取接入点-状态-状态列表
        tmps = self.get_aps_status_list()
        for tmp in tmps:
            if tmp['apType'] == aptype:
                result = tmp['clients']
                return result

    #取出ap的信道
    def get_ap_status_channel(self, aptype):
        #获取接入点-状态-状态列表
        tmps = self.get_aps_status_list()
        for tmp in tmps:
            if tmp['apType'] == aptype:
                chn_2g4 = tmp['channel']
                chn_5g = tmp['channel5g']
                return chn_2g4, chn_5g

    #判断搜索出来的ap是否正确
    def check_status_search_ap(self, search_str, ap_mac):
        AP_MAC = ap_mac.upper()
        results = self.status_search_ap(search_str)
        for result in results:
            if AP_MAC == result['mac']:
                return True
        return False


    #判断bandwidth图表是否有流量
    def check_chart_ap_bandwidth(self, time, ap_mac):
        #接入点-状态-ap信息速率页面，获取上传下载的bandwidth
        r = 0
        t = 0
        rx_bd, tx_bd = self.get_aps_status_chart_ap_bandwidth(time, ap_mac)
        for rx in rx_bd:
            r = r + rx
        for rx in rx_bd:
            r = r + rx
        print r, t
        #if (r+t) > 50000:
        if (r+t) > 10:
            return True
        else:
            return False

    #获取指定客户端的流量
    def get_client_load(self, ap_mac, client_mac):
        clients_info = self.get_aps_status_clients_info(ap_mac)
        for client_info in clients_info['result']:
            if client_info['mac'] == client_mac.upper():
                client_usage = client_info['usage']
                client_upload = client_info['upload']
                client_download = client_info['download']
                print client_usage, client_upload, client_download
                return client_usage, client_upload, client_download

    #判断ap信息概览页面-Info-基本信息正确
    def check_ap_info(self, ap_mac, host, user, pwd):
        #获取接入点-状态-ap-信息
        MAC, aptype, PN, bootversion, FWversion = \
            self.get_aps_status_Info(ap_mac)
        #登录AP后台取出管理员密码,取出设备状态信息
        ssh = SSH(host, pwd)
        result_ssh = ssh.ssh_cmd(user,'ubus call controller.core status')
        print MAC, aptype, PN, bootversion, FWversion
        if (MAC.lower() in result_ssh) and (aptype in result_ssh) \
                and (PN in result_ssh) and (bootversion in result_ssh) \
                and (FWversion in result_ssh):
            return True
        else:
            return False

    #登录ap后台，取出无线发射功率值
    def get_ap_ssh_power(self, ath, host, user, pwd):
        time.sleep(10)
        ssh = SSH(host, pwd)
        result = ssh.ssh_cmd(user, "iwconfig %s | grep Tx-Power"%ath)
        a = result.split("Tx-Power=")
        for b in a:
            if " dBm" in b:
                c = b.split(" dBm")
        power = c[0]
        print power
        return power






    ######################################################################
    #######以下是配置页面的方法##############################################

    #将ap复位，并将ap的hosts替换，指向本地cloud，然后将该ap添加到cloud中
    def add_ap_2_local_cloud(self, ip, mac, name):
        #ap恢复出厂设置,并设置ap的hosts为本地cloud,并返回ap的ssid的随机密码
        pwd = self.set_ap_2_local_cloud(ip)
        #cloud增加ap
        self.add_ap(mac, pwd, name)
        time.sleep(60)

    #判断ap是否已经和cloud配对上
    def check_ap_pair_cloud(self,ip, user, pwd):
        ssh = SSH(ip, pwd)
        result = ssh.ssh_cmd(user, "netstat | grep %s"%ip)
        if "gateway.gwn.cloud:https ESTABLISHED" in result:
            return True
        else:
            return False

    #判断按照设备类型进行过滤能够显示过滤结果
    def check_configure_filter_ap(self, aptype):
        #按照设备类型进行过滤
        results = self.configure_filter_ap(aptype)
        for result in results:
            if result['apType'] == aptype:
                return True
        return False

    #判断搜索结果是否正确
    def check_configure_search_ap(self, search_str, ap_mac):
        AP_MAC = ap_mac.upper()
        #按照设备进系搜索
        results = self.configure_search_ap(search_str)
        for result in results:
            if result['mac'] == AP_MAC:
                return True
        return False

    #判断设备类型过滤后再搜索结果是否正确
    def check_configure_filter_search_ap(self, aptyep, search_str, ap_mac):
        AP_MAC = ap_mac.upper()
        #设备类型过滤后再搜索
        results = self.configure_filter_search_ap(aptyep, search_str)
        for result in results:
            if result['mac'] == AP_MAC:
                return True
        return False

    #判断设备类型和对应的mac地址显示正确
    def check_configure_type_mac(self):
        result = []
        #获取配置页面的ap信息
        tmps = self.get_configure_ap_info()
        for tmp in tmps:
            if tmp['apType'] == 'GWN7600':
                if tmp['mac'] == data_ap['7600_mac'].upper():
                    result.append(True)
                else:
                    result.append(False)

            if tmp['apType'] == 'GWN7610':
                if tmp['mac'] == data_ap['7610_mac'].upper():
                    result.append(True)
                else:
                    result.append(False)

            if tmp['apType'] == 'GWN7600LR':
                if tmp['mac'] == data_ap['7600lr_mac'].upper():
                    result.append(True)
                else:
                    result.append(False)
        print result
        return result

    #判断ap名称是否正确
    def check_configure_device_name(self, aptype, device_name):
        #获取配置页面的ap信息
        tmps = self.get_configure_ap_info()
        for tmp in tmps:
            if tmp['apType'] == aptype:
                if tmp['name'] == device_name:
                    return True
        return False

    #判断ap ip类型是否正确
    def check_configure_ip_model(self, aptype, ipModel):
        #获取配置页面的ap信息
        tmps = self.get_configure_ap_info()
        for tmp in tmps:
            if tmp['apType'] == aptype:
                if tmp['ipModel'] == ipModel:
                    return True
        return False

    #判断ap显示版本是否正确
    def check_configure_fw(self, aptype, host, user, pwd):
        #获取配置页面的ap信息
        tmp = APSControl(self.s)
        #登录ap后台，获取ap的版本号
        version = tmp.get_router_version(host, user, pwd)
        tmps = tmp.get_configure_ap_info()
        for tmp in tmps:
            if tmp['apType'] == aptype:
                if tmp['versionFirmware'] in version:
                    return True
        return False

    #判断ap显示当前信道是否正确
    def check_configure_channel(self, aptype, chn_2g4, chn_5g):
        #获取配置页面的ap信息
        tmps = self.get_configure_ap_info()
        for tmp in tmps:
            if tmp['apType'] == aptype:
                if (tmp['channel'] == chn_2g4) and (tmp['channel5g'] == chn_5g):
                    return True
        return False

    #判断ap显示当前无线电传输功率是否正确
    def check_configure_power(self, aptype, host, user, pwd):
        #登录ap后台，取出无线发射功率值
        power_2g4 = self.get_ap_ssh_power("ath0", host, user, pwd)
        power_5g = self.get_ap_ssh_power("ath1", host, user, pwd)
        #获取配置页面的ap信息
        tmps = self.get_configure_ap_info()
        for tmp in tmps:
            if tmp['apType'] == aptype:
                if (tmp['power'] == int(power_2g4)) and (tmp['power5g'] == int(power_5g)):
                    return True
                print int(power_2g4), int(power_5g), tmp['power'], tmp['power5g']
        return False

    #确定ap已经重启成功
    def check_ap_reboot(self, ips):
        result = []
        time.sleep(90)
        for ip in ips:
            tmp = self.get_ping(ip)
            if tmp != 0:
                result.append(True)
            else:
                result.append(False)
        return result

     #AP 下载流量统计的准确性-30M
    def run_AP_download_back(self,ssid,password,wlan,lan):
        #无线网卡连接master ap
        self.connect_DHCP_WPA_AP(ssid,password,wlan)
        #禁用有线网卡
        self.wlan_disable(lan)
        i =0
        while i<3:
            tmp = self.get_ping(data_basic['iperf_ip'])
            if tmp == 0:
                #描述：使用iperf3进行下载
                tmp1 = subprocess.call("iperf3 -c %s -n 30M -R"%data_basic['iperf_ip'],shell=True)
                print tmp1
                break
            else:
                self.wlan_enable(lan)
                self.dhcp_release_wlan(wlan)
                self.dhcp_wlan(wlan)
                self.wlan_disable(lan)
                print "run iperf3 fail,try %s again!"%(i+1)
                i = i+1
                continue
        #启用有线网卡
        self.wlan_enable(lan)
        #使无线网卡释放IP地址
        self.dhcp_release_wlan(wlan)
        # #断开无线
        # self.disconnect_ap()