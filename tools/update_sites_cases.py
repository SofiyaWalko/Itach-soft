# -*- coding: utf-8 -*-
"""Кейсы по теме страницы на всех подстраницах направления «Сайты».

Каждая страница получает кейсы, соответствующие её услуге: визитки — компактные
сайты и промо-страницы, шаблоны — проекты на Aspro, поддержка/доработка —
сопровождение и доработки, порталы/кабинеты/React — веб-сервисы и кабинеты,
интеграция 1С — кейсы с обменом данными с 1С.

Карточки и детальные шаблоны: готовые свёрстанные дублируются как есть
(service-corporate-sites / service-sites / service-web-services / service-bitrix24),
новые собираются из itach.by (cases_data.json).
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_bitrix24 as b  # noqa: E402  (main защищён __name__)

# ---------------------------------------------------------------- данные ---
# короткие «служебные» абзацы из вёрстки itach.by («О проекте» и т.п.) не используем
for c in b.CASES_DATA.values():
    c["about"] = [a for a in c.get("about", []) if len(a.strip()) >= 25]

# длительности, которые не парсятся duration_stat, — приводим к короткой форме
b.CASES_DATA["case-avant-tekno"]["duration"] = "2 недели"
b.CASES_DATA["case-maksiznay"]["duration"] = "14 месяцев"
# сайт клиента на странице кейса не указан — адрес дал заказчик
b.CASES_DATA["case-avant-tekno"]["site"] = "https://avant.by/"
# сайты клиентов не указаны на страницах кейсов — домены проверены, оба отвечают
b.CASES_DATA["case-atrium"]["site"] = "https://atrium.by/"
b.CASES_DATA["case-bnb-bank"]["site"] = "https://bnb.by/"

# свёрстанные на новом сайте кейсы с других страниц — дублируем как есть
for src in ("service-corporate-sites.html", "service-sites.html", "service-web-services.html"):
    html = (b.ROOT / src).read_text(encoding="utf-8")
    for cid, parts in b.extract_existing(html).items():
        b.EXISTING.setdefault(cid, parts)

# --------------------------------------------------------------- маппинг ---
PAGES_CASES = {
    "service-sayty-vizitki": [
        "case-moto", "case-bgmu-professor", "case-smartopan",
        "case-bgmu-journal", "case-plyusagrokhim",
    ],
    "service-lending": [
        "case-moto", "case-bgmu-professor", "case-smartopan",
        "case-bgmu-journal", "case-plyusagrokhim",
    ],
    "service-gotovye-shablony": [
        "case-smartopan", "case-plyusagrokhim", "site-bellegprom", "case-miele", "case-avant-tekno",
    ],
    "service-gosudarstvennye": [
        "site-bgmu", "case-bgmu-professor", "case-bgmu-journal",
        "site-bellegprom", "case-vnedr-int",
    ],
    "service-sayty-na-bitriks": [
        "site-bgmu", "case-sberlizing", "site-bellegprom", "site-losbel", "case-smartopan",
    ],
    "service-podderzhka-saytov": [
        "case-atrium", "case-a100-support", "case-gadzhettreyd", "case-avant-tekno", "case-bnb-bank",
    ],
    "service-dorabotka-saytov": [
        "case-rival", "case-bnb-bank", "case-gadzhettreyd", "case-avant-tekno", "case-a100-support",
    ],
    "service-veb-dizayn": [
        "site-rozy", "site-autogroup", "case-sibifood", "case-selfielab", "case-sberlizing",
    ],
    "service-audit-sayta": [
        "case-avant-tekno", "case-rival", "case-sibifood", "case-sberlizing", "case-atrium",
    ],
    "service-veb-portaly": [
        "case-maksiznay", "case-maximus", "case-b2b-kabinet", "case-dodoma", "case-erip",
    ],
    "service-lichnyy-kabinet": [
        "case-autolight-kabinet", "case-dodoma", "case-b2b-kabinet", "case-maksiznay", "case-a100",
    ],
    "service-react-prilozheniya": [
        "case-maksiznay", "case-maximus", "case-a100", "case-dodoma", "case-b2b-kabinet",
    ],
    "service-integratsiya-1c": [
        "site-divan", "case-autolight-kabinet", "case-dodoma", "case-sibifood", "case-mebel",
    ],
}

# ---------------------------------------------------------------- замена ---
for slug, cids in PAGES_CASES.items():
    page = b.ROOT / f"{slug}.html"
    html = page.read_text(encoding="utf-8")

    cards = [b.build_card(cid) for cid in cids]
    start = html.index('<ul class="case-grid" data-reveal-stagger>') + len('<ul class="case-grid" data-reveal-stagger>')
    end = html.index("</ul>", start)
    html = html[:start] + "\n" + "\n".join(cards) + "\n            " + html[end:]

    templates = [b.build_template(cid, with_site=True) for cid in cids]
    tpl_start = html.index("    <!-- Содержимое детальных окон кейсов")
    tpl_end = html.index("  </body>")
    html = (
        html[:tpl_start]
        + "    <!-- Содержимое детальных окон кейсов: тексты и ссылки взяты с itach.by -->\n"
        + "\n\n".join(templates)
        + "\n\n"
        + html[tpl_end:]
    )

    page.write_text(html, encoding="utf-8")
    print(f"{slug}: {len(cards)} кейсов — {', '.join(cids)}")
