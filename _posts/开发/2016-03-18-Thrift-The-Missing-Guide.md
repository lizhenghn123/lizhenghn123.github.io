---
layout: post

title: Thrift使用指南及语法介绍

category: 开发

tags: 开发 Thrift RPC C++

keywords: 开发 Thrift RPC C++

description: 本文介绍了RPC框架Thrift的语法以及使用指南，本文是Thrift The Missing Guide的中文翻译版。

---

# Thrift使用指南及语法介绍
## 1. 语法参考
### 1.1 类型（Types）
Thrift类型系统包括预定义的基本类型，用户自定义结构体，容器类型，异常和服务定义。  

- 基本类型（Basic types）  
	- bool: 布尔类型，true或false，占1字节
	- byte: 有符号char
	- i16: 16位有符号整数
	- i32: 32位有符号整数
	- i64: 64位有符号整数
	- double: 64位浮点数
	- binary: 字符数组
	- string: 字符串（比如二进制字符串或者其他编码过的文本）  
	
注意：Thrift并不支持无符号整形，因为在很多Thrift支持生成的目标语言中都无法将无符号类型直接转换成该语言的原生类型。

- 容器（Containers）  
Thrift容器与流行编程语言的容器类型相对应，采用Java泛型风格。它有3种可用容器类型：

	- list<t1\>：	元素类型为t1的有序表，允许元素重复；
	- set<t1\>：	    元素类型为t1的无序表，不允许元素重复；
	- map<t1,t2>：	键类型为t1，值类型为t2的kv对，键不容许重复；  
	
说明：容器中元素类型可以是除了service之外外的任何合法的Thrift类型（包括结构体和异常）。  

- 结构体类型和异常（Structs and Exceptions）  
Thrift结构体类型在概念上类似于C语言中结构体类型，Thrift结构体将会被转换成面向对象语言中的类。

异常在语法和功能上类似于结构体，一个差别是异常使用关键字exception而不是struct来声明。但他们在语义上有明显不同之处：当定义一个RPC服务时，我们可以声明一个远程方法能够抛出一个异常。

- 服务（Services）  

服务的定义方法在语义上等同于面向对象语言中的接口。Thrift编译器会产生执行这些接口的client和server stub。

### 1.2 类型重定义（Typedef)  
Thrift支持C/C++风格的类型定义，比如：
	
	typedef i32 MyInteger   // 1
	typedef Tweet ReTweet   // 2
1.	末尾没有分号
2.	struct也可以使用Typedef

### 1.3 枚举（Enums）
什么是枚举类型就不介绍了吧，Thrift也支持枚举。
	
	enum TweetType {
	    TWEET,       // 1
	    RETWEET = 2, // 2
	    DM = 0xa,    // 3
	    REPLY
	}                // 4
	
	struct Tweet {
	    1: required i32 userId;
	    2: required string userName;
	    3: required string text;
	    4: optional Location loc;
	    5: optional TweetType tweetType = TweetType.TWEET // 5
	    16: optional string language = "english"
	}
1.	枚举类型是C语言风格的，编译器默认枚举值从0开始；  
2.	当然也可以给某个常量指定一个整数值；  
3.	接受十六进制整数赋值；  
4.	末尾没有分号；  
5.	进行赋值时要使用常量的全称；  
  
注意： 和Google Protocol Buffers不同的是, Thrift 不支持嵌套的枚举类型（也不支持嵌套的结构体），枚举常量的值必须是32位的正整数。

### 1.4 注释（Comments）
Thrift支持shell风格、C语言多行风格以及Java/C++语言单行风格的注释形式。
	
	# This is a valid comment.
	
	/*
	 * This is a multi-line comment.
	 * Just like in C.
	 */
	
	// C++/Java style single-line comments work just as well.

### 1.5 名字空间（Namespacces）
Thrift中的命名空间类似于C++中的namespace或者java中的package，命名空间提供了一种组织（隔离）代码的简便方式。命名空间也可以用于防止类型定义中的名字冲突。

由于每一种语言都有自己的独特命名空间定义方式（如python里是module）, thrift允许我们针对每一种语言定制namespace的写法：　　

	namespace cpp com.example.project  // 1
	namespace java com.example.project // 2

