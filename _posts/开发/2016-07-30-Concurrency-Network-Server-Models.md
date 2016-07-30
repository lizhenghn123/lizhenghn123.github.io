---
layout: post

title: 常见网络服务器并发编程模型

category: 开发

tags: 开发 网络

keywords: 服务器开发 网络编程模型 并发

description: 本文介绍了一些常见的网络服务器并发编程模型的多种方案，比如多线程模型、多进程模型、线程池模型、Reacotor模式等等。

---

先上一张图作为引言：  

![concurrent_net_server](http://i.imgur.com/kO0Bme9.jpg)  

下面分别对这几个方案进行介绍。

## 0. 循环式/迭代式( iterative )服务器
![iterative_server2](http://i.imgur.com/tAgVEBS.png)


这个服务器模型其实并不算是并发服务器，而是 iterative 服务器，因为它一次只能服务一个客户。所以该模型只适合处理短连接，不能处理长连接，短连接时处理完后就关闭连接，而长连接并不关闭连接，不适合执行时间较长的服务。而且由于是单线程服务，也无法充分利用多核CPU。

代码见 UNP figure 1.9， UNP 以此为对比其他方案的基准点。

## 1. PPC: 一个连接对应一个进程

![PPC](http://i.imgur.com/fRPr7xd.png)

传统的Unix并发网络编程方案，能够处理多个客户端，子进程处理客户端的请求，注意父进程需要关闭与原客户端的连接，而子进程关闭listen fd。

UNP将这种方案称之为process-per-connection，即PPC。该方案很古老，是 old-school way，[据说第一个webserver（CERN）就是使用此方案](http://bulk.fefe.de/scalable-networking.pdf)。

这种方案适合场景是：并发连接数不大，且请求响应的工作量远大于fork或pthread_create的开销。比如数据库服务器。

这种方案适合长连接，且执行时间比较长的服务，但不太适合短连接，因为创建一个进程或者线程的开销一般来说还是比较大的。

## 2. TPC: 一个连接对应一个线程
该方案同上面方案1的Process Per Connection模型类似，只是由子进程处理新来连接改为由子线程来处理，称之为thread-per-connection，即TPC。

![TPC](http://i.imgur.com/NyL1yq0.png)

PPC和TPC思想基本是一样的，就是为每一个到来的连接创建一个新的进程或线程，然后在次进程或线程内完成该连接的请求响应。
所以TPC与PPC的使用场景是一样的，但创建线程的开销远低于创建进程的开销。
两者的缺点也是一样的，一个程序创建的子进程或子线程总是有上限的，且当连接多了之后，大量的进程/线程间切换需要大量的开销；

通常这两个方案能处理的最大连接数都不会高，一般在几百个左右。

## 3. pre-fork： 预先创建子进程
  
![pre_fork](http://i.imgur.com/m8iXFdO.png)

该方案是对方案1的优化，程序启动时提前创建多个子进程等待客户端连接。

UNP 详细分析了几种变化，包括对 accept 惊群问题的考虑。

这里可能出现一个问题，就是当一个客户端请求的时候，多个子进程都accpet，只有一个进程返回是正确的， 这就是惊群现象。
这种和上一种相比，减少了系统开销

## 4. pre-thread: 预先创建子线程
![pre_thread](http://i.imgur.com/JO6hHPZ.png)
这是对方案 2 的优化， UNP 详细分析了它的几种变化。 3 和 4 这两个方案都是 Apache httpd 长期使用的方案。


## 5. 反应式( reactive )服务器 (reactor模型)： 单线程处理多个客户端
![SingleReactor](http://i.imgur.com/f704P2n.png)

该方案是第一个非阻塞式网络模型。方案0-4都是阻塞式网络编程，程序会一直阻塞在系统调用read上，等待client的数据到达。而本方案（以及之后的所有方案）都是非阻塞式网络编程，程序一般会阻塞在IO复用上（比如select、epoll_wait），而通常不会在accept、read、write调用上阻塞，这样既充分利用TCP是全双工协议的优势，也支持高并发网络请求。

本方案所有的处理都是在单线程中完成的，且是顺序完成的，因此要着重注意不要在线程中处理执行时间较长的任务，会导致后续请求的响应时间都增大，甚至连sleep都不能使用（可以通过计时器超时回调来做）。

本方案比较适合IO密集的应用，不太适合CPU密集的应用，因为较难发挥多核CPU的威力。

本方案是在一个IO线程中处理所有IO相关的操作，因此需要非阻塞IO，且不适合执行时间比较长的服务，所以为了让客户感觉是在“并发”处理而不是“循环”处理，每个请求必须在相对较短时间内执行。

本方案相对前几种方案，处理client消息的网络延迟有可能稍微增大一些，相对于阻塞模式中系统在read处等待，一旦返回就表示接收到了数据，而本方案中需要先调用poll，等有消息到来后，poll返回然后再通过read读取数据。

Reactor虽然看似增加了复杂性，但却是当前网络服务器编程的首选，因为能够处理高并发、支持大量客户端的连接，尤其适合长连接应用。但当连接数更大，比如C10K、C100K时，单线程Reactor要处理连接接收、消息读取、解码、计算、编码、消息发送这些操作，最多也就占满一个CPU核心，此时单核CPU负载虽然上升了，但程序处理速度变慢、响应时间增加，可能会导致大量消息积压。接下来会再介绍对此的优化版本。

使用单线程Reactor方案最有名的应用当属开源产品内存数据库[redis](https://github.com/antirez/redis)了，据说redis每秒可支持10W连接的查询操作。

## 6. reactor + thread per request（过渡方案）： 每当一个请求过来就创建一个线程
他能够充分利用多核CPU

过渡方案，是对方案5的一种优化（无法利用多核CPU），收到客户端请求之后，不在IO线程中计算，而是创建一个子线程进行处理，可称之为逻辑线程或者业务线程，以区别于IO线程，这样就可以充分利用多核CPU。

由于为每个请求创建一个新的线程，这个做法还是比较粗糙的，因此只是过渡方案。

且该方案隐藏了一个问题：如果一个连接上有多个请求（在长连接应用中很正常），那么可能会有多个业务线程分别进行处理，那么谁先完成，谁先返回给客户端都是不确定的（可以加id区分）。

这是非常初级的多线程应用，因为它为每个请求（而不是每个连接）创建了一个新线程。这个开销可以用线程池来避免，
即方案 8。这个方案还有一个特点是 out-of-order，即同时创建多个线程去计算同一
个连接上收到的多个请求，那么算出结果的次序是不确定的，可能第 2 个 Sudoku 比
较简单，比第 1 个先算出结果。这也是为什么我们在一开始设计协议的时候使用了
id，以便客户端区分 response 对应的是哪个 request。

## 7. reactor + worker thread（过渡方案）： 为每一个连接创建一个线程

reactor + worker thread（过渡方案） 事件循环+一个连接一个线程

是对方案6的一种优化，不再为一个请求创建一个线程，而是为每一个连接创建一个业务线程。所以更适合长连接场景。

但是该方案与TPC是类似的，存在类似的问题：支持的并发请求仍受限于最大线程数。该方案仍是过渡方案，如果要使用，可以考虑直接使用上述方案2的“TPC: 一个连接对应一个线程”。

## 8. reactor + thread pool：能适应密集计算

![SingleReactor_ThreadPool](http://i.imgur.com/FsxAjgW.png)

该方案是对方案6的一种优化，解决了方案6中为每个请求创建线程的不足。该方案中所有IO操作仍在reactor线程中，而所有的请求响应处理都通过一个线程池进行完成。

## 9. multiple reactors： one loop per thread（能适应更大的突发I/O）
multiple reactors in threads： 每个IO线程都有一个Reactor事件循环。

![MultipleReactor](http://i.imgur.com/okBfn83.png)

总共有N的Reactor IO线程，其中mainReactor是主线程，把监听套接字加进去，每当一个客户端请求过来的时候，监听套接就产生可读事件，accprtor就返回已连接套接字，然后通过比如round robin机制分别加入到各subReactor中，然后该连接就只在某一subReactor进行处理。

说明，mainReactor还可以对刚接受的新连接进行校验等操作。

## 10. multiple reactors + one loop per process（突发I/O与密集计算）

multiple reactors in process ： 一个进程一个Reactor事件循环

本方案与方案9是类似的，唯一区别就是各Reactor循环分别在线程或进程中运行。这里就不再画图了，和方案9的图是一样的。

该方案最有名的应用当属Ngnix了。

## 11. multiple reactors + thread pool

![MultipleReactor_ThreadPool](http://i.imgur.com/XdlT5dJ.png)

是对方案8和方案9的集成，既使用多个 reactors 来处理 IO，又使用线程池来处理计算。这种方案适合既有突发 IO （利用多线程处理多个连接上的 IO），又有突发计算的应用（利用线程池把一个连接上的计算任务分配给多个线程去做）。

这里的线程池在各Reactors中是共享的。

## 12. 异步IO：proactor模型
以上介绍的是阻塞式以及Reactor模式的非阻塞同步IO网络编程，以及各个变种。其实本文涉及到的另一种编程模型是异步IO模型，也即proactor模型。

![linux_aio](http://i.imgur.com/UApsFGo.png)

理论上proactor比reactor效率要高一些，异步I/O能够充分利用DMA特性，让I/O操作与计算重叠。目前已知的异步IO在Windows下通过IOCP机制实现，而在Linux系统下是aio_*，但Linux的aio尚不完善，因此在Linux下实现高并发网络编程时都是以Reacotr模式为主，比如nigix、redis、libevent等等几乎所有的知名开源产品。

另外boost asio号称实现了proactor模型，其实它在Windows下采用IOCP，而在Linux下是用Reactor模式（采用epoll）模拟出来的假的异步模型。

因此这里不再对异步IO做过多介绍。

## Reference
- [几种网络服务器模型的介绍与比较](http://www.ibm.com/developerworks/cn/linux/l-cn-edntwk/)
- [Netty系列之Netty线程模型](http://www.infoq.com/cn/articles/netty-threading-model)
- [使用异步 I/O 大大提高应用程序的性能](https://www.ibm.com/developerworks/cn/linux/l-async/)
