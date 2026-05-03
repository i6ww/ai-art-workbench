from flask import Flask, request, jsonify, Response
import requests
import re
import time
import ipaddress
import socket
from urllib.parse import urlparse

import os
import logging

from werkzeug.exceptions import HTTPException

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, 'static'), static_url_path='/')
app.config["DEBUG"] = os.environ.get("FLASK_DEBUG", "").lower() in ("1", "true", "yes")

BASE_URL = os.environ.get("API_BASE_URL", "https://www.371181668.xyz").rstrip("/")


def _parse_image_url_rewrites():
    raw = os.environ.get(
        "IMAGE_URL_REWRITES",
        "http://43.165.172.5:6001|https://adobe.371181668.xyz",
    )
    rules = []
    for part in raw.split(","):
        part = part.strip()
        if "|" not in part:
            continue
        old, new = part.split("|", 1)
        old, new = old.strip(), new.strip()
        if old and new:
            rules.append((old, new))
    return rules


IMAGE_URL_REWRITE_RULES = _parse_image_url_rewrites()

MAX_IMAGE_PAYLOAD_CHARS = int(os.environ.get("MAX_IMAGE_PAYLOAD_CHARS", str(12 * 1024 * 1024)))

DOWNLOAD_ALLOWED_HOSTS = frozenset(
    h.strip().lower()
    for h in os.environ.get(
        "DOWNLOAD_ALLOWED_HOSTS",
        "www.371181668.xyz,adobe.371181668.xyz,371181668.xyz",
    ).split(",")
    if h.strip()
)

MAX_DOWNLOAD_BYTES = int(os.environ.get("MAX_DOWNLOAD_BYTES", str(30 * 1024 * 1024)))

http_session = requests.Session()


def _rewrite_generated_image_urls(urls):
    out = []
    for url in urls:
        for old, new in IMAGE_URL_REWRITE_RULES:
            if url.startswith(old):
                url = new + url[len(old):]
                break
        out.append(url)
    return out


def _estimate_image_payload_chars(data):
    if not data:
        return 0
    n = 0
    img = data.get("image")
    imgs = data.get("images")
    if isinstance(img, str):
        n += len(img)
    if isinstance(imgs, list):
        for s in imgs:
            if isinstance(s, str):
                n += len(s)
    return n


def _validate_download_url(url):
    try:
        parsed = urlparse(url)
    except Exception:
        return False, "无效的下载地址"
    if parsed.scheme not in ("http", "https"):
        return False, "仅允许 http/https 链接"
    host = (parsed.hostname or "").lower()
    if not host:
        return False, "缺少主机名"
    if host not in DOWNLOAD_ALLOWED_HOSTS:
        return False, "不允许的下载域名"
    try:
        for res in socket.getaddrinfo(host, None):
            addr = res[4][0]
            try:
                ip = ipaddress.ip_address(addr)
            except ValueError:
                continue
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                return False, "目标地址不允许"
    except socket.gaierror:
        return False, "无法解析主机名"
    return True, None

