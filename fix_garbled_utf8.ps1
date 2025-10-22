# 修正乱码提交信息的UTF-8脚本
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 创建UTF-8编码的提交信息
$commitMessage = "修正乱码提交信息：添加Docker部署配置、测试中文提交信息、清理临时文件"
[System.IO.File]::WriteAllText("commit_msg_utf8.txt", $commitMessage, [System.Text.Encoding]::UTF8)

# 提交更改
git add .
git commit -F commit_msg_utf8.txt

# 清理临时文件
Remove-Item "commit_msg_utf8.txt" -ErrorAction SilentlyContinue

Write-Host "乱码提交信息修正完成！"
