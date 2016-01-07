---
layout: post
title: 面向对象设计之要两大要点
category: 架构
tags: 开发 技术 设计模式
keywords: 面向对象 设计模式 面向接口编程 优先使用组合
description: 面向对象设计之两大要点 面向接口编程而不是面向实现编程 优先使用组合而不是继承
---

**总览**

在工作初期，我们可能会经常会有这样的感觉，自己的代码接口设计混乱、代码耦合较为严重、一个类的代码过多等等，自己回头看的时候都觉得汗颜。再看那些知名的开源库，它们大多有着整洁的代码、清晰简单的接口、职责单一的类，这个时候我们通常会捶胸顿足而感叹：什么时候老夫才能写出这样的代码！

作为新手，我们写的东西不规范或者说不够清晰的原因是缺乏一些指导原则。我们手中挥舞着面向对象的大旗，写出来的东西却充斥着面向过程的气味。也许是我们不知道有这些原则，也许是我们知道但是不能很好运用到实际代码中，亦或是我们没有在实战项目中体会到这些原则能够带来的优点，以至于我们对这些原则并没有足够的重视。

在这里，我们将一块学习一些面向对象设计的要点、原则及模式。

在此之前，有一点需要大家知道，熟悉这些原则不会让你写出优秀的代码，只是为你的优秀代码之路铺上了一层栅栏，在这些原则的指导下你才能避免陷入一些常见的代码泥沼，从而让你专心写出优秀的东西。

本文将逐渐介绍一下内容：

0. 面向对象之2大要点
1. 面向对象之6大原则
2. 面向对象之23种设计模式

本节先介绍面向对象之2大要点。

## 面向对象之两大要点
### 面向接口编程而不是面向实现编程
**简述**

面向接口和面向实现都基于面向对象的模式，也就是说面向接口并不能称为比面向对象的更高的一种编程模式，而是在面向对象中大的背景下的一种更加合理的软件设计模式，这里的接口并不是具体语言中的实现机制（比如java中的interface），而是软件设计层面的一种模式。面向接口编程它增强了类与类之间，模块与模块的之间的低耦合性，使软件系统更容易维护、扩展。

举个简单的例子，我们经常用的操作数据库的方法，在jdk中定义的都是接口，由不同的数据库厂商实现，比如mysql的驱动，oracle的驱动，都是实现了jdk中定义接口标准。jdk中数据库驱动的设计就是面向接口的，而不同的数据库厂商就是面向实现的。面向接口的好处就是，定义好接口标准，不管是谁只要按定义好的标准来实现，都可以无缝的切换，所以不管是用mysql也好，还是用oracle也都，从用户层面来说都是在使用jdk的api。

面向实现编程主要缺点是高耦合，不支持扩展，而面向接口编程的主要优点是低耦合，便于扩展。

**优点**

- 客户端不知道他们所使用对象的具体类型
- 一个对象可以被另一个对象轻易地替换
- 对象不需要硬连接到一个特殊类的对象，因此增加了灵活性
- 松耦合
- 增加了重用的机会
- 增加了组合的机会，因为被包含的对象可以被实现了特定接口的其他对象替换

**缺点**

- 某种程度上增加了设计的复杂性

**例子**

假设我们要封装一个IO复用的类，通常有select、poll、epoll模型，且允许用户自行选择某一模型， 因此可以通过继承体系来实现。

    /// I/O MultiPlexing 抽象接口
    class Poller
    {
    public:
        typedef std::vector<Channel *>          ChannelList;
        typedef std::map<ZL_SOCKET, Channel *>  ChannelMap;
    
    public:
        explicit Poller(EventLoop *loop);
        virtual ~Poller();
    
        /// 根据各种宏定义及操作系统区分创建可用的backends
        static Poller *createPoller(EventLoop *loop);

    public:
        /// 添加/更新Channel所绑定socket的I/O events, 必须在主循环中调用
        virtual bool updateChannel(Channel *channel) = 0;
    
        /// 删除Channel所绑定socket的I/O events, 必须在主循环中调用
        virtual bool removeChannel(Channel *channel) = 0;
    
        /// 得到可响应读写事件的所有连接, 必须在主循环中调用
        virtual Timestamp poll_once(int timeoutMs, ChannelList &activeChannels) = 0;
    
        /// 获得当前所使用的IO复用backends的描述
        virtual const char* ioMultiplexerName() const = 0;
    protected:
        ChannelMap  channelMap_;
        EventLoop   *loop_;
    };

    /*static*/ Poller* Poller::createPoller(EventLoop *loop)
    {
    #if defined(USE_POLLER_EPOLL)
    	return new EpollPoller(loop);
    #elif defined(USE_POLLER_SELECT)
        return new SelectPoller(loop);
    #elif defined(USE_POLLER_POLL)
        return new PollPoller(loop);
    #else
    	return NULL;
    #endif
    }

    class SelectPoller : public Poller
    {
    public:
        explicit SelectPoller(EventLoop *loop);
        ~SelectPoller();
        
        virtual bool updateChannel(Channel *channel);
        virtual bool removeChannel(Channel *channel);
        virtual Timestamp poll_once(int timeoutMs, ChannelList& activeChannels);
        virtual const char* ioMultiplexerName() const { return "select"; }
    private:
        fd_set readfds_;           /// select返回的所有可读事件
        fd_set writefds_;          /// select返回的所有可写事件
        fd_set exceptfds_;         /// select返回的所有错误事件
    
        fd_set select_readfds_;    /// 加入到select中的感兴趣的所有可读事件
        fd_set select_writefds_;   /// 加入到select中的感兴趣的所有可写事件
        fd_set select_exceptfds_;  /// 加入到select中的感兴趣的所有错误事件
        std::set< int, std::greater<int> >  fdlist_;
    };
    
    class EpollPoller : public Poller
    {
    public:
        explicit EpollPoller(EventLoop *loop, bool enableET = false);
        ~EpollPoller();
        
        virtual bool updateChannel(Channel *channel);
        virtual bool removeChannel(Channel *channel);
        virtual Timestamp poll_once(int timeoutMs, ChannelList& activeChannels);
        virtual const char* ioMultiplexerName() const { return "linux_epoll"; }
    
    private:
        typedef std::vector<struct epoll_event> EpollEventList;
        int  epollfd_;
        bool enableET_;
        EpollEventList events_;
    };

