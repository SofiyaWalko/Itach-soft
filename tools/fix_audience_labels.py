# -*- coding: utf-8 -*-
"""Приводит ярлыки блока «Кому подходит» к ответу на вопрос «кому?».

Раньше часть вкладок называла тему («База знаний», «Ручные процессы»), а не
аудиторию. Скрипт переписывает вкладку и заголовок панели на дательный падеж
аудитории; тексты панелей не трогаются.

Страницы подуслуг аутстаффинга правятся в их генераторе
(tools/build_outstaff_subpages.py) — здесь только статические страницы.

Запуск: python tools/fix_audience_labels.py
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
LINE = '<span class="audience-panel__line audience-panel__muted">%s</span>'


def line(title):
    """Заголовок в две строки, как в существующих панелях."""
    head, tail = title.split(" ", 1)
    return f"{head} {LINE % tail}"


# page -> список из шести пар (вкладка, заголовок панели) или None, если не меняем
DATA = {
    "service-ai.html": [
        ("Службам поддержки", "Службы поддержки"),
        ("Отделам продаж", "Отделы продаж"),
        ("Бухгалтерии и бэк-офису", "Бухгалтерия и бэк-офис"),
        ("HR и внутренним службам", "HR и внутренние службы"),
        ("Аналитикам и руководителям", "Аналитики и руководители"),
        ("Руководителям", "Руководители бизнеса"),
    ],
    "service-asterisk-bezopasnost.html": [
        ("Контакт-центрам", "Контакт-центры"),
        ("Компаниям с записью разговоров", "Компании с записью разговоров"),
        ("Компаниям с удалёнными сотрудниками", "Компании с удалёнными сотрудниками"),
        ("ИТ-службам", "ИТ-службы"),
        ("Компаниям с унаследованной АТС", "Компании с унаследованной АТС"),
        ("Финансовым организациям", "Финансовые организации"),
    ],
    "service-asterisk-nastroyka-voip.html": [
        ("Компаниям с АТС", "Компании с АТС"),
        ("Офисам с проблемной связью", "Офисы с проблемной связью"),
        ("Офисам с IP-телефонами", "Офисы с IP-телефонами"),
        None,
        ("Компаниям на Битрикс24", "Компании на Битрикс24"),
        ("ИТ-службам", "ИТ-службы"),
    ],
    "service-asterisk-podderzhka.html": [
        ("Компаниям с АТС", "Компании с работающей АТС"),
        ("ИТ-службам", "ИТ-службы"),
        ("Компаниям на Asterisk", "Компании на Asterisk"),
        ("Контакт-центрам", "Контакт-центры"),
        ("Растущим компаниям", "Растущие компании"),
        ("Отделам продаж", "Отдел продаж"),
    ],
    "service-asterisk-vnedrenie.html": [
        None, None,
        ("Компаниям на Битрикс24", "Компании на Битрикс24"),
        None, None, None,
    ],
    "service-audit-sayta.html": [
        None, None,
        ("Компаниям перед редизайном", line("Компании перед редизайном")),
        ("Компаниям перед продвижением", line("Компании перед продвижением")),
        ("Компаниям перед сменой подрядчика", line("Компании перед сменой подрядчика")),
        None,
    ],
    "service-bitrix24-avtomatizatsiya.html": [
        None,
        ("Финансовым службам", "Финансовые службы"),
        None, None, None,
        ("Службе поддержки", "Служба поддержки"),
    ],
    "service-bitrix24-dorabotka.html": [
        None, None,
        ("Финансовым службам", "Финансовые службы"),
        None, None, None,
    ],
    "service-bitrix24-obuchenie.html": [
        ("Компаниям после внедрения", "Компании после внедрения"),
        None, None, None, None, None,
    ],
    "service-bitrix24-perenos.html": [
        ("Компаниям с требованиями ИБ", "Компании с требованиями ИБ"),
        None,
        ("Компаниям с доработками", "Компании с доработками"),
        None, None, None,
    ],
    "service-bitrix24-podderzhka.html": [
        None, None, None,
        ("Компаниям после внедрения", "Компании после внедрения"),
        None, None,
    ],
    "service-bitrix24-telefoniya.html": [
        None, None, None, None, None,
        ("Компаниям в сезон пиков", "Компании в сезон пиков"),
    ],
    "service-dorabotka-saytov.html": [
        None, None, None, None,
        ("Компаниям на Битриксе", "Компании на Битриксе"),
        None,
    ],
    "service-gotovye-shablony.html": [
        None, None, None,
        ("Компаниям с ограниченным бюджетом", "Компании с ограниченным бюджетом"),
        None, None,
    ],
    "service-integratsiya-1c.html": [
        None, None,
        ("Оптовым компаниям", "Оптовые компании"),
        None, None, None,
    ],
    "service-lending.html": [
        None, None,
        ("Компаниям с сезонными кампаниями", "Компании с сезонными кампаниями"),
        None,
        ("Организаторам мероприятий", "Организаторы мероприятий"),
        None,
    ],
    "service-podderzhka-saytov.html": [
        None, None, None,
        ("Компаниям на Битриксе", "Компании на Битриксе"),
        None, None,
    ],
    "service-veb-portaly.html": [
        None, None, None, None,
        ("Логистическим компаниям", "Логистические компании"),
        None,
    ],
    "service-web-services-s-nulya.html": [
        ("Компаниям с ручными процессами", "Компании с ручными процессами"),
        ("Компаниям с клиентским кабинетом", "Компании с клиентским кабинетом"),
        ("Компаниям с внутренними системами", "Компании с внутренними системами"),
        ("B2B-компаниям", "B2B-компании"),
        ("Отраслевым компаниям", "Отраслевые компании"),
        ("Продуктовым командам", "Продуктовые команды"),
    ],
    "service-web-services-integratsiya.html": [
        ("Компаниям с CRM и 1С", "Компании с CRM и 1С"),
        ("Компаниям со складом", "Компании со складом"),
        ("Компаниям с онлайн-оплатой", "Компании с онлайн-оплатой"),
        ("Продавцам на маркетплейсах", "Продавцы на маркетплейсах"),
        ("Компаниям с партнёрским обменом", "Компании с партнёрским обменом"),
        ("Руководителям и аналитикам", "Руководители и аналитики"),
    ],
    "service-web-services-podderzhka.html": [
        ("Компаниям со своими сервисами", "Компании со своими сервисами"),
        ("Компаниям после других подрядчиков", "Компании после других подрядчиков"),
        ("Компаниям с нестабильной системой", "Компании с нестабильной системой"),
        ("Компаниям с планами развития", "Компании с планами развития"),
        ("ИТ-службам", "ИТ-службы"),
        ("Компаниям с требованиями ИБ", "Компании с требованиями ИБ"),
    ],
}

TAB_RE = re.compile(r'(<span class="audience-tab__text">)([^<]*)(</span>)')
TITLE_RE = re.compile(r'(<h3 class="audience-panel__title">)(.*?)(</h3>)', re.S)


def fix_page(name, entries):
    path = ROOT / name
    s = path.read_text(encoding="utf-8")
    start = s.index('class="audience"')
    end = s.index("\n        </section>", start)
    block = s[start:end]

    tabs = list(TAB_RE.finditer(block))
    titles = list(TITLE_RE.finditer(block))
    assert len(tabs) == 6 and len(titles) == 6, (name, len(tabs), len(titles))

    # заменяем с конца, чтобы не сбить смещения
    for i in reversed(range(6)):
        if entries[i] is None:
            continue
        new_tab, new_title = entries[i]
        t = tabs[i]
        block = block[:t.start(2)] + new_tab + block[t.end(2):]

    # заголовки ищем заново после правки вкладок
    titles = list(TITLE_RE.finditer(block))
    for i in reversed(range(6)):
        if entries[i] is None:
            continue
        new_title = entries[i][1]
        t = titles[i]
        block = block[:t.start(2)] + new_title + block[t.end(2):]

    path.write_text(s[:start] + block + s[end:], encoding="utf-8")
    changed = sum(1 for e in entries if e)
    print(f"fixed {name}: {changed} аудиторий")


def main():
    for name, entries in DATA.items():
        fix_page(name, entries)


if __name__ == "__main__":
    main()
