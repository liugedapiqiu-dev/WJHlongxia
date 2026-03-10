#!/bin/bash
# name: long_term_memory
# description: 访问自主向量记忆库 - 使用 Ollama + FAISS 的本地记忆系统，支持语义搜索和持久化存储
# version: 1.0.0
# author: 健豪 + 阿豪
# usage: 支持 add/search/list/stats 命令

# 配置
PYTHON_BIN="/Users/jo/.openclaw/venv-memmachine/bin/python"
MEMORY_SCRIPT="/Users/jo/.openclaw/memory/autonomous/memory_cli.py"
MEMORY_DIR="/Users/jo/.openclaw/memory/autonomous"

# 切换到记忆系统目录
cd "$MEMORY_DIR"

# 解析参数
ACTION="$1"
shift

case "$ACTION" in
    add)
        # 添加记忆：add "内容" [--category 分类] [--importance 重要性]
        CONTENT="$1"
        shift
        $PYTHON_BIN "$MEMORY_SCRIPT" add "$CONTENT" "$@"
        ;;
    
    search|find|lookup)
        # 搜索记忆：search "查询文本" [-k 数量]
        QUERY="$1"
        shift
        $PYTHON_BIN "$MEMORY_SCRIPT" search "$QUERY" "$@"
        ;;
    
    list|ls|all)
        # 列出记忆：list [--limit 数量]
        $PYTHON_BIN "$MEMORY_SCRIPT" list "$@"
        ;;
    
    stats|status|info)
        # 系统统计：stats
        $PYTHON_BIN "$MEMORY_SCRIPT" stats
        ;;
    
    help|--help|-h)
        echo "🧠 阿豪的自主向量记忆系统"
        echo ""
        echo "用法:"
        echo "  add \"内容\" [--category 分类] [--importance 1-5]"
        echo "     添加记忆到记忆库"
        echo ""
        echo "  search \"查询文本\" [-k 返回数量]"
        echo "     语义搜索记忆"
        echo ""
        echo "  list [--limit 显示数量]"
        echo "     列出所有记忆"
        echo ""
        echo "  stats"
        echo "     显示系统统计信息"
        echo ""
        echo "示例:"
        echo "  add \"我喜欢蓝色\" --category 偏好 --importance 3"
        echo "  search \"口令是什么\" -k 3"
        echo "  list -l 10"
        ;;
    
    *)
        echo "❌ 未知命令：$ACTION"
        echo ""
        echo "使用 help 查看帮助"
        exit 1
        ;;
esac
