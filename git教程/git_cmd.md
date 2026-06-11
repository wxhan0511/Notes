
## 添加链接

git remote add origin xxx

## 删除链接

git remote remove origin

## 查看新分支 你当前所在的分支

git branch

## 查看远程分支

git branch -r

## 显示本地分支及其上游分支的状态

git branch -vv

## 查看当前 Git 仓库的远程 URL

git remote -v

## git忽略CRLF警告

git config --global core.safecrlf false

## 上传

git pull origin main 其中 origin 是远程仓库名，main 是分支名。
git log origin/main..main 查看本地分支比远程多的提交（ahead）
git log main..origin/main 显示远程 origin/main 分支有但本地没有的提交。
git push -f origin main 本地分支强行覆盖远程分支（慎用，会丢弃远程分支的所有新提交）
git push -u origin main --verbose 各参数含义如下：
git push：将本地分支的提交推送到远程仓库。
-u（或 --set-upstream）：设置本地分支与远程分支的关联，后续可直接用 git push 或 git pull，无需指定远程和分支名。
origin：远程仓库的名字（默认是 origin，即你用 git remote add origin ... 添加的仓库）。
main：要推送的分支名（通常是主分支）。
--verbose:详细信息
总结：
这条命令把本地 main 分支的内容推送到远程仓库 origin 的 main 分支，并建立关联。
-u 是 --set-upstream 的简写，用于建立本地分支与远程分支的关联。
当你执行 git push -u origin main 时，Git 会把本地的 main 分支推送到远程仓库 origin 的 main 分支，并且记录下这两个分支的对应关系。
这样以后你只需输入 git push 或 git pull，Git 就知道要操作哪个远程分支，无需再写 origin main。
适用于首次推送新分支，或需要建立分支跟踪关系时。

## 拉取

git pull origin main 拉取远程分支并自动合并
git pull --rebase  先拉取远程分支，再把本地提交“挪到”远程提交之后，形成一条线性历史。
git push -u origin main
git clone --recursive -b 的含义如下：
git clone：克隆（下载）一个Git仓库到本地。
--recursive：在克隆主仓库的同时，也自动克隆所有子模块（submodule），适用于项目依赖其他Git仓库的情况。
-b <branch>：指定要克隆的分支（branch），不是默认的master/main分支。例如 -b develop 表示克隆 develop 分支。

## 提交

git commit -m "首次提交项目代码"

## 新建分支

git branch 新分支名
git switch -c dev
git checkout -b dev
git checkout -b dev

## 组织

主要分支约定（必须有）
main（或 master）：生产/发布分支，始终可发布 — 受保护（禁止直接 push，必须 PR + CI 通过）。
develop（可选）：集成分支，团队日常把 feature 合并到这里进行集成测试。也可以用 trunk（直接在 main 上短命提交，见下文）。
临时分支约定（短期、命名规范）
feature/<feature-name>：新功能或较大变更（从 develop 或 main 切出），合并回 develop。
fix/<issue-id>-<desc>：小缺陷修复（从 develop 切出），合并回 develop（必要时也合并回 main）。
hotfix/<version>-<desc>：紧急修复（直接从 main 切出，修复后合并回 main 并回合并到 develop）。
release/<version>：发布准备分支（从 develop 切出，做版本稳定、打包、生成固件和 tag），稳定后合并到 main 并打 tag。
合并策略
使用 Pull Request / Merge Request，并强制 CI（编译、单元测试、静态检查）通过后合并。
合并方式：
小变更：Squash merge（保持 main 清爽）。
大型功能：Merge commit（保留上下文）。
保证 hotfix 合并到 main 后也合并回 develop，避免回滚或丢失修复。
版本与 Tag
发布用语义化版本：vMAJOR.MINOR.PATCH（例如 v1.2.0）。
发布流程：release/<ver> -> 完成后合并到 main -> git tag -a v1.2.0 -m "release v1.2.0" -> push tag。

## 切换历史版本

git clone <https://github.com/用户名/仓库名.git>
cd 仓库名
git checkout <commit-hash>

### 保留你新建的分支（比如 fix/feature），回到 master 分支的最新版本

git checkout master
git pull origin master//你就回到了 master分支的最新状态，你的 fix/feature 分支也会保留，不会丢失。

### 从主分支（main/master）切到了历史中间版本 → 直接修改了代码 → 把修改放到master最前

假设你的提交历史如下：

```
A --- B --- C --- D --- E  (master分支)
```

你想在 `B` 后面修改并“续上”后续提交，流程如下：

1. **切换到 B 并新建分支：**

   ```
   git checkout B //切换分支或切换到某个提交,这里是切换到某个提交
   git checkout -b fix/feature   //新建一个名为 fix/feature 的分支，并切换到这个分支上。 -b:-branch 新建分支
   ```

2. **修改代码并提交：**

   ```
   git add .
   git commit -m "在B后面新增提交F"
   ```

   现在历史是：

   ```
   A --- B --- F  (fix/feature分支)
         \
          C --- D --- E  (master分支)
   ```

3. **把 master 分支后续提交合并到你的分支（rebase）：**

   ```
   git rebase master //把你当前分支上的提交，移动到 master 分支的最新提交之后
   ```

   如果有冲突，解决后继续 `git rebase --continue`。

   现在历史变成：

   ```
   A --- B --- F --- C' --- D' --- E'  (fix/feature分支)
   ```

4. **推送到远程：**

   ```
   git push origin fix/feature
   ```

---

### 图示

```
A --- B --- C --- D --- E  (main)
         \
          F               (fix/feature)
```

rebase后：

```
A --- B --- F --- C' --- D' --- E'  (fix/feature)
```

