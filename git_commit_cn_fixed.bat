@echo off
REM 修正版的Git中文提交脚本
chcp 65001 >nul

echo 请输入提交信息:
set /p commit_msg=
echo %commit_msg% > commit_msg_cn.txt
git add .
git commit -F commit_msg_cn.txt
del commit_msg_cn.txt
echo 中文提交完成！
