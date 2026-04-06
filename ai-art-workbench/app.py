from flask import Flask, request, jsonify, Response
import requests
import json
import re
import base64

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, 'static'), static_url_path='/')

BASE_URL = "https://www.371181668.xyz"

MODELS = {
    "1K": [
        "nano-banana-pro-1k-16:9",
        "nano-banana-pro-1k-9:16",
        "nano-banana-pro-1k-1:1",
        "nano-banana-pro-1k-4:3",
        "nano-banana-pro-1k-3:4",
        "nano-banana-2-1k-16:9",
        "nano-banana-2-1k-9:16",
        "nano-banana-2-1k-1:1",
        "nano-banana-2-1k-4:3",
        "nano-banana-2-1k-3:4",
    ],
    "2K": [
        "nano-banana-pro-2k-16:9",
        "nano-banana-pro-2k-9:16",
        "nano-banana-pro-2k-1:1",
        "nano-banana-pro-2k-4:3",
        "nano-banana-pro-2k-3:4",
        "nano-banana-2-2k-16:9",
        "nano-banana-2-2k-9:16",
        "nano-banana-2-2k-1:1",
        "nano-banana-2-2k-4:3",
        "nano-banana-2-2k-3:4",
    ],
    "4K": [
        "nano-banana-pro-4k-16:9",
        "nano-banana-pro-4k-9:16",
        "nano-banana-pro-4k-1:1",
        "nano-banana-pro-4k-4:3",
        "nano-banana-pro-4k-3:4",
        "nano-banana-2-4k-16:9",
        "nano-banana-2-4k-9:16",
        "nano-banana-2-4k-1:1",
        "nano-banana-2-4k-4:3",
        "nano-banana-2-4k-3:4",
    ]
}


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/api/models')
def get_models():
    return jsonify(MODELS)


@app.route('/api/text-to-image', methods=['POST'])
def text_to_image():
    data = request.json
    api_key = data.get('apiKey')
    model = data.get('model')
    prompt = data.get('prompt')

    if not api_key or not model or not prompt:
        return jsonify({'error': '缺少必要参数'}), 400

    def generate():
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True
        }

        try:
            response = requests.post(
                f"{BASE_URL}/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json=payload,
                stream=True,
                timeout=600
            )
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            return

        if response.status_code != 200:
            yield f"data: {json.dumps({'error': f'HTTP {response.status_code}'})}\n\n"
            return

        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                
                # 检查是否是 markdown 图片链接
                img_match = re.search(r'!\[.*?\]\((.+?)\)', line_str)
                if img_match:
                    img_url = img_match.group(1)
                    yield f"data: {json.dumps({'image': img_url, 'done': True})}\n\n"
                    return

                # 处理SSE数据
                if line_str.startswith('data: '):
                    line_str = line_str[6:]
                if line_str.strip() == '[DONE]':
                    yield f"data: {json.dumps({'done': True})}\n\n"
                    continue
                if not line_str.strip():
                    continue

                try:
                    line_json = json.loads(line_str)
                    if 'choices' in line_json and line_json['choices']:
                        choice = line_json['choices'][0]
                        if 'delta' in choice:
                            content = choice['delta'].get('content', '')
                            if content:
                                yield f"data: {json.dumps({'content': content})}\n\n"
                except json.JSONDecodeError:
                    continue

    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/image-to-image', methods=['POST'])
def image_to_image():
    data = request.json
    api_key = data.get('apiKey')
    model = data.get('model')
    prompt = data.get('prompt')
    image_data = data.get('image')

    if not api_key or not model or not prompt or not image_data:
        return jsonify({'error': '缺少必要参数'}), 400

    def generate():
        # 确保图片是base64格式
        if ',' in image_data:
            image_b64 = image_data.split(',')[1]
        else:
            image_b64 = image_data

        payload = {
            "model": model,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
                ]
            }],
            "stream": True
        }

        try:
            response = requests.post(
                f"{BASE_URL}/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json=payload,
                stream=True,
                timeout=600
            )
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            return

        if response.status_code != 200:
            yield f"data: {json.dumps({'error': f'HTTP {response.status_code}'})}\n\n"
            return

        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                
                # 检查是否是 markdown 图片链接
                img_match = re.search(r'!\[.*?\]\((.+?)\)', line_str)
                if img_match:
                    img_url = img_match.group(1)
                    yield f"data: {json.dumps({'image': img_url, 'done': True})}\n\n"
                    return

                # 处理SSE数据
                if line_str.startswith('data: '):
                    line_str = line_str[6:]
                if line_str.strip() == '[DONE]':
                    yield f"data: {json.dumps({'done': True})}\n\n"
                    continue
                if not line_str.strip():
                    continue

                try:
                    line_json = json.loads(line_str)
                    if 'choices' in line_json and line_json['choices']:
                        choice = line_json['choices'][0]
                        if 'delta' in choice:
                            content = choice['delta'].get('content', '')
                            if content:
                                yield f"data: {json.dumps({'content': content})}\n\n"
                except json.JSONDecodeError:
                    continue

    return Response(generate(), mimetype='text/event-stream')


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


if __name__ == '__main__':
    import time
    app.run(host='0.0.0.0', port=5000, debug=True)
