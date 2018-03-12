# -*- coding: utf-8 -*-
__time__ = '2018/2/27 15:23'
__author__ = 'winkyi@163.com'
import sys
from optparse import OptionParser
from warOperate import *
from utils import redisManager
from utils import log
from utils.utils import GetConf
from core import showOperate
from core import fileOperate

logger = log.Log()


class Saber(object):

    def __init__(self):
        self.redis_cli = redisManager.redis_cli()
        self.project_cf = GetConf("project.conf")
        self.vesionLib_cf = GetConf("saber.conf")
        self.operParam = {}
        self.getConfDic()


    def getConfDic(self):
        #先获取redis内的配置文件，如果redis无法获取配置文件，改为本地获取
        projectParam = self.redis_cli.smembers('project')
        if projectParam:
            self.projectParam = list(projectParam)
        else:
            self.projectParam = self.project_cf.getSecs()

        versionLibParam = self.redis_cli.hgetall('versionLib')
        if versionLibParam:
            self.versionLibParam = self.redis_cli.hgetall('versionLib')
        else:
            self.versionLibParam = self.vesionLib_cf.getOptions('versionLib')


    #获取工程相关的参数
    def getProjectItem(self,projectName):
        if self.redis_cli.hgetall(projectName):
            return self.redis_cli.hgetall(projectName)
        else:
            return  self.project_cf.getOptions(projectName)




    def main(self):
        parser = OptionParser(usage="usage: %prog [options] arg1 arg2")
        parser.add_option("-s","--show",type="choice",choices = ['nodes', 'servers'],dest="show_status",help=u"显示server、node等信息")
        parser.add_option("-b",'--backup',type="choice",choices =self.projectParam,dest="backup_project",help=u'备份工程')
        parser.add_option("-u",'--update',type="choice",choices =self.projectParam,dest="update_project",help=u'更新工程')
        parser.add_option("-r",'--restore',type="choice",choices =self.projectParam,dest="restore_project",help=u'回退工程')
        parser.add_option("-f",'--filedistribute',type="choice",choices =['startscript','configurefile'],dest="filedistribute",help=u'文件分发（启停脚本），需提前配置好[--sourcefile]和[--remotefile]参数')
        parser.add_option('--sourcefile',dest="sourcefile",help=u'本地文件路径')
        parser.add_option('--remotefile',dest="remotefile",help=u'远端文件路径')
        (options,agrs) = parser.parse_args()

        #如果是show命令
        if options.show_status:
            so = showOperate.ShowOperate(options.show_status)
            so.getItem()


        #判断备份和更新的工程是否一样，强制要求要一样
        if options.backup_project and  options.update_project:
            if options.backup_project != options.update_project:
                logger.error("backup project is no same update! process exit")
                sys.exit()

        #回退操作必须单独执行
        if options.restore_project:
            if options.backup_project or  options.update_project:
                logger.error("exist restore operate,not allow backup or update operate! process exit")
                sys.exit()

        #如果命令是带-c,-b,-u
        #{'backup':'redis','update':'redis','versionPath':'xxxxx','projectPath':'xxxxxx','backupPath':'xxxxx'}
        if options.backup_project:
            self.operParam['backup'] = options.backup_project
            self.operParam['operate'] = 'backup'
            project_name = options.backup_project

        if options.update_project:
            self.operParam['update'] = options.update_project
            self.operParam['operate'] = 'update'
            project_name = options.update_project


        if options.restore_project:
            self.operParam['restore'] = options.restore_project
            self.operParam['operate'] = 'restore'
            project_name = options.restore_project


        if self.operParam:
            projectItemDic = self.getProjectItem(project_name)
            nodeParam = dict(self.versionLibParam, **self.operParam)
            paramInof = dict(nodeParam, **projectItemDic)
            sendCMDToSlave(paramInof)


        #如果是updateconffile命令
        if options.filedistribute:
            #必须配置本地和远程的文件
            if options.sourcefile and options.remotefile:
                self.operParam['remoteFile'] = options.remotefile
                self.operParam['soureFile'] = options.sourcefile
                if not "/" in options.remotefile and not "/" in options.sourcefile:
                    logger.error("file path format error master has [/]")
                    sys.exit()
                fileParam = dict(self.versionLibParam,**self.operParam)
                fileDistribute = fileOperate.FileOperate(fileParam)
                fileDistribute.distribute()
            else:
                logger.error("please set [--sourcefile]和[--remotefile] param")


