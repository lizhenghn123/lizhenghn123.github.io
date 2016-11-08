---
layout: post

title: Nginx反向代理、负载均衡搭建

category: 架构

tags: 负载均衡 Ngnix

keywords: 反向代理 负载均衡 Ngnix

description: 本文整理了Nginx反向代理、负载均衡搭建。

---

## 介绍
nginx的官方介绍：  

	nginx [engine x] is an HTTP and reverse proxy server, a mail proxy server, and a generic TCP/UDP proxy server

nginx不单可以作为强大的web服务器，也可以作为一个反向代理服务器，而且nginx还可以按照调度规则实现动态、静态页面的分离，可以按照轮询、ip哈希、URL哈希、权重等多种方式对后端服务器做负载均衡，同时还支持后端服务器的健康检查。

如果只有一台服务器时,这个服务器挂了,那么对于网站来说是个灾难.因此，这时候的负载均衡就会大显身手了,它会自动剔除挂掉的服务器。

nginx内置了对后端服务器的健康检查功能。如果Nginx proxy后端的某台服务器宕机了，会把返回错误的请求重新提交到另一个节点，不会影响前端访问。它没有独立的健康检查模块，而是使用业务请求作为健康检查，这省去了独立健康检查线程，这是好处。坏处是，当业务复杂时，可能出现误判，例如后端响应超时，这可能是后端宕机，也可能是某个业务请求自身出现问题，跟后端无关。

## 安装
### yum 安装nginx
1. 执行：    
	rpm -ivh http://nginx.org/packages/centos/6/noarch/RPMS/nginx-release-centos-6-0.el6.ngx.noarch.rpm	
2. 查看：   
	yum info nginx
3. 安装  
	yum install nginx
4. 启动   
	service nginx start  

### 源码安装

	wget http://nginx.org/download/nginx-1.10.1.tar.gz  # 以1.10.1版本为例  
	tar -xf nginx-1.10.1.tar.gz  
	./configure  
	make && make install                                # 默认安装到/usr/local/nginx目录  

## 负载均衡
### 负载均衡策略
目前nginx支持以下几种负载策略：  

1. round-robin（轮询, 默认）   
      每个请求按时间顺序逐一分配到不同的后端服务器，如果后端服务器down掉，能自动剔除。 
2. least_conn  
	最少连接数。
3. least\_time   
	最少时间花费，nginx会选择平均延迟最低的后台服务器。这里有两个参数用来选举：header表示是计算从后台返回的第一个字节，last_byte计算的是从后台返回的所有数据时间。比如：  
		
		upstream bakend { 
			least_time header;
			server 192.168.100.104:80; 
			server 192.168.100.105:80; 
		} 

2. weight  
      指定轮询几率，weight和访问比率成正比，用于后端服务器性能不均的情况。 例如：  

      	upstream bakend { 
			server 192.168.100.104 weight=10; 
			server 192.168.100.105 weight=10; 
		} 
3. ip_hash  
      每个请求按访问ip的hash结果分配，这样每个访客固定访问一个后端服务器，可以解决session的问题。例如  
		
		upstream bakend { 
			ip_hash; 
			server 192.168.100.104:80; 
			server 192.168.100.105:80; 
		} 
