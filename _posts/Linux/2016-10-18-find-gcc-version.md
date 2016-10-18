---
layout: post

title: 如何查看程序是用什么GCC版本编译的

category: Linux

tags: Linux 

keywords: GCC G++ 编译版本

description: 如何查看程序是用什么GCC版本编译的。

---

对于我们使用的每一个程序(Linux下)，包括Linux系统本身，我们想知道该程序是在什么编译器及编译器版本下编译的，那么该如何做呢？

对于Linux内核本身使用什么编译器编译的，其实很好查看：
	
	$ cat /proc/version
	Linux version 2.6.32-358.el6.x86_64 (mockbuild@c6b8.bsys.dev.centos.org) (gcc version 4.4.7 20120313 (Red Hat 4.4.7-3) (GCC) ) #1 SMP Fri Feb 22 00:31:26 UTC 2013

如上显示，说明使用GCC 4.4.7版本编译的。

那么对于某一个程序或者so来说，应该怎么查看？这里我写一个小程序并分别用不同的编译器编译来验证。

测试程序test.cpp:
	
	#include <iostream>
	using namespace std;
	
	int main()
	{
	    cout << "Hello, World!\n";
	}

我本机装了3个编译器，这里分别进行编译：

	$ /usr/bin/g++  test.cpp -o t447
	$ /usr/local/bin/g++ test.cpp -o t482
	$ /usr/local/bin/clang++ test.cpp -o tclang

通过readelf命令查看：
	
	$ readelf -p .comment t447	
	String dump of section '.comment':
	  [     0]  GCC: (GNU) 4.4.7 20120313 (Red Hat 4.4.7-17)
	  [    2d]  GCC: (GNU) 4.4.7 20120313 (Red Hat 4.4.7-16)
	  
	$ readelf -p .comment t482	
	String dump of section '.comment':
	  [     0]  GCC: (GNU) 4.4.7 20120313 (Red Hat 4.4.7-17)
	  [    2d]  GCC: (GNU) 4.8.2
	  
	$ readelf -p .comment tclang	
	String dump of section '.comment':
	  [     0]  GCC: (GNU) 4.4.7 20120313 (Red Hat 4.4.7-17)
	  [    2d]  GCC: (GNU) 4.8.2
	  [    3e]  clang version 3.7.0 (tags/RELEASE_370/final)

或者通过objdump命令查看：
	
	$ objdump -s --section .comment ./t447
	
	./t447:     file format elf64-x86-64
	
	Contents of section .comment:
	 0000 4743433a 2028474e 55292034 2e342e37  GCC: (GNU) 4.4.7
	 0010 20323031 32303331 33202852 65642048   20120313 (Red H
	 0020 61742034 2e342e37 2d313729 00474343  at 4.4.7-17).GCC
	 0030 3a202847 4e552920 342e342e 37203230  : (GNU) 4.4.7 20
	 0040 31323033 31332028 52656420 48617420  120313 (Red Hat
	 0050 342e342e 372d3136 2900               4.4.7-16).

	$ objdump -s --section .comment ./t482
	
	./t482:     file format elf64-x86-64
	
	Contents of section .comment:
	 0000 4743433a 2028474e 55292034 2e342e37  GCC: (GNU) 4.4.7
	 0010 20323031 32303331 33202852 65642048   20120313 (Red H
	 0020 61742034 2e342e37 2d313729 00474343  at 4.4.7-17).GCC
	 0030 3a202847 4e552920 342e382e 3200      : (GNU) 4.8.2.
	 
	$ objdump -s --section .comment ./tclang
	
	./tclang:     file format elf64-x86-64
	
	Contents of section .comment:
	 0000 4743433a 2028474e 55292034 2e342e37  GCC: (GNU) 4.4.7
	 0010 20323031 32303331 33202852 65642048   20120313 (Red H
	 0020 61742034 2e342e37 2d313729 00474343  at 4.4.7-17).GCC
	 0030 3a202847 4e552920 342e382e 3200636c  : (GNU) 4.8.2.cl
	 0040 616e6720 76657273 696f6e20 332e372e  ang version 3.7.
	 0050 30202874 6167732f 52454c45 4153455f  0 (tags/RELEASE_
	 0060 3337302f 66696e61 6c2900             370/final).

通过以上两个命令就可以查看该程序编译时是使用的什么编译器。

是的，我本机装了三个编译器环境，分别如下：
	
	$ /usr/bin/g++ -v
	使用内建 specs。
	目标：x86_64-redhat-linux
	配置为：../configure --prefix=/usr --mandir=/usr/share/man --infodir=/usr/share/info --with-bugurl=http://bugzilla.redhat.com/bugzilla --enable-bootstrap --enable-shared --enable-threads=posix --enable-checking=release --with-system-zlib --enable-__cxa_atexit --disable-libunwind-exceptions --enable-gnu-unique-object --enable-languages=c,c++,objc,obj-c++,java,fortran,ada --enable-java-awt=gtk --disable-dssi --with-java-home=/usr/lib/jvm/java-1.5.0-gcj-1.5.0.0/jre --enable-libgcj-multifile --enable-java-maintainer-mode --with-ecj-jar=/usr/share/java/eclipse-ecj.jar --disable-libjava-multilib --with-ppl --with-cloog --with-tune=generic --with-arch_32=i686 --build=x86_64-redhat-linux
	线程模型：posix
	gcc 版本 4.4.7 20120313 (Red Hat 4.4.7-16) (GCC)

	$ /usr/local/bin/g++ -v
	使用内建 specs。
	COLLECT_GCC=/usr/local/bin/g++
	COLLECT_LTO_WRAPPER=/usr/local/libexec/gcc/x86_64-unknown-linux-gnu/4.8.2/lto-wrapper
	目标：x86_64-unknown-linux-gnu
	配置为：../configure --enable-checking=release --enable-languages=c,c++ --disable-multilib
	线程模型：posix
	gcc 版本 4.8.2 (GCC)

	$ /usr/local/bin/clang++ -v
	clang version 3.7.0 (tags/RELEASE_370/final)
	Target: x86_64-unknown-linux-gnu
	Thread model: posix
	Found candidate GCC installation: /usr/lib/gcc/x86_64-redhat-linux/4.4.4
	Found candidate GCC installation: /usr/lib/gcc/x86_64-redhat-linux/4.4.7
	Found candidate GCC installation: /usr/local/bin/../lib/gcc/x86_64-unknown-linux-gnu/4.8.2
	Selected GCC installation: /usr/local/bin/../lib/gcc/x86_64-unknown-linux-gnu/4.8.2
	Candidate multilib: .;@m64
	Selected multilib: .;@m64
