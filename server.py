#!/usr/bin/env python3
"""
AI Insight Daily - HTTP 服务器
提供 8083 端口的 Web 服务
"""

import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

PORT = 8083
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
NEWS_FILE = os.path.join(DATA_DIR, 'news.json')
ARTICLES_DIR = os.path.join(os.path.dirname(__file__), 'articles')

class NewsHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        # API 端点
        if path == '/api/news':
            self.send_json_response(get_news_data())
            return
        
        if path == '/api/news/category':
            category = query.get('category', ['all'])[0]
            self.send_json_response(get_news_by_category(category))
            return
        
        if path == '/api/article':
            url = query.get('url', [''])[0]
            self.send_json_response(get_article_by_url(url))
            return
        
        if path == '/sitemap.xml':
            self.send_sitemap()
            return
        
        if path == '/feed.xml' or path == '/rss.xml':
            self.send_rss_feed()
            return
        
        # 静态文件
        if path == '/' or path == '/index.html':
            self.path = '/index.html'
        elif path.startswith('/articles/'):
            pass  # 保持原路径
        elif path.endswith('.html') or path.endswith('.css') or path.endswith('.js'):
            pass
        elif path.startswith('/images/'):
            pass
        
        return super().do_GET()
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def send_sitemap(self):
        """生成 sitemap"""
        news_data = get_news_data()
        news_list = news_data.get('news', [])
        
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        xml += '  <url>\n'
        xml += '    <loc>https://ai-insight-daily.com/</loc>\n'
        xml += '    <lastmod>' + datetime.now().strftime('%Y-%m-%d') + '</lastmod>\n'
        xml += '    <priority>1.0</priority>\n'
        xml += '  </url>\n'
        
        for news in news_list[:50]:
            url = news.get('original_url', '')
            if url:
                xml += '  <url>\n'
                xml += f'    <loc>https://ai-insight-daily.com/articles/?url={url}</loc>\n'
                xml += '    <lastmod>' + news.get('publish_date', datetime.now().strftime('%Y-%m-%d')) + '</lastmod>\n'
                xml += '  </url>\n'
        
        xml += '</urlset>'
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/xml')
        self.end_headers()
        self.wfile.write(xml.encode('utf-8'))
    
    def send_rss_feed(self):
        """生成 RSS feed"""
        news_data = get_news_data()
        news_list = news_data.get('news', [])
        
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<rss version="2.0">\n'
        xml += '<channel>\n'
        xml += '  <title>AI Insight Daily</title>\n'
        xml += '  <description>每日 AI 资讯精选</description>\n'
        xml += '  <link>https://ai-insight-daily.com</link>\n'
        xml += '  <lastBuildDate>' + datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT') + '</lastBuildDate>\n'
        
        for news in news_list[:20]:
            xml += '  <item>\n'
            xml += f'    <title>{news.get("title", "")}</title>\n'
            xml += f'    <description>{news.get("summary", "")}</description>\n'
            xml += f'    <link>{news.get("original_url", "")}</link>\n'
            xml += f'    <pubDate>{news.get("publish_date", "")}</pubDate>\n'
            xml += f'    <category>{news.get("category_name", "")}</category>\n'
            xml += '  </item>\n'
        
        xml += '</channel>\n</rss>'
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/xml')
        self.end_headers()
        self.wfile.write(xml.encode('utf-8'))

def get_news_data():
    """获取所有新闻数据"""
    if not os.path.exists(NEWS_FILE):
        return {'news': [], 'updated_at': None}
    
    with open(NEWS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_news_by_category(category):
    """按分类获取新闻"""
    data = get_news_data()
    news_list = data.get('news', [])
    
    if category == 'all':
        return data
    
    filtered = [n for n in news_list if n.get('category') == category]
    return {
        'category': category,
        'news': filtered[:10],
        'updated_at': data.get('updated_at')
    }

def get_article_by_url(url):
    """获取单篇文章详情"""
    data = get_news_data()
    news_list = data.get('news', [])
    
    for news in news_list:
        if news.get('original_url') == url:
            return {'article': news}
    
    return {'error': 'Article not found'}

def run_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, NewsHandler)
    print(f"🚀 AI Insight Daily 服务器已启动")
    print(f"📍 访问地址：http://localhost:{PORT}")
    print(f"📁 项目目录：{os.path.dirname(__file__)}")
    print(f"⏰ 启动时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
