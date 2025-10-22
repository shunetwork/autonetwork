@echo off
REM 最终修复乱码提交信息的脚本
chcp 65001 >nul

echo 正在修复Git提交历史中的乱码信息...
echo.

REM 设置Git配置
git config --global core.quotepath false
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8
git config --global core.precomposeunicode true

echo Git配置已设置完成
echo.

REM 创建临时文件来存储正确的提交信息
echo 创建正确的提交信息文件...

echo 修正乱码提交信息：清理临时文件、更新系统日志、添加Docker部署配置 > commit_msg_fix1.txt
echo 修正乱码提交信息：清理临时文件、更新系统日志、添加Docker部署配置 > commit_msg_fix2.txt
echo 修正乱码提交信息：清理临时文件、更新系统日志、添加Docker部署配置 > commit_msg_fix3.txt

echo.
echo 开始修复提交信息...
echo.

REM 使用git rebase来修复提交信息
echo 正在执行交互式rebase来修复提交信息...
echo 请按照提示操作：
echo 1. 对于每个要修改的提交，选择 'reword' 或 'r'
echo 2. 输入正确的中文提交信息
echo 3. 保存并继续

git rebase -i HEAD~10

echo.
echo 修复完成！
echo 请检查提交历史是否正确：
git log --oneline -10

echo.
echo 如果修复成功，请运行以下命令推送到远程仓库：
echo git push origin master --force-with-lease

pause
