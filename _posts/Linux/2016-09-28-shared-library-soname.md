---
layout: post

title: linux下动态库版本(so-name)的组织

category: 开发

tags: 开发 

keywords: 开发 动态库 so-name

description: linux下动态库版本(so-name)的组织

---

由于动态链接的灵活性，使得程序本身和程序的依赖库可以分别独立开发和更新，因此目前不论Windows还是Linux系统下都大量使用动态链接技术。这也导致系统里有很多动态库(dll/so)，像类Unix系统下，可能会存在多个版本的同一动态库，如果不能很好的将这些动态库组织起来，就会给系统维护、升级造成很大的问题。

接下来主要介绍Linux系统下的动态库管理。

动态库又叫共享库，即Shared Library，可以被多个程序共享使用。通过Gcc编译时需要带上参数-fPIC。

## 共享库兼容性 

共享库的开发者一般会不停的更新共享库的版本，比如修正bug、增加新功能、改进性能等等。比如当程序A依赖于libfoo.so，而libfoo.so的开发者完成了一个新版本之后，理论上程序A只需要将新版本的libfoo.so替换掉旧版即可使用，这也是共享库的优点。不过共享库的更新也可能会导致接口的更改或删除，这有可能导致原先依赖于该共享库的程序无法更新。

共享库的更新可以分为两类：

- 兼容性更新  
所有的更新都只是在原有的共享库基础上增加一些内容，所有原接口都保持不变。

- 不兼容更新
更新可能改变了原有接口，导致依赖该原有接口的程序在更新后无法运行或者运行不正常。

这里的接口即指二进制接口，即ABI（Application Binary Interface）。

## 共享库版本命名
由于共享库存在这样那样的兼容性问题，那么保证共享库在系统中的兼容性，保证依赖于他们的应用程序能够正常运行是必须要解决的问题。有几种办法可用于解决共享库的兼容性问题，其中之一就是使用共享库版本的方法。

比如Linux下有一套规则来命名系统中都每一个共享库，它规定共享库的文件命名规则必须如下：

	libname.so.x.y.z

最前面使用"lib"前缀，中间是库的名字、后缀以".so"表示，在最后面跟着三个数字组成的版本号。其中：

- x  
主版本号，表示库的重大升级，不同主版本号之间的库是不兼容的，依赖于旧本地主版本号的程序必须要做出改动相应改动、重新编译，然后才可以在新版的共享库中运行；或者系统必须保留旧版的共享库，使得那些依赖于旧版共享库的程序能够正常运行
- y  
次版本号，表示库的增量升级，即增加一些新的接口符号，且保持原有的符号不变。在主版本号相同的情况下，高的次版本号的库向后兼容低的次版本号的库。一个依赖于旧的次版本号共享库的程序，可以在新的次版本号共享库中运行，因为新版中保留了原来所有的接口，并且不改变它们的定义和含义。
- z

或者按另外一种解释：

x ： current，表示当前库输出的接口的数量 ;
y ： revision，表示当前库输出接口的修改次数 ;
z ： age，表示当前库支持先前的库接口的数量，例如 age为 2，表示它可以和支持当前库接口的执行文件，或者支持前面两个库接口的执行文件进行链接。**所以 age 应该总是小于或者等于 current。**

例如我机器中hiredis库的命名如下：
	
	/usr/local/lib/libprotobuf.so -> libprotobuf.so.8
	/usr/local/lib/libprotobuf.so.8 -> libprotobuf.so.8.0.0

## 通过libtool创建共享库版本
在不同的系统中建立动态链接库的方法有很大的差别，这主要是因为每个系统对动态链接库的看法和实现并不相同，以及编译器对动态链接库支持的选项也不太一样。对于开发人员，如果尝试将使用动态库的软件在这些系统之间移植，需要参考枯涩难懂的系统手册，以及修改相应的 Makefile，这一工作是乏味的，并且具有一定的难度。  

使用 GNU Libtool 可以容易的在不同的系统中建立动态链接库。它通过一个称为 Libtool 库的抽象，隐藏了不同系统之间的差异，给开发人员提供了一致的的接口。对于大部分情况，开发人员甚至不用去查看相应的系统手册，只需要掌握 GNU Libtool 的用法就可以了。并且，使用 Libtool 的 Makefile 也只需要编写一次就可以在多个系统上使用。

Libtool 的库版本通过参数`-version-info current:revision:age`指定，例如下面的例子 :  

	libtool --mode=link gcc -l libcompress.la -version-info 0:1:0
如果没有指定，默认版本是 0.0.0。  

通过 -version-info 指定的版本信息，生成的版本号计算公式如下：  

	libcompress.so.(current-age).age.revision

示例（前面是）：  

	current:revision:age  				so-name
			1:4:1    		---> 		0.1.4
			2:4:1    		---> 		1.1.4
			3:4:1    		---> 		2.1.4
			3:5:2    		---> 		1.2.5

注意：
- 应该尽可能少的更新库版本号，尤其是不能强行将库版本号和软件发行号保持一致，下面是更新库版本号的几个策略 :
- 如果修改了库的源代码，那么应该增加 revision。这是当前接口的新的修订版本。
- 如果改变了接口，应该增加 current，将 revision重置为 0。这是接口的新版本。
- 如果新接口是前面接口的超集 ( 前面的接口还是可用 )，那么应该增加 age。这是一个向后兼容的版本。
- 如果新接口删除了前面接口的元素，那么应该将 age重置为 0。这是一个新的，但是不向后兼容的版本。

**避免版本信息：**

有些动态链接库，例如可动态加载模块，不需要版本号，这时可使用 Libtool 的 -avoid-version选项，例如下面的命令 :  

	libtool --mode=link gcc -o libcompress.la compress.lo -rpath /tmp -avoid-version
将只会创建一个 .so 结尾的动态链接库，而没有 .0.0.0 这样的版本后缀。
## 参考
- <<程序员的自我修养-链接、装载与库（俞甲子 石凡 潘爱民 著）>>
- [使用 GNU Libtool 创建库](https://www.ibm.com/developerworks/cn/aix/library/1007_wuxh_libtool/)