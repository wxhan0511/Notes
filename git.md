## GitHub 加速神器
eg. 
git clone https://gitclone.com/github.com/STMicroelectronics/stm32-usbx-examples.git
## SSH KEY(Secure Shell protocol) 适用于linux
1、下载
Git-2.51.2-64-bit.exe适用于windows
2、生成公钥和私钥
ssh-keygen -t ed25519 -C "wxhan0511@outlook.com"
这里的-t参数用于指定密钥对的签名算法，-C参数后面输入你的邮箱地址作为注释，方便日后识别这个公钥。
windows下保存路径如下
Your identification has been saved in /c/Users/A0004363/.ssh/id_ed25519
Your public key has been saved in /c/Users/A0004363/.ssh/id_ed25519.pub
3、公钥复制到github中
接下来，系统会要求你输入密钥对的密码，如果不希望设置密码，直接回车即可。创建完成后，私钥内容需要自己妥善保存，不要泄露给他人。
然后，你需要将公钥内容粘贴到GitHub中。登录到你的GitHub或Gitee账户，在个人设置中找到“安全设置”–“SSH公钥”，将公钥内容粘贴到相应的位置，并保存设置
4、git remote add origin xxx（SSH链接）
5、加密算法保护原理（ed25519。。。）公钥用作加密，私钥则用作解密。下面反的
    A[你电脑] -->|1. 发起连接| B(GitHub服务器)
    B -->|2. 发来随机挑战码| A
    A -->|3. 用私钥加密挑战码| A
    A -->|4. 发回加密结果| B
    B -->|5. 用公钥解密，验证通过| B
    B -->|6. 允许 push| A
## 保存密码
git config --global credential.helper wincred
让 Git 使用 Windows 的“凭据管理器”（wincred）来保存和自动填写你的 Git 远程仓库账号和密码（或 Token）。
设置为全局（--global），对所有仓库有效。
这样你首次输入账号密码后，后续推送、拉取等操作会自动读取，无需重复输入。
简而言之：
这条命令让 Git 在 Windows 下自动记住你的认证信息，提高操作效率。
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