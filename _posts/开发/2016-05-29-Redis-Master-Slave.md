---
layout: post

title: Redis 主从复制设置详细步骤

category: 开发

tags: 架构 开发 主从复制 Redis

keywords: 架构 开发 主从复制 Redis

description: 本文介绍了Redis主从复制的详细操作步骤。

---

## 概念
redis主从复制很简单，它通过配置 master-slave 复制来让slave redis server 精准拷贝master servers。 redis复制有几个特性：

- 一个master 可以有多个slaves  
- redis 使用的是 异步复制(asynchronous replicatiom), 从redis 2.8开始，slave会周期性告知master复制数据流时的过程
- slaves 可以连接其它的slaves, 除了连接同一个master，也可以像同一个结构图中与其他slaves建立链接
- redis 从master复制是非阻塞的,这就意味着master在对一个或多个slave端同步时也可以查询
同时在slaves端也是非阻塞的，假设在redis.conf里配置了redis, 当slave在执行同步时，可以接受查询旧的信息，否则就会发送一个错误到客户端。但是在同步完成后老的数据会被删除，新的数据会被载入进来
- replication也可以提高性能, 以达到多个slaves仅做只读查询(如果做一个heavy sort 操作，在数据冗余(date redundancy)后就变的相对简单)
- 使用复制也可以避免master把所有的数据写到disk时的开销, 仅需要要在master里配置redis.conf来避免保存，使用slave通过链接来实时保存。这个配置必须保证master 不会自动重启。

## 搭建步骤
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

## 一些常用的配置参数
- `slaveof <masterip> <masterport>` 设置master ip 与端口
- `masterauth <master-password>` 设置mstater 密码如果master是有密登录
- `slave-serve-stale-data yes` 当复制正在进行时slave与master链接断掉，有两种方式 yes是slave会继续回应客户端的请求，可能有过时的数据，no slave就会对除了INFO SLAVEOF的其它命令回复一个eroor 给客户端SYNC with master in progress
- `slave-read-only yes`  slave只允许读取数据
- `repl-diskless-sync no` 不通过磁盘来同步（试验阶段）
- `repl-diskless-sync-delay 5` 当无磁盘同步开启后需要配置一个延迟时间，以保证接受多个slave的同步请求，默认为5秒
- `repl-ping-slave-period 10 `多少秒ping一次master
- `repl-timeout 60 `复制的超时时间，这个时间一定要大于ping的时间
- `repl-disable-tcp-nodelay no TCP_NODELAY`，yes表示使用非常小的TCP包数和非常小的宽带来发送数据。slave那边可以增加一个延迟时间
- `repl-backlog-size 1mb` backlog的大小，backlog是一个用来积累当slave没有链接后数据的缓存，重新链接后就不需要完整同步啦。- backlog越大，slave断开的时间就越长，再次同步的便会越迟
- `repl-backlog-ttl 3600` 断开链接多少秒后释放backlog，0表示永远不释放
- `slave-priority 100` slave优先级是当master down了之后被redis哨兵拿来从slave中晋先新的master,数字越小优先级越高，0表示永远不晋选为master
- `min-slaves-to-write 3` 最小slave链接数默认为0
- `min-slaves-max-lag 10` 最小的slave，最大延迟数默认为10

## FAQ
1. slave只读  
从redis2.6开始slaves可以支持只读模式，这个行为是用`slave-read-only`参数来控制，也可以使用命令`CONFIG SET` 来开启或关闭
只读模式将会拒绝所有写的命令，所以对slave进行写是不可能的。如果希望slave示例可以进行修改操作，就需要设置slave-read-only参数为no。

2. 设置slave到master的认证  
如果master有是通过密码登陆`requirepass`，那么在slave下也需要使用密码来同步数据
运行一个redis-cli实例然后输入 `config set masterauth <password>` 如果需要设置永久的密码可以在配置文件中增加`masterauth <password>`
