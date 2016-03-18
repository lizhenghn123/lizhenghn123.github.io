---
layout: post

title: Thrift框架调研

category: 开发

tags: 开发 Thrift RPC C++

keywords: 开发 Thrift RPC C++

description: 本文介绍了RPC框架的设计、具体架构和使用方法。

---

## 1. Thrift介绍
Thrift是由facebook 开发的一套跨语言的序列化框架和RPC服务框架，在2007年捐献给Apache软件基金会。对于当时的facebook来说创造thrift是为了解决facebook系统中各系统间大数据量的传输通信以及系统之间语言环境不同需要跨平台的特性，所以thrift可以支持多种程序语言，例如生成C++, Java, Python, PHP, Ruby, Erlang, Perl, Haskell, C#, Cocoa, JavaScript, Node.js, Smalltalk等语言代码。

Thrift是IDL(interface definition language)描述性语言的一个具体实现，Thrift适用于程序对程序静态的数据交换，需要先确定好他的数据结构，他是完全静态化的，当数据结构发生变化时，必须重新编辑IDL文件，代码生成，再编译载入的流程。Thrift适用于搭建大型数据交换及存储的通用工具，对于大型系统中的子系统间数据传输相对于JSON和xml无论在性能、传输大小上有明显的优势。

Thrift代码由两部分组成：编译器（在compiler目录下，采用C++编写）和服务器（在lib目录下），其中编译器的作用是将用户定义的thrift文件编译生成对应语言的代码，而服务器是事先已经实现好的、可供用户直接使用的RPC Server（当然，用户也很容易编写自己的server）。同大部分编译器一样，Thrift编译器（采用C++语言编写）也分为词法分析、语法分析等步骤，Thrift使用了开源的flex和Bison进行词法语法分析（具体见thrift.ll和thrift.yy），经过语法分析后，Thrift根据对应语言的模板（在compiler\cpp\src\generate目录下）生成相应的代码。对于服务器实现而言，Thrift仅包含比较经典的服务器模型，比如单线程模型（TSimpleServer），线程池模型（TThreadPoolServer）、一个请求一个线程（TThreadedServer）和非阻塞模型(TNonblockingServer)等。

## 2. Thrift架构  
thrift 包含有一个完整的堆栈结构用于构建服务端和客户端，下面看下它的架构图  

