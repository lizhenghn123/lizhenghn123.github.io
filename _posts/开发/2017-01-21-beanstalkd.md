---
date: 2017-01-21
layout: post

title: 消息中间件beanstalkd的学习研究

category: 开发

tags: 开发 

keywords: 开发 beanstalkd 消息队列 消息中间件 分布式

description: 消息中间件beanstalkd的学习研究.

---
## Beanstalkd 介绍
> “(Beanstalkd) is a simple, fast workqueue service. Its interface is generic, but was originally designed for reducing the latency of page views in high-volume web applications by running time-consuming tasks asynchronously.” 

同RabbitMQ，ZeroMQ相比，beanstalkd是一个快速的、通用目的的、更加轻量级的消息队列。 beanstalkd的最初设计意图是在高并发的网络请求下，通过异步执行耗时较多的请求，及时返回结果，减少请求的响应延迟。支持过有9.5 million用户的Facebook Causes应用。后来开源，现在有PostRank大规模部署和使用，每天处理百万级任务。    

它支持优先级队列(priority queue)、延迟(delay)、超时重发(time-to-run)和预留(buried)，能够很好的支持分布式的后台任务和定时任务处理。  

Beanstalkd的job状态多样化，支持任务优先级 (priority), 延时 (delay), 超时重发 (time-to-run) 和预留 (buried), 能够很好的支持分布式的后台任务和定时任务处理。

它的内部采用libevent，服务器-客户端之间采用类似Memcached的轻量级通讯协议，因此性能很高；尽管是内存队列，beanstalkd提供了binlog机制，当重启beanstalkd，当前任务的状态能够从记录的本地binlog中恢复。 

<!-- More -->
## Beanstalkd 中的重要概念

### tube（管道） 
类似于topic，一个Beanstalkd可以支持多个tube，每个tube有自己的producer/worker，tube之间相互不影响。一个job的生命周期永远都会在同一个tube中。 

### job(任务)
Beanstalkd 用任务 (job) 代替消息 (message) 的概念。与消息不同，任务有一系列状态：

