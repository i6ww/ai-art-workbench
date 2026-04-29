#!/bin/bash
# AI Art Workbench 一键部署脚本

echo "=== AI Art Workbench 部署脚本 ==="

# 检查是否在项目目录
if [ ! -f "app.py" ]; then
    echo "错误: 未找到 app.py，请在项目目录运行此脚本"
    exit 1
fi

echo "[1/4] 安装依赖..."
pip3 install -r requirements.txt

echo "[2/4] 检查端口 5000..."
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "端口 5000 已被占用，尝试停止旧进程..."
    lsof -Pi :5000 -sTCP:LISTEN -t | xargs kill -9 2>/dev/null
fi

echo "[3/4] 启动服务..."
nohup python3 app.py > app.log 2>&1 &

echo "[4/4] 检查服务状态..."
sleep 3
if curl -s http://localhost:5000 > /dev/null; then
    echo ""
    echo "=== 部署成功 ==="
    echo "访问地址: http://$(curl -s ifconfig.me):5000"
    echo "日志查看: tail -f app.log"
else
    echo "服务启动失败，查看日志:"
    tail -20 app.log
fi
