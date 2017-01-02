---
layout: post

title: 使用Dockerfile构建镜像和容器

category: Docker

tags: [Linux, Docker, 容器] 

keywords: Linux Docker 容器

description: 使用Dockerfile构建镜像和容器。

---

## 使用Dockerfile创建静态网站
将Docker作为本地web开发环境是Docker的一个最简单的应用场景，这样的环境可以完全复制到生产环境，并确保用户开发的东西在生产环境中也能运行。 下面就逐步演示如何通过搭建一个简单的网站。  
<!-- more --> 	
首先创建一个新的空目录：first_Web，该目录结构如下所示：  

```shell
$ tree
.
├── Dockerfile
├── nginx
│   ├── global.conf
│   └── nginx.conf
└── website
    └── index.html
```

其中Dockerfile中内容如下：  

```shell
# test the usage of Dockerfile
FROM ubuntu:16.04
MAINTAINER lizhenghn <lizhenghn@gmail.com>
RUN apt-get -qq update
RUN apt-get install -y openssh-server \
			nginx
RUN mkdir -p /var/www/html/website
ADD nginx/global.conf /etc/nginx/conf.d/
ADD nginx/nginx.cong /etc/nginx/nginx.conf
EXPOSE 80
```

nginx/global.conf内容:  

```shell
server {
    listen 0.0.0.0:80;
    server_name _;

    root /var/www/html/website;
    index index.html;

    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
}
```

nginx/nginx.conf内容：  

```shell
$ cat nginx/nginx.conf 
user www-data;
worker_processes 4;
pid /run/ngnix.pid;
daemon off;

http {
    include /etc/nginx/conf.d/*.conf;
}
```

website/index.html内容：  

```shell
This is my first website!
```

现在万事俱备，只欠build： `docker build -t lizhenghn/first_web .`，经过一系列build步骤之后，如果顺利，我们的镜像就构建成功了。可以通过history命令查看构建历史：  

```shell
$ docker history lizhenghn/first_web
IMAGE               CREATED             CREATED BY                                      SIZE                COMMENT
a068122f3a0f        14 hours ago        /bin/sh -c #(nop) EXPOSE 80/tcp                 0 B                 
70095e651bb0        14 hours ago        /bin/sh -c #(nop) ADD file:e042e309a4edf5b43a   127 B               
57cc2cb18807        14 hours ago        /bin/sh -c #(nop) ADD file:f9fa41f09e438c4648   191 B               
6f96de546bf8        14 hours ago        /bin/sh -c mkdir -p /var/www/html/website       0 B                 
c59e12b83b2f        14 hours ago        /bin/sh -c apt-get install -y openssh-server    103.6 MB            
92cabc29672e        15 hours ago        /bin/sh -c apt-get -qq update                   39.48 MB            
f7f4969a4aca        15 hours ago        /bin/sh -c #(nop) MAINTAINER lizhenghn <lizhe   0 B                 
e4415b714b62        5 weeks ago         /bin/sh -c #(nop)  CMD ["/bin/bash"]            0 B                 
<missing>           5 weeks ago         /bin/sh -c mkdir -p /run/systemd && echo 'doc   7 B                 
<missing>           5 weeks ago         /bin/sh -c sed -i 's/^#\s*\(deb.*universe\)$/   1.895 kB            
<missing>           5 weeks ago         /bin/sh -c rm -rf /var/lib/apt/lists/*          0 B                 
<missing>           5 weeks ago         /bin/sh -c set -xe   && echo '#!/bin/sh' > /u   745 B               
<missing>           5 weeks ago         /bin/sh -c #(nop) ADD file:abc033900893f6c737   128.1 MB       
```

基于该镜像创建容器：  

`docker run -d -p 9000:80 --name myfirstweb -v website:/var/www/html/website lizhenghn/first_web nginx`

假设宿主机ip是192.168.14.185，此时可以通过9000端口访问刚创建容器的nginx服务了：  

![](/public/img/docker_first_image_nginx.png "访问docker容器中的nginx服务")

如果在宿主机外手动修改website/index.html内容，比如：

```shell
This is my first website! From Docker Container!
```

此时刷新页面，会发现页面立刻发生了变化：

![](/public/img/docker_first_image_nginx2.png "修改页面后立刻刷新查看")

这使得在开发过程中可以完全模拟生产环境里的真实状态，修改、验证、测试变得更简单了。

## 通过supervisor在一个容器中运行多个服务
Docker可以在启动容器的时候通过设置Dockerfile中的CMD条目启动一个进程，但如果要在容器中同时启动多个进程，就比较难办了(虽然不建议在一个容器中运行多个进程)。  

这时可以用过[supervisord](http://supervisord.org/introduction.html)达到目的， supervisord是一个进程管理工具，可以用来管理多个进程的启动、停止、重启等等，我之前也单独安装、使用过supervisord，点此查看：[Linux进程管理工具supervisor安装及使用](http://lizhenghn123.github.io/2016/04/14/supervisor-usage.html)。  

这里示例假设通过Docker容器中的supervisord启动容器内的多个进程，要启动的是sshd服务和apache httpd服务。  

首先创建一个新的空目录，比如叫：dockerfile_supervisor，该目录下只有两个文件：Dockerfile和supervisord.conf。  

```shell
$ tree
.
├── Dockerfile
└── supervisord.conf
```

其中Dockerfile中内容如下：  

```shell
# test the usage of Dockerfile
FROM ubuntu:16.04
MAINTAINER lizhenghn <lizhenghn@gmail.com>

# change passwd of root
RUN echo "root:lizhenghn" | chpasswd

# add user(guest), and add it in sudoers
RUN useradd guest
RUN echo "guest:123456" | chpasswd
RUN echo "guest ALL=(ALL) ALL" >> /etc/sudoers

RUN apt-get update
RUN apt-get install -y openssh-server apache2 supervisor
RUN mkdir -p /var/run/sshd
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/supervisord.conf
EXPOSE 22 80
CMD ["/usr/bin/supervisord"]
```

supervisord.conf内容如下：  

```shell
[supervisord]
; 设置supervisord为前台进程,docker要求
nodaemon=true

[program:sshd]
;设置sshd为前台进程，supervisord要求
command=/usr/sbin/sshd -D

[program:apache2]
;设置apache为前台进程，supervisord要求
command=/usr/sbin/apache2ctl -D FOREGROUND
```

现在万事俱备，只欠build： `docker build -t lizhenghn/two_services .`，经过一系列build步骤之后，如果顺利，我们的镜像就构建成功了。可以通过history命令查看构建历史。  

基于该镜像创建容器：  

`docker run -d -p 10022:22 -p 10080:80 lizhenghn/two_services`

假设宿主机ip是192.168.14.185，此时可以通过10080端口访问刚创建容器中的apache httpd服务了；也可以通过ssh进入到该容器中：`ssh -p 10022 guest@192.168.14.185`，然后输入Dockerfile中设置的密码123456即可登录到容器中。

