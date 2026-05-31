import json
import re
import time
import requests
import base64
import os

Base_Url = "https://nikk.pro/"  # 填写基础Url
your_api_key = ""  # 填写你的API Key

# 图片配置
resolution = "1k"  # 分辨率: "1k", "2k", "4k"
aspect_ratio = "16:9"  # 宽高比: "1:1", "4:3", "16:9"

model = "firefly-gpt-image-2k-1x1"  # 模型名称
prompt = "将这张图片转换成动漫风格"  # 填写提示词

# 参考图片路径（图生图功能）
reference_image_path = "reference_image.png"  # 填写参考图片路径，支持 jpg/png/webp 等格式

# OpenAI 兼容端点配置
CHAT_COMPLETIONS_ENDPOINT = "/v1/chat/completions"

def encode_image_to_base64(image_path):
    """将图片文件转换为Base64编码"""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            # 获取文件扩展名
            ext = os.path.splitext(image_path)[1].lower()
            mime_type = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.webp': 'image/webp',
                '.gif': 'image/gif'
            }.get(ext, 'image/jpeg')
            return f"data:{mime_type};base64,{encoded_string}"
    except Exception as e:
        print(f"❌ 读取参考图片失败: {e}")
        return None

def save_base64_image(base64_data, output_path="generated_image.png"):
    """将Base64编码的图片数据保存为文件"""
    try:
        # 移除可能的data URI前缀
        if ',' in base64_data:
            base64_data = base64_data.split(',')[1]
        
        # 解码Base64数据
        image_data = base64.b64decode(base64_data)
        
        # 保存为文件
        with open(output_path, "wb") as f:
            f.write(image_data)
        
        return True, output_path
    except Exception as e:
        return False, str(e)

def download_image_from_url(img_url, output_path="generated_image.png"):
    """从URL下载图片"""
    try:
        # 如果是Base64数据URI
        if img_url.startswith('data:'):
            return save_base64_image(img_url, output_path)
        
        # 如果是HTTP/HTTPS链接
        if img_url.startswith('http://') or img_url.startswith('https://'):
            response = requests.get(img_url, timeout=60)
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return True, output_path
            else:
                return False, f"HTTP {response.status_code}"
        
        # 纯Base64字符串
        return save_base64_image(img_url, output_path)
    except Exception as e:
        return False, str(e)

