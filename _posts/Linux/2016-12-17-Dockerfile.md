---
layout: post

title: 深入学习Dockerfile的使用

category: Docker

tags: [Linux, Docker, 容器] 

keywords: Linux Docker 容器

description: 本文介绍了Dockerfile的结构、Dockerfile指令以及构建流程。

---

构建Docker镜像一般有两种方式：

1. 使用docker commit更新已修改的镜像为新镜像；
2. 使用Dockerfile文件进行docker build命令构建新镜像；

相对来说，第二种方式(通过Dockerfile)更灵活、更强大，因为通过Dockerfile进行构建的方式更具备可重复性、透明性以及幂等性。

## 基本结构
Dockerfile 由一行行命令语句组成，并且支持以 # 开头的注释行。一般的，Dockerfile分为四部分：  

- 基础镜像信息
- 维护者信息
- 镜像操作指令
- 容器启动时执行指令

例如:
	
```shell
# This dockerfile	uses the ubuntu	image
# VERSION	2 -	EDITION	1
# Author:	docker_user
# Command	format:	Instruction	[arguments / command]	..
# Base image to use, this	must be set	as the first line FROM	ubuntu
# Maintainer:	docker_user	<docker_user	at	email.com>	(@docker_user)
MAINTAINER	docker_user	docker_user@email.com
# Commands	to	update	the	image
RUN	echo "deb http://archive.ubuntu.com/ubuntu/ raring main universe"	>>	/etc/apt/sources.list
RUN	apt-get	update	&&	apt-get	install	-y	nginx
RUN	echo "\ndaemon	off;" >> /etc/nginx/nginx.conf
# Commands when creating a new	container
CMD	/usr/sbin/nginx
```

其中，一开始必须指明所基于的镜像名称，接下来推荐说明维护者信息。后面则是镜像操作指令，例如RUN指令，RUN指令将对镜像执行跟随的命令。每运行一条RUN指令镜像添加新的一层并提交。最后是CMD指令，来指定运行容器时的操作命令。

## Dockerfile指令
Dockfile中由一系列指令和参数组成。每条指令，如FROM，都必须为大些字母，而后面要跟随参数。

### FROM
格式为`FROM  <image>`或`FROM <image>:<tag>`。  
指定基础镜像。基础镜像是必须指定的。而FROM 就是指定基础镜像，因此一个 Dockerfile 中 FROM 是必备的指令，并且必须是第一条指令。

### MAINTAINER
格式为` MAINTAINER	<name>`，指定维护者信息。比如：`MAINTAINER The CentOS Project <cloud-ops@centos.org>`。

### RUN
格式为`RUN <command>`或`RUN	["executable",	"param1",	"param2"]`。  
前者将在	shell 终端中运行命令，即`/bin/sh	-c`；后者则使用`exec`执行。指定使用其它终端可以通过第二种方式实现，例如`RUN	["/bin/bash", "-c", "echo	hello"]`。  
每条 RUN	指令将在当前镜像基础上执行指定命令，并提交为新的镜像。当命令较长时可以使用"\"	来换行。 

### CMD
CMD用于指定一个容器启动时要运行的命令。支持三种格式：

- `CMD	["executable","param1","param2"]` : 使用 exec 执行，推荐方式；
- `CMD	command	param1	param2`： 在 /bin/sh 中执行，提供给需要交互的应用；
- `CMD	["param1","param2"]`： 提供给ENTRYPOINT的默认参数；

说明：

- 指定启动容器时执行的命令，每个Dockerfile只能有一条 CMD	命令。如果指定了多条命令，只有最后一条会被执行；
- 如果用户启动容器时候指定了运行的命令，则会覆盖掉CMD指定的命令；
- CMD与RUN指令有点类似，区别在于RUN指令是指定镜像被构建时要运行的命令，而CMD指令是指定容器被启动时要运行的命令；

### ENTRYPOINT
配置容器启动后执行的命令，并且不可被	docker run提供的参数覆盖。 ENTRYPOINT指令有两种格式：  

- `ENTRYPOINT	["executable",	"param1",	"param2"]`	
- `ENTRYPOINT	command	param1	param2`	（shell中执行）

说明：

- 每个Dockerfile中只能有一个ENTRYPOINT，当指定多个时，只有最后一个起效。
- ENTRYPOINT和CMD指令很类似，区别在于CMD指令会被容器启动时命令行中的命令覆盖掉，而ENTRYPOINT则不会，事实上 docker run命令行中指定的任何参数都会被当作参数再次传递给ENTRYPOINT指令中指定的命令。

比如假设Dockerfile中有以下命令：

```shell
ENTRYPOINT ["/usr/sbin/nginx"]
CMD ["-h"]
```

则在启动容器时，任何命令行中指定的参数都会被传递给nginx进程，比如我们可以指定`-g "daemon off"`参数使nginx在前台运行，如果不指定任何参数，则在CMD指令中指定的-h参数会被传给Nginx，即：`/usr/sbin/nginx -h`，用来显示nginx的帮助信息。

### EXPOSE
格式为`EXPOSE	<port>	[<port>...]`。  
告诉	Docker该容器暴露的端口号，供互联系统使用。在启动容器时需要通过`- P`参数，Docker	主机会自动分配一个端口转发到指定的该端口。  

### ENV
格式为`ENV	<key>	<value>`。指定一个环境变量，会被后续RUN	指令使用，并在容器运行时保持。例如  

