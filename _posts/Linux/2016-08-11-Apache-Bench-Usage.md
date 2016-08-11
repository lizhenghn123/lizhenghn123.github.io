---
layout: post

title: 压力测试工具ab(Apache Bench)的使用

category: Linux

tags: Linux 

keywords: Linux 压力测试工具 Apache ab 

description: 本文介绍了压力测试工具ab(Apache Bench)的使用。

---


## 1. ab工具介绍
ab全称为：apache bench。

在官网上的解释如下：
    
    ab是Apache超文本传输协议(HTTP)的性能测试工具。其设计意图是描绘当前所安装的Apache的执行性能，主要是显示你安装的Apache每秒可以处理多少个请求。

ab其实是apache服务器自带的压力测试工具。但它除了可以对apache服务器进行压力测试之外，也可以对其它类似web server进行压力测试，比如nginx、tomcat、IIS等等。

linux系统下安装过apache httpd服务后就可以直接使用ab测试工具了，否则，可以到其官网下载安装，地址是[http://httpd.apache.org/](http://httpd.apache.org/)。

windows系统要想使用ab工具，也是通过上面的地址自行下载Windows版本即可。

## 2. 一些常见指标
在介绍如何使用ab工具之前，先介绍一些常见的性能测试指标。  

1. 吞吐率（Requests per second）  
概念：服务器并发处理能力的量化描述，单位是reqs/s，指的是某个并发用户数下单位时间内处理的请求数。某个并发用户数下单位时间内能处理的最大请求数，称之为最大吞吐率。  
计算公式：总请求数 / 处理完成这些请求数所花费的时间，即  

	`Request per second = Complete requests / Time taken for tests`

2. 并发连接数（The number of concurrent connections）  
概念：某个时刻服务器所接受的请求数目，简单的讲，就是一个会话。

3. 并发用户数（The number of concurrent users，Concurrency Level）  
概念：要注意区分这个概念和并发连接数之间的区别，一个用户可能同时会产生多个会话，也即连接数。

4. 用户平均请求等待时间（Time per request）  
计算公式：处理完成所有请求数所花费的时间/ （总请求数 / 并发用户数），即  

	`Time per request = Time taken for tests /（ Complete requests / Concurrency Level）`

5. 服务器平均请求等待时间（Time per request: across all concurrent requests）  
计算公式：处理完成所有请求数所花费的时间 / 总请求数，即  


    `Time taken for / testsComplete requests`  

	可以看到，它是吞吐率的倒数。同时，它也等于用户平均请求等待时间/并发用户数，即  

	`Time per request / Concurrency Level`

## 3. 如何使用
常用命令：  

	ab -n 800 -c 100  http://192.168.14.8/    # 总共800个请求，100路并发
	ab -t 60 -c 100 http://192.168.14.8/	  # 总共运行60秒，100路并发

常见参数有：  

    -n requests     总共要运行的请求数
    -c concurrency  多少路并发请求
    -t timelimit    Seconds to max. wait for responses
    -b windowsize   tcp接收/发送缓冲区大小设置，单位是字节数
    -p postfile     postfile包含了要post的数据，注意要同时设置 -T 参数
    -u putfile      putfile包含了要put的数据，注意要同时设置 -T 参数
    -T content-type http请求头content-type设置，比如 'application/x-www-form-urlencoded'，默认是 'text/plain'
    -X proxy:port   设置反向代理服务器
    -g filename     输出统计结果到filename中，该格式可以给gnuplot使用

更多参数及其详细介绍可以参考：[http://httpd.apache.org/docs/2.2/programs/ab.html](http://httpd.apache.org/docs/2.2/programs/ab.html)。

## 4. 实例演示
通过100路并发，累计请求15000次，来练习ab工具的使用，被测服务器是apache httpd。

	  ab -n 15000 -c 100  http://192.168.14.202/index.html
运行结束后，有如下输出：  
		
	This is ApacheBench, Version 2.3 <$Revision: 655654 $>
	Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
	Licensed to The Apache Software Foundation, http://www.apache.org/
	
	Benchmarking 192.168.14.202 (be patient)
	Completed 1500 requests
	Completed 3000 requests
	Completed 4500 requests
	Completed 6000 requests
	Completed 7500 requests
	Completed 9000 requests
	Completed 10500 requests
	Completed 12000 requests
	Completed 13500 requests
	Completed 15000 requests
	Finished 15000 requests
	
	
	Server Software:        Apache/2.2.15
	Server Hostname:        192.168.14.202
	Server Port:            80
	
	Document Path:          /index.html
	Document Length:        16 bytes
	
	Concurrency Level:      100
	Time taken for tests:   4.610 seconds
	Complete requests:      15000
	Failed requests:        0
	Write errors:           0
	Total transferred:      3126656 bytes
	HTML transferred:       240512 bytes
	Requests per second:    3253.54 [#/sec] (mean)
	Time per request:       30.736 [ms] (mean)
	Time per request:       0.307 [ms] (mean, across all concurrent requests)
	Transfer rate:          662.29 [Kbytes/sec] received
	
	Connection Times (ms)
	              min  mean[+/-sd] median   max
	Connect:        2    6   2.4      6      18
	Processing:     9   24   2.9     24      31
	Waiting:        6   22   3.3     22      30
	Total:         19   31   2.6     31      39
	
	Percentage of the requests served within a certain time (ms)
	  50%     31
	  66%     32
	  75%     32
	  80%     33
	  90%     34
	  95%     35
	  98%     36
	  99%     37
	 100%     39 (longest request)

其中输出结果中包含了几大块信息提示：  

1. 服务器信息  
	
    	Server Software:Apache/2.2.15  
    	Server Hostname:192.168.14.202  
    	Server Port:80  
	说明服务器端使用的是apache，服务器域名是192.168.14.202，端口是80。
2. 文档信息  
    
    	Document Path:  /index.html
    	Document Length:16 bytes
	说明请求的页面是index.html，页面大小是16字节。
3. 性能指标(重要)  
    
    	Concurrency Level:  100						并发请求数
    	Time taken for tests:   4.610 seconds		整个测试花费的时间
    	Complete requests:  15000					完成的请求数
    	Failed requests:0							失败的请求数
    	Write errors:   0							整个测试中的网络传输量
    	Total transferred:  3126656 bytes			整个测试中的网络传输量
    	HTML transferred:   240512 bytes			整个测试中的HTML内容传输量
    	Requests per second:3253.54 [#/sec] (mean)	吞吐量，大家最关心的指标之一，相当于 LR 中的每秒事务数，后面括号中的 mean 表示这是一个平均值，值越大越好
    	Time per request:   30.736 [ms] (mean)		服务器收到请求，响应页面要花费的时间，也即用户平均等待时间，大家最关心的指标之二，相当于 LR 中的平均事务响应时间，后面括号中的 mean 表示这是一个平均值，值越小越好
    	Time per request:   0.307 [ms] (mean, across all concurrent requests)	服务器请求处理的平均花费时间
    	Transfer rate: 662.29 [Kbytes/sec] received 平均每秒网络上的流量，可以帮助排除是否存在网络流量过大导致响应时间延长的问题

4. 请求时间的统计信息  
    
    	Connection Times (ms)
    	  			min  mean[+/-sd] median   max
    	Connect:	2	  6   	2.4    6      18
    	Processing: 9    24   	2.9   24      31
    	Waiting:    6    22     3.3   22      30
    	Total:     19    31     2.6   31      39

5. 请求时间的分布信息  
    
    	Percentage of the requests served within a certain time (ms)
    	  50% 31
    	  66% 32
    	  75% 32
    	  80% 33
    	  90% 34
    	  95% 35
    	  98% 36
    	  99% 37
    	 100% 39 (longest request)

	这段是每个请求处理时间的分布情况，以上表示50%的请求处理时间在31ms内，66%的请求处理时间在32ms内...，表示99%的请求处理时间在37ms内。