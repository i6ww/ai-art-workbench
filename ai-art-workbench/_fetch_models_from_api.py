"""Fetch model IDs from upstream /v1/models and refresh app.py MODELS.

Key (pick one, never commit):
  - Environment: MODEL_FETCH_KEY
  - File (gitignored): .model_fetch_key   first line = sk-...

Usage:
  python _fetch_models_from_api.py --patch-app

API URL default matches app.py BASE_URL:
  MODEL_FETCH_URL=https://371181668.xyz/v1/models
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent

def _load_key() -> str | None:
    k = os.environ.get("MODEL_FETCH_KEY")
    if k and k.strip():
        return k.strip()
    p = ROOT / ".model_fetch_key"
    if p.is_file():
        line = p.read_text(encoding="utf-8").strip().splitlines()[0].strip()
        return line or None
    return None


def fetch_ids(url: str, key: str) -> list[str]:
    r = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {key}",
            "User-Agent": "Mozilla/5.0 (compatible; AIWorkbench/1.0)",
            "Accept": "application/json",
        },
        timeout=120,
    )
    r.raise_for_status()
    data = r.json()
    return sorted({o["id"] for o in data.get("data", []) if o.get("id")})


def partition(ids: list[str]) -> tuple[list[str], list[str], list[str], list[str]]:
    def is_nano_img(m: str) -> bool:
        return (
            m.startswith("firefly-nano-banana-")
            or m.startswith("firefly-nano-banana-pro-")
            or m.startswith("firefly-nano-banana2-")
        )

    nano = [m for m in ids if is_nano_img(m)]
    k1 = sorted([m for m in nano if "-1k-" in m])
    k2 = sorted([m for m in nano if "-2k-" in m])
    k4 = sorted([m for m in nano if "-4k-" in m])

    def is_gpt_tab(m: str) -> bool:
        if m.startswith("firefly-gpt-image"):
            return True
        if m == "gpt-image-2":
            return True
        return False

    gpt2 = sorted([m for m in ids if is_gpt_tab(m)])
    return k1, k2, k4, gpt2


def format_models_py(k1: list[str], k2: list[str], k4: list[str], gpt2: list[str]) -> str:
    lines: list[str] = []
    lines.append("# 模型列表（与上游 GET /v1/models 对齐；可用 _fetch_models_from_api.py --patch-app 刷新）")
    lines.append("MODELS = {")

    def emit(label: str, arr: list[str]) -> None:
        lines.append(f'    "{label}": [')
        for x in arr:
            lines.append(f'        "{x}",')
        lines.append("    ],")

    emit("1K", k1)
    emit("2K", k2)
    emit("4K", k4)
    emit("GPT2", gpt2)
    lines.append("}")
    return "\n".join(lines) + "\n"


def patch_app(block: str) -> None:
    app_py = ROOT / "app.py"
    text = app_py.read_text(encoding="utf-8")
    if text.startswith("\ufeff"):
        text = text.lstrip("\ufeff")
    start = text.index("# 模型列表")
    end = text.index("ALL_MODELS = frozenset")
    app_py.write_text(text[:start] + block + "\n" + text[end:], encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--patch-app",
        action="store_true",
        help="Write MODELS into app.py (same folder)",
    )
    args = parser.parse_args()

    url = os.environ.get("MODEL_FETCH_URL", "https://371181668.xyz/v1/models").strip()
    key = _load_key()
    if not key:
        print(
            "缺少 API Key：设置环境变量 MODEL_FETCH_KEY，或在项目根创建 .model_fetch_key（首行 sk-...）。",
            file=sys.stderr,
        )
        sys.exit(1)

    ids = fetch_ids(url, key)
    k1, k2, k4, gpt2 = partition(ids)
    block = format_models_py(k1, k2, k4, gpt2)

    total = len(k1) + len(k2) + len(k4) + len(gpt2)
    print(
        f"# fetched total ids={len(ids)} MODELS entries={total} "
        f"(1K={len(k1)} 2K={len(k2)} 4K={len(k4)} GPT2={len(gpt2)})",
        file=sys.stderr,
    )

    if args.patch_app:
        patch_app(block)
        print("patched app.py", file=sys.stderr)
    else:
        sys.stdout.write(block)


if __name__ == "__main__":
    main()
