# -*- coding: utf-8 -*-
"""Генератор страниц подуслуг на основе service-corporate-sites.html.

Контент страницы описывается словарем CONTENT (см. внизу).
Запуск: python tools/build-subpage.py <slug>
"""
import io
import json
import re
import sys
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "service-corporate-sites.html"

_spec = importlib.util.spec_from_file_location(
    "subpage_content_sites", Path(__file__).parent / "subpage_content_sites.py"
)
_content_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_content_mod)

_spec_steps = importlib.util.spec_from_file_location(
    "subpage_steps_sites", Path(__file__).parent / "subpage_steps_sites.py"
)
_steps_mod = importlib.util.module_from_spec(_spec_steps)
_spec_steps.loader.exec_module(_steps_mod)

STAMP = """                <span class="problem-row__stamp" aria-hidden="true">
                  <svg class="icon icon--gradient"><use href="#icon-check" /></svg>
                  <span class="problem-row__stamp-text">Решим</span>
                </span>"""


def build_problems(problems):
    rows = []
    for i, (keyword, desc) in enumerate(problems, 1):
        rows.append(
            f"""              <li class="problem-row">
                <span class="problem-row__keyword">{keyword}</span>
                <p class="problem-row__desc">{desc}</p>
{STAMP}
              </li>"""
        )
    return "\n".join(rows)


def build_steps(steps):
    rows = []
    for i, (title, text, result) in enumerate(steps, 1):
        rows.append(
            f"""              <li class="process-step">
                <span class="process-step__number" aria-hidden="true">{i:02d}</span>
                <div class="process-step__body">
                  <h3 class="process-step__title">{title}</h3>
                  <p class="process-step__text">{text}</p>
                </div>
                <div class="process-step__result">
                  <span class="process-step__result-label">Вы получаете</span>
                  <p class="process-step__result-text">{result}</p>
                </div>
              </li>"""
        )
    return "\n".join(rows)


def build_audience(audiences):
    tabs, panels = [], []
    for i, (tab, title_dark, title_line, desc) in enumerate(audiences, 1):
        active = i == 1
        tab_cls = "audience-tab glow-card is-active" if active else "audience-tab glow-card"
        sel = "true" if active else "false"
        tabindex = "" if active else ' tabindex="-1"'
        tabs.append(
            f"""                <button class="{tab_cls}" type="button" role="tab" id="aud-tab-{i}" aria-selected="{sel}" aria-controls="aud-panel-{i}"{tabindex}>
                  <span class="audience-tab__text">{tab}</span>
                </button>"""
        )
        panel_cls = "audience-panel glow-card is-active" if active else "audience-panel glow-card"
        panels.append(
            f"""                <div class="{panel_cls}" role="tabpanel" id="aud-panel-{i}" aria-labelledby="aud-tab-{i}">
                  <img class="audience-panel__art" src="assets/img/audience-wave.png" alt="" aria-hidden="true" loading="lazy" />
                  <h3 class="audience-panel__title">{title_dark} <span class="audience-panel__line audience-panel__muted">{title_line}</span></h3>
                  <p class="audience-panel__text">{desc}</p>
                </div>"""
        )
    return (
        '<div class="audience-picker" data-audience-picker data-reveal>\n'
        '              <div class="audience-picker__list" role="tablist" aria-label="Аудитории">\n'
        + "\n".join(tabs)
        + '\n              </div>\n              <div class="audience-picker__panels">\n'
        + "\n".join(panels)
        + "\n              </div>\n            </div>"
    )


def build_related(items, self_slug):
    links = []
    for name, slug in items:
        if slug == self_slug:
            continue
        links.append(f'            <li><a class="related__link" href="{slug}.html">{name}</a></li>')
    return (
        '<section class="related" aria-labelledby="related-title">\n'
        "        <div class=\"container\">\n"
        '          <h2 class="section-title" data-reveal id="related-title">\n'
        '            Другие <span class="section-title__muted">услуги направления</span>\n'
        "          </h2>\n"
        '          <ul class="related__list" data-reveal-stagger>\n'
        + "\n".join(links)
        + "\n          </ul>\n        </div>\n      </section>"
    )


