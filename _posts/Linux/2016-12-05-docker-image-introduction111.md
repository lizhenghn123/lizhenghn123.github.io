---
layout: post

title: Docker镜像(Image)学习笔记33333222

category: Linux

tags: Linux Docker 

keywords: Linux Docker 

description: 本文介绍了Docker 镜像的基本知识以及镜像的各种命令操作实例。

---


![Docker_Images](/public/img/Docker_Images_Layers.png "Docker镜像分层示意图")

## 镜像是什么
> A Docker image is a read-only template. For example, an image could contain an Ubuntu operating system with Apache and your web application installed. Images are used to create Docker containers. Docker provides a simple way to build new images or update existing images, or you can download Docker images that other people have already created. Docker images are the build component of Docker.

翻译过来就是：Docker镜像是一个只读的模板。比如一个镜像可以包含Ubuntu系统以及安装在Ubuntu上的Apache Web服务器和你自己的应用。镜像是用来创建容器的。Docker提供了一个简单的方式用以创建新的镜像或者更新现存的镜像，甚至你可以下载其他地方提供的镜像。镜像是Docker服务的组件之一。

由于Docker使用一个统一文件系统，Docker镜像其实就是一堆文件的集合，并不是像VM那样的是一个操作系统。镜像可以简单到只有一个程序文件，比如如果你写了一个简单的hello world程序放到一个空的镜像中，那么整个镜像的大小，就是你编译后的二进制文件的大小。

<!-- more --> 

总结来说就是：

- 镜像(image)是 Docker 的三大组件之一；
- 镜像是用来启动容器的基石；
- 镜像是只读的，也即是无状态的，一个镜像是永久不会变的；
- 一个没有任何父镜像的镜像，称之为基础镜像;
- 在Docker容器中所有的变更都发生顶层的镜像可写层;

Docker 运行容器前需要本地存在对应的镜像，如果镜像不存在本地，Docker 会从镜像仓库下载（ 默认是 Docker Hub 公共注册服务器中的仓库）。

## 获取镜像
可以使用docker search 命令来查找镜像。

```shell
$ docker search ubuntu:16.04
INDEX       NAME                                                     DESCRIPTION                                     STARS     OFFICIAL   AUTOMATED
docker.io   docker.io/ctuning/ck-ubuntu-16.04                        CK Ubuntu 16.04 iimages                         2                    
docker.io   docker.io/seresearch/opendavinci-ubuntu-16.04            Docker image with all Ubuntu 16.04 depende...   1                    [OK]
docker.io   docker.io/addle/ubuntu-16.04                             Ubuntu 16.04 LTS (Xenial Xerus)                 0                    
docker.io   docker.io/cdbishop89/docker-ubuntu-16.04                 Base Ubuntu 16.04 Image                         0                    [OK]
......
```

可以使用 docker pull 命令来从仓库获取所需要的镜像。  
下面的例子将从 Docker Hub 仓库下载一个 Ubuntu操作系统的镜像。  

```shell
$ docker pull ubuntu:16.04
Trying to pull repository docker.io/library/ubuntu ... 
16.04: Pulling from docker.io/library/ubuntu
aed15891ba52: Pull complete 
773ae8583d14: Pull complete 
d1d48771f782: Pull complete 
cd3d6cd6c0cf: Pull complete 
8ff6f8a9120c: Pull complete 
Digest: sha256:35bc48a1ca97c3971611dc4662d08d131869daa692acb281c7e9e052924e38b1
Status: Downloaded newer image for docker.io/ubuntu:16.04
```

下载过程中，会输出获取镜像的每一层信息。  
该命令实际上相当于 `docker pull registry.hub.docker.com/ubuntu:16.04` 命令，即从注册服务器registry.hub.docker.com 中的 ubuntu 仓库来下载标记为 16.04 的镜
像。  

有时候官方仓库注册服务器下载较慢，可以从其他仓库下载。 从其它仓库下载时需要指定完整的仓库注册服务器地址。例如从网易凤巢上下载一个镜像: 

    $ docker pull hub.c.163.com/public/logo

下载完成后，即可随时使用该镜像了，例如创建一个容器，让其中运行 bash 应用:  

