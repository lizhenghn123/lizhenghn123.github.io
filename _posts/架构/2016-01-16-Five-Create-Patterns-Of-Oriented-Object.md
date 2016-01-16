---
layout: post

title: 面向对象设计模式之五种创建型模式

category: 架构

tags: 开发 技术 设计模式

keywords: 面向对象 设计模式 创建型设计模式 单例模式 工厂方法模式 抽象工厂模式 建造者模式 原型模式

description: 本文介绍了设计模式中的五种创建型设计模式，分别是单例模式、工厂方法模式、抽象工厂模式、建造者模式、原型模式，本文参考自GOF名著<<设计模式-可复用面向对象软件的基础（中文版）>>。

---

本文主要讲述设计模式中的五种创建型设计模式。

## 创建型模式
创建型模式主要关注对象的创建过程，将对象的创建过程进行封装，使客户端可以直接得到对象，而不用去关心如何创建对象。
这里共有5种创建型模式：

- 单例模式(Singleton) :                  用于得到某类型的唯一对象；
- 工厂方法模式(Factory Method) :         用于创建复杂对象；
- 抽象工厂模式(Abstract Factory) :       用于创建一组相关或相互依赖的复杂对象；
- 建造者模式(Builder) :                  用于创建模块化的更加复杂的对象；
- 原型模式(ProtoType) :                  用于得到一个对象的拷贝；

### 1. 单例模式(Singleton)
#### **意图**

保证一个类仅有一个实例，并提供一个访问它的全局访问点。

#### **问题**
Singleton 模式解决问题十分常见： 我们怎样去创建一个唯一的变量（ 对象）？ 比如可以通过全局变量来解决，但是一个全局变量使得一个对象可以被访问，但它不能防止你实例化多个对象。

一个更好的办法是，让类自身负责保存它的唯一实例。这个类可以保证没有其他实例可以被创建（通过截取创建新对象的请求），并且它可以提供一个访问该实例的方法。这就是Singleton模式。

#### **示例**

	template <class T>
	class Singleton
	{
	public:
	    static T* getInstancePtr()
	    {
	        if(0 == proxy_.instance_)
	        {
	            createInstance();
	        }
	        return proxy_.instance_;
	    }
	
	    static T& getInstanceRef()
	    {
	        if(0 == proxy_.instance_)
	        {
	            createInstance();
	        }
	        return *(proxy_.instance_);
	    }
	
	    static T* createInstance()
	    {
	        return proxy_.createInstance();
	    }
	
	    static void deleteInstance()
	    {
	        proxy_.deleteInstance();
	    }
	
	private:
	    struct Proxy
	    {
	        Proxy() : instance_(0)
	        {
	        }
	        ~Proxy()
	        {
	            if(instance_)
	            {
	                delete instance_;
	                instance_ = 0;
	            }
	        }
	        T* createInstance()
	        {
	            T *p = instance_;
	            if(p == 0)
	            {
	                zl::thread::LockGuard<zl::thread::Mutex> guard(lock_);
	                if((p = instance_) ==0)
	                {
	                    instance_ = p = new T;
	                }
	            }
	            return instance_;
	        }
	        void deleteInstance()
	        {
	            if(proxy_.instance_)
	            {
	                delete proxy_.instance_;
	                proxy_.instance_ = 0;
	            }
	        }
	        T *instance_;
	        zl::thread::Mutex lock_;
	    };
	protected:
	    Singleton()  {	}
	    ~Singleton() {	}
	private:
	    static Proxy proxy_;
	};

    // usage
	class SomeMustBeOneObject : private Singleton<SomeMustBeOneObject>
	{}
	
	SomeMustBeOneObject* o1 = Singleton<SomeMustBeOneObject>::getInstancePtr();
	SomeMustBeOneObject* o2 = Singleton<SomeMustBeOneObject>::getInstancePtr();
	SomeMustBeOneObject& o3 = Singleton<SomeMustBeOneObject>::getInstanceRef();
	assert(o1 == o2);
	assert(o1 == &o3);
	SomeMustBeOneObject* o4 = new SomeMustBeOneObject; // Compile Error!
	SomeMustBeOneObject o5; 						   // Compile Error!

