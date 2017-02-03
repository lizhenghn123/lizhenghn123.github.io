---
layout: post

title: Docker编排工具Compose介绍及其YAML格式说明

category: Docker

tags: Linux Docker 容器

keywords: Linux Docker 容器

description: 

---

Docker Compose 是 Docker 官方编排（Orchestration）项目之一，负责快速在集群中部署分布式应用。Compose 定位是 “定义和运行多个 Docker 容器的应用”。  
 
我们知道使用一个 Dockerfile 模板文件可以让用户很方便的定义一个单独的应用容器。然而，在日常工作中，经常会碰到需要多个容器相互配合来完成某项任务的情况。例如要实现一个 Web 项目，除了 Web 服务容器本身，往往还需要再加上后端的数据库服务容器，甚至还包括负载均衡容器等。Compose 恰好满足了这样的需求。它允许用户通过一个单独的 docker-compose.yml 模板文件（YAML 格式）来定义一组相关联的应用容器为一个项目（project）。  

Compose 中有两个重要的概念：  

- 服务（service）：一个应用的容器，实际上可以包括若干运行相同镜像的容器实例。- 
- 项目(project)：由一组关联的应用容器组成的一个完整业务单元，在 docker-compose.yml 文件中定义。

一个项目可以由多个服务（容器）关联而成，Compose 面向项目进行管理，通过子命令对项目中的一组容器进行便捷地生命周期管理。

Compose 项目由 Python 编写，实现上调用了 Docker 服务提供的 API 来对容器进行管理。因此，只要所操作的平台支持 Docker API，就可以在其上利用 Compose 来进行编排管理。 

## Compose 命令说明
对于 Compose 来说，大部分命令的对象既可以是项目本身，也可以指定为项目中的服务或者容器。如果没有特别的说明，命令对象将是项目，这意味着项目中所有的服务都会受到命令影响。

### build
格式为 `docker-compose build [options] [SERVICE...]`。 

构建（重新构建）项目中的服务容器。  

服务容器一旦构建后，将会带上一个标记名，例如对于 web 项目中的一个 db 容器，可能是 web_db。  

可以随时在项目目录下运行 `docker-compose build` 来重新构建服务。  

选项包括：

- -force-rm 删除构建过程中的临时容器。
- --no-cache 构建镜像过程中不使用 cache（这将加长构建过程）。
- --pull 始终尝试通过 pull 来获取更新版本的镜像。

### kill
格式为 `docker-compose kill [options] [SERVICE...]`。  

通过发送 SIGKILL 信号来强制停止服务容器。  

支持通过 -s 参数来指定发送的信号，例如通过如下指令发送 SIGINT 信号。  

	docker-compose kill -s SIGINT

### logs
格式为 `docker-compose logs [options] [SERVICE...]`。  

查看服务容器的输出。默认情况下，docker-compose 将对不同的服务输出使用不同的颜色来区分。可以通过 --no-color 来关闭颜色。该命令在调试问题的时候十分有用。  

### pause

格式为 `docker-compose pause [SERVICE...]`。 暂停一个服务容器。

### port
格式为 `docker-compose port [options] SERVICE PRIVATE_PORT`。  

打印某个容器端口所映射的公共端口。

选项：

- --protocol=proto 指定端口协议，tcp（默认值）或者 udp。
- --index=index 如果同一服务存在多个容器，指定命令对象容器的序号（默认为 1）。

### ps
格式为 `docker-compose ps [options] [SERVICE...]`。  

列出项目中目前的所有容器。

选项：-q 只打印容器的 ID 信息。

### pull
格式为 `docker-compose pull [options] [SERVICE...]`。  

拉取服务依赖的镜像。  

选项：--ignore-pull-failures 忽略拉取镜像过程中的错误。  

### restart
格式为 `docker-compose restart [options] [SERVICE...]`。

重启项目中的服务。  

选项： -t, --timeout TIMEOUT 指定重启前停止容器的超时（默认为 10 秒）。

