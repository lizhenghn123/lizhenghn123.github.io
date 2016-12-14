---
layout: post

title: Docker容器(Container)学习笔记

category: Docker

tags: [Linux, Docker, 容器] 

keywords: Linux Docker 容器

description: 本文介绍了Docker 容器的基本知识以及容器的各种命令操作实例。

---

## 容器是什么
- 容器(Container)是 Docker 的三大组件之一。   
- 容器是独立运行的一个或一组应用，以及它们的运行态环境。对应的虚拟机可以理解为模拟运行的一整套操作系统（提供了运行态环境和其他系统环境）和跑在上面的应用。
- 容器的核心为所执行的应用程序，所需要的资源都是应用程序运行所必需的，除此之外并没有其它的资源。这种特点使得Docker对资源的利用率极高，是货真价实的轻量级虚拟化。  

<!-- more --> 

在一个容器中利用ps或top来查看进程信息:

```shell
# ps  
PID   USER     TIME   COMMAND
    1 root       0:04 /bin/s6-svscan /app/gogs/docker/s6/
   39 root       0:00 s6-supervise crond
   40 root       0:00 s6-supervise gogs
   41 root       0:00 s6-supervise openssh
   42 root       0:00 s6-supervise syslogd
   43 git        3:19 /app/gogs/gogs web
   44 root       0:00 /sbin/syslogd -nS -O-
   45 root       0:00 /usr/sbin/sshd -D -f /app/gogs/docker/sshd_config
  101 root       0:00 /bin/bash
  120 root       0:00 ps
```

也可以在宿主机(Host)上运行docker ps {容器名|ID}来查看进程信息:

```shell
# docker top mygogs
UID                 PID                 PPID                C                   STIME               TTY                 TIME                CMD
root                3210                1995                0                   Nov30               ?                   00:00:04            /bin/s6-svscan /app/gogs/docker/s6/
root                3271                3210                0                   Nov30               ?                   00:00:00            s6-supervise crond
root                3272                3210                0                   Nov30               ?                   00:00:00            s6-supervise gogs
root                3273                3210                0                   Nov30               ?                   00:00:00            s6-supervise openssh
root                3274                3210                0                   Nov30               ?                   00:00:00            s6-supervise syslogd
thinkit             3275                3272                0                   Nov30               ?                   00:03:19            /app/gogs/gogs web
root                3276                3274                0                   Nov30               ?                   00:00:00            /sbin/syslogd -nS -O-
```

从上面的例子演示可以看出一个容器内运行的进程很少，基本没有额外的进程，相对于传统虚拟机来说，系统资源利用率很高！  

## 启动容器
启动容器有两种方式，一种是基于镜像新建一个容器并启动，另外一个是将在终止状态(stopped)的容器重新启动。  

**因为Docker的容器实在太轻量级了，很多时候都是可以随时删除和新创建容器的。**  

### 新建并启动
主要是用过docker run命令新建一个容器。例如下面的命令输出一个“Hello World”，之后终止容器。

```shell
[root@localhost ~]# docker run  ubuntu:16.04 /bin/echo "Hello World"
Hello World
```
这跟在本地直接执行/bin/echo	'hello	world' 几乎感觉不出任何区别。而下面的命令则在容器中启动一个bash终端，允许用户进行交互。

```shell
[root@localhost ~]# docker run -i -t ubuntu:16.04 /bin/bash
root@055c544ca4e2:/# ls
bin  boot  dev  etc  home  lib  lib64  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var
root@055c544ca4e2:/# hostname
055c544ca4e2
```

其中，-t选项让Docker分配一个伪终端（pseudo-tty）并绑定到容器的标准输入上，-i选项则让容器的标准输入保持打开。  
在交互模式下，用户可以通过所创建的终端来输入命令，修改当前容器。

当利用docker run来创建容器时，Docker在后台运行的标准操作包括：  

- 检查本地是否存在指定的镜像，不存在就从公有仓库下载
- 利用镜像创建并启动一个容器
- 分配一个文件系统，并在只读的镜像层外面挂载一层可读写层
- 从宿主主机配置的网桥接口中桥接一个虚拟接口到容器中去
- 从地址池配置一个	ip	地址给容器
- 执行用户指定的应用程序
- 执行完毕后容器被终止

### 启动已终止容器
可以利用docker	start命令直接将一个已经终止的容器启动运行。

```shell
# docker stop mygogs
# docker start mygogs
```

## 守护态运行
更多的时候，需要让容器在后台运行而不是直接把执行命令的结果输出在当前宿主机下，此时可以通过添加-d参数来实现。  
如果不使用-d参数运行容器：

```shell
# docker run ubuntu:16.04 /bin/sh -c "while true; do echo hello world; sleep 1; done"
hello world
hello world
hello world
......
```
	
