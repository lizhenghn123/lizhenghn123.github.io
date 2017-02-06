---
layout: post

title: 通过Docker-Compose工具编排Docker项目

category: Docker

tags: Linux Docker 容器

keywords: Linux Docker 容器

description: 

---

Docker Compose 是 Docker 容器进行编排的工具，定义和运行多容器的应用，可以一条命令启动多个容器。使用Compose 基本上分为三步：

1. Dockerfile 定义应用的运行环境
2. docker-compose.yml 定义组成应用的各服务
3. docker-compose up 启动整个应用

下面以3个例子进行说明如何通过Compose工具运行一个项目。
<!-- more -->

## 简单的web访问计数功能  

创建一个简单的Python应用， 使用Flask，将数值记入Redis，当用户访问页面时显示当前该页面被访问的次数。

新建一个目录`python-flask-redis`，该目录结构如下所示：
    
    ├── app.py
    ├── docker-compose.yml
    ├── Dockerfile
    └── requirements.txt

我们先创建web项目所使用的docker 镜像，其中app.py是python flask应用，功能就是利用 redis 的 incr 方法进行访问计数，该应用依赖falsk、redis组件，这里单独设置一个requirements.txt文件，以便使用pip进行安装，Dockerfile文件就是用来只做该web镜像的。

app.py代码如下所示：

```python
#!/usr/bin/python
from flask import Flask
from redis import Redis

app = Flask(__name__)
redis = Redis(host='redis', port=6379)

@app.route('/')
def hello():
    redis.incr('hits')
    return 'Hello World! I have been seen %s times.' % redis.get('hits')

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)# 
```

requirements.txt中的内容就是要安装的python依赖库：

```shell
    flask
    redis
```

Dockerfile的内容也很简单：
    
```shell
    # 基于 python:2.7 镜像
    FROM python:2.7
    # 将本地目录中的内容添加到 container 的 /code 目录下
    ADD . /code
    # 设置程序工作目录为 /code
    WORKDIR /code
    # 运行安装命令
    RUN pip install -r requirements.txt
    # 启动程序
    CMD python app.py
```

此时就可以构建web服务的镜像了，

```shell
$ docker build -t lizheng/python-flask-redis .
```

构建完成之后，可以通过images命令查看：

```shell
$ docker images
REPOSITORY                                  TAG                 IMAGE ID            CREATED             SIZE
lizheng/python-flask-redis                  latest              063993fbc2da        8 minutes ago       683.5 MB
```

接下来制作 docker-compose 需要的配置文件 `docker-compose.yml`， 配置中创建了 2 个 service: web 和 redis ，各自有依赖的镜像，其中web 开放5000端口，并与 host 的5000端口对应， volumes 选项将本地目录中的文件加载到容器的 /code 中，links 表明 services web 依赖另一个 service redis，完整的配置如下:

```shell
web:
  image: lizheng/python-flask-redis
  ports:
    - "5000:5000"
  volumes:
    - .:/code
  links:
    - redis
  redis:
    image: redis
```

注意这里的image都是使用已经存在的镜像，比如lizheng/python-flask-redis(刚刚手动构建的)、redis(本地没有时会从远端拉取)。现在万事俱备，只需要最后一条启动命令了：`docker-compose up`。启动成功后有以下输出：

![](/public/img/compose-python-flask-redis-running.png "通过docker-compose启动项目")

通过`docker-compose ps`命令查看刚刚启动的项目：

```shell
$ docker-compose ps     # 注意此命令应该在当前目录下运行
          Name                         Command               State           Ports          
-------------------------------------------------------------------------------------------
pythonflaskredis1_redis_1   docker-entrypoint.sh redis ...   Up      6379/tcp               
pythonflaskredis1_web_1     /bin/sh -c python app.py         Up      0.0.0.0:5000->5000/tcp
```

此时访问web页面，有以下输出：

![](/public/img/compose-python-flask-redis.png "访问通过docker-compose启动的服务")
    
## haproxy-web负载均衡
这次我们创建一个经典的 Web 项目：一个 Haproxy，挂载三个 Web 容器。

创建一个 compose-haproxy-web 目录作为项目工作目录，并在其中分别创建两个子目录：haproxy 和 web。 整个目录结构如下所示：  

	├── docker-compose.yml
	├── haproxy
	│   └── haproxy.cfg
	└── web
	    ├── Dockerfile
	    ├── index.html
	    └── index.py


### docker-compose.yml
编写 docker-compose.yml 文件，这个是 Compose 使用的主模板文件。内容十分简单，指定 3 个 web 容器，以及 1 个 haproxy 容器。

```shell	
	weba:
	    build: ./web
	    expose:
	        - 80
	
	webb:
	    build: ./web
	    expose:
	        - 80
	
	webc:
	    build: ./web
	    expose:
	        - 80
	
	haproxy:
	    image: haproxy:latest
	    volumes:
	        - ./haproxy:/haproxy-override
	        - ./haproxy/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro
	    links:
	        - weba
	        - webb
	        - webc
	    ports:
	        - "8000:80"
	        - "7000:70"
	    expose:
	        - "80"
	        - "70"
```

### web 子目录
本目录中的文件用来实现一个简单的 HTTP 服务，打印出访问者的 IP 和 实际的本地 IP。

#### Dockerfile
生成一个 Dockerfile，内容为
	
```shell
	FROM python:2.7
	WORKDIR /code
	ADD . /code
	EXPOSE 80
	CMD python index.py
```

#### index.html
生成一个临时的 index.html 文件，其内容会被 index.py 更新。

	$ touch index.html

#### index.py
编写一个 index.py 作为服务器文件，代码为:

