# -*- coding: utf-8 -*-
"""Расставляет изображения по слайдам блока «Кому подходит».

Пять изображений чередуются по шести слайдам и повторяются по кругу.
Скрипт нужен для уже собранных страниц; новые собирает tools/audience_carousel.py.

Запуск: python tools/update_audience_images.py
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from audience_carousel import IMAGES  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def replace_images(section):
    index = 0

    def repl(match):
        nonlocal index
        src = IMAGES[index % len(IMAGES)]
        index += 1
        return match.group(1) + src + match.group(2)

    return re.sub(r'(<img src=")assets/img/audience/[^"]*(")', repl, section), index


def main():
    files = sorted(p for p in ROOT.glob("*.html") if "data-audience-carousel" in p.read_text(encoding="utf-8"))
    for path in files:
        html = path.read_text(encoding="utf-8")
        start = html.index('<section class="audience"')
        end = html.index("</section>", start) + len("</section>")
        section, count = replace_images(html[start:end])
        path.write_text(html[:start] + section + html[end:], encoding="utf-8")
        print(f"{path.name}: {count} изображений")
    print(f"страниц: {len(files)}")


if __name__ == "__main__":
    main()
