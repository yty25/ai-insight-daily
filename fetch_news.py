#!/usr/bin/env python3
"""
AI Insight Daily - News Fetcher
使用 Tavily API 搜索四大板块的新闻
"""

import os
import json
import requests
from datetime import datetime
from newspaper import Article
from bs4 import BeautifulSoup
import re

# 配置
TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY', '')
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
NEWS_FILE = os.path.join(DATA_DIR, 'news.json')

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

def tavily_search(query, max_results=5):
    """使用 Tavily API 搜索新闻"""
    if not TAVILY_API_KEY:
        print(f"警告：TAVILY_API_KEY 未设置，使用模拟数据")
        return generate_mock_results(query, max_results)
    
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
        return data.get('results', [])
    except Exception as e:
        print(f"搜索错误 {query}: {e}")
        return generate_mock_results(query, max_results)

def generate_mock_results(query, count):
    """生成模拟数据（当 API 不可用时）"""
    mock_data = []
    for i in range(count):
        mock_data.append({
            'title': f'{query} - Article {i+1}',
            'url': f'https://example.com/article-{i+1}',
            'content': f'This is a sample article about {query}. AI technology continues to advance rapidly...',
            'image': f'https://picsum.photos/seed/{i+1}/800/600.jpg',
            'published_date': datetime.now().strftime('%Y-%m-%d')
        })
    return mock_data

def extract_article_content(url):
    """使用 newspaper3k 提取文章内容"""
    try:
        article = Article(url, language='en')
        article.download()
        article.parse()
        
        # 清理内容
        clean_text = article.text
        if len(clean_text) > 500:
            clean_text = clean_text[:500] + '...'
        
        return {
            'title': article.title,
            'content': clean_text,
            'authors': article.authors,
            'publish_date': article.publish_date.strftime('%Y-%m-%d') if article.publish_date else None,
            'top_image': article.top_image
        }
    except Exception as e:
        print(f"提取文章失败 {url}: {e}")
        return None

def fetch_category_news(category_key, category_config):
    """抓取单个板块的新闻"""
    all_results = []
    seen_urls = set()
    
    for query in category_config['queries']:
        results = tavily_search(query, max_results=3)
        
        for result in results:
            url = result.get('url', '')
            if url in seen_urls:
                continue
            seen_urls.add(url)
            
            # 尝试提取详细内容
            article_data = extract_article_content(url)
            
            news_item = {
                'title': result.get('title', article_data['title'] if article_data else 'Untitled'),
                'summary': '',  # 将由 summarize.py 生成
                'category': category_key,
                'category_name': category_config['name'],
                'source': url.split('/')[2] if url else 'Unknown',
                'publish_date': result.get('published_date', article_data['publish_date'] if article_data else datetime.now().strftime('%Y-%m-%d')),
                'author': ', '.join(article_data['authors']) if article_data and article_data['authors'] else 'Unknown',
                'cover_image': result.get('image', article_data['top_image'] if article_data else ''),
                'original_url': url,
                'clean_content': article_data['content'] if article_data else result.get('content', '')
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
