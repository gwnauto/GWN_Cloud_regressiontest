#coding=utf-8
#作者：曾祥卫
#时间：2018.06.12
#描述：cloud system-upgrade的控制层


import time
from data import data
from publicControl.public_control import PublicControl
from connect.ssh import SSH



class UpgradeControl(PublicControl):

    def __init__(self, s):
        #继承PublicControl类的属性和方法
        PublicControl.__init__(self, s)

    ######################################################################
    #获取对应型号和版本的fileid
    def get_version_fileid(self, apType, version):
        APType = apType.upper()
        api = self.loadApi()['sysApUpgradeShow']
        request = PublicControl(self.s)
        recvdata = request.apiRequest_get(api+str(APType))
        version_lists = recvdata['data']['apFirmwares']
        for i in range(len(version_lists)):
            if version == version_lists[i]['firmwareNum']:
                fileid = version_lists[i]['fileId']
                print("fileid is {}".format(fileid))
                return fileid

    #获取ap当前的版本
    def get_ap_current_version(self, ap_mac):
        AP_mac = ap_mac.upper()
        api = self.loadApi()['sysUpgradeApList']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'filter': {'apType': "all"},
                                            'pageNum':1,
                                            'pageSize':10})
        ap_lists = recvdata['data']['result']
        for i in range(len(ap_lists)):
            if AP_mac == ap_lists[i]['mac']:
                version = ap_lists[i]['versionFirmware']
                print ("version is {}".format(version))
                return version


    #选择现在时间升级ap
    def set_ap_upgrade_now(self, apType, version, ap_mac, \
            cloud_ssh_ip, cloud_ssh_user, cloud_ssh_pwd):
        APType = apType.upper()
        AP_mac = ap_mac.upper()
        fileid = self.get_version_fileid(apType, version)
        #获取cloud的当前时间，并按标准格式输出
        ssh = SSH(cloud_ssh_ip, cloud_ssh_pwd)
        result = ssh.ssh_cmd_noKey(cloud_ssh_user, '\'date -d today +"%Y/%m/%d %H:%M"\'')
        now_time = result.strip("\r\n")
        api = self.loadApi()['sysApUpgrade']
        request = PublicControl(self.s)
        recvdata = request.apiRequest(api, {'apType':APType,
                                            'deviceNum':1,
                                            'fileId':fileid,
                                            'mac':AP_mac,
                                            'name':u"升级",
                                            'schedule':"0",
                                            'scheduleEndTime':now_time,
                                            'scheduleTime':now_time,
                                            'targetVersion':version,
                                            'timezone':"Etc/GMT"})
        return recvdata