#### **引申**
Singleton 算是最简单的一个模式了，但是最初想写对一个好用的Singleton也是有很多困难的。比如下面的这几个实现（都有问题）：

	template <class T>
	class Singleton1
	{
	public:
	    static T* getInstancePtr()
	    {
	        if(instance_ == NULL)
	        {
	            instance_ = new T;
	        }
	        return T;
	    }
	private:
		T* instance_;
	};
	
	template <class T>
	class Singleton2
	{
	public:
	    static T* getInstancePtr()
	    {
			LockGuard();
	        if(instance_ == NULL)
	        {
	            instance_ = new T;
	        }
	        return T;
	    }
	private:
		T* instance_;
	};
	
	template <class T>
	class Singleton3
	{
	public:
	    static T* getInstancePtr()
	    {		
	        if(instance_ == NULL)
	        {
				LockGuard();
	            instance_ = new T;
	        }
	        return T;
	    }
	private:
		T* instance_;
	};
	
	template <class T>
	class Singleton4
	{
	public:
	    static T* getInstancePtr()
	    {		
	        if(instance_ == NULL)
	        {
				LockGuard();
				if(instance_ == NULL)
				{
				    instance_ = new T;
				}
	        }
	        return T;
	    }
	private:
		T* instance_;
	};

#### **总结**

Singleton 模式是设计模式中最为简单、最为常见、最容易实现，也是最应该熟悉和掌握的模式。虽然简单，但曾经也是有不少坑的，上面Singleton1、Singleton2、Singleton3这几个实现其实都是错的，具体错在哪还是比较容易发现的，而Singleton4看似不错，但其实也不是完全正确的（本文最初给出的Singleton<T>与Singleton4是一个思路），具体问题请搜索DCL（double check lock）。

单例模式最好的实现应该使用linux下的pthread_once或者使用C++11的std_once或者C++编译器进行编译。比如：

    class SomeClass     // 一定要使用C++11编译器编译
    {
    public:
        SomeClass* getInstancePtr()
        {
            static SomeClass one;
            return &one;
        }
    private:
        SomeClass();
        SomeClass(const SomeClass&);
        SomeClass& operator=(const SomeClass&);
    }
    
    
Singleton 模式经常和 Factory（ Abstract Factory） 模式在一起使用， 一般来说系统中工厂对象一般来说只需要一个。

### 2. 工厂方法模式(Factory Method)
#### **意图**

1. 定义一个用于创建对象的接口，让子类决定实例化哪一个类；
2. 使一个类的实例化延迟到其子类。

#### **问题**

一般来说有几种情况需要用到Factory Method：

1. 一套工具库或者框架实现并没有考虑业务相关的东西，在我们实现自己的业务逻辑时，可能需要注册我们自己的业务类型到框架中；
2. 面向对象中，在有继承关系的体系下，可能给最初并不知道要创建何种类型，需要在特定时机下动态创建；

#### **示例**
	
	#define TYPE_PROXY_1 		1
	#define TYPE_PROXY_2 		2
	class Proxy
	{
	public:
		virtual Proxy() {}
		int type() const { return type_; }
	private:
		int type_;
	};
	class Proxy1 : public Proxy
	{
	public:
		virtual Proxy1() {}
	private:
		// some attributes
	};
	class Proxy2 : public Proxy
	{
	public:
		virtual Proxy2() {}
	};

	class ProxyFactory
	{
	public:
	    typedef std::function<Proxy*()>     CreateCallBack;
	    typedef std::function<void(Proxy*)> DeleteCallBack;	
	public:
	    static void        registerProxy(int type, const CreateCallBack& ccb, const DeleteCallBack& dcb)
	    {
	        proxyCCB_[type] = ccb;
	        proxyDCB_[type] = dcb;
	    }
	    static Proxy* createProxy(int type)
	    {
	        auto iter = proxyCCB_.find(type);
	        if(iter!=proxyCCB_.end())
	            return iter->second();
	        return defaultCreator(type);
	    }
	    static void        deleteProxy(Proxy* proxy)
	    {
	        assert(proxy);
	        auto iter = proxyDCB_.find(proxy->type());
	        if(iter!=proxyDCB_.end())
	            iter->second(proxy);
	        else
	            delete proxy;
	    }	
	private:
	    static Proxy* defaultCreator(int type);	
	    static std::map<int, CreateCallBack>  proxyCCB_;
	    static std::map<int, DeleteCallBack>  proxyDCB_;
	};

	/*static*/ Proxy* ProxyFactory::defaultCreator(int type)
	{
	    switch (type)
	    {
	    case TYPE_PROXY_1:
	        return new Proxy1(type);
	    case TYPE_PROXY_1:
	        return new Proxy2(type);
	    }
	    return NULL;
	}
	// usage
	class Proxy3 : public Proxy
	{
	public:
		virtual Proxy3() {}
		static Proxy* create()        { return new Proxy3; } 
		static void destory(Proxy* p) { delete p; } 
	};

	ProxyFactory factory;
	factory.registerProxy(1000, &Proxy3::create, &Proxy3::destory);
	Proxy* p1 = factory.createProxy(TYPE_PROXY_1);
	Proxy* p2 = factory.createProxy(TYPE_PROXY_2);
	Proxy* p3 = factory.createProxy(1000);

