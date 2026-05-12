# AI Art Workbench 部署脚本
#
# 生产环境若出现「生成一多整站打不开」，请改用 Nginx 前置：
#   chmod +x deploy-compose.sh && ./deploy-compose.sh
# （见项目根目录 docker-compose.yml）

# 配置
IMAGE_NAME="ai-art-workbench"
CONTAINER_NAME="ai-art-workbench"
HOST_PORT=80
CONTAINER_PORT=80

echo "=== AI Art Workbench 部署脚本 ==="
echo "镜像: $IMAGE_NAME"
echo "容器: $CONTAINER_NAME"
echo "端口: $HOST_PORT:$CONTAINER_PORT"
echo ""

# 停止并删除旧容器
echo "[1/4] 停止旧容器..."
docker stop $CONTAINER_NAME 2>/dev/null
docker rm $CONTAINER_NAME 2>/dev/null

# 构建新镜像
echo "[2/4] 构建 Docker 镜像..."
docker build -t $IMAGE_NAME .

# 运行新容器
echo "[3/4] 启动容器..."
docker run -d \
  --name $CONTAINER_NAME \
  -p $HOST_PORT:$CONTAINER_PORT \
  --restart unless-stopped \
  $IMAGE_NAME

# 检查状态
echo "[4/4] 检查容器状态..."
sleep 2
if docker ps | grep -q $CONTAINER_NAME; then
    echo ""
    echo "=== 部署成功 ==="
    echo "访问地址: http://localhost:$HOST_PORT"
    docker logs $CONTAINER_NAME | tail -5
else
    echo "部署失败，请检查日志: docker logs $CONTAINER_NAME"
fi
