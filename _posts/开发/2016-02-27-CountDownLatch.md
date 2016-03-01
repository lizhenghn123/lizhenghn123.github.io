---
layout: post

title: 多线程并发编程之同步工具CountDownLatch

category: 开发

tags: 开发 技术 多线程

keywords: 开发 技术 多线程 CountDownLatch 栅栏

description: 滴答滴答滴答滴答。

---

## CountDownLatch
我们先来学习一下JDK1.5 API中关于这个类的详细介绍： 

> 一个同步辅助类，在完成一组正在其他线程中执行的操作之前，它允许一个或多个线程一直等待。 用给定的计数初始化CountDownLatch，在当前计数到达零之前，await方法会一直受阻塞。之后，会释放所有等待的线程，await 的所有后续调用都将立即返回。这种现象只出现一次——计数无法被重置。如果需要重置计数，请考虑使用 CyclicBarrier。

CountDownLatch是一个倒数计数的锁，当倒数到0时触发事件，也就是开锁，此时允许可以进入。CountDownLatch最重要的方法是countDown()和await()，前者主要是倒数一次，后者是等待倒数到0，如果没有到达0，就只有阻塞等待。一个CountDouwnLatch实例是不能重复使用的，也就是说它是一次性的，锁一经被打开就不能再关闭使用了。

**在一些应用场合中，CountDownLatch非常有用：将一个任务分成若干线程执行，等到所有线程执行完，再进行汇总处理。 也即需要等待某个条件达到要求后才能做后面的事情；同时当线程都完成后也会触发事件，以便进行后面的操作。**

**比如，具有计数1的CountdownLatch对象可以用作“发号枪”，比如用来立即启动一组执行相关操作的子线程，所有子线程在闩锁处等待，主线程减少计数，从而立即释放所有子线程进行实际操作， 而具有计数N的CountdownLatch对象可以用作“结束枪”，等待所有子线程完成各自任务时，发出提示，主线程等待所有子线程完成后，再继续下一步动作。**

下面举一个简单例子进行说明，比如进行一个百米赛跑，5名参赛选手已经就绪，需要等待裁判的起跑命令才能开始跑，而在比赛结束也即所有人都到达终点后，由裁判统计所有人的成绩并进行排名。这里分别用java.util.concurrent包中的CountDownLatch和我自己用C++实现的CountDownLatch类各自实现一遍：

思路是假设每个选手都是一个线程，各自在各自的线程中运行，等运行完成后通知主线程。

Java代码：

	import java.lang.Thread;
	import java.util.concurrent.CountDownLatch;
	
	public class TestCountDownLatch {
	
		private static final int N = 5;
	
		public static void main(String[] args) throws InterruptedException {
			CountDownLatch startLatch_ = new CountDownLatch(1);				// 发号枪
			CountDownLatch doneLatch_  = new CountDownLatch(N);				// 结束信号
			
			for (int i = 1; i <= N; i++) {
				new Thread(new Worker(i, startLatch_, doneLatch_)).start(); // 各个子线程，表示一个参赛选手
			}
			System.out.println("main thread release start signal...");
			startLatch_.countDown();		// 裁判发枪，表示开始比赛，各子线程开始运行
			System.out.println("main thread wait finish signal...");
			doneLatch_.await();				// 等待所有的子线程执行完毕，表示各个选手已到达
			System.out.println("main thread game over");	
		}
	
		static class Worker implements Runnable {
			private final CountDownLatch startLatch_;
			private final CountDownLatch doneLatch_;
			private int id_;
	
			Worker(int id, CountDownLatch startLatch_, CountDownLatch doneLatch_) {
				this.id_ = id;
				this.startLatch_ = startLatch_;
				this.doneLatch_ = doneLatch_;
			}	
			public void run() {
				try {
					startLatch_.await(); 		// 等待主线程发起命令
					System.out.println("work thread [" + id_ + "] running");
					Thread.sleep((int)Math.random() % 1000);   // 模拟各自的运行时间
				} catch (InterruptedException e) {
					e.printStackTrace();
				} finally {
					System.out.println("work thread [" + id_ + "] finished");
					doneLatch_.countDown();		// 通知主线程本子线程已完成
				}
			}
		}
	}

C++代码：
	
	class TestCountDownLatch
	{
	public:
	    TestCountDownLatch(int workers)
	        : startLatch_(1) , doneLatch_(workers)
	    {
	        for (int i = 0; i < workers; ++i)
	        {
	            string name("thread_");
	            name += zl::base::toStr(i);
	            Thread *trd = new Thread(std::bind(&TestCountDownLatch::workerThread, this, i), name);
	            threads_.push_back(trd);
	        }
	    }
	    void run()
	    {
	        printf("main thread release start signal...\n");
	        startLatch_.countDown();
	        printf("main thread wait finish signal...\n");
	        doneLatch_.wait();
	        printf("main thread game over...\n");
	    }
	private:
	    void workerThread(int id)
	    {
	        startLatch_.wait();         // 等待主线程发起命令
	        printf("work thread [%d] running\n", id);
	
	        this_thread::sleep_for(chrono::milliseconds(rand() % 1000));
	
	        printf("work thread [%d] finished\n", id);
	        doneLatch_.countDown();     // 通知主线程本子线程已完成
	    }
	private:
	    CountDownLatch startLatch_;
	    CountDownLatch doneLatch_;
	    vector<Thread*> threads_;
	};
	
	int main()
	{
	    TestCountDownLatch tcd(5);
	    tcd.run();
	}

执行结果都是类似的：
	
	main thread release start signal...
	main thread wait finish signal...
	work thread [1] running
	work thread [5] running
	work thread [2] running
	work thread [3] running
	work thread [2] finished
	work thread [4] running
	work thread [3] finished
	work thread [4] finished
	work thread [5] finished
	work thread [1] finished
	main thread game over

总结
CountdownLatch 将到达和等待功能分离。任何线程都可以通过调用 countDown() 减少当前计数，这时不会阻塞线程，而只是减少计数。而调用 await()的任何线程都会被阻塞，直到闩锁计数减少为零，在该点等待的所有线程才被释放，对await() 的后续调用将立即返回。

CounDownLatch对于管理一组相关线程非常有用。上述示例代码中就形象地描述了两种使用情况。第一种是计算器为1，代表了两种状态，开关。第二种是计数器为N，代表等待N个操作完成。今后我们在编写多线程程序时，可以使用这个构件来管理一组独立线程的执行。 

注：

1. Java CountdownLatch接口及使用示例请看：[oracle.com-CountdownLatch](http://docs.oracle.com/javase/7/docs/api/java/util/concurrent/CountDownLatch.html);

2. 我用C++实现的CountdownLatch类代码可以查看：[github-CountdownLatch](https://github.com/lizhenghn123/zl_reactor/blob/master/zlreactor%2Fthread%2FCountDownLatch.h)。

