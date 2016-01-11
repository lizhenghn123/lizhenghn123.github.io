---
layout: post

title: 面向对象设计之六大原则

category: 架构

tags: 开发 技术 设计模式

keywords: 面向对象 设计模式 六大原则

description: 本文介绍面向对象设计过程中的六大原则， 比如单一职责原则、依赖倒置原则、里氏替换原则、开放封闭原则、接口隔离原则、最少知识原则。并介绍每一原则的优缺点及其示例。

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

**本节先介绍面向对象之6大原则。**

## 1. 面向对象之六大原则

### 单一职责原则（Single Responsibility Principle）
**要点**

- 一个类应该有且只有一个变化的原因。

**简述**

简单来说一个类只做一件事。这是一个备受争议却又及其重要的原则。因为单一职责的划分界限并不是如马路上的行车道那么清晰，很多时候都是需要靠个人经验来界定。当然最大的问题就是对职责的定义，什么是类的职责，以及怎么划分类的职责。
试想一下，如果你遵守了这个原则，那么你的类就会划分得很细，每个类都有自己的职责。恩，这不就是高内聚、低耦合么！当然，如何界定类的职责这需要你的个人经验了。

但是当职责单一的时候，你修改的代码能够基本上不影响其它的功能。这就在一定程度上保证了代码的可维护性。注意，单一职责原则并不是说一个类只有一个函数，而是说这个类中的函数所做的工作必须要是高度相关的，也就是高内聚。

单一职责的反例：