def replace_one(s, old, new, label):
    count = s.count(old)
    assert count == 1, f"{label}: found {count} occurrences"
    return s.replace(old, new)


def generate(slug, c):
    s = io.open(TEMPLATE, encoding="utf-8").read()

    # Шапка: title, описание, JSON-LD
    s = replace_one(s, "<title>Разработка корпоративных сайтов — цена от 195 000 ₽ | Итач-софт</title>", f"<title>{c['title']}</title>", "title")
    s = replace_one(
        s,
        '<meta name="description" content="Разработка корпоративных сайтов под ключ: представление компании, каталог услуг, заявки и интеграции с CRM. От 195 000 ₽ на шаблоне, от 450 000 ₽ индивидуально, запуск от 3 недель, гарантия до 24 месяцев." />',
        f'<meta name="description" content="{c["meta_desc"]}" />', "meta description")
    s = replace_one(s, '"name": "Разработка корпоративных сайтов",', f'"name": "{c["service_name"]}",', "jsonld name")
    s = replace_one(s, '{ "@type": "Offer", "name": "Корпоративный сайт на готовом шаблоне", "priceSpecification": { "@type": "PriceSpecification", "priceCurrency": "RUB", "minPrice": 195000 } },',
                    f'{c["jsonld_offer1"]},', "jsonld offer1")
    s = replace_one(s, '{ "@type": "Offer", "name": "Корпоративный сайт — индивидуальная разработка", "priceSpecification": { "@type": "PriceSpecification", "priceCurrency": "RUB", "minPrice": 450000 } }',
                    c["jsonld_offer2"], "jsonld offer2")

    faq_jsonld_old = None  # якоря — в функциях faq_jsonld_q / faq_jsonld_a ниже
    for i, (q, a) in enumerate(c["faq"]):
        s = replace_one(s, faq_jsonld_q(i), f'"name": "{q}"', f"jsonld faq q{i+1}")
        s = replace_one(s, faq_jsonld_a(i), f'"acceptedAnswer": {{ "@type": "Answer", "text": "{a}" }}', f"jsonld faq a{i+1}")

    # Хлебные крошки, заголовок, лид
    s = replace_one(s, '<span class="breadcrumbs__current" aria-current="page">Корпоративные сайты</span>',
                    f'<span class="breadcrumbs__current" aria-current="page">{c["short_name"]}</span>', "breadcrumb")
    s = replace_one(s, 'Корпоративные сайты <span class="section-title__muted">для бизнеса</span>',
                    c["h1"], "h1")
    s = replace_one(s, "Разрабатываем корпоративные сайты, которые представляют компанию и превращают посетителей в заявки. Структура, дизайн, интеграции с CRM и поддержка после запуска. Фиксированная смета и сроки в договоре.",
                    c["lead"], "lead")

    # Статистика
    for old_v, old_t, new_v, new_t in c["stats"]:
        s = replace_one(s, f'<span class="page-stat__value">{old_v}</span>', f'<span class="page-stat__value">{new_v}</span>', f"stat {old_v}")
        s = replace_one(s, f'<p class="page-stat__text">{old_t}</p>', f'<p class="page-stat__text">{new_t}</p>', f"stat text {old_t}")

    # Заявление
    s = replace_one(s, "Корпоративный сайт — лицо компании в интернете: он представляет бизнес, услуги и опыт, собирает заявки и работает на репутацию. Здесь клиент впервые знакомится с компанией, сравнивает предложения с конкурентами и решает, сотрудничать ли. Поэтому важно всё: структура, дизайн, скорость и удобство на любом устройстве. Мы создаём такие сайты под ключ — от прототипов и контента до интеграций с CRM и поддержки после запуска.",
                    c["statement"], "statement")

    # Проблемы: заменяем список целиком
    s = re.sub(r'(<ul class="problem-rows" data-problem-rows>).*?(</ul>)',
               lambda m: m.group(1) + "\n" + build_problems(c["problems"]) + "\n            " + m.group(2),
               s, count=1, flags=re.DOTALL)

    # Процесс: заменяем шаги целиком
    steps = c.get("steps") or _steps_mod.STEPS_SITES[slug]
    s = re.sub(r'(<ol class="process-steps" data-process-steps>).*?(</ol>)',
               lambda m: m.group(1) + "\n" + build_steps(steps) + "\n            " + m.group(2),
               s, count=1, flags=re.DOTALL)

    # Аудитории: заменяем пикер целиком (до закрытия секции)
    s = re.sub(r'<div class="audience-picker" data-audience-picker data-reveal>.*?\n        </section>',
               build_audience(c["audience"]) + "\n        </section>",
               s, count=1, flags=re.DOTALL)

    # Форматы
    s = replace_one(s, "Проверенная платформа, адаптация под бренд, базовые разделы и интеграции — быстрый старт без больших вложений.", c["format1_desc"], "format1 desc")
    s = replace_one(s, "Уникальный дизайн и сценарии под задачи бизнеса, сложная структура разделов, интеграции с CRM и учётными системами.", c["format2_desc"], "format2 desc")
    s = replace_one(s, '<span class="format-card__price-value">от 195 000 ₽</span>', f'<span class="format-card__price-value">{c["format1_price"]}</span>', "format1 price")
    s = replace_one(s, '<span class="format-card__price-value">от 450 000 ₽</span>', f'<span class="format-card__price-value">{c["format2_price"]}</span>', "format2 price")

    # Подпись у цены (например, «Стоимость тарифа» для поддержки)
    if c.get("price_label"):
        old_label = '<span class="format-card__price-label">Стоимость проекта</span>'
        assert s.count(old_label) == 2, "price label count"
        s = s.replace(old_label, f'<span class="format-card__price-label">{c["price_label"]}</span>')

    # FAQ (видимый)
    s = replace_one(s, 'Частые вопросы <span class="section-title__muted">о корпоративных сайтах</span>',
                    f'Частые вопросы <span class="section-title__muted">{c["faq_heading"]}</span>', "faq heading")
    faq_visible_old = [
        ("Какие функции выполняют корпоративные сайты?", "Корпоративный сайт представляет компанию, её услуги и опыт, собирает заявки и обращения, помогает клиентам и партнёрам найти нужную информацию. На сайте можно организовать онлайн-консультации, регистрацию на мероприятия, интеграцию с CRM и учётными системами — всё зависит от задач бизнеса."),
        ("Входит ли SEO в стоимость разработки?", "Базовая SEO-оптимизация входит: мета-теги, заголовки, семантическая разметка и скорость загрузки. Глубокое продвижение — работа с внешними ссылками, контент-маркетинг и анализ конкурентных позиций — заказывают отдельно."),
        ("Из каких этапов состоит разработка сайта?", "Проектирование, дизайн, вёрстка и программирование, тестирование, наполнение контентом и запуск. После запуска — поддержка и развитие сайта по согласованному плану."),
        ("Сколько времени занимает разработка корпоративного сайта?", "Сайт на готовом шаблоне запускаем от 3 недель, индивидуальная разработка занимает от 2 месяцев — зависит от объёма работ. Точные сроки фиксируем в договоре до старта."),
    ]
    for i, ((oq, oa), (q, a)) in enumerate(zip(faq_visible_old, c["faq"])):
        s = replace_one(s, f'<span class="faq__text">{oq}</span>', f'<span class="faq__text">{q}</span>', f"faq q{i+1}")
        s = replace_one(s, f'<div class="faq__answer-inner"><p>{oa}</p></div>', f'<div class="faq__answer-inner"><p>{a}</p></div>', f"faq a{i+1}")

    # Перелинковка
    s = re.sub(r'<section class="related" aria-labelledby="related-title">.*?\n      </section>(?=\n    </main>)',
               build_related(c["related"], slug), s, count=1, flags=re.DOTALL)

    out = ROOT / f"{slug}.html"
    io.open(out, "w", encoding="utf-8", newline="\n").write(s)
    print(f"built {out.name}")


