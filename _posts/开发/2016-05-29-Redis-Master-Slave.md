---
layout: post

title: Redis 主从复制设置详细步骤

category: 开发

tags: 架构 开发 主从复制 Redis

keywords: 架构 开发 主从复制 Redis

description: 本文介绍了Redis主从复制的详细操作步骤。

---

redis的主从复制搭建起来比较简单，这里以在一台机器上设置redis主从来进行说明。

假设已正确安装过redis-server，且已经有了一个redis的配置文件，比如/etc/redis.conf。

1.  复制一个redis.conf，比如/etc/redis\_slave.conf，其中master redis启动时使用redis.conf配置文件，slave redis启动时使用redis_slave.conf配置文件；  

    	cp /etc/redis.conf /etc/redis_slave.conf  

2. 修改配置文件，通常master的redis.conf不同修改了（前提是你已验证redis.conf是正确的，假设master redis端口是6379），下面修改/etc/redis_slave.conf，主要修改以下内容：
    	
    	pidfile /var/run/redis_slave.pid  
    	port 6380  
    	logfile /var/log/redis_slave.log  # 按需设置，默认是stdcout  
    	dbfilename /var/data/dump_slave.rdb  
    	slaveof 0.0.0.0 6379  # 设置master redis 是本机ip，端口6379如果master redis是不同机器或不同端口，就修改此处设置
    	slave-read-only yes 				  # 按需设置，是否允许客户端对slave redis进行修改

3. 启动主、从redis  
    
    	redis-server /etc/redis.conf  
    	redis-server /etc/redis_slave.conf  

	如果顺利，这里会有一些输出信息，比如master redis下输出：
    		
    	[11974] 12 May 10:51:26.682 * Slave ask for synchronization  
    	[11974] 12 May 10:51:26.682 * Starting BGSAVE for SYNC  
    	[11974] 12 May 10:51:26.683 * Background saving started by pid 12229  
    	[12229] 12 May 10:51:26.690 * DB saved on disk  
    	[12229] 12 May 10:51:26.691 * RDB: 6 MB of memory used by copy-on-write  
    	[11974] 12 May 10:51:26.765 * Background saving terminated with success  
    	[11974] 12 May 10:51:26.765 * Synchronization with slave succeeded  
    	[11974] 12 May 11:06:27.087 * 1 changes in 900 seconds. Saving...  
    	[11974] 12 May 11:06:27.088 * Background saving started by pid 25710  
    	[25710] 12 May 11:06:27.101 * DB saved on disk  
    	[25710] 12 May 11:06:27.101 * RDB: 6 MB of memory used by copy-on-write  
    	[11974] 12 May 11:06:27.189 * Background saving terminated with success  

	slave redis下有输出：
    	
    	[12226] 12 May 10:51:26.680 * MASTER <-> SLAVE sync started  
    	[12226] 12 May 10:51:26.680 * Non blocking connect for SYNC fired the event.  
    	[12226] 12 May 10:51:26.681 * Master replied to PING, replication can continue...  
    	[12226] 12 May 10:51:26.765 * MASTER <-> SLAVE sync: receiving 18 bytes from master  
    	[12226] 12 May 10:51:26.765 * MASTER <-> SLAVE sync: Loading DB in memory  
    	[12226] 12 May 10:51:26.765 * MASTER <-> SLAVE sync: Finished with success  
    	[12226] 12 May 10:56:27.048 * 10 changes in 300 seconds. Saving...  
    	[12226] 12 May 10:56:27.049 * Background saving started by pid 16784  
    	[16784] 12 May 10:56:27.092 * DB saved on disk  
    	[16784] 12 May 10:56:27.092 * RDB: 6 MB of memory used by copy-on-write  
    	[12226] 12 May 10:56:27.150 * Background saving terminated with success  

4. 查看状态  

	在master redis查看复制设置：  
    
    	redis 127.0.0.1:6379> info replication
    	role:master  
    	connected_slaves:1  
    	slave0:127.0.0.1,6380,online  
  
	在slave redis查看复制设置：  
    
    	redis 127.0.0.1:6380> info replication  
    	role:slave  
    	master_host:0.0.0.0  
    	master_port:6379  
    	master_link_status:up  
    	master_last_io_seconds_ago:1  
    	master_sync_in_progress:0  
    	slave_priority:100  
    	slave_read_only:1  
    	connected_slaves:0  
  
4. 进行验证

	在master上设置key：  
    
    	redis 127.0.0.1:6379> set hello 13  
    	OK  
    	redis 127.0.0.1:6379> expire hello 30  
    	(integer) 1  
    	redis 127.0.0.1:6379> get hello  
    	"13"  
    	redis 127.0.0.1:6379> ttl hello  
    	(integer) 24  

	在slave上查看key：  
    
    	redis 127.0.0.1:6380> get hello  
    	"13"  
    	redis 127.0.0.1:6380> ttl hello  
    	(integer) 17  

	等待key的时间过期之后，分别在master和slave上再次查看该key：  
    
     	redis 127.0.0.1:6379> ttl hello   
    	(integer) -1  
    	redis 127.0.0.1:6379> get hello  
    	(nil)  
    	  
    	redis 127.0.0.1:6380> ttl hello  
    	(integer) -1  
    	redis 127.0.0.1:6380> get hello  
    	(nil)  
    
至此 redis的主从复制就搭建完成了，如果master和slave不在同一台机器上，只需要修改配置文件中的IP即可。