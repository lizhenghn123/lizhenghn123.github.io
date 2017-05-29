---
layout: post

title: 使用keepalived和lvs搭建高可用及负载均衡环境

category: 架构

tags: 架构 高可用 负载均衡 lvs keepalive

keywords: 架构 高可用 负载均衡 lvs keepalive

description: 使用keepalived和lvs搭建高可用及负载均衡环境。

---

## lvs介绍
LVS是Linux Virtual Server的简写，意即Linux虚拟服务器，是一个虚拟的服务器集群系统。本项目在1998年5月由章文嵩博士成立，是中国国内最早出现的自由软件项目之一。目前有三种IP负载均衡技术（VS/NAT、VS/TUN和VS/DR）、十种调度算法（rrr|wrr|lc|wlc|lblc|lblcr|dh|sh|sed|nq）。

LVS在Unix-like系统中是作为一个前端(Director)存在的，又称为调度器，它本身不提供任何的服务，只是将通过互联网进来的请求接受后再转发给后台运行的真正的服务器(RealServer)进行处理，然后响应给客户端。

LVS集群采用IP负载均衡技术和基于内容请求分发技术。调度器具有很好的吞吐率，将请求均衡地转移到不同的服务器上执行，且调度器自动屏蔽掉服务器的故障，从而将一组服务器构成一个高性能的、高可用的虚拟服务器。整个服务器集群的结构对客户是透明的，而且无需修改客户端和服务器端的程序。为此，在设计时需要考虑系统的透明性、可伸缩性、高可用性和易管理性。

LVS有两个重要的组件：一个是IPVS，一个是IPVSADM。ipvs是LVS的核心组件，它本身只是一个框架，类似于iptables，工作于内核空间中。ipvsadm 是用来定义LVS的转发规则的，工作于用户空间中。

LVS有三种转发类型：

- LVS-NAT模型，称为网络地址转换，实现起来比较简单  
	1. 所有的RealServer集群节点和前端调度器Director都要在同一个子网中
	2. 这种模型可以实现端口映射
	3. RealServer的操作系统可以是任意操作系统
	4. 前端的Director既要处理客户端发起的请求，又要处理后台RealServer的响应信息，将RealServer响应的信息再转发给客户端
	5. 前端Director很容易成为整个集群系统性能的瓶颈。
	6. 通常情况下RealServer的IP地址(以下简成RIP)为私有地址，便于RealServer集群节点之间进行通信
	7. 通常情况下前端的Director有两个IP地址，一个为VIP，是虚拟的IP地址，客户端向此IP地址发起请求。一个是DIP，是真正的Director的IP地址，RIP的网关要指向Director的DIP。
- LVS-DR模型，称为直接路由模型，应用比较广泛，此种模型通过MAC地址转发工作
	2. 所有的RealServer集群节点和前端调度器Director都要在同一个物理网络中
	3. 此种模型不支持端口映射
	4. RealServer可以使用大多数的操作系统
	5. 前端的Director只处理客户端的请求，然后将请求转发给RealServer，由后台的RealServer直接响应客户端，不再经过Director
	6. 此种模型的性能要优于LVS-NAT
	7. RIP可以使用公网的IP
	7. RIP的网关不能指向DIP
- LVS-TUN模型，称为隧道模型  
	1. RealServer服务器与前端的Director可以在不同的网络中
	2. 此种模型也不支持端口映射
	3. RealServer只能使用哪些支持IP隧道的操作系统
	4. 前端的Director只处理客户端的请求，然后将请求转发给RealServer，由后台的RealServer直接响应客户端，不再经过Director
	5. RIP一定不能是私有IP

在DR、TUN模式中，数据包是直接返回给用户的，所以，在Director Server上以及集群的每个节点上都需要设置这个地址。此IP在Real Server上一般绑定在回环地址上，例如lo:0，同样，在Director Server上，虚拟IP绑定在真实的网络接口设备上，例如eth0:0。

## 安装

 在线安装

	yum -y install keepalived ipvsadm

