# 🎨 AI Art Workbench

一个简洁美观的 AI 创作工作台，支持图片生成、视频生成、图片批量和视频批量，开箱即用。

**主站点**: https://www.371181668.xyz

---

## ✨ 功能特性

### 核心功能
| 功能 | 说明 |
|------|------|
| **文生图** | 输入描述词，AI 生成精美图片 |
| **图生图** | 上传 1-6 张参考图片，AI 基于图片生成新作品 |
| **文生视频** | 输入镜头描述，生成 Sora / Veo / Kling 等视频结果 |
| **图生视频** | 上传参考图生成视频；主流程最多显示 3 张参考图，按模型限制提交 |
| **图片批量** | 6 个图片任务可独立进行，高效批量创作 |
| **视频批量** | 独立的视频批量生成模块，只展示视频模型 |
| **多图参考** | 图片最多支持 6 张参考图，视频按模型支持 1-3 张参考图，单张建议 10MB 内 |
| **多分辨率** | 支持 1K、2K、4K 输出 |
| **多模型选择** | 支持 Pro、V2、V3、GPT Image、Gemini、Sora、Veo、Kling 等多种模型 |

### 用户体验
| 功能 | 说明 |
|------|------|
| **深色/浅色主题** | 一键切换，适配不同场景 |
| **历史记录** | 保存最近使用的提示词，方便复用 |
| **完整提示词显示** | 最近提示词不再截断，长提示词完整保留与回填 |
| **隐私保护** | 默认不保存 API Key；仅在勾选「记住」后写入本机 localStorage |
| **媒体下载** | 支持图片和视频结果下载 |
| **清晰错误提示** | 区分参数、Key、权限、限流、上游错误、解析失败、下载失败等场景 |
| **售后服务群** | 右侧显示售后服务群二维码（`image.png`） |
| **响应式布局** | 支持桌面端和移动端 |

---

## 🖼️ 界面预览

```
┌─────────┬────────────────────────────┬─────────────┐
│ 分辨率  │  图片：文生图/图生图/批量    │  API 设置   │
│  1K     │      ┌──┬──┬──┐           │  API Key    │
│  2K     │      │图1│图2│图3│           │             │
│  4K     │      ├──┼──┼──┤           │  模型选择    │
│ Video   │  视频：文生/图生/视频批量    │             │
│─────────│      └──┴──┴──┘           │─────────────│
│ 最近    │  📎 参考图最大支持 10MB     │  🌐 主站点  │
│ 提示词  │                            │  https://.. │
│         │  [请输入描述词...]         │             │
│         │                            │  售后服务群  │
│         │       [开始生成]           │  image.png   │
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

访问 **`http://localhost`**（默认监听 **80**；浏览器可省略 `:80`）。

本地若无管理员权限绑定 80，可指定其它端口，例如：`set PORT=5000`（Linux/macOS 用 `export PORT=5000`）后再运行 `python app.py`。

若使用下方 Docker 命令（映射宿主机 **80** → 容器 **80**），同样访问 **`http://localhost`** 或服务器的 **`http://你的IP`**。

### Docker 部署

```bash
# 构建镜像
docker build -t ai-art-workbench .

# 运行容器
docker run -d -p 80:80 --name ai-art-workbench ai-art-workbench
```

---

## ☁️ 云服务器部署

### 环境要求
- 服务器安装了 Docker
- 开放端口 **80**（或使用 `-p 8080:80` 等自定义映射）

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
docker run -d -p 80:80 --name ai-art-workbench ai-art-workbench
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
      - "80:80"
    restart: unless-stopped
    environment:
      - FLASK_ENV=production
      - PORT=80
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

### 文生视频模式
1. 点击「文生视频」切换模式
2. 选择 Video 分组下的视频模型
3. 输入视频镜头、主体、运动和风格描述
4. 点击「开始生成」

### 图生视频模式
1. 点击「图生视频」切换模式
2. 上传 1-3 张参考图（Sora 通常 1 张；Veo/Kling 按模型支持 1-3 张）
3. 输入视频描述
4. 点击「开始生成」

### 图片批量模式
1. 点击「图片批量」切换模式
2. 设置统一模型和分辨率（可选）
3. 在每个任务卡片中：
   - 上传 0-3 张参考图（可选）
   - 输入提示词
4. 点击「全部开始」或单独点击每个任务的「开始」按钮
5. 完成后可一键下载所有结果

### 视频批量模式
1. 点击「视频批量」切换模式
2. 选择视频模型
3. 在每个视频任务卡片中：
   - 上传 0-3 张参考图（按所选模型限制）
   - 输入视频提示词
4. 点击「全部开始」或单独点击每个任务的「开始」按钮
5. 完成后可一键下载所有视频结果

### 提示词技巧
- 使用英文描述效果更佳
- 添加风格关键词（如：realistic, anime, oil painting）
- 使用负面提示词排除不需要的元素

---

## 📊 支持模型

工作台可选模型与 **`GET https://371181668.xyz/v1/models`**（需 Bearer Key）返回的 ID **保持一致**。在项目目录执行：

