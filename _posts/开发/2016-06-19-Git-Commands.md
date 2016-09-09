---
layout: post

title: Git常用命令备忘

category: 开发

tags: Git

keywords: Git GitHub 分支

description: 本文介绍了我在使用Git过程中记录下来的一些常用git 命令。

---

先上一张图作为引言

![一个git流程](http://i.imgur.com/S9pcYfs.jpg)

## Git配置
    git config --global user.name "xusd-null"
    git config --global user.email "xxyy@xxy.com"
    git config --global color.ui true
    git config --global alias.co checkout
    git config --global alias.ci commit
    git config --global alias.st status
    git config --global alias.br branch
    git config --global core.editor "vim"    # 设置Editor使用vim
    git config -l  # 列举所有配置

用户的git配置文件在`~/.gitconfig`

## Git常用命令

### git clone、commit、rm、add、status（克隆、查看、添加、提交、删除、找回、重置、修改）

    git clone repo      # clone某一repo
    git clone repo  local_dir     # clone某一repo到本地local_dir下
    # git clone支持多种协议，除了HTTP(s)以外，还支持SSH、Git、本地文件协议等，下面是一些例子。
    git clone http[s]://example.com/path/to/repo.git/
    git clone ssh://example.com/path/to/repo.git/
    git clone git://example.com/path/to/repo.git/
    git clone /opt/git/project.git
    git clone file:///opt/git/project.git
    git clone [user@]example.com:path/to/repo.git/

    git help <command>  # 显示command的help
    git show            # 显示某次提交的内容
    git show $id

    git co  -- <file>   # 抛弃工作区修改
    git co  .           # 抛弃工作区修改

    git add <file>      # 将工作文件修改提交到本地暂存区
    git add .           # 将所有修改过的工作文件提交暂存区

    git rm <file>       # 从版本库中删除文件
    git rm <file> --cached  # 从版本库中删除文件，但不删除文件

    git reset <file>    # 从暂存区恢复到工作文件
    git reset -- .      # 从暂存区恢复到工作文件
    git reset --hard    # 恢复最近一次提交过的状态，即放弃上次提交后的所有本次修改

    git ci <file>
    git ci .
    git ci -a           # 将git add, git rm和git ci等操作都合并在一起做
    git ci -am "some comments"
    git ci --amend      # 修改最后一次提交记录

    git revert <$id>    # 恢复某次提交的状态，恢复动作本身也创建了一次提交对象
    git revert HEAD     # 恢复最后一次提交的状态

    git status          # 查看状态
### 撤销(checkout)
	
	git reset --hard 3628164        # 版本回退 只需要添加commit版本号的前几位	
	git checkout [file]             # 恢复暂存区的指定文件到工作区	
	git checkout [commit] [file]    # 恢复某个commit的指定文件到工作区	
	git checkout .                  # 恢复上一个commit的所有文件到工作区	 
	git reset commit号 filename     # 对某个文件进行版本回退	
	git reset [file]                # 重置暂存区的指定文件，与上一次commit保持一致，但工作区不变	
	git reset --hard                # 重置暂存区与工作区，与上一次commit保持一致
	git reset [commit]              # 重置当前分支的指针为指定commit，同时重置暂存区，但工作区不变
	git reset --hard [commit]       # 重置当前分支的HEAD为指定commit，同时重置暂存区和工作区，与指定commit一致	
	git reset --keep [commit]       # 重置当前HEAD为指定commit，但保持暂存区和工作区不变
	# 新建一个commit，用来撤销指定commit，后者的所有变化都将被前者抵消，并且应用到当前分支
	$ git revert [commit]
	
### git diff  
    git diff
    git diff <file>     # 比较当前文件和暂存区文件差异
    git diff <$id1> <$id2>   # 比较两次提交之间的差异
    git diff <branch1>..<branch2> # 在两个分支之间比较
    git diff --staged   # 比较暂存区和版本库差异
    git diff --cached   # 比较暂存区和版本库差异
    git diff --stat     # 仅仅比较统计信息

### git log  
	git log				# 使用默认格式显示完整地项目历史。如果输出超过一屏，你可以用空格键来滚动，按q退出
	git log -n <limit>  # 用<limit>限制提交的数量。比如git log -n 3只会显示3个提交
	git log --oneline   # 将每个提交压缩到一行。当你需要查看项目历史的上层情况时这会很有用
    git log <file>      # 只显示包含特定文件的提交。查找特定文件的历史这样做会很方便
	git log -p          # 显示代表每个提交的一堆信息。显示每个提交全部的差异(diff)，这也是项目历史中最详细的视图
    git log -p <file>   # 查看每次详细修改内容的diff
    git log -p -2       # 查看最近两次详细修改内容的diff
    git log --stat      # 查看提交统计信息，除了git log信息之外，包含哪些文件被更改了，以及每个文件相对的增删行数
	git log --stat -n 5 # 简单的列出了修改过的文件
	git log --author="<pattern>"  # 搜索特定作者的提交。<pattern>可以是字符串或正则表达式。
	git log --grep="<pattern>"    # 搜索提交信息匹配特定<pattern>的提交。<pattern>可以是字符串或正则表达式。
	git log <since>..<until>      # 只显示发生在<since>和<until>之间的提交。两个参数可以是提交ID、分支名、HEAD或是任何一种引用。
	git log --graph 		# ASCII 字符串表示的简单图形，形象地展示了每个提交所在的分支及其分化衍合情况
	git log --all --decorate --graph
	git log --pretty=oneline #  只显示哈希值和提交说明
	git log --pretty=oneline/short/full/fuller/format:""(格式等)
	git log --name-only # 仅在提交信息后显示已修改的文件清单
	git log --no-merges # 不显示merge的log
	git log --graph --decorate --oneline ：--graph标记会绘制一幅字符组成的图形，左边是提交，右边是提交信息。--decorate标记会加上提交所在的分支名称和标签。--oneline标记将提交信息显示在同一行，一目了然。
	git log --author="John Smith" -p hello.py  这个命令会显示John Smith作者对hello.py文件所做的所有更改的差异比较(diff)。 
	git log --name-status -n 5 --no-merges path/filename # 显示新增、修改、删除的文件清单(不包含merge的log)
	git log --name-status --skip=5 -n 5 --no-merges path/filename # 略过5条,从第6条开始取5条log
	git log --all --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit --date=relative  # 更直观的log显示

## Git 分支管理

### git branch

    git branch -r           # 查看远程分支
	git branch -a           # 查看所有分支
    git branch <new_branch> # 创建新的分支
    git branch -v           # 查看各个分支最后提交信息
    git branch --merged     # 查看已经被合并到当前分支的分支
    git branch --no-merged  # 查看尚未被合并到当前分支的分支

	git co              # 后面不跟任何参数，则就是对工作区进行检查
    git co <branch>     # 切换到某个分支
    git co -b <new_branch> # 创建新的分支，并且切换过去
    git co -b <new_branch> <branch>  # 基于branch创建新的new_branch

    git co $id          # 把某次历史提交记录checkout出来，但无分支信息，切换到其他分支会自动删除
    git co $id -b <new_branch>  # 把某次历史提交记录checkout出来，创建成一个分支

    git branch -d <branch>  # 删除某个分支
    git branch -D <branch>  # 强制删除某个分支 (未被合并的分支被删除的时候需要强制)

### git push、pull
    git pull                         # 抓取远程仓库所有分支更新并合并到本地
    git pull --no-ff                 # 抓取远程仓库所有分支更新并合并到本地，不要快进合并
    git fetch origin                 # 抓取远程仓库更新
    git merge origin/master          # 将远程主分支合并到本地当前分支
    git co --track origin/branch     # 跟踪某个远程分支创建相应的本地分支
    git co -b <local_branch> origin/<remote_branch>  # 基于远程分支创建本地分支，功能同上

    git push                         # push所有分支
    git push origin master           # 将本地主分支推到远程主分支
    git push -u origin master        # 将本地主分支推到远程(如无远程主分支则创建，用于初始化远程仓库)
    git push origin <local_branch>   # 创建远程分支， origin是远程仓库名
    git push origin <local_branch>:<remote_branch>  # 创建远程分支
    git push origin :<remote_branch>  #先删除本地分支(git br -d <branch>)，然后再push删除远程分支


    git pull <远程主机名> <远程分支名>:<本地分支名>
	git push <远程主机名> <本地分支名>:<远程分支名>
                           from         to 
	git pull origin master:master     取回origin主机的master分支，与本地的master分支合并
	git pull origin master  如果远程分支是与当前分支合并，则冒号后面的部分可以省略。 
 
	git push origin master:master   推送本地的master分支，与origin主机的master分支合并
 	git push origin master          本地的master分支推送到origin主机的master分支。如果后者不存在，则会被新建
 	
	git pull origin				    本地的当前分支自动与对应的origin主机”追踪分支”(remote-tracking branch)进行合并。追踪分支 是 远程的同名分支
 	git push origin					当前分支与远程分支之间存在追踪关系，则本地分支和远程分支都可以省略
 	git pull						当前分支自动与唯一一个追踪分支进行合并
 	git push						当前分支只有一个追踪分支，那么主机名都可以省略

### git merge  
    git merge <branch>               # 将branch分支合并到当前分支
	默认情况下，git合并使用"fast forward”模式，相当于直接把master分支指向dev分支。删除分支后，分支信息也随即丢失。在合并的时候附
	上参数 --no-ff就可以禁用fast-forward合并模式。这样在master上能生成一个新的节点，意味着master保留的分支信息，而这种合并方式是我们希望采用的。
	git merge --no-ff <branch>
    git merge origin/master --no-ff  # 不要Fast-Foward合并，这样可以生成merge提交
    
### git rebase
    git rebase master <branch>       # 将master rebase到branch，相当于：
    git co <branch> && git rebase master && git co master && git merge <branch>
比如：  

    git checkout mywork
    git rebase origin
这些命令会把你的"mywork"分支里的每个提交(commit)取消掉，并且把它们临时 保存为补丁(patch)(这些补丁放到".git/rebase"目录中),然后把"mywork"分支更新到最新的"origin"分支，最后把保存的这些补丁应用到"mywork"分支上
 
在rebase的过程中，也许会出现冲突(conflict)。在这种情况下，Git会停止rebase并会让你去解决冲突；在解决完冲突后，用"git-add"命令去更新这些内容的索引(index)，然后，你无需执行 git-commit，只要执行: `git rebase --continue`，这样git会继续应用(apply)余下的补丁。
 
在任何时候，你可以用--abort参数来终止rebase的行动，并且"mywork" 分支会回到rebase开始前的状态。
$ git rebase --abort
    
## git remote（Git远程仓库管理）

    git remote -v                    # 查看远程服务器地址和仓库名称
    git remote show <主机名>          # 查看该主机的详细信息
    git remote show origin           # 查看远程服务器仓库状态
    git remote add <主机名> <网址>    # 添加远程主机
    git remote add origin git@github.com:cplusplus-study/fork_stl.git         # 添加远程仓库地址
    git remote set-url origin git@github.com:cplusplus-study/fork_stl.git # 设置远程仓库地址(用于修改远程仓库地址)
    git remote rm <repository>       # 删除远程仓库
	git remote rename <原主机名> <新主机名> # 重命名远程主机
### 创建远程仓库
    git clone --bare robbin_site robbin_site.git  # 用带版本的项目创建纯版本仓库
    scp -r my_project.git git@git.csdn.net:~      # 将纯仓库上传到服务器上

    mkdir robbin_site.git && cd robbin_site.git && git --bare init # 在服务器创建纯仓库
    git remote add origin git@github.com:robbin/robbin_site.git    # 设置远程仓库地址
    git push -u origin master                                      # 客户端首次提交
    git push -u origin develop  # 首次将本地develop分支提交到远程develop分支，并且track

    git remote set-head origin master   # 设置远程仓库的HEAD指向master分支

也可以命令设置跟踪远程库和本地库

    git branch --set-upstream master origin/master
    git branch --set-upstream develop origin/develop

## Git补丁管理(方便在多台机器上开发同步时用)
    git diff > ../sync.patch         # 生成补丁
    git apply ../sync.patch          # 打补丁
    git apply --check ../sync.patch  # 测试补丁能否成功

## git stash（暂存管理）
    git stash                        # 暂存，保存工作现场
    git stash list                   # 列出所有stash
    # do some work ....
	git pop 	  					 # 返回工作现场
    git stash apply                  # 恢复暂存的内容
	git stash pop stash@{num} 	     # num就是list中要恢复的工作现场编号,使用pop命令恢复的工作现场，其对应的stash 在队列中删除
	git stash apply stash@{num}	     # num就是list中要恢复的工作现场编号,使用apply命令恢复的工作现场，其对应的stash 在队列中不删除
    git stash drop                   # 删除暂存区
	git stash clear					 # 清空 stash 队列

## 其他小技巧
 
### 1. 统计代码行数
    git ls-files | xargs wc -l  # 统计代码行数
    git ls-files | grep .py | xargs wc -l # 统计python代码行数

### 2. 解决每次push都要求用户名密码的限制
正常每次提交都需要输入用户名和密码，比较烦，可以修改配置文件来避免。 要修改的文件即是： .git/config 文件，通常是这个样子：
	
	[remote "origin"]
		url = https://github.com/xxxx/xxxxxxx-repo
		fetch = +refs/heads/*:refs/remotes/origin/*

将其中的url改为：

	url = https://your-username:your-password@github.com/xxxx/xxxxxxx-repo

### 3. 在github上同步一个分支(fork)
- 设置  

在同步之前，需要创建一个远程点指向上游仓库(repo).如果你已经派生了一个原始仓库，可以按照如下方法做。

	$ git remote -v	  
	  List the current remotes （列出当前远程仓库）  
	  origin  https://github.com/user/repo.git (fetch)	  
	  origin  https://github.com/user/repo.git (push)	  
	$ git remote add upstream https://github.com/otheruser/repo.git	  
	  Set a new remote (设置一个新的远程仓库)	  
	$ git remote -v	  
	  Verify new remote (验证新的原唱仓库)	  
	  origin    https://github.com/user/repo.git (fetch)	  
      origin    https://github.com/user/repo.git (push)	  
	  upstream  https://github.com/otheruser/repo.git (fetch)	  
	  upstream  https://github.com/otheruser/repo.git (push)

- 同步  

同步上游仓库到你的仓库需要执行两步：首先你需要从远程拉去，之后你需要合并你希望的分支到你的本地副本分支。

- 拉取

从远程仓库拉取将取回其分支以及各自的提交。它们将存储在你本地仓库的指定分之下。  

	$ git fetch upstream  
	  Grab the upstream remote's branches  
	  remote: Counting objects: 75, done.  
	  remote: Compressing objects: 100% (53/53), done.  
	  remote: Total 62 (delta 27), reused 44 (delta 9)  
	  Unpacking objects: 100% (62/62), done.  
	  From https://github.com/otheruser/repo  
	  * [new branch]      master     -> upstream/master  
现在我们把上游master保存到了本地仓库，upstream/master

	$ git branch -va
	  List all local and remote-tracking branches
	  * master                  a422352 My local commit
	  remotes/origin/HEAD     -> origin/master
	  remotes/origin/master   a422352 My local commit
	  remotes/upstream/master 5fdff0f Some upstream commit
- 合并  

现在我们已经拉取了上游仓库，我们将要合并其变更到我们的本地分支。这将使该分支与上游同步，而不会失去我们的本地更改。

    $ git checkout master
	  Check out our local master branch
	  Switched to branch 'master'
	$ git merge upstream/master
	  Merge upstream's master into our own
	  Updating a422352..5fdff0f
	  Fast-forward
	  README                    |    9 -------
	  README.md                 |    7 ++++++
	  2 files changed, 7 insertions(+), 9 deletions(-)
	  delete mode 100644 README
	  create mode 100644 README.md
如果您的本地分支没有任何独特的提交，Git会改为执行“fast-forward”。

	$ git merge upstream/master
	  Updating 34e91da..16c56ad
	  Fast-forward
	  README.md                 |    5 +++--
	  1 file changed, 3 insertions(+), 2 deletions(-)
最后将本地变更推送到远程服务器即可。

## Reference  
[Syncing a fork](https://help.github.com/articles/syncing-a-fork/)  