### 源码安装

	# wget http://www.keepalived.org/software/keepalived-1.2.15.tar.gz
	# tar -xf keepalived-1.2.15.tar.gz && cd keepalived-1.2.15
	# ./configure && make && make install

	# wget http://www.linuxvirtualserver.org/software/kernel-2.6/ipvsadm-1.26.tar.gz
	# tar -xf ipvsadm-1.26.tar.gz && cd ipvsadm-1.26/
	# make && make install


关闭SELinux(改完需重启服务器)：

	# sed -i 's#^SELINUX=.*#SELINUX=disabled#' /etc/sysconfig/selinux   

创建ipvsadm配置文件，启动并加入开机启动
	
	# /etc/init.d/ipvsadm save
	# /etc/init.d/ipvsadm start
	# chkconfig ipvsadm on


## 实例：搭建lvs+keepalived
本文搭建、测试lvs+keepalived高可用架构。测试环境使用4台真实服务器，如下介绍：
	
	虚拟ip     ： 192.168.14.200，默认指向Master(192.168.14.8)
	真实服务器1 ： Master，192.168.14.8， 该机器上同时运行Apache Httpd服务(端口80)用作sorry_server且通常不提供服务；
	真实服务器2 ： Backup，192.168.14.14， 该机器上同时运行Apache Httpd服务(端口80)用作sorry_server且通常不提供服务；
	真实服务器3 ： web01 ，192.168.14.202， 该机器上运行Apache Httpd服务(端口80)用作后端server且通常提供服务；
	真实服务器4 ： web02 ，192.168.14.203， 该机器上运行Apache Httpd服务(端口80)用作后端server且通常提供服务；
系统部署结构图如下所示：

	                   +-------------+
	                   |    touter   |
	                   +-------------+
	                          |
	                          |
	                      keepalived         
	  192.168.14.8      192.168.14.200     192.168.14.14
	+-------------+    +-------------+    +-------------+
	|   MASTER    |----|  virtualIP  |----|   BACKUP    |
	+-------------+    +-------------+    +-------------+
	                          |
	       +------------------+------------------+
	       |                                    |
	 192.168.14.202                        192.168.14.203
	+-------------+                       +-------------+
	|    web01    |                       |    web02    |
	+-------------+                       +-------------+

每台机器上安装的服务有：

- Master、Backup ： keepalived  
- web01、web02   ： 设置lvs选项  

/// =======================

### 创建keepalived配置文件
keepalived只有一个配置文件keepalived.conf，里面主要包括以下几个配置区域，分别是global_defs、static_ipaddress、static_routes、vrrp_script、vrrp_instance和virtual_server。其中vrrp_instance区域用来定义对外提供服务的VIP区域及其相关属性， virtual_server、real_server区域是用来配合lvs使用的。

在Master(192.168.14.8)上:  

	# cat /etc/keepalived/keepalived.conf
	global_defs {
	   notification_email {
	   #  acassen@firewall.loc   # 指定keepalived在发生切换时需要发送email到的对象，一行一个
	   }
	   #notification_email_from Alexandre.Cassen@firewall.loc  # 指定发件人
	   #smtp_server 192.168.200.1       # smtp 服务器地址
	   #smtp_connect_timeout 30         # smtp 服务器连接超时时间
	   router_id LVS_DEVEL              # 运行keepalived机器的一个标识
	}
	
	vrrp_instance VI_1 {
	    state MASTER                    #
	    interface eth0
	    virtual_router_id 51
	    priority 100
	    advert_int 1
	    authentication {
	        auth_type PASS
	        auth_pass 1111
	    }
	    virtual_ipaddress {
	        192.168.14.200
	    }
	}
	virtual_server 192.168.14.200 80 {
	    delay_loop 6                     # 设置健康检查时间，单位是秒
	    lb_algo wlc                      # 设置负载调度的算法为wlc(最小加权算法)
	    lb_kind DR                       # 设置LVS负载均衡模式为dr机制(NAT、TUN、DR)
	    persistence_timeout 50           # 会话保持时间
	    protocol TCP                     # 指定转发协议类型(TCP、UDP)
	
	    sorry_server   127.0.0.1 80      # 当所有的real_server都不可用时将请求转发到该server上
	
	    real_server 192.168.14.202 80 {  # 设置真实的后端server
	        weight 3                     # 配置节点权值，数字越大权重越高
	        TCP_CHECK {                  # 健康检查方式
	            connect_timeout 10       # 连接超时
	            nb_get_retry 3           # 重试次数
	            delay_before_retry 3     # 重试间隔
	            connect_port 80          # 检查时连接的端口
	        }
	    }
	
	    real_server 192.168.14.203 80 {  # 设置真实的后端server
	        weight 3                     # 配置节点权值，数字越大权重越高
	        TCP_CHECK {                  # 健康检查方式
	            connect_timeout 10       # 连接超时
	            nb_get_retry 3           # 重试次数
	            delay_before_retry 3     # 重试间隔
	            connect_port 80          # 检查时连接的端口
	        }
	    }
	}

