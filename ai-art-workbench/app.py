from flask import Flask, request, jsonify, Response, send_from_directory
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import re
import time
import ipaddress
import socket
from urllib.parse import urlparse

import os
import logging
from typing import Optional
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor

from werkzeug.exceptions import HTTPException

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, 'static'), static_url_path='/')
app.config["DEBUG"] = os.environ.get("FLASK_DEBUG", "").lower() in ("1", "true", "yes")

BASE_URL = os.environ.get("API_BASE_URL", "https://371181668.xyz").rstrip("/")

LISTEN_PORT = int(os.environ.get("PORT", os.environ.get("SERVER_PORT", "80")))
UPSTREAM_TIMEOUT_SECONDS = int(os.environ.get("UPSTREAM_TIMEOUT_SECONDS", "300"))
USE_UPSTREAM_STREAM = os.environ.get("USE_UPSTREAM_STREAM", "1").lower() not in ("0", "false", "no")
WAITRESS_THREADS = int(os.environ.get("WAITRESS_THREADS", "32"))
GENERATE_WORKERS = int(os.environ.get("GENERATE_WORKERS", "16"))
MAX_PENDING_JOBS = int(os.environ.get("MAX_PENDING_JOBS", "300"))
JOB_TTL_SECONDS = int(os.environ.get("JOB_TTL_SECONDS", "3600"))
MAX_JOB_STORE = int(os.environ.get("MAX_JOB_STORE", "1000"))
GEMINI_DEFAULT_IMAGE_SIZE = os.environ.get("GEMINI_DEFAULT_IMAGE_SIZE", "1K").upper()
GEMINI_MODEL_VARIANT_SEPARATOR = "__"
GEMINI_IMAGE_SIZES = ("1K", "2K", "4K")
GEMINI_MODEL_BASE_SIZES = {
    "gemini-3-pro-image-preview": GEMINI_IMAGE_SIZES,
    "gemini-3.1-flash-image-preview": GEMINI_IMAGE_SIZES,
    "gemini-3.0-pro-image-2k": ("2K",),
    "gemini-3.0-pro-image-4k": ("4K",),
}


def _parse_image_url_rewrites():
    # 默认不重写；仅当上游偶发返回旧内网/HTTP 图片前缀时再设置 IMAGE_URL_REWRITES，例如：
    # http://43.165.172.5:6001|https://adobe.371181668.xyz
    raw = os.environ.get("IMAGE_URL_REWRITES", "")
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
        "www.371181668.xyz,adobe.371181668.xyz,adobe2.371181668.xyz,371181668.xyz",
    ).split(",")
    if h.strip()
)

MAX_DOWNLOAD_BYTES = int(os.environ.get("MAX_DOWNLOAD_BYTES", str(300 * 1024 * 1024)))
HTTP_POOL_CONNECTIONS = int(os.environ.get("HTTP_POOL_CONNECTIONS", "32"))
HTTP_POOL_MAXSIZE = int(os.environ.get("HTTP_POOL_MAXSIZE", "128"))

http_session = requests.Session()
http_session.headers.update(
    {"User-Agent": "Mozilla/5.0 (compatible; AIWorkbench/1.0)"}
)
_adapter = HTTPAdapter(
    pool_connections=HTTP_POOL_CONNECTIONS,
    pool_maxsize=HTTP_POOL_MAXSIZE,
    max_retries=Retry(total=0, connect=0, read=0, redirect=0),
)
http_session.mount("https://", _adapter)
http_session.mount("http://", _adapter)


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


def _extract_upstream_error_text(response_text: str) -> str:
    """Try to pull a human-readable message from upstream JSON or plain text."""
    text = (response_text or "").strip()
    if not text:
        return ""
    try:
        j = json.loads(text)
        err = j.get("error")
        if isinstance(err, dict):
            return (err.get("message") or err.get("msg") or "").strip()
        if isinstance(err, str):
            return err.strip()
        m = j.get("message")
        if isinstance(m, str):
            return m.strip()
    except Exception:
        pass
    return text[:800]


def _error_payload(
    message: str,
    code: str,
    *,
    status_code: int = 500,
    hint: Optional[str] = None,
    stage: str = "server",
    retryable: bool = False,
    upstream_status: Optional[int] = None,
    upstream_message: Optional[str] = None,
    debug: Optional[str] = None,
) -> dict:
    payload = {
        "error": message,
        "code": code,
        "statusCode": status_code,
        "stage": stage,
        "retryable": retryable,
    }
    if hint:
        payload["hint"] = hint
    if upstream_status is not None:
        payload["upstreamStatus"] = upstream_status
    if upstream_message:
        payload["upstreamMessage"] = upstream_message[:800]
    if debug and app.debug:
        payload["debug"] = debug[:1000]
    return payload


