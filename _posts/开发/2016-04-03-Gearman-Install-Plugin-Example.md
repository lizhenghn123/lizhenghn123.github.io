---
layout: post

title: Gearman源码安装、使用和各语言的扩展安装

category: 分布式

tags: 开发 分布式 RPC Gearman

keywords: 开发 分布式 RPC 消息队列 Gearman

description: Gearman源码安装、使用和各语言的扩展安装。

---

Gearman官网：[http://gearman.org/](http://gearman.org/)， Gearman文档：[http://gearman.info/](http://gearman.info/)。

## 1. 编译安装Gearman

说明： Gearman的编译很麻烦，我第一次编译时前前后后花了一天多的时间才搞定。这玩意对用户真不友好！ 简直想放弃调研该产品了。

### 1.1 依赖项
- boost（>=1.39）  
    boost 这么大还是自行安装吧，这里不再介绍了。推荐[boost 1.59.0](http://www.boost.org/users/history/)。  
    这里主要依赖的是boost program_options库。  
    ./bjam stage --toolset=gcc --with-program_options  
    ./bjam install --with-program_options  
- uuid  
	yum install uuid libuuid uuid-devel libuuid-devel

- libevent2  
  官网[http://libevent.org](http://libevent.org/)。  
  ./configure –prefix=/usr/local/include  
  make && make isntall  
- e2fsprogs(可选)  
	wget http://downloads.sourceforge.net/e2fsprogs/e2fsprogs-1.41.14.tar.gz  
	tar xvzf  e2fsprogs-1.41.14.tar.gz  && cd e2fsprogs-1.41.14  
    ./configure --prefix=/usr/local/e2fsprogs  --enable-elf-shlibs  
    make && make install  
    cp -r lib/uuid/   /usr/include/   && cp -rf lib/libuuid.so*   /usr/lib
- mysql(可选)
- sqlite(可选)
- 其他
    yum install gperf mysql-devel -y  

我的系统环境：

    # uname -a
    Linux lzv8 2.6.32-358.el6.x86_64 #1 SMP Fri Feb 22 00:31:26 UTC 2013 x86_64 x86_64 x86_64 GNU/Linux
    # g++ -v
    使用内建 specs。
    COLLECT_GCC=g++
    COLLECT_LTO_WRAPPER=/usr/local/libexec/gcc/x86_64-unknown-linux-gnu/4.8.2/lto-wrapper
    目标：x86_64-unknown-linux-gnu
    配置为：../configure --enable-checking=release --enable-languages=c,c++ --disable-multilib
    线程模型：posix
    gcc 版本 4.8.2 (GCC) 
    # cat /etc/issue
    CentOS release 6.4 (Final)
    Kernel \r on an \m

### 1.2 编译Gearman

下载Gearman源代码，[gearman首页点此](https://launchpad.net/gearmand)，本次编译时下载的是[gearmand-1.1.12版本](https://launchpad.net/gearmand/1.2/1.1.12/+download/gearmand-1.1.12.tar.gz)。

	# wget https://launchpad.net/gearmand/1.2/1.1.12/+download/gearmand-1.1.12.tar.gz
	# tar -xf gearmand-1.1.12.tar.gz && cd gearmand-1.1.12

#### 部分编译参数说明
- boost路径设置

在源码目录下执行如下命令可查看可boost有关的编译参数(其他也类似)：

	#./configure --help | grep boost
	#--with-boost[=ARG]       use Boost library from a standard location
    --with-boost-libdir=LIB_DIR
	                          Force given directory for boost libraries. Note that fails and you know exactly where your boost
	--with-boost-program-options[=special-lib]
	                          use the program options library from boost - it is
	                          --with-boost-program-options=boost_program_options-gcc-mt-1_33_1

假设boost安装在/usr/local/include + /usr/local/lib 下， 那么：

	--with-boost=yes --with-boost-libdir=/usr/local/lib

- 是否需要启用持久化存储
  
Gearman支持持久化存储任务，持久化到数据库中，可选数据库是mysql或者sqlite。 使用方式如下：

	--with-mysql=no
	--with-sqltie=no
	--with-sqlite=/usr/local/sqlite3

开始编译（使用mysql和sqlite）：

	# ./configure --prefix=/usr/local/gearman  --with-mysql --with-sqlite3  --with-boost=yes
      --with-boost-libdir=/usr/local/lib --with-boost-program-options=boost_program_options
    # make
   
如果编译中报如下错误：

    bin/gearadmin.o: In function `boost::program_options::basic_command_line_parser<char>::run()':
    /usr/local/include/boost/program_options/detail/parsers.hpp:108: undefined reference to `boost::program_options::detail::cmdline::get_canonical_option_prefix()'
    bin/gearadmin.o: In function `main':
    /root/temp/gearmand-1.1.12/bin/gearadmin.cc:129: undefined reference to `boost::program_options::options_description::options_description(std::string const&, unsigned int, unsigned int)'
    collect2: error: ld returned 1 exit status
    
这表示boost_program_options库没有找到，虽然之前已经设置过！所以修改Makefile文件的2723、2736、2747、2769行分别增加boost库的安装目录，比如-L/usr/local/lib， 我的设置如下（我的boost安装在/usr/local/lib）：

    line2723：benchmark_blobslap_worker_LDADD = -L/usr/local/lib -lboost_program_options \
    line2736：bin_gearadmin_LDADD = -L/usr/local/lib -lboost_program_options $(am__append_11) \
    line2747：EXAMPLES_LDADD = -L/usr/local/lib -lboost_program_options libgearman/libgearman.la
    line2769：gearmand_gearmand_LDFLAGS = -L/usr/local/lib -lboost_program_options

顺利的话到此处就编译成功了，然后安装，我的安装位置在/usr/local/gearmand:

    # make && make install
    # /usr/local/gearman/sbin/gearmand -V
    gearmand 1.1.12 - https://bugs.launchpad.net/gearmand

如上则表示已将Gearman安装到系统中了。

### 1.3 yum安装gearman

    #rpm -ivh http://dl.iuscommunity.org/pub/ius/stable/Redhat/6/x86_64/epel-release-6-5.noarch.rpm
    #yum install -y gearmand
	#service gearmand start

## 2. 启动和测试Gearman

### 2.1 启动Gearman
如果编译&安装成功，此时就可以使用Gearman了。 简单的启动方式如下：

直接启动：

	# /usr/local/gearman/sbin/gearmand -p 4730 -L 127.0.0.1 --log-file=/tmp/gearmand-4730.log --pid-file=/tmp/gearmand-4730.pid -d

使用mysql进行队列持久化保存：

    # /usr/local/gearman/sbin/gearmand -p 4730 -L 127.0.0.1 --log-file=/tmp/gearmand-4730.log --pid-file=/tmp/gearmand-4730.pid -q MySQL --mysql-host=localhost --mysql-user=root --mysql-db=gearman --verbose DEBUG  -d

注意，此时可能会发生错误，请根据当前提示信息或者/tmp/gearmand-4730.log中的详细错误信息排查问题。比如我启动时遇到以下两个错误：
	
查看/tmp/gearmand-4730.log， 有如下提示信息：

    ERROR 2016-01-12 09:48:44.237336 [  main ] Failed to connect to database: Can't connect to local MySQL server through socket '/var/lib/mysql/mysql.sock' (2) -> libgearman-server/plugins/queue/mysql/queue.cc:228

检查mysql是否启动， service mysqld status； service mysqld start。

再次启动时，仍有问题，查看/tmp/gearmand-4730.log， 有如下提示信息：

    ERROR 2016-01-12 09:52:38.422744 [  main ] Failed to connect to database: Unknown database 'gearman' -> libgearman-server/plugins/queue/mysql/queue.cc:228
原来是在启动前gearman数据库需要自己提前在mysql中自行创建。手动创建数据库gearman之后，再次启动就OK了。

如果启动成功则没有任何提示信息，使用ps查询是否启动：

	# ps -ef | grep gearman
	root     18439     1  0 15:23 ?        00:00:00 /usr/local/gearman/sbin/gearmand -p 4730 -L 127.0.0.1 --log-file=/tmp/gearmand-4730.log --pid-file=/tmp/gearmand-4730.pid -d
	# netstat -atlunp | grep 4730
	tcp        0      0 127.0.0.1:4730              0.0.0.0:*                   LISTEN      18439/gearmand  

如上表示gearmand已启动成功，且监听在4730端口上。

此时Gearman会在mysql的gearman数据库中新创建了一个数据表：gearman_queue。 在mysql里查看该表信息如下：

	show create table gearman_queue;
	
	| Table         | Create Table   
	| gearman_queue | CREATE TABLE `gearman_queue` (
	  `unique_key` varchar(64) DEFAULT NULL,
	  `function_name` varchar(255) DEFAULT NULL,
	  `priority` int(11) DEFAULT NULL,
	  `data` longblob,
	  `when_to_run` int(11) DEFAULT NULL,
	  UNIQUE KEY `unique_key` (`unique_key`,`function_name`)
	) ENGINE=MyISAM DEFAULT CHARSET=latin1 |


### 2.2 简单测试Gearman
创建一个后台job，参数格式：gearman -f 函数名 -b(后台) user-data(数据)：

    # gearman -f echo -b  hello 
执行队列中的job：

    # gearman -f echo -w  
    hello

注意: 如果开启了持久化保存，那么该任务创建后会在数据库表中产生一条记录，且该任务被执行后，数据表里该条记录会被删除：
    
    # gearman -f echo -b  1+2 
    mysql> select * from gearman_queue;
    +--------------------------------------+---------------+----------+------+-------------+
    | unique_key                           | function_name | priority | data | when_to_run |
    +--------------------------------------+---------------+----------+------+-------------+
    | 9c330ff0-b912-11e5-9ab8-0800278eb831 | echo          |        1 | 1+2  |           0 |
    +--------------------------------------+---------------+----------+------+-------------+
    1 row in set (0.00 sec)
    
    # gearman -f echo -w     
    1+2
    mysql> select * from gearman_queue;
    Empty set (0.00 sec)

## 3. 安装Gearman的Apache/Ngnix模块扩展
安装一个Apache的Gearman扩展模块，就可以通过浏览器查看Gearman的状态信息。
这里安装的扩展是[mod_gearman_status](https://github.com/amir/mod_gearman_status)。
安装方法如下(可查看原[Readme](https://github.com/amir/mod_gearman_status))：

    # git clone https://github.com/amir/mod_gearman_status && cd mod_gearman_status
    # apxs -c -i mod_gearman_status.c
    # vim /etc/httpd/conf/httpd.conf  # 增加以下内容
        LoadModule gearman_status_module modules/mod_gearman_status.so
        <Location /gearman-status>
            SetHandler gearman_status
        </Location>
    # service httpd restart   # 重启apache
    # lynx -mime_header http://localhost/gearman-status   # 测试，查看是否生效
至此就安装完成了。说明：安装过程中使用了apache模块扩展工具apxs，如果你本机没有，可以通过命令"yum install httpd-devel"安装，或者查看[此文章介绍](http://lihuan.blog.51cto.com/4391550/821448)。

通过浏览器访问效果如下：

![gearman_apache_mod](http://i.imgur.com/kkLcXuX.png)

如果是安装Ngnix的gearman扩展，可以下载该模块[ngx_http_gearman_status_module](https://github.com/amir/ngx_http_gearman_status_module)， 安装也很简单，这里不再介绍。

## 4. 安装Gearman的各语言扩展
### 4.1 c-gearman
因为Gearman本身就是C/C++编写的，如果源码编译，那么相应的C头文件和libgearman.so库也会编译在系统中。比如/usr/local/gearman/include和/usr/local/gearman/lib目录。
因此如果使用C或C++语音编写worker、client实例，可引用相应的头文件和库文件。

### 4.2 python-gearman
gearman的python模块，地址为：https://pypi.python.org/pypi/gearman/2.0.2 
我们可以用以下命令安装（两个命令均可，二选一）：

    easy_install gearman
    pip install gearman
或者通过源码安装：

    wget https://pypi.python.org/packages/source/g/gearman/gearman-2.0.2.tar.gz --no-check-certificate
    tar zxvf gearman-2.0.2.tar.gz 
    cd gearman-2.0.2 
    python setup.py install
这样，我们就完成了python-gearman的安装。

使用python的gearman模块进行测试（gearman仍是之前启动的），这里只需要写worker和client即可。
echo_worker.py 内容如下：
    
    #!/usr/bin/env python2.6
    # coding=utf-8
    import os
    import gearman
    import math
    
    class MyGearmanWorker(gearman.GearmanWorker):
        def on_job_execute(self, current_job):
            print "Job started"
            print "===================\n"
            return super(MyGearmanWorker, self).on_job_execute(current_job)
    
    def task_callback(gearman_worker, gearman_job):
        print gearman_job.data
        print "-----------\n"
        return gearman_job.data
    
    my_worker = MyGearmanWorker(['127.0.0.1:4730'])
    my_worker.register_task("echo", task_callback)
    my_worker.work()

echo_client.py 内容如下：
    
    #!/usr/bin/env python2.6
    # coding=utf-8
    from gearman import GearmanClient
    
    gearman_client = GearmanClient(['127.0.0.1:4730'])
    gearman_request = gearman_client.submit_job('echo', 'test gearman')
    result_data = gearman_request.result
    print result_data

然后分别运行以下命令，以注册一个worker实例和client发起任务:

    python echo_worker.py
    python echo_client.py
    
### 4.3 php-gearman
安装php扩展前，首先确认系统中是否安装了phpize工具，如果没有，执行： yum install php-devel即可。

    # wget http://pecl.php.net/get/gearman-1.1.2.tgz 
    # tar -xf gearman-1.1.2.tgz   &&  cd gearman-1.1.2
    # /usr/bin/phpize           ## 自行确认你的phpiz安装在哪个目录
    # ./configure --with-php-config=/usr/bin/php-config --with-gearman=/usr/local/gearman # 自行确认php-config和gearman的安装目录
    # make && make install
编译成功后，会在/usr/lib64/php/modules目录下生成gearman.so文件。
     
编辑php.ini文件（我的位于/etc/php.ini），增加以下内容：
extension=/usr/lib64/php/modules/gearman.so

查看gearman.so模块是否加载：

    # php --info | grep gearman
    gearman
    gearman support => enabled
    libgearman version => 1.1.12
    # php -m | grep gearman
    gearman
至此php-gearman的扩展已经安装完成了。

使用php的gearman模块进行测试（gearman仍是之前启动的），这里只需要写worker和client即可。
echo_worker.php 内容如下：

    <?php
        $worker= new GearmanWorker();
        $worker->addServer('127.0.0.1', 4730);
        $worker->addFunction('echo', 'echo_reverse_function');
        
        while ($worker->work());
        
        
        function echo_reverse_function($job)
        {
            return strrev($job->workload());    // 反转接收到的字符串后再返回
        }
    ?>
echo_client.php 内容如下：

    <?php
        $client= new GearmanClient();
        $client->addServer('127.0.0.1', 4730);
        echo $client->do('echo', 'Hello World!'), "\n";
    ?>
    
然后分别运行以下命令，以注册一个worker实例和client发起任务:

    php echo_worker.php
    php echo_client.php

### 4.4 perl-gearman
我不用perl，也就没有安装perl的对应模块。如果需要，可以参考[官方文档](http://gearman.org/download/)。这里也摘录原文如下：
There are three Perl client implementations, two of which are Pure Perl and one which is a wrapper around the libgearman C library.

- Gearman::XS
A Perl module that wraps the libgearman C library. On CPAN under [Gearman::XS](http://search.cpan.org/dist/Gearman-XS/).
    - [Gearman::XS (0.12)](http://launchpad.net/gearmanxs/trunk/0.12/+download/Gearman-XS-0.12.tar.gz)
- Gearman::Client & ::Worker
This pure Perl API can be found in CPAN under Gearman::Client and Gearman::Worker.
    - [Perl modules on CPAN](http://search.cpan.org/dist/Gearman/)
- AnyEvent::Gearman::Client & ::Worker
This pure Perl API can be found in CPAN under [AnyEvent::Gearman::Client](http://search.cpan.org/dist/AnyEvent-Gearman-Client) and [AnyEvent::Gearman::Worker](http://search.cpan.org/dist/AnyEvent-Gearman-Worker).
A simpler API can be found under [AnyEvent::Gearman](http://search.cpan.org/dist/AnyEvent-Gearman).
This module uses the [AnyEvent](http://search.cpan.org/dist/AnyEvent) framework and provides a event-driven asynchronous client and worker.

### 4.5 其他语言的gearman模块
 如果需要安装java、go等语言的gearman模块，请参考[官方文档](http://gearman.org/download/)。因为暂时用不到，这里不再介绍。
 
## 5. Reference
- [Libgearman C语言在线API](http://gearman.info/libgearman/index.html)
- [gearman的安装启动以及python API入门例子](http://yunjianfei.iteye.com/blog/2076658)
- [gearman队列持久化带来的问题](http://yunjianfei.iteye.com/blog/2061772)