#### **总结**

Factory 模式在实际开发中应用非常广泛，面向对象的系统经常面临着对象创建问题：要么是要创建的类实在是太多了， 要么是开始并不知道要实例化哪一个类。Factory 提供的创建对象的接口封装，可以说部分地解决了实际问题。

当然Factory 模式也带来一些问题， 比如没新增一个具体的 ConcreteProduct 类，都可能要修改Factory的接口，这样 Factory 的接口永远就不能封闭（Close）。 这时我们可以通过创建一个 Factory 的子类来通过多态实现这一点，或者通过对新的ConcreteProduct向Factory注册一个创建回调的函数。

### 3. 抽象工厂模式(Abstract Factory)
#### **意图**

用于创建一组相关或相互依赖的复杂对象。

#### **问题**

比如网络游戏中需要过关打怪，对于不同等级的玩家，应该生成与此相应的怪物和场景，比如不同的场景，动物，等等。

又比如一个支持多种视感标准的用户界面工具包，例如 Motif 和 Presentation Manager。不同的视感风格为诸如滚动条、窗口和按钮等用户界面“窗口组件”定义不同的外观和行为。为保证视感风格标准间的可移植性，一个应用不应该为一个特定的视感外观硬编码它的窗口组件。在整个应用中实例化特定视感风格的窗口组件类将使得以后很难改变视感风格。
![](http://i.imgur.com/MOjtARx.png)

#### **示例**

	class AbstractProductA
	{
	public:
	    virtual ~AbstractProductA();
	};
	
	class AbstractProductB
	{
	public:
	    virtual ~AbstractProductB();
	};
	
	class ProductA1: public AbstractProductA
	{
	};
	class ProductA2: public AbstractProductA
	{
	};	
	
	class ProductB1: public AbstractProductB
	{
	};
	class ProductB2: public AbstractProductB
	{
	};

	class AbstractFactory
	{
	public:
	    virtual ~AbstractFactory();
	    virtual AbstractProductA *CreateProductA() = 0;
	    virtual AbstractProductB *CreateProductB() = 0;
	};
	
	class ConcreteFactory1: public AbstractFactory
	{
	public:
	    AbstractProductA *CreateProductA() { return new ProductA1; }
	    AbstractProductB *CreateProductB() { return new ProductB1; }
	};
	class ConcreteFactory2: public AbstractFactory
	{
	public:
	    AbstractProductA *CreateProductA() { return new ProductA2; }
	    AbstractProductB *CreateProductB() { return new ProductB2; }
	};

	//usage
	int main(int argc, char *argv[])
	{
	    AbstractFactory *cf1 = new ConcreteFactory1();
	    cf1->CreateProductA();
	    cf1->CreateProductB();

	    AbstractFactory *cf2 = new ConcreteFactory2();
	    cf2->CreateProductA();
	    cf2->CreateProductB();
	}

#### **总结**

在以下情况可以使用 Abstract Factory模式

- 一个系统要独立于它的产品的创建、组合和表示时。
- 一个系统要由多个产品系列中的一个来配置时。
- 当你要强调一系列相关的产品对象的设计以便进行联合使用时。
- 当你提供一个产品类库，而只想显示它们的接口而不是实现时。

Abstract Factory 模式和 Factory 模式两者比较相似，但是还是有区别的，AbstractFactory 模式是为创建一组（有多种不同类型）相关或依赖的对象提供创建接口， 而 Factory 模式是为一类对象提供创建接口或延迟对象的创建到子类中实现。并且Abstract Factory 模式通常都是使用 Factory 模式实现的。

### 4. 建造者模式(Builder)
#### **意图**

将一个复杂对象的构建与它的表示分离，使得同样的构建过程可以创建不同的表示。

#### **问题**

对于一个大型的、复杂对象，我们希望将该对象的创建过程与其本身的表示或数据结构相分离。

当我们要创建的对象很复杂的时候（通常是由很多其他的对象组合而成），我们要将复杂对象的创建过程和这个对象的表示（展示）分离开来， 这样做的好处就是通过一步步的进行复杂对象的构建， 由于在每一步的构造过程中可以引入参数，使得经过相同的步骤创建最后得到的对象的展示不一样。

#### **示例**

	class Builder
	{
	public:
	    virtual ~Builder() {}
	    virtual void BuildPartA(const string &buildPara) = 0;
	    virtual void BuildPartB(const string &buildPara) = 0;
	    virtual void BuildPartC(const string &buildPara) = 0;
	    virtual Product *GetProduct() = 0;
	};
	
	class ConcreteBuilder: public Builder
	{
	public:
	    void BuildPartA(const string &buildPara)
	    {
	        cout << "Step1:Build PartA..." << buildPara << endl;
	    }
	    void BuildPartB(const string &buildPara)
	    {
	        cout << "Step1:Build PartB..." << buildPara << endl;
	    }
	    void BuildPartC(const string &buildPara)
	    {
	        cout << "Step1:Build PartC..." << buildPara << endl;
	    }
	    Product *GetProduct()
	    {
	        BuildPartA("pre-defined");
	        BuildPartB("pre-defined");
	        BuildPartC("pre-defined");
	        return new Product();
	    }
	};

	class Director
	{
	public:
	    Director(Builder *bld)
	    {
	        _bld = bld ;
	    }
	    void Construct()
	    {
	        _bld->BuildPartA("user-defined");
	        _bld->BuildPartB("user-defined");
	        _bld->BuildPartC("user-defined");
	    }
	private:
	    Builder *_bld;
	};

	// usage
	Director *d = new Director(new ConcreteBuilder());
    d->Construct();

另外一个例子，比如Java语言中的StringBuilder类(据说用来构造字符串对象时非常高效，相比String类)：

	StringBuilder MyStringBuilder = new StringBuilder("Your total is ");
	MyStringBuilder.AppendFormat("{0:C} ", MyInt);
	Console.WriteLine(MyStringBuilder);
	MyStringBuilder.Insert(6,"Beautiful ");
	MyStringBuilder.Remove(5,7);
#### **总结**

Builder 模式通过一步步创建对象，并通过相同的创建过程可以获得不同的结果对象（每一步的创建过程都可以绑定不同的参数）

### 5. 原型模式(ProtoType)
#### **意图**

用原型实例指定创建对象的种类，并且通过拷贝这些原型创建新的对象， 也即通过一个已存在对象来进行新对象的创建。

#### **问题**
你可以通过定制一个通用的图形编辑器框架和增加一些表示音符、休止符和五线谱的新对象来构造一个乐谱编辑器。这个编辑器框架可能有一个工具选择板用于将这些音乐对象加到乐谱中。这个选择板可能还包括选择、移动和其他操纵音乐对象的工具。用户可以点击四分音符工具并使用它将四分音符加到乐谱中。或者他们可以使用移动工具在五线谱上上下移动一个音符，从而改变它的音调。

我们假定该框架为音符和五线谱这样的图形构件提供了一个抽象的Graphics类。此外，为定义选择板中的那些工具，还提供一个抽象类Tool。该框架还为一些创建图形对象实例并将它们加入到文档中的工具预定义了一个GraphicsTool子类。但GraphicsTool给框架设计者带来一个问题。音符和五线谱的类特定于我们的应用，而GraphicsTool类却属于框架。GraphicsTool不知道如何创建我们的音乐类的实例，并将它们添加到乐谱中。我们可以为每一种音乐对象创建一个GraphicsTool的子类，但这样会产生大量的子
类，这些子类仅仅在它们所初始化的音乐对象的类别上有所不同。我们知道对象复合是比创建子类更灵活的一种选择。问题是，该框架怎么样用它来参数化GraphicsTool的实例，而这些实例是由Graphics类所支持创建的。

解决办法是让GraphicsTool通过拷贝或者“克隆”一个Graphics子类的实例来创建新的Graphics，我们称这个实例为一个原型。GraphicsTool将它应该克隆和添加到文档中的原型作为参数。如果所有Graphics子类都支持一个Clone操作，那么GraphicsTool可以克隆所有种类的Graphics。

因此在我们的音乐编辑器中，用于创建个音乐对象的每一种工具都是一个用不同原型进行初始化的GraphicsTool实例。通过克隆一个音乐对象的原型并将这个克隆添加到乐谱中，每个GraphicsTool实例都会产生一个音乐对象。

![](http://i.imgur.com/ueP1mLk.png)

#### **示例**
	
	class Prototype
	{
	public:
	    virtual Prototype *Clone() const = 0;
	};
	
	class ConcretePrototype: public Prototype
	{
	public:
	    Prototype *Clone() const
	    {
	        return new ConcretePrototype(*this);
	    }
	};

	//use
	Prototype *p = new ConcretePrototype();
    Prototype *p1 = p->Clone();
	Prototype *p2 = p->Clone();
#### **总结**

Prototype 模式通过复制原型（Prototype）而获得新对象创建的功能，这里 Prototype 本身就是“对象工厂”（因为能够生产对象）。

而且Prototype和Factory还是很相似的， Factory是由外部类负责产品的创建，而Prototype是由类自身负责产品的创建。

## 为什么需要创建性模式

首先，在编程中，对象的创建通常是一件比较复杂的事，因为，为了达到降低耦合的目的，我们通常采用面向抽象编程的方式，对象间的关系不会硬编码到类中，而是等到调用的时候再进行组装，这样虽然降低了对象间的耦合，提高了对象复用的可能，但在一定程度上将组装类的任务都交给了最终调用的客户端程序，大大增加了客户端程序的复杂度。采用创建类模式的优点之一就是将组装对象的过程封装到一个单独的类中，这样，既不会增加对象间的耦合，又可以最大限度的减小客户端的负担。

其次，使用普通的方式创建对象，一般都是返回一个具体的对象，即所谓的面向实现编程，这与设计模式原则是相违背的。采用创建类模式则可以实现面向抽象编程。客户端要求的只是一个抽象的类型，具体返回什么样的对象，由创建者来决定。

再次，可以对创建对象的过程进行优化，客户端关注的只是得到对象，对对象的创建过程则不关心，因此，创建者可以对创建的过程进行优化，例如在特定条件下，如果使用单例模式或者是使用原型模式，都可以优化系统的性能。

所有的创建类模式本质上都是对对象的创建过程进行封装。

创建型模式的目标都是相同的，即负责产品对象的创建。其中Singleton是使某一产品只有一个实例，Factory Method负责某一产品（及其子类）的创建，Abstract Factory负责某一系列相关或相互依赖产品（及相应子类）的创建，Builder模式通过一些复杂协议或者复杂步骤创建某一产品，Prototype则是通过复制自身来创建新对象。

通常来说Abstract Factory可以通过Factory来实现，且一般都是Singleton模式。

着重推荐Singleton、Factory、Abstract Factory模式，而Builder和Prototype目前我直接使用的还很少。

## 未完
接下来来模拟一个虚拟场景来演示这5种创建型模式的组合使用。假设有一个关于车辆的组装系统，目前有汽车（Car）和货车（Truck），每种车由发动机和车轮子构成（忽略其他零件），且可能有不同的发动机和车轮子，比如汽车的发动机和轮子与货车的就不一样，甚至不同类型的汽车的发动机和轮子也可能不完全一样。我将在该场景中同时使用这五种模式，以研究各模式的使用场景以及相互间的配合。

请等待下文介绍， 链接在此。