def _upstream_user_message(status_code: int, response_text: str) -> Optional[str]:
    """Map known upstream errors to stable Chinese copy for end users."""
    inner = _extract_upstream_error_text(response_text)
    blob = f"{inner} {response_text or ''}".lower()
    if status_code == 400:
        if "image too large" in blob or "image_too_large" in blob:
            return (
                "参考图体积过大：上游限制单张不超过 10MB，请压缩、裁剪或降低分辨率后再试；"
                "多张参考图时可减少张数。"
            )
        if "too large" in blob and "mb" in blob and ("max" in blob or "10" in blob):
            return (
                "图片或请求体过大：请将单张参考图控制在约 10MB 以内，或减少参考图数量后再试。"
            )
        if "payload too large" in blob or "request entity too large" in blob:
            return "请求体过大：请压缩参考图或减少图片数量后再试。"
    if status_code == 413:
        return "上传内容过大：请压缩图片或减少参考图数量后再试。"
    if status_code in (504, 521, 522, 524):
        return (
            f"上游生成服务超时或暂时不可用（HTTP {status_code}）。"
            "图片可能仍在后台生成，请稍后重试；若频繁出现请联系管理员检查上游服务。"
        )
    return None


def _upstream_error_payload(status_code: int, response_text: str, *, stage: str = "upstream") -> dict:
    inner = _extract_upstream_error_text(response_text)
    mapped = _upstream_user_message(status_code, response_text)
    retryable = status_code in (408, 409, 425, 429, 500, 502, 503, 504, 521, 522, 524)

    if mapped:
        message = mapped
        code = "UPSTREAM_KNOWN_ERROR"
        hint = "请按提示调整后重试；若多次出现，请联系管理员检查上游服务。"
    elif status_code == 400:
        message = "上游拒绝了这次生成请求（HTTP 400）。"
        code = "UPSTREAM_BAD_REQUEST"
        hint = "请检查模型是否支持当前模式、提示词是否为空、参考图数量和单张大小是否符合限制。"
    elif status_code == 401:
        message = "API Key 无效或已过期（上游返回 401）。"
        code = "UPSTREAM_AUTH_FAILED"
        hint = "请在右侧重新粘贴 API Key，或到上游控制台确认 Key 是否仍可用。"
    elif status_code == 403:
        message = "当前 API Key 没有权限使用这个模型或接口（上游返回 403）。"
        code = "UPSTREAM_FORBIDDEN"
        hint = "请更换有权限的 Key，或联系管理员开通该模型。"
    elif status_code == 404:
        message = "上游接口或模型不存在（HTTP 404）。"
        code = "UPSTREAM_NOT_FOUND"
        hint = "请确认 API_BASE_URL、模型 ID 和上游服务版本是否匹配。"
    elif status_code == 429:
        message = "上游请求过于频繁或额度不足（HTTP 429）。"
        code = "UPSTREAM_RATE_LIMITED"
        hint = "请稍后重试；如果一直出现，请检查上游额度或并发限制。"
    elif status_code in (500, 502, 503):
        message = f"上游生成服务异常（HTTP {status_code}）。"
        code = "UPSTREAM_SERVER_ERROR"
        hint = "这通常不是浏览器问题。请稍后重试；若持续出现，请管理员查看上游服务日志。"
    elif status_code in (504, 521, 522, 524):
        message = f"上游生成服务超时或暂时不可用（HTTP {status_code}）。"
        code = "UPSTREAM_TIMEOUT"
        hint = "生成可能仍在上游后台运行。建议稍后重试，或降低分辨率/缩短视频时长。"
    else:
        message = f"上游返回错误（HTTP {status_code}）。"
        code = "UPSTREAM_ERROR"
        hint = "请检查模型、提示词、参考图和上游服务状态。"

    return _error_payload(
        message,
        code,
        status_code=status_code,
        hint=hint,
        stage=stage,
        retryable=retryable,
        upstream_status=status_code,
        upstream_message=inner,
    )


def _chat_content_from_result(result):
    if 'choices' not in result or not result['choices']:
        logger.error(f"API返回格式错误: {str(result)[:500]}")
        return None, 'API返回格式错误'

    choice0 = result['choices'][0]
    msg_obj = choice0.get('message') if isinstance(choice0, dict) else None
    if not isinstance(msg_obj, dict):
        logger.error(f"API choices[0] 无 message: {str(result)[:500]}")
        return None, 'API返回格式错误'

    content = msg_obj.get('content')
    if not isinstance(content, str):
        logger.error(f"API message 无 content 或类型异常: {type(content)}")
        return None, 'API返回无文本内容'
    return content, None


def _stream_delta_content(event):
    choices = event.get("choices")
    if isinstance(choices, list) and choices:
        choice = choices[0]
        if isinstance(choice, dict):
            delta = choice.get("delta")
            if isinstance(delta, dict) and isinstance(delta.get("content"), str):
                return delta["content"]
            message = choice.get("message")
            if isinstance(message, dict) and isinstance(message.get("content"), str):
                return message["content"]
            if isinstance(choice.get("text"), str):
                return choice["text"]
    if isinstance(event.get("content"), str):
        return event["content"]
    return ""