# 模型列表
MODELS = {
    "1K": [
        # firefly-gpt-image-2 系列
        "firefly-gpt-image-2-16x9",
        "firefly-gpt-image-2-1x1",
        "firefly-gpt-image-2-2x3",
        "firefly-gpt-image-2-3x2",
        # nano-banana 系列
        "firefly-nano-banana-1k-16x9",
        "firefly-nano-banana-1k-1x1",
        "firefly-nano-banana-1k-21x9",
        "firefly-nano-banana-1k-3x4",
        "firefly-nano-banana-1k-4x3",
        "firefly-nano-banana-1k-4x5",
        "firefly-nano-banana-1k-5x4",
        "firefly-nano-banana-1k-9x16",
        "firefly-nano-banana-pro-1k-16x9",
        "firefly-nano-banana-pro-1k-1x1",
        "firefly-nano-banana-pro-1k-21x9",
        "firefly-nano-banana-pro-1k-3x4",
        "firefly-nano-banana-pro-1k-4x3",
        "firefly-nano-banana-pro-1k-4x5",
        "firefly-nano-banana-pro-1k-5x4",
        "firefly-nano-banana-pro-1k-9x16",
        "firefly-nano-banana2-1k-16x9",
        "firefly-nano-banana2-1k-1x1",
        "firefly-nano-banana2-1k-1x4",
        "firefly-nano-banana2-1k-1x8",
        "firefly-nano-banana2-1k-21x9",
        "firefly-nano-banana2-1k-2x3",
        "firefly-nano-banana2-1k-3x2",
        "firefly-nano-banana2-1k-3x4",
        "firefly-nano-banana2-1k-4x3",
        "firefly-nano-banana2-1k-4x5",
        "firefly-nano-banana2-1k-5x4",
        "firefly-nano-banana2-1k-8x1",
        "firefly-nano-banana2-1k-9x16",
    ],
    "2K": [
        "firefly-nano-banana-2k-16x9",
        "firefly-nano-banana-2k-1x1",
        "firefly-nano-banana-2k-21x9",
        "firefly-nano-banana-2k-3x4",
        "firefly-nano-banana-2k-4x3",
        "firefly-nano-banana-2k-4x5",
        "firefly-nano-banana-2k-5x4",
        "firefly-nano-banana-2k-9x16",
        "firefly-nano-banana-pro-2k-16x9",
        "firefly-nano-banana-pro-2k-1x1",
        "firefly-nano-banana-pro-2k-21x9",
        "firefly-nano-banana-pro-2k-3x4",
        "firefly-nano-banana-pro-2k-4x3",
        "firefly-nano-banana-pro-2k-4x5",
        "firefly-nano-banana-pro-2k-5x4",
        "firefly-nano-banana-pro-2k-9x16",
        "firefly-nano-banana2-2k-16x9",
        "firefly-nano-banana2-2k-1x1",
        "firefly-nano-banana2-2k-1x4",
        "firefly-nano-banana2-2k-1x8",
        "firefly-nano-banana2-2k-21x9",
        "firefly-nano-banana2-2k-2x3",
        "firefly-nano-banana2-2k-3x2",
        "firefly-nano-banana2-2k-3x4",
        "firefly-nano-banana2-2k-4x3",
        "firefly-nano-banana2-2k-4x5",
        "firefly-nano-banana2-2k-5x4",
        "firefly-nano-banana2-2k-8x1",
        "firefly-nano-banana2-2k-9x16",
    ],
    "4K": [
        "firefly-nano-banana-4k-16x9",
        "firefly-nano-banana-4k-1x1",
        "firefly-nano-banana-4k-21x9",
        "firefly-nano-banana-4k-3x4",
        "firefly-nano-banana-4k-4x3",
        "firefly-nano-banana-4k-4x5",
        "firefly-nano-banana-4k-5x4",
        "firefly-nano-banana-4k-9x16",
        "firefly-nano-banana-pro-4k-16x9",
        "firefly-nano-banana-pro-4k-1x1",
        "firefly-nano-banana-pro-4k-21x9",
        "firefly-nano-banana-pro-4k-3x4",
        "firefly-nano-banana-pro-4k-4x3",
        "firefly-nano-banana-pro-4k-4x5",
        "firefly-nano-banana-pro-4k-5x4",
        "firefly-nano-banana-pro-4k-9x16",
        "firefly-nano-banana2-4k-16x9",
        "firefly-nano-banana2-4k-1x1",
        "firefly-nano-banana2-4k-1x4",
        "firefly-nano-banana2-4k-1x8",
        "firefly-nano-banana2-4k-21x9",
        "firefly-nano-banana2-4k-2x3",
        "firefly-nano-banana2-4k-3x2",
        "firefly-nano-banana2-4k-3x4",
        "firefly-nano-banana2-4k-4x3",
        "firefly-nano-banana2-4k-4x5",
        "firefly-nano-banana2-4k-5x4",
        "firefly-nano-banana2-4k-8x1",
        "firefly-nano-banana2-4k-9x16",
    ],
    "GPT2": [
        # firefly-gpt-image-2 标准比例
        "firefly-gpt-image-2-16x9",
        "firefly-gpt-image-2-1x1",
        "firefly-gpt-image-2-2x3",
        "firefly-gpt-image-2-3x2",
        "firefly-gpt-image-2-4x3",
        "firefly-gpt-image-2-4x5",
        "firefly-gpt-image-2-5x4",
        "firefly-gpt-image-2-9x16",
        # firefly-gpt-image-2-4k 系列 (h=高质量, l=低质量, m=中等质量)
        "firefly-gpt-image-2-4k-16x9-h",
        "firefly-gpt-image-2-4k-16x9-m",
        "firefly-gpt-image-2-4k-16x9-l",
        "firefly-gpt-image-2-4k-1x1-h",
        "firefly-gpt-image-2-4k-1x1-m",
        "firefly-gpt-image-2-4k-1x1-l",
        "firefly-gpt-image-2-4k-2x3-h",
        "firefly-gpt-image-2-4k-2x3-m",
        "firefly-gpt-image-2-4k-2x3-l",
        "firefly-gpt-image-2-4k-3x2-h",
        "firefly-gpt-image-2-4k-3x2-m",
        "firefly-gpt-image-2-4k-3x2-l",
        "firefly-gpt-image-2-4k-4x3-h",
        "firefly-gpt-image-2-4k-4x3-m",
        "firefly-gpt-image-2-4k-4x3-l",
        "firefly-gpt-image-2-4k-4x5-h",
        "firefly-gpt-image-2-4k-4x5-m",
        "firefly-gpt-image-2-4k-4x5-l",
        "firefly-gpt-image-2-4k-5x4-h",
        "firefly-gpt-image-2-4k-5x4-m",
        "firefly-gpt-image-2-4k-5x4-l",
        "firefly-gpt-image-2-4k-9x16-h",
        "firefly-gpt-image-2-4k-9x16-m",
        "firefly-gpt-image-2-4k-9x16-l",
    ],
}