![](http://i.imgur.com/vvVcqv1.jpg)  
 
- 黄色部分为我们开发者实现的代码业务逻辑；
- 褐色部分是根据 Thrift 定义的服务接口描述文件生成的客户端和服务器端代码框架；
- 红色部分是根据 Thrift 文件生成代码实现数据的读写操作；
- 红色部分以下是 Thrift 的传输体系、协议以及底层 I/O 通信，使用 Thrift 可以很方便的定义一个服务并且选择不同的传输协议和传输层而不用重新生成代码。thrift服务器包含用于绑定协议和传输层基础架构，它提供阻塞、非阻塞、单线程、多线程的模式运行在服务器中。

### 2.1 基础架构  
如上图所示是thrift的协议栈整体的架构，thrift是一个客户端和服务器端的架构体系（c/s），在最上层是用户自行实现的业务逻辑代码。

第二层是由thrift编译器自动生成的代码，主要用于结构化数据的解析，发送和接收。TServer主要任务是高效的接受客户端请求，并将请求转发给Processor处理。Processor负责对客户端的请求做出响应，包括RPC请求转发，调用参数解析和用户逻辑调用，返回值写回等处理。

从TProtocol以下部分是thirft的传输协议和底层I/O通信。TProtocol是用于数据类型解析的，将结构化数据转化为字节流给TTransport进行传输。

TTransport是与底层数据传输密切相关的传输层，负责以字节流方式接收和发送消息体，不关注是什么数据类型。

底层IO负责实际的数据传输，包括socket、文件和压缩数据流等。

### 2.2 传输协议（TProtocol）
 thrift做到很好的让用户在服务器端与客户端选择对应的传输协议，总体上一般为2种传输协议：二进制或者文本，如果想要节省带宽可以采用二进制的协议，如果希望方便抓包、调试则可以选择文本协议，用户可用根据自己的项目需求选择对应的协议。

- TCompactProtocol ： 紧凑的、高效的二进制传输协议；
- TBinaryProtocol ： 基于二进制传输的协议，使用方法与TCompactProtocol 相同
- TJSONProtocol ： 使用json格式编码传输协议
- TDebugProtocol ： 使用易懂的可读的文本格式，以便于debug

**说明：这里以及以下的介绍都主要以Thrift C++版本实现为参考的，不同语言下都会有所差异。**

### 2.3 数据传输方式（TTransport）

- TSocket ： 阻塞式socker；
- THttpTransport ： 采用HTTP传输协议进行数据传输；
- TFramedTransport ： 以frame为单位进行传输，非阻塞式服务中使用；
- TFileTransport ： 以文件形式进行传输；
- TMemoryTransport ： 将内存用于I/O. java实现时内部实际使用了简单的ByteArrayOutputStream；
- TZlibTransport ： 使用zlib进行压缩， 与其他传输方式联合使用。当前无java实现；
- TBufferedTransport ： 对某个transport对象操作的数据进行buffer，即从buffer中读取数据进行传输，或将数据直接写入到buffer

### 2.4服务器网络模型（TServer）

- TSimpleServer ： 简单的单线程网络模型， 同时只能服务一个client，通常是结合TSocket用于测试；
- TThreadedServer ： 多线程网络模型，使用阻塞式IO，为每个请求创建一个线程；
- TThreadPoolServer ： 线程池网络模型，使用阻塞式IO，将每个请求都加入到线程池中；
- TNonblockingServer ： 多线程服务模型，使用非阻塞式IO（需使用TFramedTransport数据传输方式）；

## 3. Thrift特性

### 3.1 支持的特性  

- 支持IDL规则，对大部分语言来说遵守Thrift IDL语法的定义都可以生成相应代码；
- 丰富的多语言支持，比如C++、C#、Cocoa、D、Delphi、Erlang、Haskell、Java、OCaml、Perl、PHP、Python、Ruby、Smalltalk等等；  
- 支持命名空间：每一个IDL文件都有自己的命名空间，因而可以在不同的IDL文件中使用相同的名称
- 语言级别的命名空间：在IDL文件中写的命名空间标识都是对应到各自编程语言中的；
- 支持丰富的基础类型；
- 支持常量和枚举；
- 支持自定义的结构体类型，结构体中可以包含任何支持的类型；
- 支持稀疏结构体，如果可选的字段类型没有设置值或者为null，Thrift就不会将这些类型通过网络发送出去；
- 支持结构体的升级、变更，
struct evolution - The addition and removal of fields is handled without breaking existing clients by using integer identifiers for fields
- 支持容器，可以使用set、list、map容器，容器元素可以是基本类型、结构体、或者其他容器类型；
- 支持类型typedef，可以对某一类型进行typedef，比如typedef int AgeType
- 支持服务，一个service就是一组接口的集合；
- 支持服务的继承，子serveice可以实现父service的所有接口，也可以增加新的接口
- 支持异步调用：如果一个接口不需要返回值，就可以设计成异步的，这样client端程序就不用阻塞等待server端必须处理完本次调用才能返回了。而server端则可以对同一客户端发过来的多个异步调用并行执行或者乱序执行；
- 支持异常，如果执行一个函数时发生了错误，可以抛出标准或者自定义的异常；
- 支持结构体循环引用，从0.9.2版本开始支持支持，比如结构体可以包含自身，或者包含在本结构体之后才声明的结构体

### 3.2 不支持的特性
以下特性是Thrift目前不支持的：  

- 不支持结构体继承，可以通过包含来替代继承（service可以继承）  
- 没有多态机制，因为没有继承，所以也没有多态  
- 不支持重载，所有service的方法都有一个唯一的方法名  
- 不支持异构容器，一个容器中的所有元素都必须是同一类型的  
- 不支持空返回，一个函数不能直接返回null，可以通过一个包装的结构体或者marker vallue来代替

## 4. Thirft Rpc调用流程  
![](http://i.imgur.com/7YHT2nh.png)  

在Thrift调用过程中，Thrift客户端和服务器之间主要用到传输层类、协议层类和处理类三个主要的核心类，这三个类的相互协作共同完成rpc的整个调用过程。在调用过程中将按照以下顺序进行协同工作：

1. 将客户端程序调用的函数名和参数传递给协议层（TProtocol），协议层将函数名和参数按照协议格式进行封装，然后封装的结果交给下层的传输层。此处需要注意：要与Thrift服务器程序所使用的协议类型一样，否则Thrift服务器程序便无法在其协议层进行数据解析；
1. 传输层（TTransport）将协议层传递过来的数据进行处理，例如传输层的实现类TFramedTransport就是将数据封装成帧的形式，即“数据长度+数据内容”，然后将处理之后的数据通过网络发送给Thrift服务器；此处也需要注意：要与Thrift服务器程序所采用的传输层的实现类一致，否则Thrift的传输层也无法将数据进行逆向的处理；
1. Thrift服务器通过传输层（TTransport）接收网络上传输过来的调用请求数据，然后将接收到的数据进行逆向的处理，例如传输层的实现类TFramedTransport就是将“数据长度+数据内容”形式的网络数据，转成只有数据内容的形式，然后再交付给Thrift服务器的协议类（TProtocol）；
1. Thrift服务端的协议类（TProtocol）将传输层处理之后的数据按照协议进行解封装，并将解封装之后的数据交个Processor类进行处理；
1. Thrift服务端的Processor类根据协议层（TProtocol）解析的结果，按照函数名找到函数名所对应的函数对象；
1. Thrift服务端使用传过来的参数调用这个找到的函数对象；
1. Thrift服务端将函数对象执行的结果交给协议层；
1. Thrift服务器端的协议层将函数的执行结果进行协议封装；
1. Thrift服务器端的传输层将协议层封装的结果进行处理，例如封装成帧，然后发送给Thrift客户端程序；
1. Thrift客户端程序的传输层将收到的网络结果进行逆向处理，得到实际的协议数据；
1. Thrift客户端的协议层将数据按照协议格式进行解封装，然后得到具体的函数执行结果，并将其交付给调用函数；

## 5. Thrift安装及使用
请参考另一篇文章[Thrift在Windows及Linux平台下的安装和使用示例](http://cpper.info/2016/03/06/Thrift-Install-And-Example.html)。

## 6. Reference
[Thrift官网](http://thrift.apache.org/)  
[Thrift Introduction](http://jnb.ociweb.com/jnb/jnbJun2009.html?cm_mc_uid=66901142639114545779143&cm_mc_sid_50200000=1458185607)
[Thrift Features](http://thrift.apache.org/docs/features)  
[Apache Thrift - 可伸缩的跨语言服务开发框架](http://www.ibm.com/developerworks/cn/java/j-lo-apachethrift/)  
[Thrift框架调研(转)](http://peter8015.iteye.com/blog/2222109)  
[Thrift在Windows及Linux平台下的安装和使用示例](http://cpper.info/2016/03/06/Thrift-Install-And-Example.html)  
[thirft rpc 具体调用流程](http://blueskator.iteye.com/blog/2228418)