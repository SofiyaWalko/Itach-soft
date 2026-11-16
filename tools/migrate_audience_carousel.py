# -*- coding: utf-8 -*-
"""Переводит блок «Кому подходит» со старого селектора на карусель.

Берёт контент из существующей разметки каждой страницы (надзаголовок — это
подпись таба, заголовок и текст — из панели) и собирает новый блок той же
функцией, что используют генераторы подстраниц. Так тексты страниц остаются
своими, а вид блока — общим.

Запуск: python tools/migrate_audience_carousel.py
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))

import audience_carousel  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
COMMENT = audience_carousel.COMMENT


def parse_section(section):
    tabs = re.findall(r'<span class="audience-tab__text">(.*?)</span>', section, re.S)
    panels = re.findall(r'<div class="audience-panel[^"]*"[^>]*>(.*?)</div>', section, re.S)
    if not tabs or len(tabs) != len(panels):
        raise ValueError(f"табы: {len(tabs)}, панели: {len(panels)}")
    segments = []
    for tab, panel in zip(tabs, panels):
        title = re.search(r'<h3 class="audience-panel__title">(.*?)</h3>', panel, re.S)
        text = re.search(r'<p class="audience-panel__text">(.*?)</p>', panel, re.S)
        if not title or not text:
            raise ValueError("в панели нет заголовка или текста")
        segments.append((tab, title.group(1), text.group(1)))
    return segments


def replace_block(html, name):
    start = html.index('<section class="audience"')
    end = html.index("</section>", start) + len("</section>")
    segments = parse_section(html[start:end])

    # Старый комментарий над секцией описывает селектор — заменяем его вместе с блоком
    begin = start
    comment_at = html.rfind("<!--", 0, start)
    if comment_at != -1:
        comment_end = html.find("-->", comment_at)
        if comment_end != -1 and html[comment_end + 3:start].strip() == "":
            if "Кому подходит" in html[comment_at:comment_end]:
                begin = comment_at

    # Начало строки, чтобы не задвоить отступ перед комментарием и секцией
    line_begin = html.rfind("\n", 0, begin) + 1
    new_block = COMMENT + "\n" + audience_carousel.build_section(segments)
    return html[:line_begin] + new_block + html[end:], len(segments)


def main():
    files = sorted(
        p for p in ROOT.glob("*.html") if 'class="audience-picker"' in p.read_text(encoding="utf-8")
    )
    for path in files:
        html = path.read_text(encoding="utf-8")
        updated, count = replace_block(html, path.name)
        path.write_text(updated, encoding="utf-8")
        print(f"{path.name}: {count} слайдов")
    print(f"страниц: {len(files)}")


if __name__ == "__main__":
    main()
