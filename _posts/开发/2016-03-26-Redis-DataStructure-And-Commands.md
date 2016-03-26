---
layout: post

title: Redis常用数据类型介绍、使用场景及其操作命令

category: 开发

tags: 开发 Redis

keywords: 开发 Redis

description: Redis常用数据类型及其命令介绍。

---

Redis目前支持5种数据类型，分别是：

1. String（字符串）
1. List（列表）
1. Hash（字典）
1. Set（集合）
1. Sorted Set（有序集合）

下面就分别介绍这五种数据类型及其相应的操作命令。

## 1. String（字符串）
String是简单的 key-value 键值对，value 不仅可以是 String，也可以是数字。String在redis内部存储默认就是一个字符串，被redisObject所引用，当遇到incr,decr等操作时会转成数值型进行计算，此时redisObject的encoding字段为int。

String在redis内部存储默认就是一个字符串，被redisObject所引用，当遇到incr,decr等操作时会转成数值型进行计算，此时redisObject的encoding字段为int。

### 应用场景
String是最常用的一种数据类型，普通的key/value存储都可以归为此类，这里就不所做解释了。

### 相关命令
	SET key value					设置key=value
	GET key							或者键key对应的值
	GETRANGE key start end			得到字符串的子字符串存放在一个键
	GETSET key value		  		设置键的字符串值，并返回旧值
	GETBIT key offset				返回存储在键位值的字符串值的偏移
	MGET key1 [key2..]				得到所有的给定键的值
	SETBIT key offset value			设置或清除该位在存储在键的字符串值偏移
	SETEX key seconds value			键到期时设置值
	SETNX key value					设置键的值，只有当该键不存在
	SETRANGE key offset value		覆盖字符串的一部分从指定键的偏移
	STRLEN key						得到存储在键的值的长度
	MSET key value [key value...]	设置多个键和多个值
	MSETNX key value [key value...]	设置多个键多个值，只有在当没有按键的存在时
	PSETEX key milliseconds value	设置键的毫秒值和到期时间
	INCR key						增加键的整数值一次
	INCRBY key increment			由给定的数量递增键的整数值
	INCRBYFLOAT key increment		由给定的数量递增键的浮点值
	DECR key						递减键一次的整数值
	DECRBY key decrement			由给定数目递减键的整数值
	APPEND key value				追加值到一个键
	
其中用于操作管理键的命令有：

	DEL key							如果存在删除键
	DUMP key						返回存储在指定键的值的序列化版本
	EXISTS key						此命令检查该键是否存在
	EXPIRE key seconds				指定键的过期时间
	EXPIREAT key timestamp			指定的键过期时间。在这里，时间是在Unix时间戳格式
	PEXPIRE key milliseconds		设置键以毫秒为单位到期
	PEXPIREAT key milliseconds-timestamp		设置键在Unix时间戳指定为毫秒到期
	KEYS pattern					查找与指定模式匹配的所有键
	MOVE key db						移动键到另一个数据库
	PERSIST key						移除过期的键
	PTTL key						以毫秒为单位获取剩余时间的到期键。
	TTL key							获取键到期的剩余时间。
	RANDOMKEY						从Redis返回随机键
	RENAME key newkey				更改键的名称
	RENAMENX key newkey				重命名键，如果新的键不存在
	TYPE key						返回存储在键的数据类型的值。

### 使用示例
	redis 127.0.0.1:6379> set baidu http://www.baidu
	OK
	redis 127.0.0.1:6379> append baidu .com
	(integer) 20
	redis 127.0.0.1:6379> get baidu
	"http://www.baidu.com"
	redis 127.0.0.1:6379> set visitors 0
	OK
	redis 127.0.0.1:6379> incr visitors
	(integer) 1
	redis 127.0.0.1:6379> incr visitors
	(integer) 2
	redis 127.0.0.1:6379> get visitors
	"2"
	redis 127.0.0.1:6379> incrby visitors 100
	(integer) 102
	redis 127.0.0.1:6379> get visitors
	"102"
	redis 127.0.0.1:6379> type baidu
	string
	redis 127.0.0.1:6379> type visitors
	string
	redis 127.0.0.1:6379> ttl baidu
	(integer) -1
	redis 127.0.0.1:6379> rename baidu baidu-site
	OK
	redis 127.0.0.1:6379> get baidu
	(nil)
	redis 127.0.0.1:6379> get baidu-site
	"http://www.baidu.com"

## 2. List（列表）  
Redis列表是简单的字符串列表，可以类比到C++中的std::list，简单的说就是一个链表或者说是一个队列。可以从头部或尾部向Redis列表添加元素。列表的最大长度为2^32 - 1，也即每个列表支持超过40亿个元素。

