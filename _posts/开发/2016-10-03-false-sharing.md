---
layout: post

title: false-sharing问题及解决思路

category: 开发

tags: 开发 性能

keywords: 开发 性能 false-sharing cache-line

description: false-sharing现象及解决思路

---
## 1. 实例分析
假设有如下代码：
	
	// t0.cpp
	#include <iostream>
	#include <thread>
	
	int32_t global[2] = {0};
	
	void foo()
	{
	    for(int i = 0; i < 100000000; i++)
	    {
	        ++global[0];
	    }
	}
	
	void bar()
	{
	    for(int i = 0; i < 100000000; i++)
	    {
	        ++global[1];
	    }
	}
	
	int main()
	{
	    std::thread thread1(foo);
	    std::thread thread2(bar);
	    thread1.join();
	    thread2.join();
	    return 0;
	}

上面代码目标是开启两个线程分别对全局变量global[0]、global[1]进行累加。

编译并运行：
	
	# g++ -o t0 t0.cpp -std=c++0x -pthread
	# time ./t0
	./t0  1.33s user 0.00s system 196% cpu 0.677 total

**但上面的程序其实是有优化空间的，哪怕已经这么简单。**

## 2. false sharing

false sharing就是缓存行上的伪共享现象，因此也叫伪共享。

在对称多处理器（SMP）系统中，每一个CPU核心都会有自己的缓存空间，缓存空间是以缓存行（cache line）为单位存储的。缓存行是2的整数幂个连续字节，一般为32-256个字节。最常见的缓存行大小是64个字节。**当一个处理器改变了属于它自己缓存中的一个值，其它处理器就再也无法使用它自己原来的值，因为其对应的内存位置将被刷新(invalidate)到所有缓存。而且由于缓存操作是以缓存行而不是字节为粒度，所有缓存中整个缓存行将被刷新！**

伪共享是多核系统中一个著名的性能问题，伪共享发生的根本原因在于不同处理器上的线程修改了位于同一个cache line上的数据，如下图所示：  

![](http://i.imgur.com/0bHDNBy.jpg)  

如图所示，当多线程修改互相独立的变量时，但这些变量共享同一个缓存行，此时如果一个核心修改了该变量，该修改需要同步到其它核心的缓存，这会导致cache line失效并强制刷新，因此导致性能急剧下降，所以也有人将伪共享描述成多线程编程中无声的性能杀手，因为从代码或逻辑上很难看清楚是否会出现伪共享。

## 3. 如何查看cache line的大小
在linux系统下，可以有以下方法：

	#cat /sys/devices/system/cpu/cpu0/cache/index0/coherency_line_size
	64
	#cat /proc/cpuinfo  | grep cache_alignment | uniq
	cache_alignment	: 64

或者通过代码读取：
	
	FILE* file = fopen("/sys/devices/system/cpu/cpu0/cache/index0/coherency_line_size", "r");
	unsigned int cache_line = 0;
	if(file)
	{
		size_t n = fscanf(file, "%u", &cache_line);
		assert(n == 1);
	}

单位是字节。

## 4. 如何避免false sharing

避免伪共享的主要方法是代码审查和性能profile。比如多线程访问全局变量或者动态分配的共享数据结构是伪共享的潜在来源。而线程局部存储或者局部变量不会是伪共享的来源。

所以，如果发现了存在伪共享现象，解决办法一般比较简单：

- 使用编译指示，来强制使每一个变量对齐

		int32_t global[2] __attribute__((align(64)));

- 当使用数组或复杂数据结构时，可以在cache line尾部填充padding来保证数据元素分布在不同的cache line上。
	
		struct apple{
			int a;
			int b;
			int padding[14];   // sizeof(a) + sizeof(b) + sizeof(padding) == 64
		};
	或者：

		struct apple
		{
			int a;
			int b;
		}__attribute__((aligned (CACHELINE_SIZE)));
	这样定义`apple apples[10]`时，apples[0]和apples[1]就不再同一个cache line上了。

	而如果需要使该结构体中的两个变量(a、b)避免false sharing，可以这样定义：  

		struct apple{
			int a;
			int padding[15];   // sizeof(a) + sizeof(padding) == 64
			int b;
		};

- 使用局部变量或者线程局部存储（thread local storage，tls）  
	比如在linux下可以使用关键字__thread进行标识：
	
		__thread int sum = 0;

	注意，对于复杂数据结构，不应该使用__thread关键字，而是使用pthread_key_create、pthread_setspecific系列接口进行包装。

## 5. 再来实例分析
现在再来优化本文开始的那个简单程序，根据上面介绍的优化方式，这里分别实现了几个优化版本：
	
1. 直接使用局部变量：
	
		// t1.cpp 
		#include <iostream>
		#include <thread>
		
		int32_t global[2] = {0};
		
		void foo()
		{
		    int count = 0;
		    for(int i = 0; i < 100000000; i++)
		    {
		        //++global[0];
		        count ++;
		    }
		    global[0] = count;
		}
		
		void bar()
		{
		    int count = 0;
		    for(int i = 0; i < 100000000; i++)
		    {
		        //++global[1];
		        count ++;
		    }
		    global[1] = count;
		}
		
		int main()
		{
		    std::thread thread1(foo);
		    std::thread thread2(bar);
		    thread1.join();
		    thread2.join();
		    return 0;
		}
2. 使用线程局部存储
		
		// t2.cpp 
		#include <iostream>
		#include <thread>
		
		__thread int32_t global;
		
		void foo()
		{
		    for(int i = 0; i < 100000000; i++)
		    {
		        ++global;
		    }
		}
		
		void bar()
		{
		    int count = 0;
		    for(int i = 0; i < 100000000; i++)
		    {
		        ++global;
		    }
		}
		
		int main()
		{
		    std::thread thread1(foo);
		    std::thread thread2(bar);
		    thread1.join();
		    thread2.join();
		    return 0;
		}

3. 使用padding填充隔开cache line
			
		// t3.cpp 
		#include <iostream>
		#include <thread>
		
		int32_t global[100] = {0};
		
		void foo()
		{
		    for(int i = 0; i < 100000000; i++)
		    {
		        ++global[0];
		    }
		}
		
		void bar()
		{
		    for(int i = 0; i < 100000000; i++)
		    {
		        ++global[80];
		    }
		}
		
		int main()
		{
		    std::thread thread1(foo);
		    std::thread thread2(bar);
		    thread1.join();
		    thread2.join();
		    return 0;
		}

编译以上四个程序，并进行测试验证：
	
		# g++ -o t0 t0.cpp -std=c++0x -pthread
		# g++ -o t1 t1.cpp -std=c++0x -pthread
		# g++ -o t2 t2.cpp -std=c++0x -pthread
		# g++ -o t3 t3.cpp -std=c++0x -pthread
		# time ./t0 && time ./t1 && time ./t2 && time ./t3	
		./t0  1.35s user 0.01s system 197% cpu 0.690 total
		./t1  0.58s user 0.00s system 196% cpu 0.298 total
		./t2  0.58s user 0.00s system 196% cpu 0.299 total
		./t3  0.59s user 0.00s system 196% cpu 0.299 total


本文测试源代码可[点此下载](/public/download/false_sharing_test.tar.gz)。
