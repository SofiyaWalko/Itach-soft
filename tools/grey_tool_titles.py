# -*- coding: utf-8 -*-
"""Заголовки карточек инструментов: описательная часть — серым, как в кейсах.

В данных заголовки хранятся как ("Название", "Описание"). Скрипт заворачивает
хвост названия в <span class="section-title__muted">…</span>: первое слово
остаётся тёмным, остальное — серое. Особые случаи — в SPECIAL.
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(__file__).resolve().parent / "bitrix24_content.py"
s = p.read_text(encoding="utf-8")

# заголовок → (тёмная часть, серая часть)
SPECIAL = {
    "В экосистеме Битрикс24": ("В экосистеме", "Битрикс24"),
    "Быстрая и удобная лидогенерация": ("Быстрая и удобная", "лидогенерация"),
}

MUTED = '<span class="section-title__muted">{}</span>'

def grey_name(name):
    if name in SPECIAL:
        dark, grey = SPECIAL[name]
    else:
        parts = name.split(" ", 1)
        if len(parts) == 1:
            return name
        dark, grey = parts
    return f"{dark} {MUTED.format(grey)}"


def process_block(segment):
    # пары ("Заголовок", "длинное описание") — только карточки инструментов
    def repl(m):
        name, desc = m.group(1), m.group(2)
        if len(desc) < 60 or 'section-title__muted' in name:
            return m.group(0)
        return f'("{grey_name(name)}", "{desc}")'

    return re.sub(r'\("([^"]{3,70})", "([^"]*)"\)', repl, segment)


starts = ["        # ---- Ключевые инструменты внедрения", "        # ---- Типы интеграций"]
anchors = ['        "faq_muted": "о внедрении Битрикс24",', '        "faq_muted": "об интеграции Битрикс24",']

for start_marker, anchor in zip(starts, anchors):
    a = s.index(start_marker)
    b = s.index(anchor, a)
    s = s[:a] + process_block(s[a:b]) + s[b:]

p.write_text(s, encoding="utf-8")
print("titles greyed:", s.count('section-title__muted"'))
