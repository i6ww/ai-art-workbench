from flask import Flask, request, jsonify, Response
import requests
import json
import re
import base64
import time

import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, 'static'), static_url_path='/')

BASE_URL = "https://www.371181668.xyz"

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
    api_key = data.get('apiKey')
    model = data.get('model')
    prompt = data.get('prompt')
    image_data = data.get('image')  # 单张图片
    images_data = data.get('images')  # 多张图片
    
    # 日志请求参数（敏感信息脱敏）
    has_image = bool(image_data or images_data)
    prompt_preview = prompt[:100] + '...' if prompt and len(prompt) > 100 else prompt
    logger.info(f"请求参数: model={model}, prompt长度={len(prompt) if prompt else 0}, 有图片={has_image}")

    if not api_key or not model or not prompt:
        logger.error(f"缺少必要参数: api_key={bool(api_key)}, model={model}, prompt={bool(prompt)}")
        return jsonify({'error': '缺少必要参数'}), 400

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
            response = requests.post(
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
            return jsonify({'error': f'连接错误: {str(e)}'}), 500

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
                return jsonify({'error': f'HTTP {response.status_code}: {error_detail}'}), response.status_code

        # 解析响应
        try:
            result = response.json()
        except Exception as e:
            logger.error(f"JSON解析失败: {e}, 响应文本: {response.text[:500]}")
            return jsonify({'error': f'响应解析失败: {str(e)}'}), 500
        
        if 'choices' not in result or not result['choices']:
            logger.error(f"API返回格式错误: {str(result)[:500]}")
            return jsonify({'error': 'API返回格式错误', 'debug': str(result)[:200]}), 500

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
            # 将图片服务器地址替换为 HTTPS 域名
            image_urls = [url.replace('http://43.165.172.5:6001', 'https://adobe.371181668.xyz') for url in image_urls]
            return jsonify({'image': image_urls[0], 'allImages': image_urls, 'content': content})
        else:
            logger.warning(f"未找到图片，内容前500字符: {content[:500]}")
            return jsonify({'error': '未找到图片', 'debug': content[:500]}), 500

    except requests.exceptions.Timeout:
        logger.error("API请求超时")
        return jsonify({'error': '请求超时，请稍后重试'}), 500
    except requests.exceptions.ConnectionError as e:
        logger.error(f"连接错误: {e}")
        return jsonify({'error': '无法连接到API服务器，请稍后重试'}), 500
    except Exception as e:
        logger.error(f"生成图片时发生错误: {e}")
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500


# 全局错误处理器
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"未处理的异常: {e}")
    return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500


@app.route('/api/download')
def download_image():
    url = request.args.get('url')
    
    if not url:
        return jsonify({'error': '缺少URL'}), 400
    
    try:
        response = requests.get(url, timeout=30)
        return Response(
            response.content,
            mimetype=response.headers.get('Content-Type', 'image/jpeg'),
            headers={
                'Content-Disposition': f'attachment; filename=ai-image-{int(time.time())}.jpg',
                'Access-Control-Allow-Origin': '*'
            }
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    return {'status': 'ok'}


if __name__ == '__main__':
    # 生产环境使用 waitress 运行时忽略此配置
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000, threads=4)
