@echo off
REM 修复特定乱码提交信息的脚本
chcp 65001 >nul

echo 正在修复特定的乱码提交信息...
echo.

REM 设置Git配置
git config --global core.quotepath false
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8
git config --global core.precomposeunicode true

echo Git配置已设置完成
echo.

echo 当前需要修复的乱码提交：
echo 20e44e8 ECHO is off.
echo 7678cbc ECHO is off.
echo 9fc7e48 ECHO is off.
echo.

echo 开始修复...
echo.

REM 创建正确的提交信息
echo 修正乱码提交信息：清理临时文件、更新系统日志、添加Docker部署配置 > commit_msg_fix.txt

echo 使用git rebase修复提交信息...
echo 注意：这将重写Git历史
echo.

REM 从最早的乱码提交开始修复
echo 修复提交 9fc7e48...
git rebase -i 9fc7e48~1

echo.
echo 修复完成！
echo 请检查提交历史：
git log --oneline -15

echo.
echo 如果修复成功，请运行以下命令推送到远程仓库：
echo git push origin master --force-with-lease

pause
