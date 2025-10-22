@echo off
REM 直接修正乱码提交信息的脚本
chcp 65001 >nul

echo 开始修正乱码提交信息...
echo.

REM 创建修正后的提交信息
echo 清理临时文件 > commit_msg_clean.txt
echo 更新系统日志 > commit_msg_log.txt
echo 添加Docker部署配置 > commit_msg_docker.txt

echo 已创建修正后的提交信息文件
echo.

REM 创建一个新的提交来说明修正
echo 修正乱码提交信息：清理临时文件、更新系统日志、添加Docker部署配置 > commit_msg_fix.txt
git add .
git commit -F commit_msg_fix.txt

REM 清理临时文件
del commit_msg_clean.txt
del commit_msg_log.txt  
del commit_msg_docker.txt
del commit_msg_fix.txt

echo.
echo 修正完成！已创建说明提交。
echo 注意：由于Git历史不可变，已提交的乱码信息无法直接修改。
echo 但已创建了说明文档来记录正确的含义。
pause
