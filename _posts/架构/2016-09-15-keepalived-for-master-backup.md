---
layout: post

title: 使用keepalived搭建主备切换环境

category: 架构

tags: 架构

keywords: 架构 keepalived 主备

description: 使用keepalived搭建主备切换环境。

---

## 1. keepalived介绍
Keepalived是Linux下一个轻量级的高可用解决方案，它与HeartBeat、RoseHA实现的功能类似，都可以实现服务或者网络的高可用，但是又有差别：HeartBeat是一个专业的、功能完善的高可用软件，它提供了HA软件所需的基本功能，比如心跳检测和资源接管，监测集群中的系统服务，在群集节点间转移共享IP地址的所有者等，HeartBeat功能强大，但是部署和使用相对比较麻烦；与HeartBeat相比，Keepalived主要是通过虚拟路由冗余来实现高可用功能，虽然它没有HeartBeat功能强大，但Keepalived部署和使用非常简单，所有配置只需一个配置文件即可完成。

keepalived主要有三个模块，分别是core、check和vrrp。core模块为keepalived的核心，负责主进程的启动、维护以及全局配置文件的加载和解析。check负责健康检查，包括常见的各种检查方式。vrrp模块是来实现VRRP协议的。

keepalived实现的功能主要有三个：  

1. 将IP地址飘移到其他节点上，
2. 在另一个主机上生成ipvs规则
3. 健康状况检查。

keepalived通过软件的方式在其内部模拟实现VRRP协议，然后借助于VRRP协议实现IP地址漂移。

## 2. keepalived用来做什么
Keepalived是基于VRRP协议的高级应用，作用于网络层、传输层和应用层交换机制的处理高可用的软件。主要用作RealServer的健康状态检查以及LoadBalance主机和BackUP主机之间failover的实现。

Keepalived起初是为LVS设计的，专门用来监控集群系统中各个服务节点的状态。它根据layer3, 4 & 5交换机制检测每个服务节点的状态，如果某个服务节点出现异常，或工作出现故障，Keepalived将检测到，并将出现故障的服务节点从集群系统中剔除，而在故障节点恢复正常后，Keepalived又可以自动将此服务节点重新加入到服务器集群中，这些工作全部自动完成，不需要人工干涉，需要人工完成的只是修复出现故障的服务节点。

Keepalived后来又加入了VRRP的功能，VRRP是Virtual Router Redundancy Protocol（虚拟路由器冗余协议）的缩写，它出现的目的是为了解决静态路由出现的单点故障问题，通过VRRP可以实现网络不间断地、稳定地运行。因此，Keepalived一方面具有服务器状态检测和故障隔离功能，另一方面也具有HA cluster功能。

**keepalived可以实现轻量级的高可用，一般用于前端高可用，且不需要共享存储，一般常用于两个节点的高可用（常见的前端高可用组合有LVS+Keepalived、Nginx+Keepalived、HAproxy+Keepalived）。**

## 3. Keepalived工作原理
Keepalived作为一个高性能集群软件，它还能实现对集群中服务器运行状态的监控及故障隔离。接下来介绍下Keepalived对服务器运行状态监控和检测的工作原理。 Keepalived工作在TCP/IP参考模型的第三、第四和第五层，也就是网络层、传输层和应用层。根据TCP/IP参考模型各层所能实现的功能，Keepalived运行机制如下：

1. 在网络层，运行着四个重要的协议：互连网协议IP、互连网控制报文协议ICMP、地址转换协议ARP以及反向地址转换协议RARP。Keepalived在网络层采用的最常见的工作方式是通过ICMP协议向服务器集群中的每个节点发送一个ICMP的数据包（类似于ping实现的功能），如果某个节点没有返回响应数据包，那么就认为此节点发生了故障，Keepalived将报告此节点失效，并从服务器集群中剔除故障节点。  
2. 在传输层，提供了两个主要的协议：传输控制协议TCP和用户数据协议UDP。传输控制协议TCP可以提供可靠的数据传输服务，IP地址和端口，代表一个TCP连接的一个连接端。要获得TCP服务,须在发送机的一个端口上和接收机的一个端口上建立连接，而Keepalived在传输层就是利用TCP协议的端口连接和扫描技术来判断集群节点是否正常的。比如，对于常见的Web服务默认的80端口、SSH服务默认的22端口等，Keepalived一旦在传输层探测到这些端口没有响应数据返回，就认为这些端口发生异常，然后强制将此端口对应的节点从服务器集群组中移除。  
3. 在应用层，可以运行FTP、TELNET、SMTP、DNS等各种不同类型的高层协议，Keepalived的运行方式也更加全面化和复杂化，用户可以通过自定义Keepalived的工作方式，例如用户可以通过编写程序来运行Keepalived，而Keepalived将根据用户的设定检测各种程序或服务是否允许正常，如果Keepalived的检测结果与用户设定不一致时，Keepalived将把对应的服务从服务器中移除。

