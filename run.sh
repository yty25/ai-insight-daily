#!/bin/bash
# AI Insight Daily - 启动脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🤖 AI Insight Daily Ver 2.0"
echo "=========================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：需要 Python 3"
    exit 1
fi

echo "✅ Python 版本：$(python3 --version)"

# 安装依赖（如果需要）
if [ ! -d "__pycache__" ]; then
    echo "📦 检查依赖..."
    pip3 install -q -r requirements.txt 2>/dev/null || true
fi

# 抓取新闻
echo ""
echo "📰 抓取最新新闻..."
python3 fetch_news.py

# 生成摘要
echo ""
echo "📝 生成 AI 摘要..."
python3 summarize.py

# 启动服务器
echo ""
echo "🚀 启动服务器..."
echo "📍 访问地址：http://localhost:8083"
echo ""
python3 server.py
