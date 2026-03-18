#!/bin/bash
# AI Insight Daily - 每日新闻刷新脚本

cd /home/admin/.openclaw/workspace/ai-insight-daily-v2
export TAVILY_API_KEY=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

echo "$(date): 开始刷新新闻..." >> /tmp/ai-insight-daily.log

python3 << 'PYEOF'
import os
import json
import requests
import hashlib
from datetime import datetime
from urllib.parse import urlparse

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")
DATA_DIR = "data"
NEWS_FILE = os.path.join(DATA_DIR, "news.json")
IMAGES_DIR = "images"

# 每个分类用不同的默认图片
DEFAULT_IMAGES = {
    "llm": "/images/b398faf2.png",
    "ai_industry": "/images/41aa25e1.png", 
    "politics": "/images/fb1bf60f.png",
    "finance": "/images/ca984810.png"
}

# 查询列表 - 加入日期限定
QUERIES = [
    ("llm", "大模型动态", "OpenAI GPT Claude AI news March 2026"),
    ("ai_industry", "AI 行业资讯", "AI startup Nvidia chip news March 2026"),
    ("politics", "国际政治", "international politics breaking news today"),
    ("finance", "金融", "stock market finance news today"),
]

def tavily_search(query, max_results=3):
    url = "https://api.tavily.com/search"
    headers = {
        "Authorization": f"Bearer {TAVILY_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {"query": query, "max_results": max_results, "include_images": True}
    resp = requests.post(url, headers=headers, json=data, timeout=30)
    result = resp.json()
    return result.get("results", []), result.get("images", [])

def download_image(image_url):
    if not image_url:
        return None
    try:
        url_hash = hashlib.md5(image_url.encode()).hexdigest()[:8]
        ext = '.jpg'
        parsed = urlparse(image_url)
        path_ext = os.path.splitext(parsed.path)[1].lower()
        if path_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            ext = path_ext
        filename = f"{url_hash}{ext}"
        filepath = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(filepath):
            return f"/images/{filename}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(image_url, headers=headers, timeout=10, stream=True)
        resp.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return f"/images/{filename}"
    except:
        return None

all_news = []
for cat_key, cat_name, query in QUERIES:
    results, images = tavily_search(query)
    for i, r in enumerate(results):
        cover = DEFAULT_IMAGES.get(cat_key, "/images/b398faf2.png")
        if i < len(images):
            downloaded = download_image(images[i])
            if downloaded:
                cover = downloaded
        all_news.append({
            "title": r.get("title", ""),
            "summary": r.get("content", "")[:300],
            "category": cat_key,
            "category_name": cat_name,
            "source": r.get("url", "").split("/")[2] if r.get("url") else "",
            "publish_date": datetime.now().strftime("%Y-%m-%d"),
            "cover_image": cover,
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