def test_api(prompt, ref_image_path=None):
    # 打开日志文件
    log_file = open("api_test_log.txt", "w", encoding="utf-8")
    
    def log(message, end='\n'):
        print(message, end=end, flush=True)
        if end == '\n':
            log_file.write(message + "\n")
        else:
            log_file.write(message)
        log_file.flush()
    
    log("=" * 50)
    log("🚀 发送请求...")
    log(f"📝 提示词: {prompt}")
    log(f"🎯 模型: {model}")
    log(f"📐 分辨率: {resolution}")
    log(f"🌐 API URL: {Base_Url}")
    
    # 检查是否有参考图片（图生图模式）
    image_base64 = None
    if ref_image_path and os.path.exists(ref_image_path):
        log(f"🖼️ 参考图片: {ref_image_path}")
        image_base64 = encode_image_to_base64(ref_image_path)
        if image_base64:
            log("✅ 参考图片加载成功")
        else:
            log("⚠️ 参考图片加载失败，将使用文生图模式")
    elif ref_image_path:
        log(f"⚠️ 参考图片不存在: {ref_image_path}，将使用文生图模式")
    
    log("=" * 50)
    log("正在准备请求数据...")
    
    # 构建 OpenAI 兼容的请求数据
    # 使用 messages 字段，支持图生图
    content = []
    
    # 如果有参考图片，先添加图片
    if image_base64:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": image_base64
            }
        })
    
    # 添加文本提示词
    content.append({
        "type": "text",
        "text": prompt
    })
    
    data = {
        "model": model,
        "messages": [{
            "role": "user",
            "content": content
        }],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {
                "aspectRatio": aspect_ratio,
                "imageSize": resolution.upper()
            }
        },
        "stream": False
    }
    
    log("正在发送请求...")
    try:
        request_url = f"{Base_Url}{CHAT_COMPLETIONS_ENDPOINT}"
        log(f"请求URL: {request_url}")
        log(f"请求头: Authorization: Bearer ***")
        log(f"请求数据: {json.dumps(data, ensure_ascii=False)[:500]}...")
        
        log("开始发送POST请求...")
        response = requests.post(
            request_url,
            headers={
                "Authorization": f"Bearer {your_api_key}",
                "Content-Type": "application/json"
            },
            json=data,
            stream=False,
            timeout=600
        )
        log(f"请求发送成功，状态码: {response.status_code}")
        log(f"响应头: {dict(response.headers)}")
    except requests.exceptions.SSLError as e:
        log(f"⚠️ SSL错误: {e}")
        log("尝试重试...")
        try:
            response = requests.post(
                request_url,
                headers={
                    "Authorization": f"Bearer {your_api_key}",
                    "Content-Type": "application/json"
                },
                json=data,
                stream=False,
                timeout=600,
                verify=False
            )
            log(f"重试成功，状态码: {response.status_code}")
        except Exception as e2:
            log(f"❌ 重试失败: {e2}")
            log_file.close()
            return
    except Exception as e:
        log(f"❌ 请求发送失败: {e}")
        import traceback
        log(f"错误堆栈: {traceback.format_exc()}")
        log_file.close()
        return
    
    log(f"📥 HTTP状态码: {response.status_code}")
    log(f"📥 开始接收响应...")
    log("-" * 50)
    
    start_time = time.time()  # 记录开始时间
    
    try:
        # 读取完整响应
        response_data = response.content.decode('utf-8')
        log(f"响应数据长度: {len(response_data)} 字符")
        
        # 尝试解析JSON
        try:
            result = json.loads(response_data)
            
            # 检查是否有错误
            if 'error' in result:
                log(f"\n❌ API错误: {result['error']}")
                log_file.close()
                return
            
            # 检查是否有 choices (OpenAI 格式)
            if 'choices' in result and result['choices']:
                choice = result['choices'][0]
                if 'message' in choice and 'content' in choice['message']:
                    content = choice['message']['content']
                    
                    # 检查内容是否包含图片链接（markdown格式）
                    img_match = re.search(r'!\[.*?\]\((.+?)\)', content)
                    if img_match:
                        img_url = img_match.group(1)
                        elapsed_time = time.time() - start_time
                        log(f"\n" + "=" * 50)
                        log(f"🖼️ 生成图片成功!")
                        log(f"📎 图片链接: {img_url[:100]}...")
                        log(f"⏱️ 耗时: {elapsed_time:.1f}秒")
                        log(f"=" * 50)
                        
                        # 保存链接到文本文件
                        with open("generated_image.txt", "w") as f:
                            f.write(img_url)
                        log(f"💾 图片链接已保存到 generated_image.txt")
                        
                        # 下载并保存图片
                        log(f"📥 正在下载图片...")
                        success, result = download_image_from_url(img_url, "generated_image.png")
                        if success:
                            log(f"✅ 图片已保存到: {result}")
                            # 获取文件大小
                            file_size = os.path.getsize(result)
                            log(f"📁 文件大小: {file_size / 1024:.2f} KB")
                        else:
                            log(f"❌ 保存图片失败: {result}")
                        
                        log_file.close()
                        return
                    
                    # 检查是否是直接的URL
                    url_match = re.search(r'https?://[^\s\[\]<>"\'\)]+\.(?:png|jpg|jpeg|webp|gif)', content, re.IGNORECASE)
                    if url_match:
                        img_url = url_match.group(0)
                        elapsed_time = time.time() - start_time
                        log(f"\n" + "=" * 50)
                        log(f"🖼️ 生成图片成功!")
                        log(f"📎 图片链接: {img_url[:100]}...")
                        log(f"⏱️ 耗时: {elapsed_time:.1f}秒")
                        log(f"=" * 50)
                        
                        # 保存链接到文本文件
                        with open("generated_image.txt", "w") as f:
                            f.write(img_url)
                        log(f"💾 图片链接已保存到 generated_image.txt")
                        
                        # 下载并保存图片
                        log(f"📥 正在下载图片...")
                        success, result = download_image_from_url(img_url, "generated_image.png")
                        if success:
                            log(f"✅ 图片已保存到: {result}")
                            file_size = os.path.getsize(result)
                            log(f"📁 文件大小: {file_size / 1024:.2f} KB")
                        else:
                            log(f"❌ 保存图片失败: {result}")
                        
                        log_file.close()
                        return
            
            # 检查是否有 candidates (Gemini 格式)
            if 'candidates' in result and result['candidates']:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    for part in candidate['content']['parts']:
                        if 'inlineData' in part:
                            # 收到图片数据
                            img_data = part['inlineData']
                            img_base64 = img_data.get('data', '')
                            elapsed_time = time.time() - start_time
                            log(f"\n" + "=" * 50)
                            log(f"🖼️ 生成图片成功!")
                            log(f"📎 图片数据长度: {len(img_base64)} 字符")
                            log(f"⏱️ 耗时: {elapsed_time:.1f}秒")
                            log(f"=" * 50)
                            
                            # 保存Base64数据到文本文件
                            with open("generated_image.txt", "w") as f:
                                f.write(img_base64)
                            log(f"💾 Base64数据已保存到 generated_image.txt")
                            
                            # 保存为实际图片文件
                            success, result = save_base64_image(img_base64, "generated_image.png")
                            if success:
                                log(f"✅ 图片已保存到: {result}")
                                file_size = os.path.getsize(result)
                                log(f"📁 文件大小: {file_size / 1024:.2f} KB")
                            else:
                                log(f"❌ 保存图片失败: {result}")
                            
                            log_file.close()
                            return
                   
            # 如果没有找到图片，打印响应内容供调试
            log(f"\n📋 完整响应内容:")
            log(response_data[:1000] + "..." if len(response_data) > 1000 else response_data)
            
        except json.JSONDecodeError as e:
            log(f"\n⚠️ JSON解析失败，响应可能不是JSON格式")
            log(f"响应内容: {response_data[:500]}...")
    
    except Exception as e:
        log(f"\n❌ 错误: {e}")
        import traceback
        log(f"错误堆栈: {traceback.format_exc()}")
    
    elapsed_time = time.time() - start_time
    log("\n" + "-" * 50)
    log(f"✅ 完成!")
    log(f"⏱️ 耗时: {elapsed_time:.1f}秒")
    log_file.close()

test_api(prompt, reference_image_path)
