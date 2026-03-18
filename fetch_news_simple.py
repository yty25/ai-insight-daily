#!/usr/bin/env python3
"""
AI Insight Daily - News Fetcher (Simplified)
使用 Tavily API 搜索四大板块的新闻 (无需 newspaper3k)
"""

import os
import json
import requests
import hashlib
import time
from datetime import datetime
from urllib.parse import urlparse

# 配置
TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY', '')
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
NEWS_FILE = os.path.join(DATA_DIR, 'news.json')
IMAGES_DIR = os.path.join(os.path.dirname(__file__), 'images')

# 四大板块的搜索关键词
CATEGORIES = {
    'llm': {
        'name': '大模型动态',
        'queries': [
            'OpenAI GPT latest news 2026',
            'Anthropic Claude AI update',
            'Google Gemini AI news',
            'LLM breakthrough research 2026',
            'AI model training advancement'
        ]
    },
    'ai_industry': {
        'name': 'AI 行业资讯',
        'queries': [
            'AI startup funding 2026',
            'Nvidia AI chip news',
            'AI company acquisition 2026',
            'Artificial Intelligence business',
            'AI product launch 2026'
        ]
    },
    'politics': {
        'name': '国际政治',
        'queries': [
            'international politics news today',
            'global diplomatic relations',
            'world government policy',
            'international summit meeting 2026',
            'geopolitical analysis 2026'
        ]
    },
    'finance': {
        'name': '金融',
        'queries': [
            'stock market news today',
            'financial market analysis',
            'investment trend 2026',
            'economic policy update',
            'cryptocurrency regulation news 2026'
        ]
    }
}

def download_image(image_url, news_title):
    """下载图片到本地，返回本地路径"""
    if not image_url:
        return ''
    
    try:
        # 生成唯一文件名
        url_hash = hashlib.md5(image_url.encode()).hexdigest()[:8]
        ext = '.jpg'
        parsed = urlparse(image_url)
        path_ext = os.path.splitext(parsed.path)[1].lower()
        if path_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            ext = path_ext
        
        filename = f"{url_hash}{ext}"
        filepath = os.path.join(IMAGES_DIR, filename)
        
        # 如果文件已存在，直接返回
        if os.path.exists(filepath):
            return f"/images/{filename}"
        
        # 下载图片
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(image_url, headers=headers, timeout=15, stream=True)
        response.raise_for_status()
        
        # 确保目录存在
        os.makedirs(IMAGES_DIR, exist_ok=True)
        
        # 保存图片
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"  📷 下载图片: {filename}")
        return f"/images/{filename}"
        
    except Exception as e:
        print(f"  ⚠️ 图片下载失败: {e}")
        return ''

def extract_image_from_content(content, images_list=None):
    """从内容或图片列表中提取图片URL"""
    # 首先检查 images_list
    if images_list and len(images_list) > 0:
        for img in images_list:
            if isinstance(img, str) and img.startswith('http'):
                return img
            elif isinstance(img, dict) and img.get('url'):
                return img['url']
    
    # 从内容中提取 markdown 图片
    if content:
        import re
        # 匹配 markdown 图片
        md_match = re.search(r'!\[.*?\]\((https?://[^\s\)]+)\)', content)
        if md_match:
            return md_match.group(1)
        
        # 匹配 HTML img 标签
        html_match = re.search(r'<img[^>]+src=["\']?(https?://[^\s"\'>]+)', content)
        if html_match:
            return html_match.group(1)
    
    return ''

def tavily_search(query, max_results=5):
    """使用 Tavily API 搜索新闻"""
    if not TAVILY_API_KEY:
        print(f"错误：TAVILY_API_KEY 未设置")
        return []
    
    url = "https://api.tavily.com/search"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TAVILY_API_KEY}"
    }
    payload = {
        "query": query,
        "search_depth": "advanced",
        "max_results": max_results,
        "include_images": True,
        "include_answer": False
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Tavily 返回的图片在顶层 images 数组中
        images = data.get('images', [])
        
        # 将图片分配给各个结果
        results = data.get('results', [])
        for i, result in enumerate(results):
            # 尝试为每个结果分配一张图片
            if i < len(images):
                result['_tavily_image'] = images[i]
            elif images:
                # 循环使用图片
                result['_tavily_image'] = images[i % len(images)]
            else:
                result['_tavily_image'] = ''
        
        return results
    except Exception as e:
        print(f"搜索错误 {query}: {e}")
        return []

def fetch_category_news(category_key, category_config):
    """抓取单个板块的新闻"""
    all_results = []
    seen_urls = set()
    downloaded_images = set()  # 避免重复下载同一图片
    
    for query in category_config['queries']:
        results = tavily_search(query, max_results=3)
        
        for result in results:
            url = result.get('url', '')
            if url in seen_urls:
                continue
            seen_urls.add(url)
            
            # 提取图片URL
            tavily_image = result.get('_tavily_image', '')
            content = result.get('content', '')
            
            image_url = tavily_image or extract_image_from_content(content)
            
            # 下载图片
            cover_image = ''
            if image_url and image_url not in downloaded_images:
                cover_image = download_image(image_url, result.get('title', ''))
                if cover_image:
                    downloaded_images.add(image_url)
            
            news_item = {
                'title': result.get('title', 'Untitled'),
                'summary': result.get('content', '')[:500] if result.get('content') else '',
                'category': category_key,
                'category_name': category_config['name'],
                'source': url.split('/')[2] if url else 'Unknown',
                'publish_date': result.get('published_date', datetime.now().strftime('%Y-%m-%d')),
                'author': 'Unknown',
                'cover_image': cover_image,
                'original_url': url,
                'clean_content': result.get('content', '')[:500] if result.get('content') else ''
            }
            
            all_results.append(news_item)
            
            if len(all_results) >= 10:
                break
        
        if len(all_results) >= 10:
            break
    
    return all_results[:10]

def save_news(news_data):
    """保存新闻数据到 JSON 文件"""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 按时间排序
    news_data.sort(key=lambda x: x.get('publish_date', ''), reverse=True)
    
    with open(NEWS_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            'updated_at': datetime.now().isoformat(),
            'categories': CATEGORIES,
            'news': news_data
        }, f, ensure_ascii=False, indent=2)
    
    print(f"已保存 {len(news_data)} 条新闻到 {NEWS_FILE}")

def main():
    """主函数"""
    print("🚀 AI Insight Daily - 开始抓取新闻...")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not TAVILY_API_KEY:
        print("❌ 错误：TAVILY_API_KEY 环境变量未设置")
        return
    
    all_news = []
    
    for category_key, category_config in CATEGORIES.items():
        print(f"\n📰 抓取板块：{category_config['name']}")
        news = fetch_category_news(category_key, category_config)
        print(f"  获取 {len(news)} 条新闻")
        all_news.extend(news)
    
    save_news(all_news)
    print(f"\n✅ 完成！共抓取 {len(all_news)} 条新闻")

if __name__ == '__main__':
    main()