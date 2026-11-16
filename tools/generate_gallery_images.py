"""Генерирует квадратные фотографии для галереи «О компании» и сохраняет их в WebP."""

import base64
import io
import json
import os
import time
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "img" / "gallery"
OUT.mkdir(parents=True, exist_ok=True)

STYLE = (
    "Photorealistic editorial photograph for a corporate website gallery. "
    "Natural warm daylight, subtle orange accent tones, shallow depth of field, candid, "
    "modern European IT company, no text, no logos, no watermarks. Square composition. "
)

SCENES = {
    "office": (
        "A bright open-plan IT office: several people working at desks with laptops, "
        "ergonomic chairs, plants, large windows with soft daylight; one person in the "
        "foreground slightly out of focus."
    ),
    "whiteboard": (
        "Close-up of two colleagues' hands sketching interface wireframes and flow diagrams "
        "on a large whiteboard covered with sticky notes."
    ),
    "meeting": (
        "A project team of five having a discussion around a table in a modern meeting room, "
        "laptops and notebooks, seen from a side angle, warm daylight."
    ),
    "desk": (
        "A developer's desk close-up: two monitors showing abstract code and UI mockups, "
        "a mechanical keyboard, a small plant and a warm desk lamp."
    ),
    "lounge": (
        "A modern office lounge where colleagues chat over coffee near a green wall and soft "
        "seating, candid, warm afternoon light."
    ),
    "launch": (
        "A team celebrating a successful project launch in the office: people smiling, "
        "clapping, some raising coffee cups, candid, warm light."
    ),
}


def generate(prompt: str) -> bytes:
    payload = json.dumps(
        {
            "model": "chatgpt-image-latest",
            "prompt": prompt,
            "size": "1024x1024",
            "quality": "high",
            "n": 1,
        }
    ).encode()
    request = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=payload,
        headers={
            "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=300) as response:
        data = json.load(response)
    return base64.b64decode(data["data"][0]["b64_json"])


def save_webp(raw: bytes, name: str) -> None:
    image = Image.open(io.BytesIO(raw)).convert("RGB")
    side = min(image.size)
    left = (image.width - side) // 2
    top = (image.height - side) // 2
    image = image.crop((left, top, left + side, top + side)).resize((720, 720), Image.LANCZOS)
    image.save(OUT / f"{name}.webp", "WEBP", quality=84, method=6)


for name, scene in SCENES.items():
    target = OUT / f"{name}.webp"
    if target.exists():
        print("skip", name)
        continue
    for attempt in range(3):
        try:
            raw = generate(STYLE + scene)
            save_webp(raw, name)
            print("ok", name)
            break
        except Exception as error:  # noqa: BLE001 — сеть и лимиты API
            print("retry", name, error)
            time.sleep(5)
    else:
        raise SystemExit(f"failed {name}")