```shell
$ docker run -t -i ubuntu /bin/bash
root@fe7fc4bd8fc9:/#
```

## 列出本地镜像
使用 docker images 显示本地已有的镜像。  

```shell
$ docker images
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
docker.io/ubuntu    16.04               e4415b714b62        11 days ago         128.1 MB
docker.io/ubuntu    latest              e4415b714b62        11 days ago         128.1 MB
docker.io/ubuntu    12.04               aefa163f7a7e        11 days ago         103.5 MB
docker.io/centos    latest              0584b3d2cf6d        3 weeks ago         196.5 MB
```

在列出信息中，可以看到几个字段信息:

- 来自于哪个仓库，比如 ubuntu
- 镜像的标记，比如 16.04
- 它的 ID 号(唯一)，比如e4415b714b62
- 创建时间
- 镜像大小

其中镜像的 ID 唯一标识了镜像，注意到 ubuntu:16.04 和 ubuntu:latest具有相同的镜像 ID ，说明它们实际上是同一镜像。
TAG 信息用来标记来自同一个仓库的不同镜像。例如 ubuntu 仓库中有多个镜像，通过 TAG 信息来区分发行版本，例如10.04 、 12.04 、 12.10 、 13.04 、 14.04 等。例如可以使用`docker run -t -i ubuntu:16.04 /bin/bash`命令指定使用
镜像 ubuntu:16.04 来启动一个容器。如果不指定具体的标记，则默认使用 latest 标记信息。

## 创建镜像
创建镜像有很多方法，用户可以从 Docker Hub 获取已有镜像并更新，也可以利用本地文件系统创建一个。  

### 修改已有镜像
先通过镜像启动一个新的容器：  

```shell
$ docker run -it ubuntu:16.04 /bin/bash
root@267d3bd0a41f:/# 
```

我们假设在容器中安装sshd及nginx服务：

```shell
root@267d3bd0a41f:/# apt-get update   # 此步较慢，用以更新软件包信息
root@267d3bd0a41f:/# apt-get install -y openssh-server
root@267d3bd0a41f:/# apt-get install -y nginx
```

完成后使用 exit 或者 Ctrl + d 来退出该容器，现在该容器已经被改变了，使用docker commit 命令来提交更新后的副本。

```shell
$ docker ps -a   # 下面列出的267d3bd0a41f容器就是我们刚刚基于ubuntu:16.04启动并修改的
CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS                      PORTS               NAMES
267d3bd0a41f        ubuntu:16.04        "/bin/bash"         21 minutes ago      Exited (0) 21 seconds ago                       reverent_mestorf
$ docker commit -m="add openssh and nginx" -a "myname" 267d3bd0a41f myname/ubuntu16.04:v1
sha256:d001c19d07da8eef6e198bba5fe2b66a08f8022b160c513a6f5f516ff1affd5f    # 返回新创建的镜像ID
```

其中， -m 来指定提交的说明信息，跟我们使用的版本控制工具一样； -a 可以指定更新的用户信息；之后是用来创建镜像的容器的 ID；最后指定目标镜像的仓库名和 tag 信息。   

创建成功后会返回这个镜像的 ID 信息，使用 docker images 来查看新创建的镜像。  

```shell
$ docker images  # 查看所有镜像
REPOSITORY                  TAG                 IMAGE ID            CREATED             SIZE
myname/ubuntu16.04          v1                  d001c19d07da        37 seconds ago      271.1 MB    # 该镜像就是我们刚刚创建的镜像
docker.io/ubuntu            16.04               e4415b714b62        12 days ago         128.1 MB
docker.io/ubuntu            latest              e4415b714b62        12 days ago         128.1 MB
docker.io/ubuntu            12.04               aefa163f7a7e        12 days ago         103.5 MB
docker.io/centos            latest              0584b3d2cf6d        3 weeks ago         196.5 MB
hub.c.163.com/public/logo   latest              6fbdd13cd204        4 months ago        585 B
```

之后，就可以使用新的镜像来启动容器：  