以上通过多态实现了一个IO复用的继承体系。在纯虚基类(Poller)中定义了所有要实现IO复用的接口，而由其他子类（SelectPoller、EpollPoller）针对接口分别实现相应功能。对于使用者来说，并不需要考虑其内容实现细节，只需根据Poller类的接口即可使用。

### 优先使用组合而不是继承（CARP）
**简述**

面向对象系统中功能复用的两种最常用技术是类继承和对象组合(object composition)。

类继承允许你根据其他类的实现来定义一个类的实现。这种通过生成子类的复用通常被称为白箱复用(white-box reuse)。术语“白箱”是相对可视性而言：在继承方式中，父类的内部细节对子类可见，可以说是“破坏了封装性”，父类实现中的任何变化必然会导致子类发生变化，彼此间的依赖程度高。

对象组合是类继承之外的另一种复用选择。新的更复杂的功能可以通过组装或组合对象来获得。对象组合要求被组合的对象具有良好定义的接口。这种复用风格被称为黑箱复用(black-box reuse)，因为对象的内部细节是不可见的。对象只以“黑箱”的形式出现，只需要关心提供的接口，彼此间的依赖低。

优先使用组合而不是继承要求我们在复用对象的时候，要优先考虑使用组合，而不是继承，这是因为在使用继承时，父类的任何改变都可能影响子类的行为，而在使用组合时，是通过获得对其他对象的组合而获得更强功能，且有助于保持每个类的单一职责原则。

继承和组合各有优缺点。类继承是在编译时刻静态定义的，且可直接使用，因为程序设计语言直接支持类继承。类继承可以较方便地改变被复用的实现。当一个子类重定义一些而不是全部操作时，它也能影响它所继承的操作，只要在这些操作中调用了被重定义的操作。

优先使用对象组合有助于你保持每个类被封装，并被集中在单个任务上。这样类和类继承层次会保持较小规模，并且不太可能增长为不可控制的庞然大物。另一方面，基于对象组合的设计会有更多的对象 (而有较少的类)，且系统的行为将依赖于对象间的关系而不是被定义在某个类中。

**例子**

Echo协议是指服务端收到客户端的任何数据后都原封不动的发送回去。如果要实现一个EchoServer，按照传统的做法，一般是先实现一个TcpServer抽象类，设置几个虚函数，比如连接到来、数据到来，连接关闭等等，这也是面向对象中多态机制的常用实现方式。而这里我们演示一个基于函数回调的实现。

假设我们已经有了一个封装了IO复用的EventLoop类和一个可以直接使用但不做任何数据处理的TcpServer类。
TcpServer的接口如下：

	class TcpServer : zl::NonCopy
	{
	public:
	    TcpServer(EventLoop *loop, const InetAddress& listenAddr);	
	    void start();	
	public:
	    EventLoop* getLoop() const
	    { return loop_; }
	
	    void setConnectionCallback(const ConnectionCallback& cb)
	    { connectionCallback_ = cb; }
	
	    void setMessageCallback(const MessageCallback& cb)
	    { messageCallback_ = cb; }
	
	    void setWriteCompleteCallback(const WriteCompleteCallback& cb)
	    { writeCompleteCallback_ = cb; }
	};

那么一个EchoServer实现起来就很简单了：

	class EchoServer
	{
	public:
	    EchoServer(EventLoop *loop, const InetAddress& listenAddr);
	    void start();
	private:
		/// 客户端连接建立或关闭时的回调
	    void onConnection(const TcpConnectionPtr& conn);
		/// 客户端有数据发送过来时的回调
	    void onMessage(const TcpConnectionPtr& conn, ByteBuffer *buf, const Timestamp& time);
	private:
	    EventLoop *loop_;
	    TcpServer *server_;
	};

使用方式也很简单：

    EventLoop loop;
    InetAddress listenAddr(port);
    EchoServer server(&loop, listenAddr);
    server.start();
    loop.loop();
这样就完成了一个EchoServer。


与此类似，还有简单的daytime协议，客户端连接服务端后，服务端返回给客户端一个当前时间。一个DaytimeServer完全可以按照上面的思路来实现。


这也是面向对象和基于对象实现的差异，关于以函数回调方式替代面向对象中纯虚函数方式的更多介绍请参考：[以boost::function和boost:bind取代虚函数](http://blog.csdn.net/solstice/article/details/3066268)。

本文完。