![单一职责的反例](http://i.imgur.com/Czr0jQY.png)

**示例**

HttpRequest（向server端请求http接口形式的数据）

    class HttpRequest
    {
        bool AddHeader(const char *key, const char *value);    
        int Get(const char *url, std::string& strResponse);    
        int Post(const char *url, const char *postData, int dataSize, std::string &strResponse);    
        int Post(const char *url, const std::string& postData, std::string& strResponse);
    };
这个接口就比较简单、明确，从名字上可以看出是提供Http Get、Post的实现，除此之外不做任何多于工作，可以说是遵守了单一职责原则。

**优点**

 - 类的复杂性降低，实现什么职责都有清晰明确的定义；
 - 可读性提高，复杂性降低；
 - 可维护性提高，可读性提高；
 - 变更引起的风险降低，变更是必不可少的，如果接口的单一职责做得好，一个接口修改只对相应的实现类有影响，对其他的接口无影响，这对系统的扩展性、维护性都有非常大的帮助。

**总结**

单一职责原则是一个非常简单的原则，但通常也是最难使用正确的一个原则。在实践中经常会遇到职责间相互耦合的情况，从这些各不相同的职责中发现并隔离职责就是软件设计的真谛所在。我们所讨论的其他设计原则最终也会回归到这个原则上来（The rest of the principles we will discuss come back to this issue in one way or another）。

### 2. 依赖倒置原则（Dependency Inversion Principle）
**要点**

 - 上层模块不应该依赖于低层模块，二者都应该依赖于抽象。
 - 抽象不应该依赖于具体实现细节，而具体实现细节应该依赖于抽象。

**简述**

很多软件工程师都有过“bad design”的痛苦经历， 尤其是当我们发现这个“bad design”的作者是我们自己时。那么究竟
是什么导致了“bad design”呢？

绝大多数工程师并不是从一开始就设计出了“bad design”，而很多软件都是在不断改进中而逐步退化成了一个“bad design”。

什么是“bad design”呢？

- 难以修改，因此可能会影响到系统的其他很多模块；
- 如果修改，很难预估破坏了系统中的哪些模块；
- 难以重用，因为不能从当前系统中解耦、剥离；

而导致“bad design”的原因在于设计僵化、脆弱，以及模块间相互依赖。

如果系统耦合严重，当期望对某一处修改时，可能产生级联修改，以致按下葫芦浮起瓢。

![](http://i.imgur.com/rge9lv0.gif)

甚至当对某一处修改时，无法预期可能产生的变化。

![脆弱性示例](http://i.imgur.com/uMRKSwq.gif)

而更无法对模块进行解耦以便进行重用。

![牵一发而动全身](http://i.imgur.com/4XaCmcs.gif)
 
**示例**

正例1： stl中容器，迭代器，算法， 泛型算法比如sort，find：

	 vector<int> vi;
	 vector<stirng> vs;
	 myqueue my;
	 char buf[1024]
	 std::sort(vi.begin(), vi.end());
	 std::sort(vs.begin(), vs.end());
	 std::sort(my.start(), my.end());
	 std::sort(buf, buf + 1024);
 这里的sort算法并不依赖究竟是针对什么进行排序，相反，只要求要排序的序列满足两个规则：迭代器可随机访问；元素可比较；

**优点**

 - 可扩展性好；
 - 耦合度低；
 - 提高代码的可读性和可维护性。

**总结**

DIP是很多面向对象技术的根基。它特别适合应用于构建可复用的软件框架，其对于构建弹性地易于变化的代码也特别重要。并且，因为抽象和细节已经彼此隔离，代码也变得更易维护。

### 3. 里氏替换原则 （Liskov Substitution Principle）
**要点**

- 使用基类对象指针或引用的函数必须能够在不了解子类的条件下使用子类的对象。
- LSP要求基类和子类必须有is-a的关系。

**简述**

面向对象的语言的三大特点是继承、封装、多态，里氏替换原则就是依赖于继承、多态这两大特性。**里氏替换原则简单来说就是所有引用基类的地方必须能透明地使用其子类的对象。**通俗点讲，只要父类能出现的地方子类就可以出现，而且替换为子类也不会产生任何错误或异常，使用者可能根本就不需要知道是父类还是子类。但是，反过来就不行了，有子类出现的地方，父类未必就能适应。

**示例**

违背 LSP 原则的一个简单示例

    void DrawShape(const Shape& s)
    {
	    if (typeid(s) == typeid(Square))   // if(s.id() == 111)
	    	DrawSquare(static_cast<Square&>(s)); 
	    else if (typeid(s) == typeid(Circle))  // else if(s.id() == 222)
	    	DrawCircle(static_cast<Circle&>(s));
    }
显然 DrawShape函数的设计存在很多问题。它必须知道所有 Shape 基类的衍生子类，并且当有新的子类被创建时就必须修改这个函数。事实上，很多人看到这个函数的结构都认为是在诅咒面向对象设计。而正确的做法可以是：
	
	class Shape
	{
		virtual void draw() = 0;
	};
	
	class Square : public Shape
	{
		virtual void draw();
	};
	
	class Circle : public Shape
	{
		virtual void draw();
	};
	
	void DrawShape(const Shape& s)
	{
		s.draw();
	}

疑难案例：

- 正方形是不是特殊的长方形？
- 鸵鸟是不是鸟？


**优点**

- 代码共享，减少创建类的工作量，每个子类都拥有父类的方法和属性；
- 提高代码的重用性；
- 提高代码的可扩展性，实现父类的方法就可以“为所欲为”了，很多开源框架的扩展接口都是通过继承父类来完成的；
- 提高产品或项目的开放性。

**缺点**

- 继承是侵入性的。只要继承，就必须拥有父类的所有属性和方法；
- 降低代码的灵活性。子类必须拥有父类的属性和方法，让子类自由的世界中多了些约束；
- 增强了耦合性。当父类的常量、变量和方法被修改时，必需要考虑子类的修改，而且在缺乏规范的环境下，这种修改可能带来非常糟糕的结果——大片的代码需要重构。

**总结**

里氏替换s原则是构建可维护性和可重用性代码的基础。它强调设计良好的代码可以不通过修改而扩展，新的功能通过添加新的代码来实现，而不需要更改已有的可工作的代码。抽象（Abstraction）和多态（Polymorphism）是实现这一原则的主要机制，而继承（Inheritance）则是实现抽象和多态的主要方法。

### 4. 开放封闭原则 （Open-Close Principle）
**要点**

- 模块应该面向扩展开放（Open For Extension），面向修改封闭（Closed For Modification）；
- 需求变化时优先考虑通过扩展来解决，尽可能不要使用直接修改已有源代码的方式解决；

**简述**

开闭原则是 Java 世界里最基础的设计原则，它指导我们如何建立一个稳定的、灵活的系统。开闭原则的定义是 : 一个软件实体如类、模块和函数应该对扩展开放，对修改关闭。在软件的生命周期内，因为变化、升级和维护等原因需要对软件原有代码进行修改时，可能会给旧代码中引入错误。因此当软件需要变化时，我们应该尽量通过扩展的方式来实现变化，而不是通过修改已有的代码来实现。

在软件开发过程中，永远不变的就是变化。开闭原则是使我们的软件系统拥抱变化的核心原则之一。对扩展可放，对修改关闭给出了高层次的概括，即在需要对软件进行升级、变化时应该通过扩展的形式来实现，而非修改原有代码。当然这只是一种比较理想的状态，是通过扩展还是通过修改旧代码需要根据代码自身来定。

**优点**

- 增加稳定性；
- 可扩展性高；

**总结**

开放封闭原则是构建可维护性和可重用性代码的基础。它强调设计良好的代码可以不通过修改而扩展，新的功能通过添加新的代码来实现，而不需要更改已有的可工作的代码。可以通过多态（继承/模板）的方式实现这一原则。

### 5. 接口隔离原则 （Interface Segregation Principle）
**要点**

- 避免胖接口（fat interface）
- 客户端不应该依赖它不需要的接口Clients should not be forced to depend upon interfaces that they do not use.

**简述**

客户端不应该依赖它不需要的接口；一个类对另一个类的依赖应该建立在最小的接口上。根据接口隔离原则，当一个接口太大时，我们需要将它分割成一些更细小的接口，使用该接口的客户端仅需知道与之相关的方法即可。
可能描述起来不是很好理解，我们还是以示例来加强理解吧。

如果类的接口定义暴露了过多的行为，则说明这个类的接口定义内聚程度不够好。

**示例**

C++ STL中的map接口：

    begin           end       rbegin          rend
    cbegin          cend      crbegin         crend 
    empty           size      max_size        operator[]
    at              insert    erase           swap
    clear           emplace   emplace_hint    key_comp
    value_comp      find      count           lower_bound
    upper_bound     equal_range               get_allocator
一个支持并发的、带锁的map接口：

    add             find      remove          size
原始map的其他接口这里都要屏蔽掉，而不应该提供给用户使用。

例如一个支持并发的同步阻塞队列：

    template <typename Job, typename Queue = std::queue<Job>, typename Order = tagFIFO >
    class BlockingQueue : public zl::NonCopy
    {
        void push(const JobType& job);    
        bool pop(JobType& job);    
        JobType pop();    
        bool pop(std::vector<JobType>& vec, int pop_size = -1);    	
        bool try_pop(JobType& job);    
        void stop();    
        size_t size() const;    
        bool empty();
    };
上面接口的定义可以参考[java.util.concurrent.BlockingQueue<E>](http://docs.oracle.com/javase/7/docs/api/java/util/concurrent/BlockingQueue.html)

**优点**

- 降低耦合性；
- 提升代码的可读性；
- 隐藏实现细节。

### 6. 最少知识原则/迪米特原则 （Least Knowledge Principle/Law of Demeter）
**要点**

- 更好的信息隐藏和更少的信息重载；
- 一个对象应该对其他对象保持最少的了解；

**简述**

迪米特法则也称为最少知识原则（Least Knowledge Principle），虽然名字不同，但描述的是同一个原则：一个对象应该对其他对象有最少的了解。通俗地讲，一个类应该对自己需要耦合或调用的类知道得最少，这有点类似接口隔离原则中的最小接口的概念。类的内部如何实现、如何复杂都与调用者或者依赖者没关系，调用者或者依赖者只需要知道他需要的方法即可，其他的我一概不关心。类与类之间的关系越密切，耦合度越大，当一个类发生改变时，对另一个类的影响也越大。

迪米特法则还有一个英文解释是: Only talk to your immedate friends（ 只与直接的朋友通信。）什么叫做直接的朋友呢？每个对象都必然会与其他对象有耦合关系，两个对象之间的耦合就成为朋友关系，这种关系的类型有很多，例如组合、聚合、依赖等。

**示例**

Adapter模式
 
STL中stack<T>分类是适配器，而不同于vector<T>, deque<T>是序列容器。因为：

    template<class T, class Container = std::deque<T> >
    class stack;
stack是由deque，或者vector适配而来，甚至自己实现的只要符合stack规则的自定义容器。

另外一个就是Impl手法，也算是最少知识原则的应用了，对外暴露的只有接口，而没有任何数据结构或者算法接口：
    
	class Channel
    {
    public:
	    void CloseChannel();
	    void DestoryChannel();
	    bool Reset();
	    bool Recognize(const char* data, size_t size);

    private:
    	ChannelImpl* impl_;
    };
    
    Channel::Channel()
    {
	    impl_ = new ChannelImpl;
	    impl_->CreateChannel(); // initial
	    impl_->OpenChannel();
    }    
    void Channel::CloseChannel()
    {
    	impl_->CloseChannel();
    }    
    void Channel::DestoryChannel()
    {
    	impl_->DestoryChannel();
    }

**优点**

- 降低复杂度；
- 降低耦合度；
- 增加稳定性。

**缺点**

- 可能会设计出很多用于中转的包装方法（Wrapper Method）。

## Reference
- [http://blog.csdn.net/qq51931373/article/details/45889765](http://blog.csdn.net/qq51931373/article/details/45889765)
- [http://www.objectmentor.com/resources/articles/ocp.pdf](http://www.objectmentor.com/resources/articles/ocp.pdf)
- [http://www.objectmentor.com/resources/articles/srp.pdf](http://www.objectmentor.com/resources/articles/srp.pdf)
- [http://www.objectmentor.com/resources/articles/lsp.pdf](http://www.objectmentor.com/resources/articles/ocp.pdf)
- [http://www.objectmentor.com/resources/articles/isp.pdf](http://www.objectmentor.com/resources/articles/srp.pdf)
- [http://www.objectmentor.com/resources/articles/dip.pdf](http://www.objectmentor.com/resources/articles/ocp.pdf)
- [http://www.objectmentor.com/resources/articles/lkp.pdf](http://www.objectmentor.com/resources/articles/srp.pdf)

  [1]: java.util.concurrent.BlockingQueue%3CE%3E