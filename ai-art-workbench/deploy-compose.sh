#!/bin/sh
# 推荐：Nginx + API 双容器，静态页不占用生成线程，高负载时仍可打开工作台。
set -e
cd "$(dirname "$0")"
echo "compose 将使用宿主机 8080 端口；若有旧容器冲突请先停掉: docker stop ai-art-workbench 2>/dev/null || true"
docker compose up -d --build
echo "=== 已启动（compose）==="
docker compose ps
