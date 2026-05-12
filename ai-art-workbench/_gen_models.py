"""Regenerate MODELS dict in app.py from available_models.txt (same folder or parent)."""
import re
from pathlib import Path

_here = Path(__file__).resolve().parent
_paths = [_here / "available_models.txt", _here.parent / "available_models.txt"]
text = None
for p in _paths:
    if p.is_file():
        text = p.read_text(encoding="utf-8")
        break
if text is None:
    raise FileNotFoundError("available_models.txt not found beside _gen_models.py or one level up")

img_section = re.search(r"## Image.*?^(?=## Video)", text, re.S | re.M)
block = img_section.group(0)
ids = []
for line in block.splitlines():
    line = line.strip()
    if line.startswith("firefly-nano"):
        ids.append(line)

k1, k2, k4 = [], [], []
for m in ids:
    if "-1k-" in m:
        k1.append(m)
    elif "-2k-" in m:
        k2.append(m)
    elif "-4k-" in m:
        k4.append(m)

api = text.split("API returned models:", 1)[-1]
gpt = []
gemini_targets = (
    "gemini-3-pro-image-preview",
    "gemini-3.1-flash-image-preview",
    "gemini-3.0-pro-image-2k",
    "gemini-3.0-pro-image-4k",
)
gemini_sizes = {
    "gemini-3-pro-image-preview": ("1K", "2K", "4K"),
    "gemini-3.1-flash-image-preview": ("1K", "2K", "4K"),
    "gemini-3.0-pro-image-2k": ("2K",),
    "gemini-3.0-pro-image-4k": ("4K",),
}
gemini = []
for line in api.splitlines():
    line = line.strip()
    if line.startswith("firefly-gpt-image"):
        gpt.append(line)
    elif line == "gpt-image-2":
        gpt.append(line)
    elif line in gemini_targets:
        gemini.append(line)
gpt = sorted(set(gpt))
available_gemini = set(gemini)
gemini = [
    f"{m}__size-{size.lower()}"
    for m in gemini_targets
    if m in available_gemini
    for size in gemini_sizes[m]
]


def pylist(arr):
    for x in arr:
        print(f'        "{x}",')


print("# Auto-generated — do not edit by hand; run _gen_models.py")
print("MODELS = {")
print('    "1K": [')
pylist(k1)
print("    ],")
print('    "2K": [')
pylist(k2)
print("    ],")
print('    "4K": [')
pylist(k4)
print("    ],")
print('    "GPT2": [')
pylist(gpt)
print("    ],")
print('    "Gemini": [')
pylist(gemini)
print("    ],")
print("}")
print("#", len(k1), len(k2), len(k4), len(gpt), len(gemini), sum([len(k1), len(k2), len(k4), len(gpt), len(gemini)]))
