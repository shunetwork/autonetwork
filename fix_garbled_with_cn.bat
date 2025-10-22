@echo off
REM 使用中文提交脚本修正乱码信息
chcp 65001 >nul

echo 正在修正乱码提交信息...
echo.

REM 创建正确的中文提交信息
echo 修正乱码提交信息：添加Docker部署配置、测试中文提交信息、清理临时文件 > commit_msg_fix.txt

echo 使用正确的中文信息重新提交...
git add .
git commit -F commit_msg_fix.txt

REM 清理临时文件
del commit_msg_fix.txt

echo.
echo 乱码提交信息修正完成！
echo 现在使用正确的中文信息：修正乱码提交信息：添加Docker部署配置、测试中文提交信息、清理临时文件
pause
