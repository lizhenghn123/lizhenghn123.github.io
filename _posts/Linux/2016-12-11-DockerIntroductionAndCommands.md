---
layout: post

title: Docker的简单介绍及常用命令

category: Docker

tags: Linux Docker 

keywords: Linux Docker 

description: Docker的入门介绍、以及常用的Docker命令

---

## Docker 介绍
Docker 是一个基于Linux容器(LXC-linux container)的高级容器引擎，基于go语言开发，源代码托管在 Github 上, 遵从Apache2.0协议开源。Docker的目标是实现轻量级的操作系统虚拟化解决方案。

学习Docker首先要了解几个概念：

- 镜像(image)—Docker的镜像和常见的系统ISO镜像类似，包含了应用程序的信息；  
- 容器(container)—容器相当于一个可以运行起来的虚拟机，应用程序运行在容器中,Docker运行在“Docker”上；  
- 仓库(hub)—仓库是存放镜像的地方，有类似git的版本控制，同样分为公开仓库(Public)和私有仓库(Private)两种形式；

Docker是CS架构，主要由下面三部分组成：

<!--more-->
- Docker daemon: 运行在宿主机上，Docker守护进程，用户通过Docker client(Docker命令)与Docker daemon交互
- Docker client: Docker 命令行工具，是用户使用Docker的主要方式，Docker client与Docker daemon通信并将结果返回给用户，Docker client也可以通过socket或者RESTful api访问远程的Docker daemon
- Docker hub/registry: 共享和管理Docker镜像，用户可以上传或者下载上面的镜像，官方地址为[registry.hub.docker.com](https://registry.hub.docker.com)，当然也可以搭建自己私有的Docker registry。

Docker支持大部分的Linux发行版，通过使用Docker容器，就可以在不同的操作系统，不同的机器上运行自己的应用，不用关心硬件、运行环境之类的配置，应用程序的迁移变得非常简单。

## Docker和传统虚拟化技术的对比
相比传统虚拟机技术，Docker资源占用少，启动更快，很大的方便了项目的部署和运维。  
Docker是在操作系统层面上实现虚拟化，复用本地主机的操作系统，传统方式是在硬件的基础上，虚拟出多个操作系统，然后在系统上部署相关的应用。  
下面的这张图片参考相关博文，很形象的说明了Docker和VM之类的传统虚拟化技术的区别：

![](http://images2015.cnblogs.com/blog/524341/201512/524341-20151207170555965-2026411978.png "传统虚拟机架构") 
传统虚拟机架构

![](http://images2015.cnblogs.com/blog/524341/201512/524341-20151207170601855-2108092104.png "Docker架构")  
Docker架构

VM是一个运行在宿主机之上的完整的操作系统，VM运行自身操作系统会占用较多的CPU、内存、硬盘资源。Docker不同于VM，只包含应用程序以及依赖库，基于libcontainer运行在宿主机上，并处于一个隔离的环境中，这使得Docker更加轻量高效，启动容器只需几秒钟之内完成。由于Docker轻量、资源占用少，使得Docker可以轻易的应用到构建标准化的应用中。但Docker目前还不够完善，比如隔离效果不如VM，共享宿主机操作系统的一些基础库等；网络配置功能相对简单，主要以桥接方式为主；查看日志也不够方便灵活。

另外，IBM发表了一篇关于虚拟机和Linux container性能对比的[论文](http://domino.research.ibm.com/library/cyberdig.nsf/papers/0929052195DD819C85257D2300681E7B/$File/rc25482.pdf)，论文中实际测试了虚拟机和Linux container在CPU、内存、存储IO以及网络的负载情况，结果显示Docker容器本身几乎没有什么开销，但是使用AUFS会一定的性能损耗，不如使用Docker Volume，Docker的NAT在较高网络数据传输中会引入较大的工作负载，带来额外的开销。不过container的性能与native相差不多，各方面的性能都一般等于或者优于虚拟机。Container和虚拟机在IO密集的应用中都需要调整优化以更好的支持IO操作，两者在IO密集型的应用中都应该谨慎使用。

## Docker的核心技术
- 文件系统隔离：每个容器都拥有自己的root文件系统。
- 进程隔离：每个容器都运行在自己的进程环境中。
- 网络隔离：容器的虚拟网络接口和IP都是分开的。
- 资源隔离和分组：使用cgroups将CPU和内存资源独立分配给每个 Docker容器。
- 写时复制：文件系统都是写时复制的，速度快，占用磁盘空间更少。
- 日志收集：容器产生的stdin，stdout，stderr日志都会被收集并记录日志。
- 交互式shell：用户可以创建一个伪tty终端，将其连接到stdin，为容器提供一个交互式的shell。

## Docker能做什么
我们可以使用Docker做如下一些事情：

- 加速本地开发和构建流程，使其更加高效，更加轻量化。
- 能够让独立服务或者应用程序在不同的环境中，得到相同的运行结果。
- 用Docker创建隔离的环境来进行测试。
- Docker可以让开发者很简单地在本机构建一个复杂的环境进行测试。
- 构建一个多用户的平台即服务（PaaS）基础设施。
- 为开发，测试提供一个轻量级的独立沙盒测试环境。
- 提供软件即服务(SaaS)应用程序，如Memcached即服务。
- 高性能，超大规模的宿主机部署。

## Docker的应用场景
1. 简化配置  
这是Docker公司宣传的Docker的主要使用场景。虚拟机的最大好处是能在你的硬件设施上运行各种配置不一样的平台（软件、系统），Docker在降低额外开销的情况下提供了同样的功能。它能让你将运行环境和配置放在代码中然后部署，同一个Docker的配置可以在不同的环境中使用，这样就降低了硬件要求和应用环境之间耦合度。
2. 代码流水线（Code Pipeline）管理   
前一个场景对于管理代码的流水线起到了很大的帮助。代码从开发者的机器到最终在生产环境上的部署，需要经过很多的中间环境。而每一个中间环境都有自己微小的差别，Docker给应用提供了一个从开发到上线均一致的环境，让代码的流水线变得简单不少。
3. 提高开发效率
不同的开发环境中，我们都想把两件事做好。一是我们想让开发环境尽量贴近生产环境，二是我们想快速搭建开发环境。  
理想状态中，要达到第一个目标，我们需要将每一个服务都跑在独立的虚拟机中以便监控生产环境中服务的运行状态。然而，我们却不想每次都需要网络连接，每次重新编译的时候远程连接上去特别麻烦。这就是Docker做的特别好的地方，开发环境的机器通常内存比较小，之前使用虚拟的时候，我们经常需要为开发环境的机器加内存，而现在Docker可以轻易的让几十个服务在Docker中跑起来。
4. 隔离应用  
有很多种原因会让你选择在一个机器上运行不同的应用，比如之前提到的提高开发效率的场景等。  
我们经常需要考虑两点，一是因为要降低成本而进行服务器整合，二是将一个整体式的应用拆分成松耦合的单个服务。  
5. 整合服务器  
正如通过虚拟机来整合多个应用，Docker隔离应用的能力使得Docker可以整合多个服务器以降低成本。由于没有多个操作系统的内存占用，以及能在多个实例之间共享没有使用的内存，Docker可以比虚拟机提供更好的服务器整合解决方案。
7. 多租户环境  
另外一个使用场景是在多租户的应用中，它可以避免关键应用的重写。使用Docker，可以为每一个租户的应用层的多个实例创建隔离的环境，这不仅简单而且成本低廉，当然这一切得益于Docker环境的启动速度和其高效的diff命令。
8. 快速部署  
在虚拟机之前，引入新的硬件资源需要消耗几天的时间。虚拟化技术（Virtualization）将这个时间缩短到了分钟级别。而Docker通过为进程仅仅创建一个容器而无需启动一个操作系统，再次将这个过程缩短到了秒级。通过使用Docker并进行有效的资源分配可以提高资源的利用率。  

## Docker命令分类
- 容器生命周期管理  

    `docker [run|start|stop|restart|kill|rm|pause|unpause]`

- 容器操作运维  

    `docker [ps|inspect|top|attach|events|logs|wait|export|port]`

- 容器rootfs命令

    `docker [commit|cp|diff]`

- 镜像仓库

    `docker [login|pull|push|search]`

- 本地镜像管理

    `docker [images|rmi|tag|build|history|save|import]`

- 其他命令

    `docker [info|version]`


一张图总结所有的Docker命令：

![](/public/img/docker_commands.png "一张图总结所有的Docker命令")

## Docker 常用命令
1. 查看容器的root用户密码  

    `docker logs <容器名orID> 2>&1 | grep '^User: ' | tail -n1`
因为docker容器启动时的root用户的密码是随机分配的。所以，通过这种方式就可以得到redmine容器的root用户的密码了。

1. 查看容器日志  

    `docker logs -f <容器名orID>`

1. 查看正在运行的容器

    `docker ps`
    `docker ps -a             # 为查看所有的容器，包括已经停止的`

1. 删除所有容器

    `docker rm $(docker ps -a -q)`
    `docker rm <容器名orID>    # 删除单个容器`

1. 启动容器  

    - `docker run -i -t ubuntu /bin/bash`                       # 启动一个容器
    - `docker run -i -t --rm ubuntu /bin/bash`                  # --rm表示容器退出后立即删除该容器
    - `docker run -t -i --name test_container ubuntu /bin/bash` # --name指定容器的名称，否则会随机分配一个名称
    - `docker run -d ubuntu /bin/sh -c "while true; do echo hello world; sleep 2; done"`  # -d 表示启动后台进程, 创建容器后会直接返回
    - `docker run -t -i --net=host ubuntu /bin/bash`           # --net=host容器以Host方式进行网络通信
    - `docker run -t -i -v /host:/container ubuntu /bin/bash`  # -v绑定挂在一个Volume，在宿主机和Docker容器中共享文件或目录

1. 运行一个新容器，同时为它命名、端口映射、文件夹映射   
以redmine镜像为例：  

    `docker run --name redmine -p 9003:80 -p 9023:22 -d -v /var/redmine/files:/redmine/files -v     /var/redmine/mysql:/var/lib/mysql sameersbn/redmine`

1. 一个容器连接到另一个容器  

    `docker run -i -t --name sonar -d -link mmysql:db   tpires/sonar-server`    	
sonar容器连接到mmysql容器，并将mmysql容器重命名为db。这样，sonar容器就可以使用db的相关的环境变量了。

1. 停止、启动、杀死一个容器  	

    `docker stop <容器名orID>`  
    `docker start <容器名orID>`  
    `docker kill <容器名orID>`  

1. 深入容器获取更多信息  

    `docker inspect test_container`

1. 查看容器内进程日志  

    `docker logs test_container`
    `docker logs --tail 10 test_container`
    `docker logs --tail 0 -f -t test_container` #不断输出,-t 输出时间

1. 导出容器  

    `docker export -o ubuntu1204.tar <容器id>`  # 没有历史版本等信息，所以文件比较小

1. 查看内部进程  

    `docker top test_container`

1. 进入已启动的容器  

    `docker exec -t -i test_container /bin/bash`   # -i: 交互式

1. 查看所有镜像  

    `docker images`  

1. 删除所有镜像  
    
    `docker rmi $(docker images | grep none | awk '{print $3}' | sort -r)`

1. 将本地修改后的镜像提交为新的镜像  

    `docker commit -m 'python2.7 and yum repo' -a 'ixirong.liu@gmail.com' 415fee0a0817 xirong/centos_xirong:v0.1`

1. 拉取镜像  

    `docker pull <镜像名:tag>`   
    `docker pull sameersbn/redmine:latest`

1. 当需要把一台机器上的镜像迁移到另一台机器的时候，需要保存镜像与加载镜像   

	机器a  

		docker save busybox-1 > /home/save.tar  
	
	使用scp将save.tar拷到机器b上，然后：  

		docker load < /home/save.tar

1. 构建自己的镜像  

    `docker build -t <镜像名> <Dockerfile路径>`  
如Dockerfile在当前路径： `docker build -t xx/gitlab .`

1. 镜像的保存和载入  

    `docker save -o /tmp/mysave.tar <镜像名:tag>`
    `docker export -o ubuntu1204.tar <容器id>`  # export其实是容器的保存，只把镜像当前的状态保存下来，没有历史版本等信息，所以文件比较小
    `docker load <　/tmp/mysave.tar`