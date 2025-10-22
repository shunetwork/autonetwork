@echo off
REM 修复最近乱码提交信息的脚本
chcp 65001 >nul

echo 正在修复最近的乱码提交信息...
echo.

REM 设置Git配置
git config --global core.quotepath false
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8
git config --global core.precomposeunicode true

echo Git配置已设置完成
echo.

echo 当前最近的提交信息：
git log --oneline -5
echo.

echo 开始修复提交信息...
echo.

REM 修复最近的"ECHO is off"提交
echo 修复提交 20e44e8 (ECHO is off.)
git commit --amend -m "修正乱码提交信息：清理临时文件、更新系统日志、添加Docker部署配置"

echo.
echo 修复提交 7678cbc (ECHO is off.)
git commit --amend -m "修正乱码提交信息：清理临时文件、更新系统日志、添加Docker部署配置"

echo.
echo 修复提交 9fc7e48 (ECHO is off.)
git commit --amend -m "修正乱码提交信息：清理临时文件、更新系统日志、添加Docker部署配置"

echo.
echo 修复完成！
echo 请检查提交历史：
git log --oneline -10

echo.
echo 如果修复成功，请运行以下命令推送到远程仓库：
echo git push origin master --force-with-lease

pause
