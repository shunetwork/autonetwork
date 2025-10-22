#!/bin/bash

# 修正提交信息的脚本
echo "开始修正提交信息..."

# 使用交互式rebase来修正提交信息
git rebase -i HEAD~10

echo "提交信息修正完成"
