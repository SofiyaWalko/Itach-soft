# -*- coding: utf-8 -*-
"""Кейсы на странице «Интернет-магазины»: только магазинные.

Divan Boss и Розы.Бел — сохранённые ручные шаблоны (tools/templates-magaziny.html),
Miele, SelfieLab, SibiFood — собраны из itach.by (cases_data.json).
Корпоративные кейсы и шаблоны убираются.
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_bitrix24 as b  # noqa: E402  (main защищён __name__)

PAGE = b.ROOT / "service-internet-magaziny.html"
SAVED = b.ROOT / "tools" / "templates-magaziny.html"
html = PAGE.read_text(encoding="utf-8")
saved = SAVED.read_text(encoding="utf-8")

# SibiFood: «1 месяц на запуск проекта» — единица измерения остаётся в подписи
b.CASES_DATA["case-sibifood"]["duration"] = "1 месяц"

CARD = '''              <li class="case-card glow-card">
                <h3 class="case-card__title"><a class="case-card__link" href="{href}" data-detail-open="{cid}">{title}</a></h3>
                <span class="card-expand" aria-hidden="true"><svg class="icon icon--gradient"><use href="#icon-expand" /></svg></span>
                <img class="case-card__shot" src="{shot}" width="1440" height="940" alt="{alt}" loading="lazy" />
              </li>'''

def card(cid, title, alt, shot, href):
    return CARD.format(cid=cid, title=title, alt=alt, shot=shot, href=href)

cards = [
    card("site-divan", 'Divan Boss <span class="section-title__muted">интернет-магазин мебели</span>',
         "Интернет-магазин мебели Divan Boss", "assets/img/sites/divanboss.jpg",
         "https://itach-soft.ru/portfolio/razrabotka-internet-magazina-mebeli/"),
    card("site-rozy", 'Розы.Бел <span class="section-title__muted">интернет-магазин по доставке цветов</span>',
         "Интернет-магазин Розы.Бел", "assets/img/sites/rozy-bel.jpg",
         "https://itach-soft.ru/portfolio/razrabotka-sayta-rozy-bel/"),
] + [b.build_card(cid) for cid in ["case-miele", "case-selfielab", "case-sibifood"]]

start = html.index('<ul class="case-grid" data-reveal-stagger>') + len('<ul class="case-grid" data-reveal-stagger>')
end = html.index("</ul>", start)
html = html[:start] + "\n" + "\n".join(cards) + "\n            " + html[end:]

# --- шаблоны: Divan и Розы из сохранённого файла, три новых — из генератора
def saved_template(tid):
    m = re.search(rf'    <template id="detail-{tid}">.*?    </template>', saved, re.DOTALL)
    assert m, f"saved template {tid} not found"
    return m.group(0)

divan = saved_template("site-divan")
if "detail__bento" not in divan:
    # В сохранённом шаблоне Divan Boss нет бенто с цифрами — данные с itach.by
    divan_bento = (
        '      <div class="detail__bento">'
        '<div class="detail-tile detail-tile--stat glow-card"><p class="detail-tile__value">5</p>'
        '<p class="detail-tile__label">месяцев — длительность проекта</p></div>'
        '<div class="detail-tile detail-tile--stat glow-card"><p class="detail-tile__value">6</p>'
        '<p class="detail-tile__label">специалистов в команде</p>'
        '<ul class="detail-tile__list"><li>1 менеджер проекта</li><li>1 бизнес-аналитик</li>'
        '<li>1 дизайнер</li><li>1 frontend-разработчик</li><li>1 backend-разработчик</li>'
        '<li>1 тестировщик</li></ul></div></div>\n'
    )
    divan = divan.replace("<div class=\"detail__article\">", divan_bento + "<div class=\"detail__article\">", 1)

templates = [
    divan,
    saved_template("site-rozy"),
] + [b.build_template(cid, with_site=True) for cid in ["case-miele", "case-selfielab", "case-sibifood"]]

tpl_start = html.index("    <!-- Содержимое детальных окон кейсов")
tpl_end = html.index("  </body>")
html = (
    html[:tpl_start]
    + "    <!-- Содержимое детальных окон кейсов: тексты и ссылки взяты с itach.by -->\n"
    + "\n\n".join(templates)
    + "\n\n"
    + html[tpl_end:]
)

PAGE.write_text(html, encoding="utf-8")
print("magaziny cases:", len(cards), "cards,", len(templates), "templates")
