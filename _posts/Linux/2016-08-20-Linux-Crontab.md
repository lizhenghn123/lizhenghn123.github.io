---
layout: post

title: Linux下使用Crontab管理定时任务

category: Linux

tags: Linux 

keywords: Linux 定时任务 Crontab 

description: 本文介绍了Linux下使用Crontab管理定时任务。

---

## 1. cron 简介

crontab 是 UNIX, SOLARIS，LINUX 下的一个十分有用的工具。通过 cron 脚本能使计划任务定期地在系统后台自动运行。

crontab工具默认已经安装，下面以在centos6.4系统下为例进行介绍。

## 2. 常用命令  
crontab分为server端和client端。

server端可以通过以下命令进行管理：  
		
	$ service crond status			# 查看定时任务是否被启动
	$ service crond start			# 启动
	$ service crond stop			# 停止
	$ service crond restart			# 重启

client端一般有以下命令：  

	crontab -e                 # 编辑该用户的 crontab，当指定 crontab 不存在时新建。
	crontab -l                 # 列出该用户的 crontab。
	crontab -r      	       # 删除该用户的 crontab。
	crontab -u<用户名称>        # 指定要设定 crontab 的用户名称。

## 3. crontab语法
	
	格式：分 时 日 月 星期几 命令
	
	# 每天12点10分执行[/root/test.sh]命令
	实例：10 12 * * * /root/test.sh
	
	# "*" 号表示全部，例如下面表示每一天的每一分钟都执行一次
	实例：* * * * * /root/test.sh

crontab 字段与允许的值如下表所示：  
	
	| 字段        | 描述             | 允许的值             |
	| ----------- | ---------------- | -------------------- |
	| 分钟        | 一小时的第几分   | 0-59                 |
	| 小时        | 一天的第几小时   | 0-23                 |
	| 日期        | 一个月的的第几天 | 1-31                 |
	| 月份        | 一年的第几个月   | 1-12                 |
	| 周几        | 一周的第几天     | 0-6                  |
	| 命令        | 命令             | 可以被执行的任何命令 |

另外，对于命令中出现的比如“-”、“*”、“,”、“/”号，其意义分别如下：  
	
	| 参数     | 说明          | 备注                                          |
	| -------- | ------------- | --------------------------------------------- |
	| -        | 指定范围      | 例如：在分上写：1-3，每1到3分每分钟执行一次   |
	| *        | 所有          | 例如：分上设定，那就是每分钟执行一次          |
	| ,        | 或            | 例如：在日上设定：1,3，那就是每月1号，3号执行 |
	| /        | 每XXX间隔     | 例如＊/5，那就是每5分钟执行一次               |

此外，还有一些关键字可以替代时间表示：   
	
	| 关键字  | 等同于     | 
	| ------- | ---------  |
	| @yearly |	0 0 1 1 *  |
	| @daily  | 0 0 * * *  |
	| @hourly | 0 * * * *  |
	| @reboot |	重启时运行 |

## 4. 查看cron的运行情况
可以直接通过`tail -f /var/log/cron` 或者`tail -f /var/spool/mail/root`(root用户的cron)查看当前的cron执行情况。

## 5. 实例

- 查看所有用户的定时任务  

		for user in $(cut -f1 -d: /etc/passwd); do echo $user; crontab -u $user -l; done  

- 特定时间执行任务  
cron 的基本用法是在特定的时间执行一项任务，要注意的是时间字段采用的是 24 小时制，如果是下午 8 点，则改写为 20 点。

	- 每分钟执行一次  
			
			* * * * * /bin/date >>/tmp/date.txt

	- 6月10号上午8：30执行某一脚本

			30 08 10 06 * /root/test.sh
	- 每天10:01分和12:01分执行  

			1 10,12 * * * /root/test.sh
	- 每2小时0分执行一次 

			0 */2 * * * /root/test.sh
	- 每3月，5月的1号，10号的12:00执行一次

			0 12 1,10 3,5 * /root/test.sh
	- 每月执行定时任务
	
			@monthly /root/test.sh
	- 每天于 11:00, 16:00 执行
			
			00 11,16 * * * /root/test.sh
	- 每天零点执行任务

			@daily /root/test.sh
	- 每次重启时执行定时任务

			@reboot /root/test.sh