### rm
格式为 `docker-compose rm [options] [SERVICE...]`。

删除所有（停止状态的）服务容器。推荐先执行 docker-compose stop 命令来停止容器。

选项：

- -f, --force 强制直接删除，包括非停止状态的容器。一般尽量不要使用该选项。
- -v 删除容器所挂载的数据卷。

### run

格式为 `docker-compose run [options] [-p PORT...] [-e KEY=VAL...] SERVICE [COMMAND] [ARGS...]`。  

在指定服务上执行一个命令。  

例如： `docker-compose run ubuntu ping docker.com`，将会启动一个 ubuntu 服务容器，并执行 ping docker.com 命令。  

默认情况下，如果存在关联，则所有关联的服务将会自动被启动，除非这些服务已经在运行中。  

该命令类似启动容器后运行指定的命令，相关卷、链接等等都将会按照配置自动创建。  

两个不同点：

- 给定命令将会覆盖原有的自动运行命令；
- 不会自动创建端口，以避免冲突。

如果不希望自动启动关联的容器，可以使用 `--no-deps` 选项，例如

	docker-compose run --no-deps web python manage.py shell

将不会启动 web 容器所关联的其它容器。

选项：

- -d 后台运行容器。
- --name NAME 为容器指定一个名字。
- --entrypoint CMD 覆盖默认的容器启动指令。
- -e KEY=VAL 设置环境变量值，可多次使用选项来设置多个环境变量。
- -u, --user="" 指定运行容器的用户名或者 uid。
- --no-deps 不自动启动关联的服务容器。
- --rm 运行命令后自动删除容器，d 模式下将忽略。
- -p, --publish=[] 映射容器端口到本地主机。
- --service-ports 配置服务端口并映射到本地主机。
- -T 不分配伪 tty，意味着依赖 tty 的指令将无法运行。

### scale
格式为 `docker-compose scale [options] [SERVICE=NUM...]`。  

设置指定服务运行的容器个数。  

通过 service=num 的参数来设置数量。例如： `docker-compose scale web=3 db=2`，将启动 3 个容器运行 web 服务，2 个容器运行 db 服务。  

一般的，当指定数目多于该服务当前实际运行容器，将新创建并启动容器；反之，将停止容器。  

选项：-t, --timeout TIMEOUT 停止容器时候的超时（默认为 10 秒）。

### start
格式为 `docker-compose start [SERVICE...]`。

启动已经存在的服务容器。  

### stop

格式为 `docker-compose stop [options] [SERVICE...]`。

停止已经处于运行状态的容器，但不删除它。通过 docker-compose start 可以再次启动这些容器。

选项：-t, --timeout TIMEOUT 停止容器时候的超时（默认为 10 秒）。

### unpause
格式为 `docker-compose unpause [SERVICE...]`。

恢复处于暂停状态中的服务。

### up
格式为 `docker-compose up [options] [SERVICE...]`。  
该命令十分强大，它将尝试自动完成包括构建镜像，（重新）创建服务，启动服务，并关联服务相关容器的一系列操作。

链接的服务都将会被自动启动，除非已经处于运行状态。  

可以说，大部分时候都可以直接通过该命令来启动一个项目。  

默认情况，`docker-compose up` 启动的容器都在前台，控制台将会同时打印所有容器的输出信息，可以很方便进行调试。  

当通过 `Ctrl-C` 停止命令时，所有容器将会停止。  

如果使用 `docker-compose up -d`，将会在后台启动并运行所有的容器。一般推荐生产环境下使用该选项。  

默认情况，如果服务容器已经存在，`docker-compose up` 将会尝试停止容器，然后重新创建（保持使用 `volumes-from` 挂载的卷），以保证新启动的服务匹配 `docker-compose.yml` 文件的最新内容。如果用户不希望容器被停止并重新创建，可以使用 `docker-compose up --no-recreate`。这样将只会启动处于停止状态的容器，而忽略已经运行的服务。如果用户只想重新部署某个服务，可以使用 `docker-compose up --no-deps -d <SERVICE_NAME>` 来重新创建服务并后台停止旧服务，启动新服务，并不会影响到其所依赖的服务。

