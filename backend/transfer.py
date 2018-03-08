# -*- coding: utf-8 -*-
__time__ = '2018/3/5 17:01'
__author__ = 'winkyi@163.com'

import paramiko


host = "202.5.20.208"
port = 22
timeout = 30
user = "root"
password = "!@cwq8898859"



class Transfer(object):

    def __init__(self,host,port,user,password,timeout=30):
        self.host = host
        self.user = user
        self.port = port
        self.password = password
        self.timeout = timeout

    #Paramiko远程执行linux命令
    def sftp_exec_command(self,command):
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(self.host, self.port, self.user, self.password)
            std_in, std_out, std_err = ssh_client.exec_command(command)
            for line in std_out:
                print line.strip("\n")
            ssh_client.close()
        except Exception, e:
            print e


    #Paramiko上传文件
    def sftp_upload_file(self,server_path, local_path):
        try:
            t = paramiko.Transport((self.host, self.port))
            t.connect(username=self.user, password=self.password)
            sftp = paramiko.SFTPClient.from_transport(t)
            sftp.put(local_path, server_path)
            t.close()
        except Exception, e:
            print e


    #Paramiko下载文件
    def sftp_down_file(self,server_path, local_path):
        try:
            t = paramiko.Transport((self.host, self.port))
            t.connect(username=self.user, password=self.password)
            sftp = paramiko.SFTPClient.from_transport(t)
            sftp.get(server_path, local_path)
            t.close()
        except Exception, e:
            print e


if __name__ == '__main__':
    host = "202.5.20.208"
    port = 22
    timeout = 30
    user = "root"
    password = "!@cwq8898859"

    t = Transfer(host,port,user,password)

    t.sftp_exec_command("ls -l")
    # t.sftp_upload_file("/root/tools/test.war", "/home/ap/ldap/software/redis-4.0.8.tar.gz")
    # t.sftp_down_file("/root/tools/aabbccdd.txt", "D:/data/aabbccdd.txt")

