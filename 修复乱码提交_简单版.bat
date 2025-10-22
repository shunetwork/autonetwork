@echo off
REM 简单修复乱码提交信息的脚本
chcp 65001 >nul

echo ========================================
echo Git乱码提交信息修复脚本
echo ========================================
echo.

echo 正在设置Git配置...
git config --global core.quotepath false
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8
git config --global core.precomposeunicode true
echo Git配置设置完成！
echo.

echo 当前需要修复的乱码提交：
git log --oneline --grep="ECHO is off" -10
echo.

echo 开始修复...
echo.

REM 设置环境变量来抑制警告
set FILTER_BRANCH_SQUELCH_WARNING=1

echo 使用git filter-branch修复提交信息...
echo 这将自动修复所有包含"ECHO is off"的提交信息
echo.

REM 创建修复脚本
echo #!/bin/sh > fix_commit_msg.sh
echo if echo "$1" ^| grep -q "ECHO is off"; then >> fix_commit_msg.sh
echo   echo "修正乱码提交信息：清理临时文件、更新系统日志、添加Docker部署配置" >> fix_commit_msg.sh
echo else >> fix_commit_msg.sh
echo   cat >> fix_commit_msg.sh
echo fi >> fix_commit_msg.sh

REM 执行修复
git filter-branch --msg-filter "fix_commit_msg.sh" -- --all

echo.
echo 清理临时文件...
del fix_commit_msg.sh

echo.
echo ========================================
echo 修复完成！
echo ========================================
echo.

echo 修复后的提交历史：
git log --oneline -15

echo.
echo 如果修复成功，请运行以下命令推送到远程仓库：
echo git push origin master --force-with-lease
echo.

echo 按任意键退出...
pause