def faq_jsonld_q(i):
    # Якоря из JSON-LD в <head> — они чуть отличаются от видимого FAQ
    return [
        '"name": "Какие функции выполняют корпоративные сайты?"',
        '"name": "Входит ли SEO в стоимость разработки?"',
        '"name": "Из каких этапов состоит разработка корпоративного сайта?"',
        '"name": "Сколько времени занимает разработка корпоративного сайта?"',
    ][i]


def faq_jsonld_a(i):
    return [
        '"acceptedAnswer": { "@type": "Answer", "text": "Корпоративный сайт представляет компанию, её услуги и опыт, собирает заявки и обращения, помогает клиентам и партнёрам найти нужную информацию. На сайте можно организовать онлайн-консультации, регистрацию на мероприятия, интеграцию с CRM и учётными системами." }',
        '"acceptedAnswer": { "@type": "Answer", "text": "Базовая SEO-оптимизация входит: мета-теги, заголовки, семантическая разметка и скорость загрузки. Глубокое продвижение — работа с внешними ссылками, контент-маркетинг и анализ конкурентных позиций — заказывают отдельно." }',
        '"acceptedAnswer": { "@type": "Answer", "text": "Анализ и техническое задание, проектирование, дизайн, вёрстка и программирование, тестирование, наполнение контентом и запуск. После запуска — поддержка и развитие сайта." }',
        '"acceptedAnswer": { "@type": "Answer", "text": "Сайт на готовом шаблоне запускаем от 3 недель, индивидуальная разработка занимает от 2 месяцев. Точные сроки фиксируем в договоре до старта работ." }',
    ][i]