选项：

- -d 在后台运行服务容器。
- --no-color 不使用颜色来区分不同的服务的控制台输出。
- --no-deps 不启动服务所链接的容器。
- --force-recreate 强制重新创建容器，不能与 --no-recreate 同时使用。
- --no-recreate 如果容器已经存在了，则不重新创建，不能与 --force-recreate 同时使用。
- --no-build 不自动构建缺失的服务镜像。
- -t, --timeout TIMEOUT 停止容器时候的超时（默认为 10 秒）。

## Compose 模板文件
默认的模板文件名称为 docker-compose.yml，格式为 YAML 格式。  

在旧版本（版本 1）中，其中每个顶级元素为服务名称，次级元素为服务容器的配置信息，例如：
	
	webapp:
	  image: examples/web
	  ports:
	    - "80:80"
	  volumes:
	    - "/data"
	    
版本 2 扩展了 Compose 的语法，同时尽量保持跟版本 1 的兼容，除了可以声明网络和存储信息外，最大的不同一是添加了版本信息，另一个是需要将所有的服务放到 services 根下面。例如，上面例子改写为版本 2，内容为
	
	version: "2"
	services:
	  webapp:
	    image: examples/web
	    ports:
	      - "80:80"
	    volumes:
	      - "/data"

注意每个服务都必须通过 image 指令指定镜像或 build 指令（需要 Dockerfile）等来自动构建生成镜像。  

如果使用 build 指令，在 Dockerfile 中设置的选项(例如：CMD, EXPOSE, VOLUME, ENV 等) 将会自动被获取，无需在 docker-compose.yml 中再次设置。  

下面分别介绍各个指令的用法。  

### build

指定 Dockerfile 所在文件夹的路径（可以是绝对路径，或者相对 docker-compose.yml 文件的路径）。 Compose 将会利用它自动构建这个镜像，然后使用这个镜像。  

	build: /path/to/build/dir

### command
覆盖容器启动后默认执行的命令。  

	command: echo "hello world"

### container_name

指定容器名称。默认将会使用 项目名称_服务名称_序号 这样的格式。例如：

`container_name: docker-web-container`

需要注意，指定容器名称后，该服务将无法进行扩展（scale），因为 Docker 不允许多个容器具有相同的名称。

### dockerfile

如果需要指定额外的编译镜像的 Dockefile 文件，可以通过该指令来指定。例如  

`dockerfile: Dockerfile-alternate`

注意，该指令不能跟 image 同时使用，否则 Compose 将不知道根据哪个指令来生成最终的服务镜像。

### image

指定为镜像名称或镜像 ID。如果镜像在本地不存在，Compose 将会尝试拉去这个镜像。例如：
	
	image: ubuntu
	image: orchardup/postgresql
	image: a4bc65fd

### expose
暴露端口，但不映射到宿主机，只被连接的服务访问。仅可以指定内部端口为参数。

```shell
expose:
 - "3000"
 - "8000"
```

### ports
暴露端口信息。

使用宿主：容器 （HOST:CONTAINER）格式，或者仅仅指定容器的端口（宿主将会随机选择端口）都可以。
	
	ports:
	 - "3000"
	 - "8000:8000"
	 - "49100:22"
	 - "127.0.0.1:8001:8001"
	 
注意：当使用 HOST:CONTAINER 格式来映射端口时，如果你使用的容器端口小于 60 并且没放到引号里，可能会得到错误结果，因为 YAML 会自动解析 xx:yy 这种数字格式为 60 进制。为避免出现这种问题，建议数字串都采用引号包括起来的字符串格式。

### links
链接到其它服务中的容器。使用服务名称（同时作为别名）或服务名称：服务别名 （SERVICE:ALIAS） 格式都可以。
	
	links:
	 - db
	 - db:database
	 - redis

