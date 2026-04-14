from flask import Flask, request, jsonify, Response
import requests
import json
import re
import base64
import time

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, 'static'), static_url_path='/')

BASE_URL = "https://www.371181668.xyz"

# 模型列表
MODELS = {
    "1K": [
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
}


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/api/models')
def get_models():
    return jsonify(MODELS)


@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    api_key = data.get('apiKey')
    model = data.get('model')
    prompt = data.get('prompt')
    image_data = data.get('image')  # 单张图片
    images_data = data.get('images')  # 多张图片

    if not api_key or not model or not prompt:
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
        except requests.exceptions.Timeout:
            return jsonify({'error': '请求超时，请重试'}), 500
        except requests.exceptions.ConnectionError:
            return jsonify({'error': '无法连接到API服务器'}), 500
        except Exception as e:
            return jsonify({'error': f'连接错误: {str(e)}'}), 500

        if response.status_code != 200:
            return jsonify({'error': f'HTTP {response.status_code}: {response.text[:200]}'}), 500

        # 解析响应
        result = response.json()
        
        if 'choices' not in result or not result['choices']:
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
            return jsonify({'image': image_urls[0], 'allImages': image_urls, 'content': content})
        else:
            return jsonify({'error': '未找到图片', 'debug': content[:500]}), 500

    except requests.exceptions.Timeout:
        return jsonify({'error': '请求超时'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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