def _read_streaming_chat_content(response):
    parts = []
    last_json = None
    for raw_line in response.iter_lines(decode_unicode=True):
        if not raw_line:
            continue
        line = raw_line.strip()
        if line.startswith("data:"):
            line = line[5:].strip()
        if not line or line == "[DONE]":
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            logger.debug("忽略非 JSON 流式片段: %s", line[:120])
            continue
        last_json = event
        if isinstance(event.get("error"), (str, dict)):
            return "", _extract_upstream_error_text(json.dumps(event, ensure_ascii=False))
        piece = _stream_delta_content(event)
        if piece:
            parts.append(piece)

    content = "".join(parts)
    if content:
        return content, None
    if isinstance(last_json, dict):
        content, err = _chat_content_from_result(last_json)
        if content:
            return content, None
        return "", err
    return "", "上游没有返回生成内容"


def _extract_image_urls(content):
    image_urls = []
    image_urls.extend(re.findall(r'!\[.*?\]\((.*?)\)', content))
    image_urls.extend(re.findall(r'(https?://[^\s]+\.(?:jpg|jpeg|png|gif|webp))', content, re.I))
    for match in re.findall(r'https?://[^\s"\')\]]+', content):
        if any(ext in match.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', 'file', 'img', 'generated']):
            if match not in image_urls:
                image_urls.append(match)
    return image_urls


def _normalize_media_url(url: str) -> str:
    url = (url or "").strip().strip("<>").strip('"').strip("'")
    if url.startswith("/"):
        return BASE_URL + url
    return url


def _extract_video_urls(content):
    video_urls = []
    candidates = []
    candidates.extend(re.findall(r'!\[.*?\]\((.*?)\)', content or ""))
    candidates.extend(re.findall(r'\[.*?\]\((.*?)\)', content or ""))
    candidates.extend(re.findall(r'(?:https?://|/)[^\s"\')\]]+', content or ""))

    for raw_url in candidates:
        url = _normalize_media_url(raw_url)
        lower = url.lower().split("?", 1)[0]
        if any(lower.endswith(ext) for ext in (".mp4", ".mov", ".webm", ".m4v")):
            if url not in video_urls:
                video_urls.append(url)
    return video_urls


def _is_video_model(model: str) -> bool:
    return (model or "").startswith((
        "firefly-sora2-",
        "firefly-veo31-",
        "firefly-kling3-",
    ))


def _is_gemini_image_model(model: str) -> bool:
    return _gemini_upstream_model(model).startswith("gemini-") and "image" in _gemini_upstream_model(model)


def _gemini_upstream_model(model: str) -> str:
    return (model or "").split(GEMINI_MODEL_VARIANT_SEPARATOR, 1)[0]


def _gemini_image_size(model: str) -> str:
    match = re.search(r'__size-(1k|2k|4k)(?:__|$)', model, re.I)
    if match:
        return match.group(1).upper()
    match = re.search(r'-(1k|2k|4k)(?:-|$)', model, re.I)
    if match:
        return match.group(1).upper()
    return GEMINI_DEFAULT_IMAGE_SIZE


def _gemini_generation_config(model: str) -> dict:
    return {
        "responseModalities": ["IMAGE"],
        "imageConfig": {
            "imageSize": _gemini_image_size(model),
        },
    }


def _gemini_prompt_with_constraints(prompt: str, model: str) -> str:
    image_size = _gemini_image_size(model)
    return (
        f"{prompt}\n\n"
        f"Output requirements: generate the final image at image size {image_size}. "
        "Use the model default aspect ratio."
    )


def _gemini_model_option(base_model: str, size: str) -> str:
    return f"{base_model}{GEMINI_MODEL_VARIANT_SEPARATOR}size-{size.lower()}"


def _make_gemini_model_options() -> list[str]:
    out = []
    for base_model, sizes in GEMINI_MODEL_BASE_SIZES.items():
        for size in sizes:
            out.append(_gemini_model_option(base_model, size))
    return out


def _make_video_model_options() -> list[str]:
    models = []
    for family in ("firefly-sora2",):
        for duration in ("4s", "8s", "12s"):
            for ratio in ("16x9", "9x16"):
                models.append(f"{family}-{duration}-{ratio}")

    for family in ("firefly-veo31", "firefly-veo31-ref", "firefly-veo31-fast"):
        for duration in ("4s", "6s", "8s"):
            for ratio in ("16x9", "9x16"):
                for resolution in ("1080p", "720p"):
                    models.append(f"{family}-{duration}-{ratio}-{resolution}")

    for duration in ("5s", "10s", "15s"):
        for ratio in ("16x9", "9x16"):
            models.append(f"firefly-kling3-{duration}-{ratio}")

    return models


def _extract_inline_image_data(result):
    images = []
    candidates = result.get("candidates")
    if not isinstance(candidates, list):
        return images

    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        content = candidate.get("content")
        parts = content.get("parts") if isinstance(content, dict) else None
        if not isinstance(parts, list):
            continue
        for part in parts:
            if not isinstance(part, dict):
                continue
            inline_data = part.get("inlineData") or part.get("inline_data")
            if not isinstance(inline_data, dict):
                continue
            data = inline_data.get("data")
            if not isinstance(data, str) or not data.strip():
                continue
            if data.startswith("data:"):
                images.append(data)
            else:
                mime_type = inline_data.get("mimeType") or inline_data.get("mime_type") or "image/png"
                images.append(f"data:{mime_type};base64,{data}")
    return images


def _should_retry_without_stream(status_code: int, response_text: str) -> bool:
    blob = (response_text or "").lower()
    stream_words = ("stream", "streaming", "流式")
    reject_words = ("not support", "unsupported", "unknown", "invalid", "unrecognized", "不支持", "无效")
    return status_code in (400, 404, 422) and any(w in blob for w in stream_words) and any(w in blob for w in reject_words)


def _upstream_error_response(status_code: int, error_detail: str):
    mapped = _upstream_user_message(status_code, error_detail)
    if mapped:
        return jsonify({'error': mapped}), status_code

    if status_code == 401:
        return jsonify({'error': 'API Key无效或已过期，请检查后重新输入'}), 401
    if status_code == 403:
        return jsonify({'error': 'API Key没有访问权限'}), 403
    if status_code == 429:
        return jsonify({'error': '请求过于频繁，请稍后再试'}), 429

    err_msg = (
        f"上游服务返回错误（HTTP {status_code}）。"
        "请检查模型、提示词与参考图大小后重试。"
    )
    if app.debug:
        err_msg = f"{err_msg} 调试信息：{error_detail[:500]}"
    return jsonify({'error': err_msg}), status_code


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

# 模型列表（与上游 GET /v1/models 对齐；可用 _fetch_models_from_api.py --patch-app 刷新）
MODELS = {
    "1K": [
        "firefly-nano-banana-1k-16x9",
        "firefly-nano-banana-1k-1x1",
        "firefly-nano-banana-1k-21x9",
        "firefly-nano-banana-1k-2x3",
        "firefly-nano-banana-1k-3x2",
        "firefly-nano-banana-1k-3x4",
        "firefly-nano-banana-1k-4x3",
        "firefly-nano-banana-1k-4x5",
        "firefly-nano-banana-1k-5x4",
        "firefly-nano-banana-1k-9x16",
        "firefly-nano-banana-pro-1k-16x9",
        "firefly-nano-banana-pro-1k-1x1",
        "firefly-nano-banana-pro-1k-21x9",
        "firefly-nano-banana-pro-1k-2x3",
        "firefly-nano-banana-pro-1k-3x2",
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
        "firefly-nano-banana2-1k-4x1",
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
        "firefly-nano-banana-2k-2x3",
        "firefly-nano-banana-2k-3x2",
        "firefly-nano-banana-2k-3x4",
        "firefly-nano-banana-2k-4x3",
        "firefly-nano-banana-2k-4x5",
        "firefly-nano-banana-2k-5x4",
        "firefly-nano-banana-2k-9x16",
        "firefly-nano-banana-pro-2k-16x9",
        "firefly-nano-banana-pro-2k-1x1",
        "firefly-nano-banana-pro-2k-21x9",
        "firefly-nano-banana-pro-2k-2x3",
        "firefly-nano-banana-pro-2k-3x2",
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
        "firefly-nano-banana2-2k-4x1",
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
        "firefly-nano-banana-4k-2x3",
        "firefly-nano-banana-4k-3x2",
        "firefly-nano-banana-4k-3x4",
        "firefly-nano-banana-4k-4x3",
        "firefly-nano-banana-4k-4x5",
        "firefly-nano-banana-4k-5x4",
        "firefly-nano-banana-4k-9x16",
        "firefly-nano-banana-pro-4k-16x9",
        "firefly-nano-banana-pro-4k-1x1",
        "firefly-nano-banana-pro-4k-21x9",
        "firefly-nano-banana-pro-4k-2x3",
        "firefly-nano-banana-pro-4k-3x2",
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
        "firefly-nano-banana2-4k-4x1",
        "firefly-nano-banana2-4k-4x3",
        "firefly-nano-banana2-4k-4x5",
        "firefly-nano-banana2-4k-5x4",
        "firefly-nano-banana2-4k-8x1",
        "firefly-nano-banana2-4k-9x16",
    ],
    "GPT2": [
        "firefly-gpt-image-1k-16x9",
        "firefly-gpt-image-1k-1x1",
        "firefly-gpt-image-1k-21x9",
        "firefly-gpt-image-1k-2x3",
        "firefly-gpt-image-1k-3x2",
        "firefly-gpt-image-1k-3x4",
        "firefly-gpt-image-1k-4x3",
        "firefly-gpt-image-1k-4x5",
        "firefly-gpt-image-1k-5x4",
        "firefly-gpt-image-1k-9x16",
        "firefly-gpt-image-2k-16x9",
        "firefly-gpt-image-2k-1x1",
        "firefly-gpt-image-2k-21x9",
        "firefly-gpt-image-2k-2x3",
        "firefly-gpt-image-2k-3x2",
        "firefly-gpt-image-2k-3x4",
        "firefly-gpt-image-2k-4x3",
        "firefly-gpt-image-2k-4x5",
        "firefly-gpt-image-2k-5x4",
        "firefly-gpt-image-2k-9x16",
        "firefly-gpt-image-4k-16x9",
        "firefly-gpt-image-4k-1x1",
        "firefly-gpt-image-4k-21x9",
        "firefly-gpt-image-4k-2x3",
        "firefly-gpt-image-4k-3x2",
        "firefly-gpt-image-4k-3x4",
        "firefly-gpt-image-4k-4x3",
        "firefly-gpt-image-4k-4x5",
        "firefly-gpt-image-4k-5x4",
        "firefly-gpt-image-4k-9x16",
    ],
    "Gemini": _make_gemini_model_options(),
    "Video": _make_video_model_options(),
}

ALL_MODELS = frozenset(m for models in MODELS.values() for m in models)

job_executor = ThreadPoolExecutor(max_workers=GENERATE_WORKERS)
job_lock = threading.Lock()
job_store = {}


def _prune_jobs_unlocked(now_ts: float):
    expired = [
        job_id
        for job_id, info in job_store.items()
        if now_ts - info.get("created_at", now_ts) > JOB_TTL_SECONDS
    ]
    for job_id in expired:
        job_store.pop(job_id, None)
    if len(job_store) <= MAX_JOB_STORE:
        return
    ordered = sorted(
        job_store.items(),
        key=lambda kv: kv[1].get("created_at", 0),
    )
    for job_id, _ in ordered[: max(0, len(job_store) - MAX_JOB_STORE)]:
        job_store.pop(job_id, None)


def _active_job_count_unlocked():
    return sum(1 for info in job_store.values() if info.get("status") in ("queued", "running"))


def _process_generate_request(data):
    api_key = data.get('apiKey')
    model = data.get('model')
    prompt = data.get('prompt')
    image_data = data.get('image')
    images_data = data.get('images')

    if _estimate_image_payload_chars(data) > MAX_IMAGE_PAYLOAD_CHARS:
        return None, _error_payload(
            "参考图数据过大，当前请求体超过服务端限制。",
            "IMAGE_PAYLOAD_TOO_LARGE",
            status_code=413,
            hint="请压缩图片、降低分辨率，或减少参考图数量后再试。",
            stage="request",
        ), 413

    has_image = bool(image_data or images_data)
    logger.info(f"请求参数: model={model}, prompt长度={len(prompt) if prompt else 0}, 有图片={has_image}")

    if not api_key or not model or not prompt:
        logger.error(f"缺少必要参数: api_key={bool(api_key)}, model={model}, prompt={bool(prompt)}")
        return None, _error_payload(
            "缺少必要参数。",
            "MISSING_REQUIRED_FIELDS",
            status_code=400,
            hint="请确认已填写 API Key、选择模型，并输入提示词。",
            stage="request",
        ), 400

    if model not in ALL_MODELS:
        logger.error(f"无效的模型: {model}")
        return None, _error_payload(
            f"无效的模型：{model}",
            "INVALID_MODEL",
            status_code=400,
            hint="请重新选择左侧分组和右侧模型；如果模型来自新文档，需要先更新后端模型列表。",
            stage="request",
        ), 400

    try:
        is_gemini_image_model = _is_gemini_image_model(model)
        gemini_prompt = _gemini_prompt_with_constraints(prompt, model) if is_gemini_image_model else prompt

        if image_data or images_data:
            content = [] if is_gemini_image_model else [{"type": "text", "text": prompt}]
            if images_data:
                for img in images_data:
                    if is_gemini_image_model and img.startswith("data:"):
                        image_b64 = img
                    elif ',' in img:
                        image_b64 = img.split(',')[1]
                    else:
                        image_b64 = img
                    image_url = image_b64 if image_b64.startswith("data:") else f"data:image/jpeg;base64,{image_b64}"
                    content.append({"type": "image_url", "image_url": {"url": image_url}})
            elif image_data:
                if is_gemini_image_model and image_data.startswith("data:"):
                    image_b64 = image_data
                elif ',' in image_data:
                    image_b64 = image_data.split(',')[1]
                else:
                    image_b64 = image_data
                image_url = image_b64 if image_b64.startswith("data:") else f"data:image/jpeg;base64,{image_b64}"
                content.append({"type": "image_url", "image_url": {"url": image_url}})
            if is_gemini_image_model:
                content.append({"type": "text", "text": gemini_prompt})
            messages = [{"role": "user", "content": content}]
        else:
            if is_gemini_image_model:
                messages = [{"role": "user", "content": [{"type": "text", "text": gemini_prompt}]}]
            else:
                messages = [{"role": "user", "content": prompt}]

        payload = {
            "model": _gemini_upstream_model(model) if is_gemini_image_model else model,
            "messages": messages,
        }
        if is_gemini_image_model:
            payload["generationConfig"] = _gemini_generation_config(model)
            logger.info(
                "Gemini生成配置: upstream_model=%s, imageSize=%s, aspectRatio=default",
                payload["model"],
                payload["generationConfig"]["imageConfig"]["imageSize"],
            )
        content = None
        response = None
        logger.info(f"正在调用API: {BASE_URL}/v1/chat/completions, 模型: {model}")
        try:
            if USE_UPSTREAM_STREAM and not is_gemini_image_model:
                response = http_session.post(
                    f"{BASE_URL}/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={**payload, "stream": True},
                    stream=True,
                    timeout=(15, UPSTREAM_TIMEOUT_SECONDS),
                )
                logger.info(f"API流式响应状态码: {response.status_code}")
                if response.status_code == 200:
                    content, stream_err = _read_streaming_chat_content(response)
                    if stream_err:
                        logger.error(f"流式响应解析失败: {stream_err}")
                        return None, _error_payload(
                            "上游流式响应解析失败。",
                            "UPSTREAM_STREAM_PARSE_FAILED",
                            status_code=502,
                            hint="上游返回了无法解析的流式内容。请稍后重试；若持续出现，请管理员检查上游兼容格式。",
                            stage="upstream",
                            retryable=True,
                            upstream_message=stream_err,
                        ), 502
                else:
                    error_detail = response.text[:4000]
                    logger.error(
                        "API流式返回错误状态码: %s, 响应: %s",
                        response.status_code,
                        error_detail[:500],
                    )
                    if _should_retry_without_stream(response.status_code, error_detail):
                        logger.warning("上游不支持流式参数，回退为普通请求")
                        content = None
                    else:
                        payload_err = _upstream_error_payload(response.status_code, error_detail, stage="upstream_stream")
                        return None, payload_err, response.status_code

            if content is None:
                response = http_session.post(
                    f"{BASE_URL}/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json=payload,
                    timeout=(15, UPSTREAM_TIMEOUT_SECONDS),
                )
                logger.info(f"API响应状态码: {response.status_code}")
        except requests.exceptions.Timeout:
            logger.error("API请求超时")
            return None, _error_payload(
                "连接上游生成服务超时。",
                "UPSTREAM_REQUEST_TIMEOUT",
                status_code=504,
                hint="生成可能仍在上游后台运行。请稍后重试；视频生成可尝试缩短时长或降低分辨率。",
                stage="upstream",
                retryable=True,
            ), 504
        except requests.exceptions.ConnectionError as e:
            logger.error(f"无法连接到API服务器: {e}")
            return None, _error_payload(
                "无法连接到上游 API 服务器。",
                "UPSTREAM_CONNECTION_FAILED",
                status_code=502,
                hint="请检查 API_BASE_URL 是否正确、网络是否可访问，以及上游服务是否在线。",
                stage="network",
                retryable=True,
                upstream_message=str(e),
            ), 502
        except Exception as e:
            logger.error(f"连接异常: {e}")
            return None, _error_payload(
                "调用上游时发生连接异常。",
                "UPSTREAM_CONNECTION_EXCEPTION",
                status_code=502,
                hint="请稍后重试；若持续出现，请管理员查看服务端日志。",
                stage="network",
                retryable=True,
                upstream_message=str(e),
            ), 502

        if content is None and response.status_code != 200:
            error_detail = response.text[:4000]
            logger.error(
                "API返回错误状态码: %s, 响应: %s",
                response.status_code,
                error_detail[:500],
            )
            payload_err = _upstream_error_payload(response.status_code, error_detail)
            return None, payload_err, response.status_code

        if content is None:
            try:
                result = response.json()
            except Exception as e:
                logger.error(f"JSON解析失败: {e}, 响应文本: {response.text[:500]}")
                return None, _error_payload(
                    "上游响应不是有效 JSON，无法解析生成结果。",
                    "UPSTREAM_INVALID_JSON",
                    status_code=502,
                    hint="上游可能返回了 HTML 错误页、网关报错或非兼容响应。请管理员查看上游原始响应。",
                    stage="parse",
                    retryable=True,
                    upstream_message=response.text[:800],
                    debug=str(e),
                ), 502

            inline_images = _extract_inline_image_data(result)
            if inline_images:
                logger.info(f"成功提取 Gemini inline 图片数量: {len(inline_images)}")
                return {
                    'image': inline_images[0],
                    'allImages': inline_images,
                    'content': '[Gemini inline image]',
                }, None, 200

            content, parse_err = _chat_content_from_result(result)
            if parse_err:
                return None, _error_payload(
                    "上游响应格式不符合预期，无法读取生成内容。",
                    "UPSTREAM_UNEXPECTED_FORMAT",
                    status_code=502,
                    hint="上游没有返回 choices[0].message.content 或 Gemini inline 图片。请检查模型是否仍兼容 chat/completions。",
                    stage="parse",
                    retryable=True,
                    upstream_message=parse_err,
                    debug=str(result)[:1000],
                ), 502

        if _is_video_model(model):
            video_urls = _extract_video_urls(content)
            if video_urls:
                logger.info(f"成功提取视频数量: {len(video_urls)}")
                video_urls = _rewrite_generated_image_urls(video_urls)
                return {
                    'video': video_urls[0],
                    'media': video_urls[0],
                    'mediaType': 'video',
                    'allVideos': video_urls,
                    'content': content,
                }, None, 200

        image_urls = _extract_image_urls(content)
        if image_urls:
            logger.info(f"成功提取图片数量: {len(image_urls)}")
            image_urls = _rewrite_generated_image_urls(image_urls)
            return {
                'image': image_urls[0],
                'media': image_urls[0],
                'mediaType': 'image',
                'allImages': image_urls,
                'content': content,
            }, None, 200

        logger.warning(f"未找到媒体，内容前500字符: {content[:500]}")
        return None, _error_payload(
            "生成完成，但没有在上游响应中找到可显示的图片或视频链接。",
            "MEDIA_NOT_FOUND",
            status_code=502,
            hint="可能是上游返回了纯文本、媒体链接格式变化，或生成被内容策略拦截。请换提示词重试；若持续出现，请管理员查看上游原始内容。",
            stage="parse",
            retryable=True,
            upstream_message=content[:800],
            debug=content[:1000],
        ), 502
    except Exception as e:
        logger.exception("生成图片时发生错误")
        return None, _error_payload(
            "服务器处理生成请求时发生内部错误。",
            "SERVER_INTERNAL_ERROR",
            status_code=500,
            hint="请稍后重试；若重复出现，请管理员查看后端日志。",
            stage="server",
            retryable=False,
            debug=str(e),
        ), 500


def _run_generate_job(job_id: str, data: dict):
    with job_lock:
        if job_id not in job_store:
            return
        job_store[job_id]["status"] = "running"
        job_store[job_id]["started_at"] = time.time()
    result, error_payload, status_code = _process_generate_request(data)
    with job_lock:
        if job_id not in job_store:
            return
        job_store[job_id]["finished_at"] = time.time()
        if error_payload:
            job_store[job_id]["status"] = "failed"
            job_store[job_id]["error"] = error_payload.get("error", "生成失败")
            job_store[job_id]["status_code"] = status_code
            for key in ("code", "hint", "stage", "retryable", "upstreamStatus", "upstreamMessage"):
                if key in error_payload:
                    job_store[job_id][key] = error_payload[key]
            if app.debug and "debug" in error_payload:
                job_store[job_id]["debug"] = error_payload["debug"]
        else:
            job_store[job_id]["status"] = "succeeded"
            job_store[job_id]["result"] = result
            job_store[job_id]["status_code"] = 200


@app.route('/favicon.ico')
def favicon():
    return '', 204  # 返回空响应


@app.route('/image.png')
def image_png():
    return send_from_directory(BASE_DIR, 'image.png')

@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/api/models')
def get_models():
    return jsonify(MODELS)


@app.route('/api/generate', methods=['POST'])
def generate():
    logger.info("收到生成请求")
    if not request.is_json:
        return jsonify(_error_payload(
            "请求格式错误：Content-Type 必须为 application/json。",
            "INVALID_CONTENT_TYPE",
            status_code=400,
            hint="请刷新页面后重试；如果你在直接调用接口，请使用 JSON 请求体。",
            stage="request",
        )), 400
    data = request.json
    if data is None:
        return jsonify(_error_payload(
            "请求体必须为 JSON。",
            "INVALID_JSON_BODY",
            status_code=400,
            hint="请刷新页面后重试；如果你在直接调用接口，请检查 JSON 格式。",
            stage="request",
        )), 400

    # 轻量字段校验，避免无效请求占用队列槽位
    if not data.get("apiKey") or not data.get("model") or not data.get("prompt"):
        return jsonify(_error_payload(
            "缺少必要参数。",
            "MISSING_REQUIRED_FIELDS",
            status_code=400,
            hint="请确认已填写 API Key、选择模型，并输入提示词。",
            stage="request",
        )), 400
    if data.get("model") not in ALL_MODELS:
        return jsonify(_error_payload(
            f"无效的模型：{data.get('model')}",
            "INVALID_MODEL",
            status_code=400,
            hint="请重新选择模型；如果刚更新过 API 文档，需要同步后端模型列表。",
            stage="request",
        )), 400
    if _estimate_image_payload_chars(data) > MAX_IMAGE_PAYLOAD_CHARS:
        return jsonify(_error_payload(
            "参考图数据过大，当前请求体超过服务端限制。",
            "IMAGE_PAYLOAD_TOO_LARGE",
            status_code=413,
            hint="请压缩图片、降低分辨率，或减少参考图数量后再试。",
            stage="request",
        )), 413

    now_ts = time.time()
    with job_lock:
        _prune_jobs_unlocked(now_ts)
        if _active_job_count_unlocked() >= MAX_PENDING_JOBS:
            return jsonify(_error_payload(
                "服务当前排队任务过多。",
                "LOCAL_QUEUE_FULL",
                status_code=429,
                hint="请稍后再提交，或减少批量任务并发数量。",
                stage="queue",
                retryable=True,
            )), 429
        job_id = uuid.uuid4().hex
        job_store[job_id] = {
            "id": job_id,
            "status": "queued",
            "created_at": now_ts,
            "status_code": 202,
        }
    job_executor.submit(_run_generate_job, job_id, data)
    return jsonify({"jobId": job_id, "status": "queued"}), 202


@app.route('/api/jobs/<job_id>', methods=['GET'])
def get_job_status(job_id):
    with job_lock:
        info = job_store.get(job_id)
        if not info:
            return jsonify({'error': '任务不存在或已过期'}), 404
        status = info.get("status")
        resp = {"jobId": job_id, "status": status}
        if status == "succeeded":
            resp["result"] = info.get("result")
        elif status == "failed":
            resp["error"] = info.get("error", "生成失败")
            resp["statusCode"] = info.get("status_code", 500)
            for key in ("code", "hint", "stage", "retryable", "upstreamStatus", "upstreamMessage"):
                if key in info:
                    resp[key] = info[key]
            if app.debug and "debug" in info:
                resp["debug"] = info["debug"]
        return jsonify(resp), 200


@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return jsonify(_error_payload(
            e.description or e.name,
            "HTTP_EXCEPTION",
            status_code=e.code or 500,
            hint="请检查请求路径和参数后重试。",
            stage="server",
        )), e.code
    logger.exception("未处理的异常")
    return jsonify(_error_payload(
        "服务器内部错误。",
        "SERVER_UNHANDLED_EXCEPTION",
        status_code=500,
        hint="请稍后重试；若重复出现，请管理员查看后端日志。",
        stage="server",
        debug=str(e),
    )), 500


@app.route('/api/download')
def download_image():
    url = request.args.get('url')
    
    if not url:
        return jsonify(_error_payload(
            "缺少下载 URL。",
            "DOWNLOAD_MISSING_URL",
            status_code=400,
            hint="请重新点击下载按钮；如果仍然出现，说明生成结果没有返回有效媒体地址。",
            stage="download",
        )), 400

    ok, err = _validate_download_url(url)
    if not ok:
        return jsonify(_error_payload(
            f"下载地址不被允许：{err}",
            "DOWNLOAD_URL_REJECTED",
            status_code=400,
            hint="为防止 SSRF，下载代理只允许白名单域名。可让管理员把可信媒体域名加入 DOWNLOAD_ALLOWED_HOSTS。",
            stage="download",
        )), 400
    
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
                return jsonify(_error_payload(
                    "媒体文件过大，超过下载代理限制。",
                    "DOWNLOAD_FILE_TOO_LARGE",
                    status_code=413,
                    hint="请直接打开媒体链接保存，或让管理员调大 MAX_DOWNLOAD_BYTES。",
                    stage="download",
                )), 413
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
        return jsonify(_error_payload(
            "下载代理无法获取媒体文件。",
            "DOWNLOAD_FETCH_FAILED",
            status_code=502,
            hint="媒体链接可能已过期、上游不可访问，或域名网络异常。请先尝试“打开视频/查看大图”。",
            stage="download",
            retryable=True,
            upstream_message=str(e),
        )), 502


@app.route('/health')
def health():
    return {'status': 'ok'}


if __name__ == '__main__':
    # 生产环境使用 waitress；默认监听 80（Linux 绑定 1024 以下端口通常需 root 或 setcap）
    from waitress import serve
    logger.info("监听 0.0.0.0:%s，Waitress threads=%s", LISTEN_PORT, WAITRESS_THREADS)
    serve(app, host='0.0.0.0', port=LISTEN_PORT, threads=WAITRESS_THREADS)
