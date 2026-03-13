#!/bin/bash
# VectorBrain GitHub 推送脚本
# 使用方法：./PUSH_TO_GITHUB.sh

cd ~/.vectorbrain

echo "🔍 检查 Git 状态..."
git status --short

echo ""
echo "🚀 推送到 GitHub: https://github.com/liugedapiqiu-dev/WJHlongxia"
echo ""
echo "请选择认证方式:"
echo "1. 使用 Personal Access Token (HTTPS)"
echo "2. 使用 SSH Key"
echo "3. 手动推送 (退出脚本)"
echo ""
read -p "选择 (1/2/3): " choice

case $choice in
  1)
    read -p "输入 GitHub Personal Access Token: " -s token
    echo ""
    git remote set-url origin https://${token}@github.com/liugedapiqiu-dev/WJHlongxia.git
    git push -u origin main --force
    ;;
  2)
    git remote set-url origin git@github.com:liugedapiqiu-dev/WJHlongxia.git
    git push -u origin main --force
    ;;
  3)
    echo "已退出。可以稍后手动执行推送。"
    exit 0
    ;;
  *)
    echo "无效选择"
    exit 1
    ;;
esac

if [ $? -eq 0 ]; then
  echo ""
  echo "✅ 推送成功！"
  echo "📦 查看仓库：https://github.com/liugedapiqiu-dev/WJHlongxia"
else
  echo ""
  echo "❌ 推送失败，请检查认证信息"
fi
