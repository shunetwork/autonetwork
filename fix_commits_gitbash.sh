#!/bin/bash

# 使用Git Bash修正提交信息的脚本
echo "开始修正提交信息..."

# 检查当前目录
pwd

# 检查Git状态
git status

# 显示最近的提交
echo "最近的提交历史："
git log --oneline -10

# 使用交互式rebase修正提交信息
echo "开始交互式rebase..."
git rebase -i HEAD~10

echo "提交信息修正完成"