```shell
ENV	PG_MAJOR	9.3
ENV	PG_VERSION	9.3.4
RUN	curl -SL http://example.com/postgres-$PG_VERSION.tar.xz | tar -xJC /usr/src/postgress
ENV	PATH	/usr/local/postgres-$PG_MAJOR/bin:$PATH
ENV MY_NAME=gogs MY_GROUP=gogsgroup
ENV MY_DIR /opt/app
WORKDIR $MY_DIR
```

也可以在run命令中通过`-e`标记传递环境变量，比如：

`docker run -it -e "WEB_PORT=8080" ubuntu env`

不过这些变量将只会存在运行时有效(ENV指定的环境变量会持久保存)。

### ADD
格式为`ADD	<src>	<dest>`。  
该命令将复制指定的<src\>到容器中的<dest\>	。其中<src\>可以是Dockerfile所在目录的一个相对路径；也可以是一个URL；还可以是一个tar文件（自动解压为目录）。

### COPY
格式为` COPY	<src>	<dest>`。  
复制本地主机的 <src\>（为Dockerfile所在目录的相对路径）到容器中的<dest\>。  
当使用本地目录为源目录时，推荐使用COPY指令。  

### VOLUME
格式为`VOLUME	["/data"]`。  
创建一个可以从本地主机或其他容器挂载的挂载点，一般用来存放数据库和需要保持的数据等。

### WORKDIR
格式为` WORKDIR /path/to/workdir`。  
为后续的RUN、CMD、ENTRYPOINT指令配置工作目录(都会在这个目录下执行)。 
可以使用多个WORKDIR指令，后续命令如果参数是相对路径，则会基于之前命令指定的路径。例如  

```shell
WORKDIR	/a
WORKDIR	b
WORKDIR	c
RUN	pwd
```

则最终路径为/a/b/c。

另外我们既可以为最终的容器设置工作目录，也可以为Dockerfile中的一系列指令设置工作目录。比如：

```shell
WORKDIR	/opt/webapp/db
RUN bundle install
WORKDIR	/opt/webapp
ENTRYPOINT	["backup"]
```

可以在容器启动时通过`-w`参数覆盖Dockerfile中的工作目录：

`docker run -it -w /usr/local ubuntu pwd`

上面指令就会把容器内的工作目录设置为/usr/loca。

### USER
格式为`USER	daemon`。  
指定运行容器时的用户名或UID，后续的RUN也会使用指定用户。  
当服务不需要管理员权限时，可以通过该命令指定运行用户。并且可以在之前创建所需要的用户，例如：`RUN groupadd -r postgres && useradd -r	-g postgres	postgres`。要临时获取管理员权限可以使用	gosu，而不推荐sudo。

### ONBUILD
格式为`ONBUILD	[INSTRUCTION]`。  
配置当所创建的镜像作为其它新创建镜像的基础镜像时，所执行的操作指令。  
例如，Dockerfile	使用如下的内容创建了镜像image-A	。

```shell
[...]
ONBUILD	ADD	.	/app/src
ONBUILD	RUN	/usr/local/bin/python-build	--dir	/app/src
[...]
```

如果基于image-A	创建新的镜像时，新的Dockerfile中使用FROM image-A 指定基础镜像时，会自动执行	ONBUILD指令内容，等价于在后面添加了两条指令：

```shell
FROM	image-A
#Automatically	run	the	following
ADD	.	/app/src
RUN	/usr/local/bin/python-build	--dir	/app/src
```

使用ONBUILD指令的镜像，推荐在标签中注明，例如ruby:1.9-onbuild。

## 构建镜像

### 构建指令
编写完成	Dockerfile之后，可以通过docker build 命令来创建镜像。  
基本的格式为`docker build [选项] 路径	`，该命令将读取指定路径下（包括子目录）的Dockerfile，并将该路径下所有内容发送给	Docker	服务端，由服务端来创建镜像。因此一般建议放置Dockerfile的目录为空目录。也可以通过`.dockerignore`文件（每一行添加一条匹配模式）来让Docker忽略路径下的目录和文件。  
要指定镜像的标签信息，可以通过`-t`选项，例如:

`docker	build -t="myname/myimagename:v1"  .`

如果Dockerfile不在当前目录，则可以：

`docker	build -t="myname/myimagename:v1" -f path/to/file .`

以上指令将从本地目录下寻找Dockerfile文件，如果希望从某一远程git仓库中进行构建，则可以（该git仓库中必须要有Dockerfile文件）：  

`docker build -t="myname/myimagename:v1" git@github.com/jamtur01/docker-static_web`

### 构建流程

Dockerfile中的指令会按顺序从上到下依次执行，每条指令都会创建一个新的镜像层并对镜像进行提交。Docker大体上按照以下流程执行Dockerfile中的指令：

1. Docker从基础镜像运行一个容器；
2. 执行一条指令，对容器作出修改；
3. 执行类似docker commit的操作，提交一个新的镜像层；
4. Docker再基于刚提交的镜像运行一个新容器；
5. 执行Dockerfile中的下一条指令，直到所有指令都执行完毕；

从上面也可以看出，如果用户端Dockerfile由于某些原因（如某条指令失败了）没有正常结束，那么用户将得到一个可以使用的中间镜像，这对调试非常有帮助：可以基于该进行运行一个具备交互功能的容器，使用最后创建的镜像对为什么下一条指令会失败进行调试。

