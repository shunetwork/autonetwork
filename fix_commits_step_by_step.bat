@echo off
REM 逐步修复乱码提交信息的脚本
chcp 65001 >nul

echo 正在逐步修复Git提交历史中的乱码信息...
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

echo 开始逐步修复...
echo.

echo 步骤1：修复提交 9fc7e48 (ECHO is off.)
echo 这将启动交互式rebase，请按照提示操作
echo 按任意键继续...
pause

git rebase -i 9fc7e48~1

echo.
echo 步骤2：修复提交 7678cbc (ECHO is off.)
echo 按任意键继续...
pause

git rebase -i 7678cbc~1

echo.
echo 步骤3：修复提交 20e44e8 (ECHO is off.)
echo 按任意键继续...
pause

git rebase -i 20e44e8~1

echo.
echo 修复完成！
echo 请检查提交历史：
git log --oneline -15

echo.
echo 如果修复成功，请运行以下命令推送到远程仓库：
echo git push origin master --force-with-lease

echo.
echo 按任意键退出...
pause
