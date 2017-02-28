---
layout: post

title: Redis配置文件redis.conf介绍

category: 开发

tags: 开发 Redis

keywords: 开发 Redis

description: Redis配置文件redis.conf介绍。

---

Redis的配置文件叫做redis.conf， 在Linux系统下默认位于/etc/redis.conf。本节就简单介绍下该配置文件中的参数意义。

## 查看配置
我们可以通过 CONFIG 命令查看或设置配置项。Redis CONFIG 命令格式如下：

	redis 127.0.0.1:6379> CONFIG GET CONFIG_SETTING_NAME

示例：
	
	redis 127.0.0.1:6379> CONFIG GET loglevel
	1) "loglevel"
	2) "notice"
	redis 127.0.0.1:6379> CONFIG GET *		# 使用 * 号获取所有配置项：
	1) "dbfilename"
  	2) "dump.rdb"
  	3) "requirepass"
  	4) ""
  	5) "masterauth"
  	6) ""
	....... 这里就不列出所有了

## 修改配置
可以通过直接修改 redis.conf 文件或使用 CONFIG set 命令来修改配置。

CONFIG SET 命令基本语法：  

	redis 127.0.0.1:6379> CONFIG SET CONFIG_SETTING_NAME NEW_CONFIG_VALUE

示例：

	redis 127.0.0.1:6379> CONFIG SET loglevel "debug"
	OK
	redis 127.0.0.1:6379> CONFIG GET loglevel
	1) "loglevel"
	2) "debug"

## 配置参数介绍
redis.conf 配置项说明如下：

1. Redis默认不是以守护进程的方式运行，可以通过该配置项修改，使用yes启用守护进程  
	**daemonize no**
2. 当Redis以守护进程方式运行时，Redis默认会把pid写入/var/run/redis.pid文件，可以通过pidfile指定  
    **pidfile /var/run/redis.pid**
3. 指定Redis监听端口，默认端口为6379，作者在自己的一篇博文中解释了为什么选用6379作为默认端口，因为6379在手机按键上MERZ对应的号码，而MERZ取自意大利歌女Alessia Merz的名字  
    **port 6379**
4. 绑定的主机地址  
    **bind 127.0.0.1**
5. 当 客户端闲置多长时间后关闭连接，如果指定为0，表示关闭该功能    
    **timeout 300**
6. 指定日志记录级别，Redis总共支持四个级别：debug、verbose、notice、warning，默认为verbose  
    **loglevel verbose**
7. 日志记录方式，默认为标准输出，如果配置Redis为守护进程方式运行，而这里又配置为日志记录方式为标准输出，则日志将会发送给/dev/null  
    **logfile stdout**
8. 设置数据库的数量，默认数据库为0，可以使用SELECT <dbid>命令在连接上指定数据库id  
    **databases 16**
9. 指定在多长时间内，有多少次更新操作，就将数据同步到数据文件，可以多个条件配合  
    **save <seconds> <changes>**
    Redis默认配置文件中提供了三个条件：  
    **save 900 1**  
    **save 300 10**  
    **save 60 10000**  
    分别表示900秒（15分钟）内有1个更改，300秒（5分钟）内有10个更改以及60秒内有10000个更改。 
10. 指定存储至本地数据库时是否压缩数据，默认为yes，Redis采用LZF压缩，如果为了节省CPU时间，可以关闭该选项，但会导致数据库文件变的巨大  
    **rdbcompression yes**
11. 指定本地数据库文件名，默认值为dump.rdb  
    **dbfilename dump.rdb**
