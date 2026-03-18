#!/usr/bin/env python3
"""
AI Insight Daily - 摘要生成器
为每篇文章生成 80-120 字的 AI 摘要
"""

import os
import json
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
NEWS_FILE = os.path.join(DATA_DIR, 'news.json')

# 摘要长度要求
MIN_SUMMARY_LENGTH = 80
MAX_SUMMARY_LENGTH = 120

def generate_summary(content, title):
    """
    生成文章摘要
    使用简单的提取式摘要（生产环境可替换为 LLM API）
    """
    if not content:
        return title
    
    # 清理文本
    content = content.strip()
    
    # 如果内容太短，直接返回
    if len(content) < MIN_SUMMARY_LENGTH:
        return content
    
    # 提取关键句子
    sentences = content.replace('。', '.').replace('！', '.').replace('？', '.').split('.')
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    
    # 取前 2-3 句作为摘要
    summary_sentences = sentences[:2]
    summary = '. '.join(summary_sentences)
    
    # 调整长度到目标范围
    if len(summary) > MAX_SUMMARY_LENGTH:
        summary = summary[:MAX_SUMMARY_LENGTH-3] + '...'
    elif len(summary) < MIN_SUMMARY_LENGTH and len(sentences) > 2:
        summary_sentences = sentences[:3]
        summary = '. '.join(summary_sentences)
        if len(summary) > MAX_SUMMARY_LENGTH:
            summary = summary[:MAX_SUMMARY_LENGTH-3] + '...'
    
    # 确保有合理的长度
    if len(summary) < 50:
        summary = content[:100] + '...' if len(content) > 100 else content
    
    return summary

def summarize_news():
    """为所有新闻生成摘要"""
    if not os.path.exists(NEWS_FILE):
        print(f"错误：新闻文件不存在 {NEWS_FILE}")
        print("请先运行 fetch_news.py")
        return
    
    with open(NEWS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    news_list = data.get('news', [])
    updated_count = 0
    
    print(f"📝 开始为 {len(news_list)} 条新闻生成摘要...")
    
    for news in news_list:
        if not news.get('summary'):
            content = news.get('clean_content', '')
            title = news.get('title', '')
            
            summary = generate_summary(content, title)
            news['summary'] = summary
            updated_count += 1
    
    # 保存更新后的数据
    data['news'] = news_list
    data['summarized_at'] = datetime.now().isoformat()
    
    with open(NEWS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 完成！更新了 {updated_count} 条新闻的摘要")

if __name__ == '__main__':
    summarize_news()