使用的别名将会自动在服务容器中的 /etc/hosts 里创建。例如：
	
	172.17.2.186  db
	172.17.2.186  database
	172.17.2.187  redis

被链接容器中相应的环境变量也将被创建。

### external_links
链接到 docker-compose.yml 外部的容器，甚至 并非 Compose 管理的外部容器。参数格式跟 links 类似。
	
	external_links:
	 - redis_1
	 - project_db_1:mysql
	 - project_db_1:postgresql

### extra_hosts
类似 Docker 中的 --add-host 参数，指定额外的 host 名称映射信息。例如：
	
	extra_hosts:
	 - "googledns:8.8.8.8"
	 - "dockerhub:52.1.157.61"

会在启动后的服务容器中 /etc/hosts 文件中添加如下两条条目。
	
	8.8.8.8 googledns
	52.1.157.61 dockerhub

### volumes
数据卷所挂载路径设置。可以设置宿主机路径 （HOST:CONTAINER） 或加上访问模式 （HOST:CONTAINER:ro）。该指令中路径支持相对路径。例如
	
	volumes:
	 - /var/lib/mysql
	 - cache/:/tmp/cache
	 - ~/configs:/etc/configs/:ro

### volumes_from
从另一个服务或容器挂载它的数据卷。
	
	volumes_from:
	 - service_name
	 - container_name
	 
### ulimits
指定容器的 ulimits 限制值。例如，指定最大进程数为 65535，指定文件句柄数为 20000（软限制，应用可以随时修改，不能超过硬限制） 和 40000（系统硬限制，只能 root 用户提高）。
	
	ulimits:
	  nproc: 65535
	  nofile:
	  soft: 20000
	  hard: 40000

### 其它指令
此外，还有包括` cpu_shares, cpuset, domainname, entrypoint, hostname, ipc, mac_address, mem_limit, memswap_limit, privileged, read_only, restart, stdin_open, tty, user, working_dir `等指令，基本跟 docker-run 中对应参数的功能一致。

例如，指定使用 cpu 核 0 和 核 1，只用 50% 的 CPU 资源：
	
	cpu_shares: 73
	cpuset: 0,1

指定服务容器启动后执行的命令。

	entrypoint: /code/entrypoint.sh

指定容器中运行应用的用户名。

	user: nginx

指定容器中工作目录。

	working_dir: /code

指定容器中搜索域名、主机名、mac 地址等。
	
	domainname: your_website.com
	hostname: test
	mac_address: 08-00-27-00-0C-0A

指定容器中内存和内存交换区限制都为 1G。
	
	mem_limit: 1g
	memswap_limit: 1g

允许容器中运行一些特权命令。

	privileged: true

指定容器退出后的重启策略为始终重启。该命令对保持服务始终运行十分有效，在生产环境中推荐配置为 always 或者 unless-stopped。

	restart: always

以只读模式挂载容器的 root 文件系统，意味着不能对容器内容进行修改。

	read_only: true

## YAML模板文件
默认的模板文件名称为 docker-compose.yml，格式为 YAML 格式。模板文件是使用 Compose 的核心，涉及到的指令关键字也比较多，不过大部分指令跟 docker run 相关参数的含义都是类似的。  

在旧版本（版本 1）中，其中每个顶级元素为服务名称，次级元素为服务容器的配置信息，例如
	
	webapp:
	  image: examples/web
	  ports:
	    - "80:80"
	  volumes:
	    - "/data"

版本 2 扩展了 Compose 的语法，同时尽量保持跟版本 1 的兼容，除了可以声明网络和存储信息外，最大的不同一是添加了版本信息，另一个是需要将所有的服务放到 services 根下面。上面例子改写为版本 2，内容为
	
	version: "2"
	services:
	  webapp:
	    image: examples/web
	    ports:
	      - "80:80"
	    volumes:
	      - "/data"

注意每个服务都必须通过 image 指令指定镜像或 build 指令（需要 Dockerfile）等来自动构建生成镜像。 如果使用 build 指令，在 Dockerfile 中设置的选项(例如：CMD, EXPOSE, VOLUME, ENV 等) 将会自动被获取，无需在 docker-compose.yml 中再次设置。

