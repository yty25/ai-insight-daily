#!/bin/bash
# AI Insight Daily - 每日新闻刷新脚本

cd /home/admin/.openclaw/workspace/ai-insight-daily-v2
export TAVILY_API_KEY=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

echo "$(date): 开始刷新新闻..." >> /tmp/ai-insight-daily.log

python3 << 'PYEOF'
import os
import json
import requests
from datetime import datetime

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")
DATA_DIR = "data"
NEWS_FILE = os.path.join(DATA_DIR, "news.json")

QUERIES = [
    ("llm", "大模型动态", "OpenAI GPT Claude latest news 2026"),
    ("ai_industry", "AI 行业资讯", "AI startup Nvidia funding 2026"),
    ("politics", "国际政治", "international politics news 2026"),
    ("finance", "金融", "stock market finance news 2026"),
]

def tavily_search(query, max_results=3):
    url = "https://api.tavily.com/search"
    headers = {
        "Authorization": f"Bearer {TAVILY_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {"query": query, "max_results": max_results, "include_images": False}
    resp = requests.post(url, headers=headers, json=data, timeout=30)
    return resp.json().get("results", [])

all_news = []
for cat_key, cat_name, query in QUERIES:
    results = tavily_search(query)
    for r in results:
        all_news.append({
            "title": r.get("title", ""),
            "summary": r.get("content", "")[:300],
            "category": cat_key,
            "category_name": cat_name,
            "source": r.get("url", "").split("/")[2] if r.get("url") else "",
            "publish_date": datetime.now().strftime("%Y-%m-%d"),
            "cover_image": "/images/b398faf2.png",
            "original_url": r.get("url", ""),
            "clean_content": r.get("content", "")
        })

news_data = {
    "updated_at": datetime.now().isoformat(),
    "categories": {q[0]: {"name": q[1], "queries": [q[2]]} for q in QUERIES},
    "news": all_news
}

os.makedirs(DATA_DIR, exist_ok=True)
with open(NEWS_FILE, "w", encoding="utf-8") as f:
    json.dump(news_data, f, ensure_ascii=False, indent=2)

print(f"完成！共 {len(all_news)} 条新闻")
PYEOF

echo "$(date): 刷新完成" >> /tmp/ai-insight-daily.log