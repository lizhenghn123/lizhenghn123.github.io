---
layout: post

title: Linux下PHP安装Redis扩展和mongodb扩展

category: 开发

tags: Linux Redis 数据库 

keywords: Linux Redis MongoDB 数据库 

description: 本文介绍如何在linux下安装redis及MongoDB的php扩展。

---

本文介绍如何在linux下安装redis及MongoDB的php扩展。

##1. Linux下PHP安装Redis扩展

###1.1  前提准备  
- php redis 下载地址[在此](http://pecl.php.net/package/redis)  
- phpize工具
###1.2  安装步骤  

wget、phpize、make、make install：

	# wget http://pecl.php.net/get/redis-2.2.7.tgz
	# tar -xf redis-2.2.7.tgz && cd redis-2.2.7
	# locate phpize
	/usr/bin/phpize
	# /usr/bin/phpize 
	# locate php-config
	/usr/bin/php-config
	# ./configure --with-php-config=/usr/bin/php-config
	# make && make install

顺利的话就将编译后的redis.so安装到php的modules目录下了，比如我的目录是/usr/lib64/php/modules。

###1.3 配置php.ini，增加以下内容  
	
	extension=redis.so
然后重启apache或者ngnix即可。

###1.4  测试是否安装成功
增加一个phpinfo.php页面，添加以下内容：

	<?php	
	phpinfo();	
	?>
访问该页面，如果出现以下内容表明安装成功：

![php_redis](http://i.imgur.com/fG2LK3G.png)

增加一个phpredis.php页面，添加以下内容

###1.5 通过程序连接Redis
增加一个test_redis.php， 代码如下：

	<?php
	    //连接本地的 Redis 服务
	   $redis = new Redis();
	   $redis->connect('127.0.0.1', 6379);
	
	   echo "Connection to server sucessfully!\r\n";
	         //查看服务是否运行
	   echo "Server is running: " . $redis->ping()."\r\n";
	
	   //设置 redis 字符串数据
	   $redis->set("tutorial-name", "Redis tutorial");
	   // 获取存储的数据并输出
	   echo "Stored string in redis:: " . $redis->get("tutorial-name")."\r\n";
	
	   //存储数据到列表中
	   $redis->lpush("tutorial-list", "Redis");
	   $redis->lpush("tutorial-list", "Mongodb");
	   $redis->lpush("tutorial-list", "Mysql");
	   // 获取存储的数据并输出
	   $arList = $redis->lrange("tutorial-list", 0 ,5);
	   echo "Stored string in redis:: ";
	   print_r($arList);
	?>

通过网页访问上面的php页面，或者直接运行（首先运行redis-server）：
	
	#php /var/www/html/test_redis.php
	Connection to server sucessfully!
	Server is running: +PONG
	Stored string in redis:: Redis tutorial
	Stored string in redis:: Array
	(
	    [0] => Mysql
	    [1] => Mongodb
	    [2] => Redis
	)
如果有以上输出，说明安装完全成功。 更多通过PHP操作Redis的接口请看参考文档：[PHP-redis中文文档](http://www.cnblogs.com/weafer/archive/2011/09/21/2184059.html)。

##2. Linux下PHP安装MongoDB扩展

###2.1  前提准备  
- php mongodb 下载地址[在此](http://pecl.php.net/package/mongo)  
- phpize工具
###2.2  安装步骤  

wget、phpize、make、make install：

	# wget http://pecl.php.net/get/mongo-1.6.12.tgz
	# tar -xf mongo-1.6.12.tgz && cd mongo-1.6.12
	# /usr/bin/phpize 
	# ./configure --with-php-config=/usr/bin/php-config
	# make && make install

顺利的话就将编译后的mongo.so安装到php的modules目录下了，比如我的目录是/usr/lib64/php/modules。

###2.3 配置php.ini，增加以下内容  
	
	extension=mongo.so
然后重启apache或者ngnix即可。

###2.4 测试是否安装成功
增加一个phpinfo.php页面，添加以下内容：

	<?php	
	phpinfo();	
	?>
访问该页面，如果出现以下内容表明安装成功：

![php_mongodb](http://i.imgur.com/7TRT2hj.png)

##3. Redference  
[PHP-redis中文文档](http://www.cnblogs.com/weafer/archive/2011/09/21/2184059.html)  