#!/bin/bash
# name: import_knowledge_base
# description: 批量导入高价值知识资产到 FAISS 记忆库
# version: 1.0.0
# author: 健豪 + 阿豪

PYTHON_BIN="/Users/jo/.openclaw/venv-memmachine/bin/python"
MEMORY_SCRIPT="/Users/jo/.openclaw/memory/autonomous/memory_cli.py"
MEMORY_DIR="/Users/jo/.openclaw/memory/autonomous"

cd "$MEMORY_DIR"

echo "🚀 开始批量导入知识资产到 FAISS 记忆库..."
echo "============================================================"

# 统计计数器
TOTAL=0
SUCCESS=0
FAILED=0

# 导入函数
import_file() {
    local file="$1"
    local category="$2"
    local importance="$3"
    
    # 读取文件内容（限制大小，避免过大文件）
    local content=$(head -c 50000 "$file" | tr '\n' ' ' | sed 's/  */ /g')
    
    if [ -n "$content" ]; then
        # 截取文件名作为标题
        local filename=$(basename "$file")
        local filepath=$(echo "$file" | sed 's|/Users/jo/.openclaw/||')
        
        # 组合内容
        local full_content="[$filename] $filepath - $content"
        
        # 添加到记忆库
        $PYTHON_BIN "$MEMORY_SCRIPT" add "$full_content" \
            --category "$category" \
            --importance "$importance" > /dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            echo "✅ $filepath"
            ((SUCCESS++))
        else
            echo "❌ $filepath (失败)"
            ((FAILED++))
        fi
        ((TOTAL++))
    fi
}

echo ""
echo "📚 P0: 导入 Markdown 文档（核心知识）..."
echo "-----------------------------------------------------------"

# 导入 workspace 下的 MD 文件
find ~/.openclaw/workspace -name "*.md" -type f \
  -not -path "*/node_modules/*" \
  2>/dev/null | while read file; do
    import_file "$file" "knowledge" 4
done

# 导入 skills 下的 MD 文件
find ~/.openclaw/workspace/skills -name "*.md" -type f \
  2>/dev/null | while read file; do
    import_file "$file" "skill_doc" 5
done

# 导入 memory 下的 MD 文件
find ~/.openclaw/memory -name "*.md" -type f \
  -not -path "*/autonomous/*" \
  2>/dev/null | while read file; do
    import_file "$file" "memory_note" 3
done

echo ""
echo "🐍 P1: 导入 Python 脚本（技术文档）..."
echo "-----------------------------------------------------------"

find ~/.openclaw/workspace -name "*.py" -type f \
  -not -path "*/node_modules/*" \
  2>/dev/null | while read file; do
    import_file "$file" "python_code" 3
done

find ~/.openclaw/workspace/skills -name "*.py" -type f \
  2>/dev/null | while read file; do
    import_file "$file" "skill_code" 4
done

echo ""
echo "📋 P2: 导入重要 JSON 配置..."
echo "-----------------------------------------------------------"

# 只导入重要的 JSON 文件
for file in \
  ~/.openclaw/openclaw.json \
  ~/.openclaw/workspace/*.json \
  ~/.openclaw/workspace/skills/*/SKILL.md 2>/dev/null; do
  if [ -f "$file" ]; then
    import_file "$file" "config" 2
  fi
done

echo ""
echo "============================================================"
echo "📊 导入完成统计:"
echo "  总文件数：$TOTAL"
echo "  成功：$SUCCESS"
echo "  失败：$FAILED"
echo ""

# 显示记忆库统计
echo "📊 当前记忆库状态:"
$PYTHON_BIN "$MEMORY_SCRIPT" stats

echo ""
echo "✅ 知识资产批量导入完成！"