12. 指定本地数据库存放目录  
    **dir ./**
13. 设置当本机为slav服务时，设置master服务的IP地址及端口，在Redis启动时，它会自动从master进行数据同步  
    **slaveof <masterip> <masterport>**
14. 当master服务设置了密码保护时，slav服务连接master的密码  
    **masterauth <master-password>**
15. 设置Redis连接密码，如果配置了连接密码，客户端在连接Redis时需要通过AUTH <password>命令提供密码，默认关闭  
    **requirepass foobared**
16. 设置同一时间最大客户端连接数，默认无限制，Redis可以同时打开的客户端连接数为Redis进程可以打开的最大文件描述符数，如果设置 maxclients 0，表示不作限制。当客户端连接数到达限制时，Redis会关闭新的连接并向客户端返回max number of clients reached错误信息  
    **maxclients 128**
17. 指定Redis最大内存限制，Redis在启动时会把数据加载到内存中，达到最大内存后，Redis会先尝试清除已到期或即将到期的Key，当此方法处理 后，仍然到达最大内存设置，将无法再进行写入操作，但仍然可以进行读取操作。Redis新的vm机制，会把Key存放内存，Value会存放在swap区  
    **maxmemory <bytes>**
18. 指定是否在每次更新操作后进行日志记录，Redis在默认情况下是异步的把数据写入磁盘，如果不开启，可能会在断电时导致一段时间内的数据丢失。因为 redis本身同步数据文件是按上面save条件来同步的，所以有的数据会在一段时间内只存在于内存中。默认为no  
    **appendonly no**
19. 指定更新日志文件名，默认为appendonly.aof  
    **appendfilename appendonly.aof**
20. 指定更新日志条件，共有3个可选值：  
    **no：表示等操作系统进行数据缓存同步到磁盘（快）**  
    **always：表示每次更新操作后手动调用fsync()将数据写到磁盘（慢，安全）**  
    **everysec：表示每秒同步一次（折衷，默认值）**  
    **appendfsync everysec** 
21. 指定是否启用虚拟内存机制，默认值为no，简单的介绍一下，VM机制将数据分页存放，由Redis将访问量较少的页即冷数据swap到磁盘上，访问多的页面由磁盘自动换出到内存中（在后面的文章我会仔细分析Redis的VM机制）  
    **vm-enabled no**
22. 虚拟内存文件路径，默认值为/tmp/redis.swap，不可多个Redis实例共享  
    **vm-swap-file /tmp/redis.swap**
23. 将所有大于vm-max-memory的数据存入虚拟内存,无论vm-max-memory设置多小,所有索引数据都是内存存储的(Redis的索引数据 就是keys),也就是说,当vm-max-memory设置为0的时候,其实是所有value都存在于磁盘。默认值为0  
    **vm-max-memory 0**
24. Redis swap文件分成了很多的page，一个对象可以保存在多个page上面，但一个page上不能被多个对象共享，vm-page-size是要根据存储的 数据大小来设定的，作者建议如果存储很多小对象，page大小最好设置为32或者64bytes；如果存储很大大对象，则可以使用更大的page，如果不 确定，就使用默认值  
    **vm-page-size 32**
25. 设置swap文件中的page数量，由于页表（一种表示页面空闲或使用的bitmap）是在放在内存中的，，在磁盘上每8个pages将消耗1byte的内存。  
    **vm-pages 134217728**
26. 设置访问swap文件的线程数,最好不要超过机器的核数,如果设置为0,那么所有对swap文件的操作都是串行的，可能会造成比较长时间的延迟。默认值为4  
    **vm-max-threads 4**
27. 设置在向客户端应答时，是否把较小的包合并为一个包发送，默认为开启  
    **glueoutputbuf yes**
28. 指定在超过一定的数量或者最大的元素超过某一临界值时，采用一种特殊的哈希算法  
    **hash-max-zipmap-entries 64**
    **hash-max-zipmap-value 512**
29. 指定是否激活重置哈希，默认为开启（后面在介绍Redis的哈希算法时具体介绍）  
    **activerehashing yes**
30. 指定包含其它的配置文件，可以在同一主机上多个Redis实例之间使用同一份配置文件，而同时各个实例又拥有自己的特定配置文件  
    **include /path/to/local.conf**

## 优化

### vm.overcommit_memory

Redis在启动时可能会出现这样的日志：

> 
> WARNING overcommit_memory is set to 0! Background save may fail under low memory condition. To fix this issue add 'vm.overcommit_memory = 1' to /etc/sysctl.conf and then reboot or run the command 'sysctl vm.overcommit_memory=1' for this to take effect.


Linux操作系统对大部分申请内存的请求都回复yes，以便能运行更多的程序。因为申请内存后，并不会马上使用内存，这种技术叫做overcommit。如果Redis在启动时有上面的日志，说明vm.overcommit_memory=0，**Redis提示把它设置为1**。  
vm.overcommit_memory用来设置内存分配策略，它有三个可选值，如下表所示：  

vm.overcommit_memory | 含义
--------|---------
0 | 表示内核将检查是否有足够的可用内存。如果有足够的可用内存，内存申请通过，否则内存申请失败，并把错误返回给应用进程
1 | 表示内核允许超量使用内存直到用完为止
2 | 表示内核决不过量的(“never overcommit”)使用内存，即系统整个内存地址空间不能超过swap+50%的RAM值，50%是overcommit_ratio默认值，此参数同样支持修改

设置overcommit_memory：  

```shell
$ cat /proc/sys/vm/overcommit_memory                    # 查看
$ echo "vm.overcommit_memory=1" >> /etc/sysctl.conf     # 设置
$ sysctl vm.overcommit_memory=1
vm.overcommit_memory = 1
$ cat /proc/sys/vm/overcommit_memory
1
```

### Transparent Huge Pages
Redis在启动时可能会看到如下日志：  

> 
> WARNING you have Transparent Huge Pages (THP) support enabled in your kernel. This will create latency and memory usage issues with Redis. To fix this issue run the command 'echo never > /sys/kernel/mm/transparent_hugepage/enabled' as root, and add it to your /etc/rc.local in order to retain the setting after a reboot. Redis must be restarted after THP is disabled.

Linux kernel在2.6.38内核增加了Transparent Huge Pages (THP)特性 ，支持大内存页(2MB)分配，默认开启。当开启时可以降低fork子进程的速度，但fork之后，每个内存页从原来4KB变为2MB，会大幅增加重写期间父进程内存消耗。同时每次写命令引起的复制内存页单位放大了512倍，会拖慢写操作的执行时间，导致大量写操作慢查询。例如简单的incr命令也会出现在慢查询中。因此Redis日志中建议将此特性进行禁用，禁用方法如下：  

```shell
echo never >  /sys/kernel/mm/transparent_hugepage/enabled
```

为了使机器重启后THP配置依然生效，可以在/etc/rc.local中追加`echo never > /sys/kernel/mm/transparent_hugepage/enabled`。  

### TCP backlog
Redis默认的tcp-backlog为511，可以通过修改配置tcp-backlog进行调整，如果Linux的tcp-backlog小于Redis设置的tcp-backlog，那么在Redis启动时会看到如下日志：

> 
> WARNING: The TCP backlog setting of 511 cannot be enforced because /proc/sys/net/core/somaxconn is set to the lower value of 128.

可以通过以下步骤进行修改：  

```shell
$ cat /proc/sys/net/core/somaxconn          # 查看  
$ echo 511 > /proc/sys/net/core/somaxconn   # 设置 
```

### open files
在Linux中，可以通过ulimit查看和设置系统的当前用户进程的资源数。其中ulimit -a命令包含的open files参数，是单个用户同时打开的最大文件个数。

Redis允许同时有多个客户端通过网络进行连接，可以通过配置maxclients来限制最大客户端连接数。对Linux操作系统来说这些网络连接都是文件句柄。假设当前open files是4096，那么启动Redis时会看到如下日志：  

> You requested maxclients of 10000 requiring at least 10032 max file descriptors.
> Redis can’t set maximum open files to 10032 because of OS error: Operation not permitted.
> Current maximum open files is 4096. Maxclients has been reduced to 4064 to compensate for low ulimit. If you need higher maxclients increase ‘ulimit –n’.


可以通过以下步骤进行修改： 

```shell
$ ulimit -n          # 查看 
1024 
$ ulimit -n 102400   # 设置 
```

## Reference

- [Redis 配置](http://www.runoob.com/redis/redis-conf.html)

