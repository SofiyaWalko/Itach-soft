# -*- coding: utf-8 -*-
"""Генератор 8 подстраниц «Битрикс24» по образцу service-internet-magaziny.html.

Общий каркас (шапка, клиенты, калькулятор, команда, технологии, достижения,
отзывы, форма, футер, модалки) копируется из образца; уникальные блоки
(hero, заявление, проблемы, аудитории, кейсы, форматы, процесс, FAQ,
перелинковка, шаблоны кейсов) собираются из данных PAGES.

Кейсы и их детальные шаблоны извлекаются из service-bitrix24.html.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parent.parent
BASE_FILE = ROOT / "service-internet-magaziny.html"
B24_FILE = ROOT / "service-bitrix24.html"

base = BASE_FILE.read_text(encoding="utf-8")
b24 = B24_FILE.read_text(encoding="utf-8")

# ---------------------------------------------------------------- размеры картинок
import struct

def img_size(rel_path):
    """Реальные (width, height) png/jpeg/webp по заголовкам файла."""
    try:
        data = (ROOT / rel_path).read_bytes()
    except OSError:
        return None
    try:
        if data[:8] == b"\x89PNG\r\n\x1a\n":
            return struct.unpack(">II", data[16:24])
        if data[:2] == b"\xff\xd8":
            i = 2
            while i < len(data) - 9:
                if data[i] == 0xFF and data[i + 1] in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    h, w = struct.unpack(">HH", data[i + 5 : i + 9])
                    return (w, h)
                i += 2 if data[i] != 0xFF else 1
            return None
        if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            fmt = data[12:16]
            if fmt == b"VP8X":
                w = 1 + int.from_bytes(data[24:27], "little")
                h = 1 + int.from_bytes(data[27:30], "little")
                return (w, h)
            if fmt == b"VP8 ":
                w, h = struct.unpack("<HH", data[26:30])
                return (w & 0x3FFF, h & 0x3FFF)
            return None
    except Exception:
        return None
    return None


def img_attrs(rel_path):
    size = img_size(rel_path)
    if size:
        return f'width="{size[0]}" height="{size[1]}"'
    return ""


def img_figure(rel_path, alt, cls):
    """Figure с реальными width/height: раскладка-заглушка есть до загрузки картинки."""
    size = img_size(rel_path)
    dims = f'width="{size[0]}" height="{size[1]}"' if size else ""
    portrait = " detail__figure--portrait" if size and size[1] > size[0] else ""
    return (
        f'<figure class="{cls}{portrait}"><img src="{rel_path}" {dims} alt="{alt}" loading="lazy" /></figure>'
    )

# ---------------------------------------------------------------- кейсы
# Данные и картинки кейсов извлекаются скриптом extract_cases.py → cases_data.json
CASES_DATA = json.loads((ROOT / "tools" / "cases_data.json").read_text(encoding="utf-8"))


def extract_existing(html):
    """Кейсы, уже свёрстанные на новом сайте (page service-bitrix24.html):
    карточка + детальный шаблон с локальными картинками — дублируем как есть."""
    cases = {}
    section = html.split('class="cases__scroller">')[1].split("</section>")[0]
    for block in section.split('<li class="case-card glow-card">')[1:]:
        card = '<li class="case-card glow-card">' + block.split("</li>")[0] + "</li>"
        m = re.search(r'data-detail-open="([^"]+)"', card)
        if m:
            cases.setdefault(m.group(1), {})["card"] = card.strip()
    for m in re.finditer(r'    <template id="(detail-[^"]+)">.*?    </template>', html, re.DOTALL):
        key = m.group(1).replace("detail-", "")
        if key in cases:
            cases[key]["template"] = m.group(0)
    return cases


EXISTING = extract_existing(b24)

# meta: eyebrow, html-заголовок карточки, alt обложки (совпадает с CASE_MAP в extract_cases.py)
CASE_META = {
    "case-mebel": ("Кейс · Мебельная компания", 'Мебельная компания <span class="section-title__muted">Битрикс24 для 3000+ сотрудников</span>', "Внедрение Битрикс24 в мебельную компанию"),
    "case-totek": ("Кейс · Тотек", 'Тотек <span class="section-title__muted">внедрение и настройка Битрикс24</span>', "Внедрение Битрикс24 для компании Тотек"),
    "case-contact-center": ("Кейс · Белтаможсервис", 'Белтаможсервис <span class="section-title__muted">автоматизация обработки обращений на CRM Битрикс24</span>', "Автоматизация работы с обращениями клиентов РУП «Белтаможсервис» на базе Битрикс24"),
    "case-zenit": ("Кейс · УК «Зенит»", 'УК «Зенит» <span class="section-title__muted">доработка Битрикс24 и автоматизация процессов</span>', "Доработка Битрикс24 для УК «Зенит»"),
    "case-hr": ("Кейс · HR-портал", 'HR-портал <span class="section-title__muted">доработка HR-модуля и оргструктуры</span>', "Доработка HR-модуля и оргструктуры на портале Битрикс24"),
    "case-zajamnae": ("Кейс · ZAJAMNAE", 'ZAJAMNAE <span class="section-title__muted">доработки Битрикс24 для бренда</span>', "Доработки Битрикс24 для бренда ZAJAMNAE"),
    "case-miele": ("Кейс · Miele", 'Miele <span class="section-title__muted">интернет-магазин бытовой техники</span>', "Интернет-магазин бытовой техники Miele"),
    "case-selfielab": ("Кейс · SelfieLab", 'SelfieLab <span class="section-title__muted">интернет-магазин косметики</span>', "Интернет-магазин косметики SelfieLab"),
    "case-sibifood": ("Кейс · SibiFood", 'SibiFood <span class="section-title__muted">редизайн интернет-магазина продуктов</span>', "Редизайн интернет-магазина экологических продуктов SibiFood"),
    "case-alkor": ("Кейс · Алькор", 'Алькор <span class="section-title__muted">доработка Битрикс24 для бренда бриллиантов</span>', "Доработка Битрикс24 для Алькор Бриллианты России"),
    "case-maximus-int": ("Кейс · Maximus", 'Maximus <span class="section-title__muted">интеграция веб-платформы с Битрикс24</span>', "Интеграция веб-платформы Maximus с Битрикс24"),
    "case-vnedr-int": ("Кейс · Санаторий «Приозерный»", 'Санаторий «Приозерный» <span class="section-title__muted">внедрение и интеграции</span>', "Внедрение Битрикс24 и настройка интеграций для санатория «Приозерный»"),
    "case-triovist": ("Кейс · Триовист", 'Триовист <span class="section-title__muted">приложение для Битрикс24: импорт кандидатов из rabota.by</span>', "Приложение для Битрикс24 по импорту кандидатов из rabota.by для Триовист"),
    "case-cititrade": ("Кейс · Рулез", 'Рулез <span class="section-title__muted">модернизация IT-инфраструктуры: IP-телефония и Битрикс24</span>', "Модернизация IT-инфраструктуры для Рулез: IP-телефония и доработка Битрикс24"),
    "case-docbank": ("Кейс · Свой Банк", 'Свой Банк <span class="section-title__muted">автоматизация документооборота</span>', "Автоматизация документооборота в Свой Банке"),
    "case-hr-avto": ("Кейс · HR-процессы", 'HR-процессы <span class="section-title__muted">автоматизация кадровых процессов в Битрикс24</span>', "Автоматизация кадровых процессов в Битрикс24"),
    "case-telefonia": ("Кейс · Марко", 'Марко <span class="section-title__muted">внедрение и интеграция IP-телефонии с Битрикс24</span>', "Внедрение и интеграция IP-телефонии с Битрикс24 для холдинга «Марко»"),
    "case-cepterbank": ("Кейс · Цептер Банк", 'Цептер Банк <span class="section-title__muted">АТС Asterisk и модули автообзвона</span>', "Внедрение АТС и модулей автообзвона в Цептер Банке"),
    "case-e2e4": ("Кейс · E2E4", 'E2E4 <span class="section-title__muted">доработки и техническая поддержка Битрикс24</span>', "Доработки и техническая поддержка Битрикс24 для E2E4"),
    "case-rozyb24": ("Кейс · Розы.Бел", 'Розы.Бел <span class="section-title__muted">внедрение Битрикс24 в сеть магазинов</span>', "Внедрение Битрикс24 в сеть цветочных магазинов Розы.Бел"),
    "case-erip": ("Кейс · ЕРИП", 'ЕРИП <span class="section-title__muted">контакт-центр на базе Asterisk и Битрикс24</span>', "Контакт-центр ЕРИП"),
    "case-paritetbank": ("Кейс · Паритетбанк", 'Паритетбанк <span class="section-title__muted">автоматизация B2B-направления</span>', "Автоматизация B2B-направления в Паритетбанке"),
    "case-helix": ("Кейс · Helix", 'Helix <span class="section-title__muted">доработка Битрикс24 для лаборатории</span>', "Доработка Битрикс24 для лаборатории Helix"),
    "case-imkliva": ("Кейс · Imkliva Insurance", 'Imkliva Insurance <span class="section-title__muted">обработка обращений в Битрикс24</span>', "Система обработки обращений Imkliva Insurance"),
    # направление «Сайты»
    "case-moto": ("Кейс · Автогрупп", 'Автогрупп <span class="section-title__muted">промо-страница доставки мотоциклов из США</span>', "Промо-страница доставки мотоциклов из США Автогрупп"),
    "case-plyusagrokhim": ("Кейс · Плюсагрохим", 'Плюсагрохим <span class="section-title__muted">сайт агрохимической компании</span>', "Сайт агрохимической компании Плюсагрохим"),
    "case-smartopan": ("Кейс · SmartOpan", 'SmartOpan <span class="section-title__muted">сайт производителя сэндвич-панелей</span>', "Сайт производителя сэндвич-панелей SmartOpan"),
    "case-bgmu-journal": ("Кейс · БГМУ", 'Медицинский журнал БГМУ <span class="section-title__muted">сайт научного издания</span>', "Сайт медицинского журнала БГМУ"),
    "case-bgmu-professor": ("Кейс · БГМУ Профессор", 'БГМУ Профессор <span class="section-title__muted">сайт медицинских услуг с онлайн-записью</span>', "Сайт медицинских услуг БГМУ Профессор с онлайн-записью"),
    "case-rival": ("Кейс · RIVAL", 'RIVAL <span class="section-title__muted">редизайн сайта производителя автозапчастей</span>', "Редизайн сайта производителя автозапчастей RIVAL"),
    "case-avant-tekno": ("Кейс · АВАНТ-ТЕХНО", 'АВАНТ-ТЕХНО <span class="section-title__muted">восстановление сайта после вирусной атаки</span>', "Восстановление сайта и CRM АВАНТ-ТЕХНО после вирусной атаки"),
    "case-atrium": ("Кейс · Atrium.by", 'Atrium.by <span class="section-title__muted">техническая поддержка интернет-магазина</span>', "Техническая поддержка интернет-магазина Atrium.by"),
    "case-a100-support": ("Кейс · АЗС А-100", 'АЗС А-100 <span class="section-title__muted">доработки и техническая поддержка сайта</span>', "Доработки и техническая поддержка сайта АЗС А-100"),
    "case-bnb-bank": ("Кейс · БНБ-Банк", 'БНБ-Банк <span class="section-title__muted">доработка функционала сайта банка</span>', "Доработка функционала сайта БНБ-Банка"),
    "case-gadzhettreyd": ("Кейс · Гаджеттрэйд", 'Гаджеттрэйд <span class="section-title__muted">доработка и поддержка сайта электроники</span>', "Доработка сайта сети магазинов электроники Гаджеттрэйд"),
    "case-autolight-kabinet": ("Кейс · АвтолайтЭкспресс", 'АвтолайтЭкспресс <span class="section-title__muted">личный кабинет с интеграцией 1С</span>', "Личный кабинет АвтолайтЭкспресс с интеграцией 1С"),
    "case-b2b-kabinet": ("Кейс · АЗС А-100", 'АЗС А-100 <span class="section-title__muted">B2B-кабинет заказа топлива</span>', "Многофункциональный B2B-кабинет для АЗС А-100"),
    "case-dodoma": ("Кейс · До дома", 'До дома <span class="section-title__muted">личный кабинет службы доставки</span>', "Личный кабинет службы доставки До дома"),
    "case-maksiznay": ("Кейс · МаксиЗнай", 'МаксиЗнай <span class="section-title__muted">детская образовательная соцсеть</span>', "Детская образовательная социальная сеть МаксиЗнай"),
    "case-maximus": ("Кейс · Maximus", 'Maximus <span class="section-title__muted">детская образовательная платформа</span>', "Детская образовательная платформа Maximus"),
    # направление «IP-АТС на базе Asterisk»
    "case-beltelekom": ("Кейс · Белтелеком", 'Белтелеком <span class="section-title__muted">IP-АТС Asterisk и интеграция с Битрикс24</span>', "Внедрение IP-АТС Asterisk для Белтелекома"),
    "case-worldclass": ("Кейс · World Class", 'World Class <span class="section-title__muted">внедрение IP-АТС на базе Asterisk</span>', "Внедрение IP-АТС Asterisk для World Class"),
    "case-alatantur": ("Кейс · АлатанТур", 'АлатанТур <span class="section-title__muted">IP-телефония и интеграция с Битрикс24</span>', "Внедрение IP-телефонии и интеграция с Битрикс24 для АлатанТур"),
    "case-pinskdrev": ("Кейс · Пинскдрев", 'Пинскдрев <span class="section-title__muted">IP-АТС Asterisk для холдинга</span>', "Внедрение IP-АТС Asterisk для холдинга «Пинскдрев»"),
    "case-belita": ("Кейс · Белита", 'Белита <span class="section-title__muted">IP-АТС Asterisk и интеграция с Битрикс24</span>', "Внедрение IP-АТС Asterisk и интеграция с Битрикс24 для Белиты"),
    "case-aktivlizing": ("Кейс · Активлизинг", 'Активлизинг <span class="section-title__muted">внедрение IP-АТС на базе Asterisk</span>', "Внедрение IP-АТС Asterisk для Активлизинга"),
    "case-karandash": ("Кейс · Карандаш", 'Карандаш <span class="section-title__muted">внедрение IP-АТС на базе Asterisk</span>', "Внедрение IP-АТС Asterisk для компании Карандаш"),
    "case-tvoya-stolitsa": ("Кейс · Твоя Столица", 'Твоя Столица <span class="section-title__muted">внедрение IP-АТС на базе Asterisk</span>', "Внедрение IP-АТС Asterisk для компании Твоя Столица"),
    "case-viliya-park": ("Кейс · Вилия Парк", 'Вилия Парк <span class="section-title__muted">IP-АТС Asterisk для отельного комплекса</span>', "Внедрение IP-АТС Asterisk для Вилия Парк"),
    "case-adel": ("Кейс · ADEL", 'ADEL <span class="section-title__muted">IP-телефония для сети аптек</span>', "Внедрение и настройка IP-телефонии для сети аптек ADEL"),
    "case-santa": ("Кейс · Санта", 'Санта <span class="section-title__muted">интеграция Битрикс24 с IP-АТС Asterisk</span>', "Внедрение модуля интеграции Битрикс24 с IP-АТС на базе Asterisk для Санты"),
}


def build_card(cid):
    # Кейсы, которые уже свёрстаны на новом сайте (service-bitrix24.html), дублируем как есть
    if cid in EXISTING:
        return EXISTING[cid]["card"]
    c = CASES_DATA[cid]
    eyebrow, card_title, alt = CASE_META[cid]
    shot = c["tile"] or "assets/img/mega-menu-banner.webp"
    return f'''              <li class="case-card glow-card">
                <h3 class="case-card__title"><a class="case-card__link" href="https://itach.by/portfolio/{c['slug']}/" data-detail-open="{cid}">{card_title}</a></h3>
                <span class="card-expand" aria-hidden="true"><svg class="icon icon--gradient"><use href="#icon-expand" /></svg></span>
                <img class="case-card__shot" src="{shot}" width="1440" height="940" alt="{alt}" loading="lazy" />
              </li>'''


def _blocks_html(blocks):
    out = []
    for b in blocks:
        if b["t"] == "h":
            out.append(f'<h4 class="detail__subh">{b["text"]}</h4>')
        elif b["t"] == "p":
            out.append(f'<p>{b["html"]}</p>')
        elif b["t"] in ("ul", "ol"):
            tag = "ol" if b["t"] == "ol" else "ul"
            out.append(f'<{tag}><li>' + "</li><li>".join(b["items"]) + "</li></" + tag + ">")
        elif b["t"] == "img" and b.get("src"):
            out.append(img_figure(b["src"], b.get("alt", ""), "detail__figure"))
    return "\n".join(out)


def duration_stat(duration):
    """Градиентное значение — только цифры и предлоги (от/до/более…),
    единицы времени (год, месяц, неделя…) — в тёмный текст."""
    d = duration.strip()
    m = re.match(r"^(более|менее|свыше|около)?\s*(\d+)\s*год\w*\s+(\d+)\s*месяц\w*$", d)
    if m:
        years = int(m.group(2)) + int(m.group(3)) / 12
        val = f"{years:.2f}".rstrip("0").rstrip(".").replace(".", ",")
        prep = (m.group(1) or "").strip()
        return f"{prep} {val}".strip(), "года — длительность проекта"
    m = re.match(r"^(более|менее|свыше|около)?\s*(\d+)\s*(недел\w*|месяц\w*|год\w*|лет|дн\w*|час\w*|минут\w*)$", d)
    if m:
        val = f"{m.group(1) or ''} {m.group(2)}".strip()
        return val, f"{m.group(3)} — длительность проекта"
    return d, "длительность проекта"


def bento_html(c):
    """Бенто со сроком и составом команды (карточки с цифрами)."""
    tiles = []
    if c.get("duration"):
        value, label = duration_stat(c["duration"])
        tiles.append(
            f'<div class="detail-tile detail-tile--stat glow-card"><p class="detail-tile__value">{value}</p>'
            f'<p class="detail-tile__label">{label}</p></div>'
        )
    if c.get("team"):
        team_items = [re.sub(r"^[·\s\xa0]+", "", t).strip() for t in c["team"]]
        team_items = [t for t in team_items if t]
        items = "".join(f"<li>{t}</li>" for t in team_items)
        tiles.append(
            f'<div class="detail-tile detail-tile--stat glow-card"><p class="detail-tile__value">{len(team_items)}</p>'
            f'<p class="detail-tile__label">специалистов в команде</p><ul class="detail-tile__list">{items}</ul></div>'
        )
    return f'<div class="detail__bento">{"".join(tiles)}</div>' if tiles else ""


def build_template(cid, with_site=False):
    # Уже свёрстанные на новом сайте кейсы дублируем без изменений; если в оригинале
    # нет бенто с цифрами, но данные есть — дополняем
    if cid in EXISTING:
        tpl = EXISTING[cid]["template"]
        if 'detail__bento' not in tpl and cid in CASES_DATA:
            b = bento_html(CASES_DATA[cid])
            if b:
                tpl = tpl.replace('<div class="detail__article">', b + '\n<div class="detail__article">', 1)
        return tpl
    c = CASES_DATA[cid]
    eyebrow, card_title, alt = CASE_META[cid]
    about = c.get("about", [])
    lead = about[0] if about else c["title"]

    # Кнопка «Открыть сайт»: у кейсов «Битрикс24» её нет, на страницах «Сайтов» — есть
    site_btn = ""
    if with_site and c.get("site"):
        host = re.sub(r"^https?://(www\.)?", "", c["site"]).rstrip("/")
        site_btn = (
            f'<a class="btn btn--outline detail__site" href="{c["site"]}" target="_blank" rel="noopener noreferrer">'
            f'<span>Открыть сайт {host}</span><svg class="icon" aria-hidden="true"><use href="#icon-arrow-up-right" /></svg></a>'
        )

    points = ""
    if c.get("points"):
        cls = "detail__check" if len(c["points"]) > 4 else "detail__check detail__check--single"
        items = "".join(f"<li>{p}</li>" for p in c["points"])
        points = (
            f'<div class="detail__points"><h3 class="detail__points-title">Проект включал</h3>'
            f'<ul class="{cls}">{items}</ul></div>'
        )

    bento = bento_html(c)

    article_parts = []
    for extra in about[1:]:
        article_parts.append(f"<p>{extra}</p>")
    # в конце описания картинок быть не должно: срезаем иллюстрации «хвостом»
    # после последнего текстового блока (скрины остаются только внутри текста)
    flow = list(c.get("flow") or c.get("sections", []))
    while flow and all(b["t"] == "img" for b in flow[-1]["blocks"]):
        flow = flow[:-1]
    if flow:
        blocks = list(flow[-1]["blocks"])
        while blocks and blocks[-1]["t"] == "img":
            blocks = blocks[:-1]
        flow[-1] = dict(flow[-1], blocks=blocks)
    for sec in flow:
        body = _blocks_html(sec["blocks"])
        if not body:
            continue
        if sec["heading"]:
            article_parts.append(f'<h3 class="detail__h">{sec["heading"]}</h3>')
        article_parts.append(body)

    return f'''    <template id="detail-{cid}">
      <header class="detail__head">
        <p class="detail__eyebrow">{eyebrow}</p>
        <h2 class="detail__title" id="detail-title">{c["title"]}</h2>
        <p class="detail__lead">{lead}</p>
        <div class="detail__actions"><button class="btn btn--primary" type="button" data-detail-lead>Обсудить похожий проект</button>{site_btn}</div>
      </header>
      <figure class="detail__hero"><img src="{c['tile']}" {img_attrs(c['tile'])} alt="" /></figure>
{points}
{bento}
      <div class="detail__article">{"".join(article_parts)}</div>
    </template>'''

# ---------------------------------------------------------------- сегменты образца
M_MAIN = "    <main id=\"main\">"
M_CLIENTS = "      <!-- Лента логотипов клиентов"
M_SECTIONS = '      <div class="service-sections">\n'
M_CALC = "        <!-- Калькулятор стоимости -->"
M_AUDIENCE = "        <!-- Кому подходит: селектор аудиторий"
M_PROCESS = "        <!-- 4. Процесс -->"
M_TEAM = "        <!-- 5. Команда -->"
M_TECH = "        <!-- 6. Технологии -->"
M_AWARDS = "        <!-- 8. Наши достижения"
M_REVIEWS = "        <!-- 9. Отзывы -->"
M_FAQ = "        <!-- 10. FAQ -->"
M_FORM = "      <!-- 10. Форма -->"
M_RELATED = "      <!-- 11. Перелинковка"
M_FOOTER = '    <footer class="site-footer">'
M_TEMPLATES = "    <!-- Содержимое детальных окон кейсов"
M_BODYEND = "  </body>"

def seg(src, start, end):
    a = src.index(start)
    b = src.index(end)
    assert a < b, f"порядок маркеров нарушен: {start!r} -> {end!r}"
    return src[a:b]

SEG_HEAD = base.split(M_MAIN)[0]                 # doctype..<header>..до <main>
SEG_CLIENTS = seg(base, M_CLIENTS, M_SECTIONS)   # лента логотипов
SEG_CALC = seg(base, M_CALC, M_AUDIENCE)         # калькулятор (без «Кому подходит» из образца)
SEG_TECH = seg(base, M_TECH, M_AWARDS)
SEG_AWARDS = seg(base, M_AWARDS, M_REVIEWS)
SEG_REVIEWS = seg(base, M_REVIEWS, M_FAQ)
SEG_LEAD = seg(base, M_FORM, M_RELATED)          # форма
SEG_FOOTER = seg(base, M_FOOTER, M_TEMPLATES)    # футер, cookie, модалки
SEG_TAIL = base[base.index(M_BODYEND):]          # </body></html>

# ---------------------------------------------------------------- генераторы блоков
def hero(p):
    stats = "\n".join(
        f'''            <li class="page-stat glow-card" style="--i: {i}">
              <span class="page-stat__value">{v}</span>
              <p class="page-stat__text">{t}</p>
            </li>'''
        for i, (v, t) in enumerate(p["stats"])
    )
    cases_btn = (
        '\n                  <a class="btn btn--ghost" href="#cases">Смотреть кейсы</a>'
        if p.get("cases")
        else ""
    )
    return f'''      <!-- 1. Hero -->
      <section class="service-hero" aria-labelledby="service-hero-title">
        <div class="container">
          <nav class="breadcrumbs" aria-label="Хлебные крошки" data-reveal-stagger>
            <a class="breadcrumbs__link" href="index.html">Главная</a>
            <svg class="icon breadcrumbs__sep" aria-hidden="true"><use href="#icon-chevron-down" /></svg>
            <a class="breadcrumbs__link" href="services.html">Услуги</a>
            <svg class="icon breadcrumbs__sep" aria-hidden="true"><use href="#icon-chevron-down" /></svg>
            <a class="breadcrumbs__link" href="service-bitrix24.html">Битрикс24</a>
            <svg class="icon breadcrumbs__sep" aria-hidden="true"><use href="#icon-chevron-down" /></svg>
            <span class="breadcrumbs__current" aria-current="page">{p["short"]}</span>
          </nav>

          <div class="service-hero__middle">
            <div class="service-hero__intro">
              <h1 class="section-title" id="service-hero-title" data-reveal>
                {p["h1"]} <span class="section-title__muted">{p["h1_muted"]}</span>
              </h1>

              <div class="service-hero__content">
                <p class="service-hero__lead" data-reveal>
                  {p["lead"]}
                </p>
                <div class="service-hero__actions" data-reveal>
                  <a class="btn btn--primary" href="#calculator" data-calc-scroll>Рассчитать стоимость</a>{cases_btn}
                </div>
              </div>
            </div>

            <!-- Интерфейс Битрикс24: воронка сделок на экране ноутбука. Декоративная — смысл уже в заголовке -->
            <figure class="service-hero__figure" data-reveal>
              <img
                src="assets/img/b24-hero.webp"
                width="1438"
                height="1100"
                alt=""
                aria-hidden="true"
                fetchpriority="high"
                decoding="async"
              />
            </figure>
          </div>

          <ul class="page-stats page-stats--tall" data-reveal-stagger>
{stats}
          </ul>
        </div>
      </section>

'''

def about(p):
    return f'''        <!-- О направлении -->
        <section class="service-about">
          <div class="container">
            <p class="service-about__statement" data-text-fill>{p["statement"]}</p>
          </div>
        </section>

'''

def problems(p):
    rows = "\n".join(
        f'''              <li class="problem-row">
                <span class="problem-row__keyword">{kw}</span>
                <p class="problem-row__desc">{desc}</p>
                <span class="problem-row__stamp" aria-hidden="true">
                  <svg class="icon icon--gradient"><use href="#icon-check" /></svg>
                  <span class="problem-row__stamp-text">Решим</span>
                </span>
              </li>'''
        for kw, desc in p["problems"]
    )
    return f'''        <!-- Проблемы строками: ключевое слово слева серым, описание по центру,
             справа — штамп «Решим». Каждая строка всплывает по мере скролла -->
        <section class="problems" aria-labelledby="problems-title">
          <div class="container">
            <h2 class="section-title" data-reveal id="problems-title">
              Проблемы, которые <span class="section-title__muted">решаем</span>
            </h2>
            <ul class="problem-rows" data-problem-rows>
{rows}
            </ul>
          </div>
        </section>

'''

def audience(p):
    tabs = "\n".join(
        f'''                <button class="audience-tab glow-card{' is-active' if i == 0 else ''}" type="button" role="tab" id="aud-tab-{i+1}" aria-selected="{'true' if i == 0 else 'false'}" aria-controls="aud-panel-{i+1}"{' tabindex="-1"' if i else ''}>
                  <span class="audience-tab__text">{tab}</span>
                </button>'''
        for i, (tab, _, _) in enumerate(p["audience"])
    )
    panels = "\n".join(
        f'''                <div class="audience-panel glow-card{' is-active' if i == 0 else ''}" role="tabpanel" id="aud-panel-{i+1}" aria-labelledby="aud-tab-{i+1}">
                  <img class="audience-panel__art" src="assets/img/audience-wave.png" alt="" aria-hidden="true" loading="lazy" />
                  <h3 class="audience-panel__title">{title}</h3>
                  <p class="audience-panel__text">{text}</p>
                </div>'''
        for i, (_, title, text) in enumerate(p["audience"])
    )
    return f'''        <!-- Кому подходит: селектор аудиторий. Список слева, панель выбранного справа;
             переключение наведением на десктопе и кликом везде -->
        <section class="audience" aria-labelledby="segments-title">
          <div class="container">
            <h2 class="section-title" data-reveal id="segments-title">
              Кому <span class="section-title__muted">подходит</span>
            </h2>
            <div class="audience-picker" data-audience-picker data-reveal>
              <div class="audience-picker__list" role="tablist" aria-label="Аудитории">
{tabs}
              </div>
              <div class="audience-picker__panels">
{panels}
              </div>
            </div>
        </section>

'''

def cases(p):
    if not p.get("cases"):
        return ""
    cards = "\n".join(build_card(c) for c in p["cases"])
    cases_heading = p.get("cases_title_html") or (
        f'Кейсы <span class="section-title__muted">{p["cases_title"]}</span>'
    )
    # Раскладка по числу кейсов: 2 — две большие (базовая), 3 — три маленькие в ряд,
    # 4 — четыре большие в два ряда, 5 — две большие + три маленькие (базовая)
    n = len(p["cases"])
    grid_cls = "case-grid"
    if n == 3:
        grid_cls += " case-grid--three"
    elif n == 4:
        grid_cls += " case-grid--four"
    return f'''        <!-- 2. Кейсы -->
        <section class="cases" id="cases" aria-labelledby="cases-title">
          <div class="container">
            <h2 class="section-title" data-reveal id="cases-title">
              {cases_heading}
            </h2>
            <div class="cases__scroller">
            <ul class="{grid_cls}" data-reveal-stagger>
{cards}
            </ul>
            </div>
            <div class="section-action" data-reveal>
              <a class="btn btn--outline" href="portfolio.html">Все кейсы</a>
            </div>
          </div>
        </section>

'''

def formats(p):
    cards = "\n".join(
        f'''              <li class="format-card format-card--static glow-card">
                <div class="format-card__link">
                  <h3 class="format-card__title">{title}</h3>
                  <p class="format-card__desc">{desc}</p>
                  <ul class="format-card__prices">
                  <li class="format-card__price">
                    <span class="format-card__price-label">{label}</span>
                    <span class="format-card__price-value">{price}</span>
                  </li>
                  </ul>
                </div>
              </li>'''
        for title, desc, label, price in p["formats"]
    )
    return f'''        <!-- Форматы и стоимость -->
        <section class="formats" id="formats" aria-labelledby="formats-title">
          <div class="container">
            <h2 class="section-title" data-reveal id="formats-title">
              Форматы и <span class="section-title__muted">стоимость</span>
            </h2>
            <p class="formats__note" data-reveal>
              {p["formats_note"]}
            </p>
            <ul class="format-grid" data-reveal-stagger data-reveal-pair>
{cards}
            </ul>
          </div>
        </section>

'''

def process(p):
    steps = "\n".join(
        f'''              <li class="process-step">
                <span class="process-step__number" aria-hidden="true">{i+1:02d}</span>
                <div class="process-step__body">
                  <h3 class="process-step__title">{title}</h3>
                  <p class="process-step__text">{text}</p>
                </div>
                <div class="process-step__result">
                  <span class="process-step__result-label">Вы получаете</span>
                  <p class="process-step__result-text">{result}</p>
                </div>
              </li>'''
        for i, (title, text, result) in enumerate(p["process"])
    )
    return f'''        <!-- 4. Процесс -->
        <section class="process" id="process" aria-labelledby="process-title">
          <div class="container">
            <h2 class="section-title" data-reveal id="process-title">
              Как мы <span class="section-title__muted">работаем</span>
            </h2>
<ol class="process-steps" data-process-steps>
{steps}
            </ol>
          </div>
          <div class="container section-action" data-reveal>
            <a class="btn btn--outline" href="#lead">Обсудить проект</a>
          </div>
        </section>

'''

def faq(p):
    items = "\n".join(
        f'''              <li class="faq__item glow-card">
                <h3 class="faq__question">
                  <button class="faq__trigger" type="button" id="faq-q{i+1}" aria-expanded="false" aria-controls="faq-a{i+1}">
                    <span class="faq__text">{q}</span>
                    <span class="faq__toggle" aria-hidden="true"></span>
                  </button>
                </h3>
                <div class="faq__answer" id="faq-a{i+1}" role="region" aria-labelledby="faq-q{i+1}">
                  <div class="faq__answer-inner"><p>{a}</p></div>
                </div>
              </li>'''
        for i, (q, a) in enumerate(p["faq"])
    )
    return f'''        <!-- 10. FAQ -->
        <section class="faq" id="faq" aria-labelledby="faq-title">
          <div class="container faq__layout" data-faq>
            <div class="faq__intro" data-reveal>
              <h2 class="section-title faq__title" id="faq-title">Частые вопросы <span class="section-title__muted">{p["faq_muted"]}</span></h2>
              <a class="btn btn--outline" href="#lead">Задать свой вопрос</a>
            </div>
            <ul class="faq__list" data-reveal-stagger>
{items}
            </ul>
          </div>
        </section>
'''

def tools_block(p):
    groups = p.get("tools") or []
    if not groups:
        return ""
    tabs = "\n".join(
        f'''                <button class="tools-tab{' is-active' if i == 0 else ''}" type="button" role="tab" id="tools-tab-{i+1}" aria-selected="{'true' if i == 0 else 'false'}" aria-controls="tools-panel-{i+1}"{' tabindex="-1"' if i else ''}>
                  <span>{g["title"]}</span>
                </button>'''
        for i, g in enumerate(groups)
    )
    panels = "\n".join(
        f'''              <div class="tools-panel{' is-active' if i == 0 else ''}" role="tabpanel" id="tools-panel-{i+1}" aria-labelledby="tools-tab-{i+1}">
                {f'<p class="tools-intro">{g["intro"]}</p>' if g.get("intro") else ''}
                <ul class="tools-list">
                  {chr(10).join(f'<li class="tools-item glow-card"><h3 class="tools-item__name">{name}</h3><p class="tools-item__text">{text}</p></li>' for name, text in g["tools"])}
                </ul>
              </div>'''
        for i, g in enumerate(groups)
    )
    lead = f'<p class="tools-lead" data-reveal>{p["tools_lead"]}</p>\n            ' if p.get("tools_lead") else ""
    cta = (
        f'''<div class="section-action" data-reveal>
              <a class="btn btn--outline" href="#lead">{p["tools_cta"]}</a>
            </div>
            '''
        if p.get("tools_cta")
        else ""
    )
    return f'''        <!-- Табы групп (переключение по клику), под ними панель выбранной группы -->
        <section class="tools" aria-labelledby="tools-title">
          <div class="container">
            <h2 class="section-title" data-reveal id="tools-title">
              {p["tools_title"]} <span class="section-title__muted">{p["tools_title_muted"]}</span>
            </h2>
            {lead}<div class="tools-picker" data-tools-picker data-no-hover-switch data-reveal>
              <div class="tools-tabs" role="tablist" aria-label="Группы инструментов">
{tabs}
              </div>
              <div class="tools-panels">
{panels}
              </div>
            </div>
            {cta}</div>
        </section>

'''

def related(p):
    links = "\n".join(
        f'            <li><a class="related__link" href="{href}">{text}</a></li>'
        for href, text in p["related"]
    )
    return f'''      <!-- 11. Перелинковка: другие услуги направления -->
      <section class="related" aria-labelledby="related-title">
        <div class="container">
          <h2 class="section-title" data-reveal id="related-title">
            Другие <span class="section-title__muted">услуги направления</span>
          </h2>
          <ul class="related__list" data-reveal-stagger>
{links}
          </ul>
        </div>
      </section>
'''

def templates(p):
    if not p.get("cases"):
        return ""
    body = "\n\n".join(build_template(c) for c in p["cases"])
    return f'''    <!-- Содержимое детальных окон кейсов: тексты и ссылки взяты с itach.by -->
{body}

'''

# ---------------------------------------------------------------- head
def head(p):
    h = SEG_HEAD
    h = re.sub(r"<title>.*?</title>", f"<title>{p['title']}</title>", h, flags=re.DOTALL)
    h = re.sub(
        r'<meta name="description" content="[^"]*"',
        f'<meta name="description" content="{p["description"]}"',
        h,
    )
    service_ld = {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": p["ld_name"],
        "provider": {"@type": "Organization", "name": "Итач-софт", "url": "https://itach-soft.ru"},
        "areaServed": ["RU", "BY"],
        "offers": [
            {
                "@type": "Offer",
                "name": title,
                "priceSpecification": {
                    "@type": "PriceSpecification",
                    "priceCurrency": "RUB",
                    "minPrice": price_num,
                },
            }
            for title, _, _, _, price_num in p["formats_ld"]
        ],
    }
    faq_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in p["faq"]
        ],
    }
    blocks = [
        "<script type=\"application/ld+json\">\n" + json.dumps(service_ld, ensure_ascii=False, indent=2) + "\n    </script>",
        "<script type=\"application/ld+json\">\n" + json.dumps(faq_ld, ensure_ascii=False, indent=2) + "\n    </script>",
    ]
    it = iter(blocks)
    h = re.sub(
        r'<script type="application/ld\+json">.*?</script>',
        lambda m: next(it),
        h,
        count=2,
        flags=re.DOTALL,
    )
    h = h.replace(
        'href="service-sites.html" aria-current="page"><span>Сайты</span>',
        'href="service-bitrix24.html" aria-current="page"><span>Битрикс24</span>',
    )
    return h

# ---------------------------------------------------------------- сборка
def build(p):
    return "".join(
        [
            head(p),
            M_MAIN + "\n",
            hero(p),
            SEG_CLIENTS,
            M_SECTIONS,
            about(p),
            problems(p),
            cases(p),
            formats(p),
            SEG_CALC,
            audience(p),
            process(p),
            tools_block(p),
            "" if p.get("hide_tech") else SEG_TECH,
            SEG_AWARDS,
            SEG_REVIEWS,
            faq(p),
            "      </div>\n\n",  # закрыть service-sections
            SEG_LEAD,
            related(p),
            SEG_FOOTER,
            templates(p),
            SEG_TAIL,
        ]
    )

if __name__ == "__main__":
    from bitrix24_content import PAGES  # noqa: E402

    for p in PAGES:
        html = build(p)
        out = ROOT / p["file"]
        out.write_text(html, encoding="utf-8")
        print(f"OK {out.name} ({len(html.splitlines())} строк)")
