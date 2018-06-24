# Git命令行学习  

1. 新建代码库
- 初始化本地仓库  
```git
git init
```
命令会在当前目录初始化仓库，建立.git文件夹存储git数据  
- 添加远程仓库
```git
git remote add origin location-to-your-git-repository
```
可以添加多个远程仓库，origin为远程仓库的名字
- 克隆远程仓库
在本地新建git项目跟踪远程仓库
```git
git clone location-to-your-git-repository
```

2. 配置  
- 显示当前配置信息
```git
git config --list
```
- 编辑git配置文件
```git
git config -e [--global]
```
- 设置提交代码时的用户信息
```git
git config --global user.name 'user-name'
git config --global user.email 'user-email'
```

3. 更新文件到仓库
```git
git add [file1] [file2] # 将变动添加到暂存区
git add [dir] # 将该目录下的变动添加到暂存区
git rm [file1] [file2]
git rm --cached [file] # 停止追踪文件，但该文件会保留在工作区
git mv file-from file-to # 移动文件
git status # 查看文件变动情况
vim .gitignore # 不希望跟踪的文件、目录
git diff # 比较当前文件和暂存区快照之间的差异
git diff --cached/--staged # 显示暂存区快照中的改动
git commit -m 'message-of-this-commit' # 提交暂存区代码到本地仓库
```

4. 查看提交历史  
```
git log
```
- -p选项显示每次提交的内容差异  
- -2显示最近的2次提交  
- --state显示每次提交的简略统计信息  
- --pretty=oneline 每个提交放在一行显示

5. 撤销操作
```
git commit --amend
```
提交完发现有几个文件还没有提交，或提交信息写错了，可以用该命令尝试重新提交  
该命令会将暂存区的文件提交
```
git reset # 撤销暂存区中全部文件
git reset HEAD [file1] # 撤销暂存区中的指定文件
```
将文件从暂存区中撤销

6. 远程仓库操作
- 查看远程仓库
```
git remote -v
```
- 从远程仓库抓取与拉取
```
git fetch origin
```
origin为远程仓库的名字，可以通过git remote -v命令查看  
该命令只会讲远程仓库的数据拉取到本地仓库，但不会改动当前工作区的文件  

```
git pull
```
该命令从远程仓库抓取数据并将改动合并到当前分支
- 推送到远程仓库
```
git push origin local-branch:remote-branch
```
将本地仓库的local-branch分支的commit，推送到名字为origin的远程仓库中的remote-branch分支，如果分支名相同的话可以只写一个分支名  
**只有当你有origin远程仓库的写入权限，且之前没有其它人推送过时，该命令才会生效**  ，所以在push之前一定要先fetch，然后merge其它人的修改  
- 远程仓库移除与重命名
```
git remote rename origin new-name
git remote rm origin
```

7. 打标签  

给历史中某次提交打上标签，以示重要  
- 列出标签
```
git tag
```
- 以特定模式查找标签
```
git tag -l 'v1.8.5*'
```
显示所有以v1.8.5开头的标签  
- 打轻量标签
轻量标签是对一次提交的引用
附注标签是git数据库中一个完整的对象，包括打标签者的名字、电邮地址、日期、标签message
```
git tag [tag-name]
```
- 打附注标签
```
git tag -a [tag-name] -m "tag-message"
```
- 给历史提交打标签
要给某个提交打标签，只需要在tag命令的末尾指定该次提交的校验和
```
git log --pretty=oneline # 查找到要打标签的校验和，比如9fceb02
git tag -a v1.2 9fceb02
```
- 向远程仓库推送标签
git push命令默认不会推送tag到远程仓库，需要显式推送tag
```
git push origin [tag-name] # 推送某个tag
git push origin --tags # 推送本地所有tag
```
- 检出标签
需要创建新分支，将新分支移动到标签处
```
git checkout -b [new-branch-name] [tag-name]
```
- 标签删除  
删除本地标签
```
git tag -d [tag-name]
```
如果要删除远程标签，需要先删除本地标签，然后：
```
git push origin :refs/tags/[tag-name]
```
1. 分支

- 创建分支
```
git branch [branch-name]
```
git有一个名为HEAD的特殊指针，指向当前的本地分支
- 分支切换
```
git checkout [branch-name]
```
- 分支合并    
将一个分支的修改合并到当前分支
```
git merge [hotfix]
```
- 分支删除
```
git branch -d [hotfix]
```
- 冲突处理  
分支合并时，如果2个分支修改了同一个文件，可能会造成冲突  
用git status可以查看因包含冲突而未合并的文件  
例如：
```
<<<<<<< HEAD:index.html
<div id="footer">contact : email.support@github.com</div>
=======
<div id="footer">
 please contact us at support@github.com
</div>
>>>>>>> iss53:index.html
```
=====号分隔了有冲突的部分，需要手动修改这部分代码以解决冲突  
修改完后用git add来暂存这个有冲突的文件，git就会将它们标记为已解决  
用git status再次检查是否还有未解决的冲突，没有冲突后使用git commit提交  

- 跟踪分支  
当clone一个远程仓库时，git会自动创建一个跟踪origin/master的master分支，我们也可以设置跟踪其它分支
```
git checkout --track origin/feature
```
这条命令会自动在本地创建一个名为feature的分支，并跟踪远程仓库的feature分支  
如果想为本地分支指定不同的名字，可以使用-b选项:
```
git checkout -b my-branch origin/feature
```
当然，我们也可以随意设置本地分支跟踪的远程分支，使用-u或--set-upstream-to选项运行git branch:
```
git branch -u origin/feature
git branch --set-upstream-to origin/feature
```
