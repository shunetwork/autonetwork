#!/bin/bash

# 修正提交信息的脚本
git filter-branch --msg-filter '
case "$GIT_COMMIT" in
    7b5e698*)
        echo "feat: 添加批量设备导入功能"
        ;;
    6b37899*)
        echo "feat: 添加Docker部署配置"
        ;;
    986a289*)
        echo "feat: 添加Docker部署配置"
        ;;
    0ededbe*)
        echo "清理临时文件"
        ;;
    7f0cb8a*)
        echo "feat: 添加Docker部署配置"
        ;;
    *)
        cat
        ;;
esac
' HEAD~10..HEAD
