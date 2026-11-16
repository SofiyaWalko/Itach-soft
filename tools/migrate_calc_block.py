# -*- coding: utf-8 -*-
"""Переводит встроенный калькулятор на новый вид: заголовок сверху,
слева выбор параметров, справа ориентировочная стоимость.

Старая разметка мастера (шаги, трекер, форма) заменяется пустым контейнером
[data-calc-config] — интерфейс и расчёт собирает assets/js/calculator.js.

Запуск: python tools/migrate_calc_block.py
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent


def default_service(name):
    """Услуга, выбранная в калькуляторе по умолчанию — по теме страницы."""
    if name.startswith("service-ai"):
        return "ai"
    if name.startswith("service-outstaff"):
        return "outstaff"
    if name.startswith("service-asterisk"):
        return "asterisk"
    if name.startswith("service-bitrix24"):
        return "bitrix24"
    if name == "index.html":
        return "bitrix24"
    return "sites"


def default_need(name):
    """Задача по умолчанию: на страницах поддержки — обслуживание, а не запуск."""
    if name == "service-asterisk-podderzhka.html":
        return 3
    if name == "service-bitrix24-podderzhka.html":
        return 2
    if name in ("service-podderzhka-saytov.html", "service-web-services-podderzhka.html", "service-support.html"):
        return 4
    return 0


def build_section(indent, service, need):
    pad = " " * indent
    return "\n".join(
        [
            f'{pad}<section class="calc" id="calculator" aria-labelledby="calc-title">',
            f'{pad}  <div class="container calc__layout" data-calc>',
            f'{pad}    <div class="calc__intro" data-reveal>',
            f'{pad}      <h2 class="section-title calc__title" id="calc-title">Рассчитайте стоимость работ <span class="section-title__muted">за 2 минуты</span></h2>',
            f'{pad}      <p class="calc__lead">Выберите услугу и параметры — ориентировочная стоимость обновится сразу. Точную смету пришлём после короткого разговора.</p>',
            f'{pad}    </div>',
            f'{pad}    <div class="calc__config" data-calc-config data-calc-default="{service}" data-calc-default-need="{need}" data-reveal></div>',
            f'{pad}  </div>',
            f'{pad}</section>',
        ]
    )


def replace_section(html, name):
    start = html.index('<section class="calc"')
    end = html.index("</section>", start) + len("</section>")
    line_start = html.rfind("\n", 0, start) + 1
    indent = start - line_start
    return html[:line_start] + build_section(indent, default_service(name), default_need(name)) + html[end:]


def main():
    files = sorted(p for p in ROOT.glob("*.html") if '<section class="calc"' in p.read_text(encoding="utf-8"))
    for path in files:
        html = path.read_text(encoding="utf-8")
        assert html.count('<section class="calc"') == 1, f"{path.name}: секций больше одной"
        path.write_text(replace_section(html, path.name), encoding="utf-8")
        print(f"{path.name}: {default_service(path.name)}")
    print(f"страниц: {len(files)}")


if __name__ == "__main__":
    main()
