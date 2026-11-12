# -*- coding: utf-8 -*-
"""Извлечение кейсов с itach.by → tools/cases_data.json + assets/img/detail/.

Для каждого кейса: заголовок, лид, список «Проект включал», команда,
длительность, статья с детализацией и результатами, скриншоты.
Картинки скачиваются в assets/img/detail/case-<id>-*.(jpg|png|webp).
"""
import json
import re
import sys
import html as htmllib
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = ROOT / "analysis" / "cases"
IMG_DIR = ROOT / "assets" / "img" / "detail"
IMG_DIR.mkdir(parents=True, exist_ok=True)

BASE = "https://itach.by"

# case_id → (slug на itach.by, eyebrow для detail__head, подпись карточки, alt обложки)
CASE_MAP = {
    "case-mebel": ("vnedrenie-bitriks24-v-mebelnuyu-kompaniyu", "Кейс · Мебельная компания",
                   'Мебельная компания <span class="section-title__muted">Битрикс24 для 3000+ сотрудников</span>',
                   "Внедрение Битрикс24 в мебельную компанию"),
    "case-totek": ("vnedrenie-i-nastroyka-bitriks24-dlya-kompanii-totek", "Кейс · Тотек",
                   'Тотек <span class="section-title__muted">внедрение и настройка Битрикс24</span>',
                   "Внедрение Битрикс24 для компании Тотек"),
    "case-contact-center": ("vnedrenie-i-nastroyka-bitriks24-dlya-kontakt-tsentra", "Кейс · Контакт-центр",
                            'Контакт-центр <span class="section-title__muted">автоматизация обращений на CRM Битрикс24</span>',
                            "Автоматизация работы контакт-центра на базе Битрикс24"),
    "case-zenit": ("dorabotka-bitriks24-dlya-yuk-zenit", "Кейс · УК «Зенит»",
                   'УК «Зенит» <span class="section-title__muted">доработка Битрикс24 и автоматизация процессов</span>',
                   "Доработка Битрикс24 для УК «Зенит»"),
    "case-hr": ("dorabotka-hr-modulya-i-organizatsionnoy-struktury-na-portale-bitriks24", "Кейс · HR-портал",
                'HR-портал <span class="section-title__muted">доработка HR-модуля и оргструктуры</span>',
                "Доработка HR-модуля и оргструктуры на портале Битрикс24"),
    "case-zajamnae": ("dorabotki-bitriks24-dlya-brenda-zajamnae", "Кейс · ZAJAMNAE",
                      'ZAJAMNAE <span class="section-title__muted">доработки Битрикс24 для бренда</span>',
                      "Доработки Битрикс24 для бренда ZAJAMNAE"),
    "case-miele": ("razrabotka-sayta-kataloga-bytovoy-tekhniki", "Кейс · Miele",
                    'Miele <span class="section-title__muted">интернет-магазин бытовой техники</span>',
                    "Интернет-магазин бытовой техники Miele"),
    "case-selfielab": ("razrabotka-sayta-kataloga-dlya-brenda-kosmetiki", "Кейс · SelfieLab",
                       'SelfieLab <span class="section-title__muted">интернет-магазин косметики</span>',
                       "Интернет-магазин косметики SelfieLab"),
    "case-sibifood": ("redizayn-internet-magazina-produktov", "Кейс · SibiFood",
                      'SibiFood <span class="section-title__muted">редизайн интернет-магазина продуктов</span>',
                      "Редизайн интернет-магазина экологических продуктов SibiFood"),
    "case-alkor": ("alkor-brillianty-rossii", "Кейс · Алькор",
                   'Алькор <span class="section-title__muted">доработка Битрикс24 для бренда бриллиантов</span>',
                   "Доработка Битрикс24 для Алькор Бриллианты России"),
    "case-maximus-int": ("integratsiya-veb-platformy-s-bitriks24", "Кейс · Maximus",
                         'Maximus <span class="section-title__muted">интеграция веб-платформы с Битрикс24</span>',
                         "Интеграция веб-платформы Maximus с Битрикс24"),
    "case-vnedr-int": ("vnedrenie-bitriks24-i-nastroyka-integratsiy", "Кейс · Санаторий «Приозерный»",
                       'Санаторий «Приозерный» <span class="section-title__muted">внедрение Битрикс24 и настройка интеграций</span>',
                       "Внедрение Битрикс24 и настройка интеграций для санатория «Приозерный»"),
    "case-triovist": ("razrabotka-prilozheniya-dlya-bitriks24-po-importu-kandidatov", "Кейс · Триовист",
                      'Триовист <span class="section-title__muted">приложение для Битрикс24: импорт кандидатов из rabota.by</span>',
                      "Приложение для Битрикс24 по импорту кандидатов из rabota.by для Триовист"),
    "case-cititrade": ("modernizatsiya-it-infrastruktury-s-vnedreniem-ip-telefonii-i-dorabotkoy-bitriks24", "Кейс · Сититрейдмаркет",
                       'Сититрейдмаркет <span class="section-title__muted">IP-телефония и доработка Битрикс24</span>',
                       "Модернизация IT-инфраструктуры с IP-телефонией и Битрикс24"),
    "case-docbank": ("avtomatizatsiya-dokumentooborota-v-banke", "Кейс · Банк",
                     'Банк <span class="section-title__muted">автоматизация документооборота</span>',
                     "Автоматизация документооборота в банке"),
    "case-hr-avto": ("avtomatizatsiya-kadrovykh-protsessov-v-bitriks24", "Кейс · HR-процессы",
                     'HR-процессы <span class="section-title__muted">автоматизация кадровых процессов в Битрикс24</span>',
                     "Автоматизация кадровых процессов в Битрикс24"),
    "case-telefonia": ("vnedrenie-i-integratsiya-ip-telefonii-s-bitriks24", "Кейс · IP-телефония",
                       'IP-телефония <span class="section-title__muted">внедрение и интеграция с Битрикс24</span>',
                       "Внедрение и интеграция IP-телефонии с Битрикс24"),
    "case-cepterbank": ("vnedrenie-ats-i-moduley-avtoobzvona-i-obrabotki-zvonkov", "Кейс · Цептер Банк",
                        'Цептер Банк <span class="section-title__muted">АТС Asterisk и модули автообзвона</span>',
                        "Внедрение АТС и модулей автообзвона в Цептер Банке"),
    "case-e2e4": ("dorabotki-i-tekhnicheskaya-podderzhka-bitriks24", "Кейс · E2E4",
                  'E2E4 <span class="section-title__muted">доработки и техническая поддержка Битрикс24</span>',
                  "Доработки и техническая поддержка Битрикс24 для E2E4"),
    # уже используемые — обогащаем скриншотами
    "case-rozyb24": ("vnedrenie-bitriks24-v-kompaniyu-rozy-bel", "Кейс · Розы.Бел",
                     'Розы.Бел <span class="section-title__muted">внедрение Битрикс24 в сеть магазинов</span>',
                     "Внедрение Битрикс24 в сеть цветочных магазинов Розы.Бел"),
    "case-erip": ("vnedrenie-kontakt-tsentra-na-baze-ip-asterisk", "Кейс · ЕРИП",
                  'ЕРИП <span class="section-title__muted">контакт-центр на базе Asterisk и Битрикс24</span>',
                  "Контакт-центр ЕРИП"),
    "case-paritetbank": ("kompleksnaya-avtomatizatsiya-b2b-napravleniya-v-paritetbanke", "Кейс · Паритетбанк",
                         'Паритетбанк <span class="section-title__muted">автоматизация B2B-направления</span>',
                         "Автоматизация B2B-направления в Паритетбанке"),
    "case-helix": ("dorabotki-bitriks24-dlya-laboratorii-helix", "Кейс · Helix",
                   'Helix <span class="section-title__muted">доработка Битрикс24 для лаборатории</span>',
                   "Доработка Битрикс24 для лаборатории Helix"),
    "case-imkliva": ("kompleksnaya-dorabotka-bitriks24-dlya-strakhovoy-kompanii", "Кейс · Imkliva Insurance",
                     'Imkliva Insurance <span class="section-title__muted">обработка обращений в Битрикс24</span>',
                     "Система обработки обращений Imkliva Insurance"),
    # --- кейсы направления «Сайты» ---
    "case-moto": ("lending-peydzh-po-dostavke-moto-iz-ssha", "Кейс · Автогрупп",
                  'Автогрупп <span class="section-title__muted">промо-страница доставки мотоциклов из США</span>',
                  "Промо-страница доставки мотоциклов из США Автогрупп"),
    "case-plyusagrokhim": ("razrabotka-sayta-dlya-kompanii-ooo-plyusagrokhim", "Кейс · Плюсагрохим",
                           'Плюсагрохим <span class="section-title__muted">сайт агрохимической компании</span>',
                           "Сайт агрохимической компании Плюсагрохим"),
    "case-smartopan": ("razrabotka-korporativnogo-sayta-dlya-proizvoditelya-metallokonstruktsiy", "Кейс · SmartOpan",
                       'SmartOpan <span class="section-title__muted">сайт производителя сэндвич-панелей</span>',
                       "Сайт производителя сэндвич-панелей SmartOpan"),
    "case-bgmu-journal": ("razrabotka-sayta-meditsinskogo-zhurnala", "Кейс · БГМУ",
                          'Медицинский журнал БГМУ <span class="section-title__muted">сайт научного издания</span>',
                          "Сайт медицинского журнала БГМУ"),
    "case-bgmu-professor": ("korporativnyy-sayt-bgmu-professor", "Кейс · БГМУ Профессор",
                            'БГМУ Профессор <span class="section-title__muted">сайт медицинских услуг с онлайн-записью</span>',
                            "Сайт медицинских услуг БГМУ Профессор с онлайн-записью"),
    "case-rival": ("dorabotki-i-redizayn-sayta-rival", "Кейс · RIVAL",
                   'RIVAL <span class="section-title__muted">редизайн сайта производителя автозапчастей</span>',
                   "Редизайн сайта производителя автозапчастей RIVAL"),
    "case-avant-tekno": ("vosstanovlenie-sayta-i-crm-posle-virusnoy-ataki", "Кейс · АВАНТ-ТЕХНО",
                         'АВАНТ-ТЕХНО <span class="section-title__muted">восстановление сайта после вирусной атаки</span>',
                         "Восстановление сайта и CRM АВАНТ-ТЕХНО после вирусной атаки"),
    "case-atrium": ("tekhnicheskaya-podderzhka-internet-magazina-atrium-by", "Кейс · Atrium.by",
                    'Atrium.by <span class="section-title__muted">техническая поддержка интернет-магазина</span>',
                    "Техническая поддержка интернет-магазина Atrium.by"),
    "case-a100-support": ("dorabotki-i-tekhnicheskaya-podderzhka-sayta-azs-a-100", "Кейс · АЗС А-100",
                          'АЗС А-100 <span class="section-title__muted">доработки и техническая поддержка сайта</span>',
                          "Доработки и техническая поддержка сайта АЗС А-100"),
    "case-bnb-bank": ("dorabotka-funktsionala-dlya-sayta-bnb-banka", "Кейс · БНБ-Банк",
                      'БНБ-Банк <span class="section-title__muted">доработка функционала сайта банка</span>',
                      "Доработка функционала сайта БНБ-Банка"),
    "case-gadzhettreyd": ("dorabotka-sayta-dlya-kompanii-ooo-gadzhettreyd", "Кейс · Гаджеттрэйд",
                          'Гаджеттрэйд <span class="section-title__muted">доработка и поддержка сайта электроники</span>',
                          "Доработка сайта сети магазинов электроники Гаджеттрэйд"),
    "case-autolight-kabinet": ("razrabotka-lichnogo-kabineta-sayta-avtolayt-ekspress", "Кейс · АвтолайтЭкспресс",
                               'АвтолайтЭкспресс <span class="section-title__muted">личный кабинет с интеграцией 1С</span>',
                               "Личный кабинет АвтолайтЭкспресс с интеграцией 1С"),
    # веб-сервисы: данные для бенто (шаблоны уже свёрстаны на service-web-services.html)
    "case-b2b-kabinet": ("razrabotka-mnogofunktsionalnogo-b2b-kabineta", "Кейс · АЗС А-100",
                         'АЗС А-100 <span class="section-title__muted">B2B-кабинет заказа топлива</span>',
                         "Многофункциональный B2B-кабинет для АЗС А-100"),
    "case-dodoma": ("razrabotka-lichnogo-kabineta-dlya-sluzhby-dostavki-", "Кейс · До дома",
                    'До дома <span class="section-title__muted">личный кабинет службы доставки</span>',
                    "Личный кабинет службы доставки До дома"),
    "case-maksiznay": ("razrabotka-detskaya-obrazovatelnoy-sotsialnoy-seti", "Кейс · МаксиЗнай",
                       'МаксиЗнай <span class="section-title__muted">детская образовательная соцсеть</span>',
                       "Детская образовательная социальная сеть МаксиЗнай"),
    "case-maximus": ("razrabotka-detskoy-obrazovatelnoy-platformy-maksimus", "Кейс · Maximus",
                     'Maximus <span class="section-title__muted">детская образовательная платформа</span>',
                     "Детская образовательная платформа Maximus"),
    # направление «IP-АТС на базе Asterisk»
    "case-beltelekom": ("vnedrenie-ip-ats-na-baze-asterisk-dlya-rup-beltelekom", "Кейс · Белтелеком",
                        'Белтелеком <span class="section-title__muted">IP-АТС Asterisk и интеграция с Битрикс24</span>',
                        "Внедрение IP-АТС Asterisk для Белтелекома"),
    "case-worldclass": ("vnedrenie-ip-ats-na-baze-asterisk-dlya-kompanii-worldclass", "Кейс · World Class",
                        'World Class <span class="section-title__muted">внедрение IP-АТС на базе Asterisk</span>',
                        "Внедрение IP-АТС Asterisk для World Class"),
    "case-alatantur": ("vnedrenie-ip-telefonii-i-integratsiya-s-bitriks24-dlya-kompanii-alatantur", "Кейс · АлатанТур",
                       'АлатанТур <span class="section-title__muted">IP-телефония и интеграция с Битрикс24</span>',
                       "Внедрение IP-телефонии и интеграция с Битрикс24 для АлатанТур"),
    "case-pinskdrev": ("vnedrenie-ip-ats-na-baze-asterisk-dlya-zao-kholdingovaya-kompaniya-pinskdrev", "Кейс · Пинскдрев",
                       'Пинскдрев <span class="section-title__muted">IP-АТС Asterisk для холдинга</span>',
                       "Внедрение IP-АТС Asterisk для холдинга «Пинскдрев»"),
    "case-belita": ("vnedrenie-ip-ats-na-baze-asterisk-i-integratsiya-s-bitriks24-dlya-sp-belita-ooo", "Кейс · Белита",
                    'Белита <span class="section-title__muted">IP-АТС Asterisk и интеграция с Битрикс24</span>',
                    "Внедрение IP-АТС Asterisk и интеграция с Битрикс24 для Белиты"),
    "case-aktivlizing": ("vnedrenie-ip-ats-na-baze-asterisk-dlya-kompanii-aktivlizing", "Кейс · Активлизинг",
                         'Активлизинг <span class="section-title__muted">внедрение IP-АТС на базе Asterisk</span>',
                         "Внедрение IP-АТС Asterisk для Активлизинга"),
    "case-karandash": ("vnedrenie-ip-ats-na-baze-asterisk-dlya-kompanii-karandash", "Кейс · Карандаш",
                       'Карандаш <span class="section-title__muted">внедрение IP-АТС на базе Asterisk</span>',
                       "Внедрение IP-АТС Asterisk для компании Карандаш"),
    "case-tvoya-stolitsa": ("vnedrenie-ip-ats-na-baze-asterisk-dlya-kompanii-tvoya-stolitsa", "Кейс · Твоя Столица",
                            'Твоя Столица <span class="section-title__muted">внедрение IP-АТС на базе Asterisk</span>',
                            "Внедрение IP-АТС Asterisk для компании Твоя Столица"),
    "case-viliya-park": ("vnedrenie-ip-ats-na-baze-asterisk-dlya-viliya-park", "Кейс · Вилия Парк",
                         'Вилия Парк <span class="section-title__muted">IP-АТС Asterisk для отельного комплекса</span>',
                         "Внедрение IP-АТС Asterisk для Вилия Парк"),
    "case-adel": ("vnedrenie-i-nastroyka-ip-telefonii-dlya-aptek-adel", "Кейс · ADEL",
                  'ADEL <span class="section-title__muted">IP-телефония для сети аптек</span>',
                  "Внедрение и настройка IP-телефонии для сети аптек ADEL"),
    "case-santa": ("vnedrenie-modulya-integratsii-bitriks24-s-ip-ats-na-baze-asterisk", "Кейс · Санта",
                   'Санта <span class="section-title__muted">интеграция Битрикс24 с IP-АТС Asterisk</span>',
                   "Внедрение модуля интеграции Битрикс24 с IP-АТС на базе Asterisk для Санты"),
}


