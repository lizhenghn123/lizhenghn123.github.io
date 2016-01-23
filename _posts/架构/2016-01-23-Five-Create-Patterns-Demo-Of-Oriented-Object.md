---
layout: post

title: 通过代码实例组合使用5种创建型设计模式

category: 架构

tags: 开发 技术 设计模式

keywords: 面向对象 设计模式 Gof

description: 本文通过实例代码演示5种创建型设计模式的组合使用。 本文参考自GOF名著<<设计模式-可复用面向对象软件的基础（中文版）>>， 这五种创建型设计模式分别是单例模式、工厂方法模式、抽象工厂模式、建造者模式、原型模式。

---

上次介绍了五种创建型设计模式，本文打算组合使用这五种创建型模式（单例模式、工厂方法模式、抽象工厂模式、建造者模式、原型模式），以模拟一个产品实例。

假设有一个关于车辆的组装系统，目前有汽车（Car）和货车（Truck），每种车由发动机和车轮子构成（忽略其他零件），且可能有不同的发动机和车轮子，比如汽车的发动机和轮子与货车的就不一样，甚至不同类型的汽车的发动机和轮子也可能不完全一样。

我将在该场景中同时使用这五种模式，以研究各模式的使用场景以及相互间的配合。

**这里先上一张所有类及其关系的示意图**。

