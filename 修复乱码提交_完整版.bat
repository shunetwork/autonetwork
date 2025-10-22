@echo off
REM 修复所有乱码提交信息的完整脚本
chcp 65001 >nul

echo ========================================
echo Git乱码提交信息修复脚本
echo ========================================
echo.

echo 正在设置Git配置...
git config --global core.quotepath false
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8
git config --global core.precomposeunicode true
echo Git配置设置完成！
echo.

echo 当前需要修复的乱码提交：
git log --oneline --grep="ECHO is off" -10
echo.

echo 开始修复...
echo.

echo 使用git rebase修复提交信息...
echo 这将启动交互式rebase，请按照以下步骤操作：
echo.
echo 步骤1: 在编辑器中，找到要修改的提交行（包含"ECHO is off"的提交）
echo 步骤2: 将 'pick' 改为 'reword' 或 'r'
echo 步骤3: 保存并退出编辑器
echo 步骤4: 在下一个编辑器中输入正确的中文提交信息：
echo        "修正乱码提交信息：清理临时文件、更新系统日志、添加Docker部署配置"
echo 步骤5: 保存并退出
echo 步骤6: 重复步骤4-5直到所有提交都修复完成
echo.

echo 按任意键开始修复...
pause

REM 启动交互式rebase
git rebase -i HEAD~15

echo.
echo ========================================
echo 修复完成！
echo ========================================
echo.

echo 修复后的提交历史：
git log --oneline -15

echo.
echo 如果修复成功，请运行以下命令推送到远程仓库：
echo git push origin master --force-with-lease
echo.

echo 按任意键退出...
pause