---

你可以在 `git log --oneline --graph` 看到类似的分支结构。

## 如果我修改历史上某个版本后,想跟最新版本合并后提交,怎么做

好的，假设你要在历史版本 B 后修改，并让你的修改最终**合并到 master 分支**，全步骤如下：

---

### 1. 切换到历史版本并新建分支

```sh
git checkout B
git checkout -b fix/feature
```

---

### 2. 修改代码并提交

```sh
git add .
git commit -m "在B后面新增提交F"
```

---

### 3. 把 master 分支后续提交合并到你的分支（rebase）

```sh
git rebase master
```

如果有冲突，解决冲突后执行：改同一行、删和改同一行、同一位置都新增，都会冲突

```sh
git add .
git rebase --continue
```

直到 rebase 完成。

---

### 4. 切换回 master 分支并拉取最新

```sh
git checkout master
git pull origin master
```

---

### 5. 合并你的修改到 master

```sh
git merge fix/feature
```

---

### 6. 推送 master 到远程

```sh
git push origin master
```

---

### 总结流程图

```
A --- B --- C --- D --- E  (master)
         \
          F               (fix/feature, rebase前)
```

rebase后：

```
A --- B --- C --- D --- E --- F'  (fix/feature)
```

合并到 master 后：

```
A --- B --- C --- D --- E --- F  (master)
```

---

这样你的修改就会排在 master 的最新提交之后，并且已经推送到远程 master 分支。

## 修改注释

git checkout master  进入当前分支
git reset --hard fdf3b3b  回到最新版本
git rebase -i HEAD~3  显示最近几(3)个注释
在弹出的窗口里，确保能看到你想改的那个 commit，以及它后面的所有 commits。只把你想改的那行 pick 换成 reword，其他的 pick 不要动
git push origin master --force 推送到远程

## vscode源代码管理

在 VS Code 的 Git 源代码管理面板中，这几个选项的区别如下：

提交 (Commit):
将你暂存的更改保存到本地仓

库。这只是在本地创建一个快照，不会影响远程服务器。

提交 (修改) (Commit (Amend)):
将当前的更改合并到上一次提交中，而不是创建一个新的提交。通常用于修复上一个提交中的小错误或修改提交信息。

提交和推送 (Commit & Push):
先执行本地提交，然后立即将本地分支的提交上传到远程仓库（如 GitHub 或 GitLab）。

提交和同步 (Commit & Sync):
先执行本地提交，然后执行“同步”操作。同步通常包括从远程仓库拉取 (Pull) 最新的更改，然后再将你的本地更改推送 (Push) 到远程。这可以确保你的本地代码与服务器保持一致。

## git pull

### 完全覆盖本地

git checkout master
git fetch origin
<!-- git fetch：从远程拉取元数据（不合并）
origin：远程仓库名 -->
 <!-- 只更新了"远程追踪分支"，你的工作目录还是原样 -->
git reset --hard origin/master
<!-- git reset：重置当前分支到某个状态
--hard：彻底重置，包括：
重置 HEAD 指针
重置暂存区
重置工作目录（本地文件全部覆盖）
origin/master：目标位置（远程 master -->
<!-- 用远程 master 的内容完全覆盖你的本地 master，所有本地改动全部丢失。 -->
git clean -fd
<!-- git clean：删除未被 Git 追踪的文件
-f（force）：强制删除
-d（directory）：也删除未追踪的目录
完整含义：
删除你工作目录里所有 Git 不知道的文件和文件夹 -->
## 删除最近一次提交,再提交(上次提交不全)

情况 1：只在本地，还没 push
git reset --hard HEAD~1
<!-- git reset：重置当前分支
--hard：彻底重置（包括工作目录、暂存区、HEAD 指针）
HEAD~1：上一个提交 -->
<!-- 提交历史：A --- B --- C  (HEAD 在 C)

执行 git reset --hard HEAD~1 后：
提交历史：A --- B  (HEAD 回到 B)

C 被完全删除 -->
情况 2：已经 push 到远程，要删除并重新 push
git reset --hard HEAD~1
git push -f origin master

删掉远程最后一次提交，但保留本地代码用于重提
git reset --soft HEAD~1
git push --force-with-lease origin master
<!-- #然后重新 commit 再 push -->
如果已经误用 --hard，可：
git reflog
直接回到那个提交（覆盖当前
git reset --hard f50d717

 <!-- 只移动 HEAD 到上一个提交
不改动暂存区（index）
不改动工作区（working tree）
最近一次提交被撤销了
那次提交里的改动仍然是 staged（已暂存）-->
git reset --soft HEAD~1
<!-- 撤销最近一次提交 -->

<!-- 在 Git 里，工作区和暂存区是两层：

工作区（Working Directory）
你实际编辑文件的地方（VS Code 里改代码就是改这里）。

暂存区（Staging Area / Index）
一个“待提交清单”。你用 git add 选中的改动会先放这里，git commit 只提交这里的内容。

流程关系
改文件 → 在工作区
git add → 进入暂存区
git commit → 生成提交（进入仓库历史） -->
（可选）如果你想先取消暂存再挑文件提交
git reset

重新提交当前代码
git add .
git commit -m "重新提交当前代码"

 推送
git push origin master

# 本地查看历史

git log --oneline --graph --decorate
<!-- 参数	含义
--oneline	每个提交只显示一行（短哈希 + 提交信息），输出更紧凑
--graph	在左侧用 ASCII 字符画出分支合并的树形结构（* / \ `
--decorate	显示每个提交上的标签（tag）、分支名、HEAD 指向等引用信息 -->

## 解决冲突后

git diff main...work-oneshot