![ClassOfFiveCreatePattern](http://7xq2y6.com1.z0.glb.clouddn.com/ClassOfFiveCreatePattern.png)

下面贴部分代码并解释。
	
**车的类继承体系**：

	// 汽车类
	class Vehicle
	{
	public:
	    virtual void run()   // 一般认为是先启动发动机再转动轮子,因此该虚函数有个默认实现
	    {
	        for (auto e : engines_)
	            e->fire();
	        for (auto w : wheels_)
	            w->wheel();
	    }
	
	public:
	    void attach(Engine* e)
	    {
	        engines_.push_back(e);
	    }
	    void attach(Wheel* w)
	    {
	        wheels_.push_back(w);
	    }
	
	protected:
	    std::vector<Engine*>   engines_;     // 有多个发动机的？
	    std::vector<Wheel*>    wheels_;      // 轮子肯定有多个
	};
	
	
	class Car : public Vehicle
	{
	};
	
	class Truck : public Vehicle
	{
	public:
	    virtual void run()      // 货车启动前可能要做一些简单，so...
	    {
	        std::cout << "check something before running of Truck\n";
	        Vehicle::run();
	    }
	};
	
	
	// 车的抽象工厂类，负责生产引擎、车轮等等
	class VehicleAbstructFactory
	{
	public:
	    virtual Vehicle*  createVehicle() = 0;
	    virtual Engine*   createEngine() = 0;
	    virtual Wheel*    createWheel() = 0;
	};
	
	// 车的建造者
	class VehicleBuilder
	{
	protected:
	    virtual void buildEngine(Vehicle* v) = 0;
	    virtual void buildWheel(Vehicle* v) = 0;
	public:
	    void  builder()
	    {
	        buildEngine(vehicle_);
	        buildWheel(vehicle_);
	    }
	
	    Vehicle* getVehicle() const
	    {
	        return vehicle_;
	    }
	protected:
	    Vehicle* vehicle_;
	};

	// 制造小汽车的抽象工厂类
	class CarAbstructFactory : public VehicleAbstructFactory
	{
	public:
	    CarAbstructFactory()
	        : ef_(Singleton<CarEngineFactory>::getInstancePtr())
	        , wf_(Singleton<CarWheelFactory>::getInstancePtr())
	    {
	    }
	    CarAbstructFactory(EngineFactory* ef, WheelFactory* wf)
	        : ef_(ef)
	        , wf_(wf)
	    {
	    }
	public:
	    virtual Vehicle*  createVehicle()
	    {
	        return new Car;      // FIXME 是否允许定死，也即是否允许Car的扩展，如果允许，这里也用Factory
	    }
	    virtual Engine*   createEngine()
	    {
	        return ef_->createEngine();
	    }
	    virtual Wheel*    createWheel()
	    {
	        return wf_->createWheel();
	    }
	
	private:
	    EngineFactory* ef_;
	    WheelFactory*  wf_;
	};
	
	// 制造小汽车的建造者类
	class CarBuilder : public VehicleBuilder
	{
	public:
	    CarBuilder::CarBuilder()   // 默认使用CarAbstructFactory，当然也可以传参进来
	        : vaf_(new CarAbstructFactory)
	    {
	        vehicle_ = vaf_->createVehicle();
	    }
	
	    explicit CarBuilder::CarBuilder(VehicleAbstructFactory* vaf)
	        : vaf_(vaf)
	    {
	        vehicle_ = vaf_->createVehicle();
	    }
	protected:
	    virtual void buildEngine(Vehicle* v)
	    {
	        Engine* e1 = vaf_->createEngine();	
	        v->attach(e1);
	    }
	    virtual void buildWheel(Vehicle* v)
	    {
	        Wheel* w = vaf_->createWheel();
	        v->attach(w);	
	        for (int i = 0; i < 3; ++i)    // 再来3个轮子
	        {
	            Wheel* ww = w->clone();
	            v->attach(ww);
	        }
	    }	
	private:
	    VehicleAbstructFactory* vaf_;
	};
	
	// 制造货车的抽象工厂类和建造者类分别与小汽车的抽象工厂类和建造者类相对应，且比较相似，此处不再列出来，可下载附件源代码查看。
	
**和引擎Engine相关的几个类**：


- Engine        ：抽象引擎类
- EngineFactory ：抽象引擎工厂类
- CarEngine     ：小汽车引擎类
- EngineFactory ：小汽车引擎工厂类
- TruckEngine   ：货车引擎类
- EngineFactory ：货车引擎工厂类

部分代码如下：

	class Engine
	{
	public:
	    virtual void fire() = 0;
	};
	
	class EngineFactory
	{
	public:
	    virtual Engine*      createEngine() = 0;
	};	
	
	class CarEngine : public Engine
	{
	public:
	    virtual void fire()
	    {
	        TRACE_CONSTRUCTION
	    }
	};	
	
	class CarEngineFactory : public EngineFactory, private Singleton<CarEngineFactory>
	{
	public:
	    virtual Engine*      createEngine()
	    {
	        return new CarEngine();
	    }
	};
	
	class TruckEngine : public Engine
	{
	public:
	    virtual void fire()
	    {
	        TRACE_CONSTRUCTION
	    }
	};	
	
	class TruckEngineFactory : public EngineFactory, private Singleton<TruckEngineFactory>
	{
	public:
	    virtual Engine*      createEngine()
	    {
	        return new TruckEngine();
	    }
	};

车轮类的继承体系与引擎类一样，这里不再写了，可下载附件源代码自行查看。


**如何使用**：

	template<class Builder, class AbstructFactory, class EngineFactory, class WheelFactory>
	void test_five_pattern()
	{
	    VehicleBuilder* builder = new Builder(new AbstructFactory(Singleton<EngineFactory>::getInstancePtr(), Singleton<WheelFactory>::getInstancePtr()));
	    builder->builder();
	
	    cout << "### now vehicle[" << builder->name() << "] is ready, so buidler vehicle and run it ###\n";
	    Vehicle* v = builder->getVehicle();
	    v->run();
	}
	
	int main()
	{
	    //just_test_constructor();
	    cout << "\n= = = = = = = = = = = = = = = = = = = = = = =\n";
	    test_five_pattern<CarBuilder, CarAbstructFactory, CarEngineFactory, CarWheelFactory>();
	
	    cout << "\n= = = = = = = = = = = = = = = = = = = = = = =\n";
	    test_five_pattern<TruckBuilder, TruckAbstructFactory, TruckEngineFactory, TruckWheelFactory>();
	
	    cout << "\n= = = = = = = = = = = = = = = = = = = = = = =\n";
	    //  好吧，打算造一辆高级点的车，其他不变，但是车轮子呢镶个金边什么的
	    test_five_pattern<CarBuilder, CarAbstructFactory, CarEngineFactory, mygoldcar::CarWheelwithGoldFactory>();
	
	}

**在这个示例中， 我糅合了五种创建型设计模式：单例、工厂方法、抽象工厂、原型、建造者模式。使得系统的可维护性和可扩展性得到大大增强。**

当然，也不是没有缺点的，比如设计的类过多，这也是纯面向对象设计的一个缺点吧。

如果改为使用面向对象好 + 基于对象（也即回调）的方式，可以减少一部分类型。以后有时间再写吧。

所有源代码下载： [点击下载](/public/download/FiveCreatePattern_SourceCode.zip)。
