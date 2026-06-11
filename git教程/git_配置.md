
## windows SSH KEY(Secure Shell protocol)
1)、下载
Git-2.51.2-64-bit.exe适用于windows
2)、生成公钥和私钥
ssh-keygen -t ed25519 -C "wxhan0511@outlook.com"
这里的-t参数用于指定密钥对的签名算法，-C参数后面输入你的邮箱地址作为注释，方便日后识别这个公钥。
windows下保存路径如下
Your identification has been saved in /c/Users/A0004363/.ssh/id_ed25519
Your public key has been saved in /c/Users/A0004363/.ssh/id_ed25519.pub
3)、公钥复制到github中
接下来，系统会要求你输入密钥对的密码，如果不希望设置密码，直接回车即可。创建完成后，私钥内容需要自己妥善保存，不要泄露给他人。
然后，你需要将公钥内容粘贴到GitHub中。登录到你的GitHub或Gitee账户，在个人设置中找到“安全设置”–“SSH公钥”，将公钥内容粘贴到相应的位置，并保存设置  注意要是SSH链接
git config --global core.sshCommand "C:/Windows/System32/OpenSSH/ssh.exe -i C:/Users/A0004363/.ssh/id_ed25519 -o UserKnownHostsFile=C:/Users/A0004363/.ssh/known_hosts -o StrictHostKeyChecking=accept-new"

4)、git remote add origin xxx（SSH链接）

## debian SSH配置
1) 创建 .ssh 并生成新密钥
mkdir -p ~/.ssh
chmod 700 ~/.ssh
ssh-keygen -t ed25519 -C "你的GitHub邮箱"

一路回车即可，默认会生成：
~/.ssh/id_ed25519
~/.ssh/id_ed25519.pub

2) 启动 ssh-agent 并加载私钥
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

3) 输出公钥，复制整行内容
cat ~/.ssh/id_ed25519.pub
把第 3 步输出的公钥粘到：
GitHub → Settings → SSH and GPG keys → New SSH key
ssh -T git@github.com
cd ~/hwx
git clone git@github.com:wxhan0511/GCV5_SERVICE.git