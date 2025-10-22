@echo off
REM 修正乱码提交信息的脚本
chcp 65001 >nul

echo 开始修正乱码提交信息...
echo.

REM 创建修正后的提交信息文件
echo 清理临时文件 > commit_msg_clean.txt
echo 更新系统日志 > commit_msg_log.txt  
echo 添加Docker部署配置 > commit_msg_docker.txt

echo 已创建修正后的提交信息文件
echo.
echo 现在开始修正提交信息...

REM 使用交互式rebase来修正提交信息
echo 正在启动交互式rebase...
git rebase -i HEAD~10

echo.
echo 修正完成！
pause