下面分别介绍各个指令的用法。

### build
指定 Dockerfile 所在文件夹的路径（可以是绝对路径，或者相对 docker-compose.yml 文件的路径）。 Compose 将会利用它自动构建这个镜像，然后使用这个镜像。

	build: /path/to/build/dir

### command
覆盖容器启动后默认执行的命令。

	command: echo "hello world"

### container_name
指定容器名称。默认将会使用 项目名称_服务名称_序号 这样的格式。例如：

	container_name: docker-web-container

需要注意，指定容器名称后，该服务将无法进行扩展（scale），因为 Docker 不允许多个容器具有相同的名称。

### dockerfile
如果需要指定额外的编译镜像的 Dockefile 文件，可以通过该指令来指定。例如

	dockerfile: Dockerfile-alternate

注意，该指令不能跟 image 同时使用，否则 Compose 将不知道根据哪个指令来生成最终的服务镜像。

### env_file
从文件中获取环境变量，可以为单独的文件路径或列表。

如果通过 `docker-compose -f FILE` 方式来指定 Compose 模板文件，则 `env_file` 中变量的路径会基于模板文件路径。

如果有变量名称与 `environment` 指令冲突，则按照惯例，以后者为准。
	
	env_file: .env
	
	env_file:
	  - ./common.env
	  - ./apps/web.env
	  - /opt/secrets.env

环境变量文件中每一行必须符合格式，支持 # 开头的注释行。
	
	# common.env: Set development environment
	PROG_ENV=development

### environment
设置环境变量。你可以使用数组或字典两种格式。

只给定名称的变量会自动获取运行 Compose 主机上对应变量的值，可以用来防止泄露不必要的数据。例如
	
	environment:
	  RACK_ENV: development
	  SESSION_SECRET:

或者
	
	environment:
	  - RACK_ENV=development
	  - SESSION_SECRET

注意，如果变量名称或者值中用到 true|false，yes|no 等表达布尔含义的词汇，最好放到引号里，避免 YAML 自动解析某些内容为对应的布尔语义。