def clean_text(t):
    t = re.sub(r"<[^>]+>", "", t)
    return htmllib.unescape(re.sub(r"\s+", " ", t)).strip()


def block_text(html):
    """Текст блока с сохранением абзацев: <br> и границы тегов → переносы."""
    t = re.sub(r"<br\s*/?>", "\n", html, flags=re.I)
    t = re.sub(r"</(p|li|h3|h4|div)>", "\n", t, flags=re.I)
    t = re.sub(r"<[^>]+>", "", t)
    t = htmllib.unescape(t)
    lines = [re.sub(r"\s+", " ", ln).strip("  ·\t") for ln in t.split("\n")]
    return [ln for ln in lines if ln]


def list_items(html):
    return [clean_text(li) for li in re.findall(r"<li[^>]*>(.*?)</li>", html, re.DOTALL)]


def download(url, dest):
    if dest.exists():
        return True
    path = quote(url, safe="/:?=&%")
    try:
        data = urlopen(BASE + path, timeout=60).read()
        dest.write_bytes(data)
        return True
    except Exception as e:
        print(f"  !! download failed {url}: {e}")
        return False


def extract_case(case_id, slug):
    raw = (CASES_DIR / f"{slug}.html").read_bytes().decode("utf-8", errors="replace")
    main = raw[raw.find("<main"):]
    data = {"id": case_id, "slug": slug}

    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', main, re.DOTALL)
    data["title"] = clean_text(h1.group(1)) if h1 else case_id

    descr = re.search(r'<div class="section-project__descr">(.*?)</div>\s*</div>\s*<div class="section-project__col', main, re.DOTALL)
    if descr:
        paras = block_text(re.sub(r"<h3>.*?</h3>", "", descr.group(1), flags=re.DOTALL))
        data["about"] = paras
    else:
        data["about"] = []

    m = re.search(r'<a class="section-project__link" href="(https?://[^"]+)"', main)
    data["site"] = m.group(1) if m and m.group(1).rstrip("/") not in ("https:", "http:") else ""

    # главная картинка
    main_pic = None
    pm = re.search(r'section-project__pic-wrap.*?<img src="([^"]+)"', main, re.DOTALL)
    if pm:
        main_pic = pm.group(1)
    elif descr is None:
        pm = re.search(r'<section class="section section-project[^>]*>.*?<img src="([^"]+)"', main, re.DOTALL)
        main_pic = pm.group(1) if pm else None

    ext = Path(main_pic).suffix if main_pic else ""
    ext = ext if ext.lower() in (".jpg", ".jpeg", ".png", ".webp") else ".jpg"
    tile = f"assets/img/detail/{case_id}-tile-0{ext}"
    if main_pic and download(main_pic, ROOT / tile):
        data["tile"] = tile
    else:
        data["tile"] = ""

    # сводка
    desc_sec = re.search(r'<section class="section section-project-desc">(.*?)<section class="section section-project-style', main, re.DOTALL)
    sec_html = desc_sec.group(1) if desc_sec else ""
    blocks = re.split(r'<div class="col-25 col-25__title text-l">', sec_html)
    data["points"], data["team"], data["duration"] = [], [], ""
    for b in blocks[1:]:
        head, _, body = b.partition("</div>")
        items = list_items(body)
        if "Проект включал" in head:
            # пункты могут быть в <p> внутри <ul>
            items = [clean_text(p) for p in re.findall(r"<p[^>]*>(.*?)</p>", body, re.DOTALL)] or items
            data["points"] = [i for i in items if i]
        elif "Команда" in head:
            items = [clean_text(p) for p in re.findall(r"<p[^>]*>(.*?)</p>", body, re.DOTALL)] or items
            data["team"] = [i for i in items if i]
        elif "Длительность" in head:
            data["duration"] = clean_text(body)

    # детализация и результаты: каждая секция project-style отдельно,
    # блоки в порядке следования: h3 / p / список / картинка
    def parse_content(content):
        blocks = []
        for m in re.finditer(
            r"<h3[^>]*>(.*?)</h3>|<p[^>]*>(.*?)</p>|<(ul|ol)[^>]*>(.*?)</\3>|<img[^>]+src=\"([^\"]+)\"[^>]*?(?:alt=\"([^\"]*)\")?[^>]*>",
            content, re.DOTALL,
        ):
            if m.group(1) is not None:
                blocks.append({"t": "h", "text": clean_text(m.group(1))})
            elif m.group(2) is not None:
                txt = re.sub(r"\s+", " ", m.group(2)).strip()
                if txt:
                    blocks.append({"t": "p", "html": txt})
            elif m.group(4) is not None:
                tag = m.group(3)
                items = []
                for li in re.findall(r"<li[^>]*>(.*?)</li>", m.group(4), re.DOTALL):
                    txt = re.sub(r"\s+", " ", li).strip()
                    if txt:
                        items.append(txt)
                if items:
                    blocks.append({"t": "ol" if tag == "ol" else "ul", "items": items})
            elif m.group(5) is not None:
                src, alt = m.group(5), m.group(6) or ""
                if re.search(r"logo|icon|sprite", src, re.I) or src.startswith("data:"):
                    continue
                blocks.append({"t": "img", "src": src, "alt": htmllib.unescape(alt).strip()})
        return blocks

    data["sections"] = []
    for chunk in main.split('<section class="section section-project-style">')[1:]:
        body = chunk.split('<section class="section', 1)[0]
        heading = re.search(r'<div class="title(?:-l)?"[^>]*>(.*?)</div>', body, re.DOTALL)
        content = body[body.find("</div>") + 6:] if heading else body
        data["sections"].append({
            "heading": clean_text(heading.group(1)) if heading else "",
            "blocks": parse_content(content),
        })

    # сквозной поток контента в порядке документа: текстовые секции и
    # иллюстрации (project-pic / pic-100) на своих местах — «в процессе работы»
    data["flow"] = []
    for m in re.finditer(
        r'<section class="section section-(project-style|project-pic|pic-100)">',
        main,
    ):
        kind = m.group(1)
        body = main[m.end():].split('<section class="section', 1)[0]
        if kind == "project-style":
            heading = re.search(r'<div class="title(?:-l)?"[^>]*>(.*?)</div>', body, re.DOTALL)
            content = body[body.find("</div>") + 6:] if heading else body
            data["flow"].append({
                "heading": clean_text(heading.group(1)) if heading else "",
                "blocks": parse_content(content),
            })
        else:
            blocks = []
            for im in re.finditer(r'<img[^>]+src="([^"]+)"[^>]*?(?:alt="([^"]*)")?[^>]*>', body):
                src, alt = im.group(1), im.group(2) or ""
                if re.search(r"logo|icon|sprite", src, re.I) or src.startswith("data:"):
                    continue
                blocks.append({"t": "img", "src": src, "alt": htmllib.unescape(alt).strip()})
            if blocks:
                data["flow"].append({"heading": "", "blocks": blocks})

    # чистим артефакты сводки
    data["duration"] = re.sub(r"^[·\s\xa0]+", "", data.get("duration", ""))

    # скачиваем inline-иллюстрации из текстов секций и из потока (pic-секции)
    inline_n = 0
    downloaded = {}
    for sec in data["sections"] + data.get("flow", []):
        for blk in sec["blocks"]:
            if blk["t"] == "img" and blk.get("src"):
                orig = blk["src"]
                if orig in downloaded:
                    blk["src"] = downloaded[orig]
                    continue
                ext = Path(orig).suffix.lower()
                ext = ext if ext in (".jpg", ".jpeg", ".png", ".webp") else ".jpg"
                local = f"assets/img/detail/{case_id}-inline-{inline_n}{ext}"
                if download(orig, ROOT / local):
                    blk["src"] = local
                    downloaded[orig] = local
                    inline_n += 1
                else:
                    blk["src"] = ""

    # иллюстрации вне текстовых секций: project-pic, pic-100 и прочие upload-картинки
    shots, seen = [], set()

    def add_shot(src, alt):
        if not src or src == main_pic or src in seen:
            return
        seen.add(src)
        if re.search(r"logo|icon|sprite", src, re.I) or src.startswith("data:"):
            return
        shots.append({"src": src, "alt": htmllib.unescape(alt).strip() or data["title"]})

    for sec in re.finditer(r'<section class="section section-(?:project-pic|pic-100)">(.*?)<section class="section', main, re.DOTALL):
        for im in re.finditer(r'<img[^>]+src="([^"]+)"[^>]*?(?:alt="([^"]*)")?[^>]*>', sec.group(1)):
            add_shot(im.group(1), im.group(2) or "")

    style_starts = [m.start() for m in re.finditer(r'<section class="section section-project-style">', main)]
    style_ends = [main.find('<section class="section', s + 10) for s in style_starts]

    def in_style(pos):
        return any(s <= pos <= (e if e != -1 else len(main)) for s, e in zip(style_starts, style_ends))

    for im in re.finditer(r'<img[^>]+src="(/upload/[^"]+)"[^>]*?(?:alt="([^"]*)")?[^>]*>', main):
        if not in_style(im.start()):
            add_shot(im.group(1), im.group(2) or "")

    kept = []
    for i, sh in enumerate(shots[:8]):
        ext = Path(sh["src"]).suffix.lower()
        ext = ext if ext in (".jpg", ".jpeg", ".png", ".webp") else ".jpg"
        local = f"assets/img/detail/{case_id}-shot-{i}{ext}"
        if download(sh["src"], ROOT / local):
            kept.append({"src": local, "alt": sh["alt"]})
    data["shots"] = kept
    return data


def main():
    """Без аргументов — пересобрать все кейсы. С id кейсов — обновить только их,
    остальные данные и подобранные обложки сохраняются."""
    only = set(sys.argv[1:])
    data_file = ROOT / "tools" / "cases_data.json"
    if only:
        result = json.loads(data_file.read_text(encoding="utf-8")) if data_file.exists() else {}
    else:
        result = {}
    for cid, (slug, *_rest) in CASE_MAP.items():
        if only and cid not in only:
            continue
        d = extract_case(cid, slug)
        result[cid] = d
        print(f'{cid}: tile={"Y" if d["tile"] else "N"} shots={len(d["shots"])} points={len(d["points"])} team={len(d["team"])} dur={d["duration"]!r} secs={len(d["sections"])}')

    unknown = only - set(CASE_MAP)
    assert not unknown, f"неизвестные id: {unknown}"
    data_file.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print("saved tools/cases_data.json")


if __name__ == "__main__":
    main()
