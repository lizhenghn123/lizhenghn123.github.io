---
layout: post

title: Thrift在Windows及Linux平台下的安装和使用示例

category: 开发

tags: 开发 Thrift RPC C++

keywords: 开发 Thrift RPC C++

description: 本文介绍了RPC框架Thrift在Windows及Linux平台下的安装，以及实现了一个简单的demo演示Thrift的使用方法。

---

## thrift介绍
Apache Thrift 是 Facebook 实现的一种高效的、支持多种编程语言的RPC(远程服务调用)框架。

本文主要目的是分别介绍在Windows及Linux平台下的Thrift安装步骤，以及实现一个简单的demo演示Thrift的使用方法。更多Thrift原理留在以后再行介绍。
## thrift安装

源码下载：[thrift官网](https://thrift.apache.org/)，或者[thrift-github地址](https://github.com/apache/thrift/releases)，我下载的是[thrift-0.9.3.tar.gz](https://github.com/apache/thrift/archive/0.9.3.tar.gz)。

### 安装依赖库

1. boost  
boost的编译就不再这里介绍了，我分别使用了boost1.55或boost1.49编译通过；
2. libevent  
按需编译，如果不需要异步server就可以不编译libevent，否则可以点此下载libevent-2.0.21-stable；
3. openssl  
下载针对你系统版本的openssl库，windows下有编译好的二进制文件，可以直接下载，[32位/62位系统openssl](http://www.heise.de/download/win32-openssl-8bf9143dad303712e33d77d8fb17c374-1457185005-2647316.html)； Linux发行版一般都自带ssl库；

### thrift在Windows下的安装
我是在Windows7 64bit， VS2010编译的。 Windows下编译倒也不麻烦，简单介绍如下：

1. 解压缩源代码，进入到lib\cpp目录下，打开Thrift.sln，里面有libthrift和libthriftnb两个工程，其中libthrift工程是常规的阻塞型server端（单线程server，一个连接一个线程server，线程池server），libthriftnb工程是非阻塞（non-blocking）模式的服务server端，也只有编译libthriftnb时才需要依赖libevent库，否则可以不编译libevent库；
2. 设置依赖库头文件和库文件，这就不再介绍了；	
3. 编译，顺利的话就OK了，会在lib\cpp\Debug目录下生成libthrift.lib和libthriftnb.lib（如果编译的话）；

说明： thrift-0.9.3这一版的release其实在windows下是编译不过的，因为vs工程中要编译的Thrift.cpp已经不存在了，从工程中移除就可以顺利编译了，参考[thrift-pull-739](https://github.com/apache/thrift/pull/739)。

另外还可以自行编译thrift文件的生成工具，当然也可以直接从[官网下载](http://www.apache.org/dyn/closer.cgi?path=/thrift/0.9.1/thrift-0.9.3.exe)，这里给出编译步骤：  

1. 将compiler\cpp\src\windows\version.h.in文件拷贝到compiler\cpp\src\目录下，并重命名为version.h；
2. 到compiler\cpp目录下，打开compiler.sln，编译即可

### thrift在linux(Centos)下的安装
我是在Centos6.4 64bit，g++ 4.4.7编译的，编译很简单，分别可以使用cmake或者make工具进行编译，这里不再多做介绍，当然，编译过程中缺少了某些库什么的，就先按照即可，更详细的步骤请看本文的参考文章链接。

## 开发步骤
1. 写一个.thrift文件，也就是IDL（Interface Description File，接口描述文件）；
2. 用Thrift的IDL生成工具（windows下就是上面提供下载链接的[thrift-0.9.1.exe](http://www.apache.org/dyn/closer.cgi?path=/thrift/0.9.1/thrift-0.9.3.exe)， Linux下就是/usr/local/bin/thrift程序） ，然后根据需要生成目标语言代码；
3. server端程序引入第2步生成的代码，实现RPC业务代码；
4. client端程序引入第2步生成的代码，实现RPC调用逻辑；
5. 用第4步生成的程序就可以调用第3步实现的远程服务了；

## 入门示例
下面就演示一个简单的server端和client端程序。

### 设计thrift文件（IDL） 
假设实现这么一个简单服务，client通过hello接口发送自己的名字，且需要server端回复，比如 hello.thrift:
	
	service HelloService
	{
	    void hello(1: string name);
	}

### 通过IDL工具生成源代码
执行thirift命令生成源文件：

	thrift --gen cpp hello.thrift   			  # centos下
	thrift-0.9.3.exe --gen cpp hello.thrift   # Windows下
以上命令表示生成C++语言的源代码，然后会生成一个gen-cpp目录，里面包含自动生成的几个源代码文件：
	
	hello_constants.cpp
	hello_constants.h
    HelloService.cpp
    HelloService.h
    HelloService_server.skeleton.cpp
    hello_types.cpp
    hello_types.h

### 实现server端程序
HelloService_server.skeleton.cpp就是默认的server端程序入口，可以直接修改该文件，或者拷贝一份再做修改（我是拷贝并重命名为server.cpp），以便增加自己的逻辑处理：

	class HelloServiceHandler : virtual public HelloServiceIf {
	 public:
	  HelloServiceHandler() {
	    // Your initialization goes here
	  }
	
	  void hello(const std::string& name) {
	    // Your implementation goes here
		// 这里只简单打印出client传入的名称
	    printf("hello, I got your name %s\n", name.c_str());
	  }	
	};

如果是在linux平台下，直接通过g++编译：

	g++ -o server hello_constants.cpp  HelloService.cpp hello_types.cpp  server.cpp -I/usr/local/include/thrift -L/usr/local/lib -lthrift

如果是在Windows平台下，通过vs2010新建win32控制台工程，将gen-cpp目录下的所有文件复制到新工程下，设置头文件包含和lib库目录。 比如设置libthrift.lib的头文件目录为thrift-0.9.3\lib\cpp\src\thrift，lib库目录为thrift-0.9.3\lib\cpp\Debug。

### 实现client端程序
因为没有默认的client实现，所以需要新建一个client.cpp文件，自己增加实现：
	
	#include <stdio.h>
	#include <string>
	#include "transport/TSocket.h"
	#include "protocol/TBinaryProtocol.h"
	#include "server/TSimpleServer.h"
	#include "transport/TServerSocket.h"
	#include "transport/TBufferTransports.h"
	#include "hello_types.h"
	#include "HelloService.h"
	using namespace ::apache::thrift;
	using namespace ::apache::thrift::protocol;
	using namespace ::apache::thrift::transport;
	using namespace ::apache::thrift::server;
	using boost::shared_ptr;
	
	int main(int argc, char** argv)
	{
	    shared_ptr<TTransport> socket(new TSocket("localhost", 9090));
	    shared_ptr<TTransport> transport(new TBufferedTransport(socket));
	    shared_ptr<TProtocol> protocol(new TBinaryProtocol(transport));
	    HelloServiceClient client(protocol);
		try
		{
			transport->open();
	        client.hello("cpper.info");
			transport->close();
		}
		catch(TException& tx)
		{
			printf("ERROR:%s\n",tx.what());
		}
	}

如果是在linux平台下，直接通过g++编译：

	g++ -o client client.cpp hello_constants.cpp  HelloService.cpp hello_types.cpp -I/usr/local/include/thrift -L/usr/local/lib -lthrift

如果是在Windows平台下，通过vs2010新建win32控制台工程，将gen-cpp目录下的所有文件（除HelloService_server.skeleton.cpp之外）复制到新工程下，并增加上面手动实现的client.cpp。

通过以上步骤，就实现一个简单的RPC server和client程序了，可以分别运行进行测试看看效果怎么样。

## Reference
[Thrift官方安装手册（译）](http://blog.csdn.net/qq910894904/article/details/41132779)