# -*- coding: utf-8 -*-
"""Генерация иллюстраций ролей «Интегратор Битрикс24» и «Системный инженер»
в стиле существующих силуэтов assets/img/team/ (тёмный силуэт + белый контур,
прозрачный фон). OpenAI chatgpt-image-latest, затем обрезка по alpha и ресайз до высоты 600."""
import base64
import io
import os
import sys
import urllib.request

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = os.path.join("assets", "img", "team")
HEIGHT = 600

STYLE = (
    "Flat minimalist vector illustration, faceless person silhouette filled with a single "
    "dark slate gray color, thin white outline strokes showing curly hair, clothing folds "
    "and hands. Monochrome two-tone style: dark silhouette plus white line details only. "
    "Fully transparent background, portrait orientation, no text, no letters, no logos."
)

JOBS = {
    "role-bitrix24-integrator": (
        "The person wears a telephone headset with microphone and holds a large tablet "
        "displaying a simple CRM dashboard: kanban columns with cards, a small chart and "
        "a gear icon. Confident posture, looking at the tablet. " + STYLE
    ),
    "role-system-engineer": (
        "The person wears a telephone headset with microphone and stands next to a tall "
        "server rack tower with rows of small indicator lights and slots, one hand resting "
        "on the server, holding a wrench in the other hand. " + STYLE
    ),
}


def generate(name: str, prompt: str) -> None:
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=(
            '{"model": "chatgpt-image-latest", "size": "1024x1536", '
            '"background": "transparent", '
            f'"prompt": {__import__("json").dumps(prompt)}}}'
        ).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
        },
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        payload = __import__("json").load(resp)
    raw = base64.b64decode(payload["data"][0]["b64_json"])
    img = Image.open(io.BytesIO(raw)).convert("RGBA")

    # Обрезаем прозрачные поля с небольшим запасом, затем ресайз до общей высоты ряда
    bbox = img.getchannel("A").getbbox()
    if bbox:
        pad = 12
        bbox = (
            max(0, bbox[0] - pad),
            max(0, bbox[1] - pad),
            min(img.width, bbox[2] + pad),
            min(img.height, bbox[3] + pad),
        )
        img = img.crop(bbox)
    ratio = HEIGHT / img.height
    img = img.resize((round(img.width * ratio), HEIGHT), Image.LANCZOS)

    out = os.path.join(OUT_DIR, f"{name}.webp")
    img.save(out, "WEBP", quality=90)
    print(f"{out}: {img.width}x{img.height}")


for name, prompt in JOBS.items():
    generate(name, prompt)
