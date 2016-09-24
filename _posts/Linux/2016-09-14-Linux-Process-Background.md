---
layout: post

title: linux进程后台运行的几种方式

category: Linux

tags: Linux 

keywords: Linux 后台进程 

description: linux进程后台运行的几种方式。

---


如果需要执行一个耗时比较久的任务，尤其是要ssh到远程服务器上执行，如果直接在shell里启动的话，此时该shell肯定不能关闭，本机和远程服务器之间的网络也要一直连通，否则该程序就会退出。

此时的做法通常会选择在后台运行程序，这里介绍几种常见的后台运行方式。

## 以守护进程方式启动

	# ps -e | grep httpd 
	# service httpd start 
	正在启动 httpd：                                           [确定]
	# ps -e | grep httpd 
	30413 ?        00:00:00 httpd
	30421 ?        00:00:00 httpd
	30422 ?        00:00:00 httpd
	30423 ?        00:00:00 httpd
	30424 ?        00:00:00 httpd
	30425 ?        00:00:00 httpd
	30426 ?        00:00:00 httpd
	30427 ?        00:00:00 httpd
	30428 ?        00:00:00 httpd
以这种方式启动的通过是一些做的比较成熟的服务，比如Apache Httpd、Mysqld等等。

## 程序本身带有后台运行模式
比如redis server服务，默认直接启动时是以前台模式运行的：   
	
	# redis-server                
	30914:C 14 Sep 10:07:39.470 # Warning: no config file specified, using the default config. In order to specify a config file use redis-server /path/to/redis.conf
	                _._                                                  
	           _.-``__ ''-._                                             
	      _.-``    `.  `_.  ''-._           Redis 3.2.3 (00000000/0) 64 bit
	  .-`` .-```.  ```\/    _.,_ ''-._                                   
	 (    '      ,       .-`  | `,    )     Running in standalone mode
	 |`-._`-...-` __...-.``-._|'` _.-'|     Port: 6379
	 |    `-._   `._    /     _.-'    |     PID: 30914
	  `-._    `-._  `-./  _.-'    _.-'                                   
	 |`-._`-._    `-.__.-'    _.-'_.-'|                                  
	 |    `-._`-._        _.-'_.-'    |           http://redis.io        
	  `-._    `-._`-.__.-'_.-'    _.-'                                   
	 |`-._`-._    `-.__.-'    _.-'_.-'|                                  
	 |    `-._`-._        _.-'_.-'    |                                  
	  `-._    `-._`-.__.-'_.-'    _.-'                                   
	      `-._    `-.__.-'    _.-'                                       
	          `-._        _.-'                                           
	              `-.__.-'                                               
	
	30914:M 14 Sep 10:07:39.471 # WARNING: The TCP backlog setting of 511 cannot be enforced because /proc/sys/net/core/somaxconn is set to the lower value of 128.
	30914:M 14 Sep 10:07:39.471 # Server started, Redis version 3.2.3
而如果在redis-server启动时带上一个配置文件，且配置文件中设置`daemonize yes`，那么再启动时就会变成后台服务的方式：  

	# redis-server /etc/redis.conf
	# ps -ef | grep redis
	root     31147     1  0 10:09 ?        00:00:00 redis-server 0.0.0.0:6379   

有的程序是通过配置文件决定，有的是通过运行参数决定是否以后台模式启动，比如：  
	
	# ./unimrcpserver -d
	#$#[Current Version Build at:Sep 12 2016 13:07:22]#$#
	2016-09-14 10:15:10:252825 [NOTICE] Run as Daemon
	# ps -ef | grep mrcp
	root      8658     1  0 10:15 ?        00:00:00 ./unimrcpserver -d


以上两种方式都是本身可以直接后台运行的，接下来介绍的nohup和screen方式都是程序本身没有后台运行模式，比如一些第三方程序、脚本或者我们自己随手写的小工具之类的。

## Ctrl+z/bg
对于正在运行的、以前台方式启动的程序，我们可以通过以下方式将其转到后台运行：

	# ctrl + z    # 在该程序所在shell上指向ctrl+z，相当于把该程序暂停
    # jobs        # 查看所有的后台运行的程序
	# bg %1       # 将标号1的程序转为后台运行(也可能是标号2、3、4...)
	# %1          # 放回前台运行
注意： 在将进程方到后台执行后，其父进程还是当前终端shell的进程，而一旦父进程退出(shell关闭)，则会发送hangup信号给所有子进程，子进程收到hangup以后也会退出。如果我们要在退出shell的时候继续运行进程，则需要使用nohup忽略sighup信号，或者setsid将将父进程设为init进程(像tomcat就是忽略sighup)。

## 通过nohup方式启动
	nohup ./a.out &
以上命令就运行了一些后台程序(a.out)， 注意此时可能会在当前目录产生一个nohup.out文件，且该文件有可能很大，直接删掉该文件即可。  
或者将所有输出dump到/dev/null下：  

	nohup ./elasticsearch > /dev/null 2>log & 
	rm -rf nohup.out

## 通过screen命令进行启动

	screen -ls                    # 列出所有screen窗口
	screen -S firsts              # 创建名字为firsts的screen窗口并执行某些命令
	Ctrl + a， d   	           # 退出当前screen，但保持screen在后台运行
	Ctrl + a， c                  # 在同一screen下创建一个新的窗口
	Ctrl + a， [num]              # 按相应数字就切到相应的数字对应的窗口
	Ctrl + a， n                  # 切换到下一个窗口
	Ctrl+a，"                     # 列出所有的screen窗口，然后通过上下键选择，这样对于screen窗口数较多时非常实用
	screen -r firsts      	    # 打开刚刚创建的screen(名字叫firsts)
	screen -dmS seconds ./a.out   # 创建一个后台运行的screen，名字叫seconds， 运行的命令是a.out（启动一个Activate的Screen但不Attach，同时执行命令）

对于一些程序本身不能直接后台运行的程序，可以通过screen进行运行，这样我们就可以和远程服务器断开链接，等过一段时间后再ssh到远程，并通过screen查看程序的运行状态，这种做法比nohup有一个好处就是可以随时看到屏幕输出。
