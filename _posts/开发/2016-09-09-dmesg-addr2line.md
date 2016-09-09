---
layout: post

title: 使用dmesg和addr2line查找程序崩溃后的现场报告

category: 开发

tags: 开发 

keywords: 开发 dmesg addr2line

description: 使用dmesg和addr2line查找程序崩溃后的现场报告。

---

dmesg命令用会把开机信息存到ring bufer中， 形成一个缓冲， 免得用户来不及看。 在root权限下， 可以用dmesg -c来清除这个消息。 不带参数执行dmesg命令则是用来输出这些记录信息的。

dmesg有什么用呢？
服务器上由于怕软件bug以及磁盘的限制,一般会将core文件关掉。可以通过以下命令查看当前core file size设置：

	ulimit -a

而并不是所有的的程序在core dump之后都会产生core文件，这样在程序有bug崩溃以后，就可以通过dmesg查看一些关键信息。典型信息如下:

	a.out[2956]: segfault at 0 ip 0000000000400600 sp 00007fff2b646530 error 4 in a.out[400000+1000]

解释： 

 - at后面地址:访问越界的地址
 - rip:指令地址
 - rsp:栈地址
 - error:错误类型  
	error number是由三个字位组成的，从高到底分别为bit2 bit1和bit0,所以它的取值范围是0~7.  
	bit2: 值为1表示是用户态程序内存访问越界，值为0表示是内核态程序内存访问越界  
	bit1: 值为1表示是写操作导致内存访问越界，值为0表示是读操作导致内存访问越界  
	bit0: 值为1表示没有足够的权限访问非法地址的内容，值为0表示访问的非法地址根本没有对应的页面，也就是无效地址  

此时， 我们的重要目的是： 获取出错堆栈的地址， 而dmesg恰好可以目的。  

下面， 我们来看一下经典的dmesg + addr2line组合操作：

	$ cat 1.cpp
	
	#include<stdio.h>
	
	void print(int* p)
	{
	    printf("%d\n", *p);
	}
	
	int main()
	{
	    int *p = NULL;
	    //*p = 0;
	
	    print(p);
	    return 0;
	}
	 
	$ g++ -g 1.cpp -o a.out   # 带-g进行编译
	$ ./a.out 
	3433 segmentation fault (core dumped)  ./a.out
	$ dmesg
	a.out[3433]: segfault at 0 ip 0000000000400600 sp 00007fff24b40260 error 4 in a.out[400000+1000]
	$ addr2line -e ./a.out 0000000000400600 -f
	_Z5printPi     # 当前被调用的函数
	??:0           # 当前代码行数（我一直打印不出来，还不知道怎么搞）
	$ c++filt _Z5printPi
	print(int*)    # 解析出呗调用函数的原型
	$ objdump -d ./a.out | grep 400600 # 查找对应的汇编代码，会发现此地址对应在_Z5printPi函数中
	400600:	8b 00                	mov    (%rax),%eax
	


当然core文件能更好的帮助解决问题，最好还是在程序里用setrlimit来设置core文件，然后根据命令行参数及是否已经生成了core文件等逻辑来判断是否生成core文件。