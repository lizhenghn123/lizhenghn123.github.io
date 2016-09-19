---
layout: post

title: mysql 主从复制和主主复制

category: 开发

tags: 架构 开发 主从复制

keywords: 架构 开发 主从复制 主主复制

description: 本文介绍了mysql数据库的主从复制和主主复制的实战操作步骤。

---

## 1. 主从复制
假设master为192.168.14.202，slave为192.168.14.201。目前所有的写入/读取都是针对master操作的，slave用来做master的数据备份。目标是当master机器挂掉后，slave能够提供服务。

###1.1 从master上导出数据库  

	mysqldump -u 用户名 -p 数据库名 > 导出的文件名
	mysqldump -u root -p db1 > db1.sql 

注意：mysqldump是把master上的所有数据也导出了，如果不关注这些旧数据记录，可以只导出表的创建sql即可。

###1.2 在slave上导入数据库

登录mysql后，创建数据库，然后执行source db1.sql；

###1.3 修改master上的my.cnf

vim /etc/my.cnf，增加以下内容：  
	
	#数据库ID号， 为1时表示为Master,其中master_id必须为1到2^32–1之间的一个正整数值; 
	server-id=1
	#启用二进制日志； 
	log-bin=mysql-bin
	#需要同步的二进制数据库名； 
	binlog-do-db=wuxi
	#不同步的二进制数据库名;这个同步后听说很麻烦，我没有同步； 
	binlog-ignore-db=mysql
	#把更新的记录写到二进制文件中； 
	log-slave-updates
	#跳过错误，继续执行复制； 
	slave-skip-errors

###1.4 修改slave上的my.cnf

vim /etc/my.cnf，增加以下内容：
	
	server-id=2  # server-id要唯一
	log-bin=mysql-bin 
	master-host=192.168.14.202 
	master-user=test
	master-password = 123456
	master-port=3306 
	#如果发现主服务器断线，重新连接的时间差； 
	master-connect-retry=60
	#需要备份的数据库 
	replicate-do-db=wuxi
	#不需要备份的数据库； 
	replicate-ignore-db=mysql 
	log-slave-updates 
	slave-skip-errors

###1.5 设置master和slave的mysql

在master上，登录mysql，建立同步帐号

	mysql> grant replication slave on *.* to test@'192.168.14.%' identified by '123456'  

然后重启master上的mysql。

在slave上，登录mysql  

	mysql> slave start; 
	mysql> show slave status\G; 
如果一切顺利，这里显示就是正常的。

此时可以查看master和slave的状态：
	
	mysql> show master status; 
	mysql> show slave status; 

也可以在master上查看slave的I/O线程创建的连接：  

	mysql> show processlist \G
###1.6 FAQ
#### Last_Errno: 1062， Error Duplicate entry
是由于某个时候主键不同步导致从库插入记录时发现了主键重复导致，这里有三种可行办法解决：

1. 通过mysql设置  

	mysql> slave stop;  
    mysql> set GLOBAL SQL_SLAVE_SKIP_COUNTER=1;  
    mysql> slave start;  

2. 设置从库的my.cnf，增加以下设置，并重启从库mysql服务    

	 slave-skip-errors = 1062 

3. 设置同步位置  

	进入主库mysql，并锁表：

	mysql> FLUSH TABLES WITH READ LOCK;  
	mysql> show master status;  
	+------------------+----------+--------------+------------------+  
	| File             | Position | Binlog_Do_DB | Binlog_Ignore_DB |  
	+------------------+----------+--------------+------------------+  
	| mysql-bin.000006 |     6762 | wuxi         | mysql            |  
	+------------------+----------+--------------+------------------+  

	进入从库

　　mysql> change master to master\_host='192.168.14.202', master\_user='test',master\_password='123456',master\_port=3306,　master\_log\_file='mysql-bin.000006',master\_log_pos=6762;  

　　mysql>  start slave;

　　回到主库

　　mysql> unlock tables; #解锁

　　回到从库 查看

　　mysql> show slave status \G;  
	此时即正常了。  

## 2. 主主复制

主主复制是主从复制的双向做法，这篇文章介绍的比较详细[mysql 主主互备](http://www.cnblogs.com/kristain/articles/4142970.html)。

下面贴上设置过主主复制后，两台mysql的配置文件：

master上：
	
	#数据库ID号， 为1时表示为Master,其中master_id必须为1到232–1之间的一个正整数值; 
	server-id=1
	#启用二进制日志； 
	log-bin=mysql-bin
	#需要同步的二进制数据库名； 
	binlog-do-db=wuxi
	#不同步的二进制数据库名;这个同步后听说很麻烦，我没有同步； 
	binlog-ignore-db=mysql
	#设定生成的log文件名； 
	#log-bin=/var/log/mysql/updatelog
	#把更新的记录写到二进制文件中； 
	log-slave-updates
	#跳过错误，继续执行复制； 
	slave-skip-errors
	
	auto-increment-increment = 3
	auto-increment-offset = 1
	
	### slave of 192.168.14.201
	#需要备份的数据库 
	replicate-do-db=wuxi
	#不需要备份的数据库； 
	replicate-ignore-db=mysql 
	log-slave-updates
	slave-skip-errors

slave上：  
	
	server-id=2
	log-bin=mysql-bin 
	master-host=192.168.14.202 
	master-user=test
	master-password = 123456
	master-port=3306 
	#如果发现主服务器断线，重新连接的时间差； 
	master-connect-retry=60
	#需要备份的数据库 
	replicate-do-db=wuxi
	#不需要备份的数据库； 
	replicate-ignore-db=mysql 
	log-slave-update 
	slave-skip-errors 
		
	read-only=0
	#需要同步的二进制数据库名； 
	binlog-do-db=wuxi
	##不同步的二进制数据库名;这个同步后听说很麻烦，我没有同步； 
	binlog-ignore-db=mysql
	auto-increment-increment = 3
	auto-increment-offset = 2
 
## 3. Reference
- [MYSQL主从同步](http://blog.csdn.net/gaowenhui2008/article/details/46698321)  
- [主从server-id不生效，The server is not configured as slave ](http://blog.itpub.net/27099995/viewspace-1294103/)
- [mysql故障~Got fatal error 1236 解决方法](http://blog.chinaunix.net/uid-26446098-id-3310546.html)  
- [MySQL主从同步、读写分离配置步骤](http://www.jb51.net/article/29818.htm)  
- [MYSQL管理之主从同步管理](http://blog.chinaunix.net/uid-20639775-id-3254611.html)   
- [mysql高可用探究(二)Lvs+Keepalived+Mysql单点写入主主同步高可用方案](http://szgb2014.blog.51cto.com/340201/1181286)
- [浅谈mysql主从复制的高可用解决方案](http://aokunsang.iteye.com/blog/2054559)   
- [MySQL高可用方案介绍](http://blog.itpub.net/26355921/viewspace-1248096/)