# lizhenghn123.github.io

**点击预览：[cpper.info](http://cpper.info)**


本站是通过jekyll和github搭建起来的。

下面介绍下jekyll的目录结构：

1. _layouts：用于存放模板的文件夹，里面有两个模板，default.html和post.html
2. _posts：用于存放博客文章的文件夹
3. css：存放博客所用css的文件夹
4. _site：jekyll自动生成的目录，为静态的页面
5. _coinfig.yml：jekyll的配置文件，里面可以定义相当多的配置参数，具体配置参数可以参照其官网

根据实际需要，可能还需要创建如下文件或文件夹：

1. _includes:用于存放一些固定的HTML代码段，文件为.html格式，可以在模板中通过liquid标签引常用来在各个模板中复用如 导航条、标签栏、侧边栏 之类的在每个页面上都一样不变的内容，
需要注意的是，这个代码段也可以是未被编译的，也就是说也可以使用liquid标签放在这些代码段中
2. image和js等自定义文件夹：用来存放一些需要的资源文件，如图片或者javascript文件，可以任意命名
3. CNAME文件：用来在github上做域名绑定的
4. favicon.ico：网站的小图标


本站使用的评论系统是第三方应用：[disqus](http://disqus.com)



# 想使用我的博客模板?
很简单，前提是你已经搭建了jekyll的环境。那么：

1. fork库到自己的github；
2. 修改名字为：`username.github.io`，username即是你自己的github username；
3. clone库到本地，参考`_posts`中的目录结构自己创建适合自己的文章目录结构；
4. 修改CNAME，或者删掉这个文件；
5. 修改`_config.yml`配置项（也是主要的修改地方）；
6. 像百度分享、百度统计、google 统计的辅助功能，你可以自行注册，之后将生成的js代码替换掉我的即可。
