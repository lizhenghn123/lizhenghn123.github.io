---
layout: post

title: Gearman调研及介绍

category: 分布式

tags: 开发 分布式 RPC Gearman

keywords: 开发 分布式 RPC 消息队列 Gearman

description: 本文对Gearman这一分布式任务分发平台做了调研、探索。

---

说明：以下内容是当时调研分布式任务分析、处理系统时发现的一个Gearman产品，功能还不错，使用也简单，轻量级，虽然最终因为别的原因而没有选择该产品，但还是把当时搜集的资料记录一下吧。

## 简介

现代计算环境最大的挑战之一就是工作分布和计算资源的有效利用。目前的一般趋势是，便宜且轻松地安装一台强大的机器来执行比较直观和简单的任务，但是这可能得不到最佳的总体性能和机器的最佳利用。相反，很多应用程序现在发现自己需要执行一些相当小的操作，但是可能要执行成千上万次，不需要一台强大的机器。

[Gearman](http://gearman.org/) 是 [Brad Fitzpatrick](http://brad.livejournal.com/)早期开发的一个作品，最初用Perl，后来用C重写的任务调度程序，它提供一个服务器端和多种语言的客户端接口，包括 C/Perl/Python/Java/Ruby 等。其最初的使用场景是用于LiveJournal的图片resize 功能，比较resize还是一个挺耗时的工作。

Gearman为跨一组机器分布离散的任务提供一种灵活的机制，它把工作委派给其他机器，并发的处理某项工作，且在多个调用间做负载均衡，或用来在调用其它语言的函数。

## Gearman能用来干什么
gearman可以用在各个方面，最简单就是在不同语言之间架起一座桥梁。比如你可能希望你的php程序调用一个c 函数，那么用gearman就可以实现了，当然了实际你可以通过写一个php扩展来实现同样的工作，但是比如你要php调用java,perl,或者python那么，gearman就非常棒了。 
gearman另一个应用方面是负载分担，你可以将worker放在不同的服务器（或者一些列服务器）上，比如你的php程序需要图片转换，但是不希望本地服务器有太多的这样图片转换的进程，那么你可以建立一系列服务器，在上面加载worker处理图片转换。这样你的web服务器将不受图片转换的影响，同时你得到了负载均衡的功能，因为job server会在请求到来的时候，将这个请求发给空闲的worker.同样对于多核的服务器，你可以在同一机器上创建同样数目的worker. 你可能担心，job server处于一个中心，那么这会是一个单点的瓶颈，如果死了，会怎么样？对于这样的情况，你可以运行多个job server。这样如果一个job server down了，client和worker会自动迁移到另一台job server上。

## Gearman的优缺点
优点：

1. 分布式任务分发，worker与job server，client与job server通信基于tcp的socket连接；
2. 高可用，可以使用多个server进行任务调用，一个出现故障时并不影响整个系统的使用；
3. 扩展简单，松耦合的接口和无状态的job，只需要启动一个worker，注册到Job server集群即可，新加入的worker不会对现有系统有任何的影响；
2. 解耦
3. 支持带优先级的job
3. 支持持久化
4. 支持同步调用和异步调用两种方式
5. 本身可做任务负载均衡
6. Server端也支持负载
7. 多语言支持

缺点：  

1. 版本比较老，近几年很少有更新；
2. 近来使用的人或公司不多，没有太多成熟案例（第1，第2点会导致更少的人选择该产品）；
3. 只支持一对一也即生产者-消费者模式，不支持发布订阅模式，也是一个job，多个worker处理；

不过因为简单、也好上手，所以在一些非关键业务上还是可以使用的，比如日志收集、各个机器状态的抓取、程序部署安装之类的。

## Gearman怎么样工作
一个Gearnan体系包括三个角色，一个client,一个worker，一个job server，client负责创建并发起一个job请求,job server负责找到合适的worker，worker负责执行job，事实上是worker完成了实际的任务。

![Gearman-demo](http://www.ibm.com/developerworks/cn/opensource/os-gearman/fig01.gif)

其中：

- Gearman job server : gearmand, Gearman守护进程（或作业服务器）；
- Client : 用于向 Gearman 服务提交请求的用户，也称生产者（producer ），每个Client向server请求它想要的处理功能；
- Worker： 执行实际工作的工作者，也称消费者（consumer），每个Worker向server注册它所能响应的一个或多个函数；

gearman提供一系列api从而使你的client与worker能够与job server通信，且不用考虑底层的网络实现，极大减轻了一个分布式处理平台的搭建工作。仅仅通过API即可完成一个具体业务的发起、调用、处理。  

![](http://gearman.org/img/stack.png)  

Gearman 不但可以做为任务分发，还可以做为应用方面是负载均衡，我们可以让 Workerer 放在不同的一堆服务器上，也可以启动放在同一个 CPU 的多个核上。比如，以我们常用的应用视频转换程序，但是不希望 Web 的服务器来处理视频的格式处理的过程，这时，我们就可以在这一堆服务器上进行任务分发，在上面加载 Workerer 处理视频格式处理和转换。这样对外的 web 服务器将不会被视频转换的过程影响，同时也能很多的让所有服务器负载均衡的工作来处理，也非常方便扩展，加一个机器到任务调度中心，注册成 Workerer 就行，这时 Job Server 会在请求到来的时候，将这个请求发给空闲的这个 Workerer. 另外你还可以运行多个Job Server。可以组成一个 HA 的架构，如果一个Job Server 的进程 down了，client 和 Workerer 会自动迁移到另一台Job Server上。

从上面可以看出来 Worker 是可扩展的。如果你有需要 Worker 是可以运行任意多个的。另外，我们对 Application不用过多在意，同样也是可以多个。 Application 的客户只有一个任务，就是加入任务到 Gearman 中来.

## 示例应用
该示例来自：[IBM:跨多种环境部署Gearman](http://www.ibm.com/developerworks/cn/opensource/os-gearman/index.html)，场景是使用gearman和memcached进行单词计数的统计，下面直接抄自原文。

通常有这么一些情况，您会想要对一些信息执行某些操作，但是处理在时间上不是很紧急，或者数据源和目的地之间存在一些距离（在网络上，不是地理位置上）。

考虑这样一个 web 应用程序，它在注册过程中会发送一个注册 e-mail。当用户点击 web 窗体上的 Submit 按钮时实时发送这样的 e-mail时，会有很多潜在的问题。问题到达邮件服务器或者只是在忙时提交 e-mail，都会延迟 web 应用程序。有了 Gearman，您可以将任务提交到队列，让您的一个Worker完成 e-mail 的实际处理和格式化并发送，这可以让 web 接口做出即时响应。下面是一个很好的例子，演示了在前端不需要等待响应时分派一个 background 进程。

您也可以使用 Gearman 来处理数据库和其他更新（更新的即时特点不是很重要，所以信息不必即时地写入数据库）。在这种情况下，可以充分利用现代 web 应用程序工具组中其他组件（比如 memcached）的优势。

有一个应用程序是很好的例子，它处理诸如此类的内容，比如说文档归档器，您想要从内容构建索引和其他信息。尽管已经有用于此类操作的传统队列可用，但是 Gearman 让在一组机器中扩散和分布信息变得更容易，提高了索引过程的性能。

有助于这些情况的一个要素是，与 memcached 组合使用 Gearman 的处理，以允许您提交数据，解析和处理数据，然后自动更新该信息的高速缓存版本。

在博客或其他内容管理系统中，可以使用该方式来允许更新和信息的即时发布，方法是更新内容的 memcached 版本并在后台更新数据库，或者更新数据库并在写操作完成后马上更新 memcached 客户端版本以用于显示。通过减少同步写操作的次数，两种方案都有助于减少向数据库写入内容，同时提高前端应用程序的响应性。

下面演示一个使用 memcached 的例子。Client把要被计数的字符串写入memcached，Worker使用Client提供的ID读取字符串，统计单词数量，然后将信息写回memcached。本例中使用了一个硬编码的 ID，但是也可以使用来自数据库的ID或UUID。


基于memcached和Gearman的Client.pl：

	use Gearman::Client;
	use Cache::Memcached;	
	# Set up memcached	
	my $cache = new Cache::Memcached {
	    'servers' => [
	                   '192.168.0.2:11211',
	                   ],
	};	
	# Set up Gearman	
	my $client = Gearman::Client->new;
	$client->job_servers('192.168.0.2:4730');

	# Obtain the information you want to process and generate a unique key	
	my $id = 9334;
	
	# Write some metadata	
	$cache->set(sprintf('doc-%d-srctxt',$id), 'The quick brown fox jumps over the lazy dog');
	
	my $result = $client->dispatch_background('wordcount',$id);

基于memcached和Gearman的Worker.pl：

	use Cache::Memcached;
	use Gearman::Worker;
	
	my $cache = new Cache::Memcached {
	    'servers' => [
	                   '192.168.0.2:11211',
	                   ],
	    };
	
	my $worker = Gearman::Worker->new;
	$worker->job_servers('192.168.0.2:4730');
	$worker->register_function('wordcount' => \&wordcount);
	$worker->work while 1;	
	
	sub wordcount
	{
	    my ($arg) = @_;	
	    my $id = $arg->arg;
	    print STDERR "Providing word count for ",$id,"\n";	
	    my $string = $cache->get(sprintf('doc-%d-srctxt',$id));
	
	    if (!defined($string))
	    {
	        $cache->set(sprintf('doc-%d-status',$id), 'Error: Source text not found');
	        return;
	    }
	
	    my @words = split /\s+/,$string;
	    $cache->set(sprintf('doc-%d-status',$id), 'Complete');
	    $cache->set(sprintf('doc-%d-result',$id), scalar @words);
	}
注意，在worker中，脚本使用 status 和 tagged memcached 项来保留信息；失败可以被写入 status。这允许客户机在发生暂时的失败时重新提交工作请求。

由于客户机不期待收到响应，所以需要一个单独的脚本在 memached 就绪时从它取得信息。下面演示了一个用于此目的的简单客户机脚本，它识别是否出错（并报告错误）或报告结果。

从 memcached 取得结果getresult.pl：

	use Cache::Memcached;
	
	my $cache = new Cache::Memcached {
	    'servers' => [
	                   '192.168.0.2:11211',
	                   ],
	};
	
	my $id = 9334;	
	if ((my $result = $cache->get(sprintf('doc-%d-status',$id))) =~ m/Complete/)
	{
	    print "Count is ",$cache->get(sprintf('doc-%d-result',$id),),"\n";
	}
	else
	{
	    print "Result not ready: $result\n";
	}

要使用该脚本，可运行工人脚本：$ perl Worker.pl。然后运行客户机脚本，将请求提交到队列中：$ perl Client.pl。

可以通过使用检索脚本，了解请求是否已完成。

检索脚本：

	$ perl getresult.pl
	Result not ready:
一旦结果最终可用，您就可以看到：
最终结果
	
	$ perl Client.pl
	Words 9
您可以对所有类型的数据和环境重复该脚本，并在该过程中可以包括数据库写入和恢复工作等等。

## Gearman高级使用

一个典型的部署结构图：

![](http://gearman.org/img/cluster.png)

上图中server是两台，以保持高可用性。Client自动向不同的server发起请求，每一个Client代表的任务可以是不相同的，Worker自动的向两个server请求任务，且请求的任务也可以是不同的。

## Reference
- [Gearman.org](http://gearman.org/)  
- [IBM:跨多种环境部署Gearman](http://www.ibm.com/developerworks/cn/opensource/os-gearman/index.html)
- [用 Gearman 分发 PHP 应用程序的工作负载](http://www.ibm.com/developerworks/cn/opensource/os-php-gearman/index.html)  
- [使用 Gearman 实现分布式处理](http://www.oschina.net/question/4873_11032?fromerr=Jc4zGCam)
- [金山公司利用开源的Gearman框架构建分布式图片处理平台](http://zyan.cc/dips/)
- [Gearman调研/测试/原理分析](http://www.phpboy.net/2014-05/40-gearman-instruction.html)