![Beanstalkd中Job的状态](http://ww2.sinaimg.cn/mw600/68c3cad3jw1dpsqabts9dj.jpg "Beanstalkd中Job的状态")

- READY - 需要立即处理的任务，当延时 (DELAYED) 任务到期后会自动成为当前任务；
- DELAYED - 延迟执行的任务, 当消费者处理任务后, 可以用将消息再次放回 DELAYED 队列延迟执行；
- RESERVED - 已经被消费者获取, 正在执行的任务。Beanstalkd 负责检查任务是否在 TTR(time-to-run) 内完成；
- BURIED - 保留的任务: 任务不会被执行，也不会消失，除非有人把它 "踢" 回队列；
- DELETED - 消息被彻底删除。Beanstalkd 不再维持这些消息。

### 任务优先级 (priority)
job可以有0~2^32个优先级，0代表最高优先级，小于1024的优先级beanstalkd认为是urgent。beanstalkd使用最大最小堆来实现优先级排序，任何时刻调用reserve命令，拿到的都是优先级最高的job，时间复杂度是O(logN)。 

- 延时任务 (delay)  
有两种方式可以延时执行任务(job): 生产者发布任务时指定延时(put with delay)；或者当任务处理完毕后, 消费者再次将任务放入队列延时执行(release with delay)。这种机制可以实现分布式的 java.util.Timer，这种分布式定时任务的优势是：如果某个消费者节点故障，任务超时重发 (time-to-run) 能够保证任务转移到另外的节点执行。
 
- 任务超时重发 (time-to-run)  
Beanstalkd 把任务返回给消费者以后，消费者必须在预设的 TTR (time-to-run) 时间内发送 delete / release/ bury 改变任务状态；否则 Beanstalkd 会认为消息处理失败，然后把任务交给另外的消费者节点执行。如果消费者预计在 TTR (time-to-run) 时间内无法完成任务, 也可以发送 touch 命令, 它的作用是让 Beanstalkd 从系统时间重新计算 TTR (time-to-run).
 
- 任务预留 (buried)  
如果任务因为某些原因无法执行, 消费者可以把任务置为 buried 状态让 Beanstalkd 保留这些任务。管理员可以通过 peek buried 命令查询被保留的任务，并且进行人工干预。简单的, kick <n> 能够一次性把 n 条被保留的任务踢回队列。

### Beanstalkd 协议
Beanstalkd 采用类 memcached 协议, 客户端通过文本命令与服务器交互。这些命令可以简单的分成三组: 
 
生产者用 use 选择一个管道 (tube), 然后用 put 命令向管道发布任务 (job)：  

    生产类 - use <tube> / put <priority> <delay> <ttr> [bytes]:  

消费者用 watch 选择多个管道 (tube), 然后用 reserve 命令获取待执行的任务，这个命令是阻塞的。客户端直到有任务可执行才返回。当任务处理完毕后, 消费者可以彻底删除任务 (DELETE), 释放任务让别人处理 (RELEASE), 或者保留 (BURY) 任务：

    消费类 - watch <tubes> / reserve / delete <id> / release <id> <priority> <delay> / bury <id> / touch <id>

用于维护管道内的任务状态, 在不改变任务状态的条件下获取任务。可以用消费类命令改变这些任务的状态。
被保留 (buried) 的任务可以用 kick 命令 "踢" 回队列：

    维护类 - peek job / peek delayed / peek ready / peek buried / kick <n>

更多协议介绍可以点此查看：https://raw.github.com/kr/beanstalkd/master/doc/protocol.txt。

### 如何生产和消费
生产者通过 PUT 命令来产生一条消息, 命令格式如下:
    
    put <pri> <delay> <ttr> <bytes>\r\n
    <data>\r\n

- delay = 0，进入就绪(READY)队列, 可以直接被消费。
- dealy > 0, 进入延时队列(DELAYED), 等到延时时间到了之后自动迁移就绪队列。

消费者通过 RESERVE 命令从就绪队列取出一个任务, 格式如下:
    
    reserve\r\n

任务状态会从 READY 变为 RESERVED(预定)，其他人就无法获取。 PUT 产生消息的时候，携带了 ttr(time to run)，如果这个时间内，消费者没有发送 delete, release 或者 buried 命令。 任务会自动回到 READY 状态，其他人可以继续获取。其中：  

- 消费者返回 delete 命令，这个任务就从此消失
- 消费者返回 buried 命令, 这个任务就进入休眠状态
- 消费者返回 release 命令或者不返回，就回到 READY/DELAYED 状态，可以重新被消费
- 休眠(BURIED)状态的任务，可以通过 kick 命令让任务回到 READY 队列中去。

## Beanstalkd 的一些应用场景
- 延时系统  
比如延迟20分钟发送短信，在投放的时候就设定一定的延迟时间值，让任务在延迟时间到了之后进入ready队列，等待worker预订处理。

- 轮询系统  
如下图，一个被投放的任务，在延迟时间过后需要再检查一遍状态，如果不符合，继续释放（release with delay）为延迟投放状态（DELAYED），直到时间过期之后，再次进入ready队列，被worker预订，进行一些逻辑判断，比如微信银行卡退款是否成功，如果成功，删除该任务，如果没成功，继续释放（release with delay）为延迟投放状态。

![](/public/img/beanstalkd_job_status.png)

## Beanstalkd 使用 
运行Beanstalkd server端：  

    beanstalkd -l 0.0.0.0 -p 11300 -b /var/lib/beanstalkd/binlog

其中 -b 开启binlog进行持久化，断电后重启会自动恢复任务。

使用php进行客户端开发调用，可以使用这个简单的PHP Client：https://github.com/davidpersson/beanstalk。
发送任务：  

```php
<?php
//发送任务

require_once 'src/Socket/Beanstalk.php';

//实例化beanstalk
$beanstalk = new Socket_Beanstalk(array(
    'persistent' => false, //是否长连接
    'host' => 'ip地址',
    'port' => 11600,  //端口号默认11300
    'timeout' => 3    //连接超时时间
));

if (!$beanstalk->connect()) {
    exit(current($beanstalk->errors()));
}
//选择使用的tube
$beanstalk->useTube('test');
//往tube中增加数据
$put = $beanstalk->put(
    23, // 任务的优先级.
    0,  // 不等待直接放到ready队列中.
    60, // 处理任务的时间.
    'hello, beanstalk' // 任务内容
);

if (!$put) {
    exit('commit job fail');
}

$beanstalk->disconnect();
```

处理任务：  

```php
<?php
require_once 'src/Socket/Beanstalk.php';
//实例化beanstalk
$beanstalk = new Socket_Beanstalk(array(
    'persistent' => false, //是否长连接
    'host' => 'ip地址',
    'port' => 11600,  //端口号默认11300
    'timeout' => 3    //连接超时时间
));

if (!$beanstalk->connect()) {
    exit(current($beanstalk->errors()));
}
//查看beanstalkd状态
//var_dump($beanstalk->stats());

//查看有多少个tube
//var_dump($beanstalk->listTubes());

$beanstalk->useTube('test');

//设置要监听的tube
$beanstalk->watch('test');

//取消对默认tube的监听，可以省略
$beanstalk->ignore('default');

//查看监听的tube列表
//var_dump($beanstalk->listTubesWatched());

//查看test的tube当前的状态
//var_dump($beanstalk->statsTube('test'));


while (true) {
    //获取任务，此为阻塞获取，直到获取有用的任务为止
    $job = $beanstalk->reserve(); //返回格式array('id' => 123, 'body' => 'hello, beanstalk')

    //处理任务
    $result = doJob($job['body']);

    if ($result) {
        //删除任务
        $beanstalk->delete($job['id']);
    } else {
        //休眠任务
        $beanstalk->bury($job['id']);
    }
    //跳出无限循环
    if (file_exists('shutdown')) {
        file_put_contents('shutdown', 'beanstalkd在'.date('Y-m-d H:i:s').'关闭');
        break;
    }
}
$beanstalk->disconnect();
```

## Beanstalkd 不足 
1. 没有提供主从同步+故障切换机制，在应用中有可能成为单点的风险。在实际应用中，可以使用数据库为job提供持久化存储；
2. 和Memcached类似，Beanstalkd依赖libevent单线程事件分发机制，不能有效的利用多核cpu的性能。这一点可以通过单机部署多个实例克服；

## Reference
- [Beanstalkd 介绍](http://www.programgo.com/article/74323032891/;jsessionid=5A3500355E23354B4EEEC5B5F0069DBD)
- [基于beanstalkd的消息队列实践](http://www.fzb.me/2015-5-2-beanstalkd-in-action.html)
- [Beanstalkd中文协议解读](http://www.fzb.me/2015-3-21-beanstalkd-protocol-chinese-version.html)
- [Beanstalkd FAQ 中文版](http://www.fzb.me/2015-7-31-beanstalkd-faq.html)
- [beanstalk和rabbitmq区别](https://www.zhihu.com/question/21062715/answer/59800055)