```shell
[root@localhost ~]# docker run -it --rm --name test_my_image myname/ubuntu16.04:v1 /bin/bash
root@b5c33db5b1fa:/# nginx 
root@b5c33db5b1fa:/# ps -ef | grep nginx
root        27     1  0 02:19 ?        00:00:00 nginx: master process nginx
www-data    28    27  0 02:19 ?        00:00:00 nginx: worker process
```

### 利用 Dockerfile 来创建镜像
使用 docker commit 来扩展一个镜像比较简单，但是不方便在一个团队中分享。我们可以使用 docker build 来创建一个新的镜像。为此，首先需要创建一个 Dockerfile，包含一些如何创建镜像的指令。  

Dockerfile 基本的语法是：

- 使用 # 来注释
- FROM 指令告诉 Docker 使用哪个镜像作为基础
- 接着是维护者的信息
- RUN 开头的指令会在创建中运行，比如安装一个软件包，在这里使用 apt-get来安装了一些软件

说明：Dockerfile 中每一条指令都创建镜像的一层。  

这里假设仍然基于ubuntu16:04镜像安装openssh和nginx服务(和上节的目标一样)。

```shell
$ mkdir create_image && cd create_image/
$ touch Dockerfile
```

在Dockerfile增加以下内容：  

```shell
# test the usage of Dockerfile
FROM ubuntu:16.04
MAINTAINER myname <myname@mycompany.com>
RUN apt-get -qq update
RUN apt-get install -y openssh-server
RUN apt-get install -y nginx
```

编写完成 Dockerfile 后可以使用 docker build 来生成镜像。

```shell
$ docker build -t="myname/newubuntu16.04:v0.1" .
Sending build context to Docker daemon 2.048 kB
Step 1 : FROM ubuntu:16.04
 ---> e4415b714b62
Step 2 : MAINTAINER myname <myname@mycompany.com>
 ---> Using cache
 ---> 2fb9cb8306e1
Step 3 : RUN apt-get -qq update
 ---> Using cache
 ---> 6ab9290074be
Step 4 : RUN apt-get install -y openssh-server
 ---> Running in 6af5fd45a684
Reading package lists...
Building dependency tree...
Reading state information...
The following additional packages will be installed:
.......                             # 省略中间一大串输出信息
 ---> 8e20ce3c9c8d
Removing intermediate container 6af5fd45a684
Step 5 : RUN apt-get install -y nginx
 ---> Running in ed642cc5b3a7
Reading package lists...
Building dependency tree...
Reading state information...
.......                             # 省略中间一大串输出信息
 ---> dbac478b3d20
Removing intermediate container ed642cc5b3a7
Successfully built dbac478b3d20     # 创建成功，注意此处的id
```

其中 -t 标记用来添加 tag，指定新的镜像的用户信息。 “.” 是 Dockerfile 所在的路径(当前目录)，也可以替换为一个具体的 Dockerfile 的路径。

可以看到 build 进程在执行操作。它要做的第一件事情就是上传这个 Dockerfile 内容，因为所有的操作都要依据 Dockerfile 来进行。 然后，Dockfile 中的指令被一条一条的执行。每一步都创建了一个新的容器，在容器中执行指令并提交修改（ 就跟
之前介绍过的 docker commit 一样） 。当所有的指令都执行完毕之后，返回了最终的镜像 id。所有的中间步骤所产生的容器都被删除和清理了。

查看新创建的镜像：

```shell
$ docker images | grep myname
myname/newubuntu16.04       v0.1                dbac478b3d20        4 minutes ago       272.9 MB    # 新镜像，注意此处的id
myname/ubuntu16.04          v1                  d001c19d07da        46 minutes ago      271.1 MB
```

上面第一行的输出即是通过Dockerfile创建的新镜像，注意这里的ID和上面build过程中的ID。  

注意： 如果某一行命令是错误的，比如不存在或者自己手误写错了，在运行过程中执行到该行时就报错并停止继续进行，此时我们可以自行修改Dockerfile，然后重新运行build命令。  
当然在错误命令行之前已经执行过的命令(生成了中间临时容器)都不会再重新生成，所以试错的代价很低，不用担心所有命令必须一次性全部正确。

现在可以利用新创建的镜像来启动一个容器：