4. fair（第三方）  
      按后端服务器的响应时间来分配请求，响应时间短的优先分配。例如  
		
		upstream bakend { 
			fair; 
			server 192.168.100.104:80; 
			server 192.168.100.105:80; 
		}   

	使用该机制时需要在源码编译nginx时加上ngx\_http\_upstream\_fair\_module的编译，需要从[github](https://github.com/gnosek/nginx-upstream-fair)下载。  

		git clone https://github.com/gnosek/nginx-upstream-fair /tmp/nginx-upstream-fair    
		./configure --add-module=/tmp/nginx-upstream-fair/   # 在nginx目录下编译时带上该模块

5. url_hash（第三方）  
      基于url的哈希。例如  
		
		upstream bakend { 
			hash $request_uri; 
			server 192.168.100.104:80; 
			server 192.168.100.105:80; 
		}   

6. 一致性哈希（第三方）  
ngx\_http\_upstream\_consistent\_hash 模块是一个负载均衡器，使用一个内部一致性hash算法来选择合适的后端节点。该模块通过使用客户端信息(如：$ip, $uri, $args等变量)作为参数，使用一致性hash算法将客户端映射到后端节点。该模块可以根据配置参数采取不同的方式将请求均匀映射到后端机器，比如：  

 - consistent_hash $remote\_addr：可以根据客户端ip映射
 - consistent_hash $request\_uri： 根据客户端请求的uri映射
 - consistent_hash $args：根据客户端携带的参数进行映射  

		假设一个url的形式是http://ip:port/test/username=ew&id=245sd&score=34。如果是根据其中id来进行hash的话，则：  

			consistent_hash  $arg_id;  

	使用该机制时需要在源码编译nginx时加上consistent\_hash的编译，需要从[github](https://github.com/replay/ngx_http_consistent_hash)下载。  

		git clone https://github.com/replay/ngx_http_consistent_hash /tmp/ngx_http_consistent_hash    # 下载一致性hash模块
		./configure --add-module=/tmp/ngx_http_consistent_hash/   # 在nginx目录下编译时带上该模块

一个示例配置如下（以下内容是在http节点里添加的）：  
	
	upstream myServer {
	    server 127.0.0.1:9090 down; 
	    server 127.0.0.1:8080 weight=2; 
	    server 127.0.0.1:6060; 
	    server 127.0.0.1:7070 backup; 
	}
	 
	proxy_pass http://myServer;    # 在需要使用负载的Server节点下添加

upstream 节点中每个状态的意义:  

- down  
表示单前的server暂时不参与负载 
- weight  
默认为1.weight越大，负载的权重就越大。 
- max\_fails  
允许请求失败的次数默认为1.当超过最大次数时，返回proxy\_next\_upstream 模块定义的错误 
- fail\_timeout  
max\_fails 次失败后，暂停的时间。 
- backup  
其它所有的非backup机器down或者忙的时候，请求backup机器。所以这台机器压力会最轻。  
疑问：backup和hash、consistent_hash有冲突，不能同时设置，但是[官网给出的示例](https://nginx.org/en/docs/stream/ngx_stream_upstream_module.html)是可以的，还不知道为什么？？？

另外，对于如下两种配置：  
	
	upstream my_server {                                                         
	    server 10.0.0.2:8080;                                                
	    keepalive 2000;
	}
	server {
	    listen       80;                                                         
	    server_name  10.0.0.1;                                               
	    client_max_body_size 1024M;
	
	    location /my/ {
	        proxy_pass http://my_server/;
	        proxy_set_header Host $host:$server_port;
	    }
	}
和  
	
	upstream my_server {                                                         
	    server 10.0.0.2:8080;                                                
	    keepalive 2000;
	}
	server {
	    listen       80;                                                         
	    server_name  10.0.0.1;                                               
	    client_max_body_size 1024M;
	
	    location /my/ {
	        proxy_pass http://my_server;
	        proxy_set_header Host $host:$server_port;
	    }
	}
按第一种配置的话，访问nginx地址`http://10.0.0.1:80/my`的请求会被转发到my_server服务地址`http://10.0.0.2:8080/`；而按第二种配置的话，访问nginx地址`http://10.0.0.1:80/my`的请求会被转发到my_server服务地址`http://10.0.0.2:8080/my`。这是因为proxy_pass参数中如果不包含url的路径，则会将location的pattern识别的路径作为绝对路径。

### 多台机器间session共享问题
配置负载均衡并不麻烦，但是最关键的一个问题是怎么实现多台服务器之间session的共享。  
这里也有几个思路可以作为参考：  

1. 不使用session，改为使用cookie  
2. 应用自己实现session共享  
比如自己的应用通过redis或者memcached来保存session，相当于将session通过第三方模块存储。  
3. ip_hash  
是将某一个ip的所有请求都转发到同一个后台服务器。这样下来nginx前面的一个客户端和nginx后面的某一个后端就保持一致的联系。

## TCP负载均衡
nginx默认都是在应用层协议进行负载均衡的（比如HTTP），而事实上从1.9.0版本开始，nginx也支持tcp协议的负载均衡。做法并没有什么复杂的，一个简单的配置如下所示：
	
	stream {
	    upstream realservers{
	        hash $remote_addr consistent;
	        server 192.168.14.207:8888 weight=5 max_fails=3 fail_timeout=30s;
	    }
	    server{
	        listen 8001;
	        proxy_connect_timeout 1s;
	        proxy_timeout 3s;
	        proxy_pass realservers;
	    }
	}

此时nginx监听在8001端口，真实tcp server监听在192.168.14.207:8888。

注意： tcp协议的负载并不在nginx的默认编译选项中，需要在编译选项中加入`--with-stream`项，比如：  

	./configure --with-stream ....

## nginx 日志
nginx的日志保存为两种：access.log和error.log。其中access.log中每一行都是客户端访问nginx的一个请求，其格式如下：  

	$remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent" $http_x_forwarded_for

比如如下两条log：  

	192.168.10.18 - - [25/Jul/2016:09:42:53 +0800] "GET /favicon.ico HTTP/1.1" 404 281 "-" "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0"
	192.168.10.56 - - [25/Jul/2016:09:42:59 +0800] "GET /index.html?username=224&id=24&fdfd=23456456 HTTP/1.1" 200 83 "-" "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36"

nginx 中的一些请求头信息：
	
	$arg_PARAMETER 这个变量包含在查询字符串时GET请求PARAMETER的值。
	$args 这个变量等于请求行中的参数。
	$binary_remote_addr 二进制码形式的客户端地址。
	$body_bytes_sent
	$content_length 请求头中的Content-length字段。
	$content_type 请求头中的Content-Type字段。
	$cookie_COOKIE cookie COOKIE的值。
	$document_root 当前请求在root指令中指定的值。
	$document_uri 与$uri相同。
	$host 请求中的主机头字段，如果请求中的主机头不可用，则为服务器处理请求的服务器名称。
	$is_args 如果$args设置，值为"?"，否则为""。
	$limit_rate 这个变量可以限制连接速率。
	$nginx_version 当前运行的nginx版本号。
	$query_string 与$args相同。
	$remote_addr 客户端的IP地址。
	$remote_port 客户端的端口。
	$remote_user 已经经过Auth Basic Module验证的用户名。
	$request_filename 当前连接请求的文件路径，由root或alias指令与URI请求生成。
	$request_body 这个变量（0.7.58+）包含请求的主要信息。在使用proxy_pass或fastcgi_pass指令的location中比较有意义。
	$request_body_file 客户端请求主体信息的临时文件名。
	$request_completion 请求完成
	$request_method 这个变量是客户端请求的动作，通常为GET或POST。包括0.8.20及之前的版本中，这个变量总为main request中的动作，如果当前请求是一个子请求，并不使用这个当前请求的动作。
	$request_uri 这个变量等于包含一些客户端请求参数的原始URI，它无法修改，请查看$uri更改或重写URI。
	$schemeHTTP 方法（如http，https）。按需使用，例：
	rewrite ^(.+)$ $scheme://example.com$1 redirect;
	$server_addr 服务器地址，在完成一次系统调用后可以确定这个值，如果要绕开系统调用，则必须在listen中指定地址并且使用bind参数。
	$server_name 服务器名称。
	$server_port 请求到达服务器的端口号。
	$server_protocol 请求使用的协议，通常是HTTP/1.0或HTTP/1.1。
	$uri 请求中的当前URI(不带请求参数，参数位于$args)，可以不同于浏览器传递的$request_uri的值，它可以通过内部重定向，或者使用index指令进行修改。

上面的这些是nginx 支持一些内置的变量，当然我们可以自定义，例如$http\_x\_forwarded\_for，这个变量就是自定义的，用来获得用了代理用户的真实IP：  

	proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

## Reference
- [Linux（CentOS）下，下载安装Nginx并配置](http://blog.csdn.net/gaojinshan/article/details/37603157)  
- [Nginx load balancer](https://www.nginx.com/resources/admin-guide/load-balancer/)  
- [Nginx Upstream Consistent Hash](https://www.nginx.com/resources/wiki/modules/consistent_hash)  
- [Nginx fair_balancer](https://www.nginx.com/resources/wiki/modules/fair_balancer)
- [Nginx choose upstream depending on args](http://serverfault.com/questions/561993/nginx-choose-upstream-depending-on-args)
- [how to use url pathname as upstream hash in nginx](http://stackoverflow.com/questions/31994395/how-to-use-url-pathname-as-upstream-hash-in-nginx)
- [http://blog.51yip.com/apachenginx/1277.html](http://blog.51yip.com/apachenginx/1277.html)
- [简单测试nginx1.90做TCP协议负载均衡的功能](http://www.cnblogs.com/tzyy/p/4485613.html)
- [Nginx Tcp Proxy](http://nginx.org/en/docs/stream/ngx_stream_core_module.html)