@echo off
chcp 65001 >nul
echo 测试中文提交信息：验证批处理脚本中文支持 > commit_msg_bat.txt
git add .
git commit -F commit_msg_bat.txt
del commit_msg_bat.txt