Redis list的实现为一个双向链表，即可以支持反向查找和遍历，更方便操作，不过带来了部分额外的内存开销，Redis内部的很多实现，包括发送缓冲队列等也都是用的这个数据结构。

### 应用场景
Redis list的应用场景非常多，也是Redis最重要的数据结构之一，比如twitter的关注列表、粉丝列表等都可以用Redis的list结构来实现，再比如有的应用使用Redis的list类型实现一个简单的轻量级消息队列，生产者push，消费者pop/bpop。

### 相关命令  
- BLPOP  
BLPOP key1 [key2 ] timeout   取出并获取列表中的第一个元素，或阻塞，直到有可用
- BRPOP  
BRPOP key1 [key2 ] timeout 	 取出并获取列表中的最后一个元素，或阻塞，直到有可用
- BRPOPLPUSH  
BRPOPLPUSH source destination timeout   从列表中弹出一个值，它推到另一个列表并返回它;或阻塞，直到有可用
- LINDEX  
LINDEX key index 			 从一个列表其索引获取对应的元素
- LINSERT  
LINSERT key BEFORE|AFTER pivot value  在列表中的其他元素之后或之前插入一个元素
- LLEN  
LLEN key					    获取列表的长度
- LPOP  
LPOP key						获取并取出列表中的第一个元素
- LPUSH  
LPUSH key value1 [value2]		在前面加上一个或多个值的列表
- LPUSHX  
LPUSHX key value				在前面加上一个值列表，仅当列表中存在
- LRANGE  
LRANGE key start stop			从一个列表获取各种元素
- LREM  
LREM key count value			从列表中删除元素
- LSET  
LSET key index value			在列表中的索引设置一个元素的值
- LTRIM  
LTRIM key start stop			修剪列表到指定的范围内
- RPOP  
RPOP key						取出并获取列表中的最后一个元素
- RPOPLPUSH  
RPOPLPUSH source destination	删除最后一个元素的列表，将其附加到另一个列表并返回它
- RPUSH  
RPUSH key value1 [value2]		添加一个或多个值到列表
- RPUSHX  
RPUSHX key value				添加一个值列表，仅当列表中存在

### 使用示例
	
	redis 127.0.0.1:6379> lpush list1 redis
	(integer) 1
	redis 127.0.0.1:6379> lpush list1 hello
	(integer) 2
	redis 127.0.0.1:6379> rpush list1 world
	(integer) 3
	redis 127.0.0.1:6379> llen list1
	(integer) 3
	redis 127.0.0.1:6379> lrange list1 0 3
	1) "hello"
	2) "redis"
	3) "world"
	redis 127.0.0.1:6379> lpop list1
	"hello"
	redis 127.0.0.1:6379> rpop list1
	"world"
	redis 127.0.0.1:6379> lrange list1 0 3
	1) "redis"

## 3. Hash（字典，哈希表）  
类似C#中的dict类型或者C++中的hash_map类型。

Redis Hash对应Value内部实际就是一个HashMap，实际这里会有2种不同实现，这个Hash的成员比较少时Redis为了节省内存会采用类似一维数组的方式来紧凑存储，而不会采用真正的HashMap结构，对应的value redisObject的encoding为zipmap,当成员数量增大时会自动转成真正的HashMap,此时encoding为ht。

### 应用场景  
假设有多个用户及对应的用户信息，可以用来存储以用户ID为key，将用户信息序列化为比如json格式做为value进行保存。

### 相关命令

- HDEL  
HDEL key field[field...]            删除对象的一个或几个属性域，不存在的属性将被忽略
- HEXISTS  
HEXISTS key field                   查看对象是否存在该属性域
- HGET  
HGET key field                      获取对象中该field属性域的值
- HGETALL  
HGETALL key                         获取对象的所有属性域和值
- HINCRBY  
HINCRBY key field value             将该对象中指定域的值增加给定的value，原子自增操作，只能是integer的属性值可以使用
- HINCRBYFLOAT  
HINCRBYFLOAT key field increment    将该对象中指定域的值增加给定的浮点数  
- HKEYS  
HKEYS key                           获取对象的所有属性字段
- HVALS
HVALS key                           获取对象的所有属性值
- HLEN  
HLEN key                            获取对象的所有属性字段的总数
- HMGET  
HMGET key field[field...]           获取对象的一个或多个指定字段的值
- HSET  
HSET key field value                设置对象指定字段的值 
- HMSET 
HMSET key field value [field value ...] 同时设置对象中一个或多个字段的值
- HSETNX  
HSETNX key field value               只在对象不存在指定的字段时才设置字段的值 
- HSTRLEN
HSTRLEN key field                    返回对象指定field的value的字符串长度，如果该对象或者field不存在，返回0.
- HSCAN    
HSCAN key cursor [MATCH pattern] [COUNT count]  类似SCAN命令