```shell
$ docker run -it --rm myname/newubuntu16.04:v0.1 /bin/bash
root@75ff5fda2fcc:/# 
```

此外，在Dockerfile中还可以利用 ADD 命令复制本地文件到镜像；用 EXPOSE 命令来向外部开放端口；用 CMD 命令来描述容器启动后运行的程序等。例如：  

```shell
# put my local web site in myApp folder to /var/www
ADD myApp /var/www
# expose httpd port
EXPOSE 80
# the command to run
CMD ["/usr/sbin/apachectl", "-D", "FOREGROUND"]
```

Dockerfile的支持的操作有很多，也是以后主要使用的方式，更多Dockerfile的使用细节会在之后专门写一个总结介绍。

### 从本地文件系统导入
我们可以手动下载一个系统模板，然后再通过Docker导入。这里推荐从[openvz](https://openvz.org/Download/template/precreated)上下载模板。

```shell
$ wget http://download.openvz.org/template/precreated/ubuntu-14.04-x86_64-minimal.tar.gz
$ cat ubuntu-14.04-x86_64-minimal.tar.gz | docker import - ubuntu:14.04
sha256:a737264e205e245ac91f19c5a2a8e5c4716fe824aeb86a6f20ffb333155da82a
$ docker images | grep ubuntu
ubuntu                      14.04               a737264e205e        18 seconds ago      214.8 MB    # 本行即为新导入的镜像信息
myname/newubuntu16.04       v0.1                dbac478b3d20        12 minutes ago      272.9 MB
myname/ubuntu16.04          v1                  d001c19d07da        54 minutes ago      271.1 MB
docker.io/ubuntu            16.04               e4415b714b62        12 days ago         128.1 MB
docker.io/ubuntu            latest              e4415b714b62        12 days ago         128.1 MB
docker.io/ubuntu            12.04               aefa163f7a7e        12 days ago         103.5 MB
```

### 上传镜像
用户可以通过 docker push 命令，把自己创建的镜像上传到仓库中来共享。例如，用户在 Docker Hub 上完成注册后，可以推送自己的镜像到仓库中。

```shell
$ sudo docker push myname/newubuntu16.04:v0.1       # push前需要首先docker login登录
```

## 保存和加载镜像
如果要保存镜像到本地文件，可以使用 docker save 命令。

    $ docker save -o ubuntu_16.04.tar ubuntu:16.04

可以使用 docker load 从导出的本地文件中再加载到本地镜像库。

    $ docker load --input ubuntu_14.04.tar

或者：

    $ docker load < ubuntu_16.04.tar
    
## 删除镜像
如果要移除本地的镜像，可以使用 docker rmi 命令。rmi 命令后面可以通过镜像名或者镜像id标示要删除的镜像。  

```shell
$ docker rmi e4415b714b62
Untagged: docker.io/ubuntu:16.04
Deleted: sha256:e4415b714b624040f19f45994b51daed5cbdb00e0eb9a07221ff0bd6bcf55ed7
Deleted: sha256:2376de67376e394bacd54cf46c6e381de3ed0c89b92b1180f6f7275210114e27
Deleted: sha256:ee0f021882bcaaa78cec72082efd81bef483098334cd6433e540c595333be4e6
Deleted: sha256:c5b75c815fe3fb5035774723dfcfc0b140c252eabc570a27b8c6c897388c61d8
Deleted: sha256:7619cf689c8980fadbcb9e1c77d2009588d4e233b170d154c8448185a42e6bde
Deleted: sha256:e7ebc6e16708285bee3917ae12bf8d172ee0d7684a7830751ab9a1c070e7a125
```

注意：在删除镜像之前要先用 docker rm 删掉依赖于这个镜像的所有容器（哪怕是已经停止的容器），否则无法删除该镜像。

```shell
$ docker rmi e4415b714b62
Failed to remove image (e4415b714b62): Error response from daemon: conflict: unable to delete e4415b714b62 (cannot be forced) - image has dependent child images
```

## Reference
- <<我的第一本Docker书>>
- << Docker从入门到实践 >>
- [Centos 7 docker私有仓库的搭建](https://www.tianmaying.com/tutorial/docker-registry)