```bash
# 推荐：创建 .model_fetch_key（首行一行 sk-...，已 gitignore），然后自动写回 app.py
python _fetch_models_from_api.py --patch-app
```

或仅用环境变量（勿把 Key 写进仓库）：

```bash
set MODEL_FETCH_KEY=你的_API_Key
python _fetch_models_from_api.py --patch-app
```

也可去掉 `--patch-app`，把脚本打印的 `MODELS = { ... }` 手动粘贴进 `app.py`。

可选环境变量：`MODEL_FETCH_URL`（默认 `https://371181668.xyz/v1/models`）。

| 分辨率分组 | 说明 |
|-----------|------|
| **1K / 2K / 4K** | `firefly-nano-banana`、`firefly-nano-banana-pro`、`firefly-nano-banana2`，按模型 ID 中的 `-1k-` / `-2k-` / `-4k-` 归类 |
| **GPT2** | 接口返回中含 `firefly-gpt-image`、`gpt-image-2` 的模型 |
| **Gemini** | `gemini-3-pro-image-preview`、`gemini-3.1-flash-image-preview` 可选 `1K/2K/4K`；`gemini-3.0-pro-image-2k` 固定 `2K`，`gemini-3.0-pro-image-4k` 固定 `4K`；不设置比例，使用模型默认比例 |
| **Video** | `firefly-sora2-*`、`firefly-veo31-*`、`firefly-veo31-ref-*`、`firefly-veo31-fast-*`、`firefly-kling3-*` |

图片模型和视频模型在 UI 中分组展示；图片批量和视频批量使用独立模块，避免误选模型类型。

---

## 🔧 常见问题

### Q: 端口被占用？
```bash
# 查看端口占用（Linux）
sudo netstat -tlnp | grep ':80 '

# 改用其它宿主机端口映射，例如宿主机 8080 -> 容器 80
docker run -d -p 8080:80 --name ai-art-workbench ai-art-workbench
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
docker run -d -p 80:80 --name ai-art-workbench ai-art-workbench
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
├── app.py                 # Flask 后端 API（内含 MODELS 清单）
├── image.png              # 售后服务群二维码
├── available_models.txt   # 旧版参考清单（请以 /v1/models 为准）
├── _fetch_models_from_api.py   # 从上游 /v1/models 拉取并打印 MODELS 块
├── _gen_models.py         # 根据本地 available_models.txt 生成 MODELS（离线）
├── requirements.txt
├── Dockerfile
├── README.md
└── static/
    ├── index.html
    ├── styles.css
    └── script.js
```

---

## 🔌 API 配置

- **API 地址**: https://371181668.xyz（与 `API_BASE_URL` 默认一致；站长入口常为 www 子域）
- **认证方式**: Bearer API Key

### 服务端环境变量（可选）

| 变量 | 说明 | 默认 |
|------|------|------|
| `API_BASE_URL` | 上游 OpenAI 兼容 API 根地址 | `https://371181668.xyz` |
| `IMAGE_URL_REWRITES` | 将返回中的图片内网/旧 HTTP 前缀替换为公网 HTTPS，格式 `旧前缀\|新前缀`，多项用英文逗号分隔 | （默认空；按需示例：`http://43.165.172.5:6001\|https://adobe.371181668.xyz`） |
| `DOWNLOAD_ALLOWED_HOSTS` | 代理下载接口允许的主机名（逗号分隔，防 SSRF） | `www.371181668.xyz,adobe.371181668.xyz,adobe2.371181668.xyz,371181668.xyz` |
| `MAX_DOWNLOAD_BYTES` | 单次代理下载最大字节数 | `314572800`（约 300MB，便于下载视频结果） |
| `MAX_IMAGE_PAYLOAD_CHARS` | 单次请求中参考图 Base64 总字符上限 | `12582912`（约 12MB 文本量） |
| `PORT` / `SERVER_PORT` | Waitress 监听端口（二选一，`PORT` 优先） | `80` |

### 错误返回说明

后端会尽量返回结构化错误，便于前端展示清晰原因：

| 字段 | 说明 |
|------|------|
| `error` | 面向用户的错误说明 |
| `hint` | 下一步处理建议 |
| `code` | 错误码，例如 `UPSTREAM_TIMEOUT`、`INVALID_MODEL` |
| `stage` | 失败阶段，例如 `request`、`queue`、`upstream`、`parse`、`download` |
| `upstreamStatus` | 上游 HTTP 状态码（如有） |
| `upstreamMessage` | 上游原始错误摘要（如有） |

---

## 📝 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|---------|
| 2026.05.18 | v1.4.0 | 接入文生视频、图生视频和独立视频批量模块；图片/视频模式重新分组；批量生成拆分为图片批量与视频批量 |
| 2026.05.18 | v1.4.0 | 优化错误提示，增加错误码、失败阶段、上游状态、处理建议；修复长提示词历史记录截断问题 |
| 2026.05.18 | v1.4.0 | 修复特殊比例结果遮挡参考图问题；图生视频参考图限制为 3 个上传位；右侧更新日志替换为售后服务群二维码 |
| 2026.04.14 | v1.3.0 | 新增批量生成功能，支持6个任务同时/独立进行 |
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
