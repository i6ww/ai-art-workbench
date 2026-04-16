# AI Art Workbench 部署脚本 (Windows PowerShell)

# 配置
$IMAGE_NAME = "ai-art-workbench"
$CONTAINER_NAME = "ai-art-workbench"
$HOST_PORT = 8080
$CONTAINER_PORT = 5000

Write-Host "=== AI Art Workbench 部署脚本 ===" -ForegroundColor Cyan
Write-Host "镜像: $IMAGE_NAME"
Write-Host "容器: $CONTAINER_NAME"
Write-Host "端口: $HOST_PORT`:$CONTAINER_PORT"
Write-Host ""

# 停止并删除旧容器
Write-Host "[1/4] 停止旧容器..." -ForegroundColor Yellow
docker stop $CONTAINER_NAME -ErrorAction SilentlyContinue
docker rm $CONTAINER_NAME -ErrorAction SilentlyContinue

# 构建新镜像
Write-Host "[2/4] 构建 Docker 镜像..." -ForegroundColor Yellow
docker build -t $IMAGE_NAME .

# 运行新容器
Write-Host "[3/4] 启动容器..." -ForegroundColor Yellow
docker run -d --name $CONTAINER_NAME -p $HOST_PORT`:$CONTAINER_PORT --restart unless-stopped $IMAGE_NAME

# 检查状态
Write-Host "[4/4] 检查容器状态..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
if (docker ps | Select-String $CONTAINER_NAME) {
    Write-Host ""
    Write-Host "=== 部署成功 ===" -ForegroundColor Green
    Write-Host "访问地址: http://localhost`:$HOST_PORT"
    docker logs $CONTAINER_NAME | Select-Object -Last 5
} else {
    Write-Host "部署失败，请检查日志: docker logs $CONTAINER_NAME" -ForegroundColor Red
}
