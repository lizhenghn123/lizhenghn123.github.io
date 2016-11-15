---
layout: post

title: 如何从一个git repo中分离出部分目录到新的独立的repo上

category: 开发

tags: 开发 git

keywords: 开发 git

description: 如何从一个git repo中分离出部分目录到新的独立的 git repo上

---

## 问题分析
最初我在一个git repo 中有几个不完全相关的项目，比如A，B，C三个小项目，在同一个repo下，但在不同的目录下（假设为dira、dirb、dirc）。随着A，B，C这几个小项目的不断演进，各项目都变得很大，关联性也降低很多，所以希望将这几个小项目单独拆分成几个独立的repo，且希望不丢失原来的各个项目的提交日志，但不能有其他不相关日志，比如dira的日志中不应该出现dirb或dirc的提交日志。

## 寻找利器
**git filter-branch**。

这是git里一个很重量级的命令，这个命令会按照指定的方式（一系列过滤器，filter）修改给定的commit，几乎可以针对历史commit执行你想要的任何操作。比如，从历史中删除某个文件，修改commit message等。

如果你没有指定任何filter，那么git filter-branch则会原封不动的将所有历史重新commit一次。

改写历史后，所有的object都会有新的object name。因此，你将不能轻易的将改写后的branch推送到server端（non-fastforward issue）。请不要轻易使用该命令，除非你很清楚该命令对git repo的影响。

每次执行git filter-branch操作后，务必检查改写后的历史是否正确。为了避免因操作错误造repo损坏，git会在filter-branch操作实际改写历史时，自动将原refs备份到refs/original/下。

目前，git filter-branch支持以下filter：
    
    --env-filter
    --tree-filter
    --index-filter
    --parent-filter
    --msg-filter
    --commit-filter
    --tag-name-filter
    --subdirectory-filter

比如以下两个命令都可以将filename指定的文件从历史中永久删除：  

    # git filter-branch --tree-filter 'rm filename' HEAD
    # git filter-branch --index-filter 'git rm --cached --ignore-unmatch filename' HEAD

不过，针对我们的需求，这里使用的filter是subdirectory-filter。
## 动手操作
这里以一个开源项目[crow](https://github.com/ipkn/crow)为例进行说明。
**注意，最好新建一个单独的分支进行操作。**

    # git clone https://github.com/ipkn/crow
    # cd crow && tree -d
    .
    ├── amalgamate
    ├── cmake
    ├── examples
    │   ├── ssl
    │   └── websocket
    │       └── templates
    ├── include
    │   └── crow
    └── tests
        └── template

这里演示将include目录单独拆分出来成为一个新的git repoclone。

下面开始实际操作：

    # git checkout -b check_include_alone   # 创建新的分支
    # ls                                    # 查看下当前分支下的所有文件
    amalgamate  cmake  CMakeLists.txt  examples  include  LICENSE  README.md  tests
    # ls include                            # 查看下当前分支下include目录的所有文件
    crow  crow.h                            
    # git filter-branch -f --prune-empty --subdirectory-filter include  # 重要，关键步骤
    Rewrite 3081e4e1a82a4efd8feff68850c4cc04af230cd7 (101/108) (2 seconds passed, remaining 0 predicted)    
    Ref 'refs/heads/check_include_alone' was rewritten
    # ls                                    # 查看下当前分支下的所有文件
    crow  crow.h                            # 这就是原始repo中include目录下的文件
    # git log | less                        # 可以通过git log查看当前分支下的log，验证是不是仅有include目录的日志
    
现在就建立了一个干净的分支，该分支里只有include目录，及其相应的提交日志。

## 大功告成
接下来就简单了，为该分支添加新的远程repo地址，并将本地的所有文件推送上去即可。

至此，就完成了从从一个 git repo 中分离出部分目录到新的独立的 git repo上。

## 参考
[http://www.cnblogs.com/william9/archive/2012/09/01/2666767.html](http://www.cnblogs.com/william9/archive/2012/09/01/2666767.html)


