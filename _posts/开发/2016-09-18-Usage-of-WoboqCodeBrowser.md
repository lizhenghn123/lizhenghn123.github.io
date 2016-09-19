---
layout: post

title: 利用Woboq CodeBrowser工具在线浏览源代码.

category: 开发

tags: 开发 

keywords: 开发 Woboq CodeBrowser 在线浏览源代码

description: 利用Woboq CodeBrowser工具在线浏览源代码.。

---

## 1. 前言
浏览一个项目的源代码有很多种方式和工具，比如轻量级的Source Insight、Vim、Emacs、跨平台的Visual Studio Code，重量级的Netbeans、Eclipse、Clion、Visual Stduio IDE等等。但这些工具多多少少都有些不便，比如Source Insight不支持utf8、Vim配置太复杂、Clion/VS太庞大太占内存。

据说LLVM/CLang编译链对C++代码解析做的很好，加上开源工具[woboq_codebrowser](https://github.com/woboq/woboq_codebrowser)利用LLVM/CLang深度解析C++源码并据此建立索引，并生成html文件，这样就可以通过浏览器就行在线浏览，也可以拷贝到任何地方，浏览起来很简单，字体、格式、高亮、跳转都很不错。

下面就介绍如何生成源代码的html索引。

## 2. 前提准备

需要先行安装LLVM、CLang工具。我的虚拟机(Centos 6.4)已经安装过了：
	
	# clang -v
	clang version 3.7.0 (tags/RELEASE_370/final)
	Target: x86_64-unknown-linux-gnu
	Thread model: posix
	Found candidate GCC installation: /usr/lib/gcc/x86_64-redhat-linux/4.4.4
	Found candidate GCC installation: /usr/lib/gcc/x86_64-redhat-linux/4.4.7
	Found candidate GCC installation: /usr/local/bin/../lib/gcc/x86_64-unknown-linux-gnu/4.8.2
	Selected GCC installation: /usr/local/bin/../lib/gcc/x86_64-unknown-linux-gnu/4.8.2
	Candidate multilib: .;@m64
	Selected multilib: .;@m64
	# which clang
	/usr/local/bin/clang
	# ls /llvm-config  --version
	ls (GNU coreutils) 8.4
	Copyright (C) 2010 Free Software Foundation, Inc.
	许可证：GPLv3+：GNU 通用公共许可证第3 版或更新版本<http://gnu.org/licenses/gpl.html>。
	本软件是自由软件：您可以自由修改和重新发布它。
	在法律范围内没有其他保证。
	
	由Richard M. Stallman 和David MacKenzie 编写。
	# which llvm-config
	/usr/local/bin/llvm-config

另外还需要安装CMake工具，这里也不再介绍。

## 3. woboq_codebrowser
woboq codebrowser是一个C++写的命令行工具，它调用LLVM解析任何一个C++项目的所有源码，然后输出一组HTML文件以及对应的Javascript源码。随后我们可以把这组HTML文件拷贝到某个Web服务器上，就可以在浏览器里浏览C++项目的源码了。比如可以用鼠标点击任何一个symbol，即可跳转到symbol的声明或者定义所在的位置。

为了能解析源码，woboq codebrowser需要知道源码编译的步骤。这些步骤不仅列出了需要关注的源码文件，而且会真的被woboq codebrowser调用的LLVM/Clang执行，从而做宏替换（macro execution）之类的预编译工作，从而得到完备的源码。如果一个C++项目恰好是用CMake来组织的，那么恭喜你，只需要给cmake命令加一个参数，就可以得到这个“编译步骤”，并保存到一个叫compile_commands.json的文件里，方便woboq codebrowser读取。

编译：

	git clone https://github.com/woboq/woboq_codebrowser
	cd woboq_codebrowser
	cmake . -DLLVM_CONFIG_EXECUTABLE=/usr/local/bin/llvm-config -DCMAKE_BUILD_TYPE=Release
	make 

## 4. 编译自己的项目
我们这里以一个xml解析库[pugixml](https://github.com/zeux/pugixml)为例进行说明。注意这里有两点要求：

1. 使用CMake工具编译
2. 编译时加上-DCMAKE\_EXPORT_COMPILE\_COMMANDS=ON，这样在编译时cmake还会输出compile\_commands.json，供woboq codebrowser使用

编译如下：

	# git clone https://github.com/zeux/pugixml
	# cd pugixml
	# cmake . -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
	# make

## 使用woboq_codebrowser进行源代码解析

	# OUTPUTDIRECTORY=/var/www/html/pugixml
	# DATADIRECTORY=$OUTPUTDIRECTORY/../data
	# BUILDIRECTORY=$PWD
	# VERSION=`git describe --always --tags`
	# /root/temp/woboq_codebrowser/generator/codebrowser_generator -b $BUILDIRECTORY -a -o $OUTPUTDIRECTORY -p codebrowser:$BUILDIRECTORY:$VERSION
	# /root/temp/woboq_codebrowser/indexgenerator/codebrowser_indexgenerator $OUTPUTDIRECTORY
	# cp -rv /root/temp/woboq_codebrowser/data $DATADIRECTORY

说明： 

1. woboq_codebrowser在/root/temp目录下
2. /var/www/html/pugixml是Apache Httpd的工作目录，这里直接使用Apache Httpd作为web server

现在就可以通过浏览器进行访问、查看了：  

![](http://i.imgur.com/ykCac36.jpg)

## 参考
[https://zhuanlan.zhihu.com/p/22484207](https://zhuanlan.zhihu.com/p/22484207)