[http://yaml.org/type/bool.html](http://yaml.org/type/bool.html) 中给出了这些特定词汇，包括
	
	 y|Y|yes|Yes|YES|n|N|no|No|NO
	|true|True|TRUE|false|False|FALSE
	|on|On|ON|off|Off|OFF

### expose
暴露端口，但不映射到宿主机，只被连接的服务访问。仅可以指定内部端口为参数
	
	expose:
	 - "3000"
	 - "8000"

### extends
基于其它模板文件进行扩展。例如我们已经有了一个 webapp 服务，定义一个基础模板文件为 common.yml。
	
	# common.yml
	webapp:
	  build: ./webapp
	  environment:
	    - DEBUG=false
	    - SEND_EMAILS=false

再编写一个新的 development.yml 文件，使用 common.yml 中的 webapp 服务进行扩展。
	
	# development.yml
	web:
	  extends:
	    file: common.yml
	    service: webapp
	  ports:
	    - "8000:8000"
	  links:
	    - db
	  environment:
	    - DEBUG=true
	db:
	  image: postgres

后者会自动继承 common.yml 中的 webapp 服务及环境变量定义。

使用 extends 需要注意：

- 要避免出现循环依赖，例如 A 依赖 B，B 依赖 C，C 反过来依赖 A 的情况。
- extends 不会继承 links 和 volumes_from 中定义的容器和数据卷资源。

一般的，推荐在基础模板中只定义一些可以共享的镜像和环境变量，在扩展模板中具体指定应用变量、链接、数据卷等信息。

### external_links
链接到 docker-compose.yml 外部的容器，甚至 并非 Compose 管理的外部容器。参数格式跟 links 类似。
	
	external_links:
	 - redis_1
	 - project_db_1:mysql
	 - project_db_1:postgresql

### extra_hosts
类似 Docker 中的 --add-host 参数，指定额外的 host 名称映射信息。例如：
	
	extra_hosts:
	 - "googledns:8.8.8.8"
	 - "dockerhub:52.1.157.61"

会在启动后的服务容器中 /etc/hosts 文件中添加如下两条条目。
	
	8.8.8.8 googledns
	52.1.157.61 dockerhub

### image
指定为镜像名称或镜像 ID。如果镜像在本地不存在，Compose 将会尝试拉去这个镜像。例如：
	
	image: ubuntu
	image: orchardup/postgresql
	image: a4bc65fd

### labels
为容器添加 Docker 元数据（metadata）信息。例如可以为容器添加辅助说明信息。
	
	labels:
	  com.startupteam.description: "webapp for a startup team"
	  com.startupteam.department: "devops department"
	  com.startupteam.release: "rc3 for v1.0"

### links
链接到其它服务中的容器。使用服务名称（同时作为别名）或服务名称：服务别名 （SERVICE:ALIAS） 格式都可以。
	
	links:
	 - db
	 - db:database
	 - redis

使用的别名将会自动在服务容器中的 /etc/hosts 里创建。例如：
	
	172.17.2.186  db
	172.17.2.186  database
	172.17.2.187  redis

被链接容器中相应的环境变量也将被创建。

### pid
跟主机系统共享进程命名空间。打开该选项的容器之间，以及容器和宿主机系统之间可以通过进程 ID 来相互访问和操作。

	pid: "host"

### ports
暴露端口信息。使用宿主：容器 （HOST:CONTAINER）格式，或者仅仅指定容器的端口（宿主将会随机选择端口）都可以。
	
	ports:
	 - "3000"
	 - "8000:8000"
	 - "49100:22"
	 - "127.0.0.1:8001:8001"

### ulimits
指定容器的 ulimits 限制值。

例如，指定最大进程数为 65535，指定文件句柄数为 20000（软限制，应用可以随时修改，不能超过硬限制） 和 40000（系统硬限制，只能 root 用户提高）。

	ulimits:
	  nproc: 65535
	  nofile:
		soft: 20000
		hard: 40000

### volumes
数据卷所挂载路径设置。可以设置宿主机路径 （HOST:CONTAINER） 或加上访问模式 （HOST:CONTAINER:ro）。

该指令中路径支持相对路径。例如
	
	volumes:
	 - /var/lib/mysql
	 - cache/:/tmp/cache
	 - ~/configs:/etc/configs/:ro

### volumes_from
从另一个服务或容器挂载它的数据卷。
	
	volumes_from:
	 - service_name
	 - container_name

### 其它指令
此外还有包括 cpu_shares, cpuset, domainname, entrypoint, hostname, ipc, mac_address, mem_limit, memswap_limit, privileged, read_only, restart, stdin_open, tty, user, working_dir 等指令，基本跟 docker-run 中对应参数的功能一致。

例如，指定使用 cpu 核 0 和 核 1，只用 50% 的 CPU 资源：
	
	cpu_shares: 73
	cpuset: 0,1

指定服务容器启动后执行的命令:  `entrypoint: /code/entrypoint.sh`；  
指定容器中运行应用的用户名：  `user: nginx`；  
指定容器中工作目录：  `working_dir: /code`；
指定容器中搜索域名、主机名、mac 地址等：
	
	domainname: your_website.com
	hostname: test
	mac_address: 08-00-27-00-0C-0A

指定容器中内存和内存交换区限制都为 1G:
	
	mem_limit: 1g
	memswap_limit: 1g

允许容器中运行一些特权命令:  `privileged: true`；  
指定容器退出后的重启策略为始终重启。该命令对保持服务始终运行十分有效，在生产环境中推荐配置为 always 或者 unless-stopped:  `restart: always`；  
以只读模式挂载容器的 root 文件系统，意味着不能对容器内容进行修改:`read_only: true`；  
打开标准输入，可以接受外部输入:`stdin_open: true`；  