容器会把输出的结果(STDOUT)打印到宿主机上面。

如果使用了-d参数运行容器： 

```shell
# docker run -d ubuntu:16.04 /bin/sh -c "while true; do echo hello world; sleep 1; done"
4aba8fe48b2e3f76a013c2935f3efb27a3f0e0470c731443751cf3051879dd53
```

使用-d参数启动后会返回一个唯一的id，也可以通过docker ps命令来查看容器信息。此时容器会在后台运行并不会把输出的结果(STDOUT)打印到宿主机上面(输出结果可以用docker logs查看)。  

**注：容器是否会长久运行是和docker run指定的命令有关，和-d参数无关。**

要获取容器的输出信息，可以通过 docker logs 命令。  

```shell
# docker logs 4aba
hello world
hello world
hello world
hello world
hello world
```

## 终止容器
可以使用docker stop {容器名|容器ID}来终止一个运行中的容器。此外当Docker容器中指定的应用终结时，容器也自动终止。例如对于上一章节中只启动了一个终端的容器，用户也可以通过exit命令或Ctrl+d来退出终端，所创建的容器立刻终止。  

```shell
# docker stop 4aba8fe48b2e
4aba8fe48b2e
```

其他：  

- 终止状态的容器可以用docker ps -a命令看到；
- 处于终止状态的容器，可以通过docker start命令来重新启动；
- docker restart 命令会将一个运行态的容器终止，然后再重新启动它；

## 进入容器
在使用-d参数时，容器启动后会进入后台。某些时候需要进入容器进行操作，有很多种方法，包括使用docker attach 命令或docker exec命令或nsenter工具等。

预先在宿主机上运行一个容器进行测试： 

```shell
# docker run -i -t -d -p 10022:22 ubuntu:16.04 /bin/bash
a061051c1067bd5eb38b788e980cea65d5b60f0bf9c74b15218ae954678bbc47
```

### attach 命令

```shell
# docker attach a061051c1067
root@a061051c1067:/# hostname
a061051c1067
```

但是使用attach命令有时候并不方便。当多个窗口同时attach到同一个容器的时候，所有窗口都会同步显示。当某个窗口因命令阻塞时,其他窗口也无法执行操作
了(在宿主机新的shell中同时attach该容器即可验证）。

### exec命令
exec是docker1.3版本之后增加的命令，使用起来更简单方便。

```shell
# docker exec -it a061051c1067 /bin/bash
root@a061051c1067:/# hostname
a061051c1067
root@a061051c1067:/# ls
bin  boot  dev  etc  home  lib  lib64  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var
```

### nsenter命令
nsenter工具在util-linux包2.23版本后包含。如果系统中util-linux包没有该命令，需要自行安装。nsenter启动一个新的shell进程(默认是/bin/bash)，同时会把这个新进程切换到和目标(target)进程相同的命名空间，这样就相当于进入了容器内部。nsenter要正常工作需要有root权限。   

为了连接到容器，你还需要找到容器的第一个进程的PID，可以通过下面的命令获取：

```shell
# PID=$(docker inspect --format "{{.State.Pid}}" a061051c1067)
# echo $PID
11979
```
	
通过这个PID，就可以连接到这个容器：

	nsenter	--target $PID --mount --uts --ipc --net --pid
	
### 通过ssh进入
这种做法需要预先在容器中运行sshd服务，然后从外面ssh进入到容器。上面启动容器时带了一个参数`-p 10022:22`，此时就可以通过10022端口ssh到容器内部：

	ssh -p 10022 <宿主机ip>

以上有几种进入到容器的做法，其中通过ssh的方式就要求容器内部启动sshd服务，违反了Docker所倡导的一个容器一个进程(或者叫一个应用)的原则；像nsenter之类的第三方工具需要我们自己安装和学习使用；而attach和exec是docker自带的命令，使用起来也比较简单。
	
## 导入和导出
如果要导出本地某个容器，可以使用docker export命令。

```shell
docker export 08658327264c > mygogs_container.tar
```

可以使用docker import从容器备份文件中再导入为镜像。

```shell
cat mygogs_container.tar | docker import - myname/mygogs:v1.0
```

*注：用户既可以使用docker load来导入镜像存储文件到本地镜像库，也可以使用docker import来导入一个容器快照到本地镜像库。这两者的区别在于容器快照文件将丢弃所有的历史记录和元数据信息（即仅保存容器当时的快照状
态），而镜像存储文件将保存完整记录，体积也要大。此外，从容器快照文件导入时可以重新指定标签等元数据信息。

## 删除容器
可以使用docker rm来删除一个处于终止状态的容器。  
如果要删除一个运行中的容器，可以添加-f参数。此时Docker会发送SIGKILL信号给该容器。

```shell
docker rm mygogs
docker rm -f mygogs
```