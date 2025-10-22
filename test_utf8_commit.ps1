# 设置PowerShell编码为UTF-8
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 创建UTF-8编码的提交信息文件
$commitMessage = "测试中文提交信息：验证UTF-8编码修复"
[System.IO.File]::WriteAllText("commit_msg_utf8.txt", $commitMessage, [System.Text.Encoding]::UTF8)

Write-Host "已创建UTF-8编码的提交信息文件"