## 4. 安装

在线安装：

	# yum -y install keepalived ipvsadm

或者源码安装：

	# wget http://www.keepalived.org/software/keepalived-1.2.15.tar.gz
	# tar -xf keepalived-1.2.15.tar.gz && cd keepalived-1.2.15
	# ./configure && make && make install
	# wget http://www.linuxvirtualserver.org/software/kernel-2.6/ipvsadm-1.26.tar.gz
	# tar -xf ipvsadm-1.26.tar.gz && cd ipvsadm-1.26/
	# make && make install

关闭SELinux(改完需重启服务器)：

	# sed -i 's#^SELINUX=.*#SELINUX=disabled#' /etc/sysconfig/selinux   

## 5. 实战
本文搭建、测试Keepalived高可用架构。测试环境使用两台真实服务器，如下介绍：
	
	虚拟ip     ： 192.168.14.166，默认指向Master(192.168.14.8)
	真实服务器1 ： Master，192.168.14.8， 该机器上同时运行Apache Httpd服务(端口80)和一个python脚本的HttpServer服务(端口8000)；
	真实服务器2 ： Backup，192.168.14.14， 该机器上同时运行Apache Httpd服务(端口80)和一个python脚本的HttpServer服务(端口8000)；
系统部署结构如下所示：  
	
	                   +-------------+
	                   |    router   |
	                   +-------------+
	                          |
	                          +
	    Master            keepalived           Backup
	  192.168.14.8      192.168.14.166     192.168.14.14
	+-------------+    +-------------+    +-------------+
	|  httpd_01   |----| virtual IP  |----|  httpd_01   |
	+-------------+    +-------------+    +-------------+   
  
在Master和Backup的运行的两个测试服务单独运行效果如下：  

Master(192.168.14.8)：  

