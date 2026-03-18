# 🤖 AI Insight Daily Ver 2.0

每日 AI 资讯精选 - 大模型动态 | AI 行业资讯 | 国际政治 | 金融

![AI Insight Daily](https://img.shields.io/badge/AI-Insight%20Daily-0066FF?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-green?style=for-the-badge)

## ✨ 核心功能

- **🧠 四大资讯板块**: 大模型动态、AI 行业资讯、国际政治、金融
- **🤖 AI 自动摘要**: 每篇文章 80-120 字智能摘要
- **📰 原文抓取清理**: 去除广告，保留正文和图片，阅读模式展示
- **🎨 科技媒体风格 UI**: 类似 TechCrunch/The Verge，简洁快速
- **📱 移动端优先**: 响应式设计，卡片式布局
- **🔍 SEO 优化**: Meta tags, OpenGraph, Sitemap, RSS feed

## 🚀 快速开始

### 1. 安装依赖

```bash
cd ai-insight-daily-v2
pip install -r requirements.txt
```

### 2. 配置 API Key

设置 Tavily API Key（可选，不设置会使用模拟数据）:

```bash
export TAVILY_API_KEY=your_api_key_here
```

### 3. 抓取新闻

```bash
python fetch_news.py
```

### 4. 生成摘要

```bash
python summarize.py
```

### 5. 启动服务器

```bash
python server.py
```

访问 http://localhost:8083 查看网站

## 📁 项目结构

```
ai-insight-daily-v2/
├── fetch_news.py          # Tavily 搜索 + 内容抓取
├── summarize.py           # AI 摘要生成
├── server.py              # HTTP 服务器 (8083 端口)
├── index.html             # 首页（四大板块）
├── style.css              # 样式表
├── articles/
│   └── index.html         # 文章详情页（阅读模式）
├── data/
│   ├── news.json          # 新闻数据
│   └── news.db            # SQLite 数据库（可选）
├── images/                # 图片存储
├── .github/
│   └── workflows/
│       └── deploy.yml     # GitHub Actions（每日 7:00）
├── requirements.txt       # Python 依赖
├── package.json           # 项目配置
└── README.md              # 本文档
```

## 📊 数据结构

每条新闻包含以下字段:

```json
{
  "title": "文章标题",
  "summary": "AI 生成的摘要（80-120 字）",
  "category": "分类标识 (llm/ai_industry/politics/finance)",
  "category_name": "分类名称",
  "source": "来源网站",
  "publish_date": "发布日期",
  "author": "作者",
  "cover_image": "封面图片 URL",
  "original_url": "原文链接",
  "clean_content": "清理后的正文内容"
}
```

## 🔧 配置选项

### Tavily API

获取 API Key: https://tavily.com/

```bash
export TAVILY_API_KEY=tvly-xxxxxxxxxxxxx
```

### 服务器端口

修改 `server.py` 中的 `PORT` 变量:

```python
PORT = 8083  # 修改为你想要的端口
```

## 🌐 部署

### GitHub Pages

1. Fork 本仓库
2. 在 Settings 中启用 GitHub Pages
3. 配置 GitHub Actions (已在 `.github/workflows/deploy.yml` 中设置)
4. 添加 `TAVILY_API_KEY` 到 Secrets

### 本地服务器

```bash
python server.py
```

### Docker (可选)

```bash
docker build -t ai-insight-daily .
docker run -p 8083:8083 ai-insight-daily
```

## 📈 API 端点

- `GET /api/news` - 获取所有新闻
- `GET /api/news/category?category=llm` - 按分类获取新闻
- `GET /api/article?url=xxx` - 获取单篇文章详情
- `GET /sitemap.xml` - Sitemap
- `GET /feed.xml` - RSS Feed

## 🎨 UI 特点

- **暗色模式**: 默认暗色主题，保护视力
- **响应式设计**: 完美适配手机、平板、桌面
- **卡片布局**: 现代化卡片式新闻展示
- **阅读模式**: 清爽的文章阅读体验
- **流畅动画**: 优雅的过渡效果

## 📝 定时任务

GitHub Actions 配置为每天北京时间 7:00 自动更新:

```yaml
on:
  schedule:
    - cron: '0 23 * * *'  # UTC 23:00 = 北京 7:00
```

本地可添加 cron 任务:

```bash
# 每天 7:00 更新
0 7 * * * cd /path/to/ai-insight-daily-v2 && python fetch_news.py && python summarize.py
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!

## 📄 许可证

MIT License

---

**AI Insight Daily** - 让 AI 资讯更简单 🚀
