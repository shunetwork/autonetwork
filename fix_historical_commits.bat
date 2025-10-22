@echo off
REM 修复历史乱码提交信息的脚本
chcp 65001 >nul

echo 正在修复Git历史中的乱码提交信息...
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

echo 开始修复...
echo.

REM 创建正确的提交信息文件
echo 修正乱码提交信息：清理临时文件、更新系统日志、添加Docker部署配置 > commit_msg_correct.txt

echo 使用git rebase来修复历史提交...
echo 注意：这将重写Git历史，请确保没有其他人正在使用这个仓库
echo.

REM 启动交互式rebase
echo 正在启动交互式rebase...
echo 请按照以下步骤操作：
echo 1. 在编辑器中，找到要修改的提交行
echo 2. 将 'pick' 改为 'reword' 或 'r'
echo 3. 保存并退出编辑器
echo 4. 在下一个编辑器中输入正确的中文提交信息
echo 5. 保存并退出
echo 6. 重复步骤4-5直到所有提交都修复完成
echo.

git rebase -i HEAD~15

echo.
echo 修复完成！
echo 请检查提交历史：
git log --oneline -15

echo.
echo 如果修复成功，请运行以下命令推送到远程仓库：
echo git push origin master --force-with-lease

pause
