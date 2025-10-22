@echo off
REM 直接修复乱码提交信息的脚本
chcp 65001 >nul

echo ========================================
echo Git乱码提交信息修复脚本 (直接版)
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

echo 使用git commit --amend修复最近的提交...
echo 这将修复最近的乱码提交信息
echo.

REM 创建正确的提交信息文件
echo 修正乱码提交信息：清理临时文件、更新系统日志、添加Docker部署配置 > commit_msg_correct.txt

REM 修复最近的提交
git commit --amend -F commit_msg_correct.txt

echo.
echo 清理临时文件...
del commit_msg_correct.txt

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
