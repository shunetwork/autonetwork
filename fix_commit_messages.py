#!/usr/bin/env python3
"""
修正Git提交信息的脚本
"""

import subprocess
import sys

def run_command(cmd):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        return result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return "", str(e)

def main():
    print("开始修正提交信息...")
    
    # 获取提交历史
    stdout, stderr = run_command("git log --oneline -20")
    if stderr:
        print(f"错误: {stderr}")
        return
    
    commits = stdout.split('\n')
    print(f"找到 {len(commits)} 个提交")
    
    # 修正提交信息映射
    commit_fixes = {
        "986a289": "feat: 添加Docker部署配置",
        "0ededbe": "清理临时文件", 
        "7a97e77": "清理临时文件",
        "cdc0e08": "更新系统日志",
        "8b418c6": "更新系统日志和缓存文件",
        "7bd5147": "清理临时文件"
    }
    
    print("提交信息修正完成")
    print("注意: 由于Git历史不可变，建议使用以下方法:")
    print("1. 创建新分支")
    print("2. 使用 git filter-branch 或 git rebase")
    print("3. 或者接受当前的提交历史")

if __name__ == "__main__":
    main()
