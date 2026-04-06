# AI 画图工作台

一个精美的AI图像生成工作台，支持文生图和图生图功能。

## 功能特性

- 🎨 文生图 - 输入文字描述生成图片
- 🖼️ 图生图 - 上传图片进行AI处理
- 🔑 API Key 管理 - 用户可自定义API Key
- 📱 响应式设计 - 适配各种设备
- 🌊 流式预览 - 实时显示生成进度

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t ai-art-workbench .

# 运行容器
docker run -d -p 8080:80 --name ai-art-workbench ai-art-workbench
```

访问 `http://localhost:8080`

## 技术栈

- 前端: HTML + CSS + JavaScript
- 后端: Python Flask
- 部署: Docker