### 使用示例 
	
	127.0.0.1:6379> hset person name jack
	(integer) 1
	127.0.0.1:6379> hset person age 20
	(integer) 1
	127.0.0.1:6379> hset person sex famale
	(integer) 1
	127.0.0.1:6379> hgetall person
	1) "name"
	2) "jack"
	3) "age"
	4) "20"
	5) "sex"
	6) "famale"
	127.0.0.1:6379> hkeys person
	1) "name"
	2) "age"
	3) "sex"
	127.0.0.1:6379> hvals person
	1) "jack"
	2) "20"
	3) "famale"

## 4. Set（集合）  
可以理解为一堆值不重复的列表，类似数学领域中的集合概念，且Redis也提供了针对集合的求交集、并集、差集等操作。

set 的内部实现是一个 value永远为null的HashMap，实际就是通过计算hash的方式来快速排重的，这也是set能提供判断一个成员是否在集合内的原因。

### 应用场景
Redis set对外提供的功能与list类似是一个列表的功能，特殊之处在于set是可以自动排重的，当你需要存储一个列表数据，又不希望出现重复数据时，set是一个很好的选择，并且set提供了判断某个成员是否在一个set集合内的重要接口，这个也是list所不能提供的。

又或者在微博应用中，每个用户关注的人存在一个集合中，就很容易实现求两个人的共同好友功能。

### 相关命令
- SADD  
SADD key member [member ...]    添加一个或者多个元素到集合(set)里
- SACRD  
SCARD key					    获取集合里面的元素数量
- SDIFF  
SDIFF key [key ...]				获得队列不存在的元素
- SDIFFSTORE  
SDIFFSTORE destination key [key ...]    获得队列不存在的元素，并存储在一个关键的结果集
- SINTER  
SINTER key [key ...]			获得两个集合的交集
- SINTERSTORE  
SINTERSTORE destination key [key ...]	获得两个集合的交集，并存储在一个集合中
- SISMEMBER  
SISMEMBER key member			确定一个给定的值是一个集合的成员
- SMEMBERS  
SMEMBERS key					获取集合里面的所有key
- SMOVE  
SMOVE source destination member	移动集合里面的一个key到另一个集合
- SPOP  
SPOP key [count]				获取并删除一个集合里面的元素
- SRANDMEMBER  
SRANDMEMBER key [count]			从集合里面随机获取一个元素
- SREM  
SREM key member [member ...]	从集合里删除一个或多个元素，不存在的元素会被忽略
- SUNION  
SUNION key [key ...]			添加多个set元素
- SUNIONSTORE  
SUNIONSTORE destination key [key ...]	合并set元素，并将结果存入新的set里面
- SSCAN  
SSCAN key cursor [MATCH pattern] [COUNT count]	迭代set里面的元素

###使用示例 
	redis> SADD myset "Hello"
	(integer) 1
	redis> SADD myset "World"
	(integer) 1
	redis> SMEMBERS myset
	1) "World"
	2) "Hello"
	redis> SADD myset "one"
	(integer) 1
	redis> SISMEMBER myset "one"
	(integer) 1
	redis> SISMEMBER myset "two"
	(integer) 0

使用集合数据结构的典型用例是朋友名单的实现：

	redis 127.0.0.1:6379> sadd friends:leto ghanima paul chani jessica
	(integer) 4
	redis 127.0.0.1:6379> sadd friends:duncan paul jessica alia
	(integer) 3
	redis 127.0.0.1:6379> sismember friends:leto jessica
	(integer) 1   #不管一个用户有多少个朋友，我们都能高效地（O(1)时间复杂度）识别出用户X是不是用户Y的朋友
	redis 127.0.0.1:6379> sismember friends:leto vladimir
	(integer) 0
	redis 127.0.0.1:6379> sinter friends:leto friends:duncan	#我们可以查看两个或更多的人是不是有共同的朋友
	1) "paul"
	2) "jessica"
	redis 127.0.0.1:6379> sinterstore friends:leto_duncan friends:leto friends:duncan # 可以在一个新的关键字里存储结果
	(integer) 2

## 5. Sorted Set（有序集合）
Redis有序集合类似Redis集合，不同的是增加了一个功能，即集合是有序的。一个有序集合的每个成员带有分数，用于进行排序。

Redis有序集合添加、删除和测试的时间复杂度均为O(1)(固定时间，无论里面包含的元素集合的数量)。列表的最大长度为2^32- 1元素(4294967295，超过40亿每个元素的集合)。