1.	转换成namespace com { namespace example { namespace project   
2.	转换成 package com.example.project  

### 1.6 文件包含（Includes）
Thrift允许一个IDL文件包含另一个IDL文件，被包含的文件会在当前目录下查找。在使用被包含文件中的类型时要注意通过文件名前缀来访问。
	
	include "tweet.thrift"           // 1
	...
	struct TweetSearchResult {
	    1: list<tweet.Tweet> tweets; // 2
	}
1. 文件名必须用双引号引用，末尾没有分号；  
2. 注意tweet前缀；  

### 1.7 常量（constants）
Thrift允许定义跨语言使用的常量，复杂的类型和结构体可使用JSON形式表示。

	const i32 INT_CONST = 1234;    // 1
	const map<string,string> MAP_CONST = {"hello": "world", "goodnight": "moon"}
1. 分号可有可无，这里也支持16进制  

### 1.8 结构体定义（Defining Struct）
struct（一些系统中称作消息）是Thrift IDL中的基本组成块，由一系列的域组成，每个域由唯一整数标识符、类型、名字和可选的缺省值构成。比如定义一个简单的类似于Twitter服务：
	
	struct Location {                            // 5
	    1: required double latitude;
	    2: required double longitude;
	}
	
	struct Tweet {
	    1: required i32 userId;                  // 1
	    2: required string userName;             // 2
	    3: required string text;
	    4: optional Location loc;                // 3
	    16: optional string language = "english" // 4
	}
1. 每个域有一个唯一的正整数标识符；  
1. 每个字段可标识为required或optional；  
1. 结构体可以包含其它结构体；  
1. 每个字段可以设置一个默认值； 
1. 一个Thrift文件中可以定义多个结构体，并且可以引用；  

消息定义中的每个字段都有一个唯一数字标识符，这些数字标识符在传输时用来确定相应的字段，一旦我们定义的消息类型开始，这些数字标识符都不应该再改变。（即使将来可能要变更定义，比如增加字段，但最好不要改变原有的数字标识符）。

规范的struct定义中的每个字段均会使用required或者optional关键字进行标识。如果required标识的域没有赋值，Thrift将给予提示；**如果optional标识的域没有赋值，该域将不会被序列化传输**；如果某个optional标识域有缺省值而用户没有重新赋值，则该域的值一直为缺省值。

与services不同，结构体不支持继承，也就是说一个结构体不能继承另一个结构体。

### 1.9 服务定义（Defining Services）
在几个流行的序列化/反序列化框架（如protocal buffer）中，Thrift是少有的提供跨语言RPC服务的框架。这也是Thrift的一大特色。

Thrift编译器会根据你选择的目标语言为server端产生服务接口代码，为client端产生stubs代码。
	
	service Twitter {
		// 接口定义方式类似于C语言代码，它有一个返回值，参数列表和可选的异常列表
		// 注意参数列表和异常列表定义的语法与结构体中域定义的语法一致
	    void ping(),                                                             // 1
	    bool postTweet(1:Tweet tweet) throws (1:TwitterUnavailable unavailable), // 2
	    TweetSearchResult searchTweets(1:string query);                          // 3
	
		// oneway 标识符表明client端仅仅发起一个请求但不等待该请求的响应
		// oneway接口的返回类型必须是void的
	    oneway void zip()                                                        // 4
	}

1. 接口声明支持以逗号或分号结束，这一点显得有点乱；
1. 参数可以是基本类型或结构体（参数是cosnt的，且不可以作为返回值）；
1. 返回值可以是基本类型或结构体；
1. 返回值也可以是void；

注意：参数列表（异常列表）的定义同结构体完全一致；service支持继承， 一个server可以通过关键字extends继承自另一个service。

## 2. 代码生成
本段主要介绍通过thrift产生各种目标语言代码的方式。这里先从几个基本概念开始，然后介绍生成的代码是怎么样组织的，进而帮助我们理解如何更有效的使用thrift。
### 2.1 概念

#### 2.1.1 Thrift的网络架构
	
	+-------------------------------------------+
	| cGRE                                      |
	| Server                                    |
	| (single-threaded, event-driven etc)       |
	+-------------------------------------------+
	| cBLU                                      |
	| Processor                                 |
	| (compiler generated)                      |
	+-------------------------------------------+
	| cGRE                                      |
	| Protocol                                  |
	| (JSON, compact etc)                       |
	+-------------------------------------------+
	| cGRE                                      |
	| Transport                                 |
	| (raw TCP, HTTP etc)                       |
	+-------------------------------------------+
#### 2.1.2 Transport
Transport层提供了简单对网络层进行数据读写的抽象层，这使得transport层与系统其它部分（如：序列化/反序列化）中解耦。以下是Transport层提供的一些方法：

- open
- close
- read
- write
- flush

In addition to the Transport interface above, Thrift also uses a ServerTransport interface used to accept or create primitive transport objects. As the name suggest, ServerTransport is used mainly on the server side to create new Transport objects for incoming connections.
除了以上几个接口，Thrift使用ServerTransport接口接收或创建基本的transport对象。正如其名，ServerTransport用在server端，为即将到来的client连接创建Transport对象。

- open
- listen
- accept
- close

这也有一些对支持thrift的编程语言的可用传输协议：

- file: 对硬盘上的文件进行读写
- http: http协议
#### 2.1.3 Protocol  
Protocol抽象层定义了一种将内存中数据结构映射成可进行网络传输数据格式的机制。换句话说，Protocol层定义了datatype怎样使用底层的Transport对类型进行编解码。因此，Protocol的实现要给出编码机制并负责对数据进行序列化。协议的编码格式有JSON、XML、纯文本、压缩的二进制等等。  
Protocol接口的定义如下：
	
	writeMessageBegin(name, type, seq)
	writeMessageEnd()
	writeStructBegin(name)
	writeStructEnd()
	writeFieldBegin(name, type, id)
	writeFieldEnd()
	writeFieldStop()
	writeMapBegin(ktype, vtype, size)
	writeMapEnd()
	writeListBegin(etype, size)
	writeListEnd()
	writeSetBegin(etype, size)
	writeSetEnd()
	writeBool(bool)
	writeByte(byte)
	writeI16(i16)
	writeI32(i32)
	writeI64(i64)
	writeDouble(double)
	writeString(string)
	
	name, type, seq = readMessageBegin()
	                  readMessageEnd()
	name = readStructBegin()
	       readStructEnd()
	name, type, id = readFieldBegin()
	                 readFieldEnd()
	k, v, size = readMapBegin()
	             readMapEnd()
	etype, size = readListBegin()
	              readListEnd()
	etype, size = readSetBegin()
	              readSetEnd()
	bool = readBool()
	byte = readByte()
	i16 = readI16()
	i32 = readI32()
	i64 = readI64()
	double = readDouble()
	string = readString()
Thrift Protocols是为流式而设计的，因此也没有明确的帧的概念。例如，也就是说在我们序列化一个类型时，并不需要知道其中string字符串的长度或者list中每一项的值（it is not necessary to know the length of a string or the number of items in a list before we start serializing them.）。  

下面是一些大部分thrift主要支持的语言都可以使用的protocol：  

- binary ： 简单的二进制编码，一个字段的长度和类型后面再跟上该字段的实际值
- compact ： 具体见[THRIFT-110](https://issues.apache.org/jira/browse/THRIFT-110)
- Json：

#### 2.1.4 Processor
Processor封装了从输入数据流中读数据和向输出流中写数据的操作。读写数据流都可以用Protocol对象表示。Processor的接口非常简单:

	interface TProcessor {
	    bool process(TProtocol in, TProtocol out) throws TException
	}

与服务(service)相关的processor实现由thrift 编译器产生。Processor本质上就是从网络中读取数据（使用输入protocaol），将处理委托给handler（由用户实现），最后将响应结果写到网络上（使用输出protocol）。
#### 2.1.5 Server
Server将以上所有特性集成在一起：

- 创建一个transport对象
- 为transport对象创建输入输出protocol
- 基于输入输出protocol创建processor
- 等待连接请求并将之交给processor处理

接下来我们讨论下针对具体语言的生成代码，除非另外说明，否则本节之后所有内容都假设使用下面的Thrift IDL。  
示例IDL ：
	
	namespace cpp thrift.example
	namespace java thrift.example
	
	enum TweetType {
	    TWEET,
	    RETWEET = 2,
	    DM = 0xa,
	    REPLY
	}
	
	struct Location {
	    1: required double latitude;
	    2: required double longitude;
	}
	
	struct Tweet {
	    1: required i32 userId;
	    2: required string userName;
	    3: required string text;
	    4: optional Location loc;
	    5: optional TweetType tweetType = TweetType.TWEET;
	    16: optional string language = "english";
	}
	
	typedef list<Tweet> TweetList
	
	struct TweetSearchResult {
	    1: TweetList tweets;
	}
	
	exception TwitterUnavailable {
	    1: string message;
	}
	
	const i32 MAX_RESULTS = 100;
	
	service Twitter {
	    void ping(),
	    bool postTweet(1:Tweet tweet) throws (1:TwitterUnavailable unavailable),
	    TweetSearchResult searchTweets(1:string query);
	    oneway void zip()
	}
### 2.2 Java
#### 2.2.1 产生的文件  
- 一个单独的文件（Constants.java）包含所有的常量定义；
- 每个结构体，枚举或者服务各占一个文件；   
		
我们查看一个示例idl生成后的文件列表：  

	$ tree gen-java
	`-- thrift
	    `-- example
	        |-- Constants.java
	        |-- Location.java
	        |-- Tweet.java
	        |-- TweetSearchResult.java
	        |-- TweetType.java
	        `-- Twitter.java
#### 2.2.2 类型  
thrift将各种基本类型和容器类型映射到java语言中的类型，比如：
	- bool: boolean
	- binary: byte[]
	- byte: byte
	- i16: short
	- i32: int
	- i64: long
	- double: double
	- string: String
	- list<t1>: List<t1>
	- set<t1>: Set<t1>
	- map<t1,t2>: Map<t1, t2>

如入我们看到的那样，这种映射很直观，而且大部分情况下都是一一对应的。不过也没什么奇怪的，因为Thrift项目最初就是以Java为主要的目标语言的。

#### 2.2.3 Typedefs  
Java语言中对typedef没有提供任何原生支持，所以如果在Thrift IDL中使用了typedef，那么生成的java代码中会直接替换成typedef前的原始类型。也就是说即使想typedef TypeA TypeB， 但在生成的java代码中，所有使用TypeB类型的地方都会用TypeA代替。像上面的IDL例子产生的Java代码中，TweetSearchResult会被替换成list<Tweet> tweets

#### 2.2.4 Enums  
Thrift将枚举类型映射成java的枚举类型。我们可以使用geValue方法获取枚举的值(通过TEnum接口)。此外，编译器会产生一个findByValue方法用来获取枚举对应的数值。这比利用java中枚举类型的特性有更强的鲁棒性。

#### 2.2.5 Constants  
Thrift把所有的常量都放在一个叫Constants的public类中，每个常量修饰符是public static final。任何基本类型的常量定义都是支持的。

### 2.3 C++
#### 2.3.1 产生的文件

- 所有的常量都存放在一个单一的.cpp/h文件对中；
- 所有的类型定义（枚举、结构体）存放在另一个.cpp/h文件对中；
- 每个service都有自己的.cpp/h文件对；

我们查看一个示例idl生成后的文件列表：

	$ tree gen-cpp
	|-- example_constants.cpp
	|-- example_constants.h
	|-- example_types.cpp
	|-- example_types.h
	|-- Twitter.cpp
	|-- Twitter.h
	`-- Twitter_server.skeleton.cpp
#### 2.3.2 类型  

Thrift将很多基本类型和容器类型映射到C++语言中的类型，比如:

- bool: bool
- binary: std::string
- byte: int8_t
- i16: int16_t
- i32: int32_t
- i64: int64_t
- double: double
- string: std::string
- list<t1>: std::vector<t1>
- set<t1>: std::set<t1>
- map<t1,t2>: std::map<T1, T2>

### 2.4 其他语言
比如Python、Ruby、Javascript等等，这里不再一一介绍了。

## 3. 最佳实践
### 3.1 版本/兼容性
我们使用的协议可能会随着时间而变更，如果一个已经存在的消息类型不再符合我们的需求，比如打算为消息格式添加一个额外字段，但又想继续使用之前旧的thrift 消息格式生成的代码，这对thrift来说就很简单，而且不需要更改当前使用的任何代码，而仅仅需要满足以下规则：

- 绝不要修改thrift idl中已经存在字段的整数编号；
- 任何新添加的字段需要设置成optional。这就意味着任何使用你的“旧”消息格式的代码序列化的消息可以被你的新代码所解析，因为它们不会丢掉任何required的元素。你应该为这些元素设置合理的默认值，这样新的代码就能够正确地与老代码生成的消息交互了。类似地，你的新代码创建的消息也能被你的老代码解析（老的二进制程序在解析的时候只是简单地将新字段忽略）。然而，未知的字段是不会被抛弃的，如果之后消息被序列化，未知的字段会随之一起被序列化——所以，如果消息传到了新代码那里，则新的字段仍然可用；
- 非required字段可以删除，只要它的整数编号不会被其他字段重复使用（更好的做法是重命名该字段，比如名字前面可添加“OBSOLETE_”以防止其他字段使用它的整数编号；
- 改变默认值通常是没问题的，但需要记着默认值是不会发送到网络对端的。如果你的程序接收到的消息中某一字段没有设置值，你的程序会读取定义在你程序使用的thrift协议版本下的默认值，而不会读取发送端协议版本下的默认值；
 
## Reference
[thrift-missing-guide](http://diwakergupta.github.io/thrift-missing-guide/)  
