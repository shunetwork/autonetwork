@echo off
REM 重新提交乱码信息的脚本
chcp 65001 >nul

echo 开始重新提交乱码信息...
echo.

REM 创建正确的中文提交信息
echo 添加Docker部署配置 > commit_msg_docker.txt
echo 测试中文提交信息 > commit_msg_test.txt
echo 清理临时文件 > commit_msg_clean.txt

echo 已创建正确的中文提交信息文件
echo.

REM 使用正确的中文信息重新提交
echo 重新提交乱码信息：添加Docker部署配置、测试中文提交信息、清理临时文件 > commit_msg_recommit.txt
git add .
git commit -F commit_msg_recommit.txt

REM 清理临时文件
del commit_msg_docker.txt
del commit_msg_test.txt
del commit_msg_clean.txt
del commit_msg_recommit.txt

echo.
echo 重新提交完成！现在使用正确的中文信息。
pause
