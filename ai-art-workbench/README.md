# 🎨 AI Art Workbench

一个简洁美观的 AI 画图工作台，支持文生图和图生图功能，开箱即用。

**主站点**: https://www.371181668.xyz

---

## ✨ 功能特性

### 核心功能
| 功能 | 说明 |
|------|------|
| **文生图** | 输入描述词，AI 生成精美图片 |
| **图生图** | 上传 1-6 张参考图片，AI 基于图片生成新作品 |
| **多图参考** | 最多支持 6 张参考图同时上传，单张最大 10MB |
| **多分辨率** | 支持 1K、2K、4K 输出 |
| **多模型选择** | 支持 Pro、V2、V3 等多种模型 |

### 用户体验
| 功能 | 说明 |
|------|------|
| **深色/浅色主题** | 一键切换，适配不同场景 |
| **历史记录** | 保存最近使用的提示词，方便复用 |
| **隐私保护** | API Key 不自动保存，保护用户隐私 |
| **图片下载** | 一键下载生成结果 |
| **响应式布局** | 支持桌面端和移动端 |

---

## 🖼️ 界面预览

```
┌─────────┬────────────────────────────┬─────────────┐
│ 分辨率  │      文生图 / 图生图        │  API 设置   │
│  1K     │      ┌──┬──┬──┐           │  API Key    │
│  2K     │      │图1│图2│图3│           │             │
│  4K     │      ├──┼──┼──┤           │  模型选择    │
│         │      │图4│图5│图6│           │             │
│─────────│      └──┴──┴──┘           │─────────────│
│ 最近    │  📎 参考图最大支持 10MB     │  🌐 主站点  │
│ 提示词  │                            │  https://.. │
│         │  [请输入描述词...]         │             │
│         │                            │  📋 更新日志 │
│         │       [开始生成]           │  04.13 ...  │
└─────────┴────────────────────────────┴─────────────┘
```

---

## 🚀 快速开始

### 本地运行

```bash
# 克隆项目
git clone https://github.com/i6ww/aigongzuotai.git
cd aigongzuotai/ai-art-workbench

# 安装依赖
pip install -r requirements.txt

# 运行
python app.py
```

访问 `http://localhost:8080`

### Docker 部署

```bash
# 构建镜像
docker build -t ai-art-workbench .

# 运行容器
docker run -d -p 8080:5000 --name ai-art-workbench ai-art-workbench
```

---

## ☁️ 云服务器部署

### 环境要求
- 服务器安装了 Docker
- 开放端口 8080

### 部署步骤

```bash
# 1. 连接服务器
ssh root@你的服务器IP

# 2. 安装 Docker（如未安装）
apt update && apt install -y docker.io docker-compose

# 3. 克隆项目
git clone https://github.com/i6ww/aigongzuotai.git
cd aigongzuotai/ai-art-workbench

# 4. 构建并启动
docker build -t ai-art-workbench .
docker run -d -p 8080:5000 --name ai-art-workbench ai-art-workbench
```

### Docker Compose 部署（推荐）

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  app:
    build: .
    container_name: ai-art-workbench
    ports:
      - "8080:5000"
    restart: unless-stopped
    environment:
      - FLASK_ENV=production
```

启动服务：

```bash
# 构建并启动
docker-compose up -d --build

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 更新部署
git pull origin master && docker-compose up -d --build
```

---

## 📋 使用指南

### 文生图模式
1. 选择分辨率（1K / 2K / 4K）
2. 选择合适的模型
3. 在输入框中输入图片描述
4. 点击「开始生成」

### 图生图模式
1. 点击「图生图」切换模式
2. 上传 1-6 张参考图（单张最大 10MB）
3. 输入图片描述
4. 点击「开始生成」

### 提示词技巧
- 使用英文描述效果更佳
- 添加风格关键词（如：realistic, anime, oil painting）
- 使用负面提示词排除不需要的元素

---

## 📊 支持模型

| 模型系列 | 说明 | 适用场景 |
|---------|------|---------|
| firefly-nano-banana-pro | 高质量专业模型 | 写实风格 |
| firefly-nano-banana2 | nano-banana-2 系列 | 艺术创作 |
| firefly-nano-banana | nano-banana-3 系列 | 通用场景 |

每个系列支持 1K、2K、4K 分辨率。

---

## 🔧 常见问题

### Q: 端口被占用？
```bash
# 查看端口占用
netstat -tlnp | grep 8080

# 改为其他端口，如 8090
docker run -d -p 8090:5000 --name ai-art-workbench ai-art-workbench
```

### Q: 容器启动失败？
```bash
# 查看错误日志
docker logs ai-art-workbench
```

### Q: 如何更新？
```bash
cd ai-art-workbench
git pull origin master
docker build -t ai-art-workbench .
docker stop ai-art-workbench
docker rm ai-art-workbench
docker run -d -p 8080:5000 --name ai-art-workbench ai-art-workbench
```

### Q: 如何备份？
```bash
# 导出镜像
docker save ai-art-workbench > ai-art-workbench.tar

# 导入镜像
docker load < ai-art-workbench.tar
```

---

## 🗂️ 项目结构

```
ai-art-workbench/
├── app.py              # Flask 后端 API
├── requirements.txt    # Python 依赖
├── Dockerfile          # Docker 配置
├── README.md           # 项目说明
└── static/
    ├── index.html      # 前端页面
    ├── styles.css      # 样式文件
    └── script.js       # 前端脚本
```

---

## 🔌 API 配置

- **API 地址**: https://www.371181668.xyz
- **认证方式**: Bearer API Key

---

## 📝 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|---------|
| 2026.04.13 | v1.2.0 | 新增主站点入口，优化参考图上传区域 |
| 2026.04.10 | v1.1.0 | 支持 6 张参考图上传 |
| 2026.04.05 | v1.0.2 | 新增 4K 分辨率支持 |
| 2026.03.28 | v1.0.1 | 支持深色/浅色主题切换 |
| 2026.03.20 | v1.0.0 | 初始版本发布 |

---

## 🛠️ 技术栈

- **后端**: Flask (Python)
- **前端**: HTML5 + CSS3 + JavaScript
- **部署**: Docker
- **API**: REST API

---

<p align="center">
  <a href="https://github.com/i6ww/aigongzuotai">GitHub</a> •
  <a href="https://www.371181668.xyz">主站点</a>
</p>
