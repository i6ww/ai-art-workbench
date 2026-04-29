#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Art Workbench - API 测试脚本
获取模型列表
"""

import requests
import json
import os

# 设置控制台编码
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# API 配置
BASE_URL = "https://www.371181668.xyz"
API_KEY = "sk-07YvR2sYZyp7Vd8EXygx5FwnPXtYhhYUOcQn9qtrc31Gfrc4"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def test_model_list_endpoint():
    """测试 /v1/models 端点"""
    print("\n" + "=" * 60)
    print("尝试获取模型列表...")
    print("=" * 60)
    
    endpoints = [
        "/v1/models",
        "/models",
        "/api/models",
    ]
    
    all_models = []
    
    for endpoint in endpoints:
        try:
            url = BASE_URL + endpoint
            print(f"\n尝试: {endpoint}")
            response = requests.get(url, headers=HEADERS, timeout=30)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "data" in data:
                        models = data["data"]
                        print(f"  [OK] 成功! 获取到 {len(models)} 个模型")
                        for m in models:
                            model_id = m.get('id', 'unknown')
                            all_models.append(model_id)
                            print(f"    - {model_id}")
                        return data
                    elif isinstance(data, dict):
                        # 尝试其他格式
                        print(f"  响应结构: {list(data.keys())}")
                        for key, value in data.items():
                            if isinstance(value, list):
                                print(f"  [{key}] 包含 {len(value)} 项")
                                for item in value[:5]:
                                    print(f"    - {item}")
                                if len(value) > 5:
                                    print(f"    ... 还有 {len(value)-5} 项")
                except json.JSONDecodeError:
                    print(f"  响应(非JSON): {response.text[:200]}")
            else:
                try:
                    error_data = response.json()
                    print(f"  错误: {json.dumps(error_data, indent=2)[:200]}")
                except:
                    print(f"  响应: {response.text[:100]}")
        except Exception as e:
            print(f"  请求失败: {e}")
    
    return all_models


def generate_model_list():
    """生成所有可能的模型名称"""
    print("\n" + "=" * 60)
    print("生成完整模型列表...")
    print("=" * 60)
    
    resolutions = ["1k", "2k", "4k"]
    ratios = ["16x9", "9x16", "1x1", "4x3", "3x4", "21x9", "4x5", "5x4", "1x4", "1x8", "2x3", "3x2", "8x1"]
    
    models = []
    
    # firefly-nano-banana 系列
    for res in resolutions:
        for ratio in ratios:
            models.append(f"firefly-nano-banana-{res}-{ratio}")
            models.append(f"firefly-nano-banana-pro-{res}-{ratio}")
            models.append(f"firefly-nano-banana2-{res}-{ratio}")
    
    # Sora2 视频模型
    durations = ["4s", "8s", "12s"]
    video_ratios = ["16x9", "9x16"]
    for dur in durations:
        for ratio in video_ratios:
            models.append(f"firefly-sora2-{dur}-{ratio}")
            models.append(f"firefly-sora2-pro-{dur}-{ratio}")
    
    # Veo31 视频模型
    veo_durations = ["4s", "6s", "8s"]
    veo_resolutions = ["1080p", "720p"]
    for dur in veo_durations:
        for ratio in video_ratios:
            for res in veo_resolutions:
                models.append(f"firefly-veo31-{dur}-{ratio}-{res}")
                models.append(f"firefly-veo31-ref-{dur}-{ratio}-{res}")
                models.append(f"firefly-veo31-fast-{dur}-{ratio}-{res}")
    
    print(f"共生成 {len(models)} 个模型名称")
    return models


def save_models_to_file(models, api_models=None, filename="available_models.txt"):
    """保存模型列表到文件"""
    print(f"\n保存模型列表到: {filename}")
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("AI Art Workbench - 可用模型列表\n")
        f.write("=" * 60 + "\n\n")
        
        # 按类型分组
        categories = {
            "Image - firefly-nano-banana": [],
            "Image - firefly-nano-banana-pro": [],
            "Image - firefly-nano-banana2": [],
            "Video - firefly-sora2": [],
            "Video - firefly-sora2-pro": [],
            "Video - firefly-veo31": [],
            "Video - firefly-veo31-ref": [],
            "Video - firefly-veo31-fast": [],
            "Other": [],
        }
        
        for model in sorted(models):
            if "nano-banana-pro" in model:
                categories["Image - firefly-nano-banana-pro"].append(model)
            elif "nano-banana2" in model:
                categories["Image - firefly-nano-banana2"].append(model)
            elif "nano-banana" in model:
                categories["Image - firefly-nano-banana"].append(model)
            elif "veo31-ref" in model:
                categories["Video - firefly-veo31-ref"].append(model)
            elif "veo31-fast" in model:
                categories["Video - firefly-veo31-fast"].append(model)
            elif "veo31" in model:
                categories["Video - firefly-veo31"].append(model)
            elif "sora2-pro" in model:
                categories["Video - firefly-sora2-pro"].append(model)
            elif "sora2" in model:
                categories["Video - firefly-sora2"].append(model)
            else:
                categories["Other"].append(model)
        
        total = 0
        for category, items in categories.items():
            if items:
                f.write(f"\n## {category}\n")
                for item in sorted(items):
                    f.write(f"  {item}\n")
                f.write(f"  Subtotal: {len(items)}\n")
                total += len(items)
        
        f.write(f"\n{'=' * 60}\n")
        f.write(f"Total: {total} models\n")
        
        # 如果有API返回的模型列表
        if api_models:
            f.write(f"\n{'=' * 60}\n")
            f.write("API returned models:\n")
            f.write("=" * 60 + "\n")
            for m in api_models:
                f.write(f"  {m}\n")
    
    print(f"[OK] Saved {total} models to {filename}")
    return total


def main():
    print("\n" + "=" * 60)
    print("   AI Art Workbench - API Test Tool")
    print("=" * 60)
    print(f"\nAPI URL: {BASE_URL}")
    print(f"API Key: {API_KEY[:15]}...{API_KEY[-10:]}")
    print()
    
    # 尝试从API获取模型列表
    api_result = test_model_list_endpoint()
    
    # 生成完整模型列表
    all_models = generate_model_list()
    
    # 保存到文件
    if api_result:
        if isinstance(api_result, dict) and "data" in api_result:
            api_models = [m.get('id') for m in api_result.get('data', [])]
        else:
            api_models = []
    else:
        api_models = None
    
    total = save_models_to_file(all_models, api_models)
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
    
    return all_models


if __name__ == "__main__":
    main()