其中常用的健康检查方式健康检查方式一共有HTTP_GET、SSL_GET、TCP_CHECK、SMTP_CHECK和MISC_CHECK等。

在Backup(192.168.14.14)上，其keepalived.conf与Master上基本一致，注意修改state为BACKUP，priority值改小即可。

分别在Master、Backup上启动keepalived：

	service keepalived start

### 创建lvs脚本：
在后端real_server上创建lvs脚本，也即web01(192.168.14.202)、web02(192.168.14.203)两台机器上：  

	# cat /etc/init.d/lvs
	#!/bin/bash
	#description:start realserver
	vip=192.168.14.200   # 虚拟ip，注意和Master、Backup上的virtual_ipaddress保持一致
	source /etc/rc.d/init.d/functions
	case $1 in
	start)
	        echo "Start Realserver"
	        /sbin/ifconfig lo:0 $vip broadcast $vip netmask 255.255.255.255 up
	        echo "1" > /proc/sys/net/ipv4/conf/lo/arp_ignore
	        echo "2" > /proc/sys/net/ipv4/conf/lo/arp_announce
	        echo "1" > /proc/sys/net/ipv4/conf/all/arp_ignore
	        echo "2" > /proc/sys/net/ipv4/conf/all/arp_announce
	;;
	stop)
	        echo "Stop Realserver"
	        /sbin/ifconfig lo:0 down
	        echo "0" > /proc/sys/net/ipv4/conf/lo/arp_ignore
	        echo "0" > /proc/sys/net/ipv4/conf/lo/arp_announce
	        echo "0" > /proc/sys/net/ipv4/conf/all/arp_ignore
	        echo "0" > /proc/sys/net/ipv4/conf/all/arp_announce
	;;
	*)
	        echo "Usage: $0 (start | stop)"
	exit 1
	esac

在web01、web02上运行：  

	service lvs start

### 查看ipvs规则
如果想查看生效的规则，只需安装ipvsadm即可。

	# ipvsadm -L -n
	IP Virtual Server version 1.2.1 (size=4096)
	Prot LocalAddress:Port Scheduler Flags
	  -> RemoteAddress:Port           Forward Weight ActiveConn InActConn
	TCP  192.168.14.200:80 wlc persistent 50
	  -> 192.168.14.202:80            Route   3      0          0         
	  -> 192.168.14.203:80            Route   3      0          0   

### 验证
1. 负载均衡测试  
	1. 两台real-server上的web服务都启动，通过VIP访问，正常
	2. 停掉其中一台real-server上的web服务，所有请求被负载到另一台read-server上；
	3. 停掉两台real-server上的web服务，所有请求都被负载到Master主机上预定于的sorry_server上；
	4. 启动real-server上的web服务，新的请求不再转发到sorry_server，而是抓到real-server上；
2. 高可用测试  
	1. 停掉Backup上的keepalived，没有任何影响
	2. 停掉Master上的keepalived(Backup的keepalived要运行)，此时VIP切换到Backup上，所有请求正常处理；
	3. 停掉Master和Backup上的keepalived，无法再通过VIP访问

## Reference
- [借助LVS+Keepalived实现负载均衡](http://www.cnblogs.com/edisonchou/p/4281978.html)
- [LVS负载均衡—基于Keepalived做高可用](http://www.ywnds.com/?p=6162)
- [LVS+Keepalived实现mysql的负载均衡](http://www.cnblogs.com/tangyanbo/p/4305589.html)
- [LVS+Keepalived负载均衡主备&双主架构全攻略](http://zhangge.net/135.html)