```python
#!/usr/bin/python

import sys
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
import socket
import fcntl
import struct
import pickle
from datetime import datetime
from collections import OrderedDict

class HandlerClass(SimpleHTTPRequestHandler):
    def get_ip_address(self,ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])
    def log_message(self, format, *args):
        if len(args) < 3 or "200" not in args[1]:
            return
        try:
            request = pickle.load(open("pickle_data.txt","r"))
        except:
            request=OrderedDict()
        time_now = datetime.now()
        ts = time_now.strftime('%Y-%m-%d %H:%M:%S')
        server = self.get_ip_address('eth0')
        host=self.address_string()
        addr_pair = (host,server)
        if addr_pair not in request:
            request[addr_pair]=[1,ts]
        else:
            num = request[addr_pair][0]+1
            del request[addr_pair]
            request[addr_pair]=[num,ts]
        file=open("index.html", "w")
        file.write("<!DOCTYPE html> <html> <body><center><h1><font color=\"blue\" face=\"Georgia, Arial\" size=8><em>HA</em></font> Webpage Visit Results</h1></center>");
        for pair in request:
            if pair[0] == host:
                guest = "LOCAL: "+pair[0]
            else:
                guest = pair[0]
            if (time_now-datetime.strptime(request[pair][1],'%Y-%m-%d %H:%M:%S')).seconds < 3:
                file.write("<p style=\"font-size:150%\" >#"+ str(request[pair][1]) +": <font color=\"red\">"+str(request[pair][0])+ "</font> requests " + "from &lt<font color=\"blue\">"+guest+"</font>&gt to WebServer &lt<font color=\"blue\">"+pair[1]+"</font>&gt</p>")
            else:
                file.write("<p style=\"font-size:150%\" >#"+ str(request[pair][1]) +": <font color=\"maroon\">"+str(request[pair][0])+ "</font> requests " + "from &lt<font color=\"navy\">"+guest+"</font>&gt to WebServer &lt<font color=\"navy\">"+pair[1]+"</font>&gt</p>")
        file.write("</body> </html>");
        file.close()
        pickle.dump(request,open("pickle_data.txt","w"))

if __name__ == '__main__':
    try:
        ServerClass  = BaseHTTPServer.HTTPServer
        Protocol     = "HTTP/1.0"
        addr = len(sys.argv) < 2 and "0.0.0.0" or sys.argv[1]
        port = len(sys.argv) < 3 and 80 or int(sys.argv[2])
        HandlerClass.protocol_version = Protocol
        httpd = ServerClass((addr, port), HandlerClass)
        sa = httpd.socket.getsockname()
        print "Serving HTTP on", sa[0], "port", sa[1], "..."
        httpd.serve_forever()
    except:
        exit()
```

### haproxy 目录
在其中生成一个 haproxy.cfg 文件，内容为:

```shell
	global
	  log 127.0.0.1 local0
	  log 127.0.0.1 local1 notice
	
	defaults
	  log global
	  mode http
	  option httplog
	  option dontlognull
	  timeout connect 5000ms
	  timeout client 50000ms
	  timeout server 50000ms
	
	listen stats
	    bind 0.0.0.0:70
	    stats enable
	    stats uri /
	
	frontend balancer
	    bind 0.0.0.0:80
	    mode http
	    default_backend web_backends
	
	backend web_backends
	    mode http
	    option forwardfor
	    balance roundrobin
	    server weba weba:80 check
	    server webb webb:80 check
	    server webc webc:80 check
	    option httpchk GET /
	    http-check expect status 200
```

### 运行 compose 项目
在该目录下执行 docker-compose up 命令，会整合输出所有容器的输出。
	
	$ docker-compose up
	Recreating composehaproxyweb_webb_1...
	Recreating composehaproxyweb_webc_1...
	Recreating composehaproxyweb_weba_1...
	Recreating composehaproxyweb_haproxy_1...
	Attaching to composehaproxyweb_webb_1, composehaproxyweb_webc_1, composehaproxyweb_weba_1, composehaproxyweb_haproxy_1

此时访问本地的 8000 端口，会经过 haproxy 自动转发到后端的某个 web 容器上，刷新页面可以观察到访问的容器地址的变化。

![](/public/img/compose-haproxy-web-8000.png "访问通过docker-compose搭建的负载均衡web服务")

访问本地 7000 端口，可以查看到 haproxy 的统计信息。   

![](/public/img/compose-haproxy-web-7000.png "访问通过docker-compose搭建的负载均衡web服务中haproxy的统计信息")


## 创建Wordpress应用  
新建一个wordpress目录，并创建一个docker-compose.yml文件，docker-compose.yml内容如下：

```shell 
  db:
    image: mysql:5.7
    volumes:
      - "./.data/db:/var/lib/mysql"
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: wordpress
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wordpress
      MYSQL_PASSWORD: wordpress

  wordpress:
    image: wordpress:latest
    links:
      - db
    ports:
      - "8000:80"
    restart: always
    environment:
      WORDPRESS_DB_HOST: db:3306
      WORDPRESS_DB_PASSWORD: wordpress
```

启动应用： `docker-compose up`，此时访问主页[192.168.14.185:8000](http://192.168.14.185:8000)就可以对wordpress进行简单的配置并使用了：

![](/public/img/compose-wordpress-install.png "安装worppress应用")

简单配置完成之后就可以正式使用worppress了：

![](/public/img/compose-wordpress-web.png "通过docker-compose安装的wordpress站点首页")



## Reference
[compose-usage](https://yeasy.gitbooks.io/docker_practice/content/compose/usage.html)  
[使用Docker Compose编排容器](http://www.cnblogs.com/ee900222/p/docker_5.html)  