Redis sorted set的内部使用HashMap和跳跃表(SkipList)来保证数据的存储和有序，HashMap里放的是成员到score的映射，而跳跃表里存放的是所有的成员，排序依据是HashMap里存的score,使用跳跃表的结构可以获得比较高的查找效率，并且在实现上比较简单。

### 使用场景
Redis sorted set的使用场景与set类似，区别是set不是自动有序的，而sorted set可以通过用户额外提供一个优先级(score)的参数来为成员排序，并且是插入有序的，即自动排序。当你需要一个有序的并且不重复的集合列表，那么可以选择sorted set数据结构，比如twitter 的public timeline可以以发表时间作为score来存储，这样获取时就是自动按时间排好序的。

又比如用户的积分排行榜需求就可以通过有序集合实现。还有上面介绍的使用List实现轻量级的消息队列，其实也可以通过Sorted Set实现有优先级或按权重的队列。

###相关命令  
- ZADD  
	ZADD key score1 member1 [score2 member2]	添加一个或多个成员到有序集合，或者如果它已经存在更新其分数
- ZCARD  
	ZCARD key									得到的有序集合成员的数量
- ZCOUNT  
	ZCOUNT key min max							计算一个有序集合成员与给定值范围内的分数
- ZINCRBY  
	ZINCRBY key increment member				在有序集合增加成员的分数
- ZINTERSTORE  
	ZINTERSTORE destination numkeys key [key ...]	多重交叉排序集合，并存储生成一个新的键有序集合。
- ZLEXCOUNT  
	ZLEXCOUNT key min max						计算一个给定的字典范围之间的有序集合成员的数量
- ZRANGE  
	ZRANGE key start stop [WITHSCORES]			由索引返回一个成员范围的有序集合（从低到高）
- ZRANGEBYLEX  
	ZRANGEBYLEX key min max [LIMIT offset count]返回一个成员范围的有序集合（由字典范围）
- ZRANGEBYSCORE  
	ZRANGEBYSCORE key min max [WITHSCORES] [LIMIT]	返回有序集key中，所有 score 值介于 min 和 max 之间(包括等于 min 或 max )的成员，有序集成员按 score 值递增(从小到大)次序排列
- ZRANK  
	ZRANK key member							确定成员的索引中有序集合
- ZREM  
	ZREM key member [member ...]				从有序集合中删除一个或多个成员，不存在的成员将被忽略
- ZREMRANGEBYLEX  
	ZREMRANGEBYLEX key min max					删除所有成员在给定的字典范围之间的有序集合
- ZREMRANGEBYRANK  
	ZREMRANGEBYRANK key start stop				在给定的索引之内删除所有成员的有序集合
- ZREMRANGEBYSCORE  
	ZREMRANGEBYSCORE key min max				在给定的分数之内删除所有成员的有序集合
- ZREVRANGE  
	ZREVRANGE key start stop [WITHSCORES]		返回一个成员范围的有序集合，通过索引，以分数排序，从高分到低分
- ZREVRANGEBYSCORE  
	ZREVRANGEBYSCORE key max min [WITHSCORES]	返回一个成员范围的有序集合，以socre排序从高到低
- ZREVRANK  
	ZREVRANK key member							确定一个有序集合成员的索引，以分数排序，从高分到低分
- ZSCORE  
	ZSCORE key member							获取给定成员相关联的分数在一个有序集合
- ZUNIONSTORE  
	ZUNIONSTORE destination numkeys key [key ...]	添加多个集排序，所得排序集合存储在一个新的键
- ZSCAN  
	ZSCAN key cursor [MATCH pattern] [COUNT count]	增量迭代排序元素集和相关的分数

####使用示例  

	redis 127.0.0.1:6379> zadd dbs 100 redis
	(integer) 1
	redis 127.0.0.1:6379> zadd dbs 98 memcached
	(integer) 1
	redis 127.0.0.1:6379> zadd dbs 99 mongodb
	(integer) 1
	redis 127.0.0.1:6379> zadd dbs 99 leveldb
	(integer) 1
	redis 127.0.0.1:6379> zcard dbs
	(integer) 4
	redis 127.0.0.1:6379> zcount dbs 10 99
	(integer) 3
	redis 127.0.0.1:6379> zrank dbs leveldb
	(integer) 1
	redis 127.0.0.1:6379> zrank dbs other
	(nil)
	redis 127.0.0.1:6379> zrangebyscore dbs 98 100
	1) "memcached"
	2) "leveldb"
	3) "mongodb"
	4) "redis"

## Reference  
- [http://redis.io/commands](http://redis.io/commands)
- [http://www.redis.cn/commands.html](http://www.redis.cn/commands.html)