# ---------------------------------------------------------------- контент ---
SITES_RELATED = [
    ("Интернет-магазины", "service-internet-magaziny"),
    ("Сайты-визитки", "service-sayty-vizitki"),
    ("Сайты на готовых шаблонах", "service-gotovye-shablony"),
    ("Лендинги", "service-lending"),
    ("Сайты государственных организаций", "service-gosudarstvennye"),
    ("Сайты на Битрикс", "service-sayty-na-bitriks"),
    ("Техническая поддержка сайтов", "service-podderzhka-saytov"),
    ("Доработка сайтов", "service-dorabotka-saytov"),
    ("Разработка веб-порталов", "service-veb-portaly"),
    ("Комплексный аудит сайта", "service-audit-sayta"),
    ("Разработка веб-дизайна", "service-veb-dizayn"),
    ("Разработка личного кабинета", "service-lichnyy-kabinet"),
    ("Приложения на React JS", "service-react-prilozheniya"),
    ("Интеграция 1С с сайтом", "service-integratsiya-1c"),
]

PAGES = {
    "service-internet-magaziny": {
        "title": "Разработка интернет-магазина — цена от 290 000 ₽ | Итач-софт",
        "meta_desc": "Разработка интернет-магазина под ключ: каталог, корзина, онлайн-оплата, доставка и интеграция с 1С. От 290 000 ₽ на готовом решении, от 650 000 ₽ индивидуально, запуск от 6 недель, гарантия до 24 месяцев.",
        "service_name": "Разработка интернет-магазина",
        "jsonld_offer1": '{ "@type": "Offer", "name": "Интернет-магазин на готовом решении", "priceSpecification": { "@type": "PriceSpecification", "priceCurrency": "RUB", "minPrice": 290000 } }',
        "jsonld_offer2": '{ "@type": "Offer", "name": "Интернет-магазин — индивидуальная разработка", "priceSpecification": { "@type": "PriceSpecification", "priceCurrency": "RUB", "minPrice": 650000 } }',
        "short_name": "Интернет-магазины",
        "h1": 'Интернет-магазины <span class="section-title__muted">для продаж онлайн</span>',
        "lead": "Разрабатываем интернет-магазины, которые продают круглосуточно: удобный каталог, корзина, онлайн-оплата и доставка, обмен с 1С и CRM. Заказы попадают в учётную систему автоматически. Фиксированная смета и сроки в договоре.",
        "stats": [
            ("от 195 000 ₽", "стоимость на шаблоне", "от 290 000 ₽", "стоимость на готовом решении"),
            ("от 3", "недель запуск на шаблоне", "от 6", "недель запуск на готовом решении"),
            ("до 24", "месяцев гарантии на работы и поддержка", "до 24", "месяцев гарантии на работы и поддержка"),
        ],
        "statement": "Интернет-магазин — это продавец, который не устаёт и не ошибается: круглосуточно показывает товары, принимает заказы и оплату, передаёт заказы на склад и в учётную систему. Покупатель ждёт того же, что и в обычном магазине, — только быстрее и удобнее: найти товар за минуту, оплатить в два клика и следить за доставкой. Мы создаём такие магазины под ключ — от проектирования каталога до интеграции с 1С, оплаты и доставки.",
        "problems": [
            ("Продажи", "Товары есть, а онлайн-продаж почти нет — покупатели уходят к конкурентам"),
            ("Каталог", "Ассортимент большой, а найти и сравнить товары в нём сложно"),
            ("Оплата", "Оплатить заказ и оформить доставку без помощи менеджера невозможно"),
            ("Остатки", "Цены и наличие товаров на сайте не совпадают с тем, что есть на складе"),
            ("Время", "Заказы обрабатываются вручную: менеджеры дублируют данные в 1С"),
            ("Рост", "Магазин не выдерживает роста: не тянет трафик, каталог и новые категории"),
        ],
        "audience": [
            ("Розничным магазинам и сетям", "Розничные магазины", "и сети", "Вывести ассортимент в онлайн и собирать заказы круглосуточно — без увеличения штата"),
            ("Производителям и дистрибьюторам", "Производители", "и дистрибьюторы", "Продавать напрямую конечному покупателю: каталог, цены, заказы и аналитика в одном месте"),
            ("Оптовым компаниям", "Оптовые", "компании", "Организовать оптовые продажи онлайн: заявки, личные цены и документы без звонков и переписки"),
            ("Собственным брендам", "Собственные", "бренды", "Витрина бренда под полным контролем: ассортимент, цены и прямой контакт с покупателем"),
            ("Продавцам на маркетплейсах", "Продавцы на", "маркетплейсах", "Свой канал продаж рядом с маркетплейсами: повторные продажи и лояльная аудитория"),
            ("Новым игрокам e-commerce", "Выход", "в e-commerce", "Запустить онлайн-продажи с нуля — от аналитики ниши до первых заказов"),
        ],
        "format1_desc": "Проверенное решение для интернет-магазина: каталог, корзина, онлайн-оплата и доставка, базовый обмен с 1С — быстрый старт продаж без больших вложений.",
        "format2_desc": "Магазин под специфику бизнеса: уникальный дизайн, сложные сценарии покупки, интеграции с 1С, CRM, складами и службами доставки.",
        "format1_price": "от 290 000 ₽",
        "format2_price": "от 650 000 ₽",
        "faq_heading": "об интернет-магазинах",
        "faq": [
            ("Что входит в разработку интернет-магазина?", "Каталог с фильтрами и поиском, карточки товаров, корзина и оформление заказа, онлайн-оплата, обмен с 1С или другой учётной системой, подключение доставки и аналитики. Дополнительно — импорт товаров, обучение команды и поддержка после запуска."),
            ("Сколько стоит и сколько делается интернет-магазин?", "Магазин на готовом решении — от 290 000 ₽ и от 6 недель, индивидуальная разработка — от 650 000 ₽ и от 3 месяцев. Точную смету и сроки фиксируем в договоре до старта работ."),
            ("Как магазин будет работать с 1С?", "Настраиваем обмен: товары, цены и остатки подтягиваются из 1С на сайт, а заказы из магазина автоматически попадают в учётную систему. Обмен работает по расписанию или в реальном времени — зависит от задач бизнеса."),
            ("Можно ли подключить приём платежей и доставку?", "Да: подключаем приём платежей — карты, ЕРИП и другие способы — и службы доставки с расчётом стоимости на сайте. Покупатель оплачивает заказ и выбирает доставку без участия менеджера."),
        ],
        "related": SITES_RELATED,
    },
}

if __name__ == "__main__":
    PAGES.update(_content_mod.SITES_PAGES)
    slug = sys.argv[1]
    generate(slug, PAGES[slug])