ALL_MODELS = frozenset(m for models in MODELS.values() for m in models)


@app.route('/favicon.ico')
def favicon():
    return '', 204  # 返回空响应

@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/api/models')
def get_models():
    return jsonify(MODELS)


@app.route('/api/generate', methods=['POST'])
def generate():
    logger.info(f"收到生成请求")
    
    # 检查 Content-Type
    if not request.is_json:
        logger.error(f"Content-Type 不是 application/json")
        return jsonify({'error': 'Content-Type 必须为 application/json'}), 400
    
    data = request.json
    if data is None:
        return jsonify({'error': '请求体必须为 JSON'}), 400

    api_key = data.get('apiKey')
    model = data.get('model')
    prompt = data.get('prompt')
    image_data = data.get('image')  # 单张图片
    images_data = data.get('images')  # 多张图片

    if _estimate_image_payload_chars(data) > MAX_IMAGE_PAYLOAD_CHARS:
        return jsonify({'error': '参考图数据过大，请压缩或减少图片数量'}), 413
    
    # 日志请求参数（敏感信息脱敏）
    has_image = bool(image_data or images_data)
    logger.info(f"请求参数: model={model}, prompt长度={len(prompt) if prompt else 0}, 有图片={has_image}")

    if not api_key or not model or not prompt:
        logger.error(f"缺少必要参数: api_key={bool(api_key)}, model={model}, prompt={bool(prompt)}")
        return jsonify({'error': '缺少必要参数'}), 400

    if model not in ALL_MODELS:
        logger.error(f"无效的模型: {model}")
        return jsonify({'error': '无效的模型'}), 400

    try:
        # 构建消息内容
        if image_data or images_data:
            # 图生图模式
            content = [{"type": "text", "text": prompt}]
            
            # 处理单张或多张图片
            if images_data:
                # 多图模式
                for img in images_data:
                    if ',' in img:
                        image_b64 = img.split(',')[1]
                    else:
                        image_b64 = img
                    content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}})
            elif image_data:
                # 单图模式
                if ',' in image_data:
                    image_b64 = image_data.split(',')[1]
                else:
                    image_b64 = image_data
                content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}})
            
            messages = [{"role": "user", "content": content}]
        else:
            # 文生图模式
            messages = [{"role": "user", "content": prompt}]

        # 调用API（非流式，更容易解析）
        logger.info(f"正在调用API: {BASE_URL}/v1/chat/completions, 模型: {model}")
        try:
            response = http_session.post(
                f"{BASE_URL}/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": model,
                    "messages": messages
                },
                timeout=120  # 2分钟超时
            )
            logger.info(f"API响应状态码: {response.status_code}")
        except requests.exceptions.Timeout:
            logger.error("API请求超时")
            return jsonify({'error': '请求超时，请重试'}), 500
        except requests.exceptions.ConnectionError as e:
            logger.error(f"无法连接到API服务器: {e}")
            return jsonify({'error': '无法连接到API服务器'}), 500
        except Exception as e:
            logger.error(f"连接异常: {e}")
            msg = str(e) if app.debug else '连接失败'
            return jsonify({'error': msg}), 500

        if response.status_code != 200:
            error_detail = response.text[:200]
            logger.error(f"API返回错误状态码: {response.status_code}, 响应: {error_detail}")
            
            # 更友好的错误提示
            if response.status_code == 401:
                return jsonify({'error': 'API Key无效或已过期，请检查后重新输入'}), 401
            elif response.status_code == 403:
                return jsonify({'error': 'API Key没有访问权限'}), 403
            elif response.status_code == 429:
                return jsonify({'error': '请求过于频繁，请稍后再试'}), 429
            else:
                err_msg = f'HTTP {response.status_code}'
                if app.debug:
                    err_msg += f': {error_detail}'
                return jsonify({'error': err_msg}), response.status_code

        # 解析响应
        try:
            result = response.json()
        except Exception as e:
            logger.error(f"JSON解析失败: {e}, 响应文本: {response.text[:500]}")
            msg = f'响应解析失败: {str(e)}' if app.debug else '响应解析失败'
            return jsonify({'error': msg}), 500
        
        if 'choices' not in result or not result['choices']:
            logger.error(f"API返回格式错误: {str(result)[:500]}")
            payload = {'error': 'API返回格式错误'}
            if app.debug:
                payload['debug'] = str(result)[:200]
            return jsonify(payload), 500

        content = result['choices'][0]['message']['content']
        
        # 提取图片URL（支持多种格式）
        image_urls = []
        
        # Markdown格式: ![alt](url)
        image_urls.extend(re.findall(r'!\[.*?\]\((.*?)\)', content))
        
        # 纯URL格式
        image_urls.extend(re.findall(r'(https?://[^\s]+\.(?:jpg|jpeg|png|gif|webp))', content, re.I))
        
        # 宽松URL匹配
        for match in re.findall(r'https?://[^\s"\')\]]+', content):
            if any(ext in match.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', 'file', 'img', 'generated']):
                if match not in image_urls:
                    image_urls.append(match)

        if image_urls:
            logger.info(f"成功提取图片数量: {len(image_urls)}")
            image_urls = _rewrite_generated_image_urls(image_urls)
            return jsonify({'image': image_urls[0], 'allImages': image_urls, 'content': content})
        else:
            logger.warning(f"未找到图片，内容前500字符: {content[:500]}")
            payload = {'error': '未找到图片'}
            if app.debug:
                payload['debug'] = content[:500]
            return jsonify(payload), 500

    except Exception as e:
        logger.exception("生成图片时发生错误")
        msg = str(e) if app.debug else '服务器错误'
        return jsonify({'error': msg}), 500


@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return jsonify({'error': e.description or e.name}), e.code
    logger.exception("未处理的异常")
    msg = str(e) if app.debug else '服务器内部错误'
    return jsonify({'error': msg}), 500


@app.route('/api/download')
def download_image():
    url = request.args.get('url')
    
    if not url:
        return jsonify({'error': '缺少URL'}), 400

    ok, err = _validate_download_url(url)
    if not ok:
        return jsonify({'error': err}), 400
    
    try:
        response = http_session.get(url, timeout=30, stream=True)
        response.raise_for_status()
        ct = response.headers.get('Content-Type', 'image/jpeg')
        mimetype = ct.split(';')[0].strip() if ct else 'image/jpeg'

        chunks = []
        total = 0
        for chunk in response.iter_content(chunk_size=65536):
            if not chunk:
                continue
            total += len(chunk)
            if total > MAX_DOWNLOAD_BYTES:
                return jsonify({'error': '文件过大'}), 413
            chunks.append(chunk)

        data = b''.join(chunks)
        return Response(
            data,
            mimetype=mimetype,
            headers={
                'Content-Disposition': f'attachment; filename=ai-image-{int(time.time())}.jpg',
            }
        )
    except requests.RequestException as e:
        logger.warning("下载失败: %s", e)
        return jsonify({'error': '下载失败'}), 502


@app.route('/health')
def health():
    return {'status': 'ok'}


if __name__ == '__main__':
    # 生产环境使用 waitress 运行时忽略此配置
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000, threads=4)