![](http://i.imgur.com/Cei50iN.png)  

Backup(192.168.14.14)：  

![](http://i.imgur.com/R0a1IJi.png)  
 
此时 虚拟ip(192.168.14.166)是不存在的，也即无法访问。

### 5.1 创建keepalived配置文件
keepalived只有一个配置文件keepalived.conf，里面主要包括以下几个配置区域，分别是global\_defs、vrrp\_script、vrrp\_instance和virtual\_server。其中vrrp\_instance区域用来定义对外提供服务的VIP区域及其相关属性， 而virtual\_server和real\_server区域是用来配合lvs使用的，本次暂时用不到。

在Master(192.168.14.8)上：  

	# cat /etc/keepalived/keepalived.conf
	global_defs {
	    notification_email {
	        #mr@mruse.cn       # 指定keepalived在发生切换时需要发送email到的对象，一行一个
	        #sysadmin@firewall.loc
	    }
	    notification_email_from xxx@163.com   # 指定发件人
	    smtp_server smtp@163.com              # smtp 服务器地址
	    smtp_connect_timeout 30               # smtp 服务器连接超时时间
	    router_id LVS_1 # 标识本节点的字符串,通常为hostname,但不一定非得是hostname,故障发生时,邮件通知会用到
	}
	
	vrrp_instance VI_1 {  # 实例名称
	    state MASTER      # 可以是MASTER或BACKUP，不过当其他节点keepalived启动时会将priority比较大的节点选举为MASTER
	    interface eth0    # 节点固有IP（非VIP）的网卡，用来发VRRP包做心跳检测
	    virtual_router_id 51 # 虚拟路由ID,取值在0-255之间,用来区分多个instance的VRRP组播,同一网段内ID不能重复;主备必须为一样;
	    priority 100      # 用来选举master的,要成为master那么这个选项的值最好高于其他机器50个点,该项取值范围是1-255(在此范围之外会被识别成默认值100)
	    advert_int 1      # 检查间隔默认为1秒,即1秒进行一次master选举(可以认为是健康查检时间间隔)
	    authentication {  # 认证区域,认证类型有PASS和HA（IPSEC）,推荐使用PASS(密码只识别前8位)
	        auth_type PASS  # 默认是PASS认证
	        auth_pass MrUse # PASS认证密码
	    }
	    virtual_ipaddress {
	        192.168.14.166    # 虚拟VIP地址,允许多个
	    }
	}

在Backup(192.168.14.14)上keepalived.conf文件和Master上的基本一致，拷贝过来，并修改其中的以下几项即可：  

	state BACKUP     # 此值可设置或不设置，只要保证下面的priority不一致即可
	interface eth0   # 根据实际情况选择网卡
	priority 40      # 此值要一定小于Master机器上的值，最好相差不少于50

注意：在配置keepalived.conf时，需要特别注意配置文件的语法格式以及出现重复的VIP，因为keepalived在启动时并不检测配置文件的正确性，即使没有配置文件，keepalived也能照样启动，所以一定要保证配置文件的正确性。

启动Keepalived并加入开机启动：
	
	/etc/init.d/keepalived restart
	chkconfig keepalived on

启动Keepalived：

	# service keepalived start  # 此时会尝试读取/etc/keepalived/keepalived.conf配置文件
    如果配置文件位于其他地方，则：
	# keepalived -f /xxx/path/keepalived.conf

启动之后，keepalived会运行三个进程：
	
	# ps -ef | grep keepalived
	root      2030     1  0 08:59 ?        00:00:01 keepalived -f /etc/keepalived/keepalived.conf
	root      2041  2030  0 08:59 ?        00:00:01 keepalived -f /etc/keepalived/keepalived.conf
	root      2042  2030  0 08:59 ?        00:00:03 keepalived -f /etc/keepalived/keepalived.conf

通过以下命令可以查看VIP当前绑定在哪个机器上：

	# ip addr 
	1: lo: <LOOPBACK,UP,LOWER_UP> mtu 16436 qdisc noqueue state UNKNOWN
	    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
	    inet 127.0.0.1/8 scope host lo
	2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP qlen 1000
	    link/ether 08:00:27:8e:b8:31 brd ff:ff:ff:ff:ff:ff
	    inet 192.168.14.8/16 brd 192.168.255.255 scope global eth0
	    inet 192.168.14.166/32 scope global eth0            ## 注意此行

### 5.2 测试正常情况
在Master和Backup上分别启动keepalived。此时VIP(192.168.14.166)是可访问的，也可以ping通，通过虚拟ip（192.168.14.166）访问两个测试服务：  

![](http://i.imgur.com/YoNYUb5.png)  

会发现此时VIP(192.168.14.166)指向了Master(192.168.14.8)上的服务。如果从另一台机器上通过ssh连接VIP(192.168.14.166)，可以登陆成功且登陆的主机即是Master(192.168.14.8)。

此时在Master(192.168.14.8)上运行以下命令，会发现VIP绑定在了Master上：  

	# ip addr show eth0
	2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP qlen 1000
    link/ether 08:00:27:8e:b8:31 brd ff:ff:ff:ff:ff:ff
    inet 192.168.14.8/16 brd 192.168.255.255 scope global eth0

### 5.3 测试Master宕掉的情况
现在停掉Master(192.168.14.8)上的keepalived用来模拟Master机器宕掉或者网络不通，此时再通过虚拟ip（192.168.14.166）访问两个测试服务会发现**所有服务都已指向了Backup**(192.168.14.14)：  

![](http://i.imgur.com/7KqPg9x.png)  

此时在Backup(192.168.14.14)上运行以下命令，会发现VIP绑定在了Backup上：  

	# ip addr show eth0 
	2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP qlen 1000
    link/ether 08:00:27:76:6c:46 brd ff:ff:ff:ff:ff:ff
    inet 192.168.14.14/16 brd 192.168.255.255 scope global eth0
    inet 192.168.14.166/32 scope global eth0
而Master上已经没有了该VIP(192.168.14.166)。

疑问：  

1. **多次测试时有的时候停掉Master上的keepalived，通过VIP切到Backup上时比较慢；**
2. **如果停掉Master的网络，发现不能切换；**

**不知道是我哪里设置错了？？？？？？？？？？？**

### 5.4 测试Master宕掉又恢复的情况
接上一测试，此时再重新启动Master(192.168.14.8)上的keepalived，模拟Master机器已开机或网络已修复，，此时再通过虚拟ip（192.168.14.166）访问两个测试服务会发现所有服务**又都重新指向了Master**(192.168.14.8)，这里就不截图了，可以自行验证。  

### 5.5 测试某一服务挂掉的情况
这里假设所有设置都是初始状态，VIP指向Master，但将Master(192.168.14.8)的Apache Httpd服务停掉，然后通过VIP访问：  

![](http://i.imgur.com/WhWa4dK.png)

此时发现VIP仍指向Master，但是80端口的Http服务已不可访问，而8000端口的服务还可以继续访问且仍指向Master。

## 6 解决Master存在但服务宕掉的问题
如果解决上面VIP指向Master，但是Master上服务宕掉的问题呢？其实也简单，我们在keepalived.conf中增加对Httpd服务的检测（完整配置文件）：
	
	# cat /etc/keepalived/keepalived.conf 
	global_defs {
	   notification_email {
	   #  acassen@firewall.loc   # 指定keepalived在发生切换时需要发送email到的对象，一行一个
	   #  sysadmin@firewall.loc
	   }
	   #notification_email_from Alexandre.Cassen@firewall.loc  # 指定发件人
	   #smtp_server 192.168.200.1     # smtp 服务器地址 
	   #smtp_connect_timeout 30       # smtp 服务器连接超时时间
	   router_id LVS_DEVEL            # 标识本节点的字符串,通常为hostname,但不一定非得是hostname,故障发生时,邮件通知会用到
	}
	###　新增　###
	vrrp_script chk_httpd {
	    script "/etc/keepalived/check_and_start_httpd.sh"   # apache httpd 服务检测并试图重启
	    interval 2                    # 每2s检查一次
	    weight -5                     # 检测失败（脚本返回非0）则优先级减少5个值
	    fall 3                        # 如果连续失败次数达到此值，则认为服务器已down
	    rise 2                        # 如果连续成功次数达到此值，则认为服务器已up，但不修改优先级
	}
	
	vrrp_instance VI_1 {              # 实例名称
	    state MASTER                  # 可以是MASTER或BACKUP，不过当其他节点keepalived启动时会自动将priority比较大的节点选举为MASTER
	    interface eth0                # 节点固有IP（非VIP）的网卡，用来发VRRP包做心跳检测
	    virtual_router_id 51          # 虚拟路由ID,取值在0-255之间,用来区分多个instance的VRRP组播,同一网段内ID不能重复;主备必须为一样
	    priority 100                  # 用来选举master的,要成为master那么这个选项的值最好高于其他机器50个点,该项取值范围是1-255(在此范围之外会被识别成默认值100)
	    advert_int 1                  # 检查间隔默认为1秒,即1秒进行一次master选举(可以认为是健康查检时间间隔)
	    authentication {              # 认证区域,认证类型有PASS和HA（IPSEC）,推荐使用PASS(密码只识别前8位)
	        auth_type PASS            # 默认是PASS认证
	        auth_pass 1111            # PASS认证密码
	    }
	    virtual_ipaddress {
	        192.168.14.166            # 虚拟VIP地址,允许多个,一行一个
	    #    192.168.200.17
	    }
	    ###　新增　###
	    track_script {                # 引用VRRP脚本，即在 vrrp_script 部分指定的名字。定期运行它们来改变优先级，并最终引发主备切换。
	        chk_httpd          
	    }                
	}

再写一个脚本：  
	
	# cat /etc/keepalived/check_and_start_httpd.sh 
	#!/bin/bash
	counter=$(ps -C httpd --no-heading|wc -l)
	if [ "${counter}" = "0" ]; then
	    service httpd start
	    sleep 2
	    counter=$(ps -C httpd --no-heading|wc -l)
	    if [ "${counter}" = "0" ]; then
	        /etc/rc.d/init.d/keepalived stop
	    fi
	fi
该脚本的目的是用来检测httpd服务是否存在，如果不存在就重启，重启失败就关闭本机keepalived以便VIP切换到Backup机器上。该脚本由keepalived进行调用。

此时停掉Apache Httpd服务：

	# date && service httpd status
	2016年 09月 13日 星期二 11:32:07 CST
	httpd (pid  20374) 正在运行...
	# date && service httpd stop  
	2016年 09月 13日 星期二 11:32:13 CST
	停止 httpd：                                               [确定]
	# date && service httpd status
	2016年 09月 13日 星期二 11:32:14 CST
	httpd (pid  21623) 正在运行...

可以发现Httpd停掉之后就进行自动重启了(前后pid不一样)，而且重启速度也比较快(从date显示的时间可以看到)。当然这也不能保证所有的Http请求都不丢弃(事实上很可能有部分请求是失败的)。

配置8000端口的python版HttpServer测试服务，与上面类似，这里就不再验证了。

### vrrp_script
告诉 keepalived 在什么情况下切换，所以尤为重要。可以有多个 vrrp_script

- script ： 自己写的检测脚本。也可以是一行命令如killall -0 nginx
- interval 2 ： 每2s检测一次
- weight -5 ： 检测失败（脚本返回非0）则优先级 -5
- fall 2 ： 检测连续 2 次失败才算确定是真失败。会用weight减少优先级（1-255之间）
- rise 1 ： 检测 1 次成功就算成功。但不修改优先级

这里要提示一下script一般有2种写法：

1. 通过脚本执行的返回结果，改变优先级，keepalived继续发送通告消息，backup比较优先级再决定
2. 脚本里面检测到异常，直接关闭keepalived进程，backup机器接收不到advertisement会抢占IP

上文 vrrp_script 配置部分`/etc/keepalived/check_and_start_httpd.sh`属于第2种情况（脚本中关闭keepalived）。个人更倾向于通过shell脚本判断，但有异常时exit 1，正常退出exit 0，然后keepalived根据动态调整的 vrrp_instance 优先级选举决定是否抢占VIP：

- 如果脚本执行结果为0，并且weight配置的值大于0，则优先级相应的增加
- 如果脚本执行结果非0，并且weight配置的值小于0，则优先级相应的减少
- 其他情况，原本配置的优先级不变，即配置文件中priority对应的值

提示：

- 优先级不会不断的提高或者降低
- 可以编写多个检测脚本并为每个检测脚本设置不同的weight（在配置中列出就行）
- 不管提高优先级还是降低优先级，最终优先级的范围是在[1,254]，不会出现优先级小于等于0或者优先级大于等于255的情况
- 在MASTER节点的 vrrp_instance 中 配置 nopreempt ，当它异常恢复后，即使它 prio 更高也不会抢占，这样可以避免正常情况下做无谓的切换

以上可以做到利用脚本检测业务进程的状态，并动态调整优先级从而实现主备切换。

上面写的check_and_start_httpd.sh脚本在发现httpd关闭时会试图重启httpd，如果重启失败则停掉本机的keepalived，以触发主备切换。事实上，脚本内容可以根据自己的业务灵活定义，比如使用curl命令连续获取2次主页，如果3s内没有响应则触发切换：

	#!/bin/bash
	count=0
	for (( k=0; k<2; k++ ))
	do
	    check_code=$( curl --connect-timeout 3 -sL -w "%{http_code}\\n" http://localhost/index.html -o /dev/null )
	    if [ "$check_code" != "200" ]; then
	        count=$(expr $count + 1)
	        sleep 3
	        continue
	    else
	        count=0
	        break
	    fi
	done
	if [ "$count" != "0" ]; then
	#   /etc/init.d/keepalived stop
	    exit 1
	else
	    exit 0
	fi

## 7. 其他
以上演示中，主要以Apache Httpd作为测试服务，其实这里使用Nginx也是可以的，这样就相当于Nginx是前端，做到高可用，然后Nginx上部署反向代理、负载均衡，将业务请求转发到真实的业务服务器上，**一套主备切换+负载均衡的高可用架构就形成了**。

## 8. Reference
- [高性能集群软件Keepalived之基础知识篇](http://blog.chinaunix.net/uid-203897-id-5024903.html)
- [Nginx+Keepalived实现站点高可用](http://seanlook.com/2015/05/18/nginx-keepalived-ha/)  
- [http://my.oschina.net/lzhaoqiang/blog/700753  ](http://www.cnblogs.com/wang-meng/p/5861174.html)
