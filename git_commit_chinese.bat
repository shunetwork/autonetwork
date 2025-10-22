@echo off
REM Git中文提交脚本
REM 使用方法: git_commit_chinese.bat "提交信息"

chcp 65001 >nul
set commit_msg=%1

if "%commit_msg%"=="" (
    echo 使用方法: git_commit_chinese.bat "提交信息"
    echo 示例: git_commit_chinese.bat "修复系统日志显示问题"
    exit /b 1
)

echo %commit_msg% > commit_msg_temp.txt
git add .
git commit -F commit_msg_temp.txt
del commit_msg_temp.txt

echo 中文提交完成！
