# -*- coding: utf-8 -*-
"""Генератор 3 подстраниц направления «Разработка веб-сервисов».

Шаблон — service-web-services.html: каркас (шапка, клиенты, калькулятор,
команда, технологии, награды, отзывы, форма, футер) копируется, уникальные
блоки (hero, цифры, проблемы, кейсы, форматы, процесс, FAQ, перелинковка,
модалки кейсов) собираются из PAGES.

Запуск: python tools/build_web_services_subpages.py
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_bitrix24 as b  # noqa: E402  (main защищён __name__)

TEMPLATE = b.ROOT / "service-web-services.html"

# Свёрстанные кейсы и модалки со страницы направления дублируем как есть
b.EXISTING.update(b.extract_existing(TEMPLATE.read_text(encoding="utf-8")))


def replace_one(s, old, new, label):
    count = s.count(old)
    assert count == 1, f"{label}: найдено {count} вхождений"
    return s.replace(old, new)


# ---------------------------------------------------------------- блоки ---
def build_stats(stats):
    rows = []
    for i, (value, text) in enumerate(stats):
        rows.append(
            f"""            <li class="page-stat glow-card" style="--i: {i}">
              <span class="page-stat__value">{value}</span>
              <p class="page-stat__text">{text}</p>
            </li>"""
        )
    return (
        '          <ul class="page-stats page-stats--tall" data-reveal-stagger>\n'
        + "\n".join(rows)
        + "\n          </ul>"
    )


def build_problems(problems):
    rows = []
    for keyword, desc in problems:
        rows.append(
            f"""              <li class="problem-row">
                <span class="problem-row__keyword">{keyword}</span>
                <p class="problem-row__desc">{desc}</p>
                <span class="problem-row__stamp" aria-hidden="true">
                  <svg class="icon icon--gradient"><use href="#icon-check" /></svg>
                  <span class="problem-row__stamp-text">Решим</span>
                </span>
              </li>"""
        )
    return "\n".join(rows)


def build_problems_section(problems):
    """Блок «Проблемы, которые решаем» — как на страницах Битрикс24."""
    return (
        '        <!-- Проблемы строками: ключевое слово слева серым, описание по центру,\n'
        '             справа — штамп «Решим». Каждая строка всплывает по мере скролла -->\n'
        '        <section class="problems" aria-labelledby="problems-title">\n'
        '          <div class="container">\n'
        '            <h2 class="section-title" data-reveal id="problems-title">\n'
        '              Проблемы, которые <span class="section-title__muted">решаем</span>\n'
        '            </h2>\n'
        '            <ul class="problem-rows" data-problem-rows>\n'
        + build_problems(problems)
        + "\n            </ul>\n"
        "          </div>\n"
        "        </section>"
    )


def build_why_section(items):
    """«Почему нам доверяют»: карточки с загнутым уголком (раскрытие — CSS)."""
    cards = []
    for title, text, facts in items:
        facts_html = "".join(f'<li class="why-card__fact">{fact}</li>' for fact in facts)
        cards.append(
            f"""              <article class="why-card" tabindex="0">
                <div class="why-card__body">
                  <h3 class="why-card__title">{title}</h3>
                  <p class="why-card__text">{text}</p>
                </div>
                <span class="why-card__sheet" aria-hidden="true"></span>
                <ul class="why-card__facts">{facts_html}</ul>
                <span class="why-card__fold" aria-hidden="true"></span>
              </article>"""
        )
    return (
        '        <!-- Почему нам доверяют: карточки с отворотом, раскрывается на наведении -->\n'
        '        <section class="why" id="why" aria-labelledby="why-title">\n'
        '          <div class="container">\n'
        '            <h2 class="section-title" data-reveal id="why-title">\n'
        '              Почему нам <span class="section-title__muted">доверяют</span>\n'
        "            </h2>\n"
        '            <div class="why__scroller">\n'
        '              <div class="why-cards" data-reveal-stagger>\n'
        + "\n".join(cards)
        + "\n              </div>\n            </div>\n          </div>\n        </section>"
    )


def build_methods_section(methods):
    """«Какие способы интеграции существуют» — табы по методам, как «Ключевые
    инструменты внедрения»: под каждым табом карточки с механизмами метода."""
    tabs = []
    panels = []
    for i, (label, cards) in enumerate(methods, 1):
        active = " is-active" if i == 1 else ""
        selected = "true" if i == 1 else "false"
        tabindex = "" if i == 1 else ' tabindex="-1"'
        tabs.append(
            f"""                <button class="tools-tab{active}" type="button" role="tab" id="methods-tab-{i}" aria-selected="{selected}" aria-controls="methods-panel-{i}"{tabindex}>
                  <span>{label}</span>
                </button>"""
        )
        items = []
        for head, muted, text in cards:
            items.append(
                f"""                  <li class="tools-item glow-card"><h3 class="tools-item__name">{head} <span class='section-title__muted'>{muted}</span></h3><p class="tools-item__text">{text}</p></li>"""
            )
        panels.append(
            f"""              <div class="tools-panel{active}" role="tabpanel" id="methods-panel-{i}" aria-labelledby="methods-tab-{i}">
                <ul class="tools-list">
{chr(10).join(items)}
                </ul>
              </div>"""
        )
    return (
        '        <!-- Способы интеграции: табы по методам, под ними — карточки с механизмами -->\n'
        '        <section class="tools" aria-labelledby="methods-title">\n'
        '          <div class="container">\n'
        '            <h2 class="section-title" data-reveal id="methods-title">\n'
        "              Какие способы интеграции <span class=\"section-title__muted\">приложений существуют?</span>\n"
        "            </h2>\n"
        '            <div class="tools-picker" data-tools-picker data-no-hover-switch data-reveal>\n'
        '              <div class="tools-tabs" role="tablist" aria-label="Способы интеграции">\n'
        + "\n".join(tabs)
        + "\n              </div>\n"
        '              <div class="tools-panels">\n'
        + "\n".join(panels)
        + "\n              </div>\n"
        "            </div>\n"
        '            <div class="section-action" data-reveal>\n'
        '              <a class="btn btn--outline" href="#lead">Обсудить интеграцию</a>\n'
        "            </div>\n"
        "          </div>\n"
        "        </section>"
    )


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


def build_formats(formats, price_label):
    cards = []
    for title, desc, price in formats:
        cards.append(
            f"""              <li class="format-card format-card--static glow-card">
                <div class="format-card__link">
                  <h3 class="format-card__title">{title}</h3>
                  <p class="format-card__desc">{desc}</p>
                  <ul class="format-card__prices">
                  <li class="format-card__price">
                    <span class="format-card__price-label">{price_label}</span>
                    <span class="format-card__price-value">{price}</span>
                  </li>
                  </ul>
                </div>
              </li>"""
        )
    return "\n".join(cards)


def build_faq(faq):
    items = []
    for i, (q, a) in enumerate(faq, 1):
        items.append(
            f"""              <li class="faq__item glow-card">
                <h3 class="faq__question">
                  <button class="faq__trigger" type="button" id="faq-q{i}" aria-expanded="false" aria-controls="faq-a{i}">
                    <span class="faq__text">{q}</span>
                    <span class="faq__toggle" aria-hidden="true"></span>
                  </button>
                </h3>
                <div class="faq__answer" id="faq-a{i}" role="region" aria-labelledby="faq-q{i}">
                  <div class="faq__answer-inner"><p>{a}</p></div>
                </div>
              </li>"""
        )
    return "\n".join(items)


def build_related(items, self_slug):
    links = []
    for name, slug in items:
        if slug == self_slug:
            continue
        links.append(f'            <li><a class="related__link" href="{slug}.html">{name}</a></li>')
    return "\n".join(links)


def build_service_jsonld(name, offers):
    offers_json = ",\n".join(
        f"""        {{
          "@type": "Offer",
          "name": "{offer_name}",
          "priceSpecification": {{
            "@type": "PriceSpecification",
            "priceCurrency": "RUB",
            "minPrice": {price}
          }}
        }}"""
        for offer_name, price in offers
    )
    return f"""    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "Service",
      "name": "{name}",
      "provider": {{
        "@type": "Organization",
        "name": "Итач-софт",
        "url": "https://itach-soft.ru"
      }},
      "areaServed": [
        "RU",
        "BY"
      ],
      "offers": [
{offers_json}
      ]
    }}
    </script>"""


def build_faq_jsonld(faq):
    questions = ",\n".join(
        """        {
          "@type": "Question",
          "name": "%s",
          "acceptedAnswer": { "@type": "Answer", "text": "%s" }
        }""" % (q, a)
        for q, a in faq
    )
    return f"""    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": [
{questions}
      ]
    }}
    </script>"""


# ---------------------------------------------------------------- контент ---
WS_RELATED = [
    ("Разработка веб-сервисов под ключ", "service-web-services"),
    ("Разработка веб-сервисов с нуля", "service-web-services-s-nulya"),
    ("Интеграция сложных систем", "service-web-services-integratsiya"),
    ("Техническая поддержка ПО", "service-web-services-podderzhka"),
    ("Приложения на React JS", "service-react-prilozheniya"),
    ("Разработка личного кабинета", "service-lichnyy-kabinet"),
]

PAGES = {
    "service-web-services-s-nulya": {
        "title": "Разработка веб-сервисов с нуля — от 600 000 ₽ | Итач-софт",
        "meta_desc": "Разработка веб-сервисов с нуля: аналитика, прототипы, дизайн, backend и frontend, интеграции, тестирование и запуск. Личные кабинеты, B2B-платформы, образовательные сервисы. От 600 000 ₽.",
        "service_name": "Разработка веб-сервисов с нуля",
        "short_name": "Веб-сервисы с нуля",
        "offers": [("Разработка веб-сервиса под ключ", 600000)],
        "h1": 'Разработка веб-сервисов <span class="section-title__muted">с нуля</span>',
        "lead": "Проектируем и разрабатываем веб-сервисы под задачи бизнеса: от аналитики и прототипов до запуска и развития. Личные кабинеты, B2B-платформы, образовательные сервисы и внутренние системы — с архитектурой под рост.",
        "problems": [
            ("Процессы", "Рутина держится на Excel и переписке: процессы не масштабируются"),
            ("Готовые решения", "Типовое ПО не закрывает специфику бизнеса, а доработки превращаются в самопис"),
            ("Данные", "Информация разбросана по системам и файлам — единой картины нет"),
            ("Клиенты", "Клиентам негде самостоятельно оформить заказ, заявку или документы"),
            ("Нагрузка", "Сервис не тянет рост пользователей и объём данных"),
            ("Развитие", "Каждая доработка затягивается: архитектура и код мешают расти"),
        ],
        "stats": [
            ("от 600 000 ₽", "стоимость разработки"),
            ("от 2", "месяцев запуск сервиса"),
            ("до 24", "месяцев гарантия на работы"),
        ],
        "cases": ["case-b2b-kabinet", "case-maksiznay", "case-maximus", "case-dodoma", "case-a100"],
        "cases_heading": "разработки",
        "why": [
            ("Индивидуальный подход", "Функционал проектируем от задач бизнеса, а не от готовых модулей.", ["Гибко", "Точно", "Под вас"]),
            ("Полный цикл разработки", "Аналитика, дизайн, разработка и запуск — в одной команде.", ["Аналитика", "Дизайн", "Запуск"]),
            ("Экспертная команда", "Более 1 000 000 часов разработки — от MVP до нагруженных систем.", ["Опыт", "Сертификаты", "Практика"]),
            ("Современный стек", "Актуальные технологии и проверенные практики разработки.", ["Быстро", "Стабильно", "Безопасно"]),
            ("Масштабирование", "Архитектура с запасом: нагрузка и модули подключаются без переделки.", ["Модульно", "С запасом", "Без переделок"]),
            ("Поддержка после запуска", "Мониторинг, обновления и реакция по SLA, гарантия до 24 месяцев.", ["SLA", "Мониторинг", "Гарантия"]),
        ],
        "formats": [
            ("Сервис под ключ", "Аналитика, прототипы, дизайн, backend и frontend, интеграции, тестирование и запуск — от 2 месяцев.", "от 600 000 ₽"),
            ("Платформа с развитием", "Роли и права, обмен данными, отказоустойчивость, новые модули и развитие после запуска — смета по проекту.", "по проекту"),
        ],
        "price_label": "Стоимость проекта",
        "process": [
            ("Аналитика и ТЗ", "Определяем цели и задачи, изучаем аудиторию и конкурентов, собираем требования и фиксируем объём работ в техническом задании.", "ТЗ и смета проекта"),
            ("Проектирование", "Проектируем архитектуру сервиса, пользовательские сценарии и прототипы, структуру базы данных и функциональные модули.", "Архитектура и прототип"),
            ("Дизайн", "Разрабатываем визуальную концепцию и макеты ключевых экранов — с состояниями и адаптивом под все устройства.", "Макеты интерфейса"),
            ("Разработка", "Настраиваем серверное окружение, пишем backend и frontend, подключаем сторонние API и сервисы.", "Работающий сервис"),
            ("Тестирование и запуск", "Проверяем функциональность, производительность и безопасность, разворачиваем сервис и подключаем мониторинг.", "Запущенный сервис и поддержка"),
        ],
        "faq_heading": "о разработке сервисов",
        "faq": [
            ("В каком порядке идёт работа над сервисом?", "Последовательно: анализ требований, проектирование и прототипы, дизайн, разработка, тестирование, развёртывание и запуск. После запуска — поддержка и развитие по согласованному плану."),
            ("Что входит в разработку с нуля?", "Анализ целей и аудитории, техническое задание, архитектура, прототипы, дизайн, backend и frontend, интеграции с внешними API, тестирование, развёртывание и сопровождение после запуска."),
            ("Сколько стоит и сколько занимает разработка?", "Разработка сервиса — от 600 000 ₽, запуск — от 2 месяцев. Стоимость зависит от объёма функционала, интеграций и требований к нагрузке. Предварительную оценку даём бесплатно."),
            ("Что нужно, чтобы начать?", "Описание задачи и целей, целевой аудитории и желаемых сроков. Остальное — архитектуру, прототипы, дизайн и оценку — берём на себя и согласовываем с вами до старта разработки."),
            ("Что происходит после запуска?", "Передаём документацию, обучаем команду и остаёмся на связи по гарантии до 24 месяцев. Дальше — поддержка по SLA и развитие функционала итерациями."),
        ],
    },

    "service-web-services-integratsiya": {
        "title": "Интеграция сложных систем — от 300 000 ₽ | Итач-софт",
        "meta_desc": "Интеграция бизнес-систем: CRM, ERP, 1С, склад, платежи. API, REST и SOAP, файловый обмен, шина данных. Анализ, архитектура, разработка, запуск и поддержка. От 300 000 ₽.",
        "service_name": "Интеграция сложных систем",
        "short_name": "Интеграция систем",
        "offers": [("Интеграция сложных систем", 300000)],
        "h1": 'Интеграция <span class="section-title__muted">сложных систем</span>',
        "lead": "Связываем CRM, ERP, 1С, складские и платёжные системы в единую цифровую среду: обмен данными без ручного переноса, дублей и ошибок. Проектируем архитектуру интеграции и сопровождаем её после запуска.",
        "problems": [
            ("Ручной перенос", "Данные дублируются вручную между системами — медленно и с ошибками"),
            ("Расхождения", "Цены, остатки и статусы в системах не совпадают"),
            ("Разрозненность", "CRM, 1С и склад живут отдельно: единой картины нет"),
            ("Ошибки", "Ручной ввод приводит к ошибкам в заказах и документах"),
            ("Скорость", "Обмен данными занимает часы и дни — решения принимаются вслепую"),
            ("Контроль", "Непонятно, что и когда синхронизировалось и почему обмен встал"),
        ],
        "stats": [
            ("от 300 000 ₽", "стоимость интеграции"),
            ("от 1", "месяца запуск обмена"),
            ("до 24", "месяцев гарантия на работы"),
        ],
        "cases": ["case-b2b-kabinet", "case-dodoma", "case-santa", "case-maximus-int", "case-telefonia"],
        "cases_heading": "интеграций",
        "formats": [
            ("Интеграция под ключ", "Анализ систем, архитектура обмена, разработка и тестирование, подключение и запуск — от 1 месяца.", "от 300 000 ₽"),
            ("Сложная архитектура", "Несколько систем, шина данных, высокие нагрузки и развитие обмена без остановки процессов — смета по проекту.", "по проекту"),
        ],
        "methods": [
            (
                "API-интеграция",
                [
                    ("Обмен в", "реальном времени", "Приложения общаются через открытые интерфейсы и передают данные сразу, как только они изменились. Остатки, цены, заказы и статусы остаются актуальными в обеих системах."),
                    ("Двусторонняя", "синхронизация", "Изменения из одной системы сразу появляются в другой: сотрудникам не нужно переносить данные вручную и проверять, где сейчас актуальная версия записи."),
                    ("Сложные", "сценарии", "Из отдельных API-запросов собираются логические цепочки: заказ с сайта, проверка остатка, счёт, оплата и заявка на доставку запускаются автоматически."),
                ],
            ),
            (
                "REST и SOAP",
                [
                    ("Обмен", "по REST", "Лёгкий обмен по HTTP с понятной структурой запросов — стандарт для облачных сервисов, мобильных приложений и современных платформ."),
                    ("Обмен", "по SOAP", "Строгий протокол с формальным контрактом и встроенной обработкой ошибок — для корпоративных систем с высокими требованиями к надёжности и безопасности."),
                    ("Внешние", "системы", "Веб-службы связывают ваш контур с сервисами партнёров и платформами, к которым нет прямого доступа: обмен идёт по стандартизированному протоколу."),
                ],
            ),
            (
                "Файловый обмен",
                [
                    ("Обмен", "по расписанию", "Данные передаются партиями по заданному графику — для больших выгрузок и сценариев без мгновенной реакции: ночные сверки, реестры платежей, отчёты."),
                    ("CSV", "и таблицы", "Простой и универсальный формат для выгрузок из бухгалтерских систем, реестров и обмена с подрядчиками, маркетплейсами и банками."),
                    ("XML", "и JSON", "Структурированные форматы для обмена документами со вложенной структурой: заказами, накладными, каталогами и данными справочников."),
                ],
            ),
            (
                "Шина данных",
                [
                    ("Маршрутизация", "запросов", "Шина становится единой точкой входа и сама определяет, какая система получит данные и в каком порядке, — вместо десятка прямых связей между системами."),
                    ("Трансформация", "данных", "Форматы и справочники разных систем приводятся к единому виду: шина преобразует структуру данных, а не требует переделки каждой системы."),
                    ("Контроль", "потоков", "Все обмены проходят через одно место: видно, что и когда передано и где возникла ошибка, а повторная отправка не создаёт дублей."),
                ],
            ),
            (
                "Базы данных",
                [
                    ("Общие", "хранилища", "Системы читают данные из одного хранилища и работают с единым информационным полем — без промежуточных выгрузок и файлов."),
                    ("Реплики", "и срезы", "Данные копируются в отдельную реплику: отчёты и аналитика не нагружают рабочую базу, а актуальный срез всегда доступен для чтения."),
                    ("Аналитика", "и отчётность", "Когда нужна единая картина по всем системам, данные собираются в хранилище, где по ним строятся отчёты и дашборды."),
                ],
            ),
        ],
        "price_label": "Стоимость проекта",
        "process": [
            ("Анализ систем", "Изучаем ИТ-инфраструктуру, определяем точки обмена, ограничения систем и бизнес-требования к данным.", "Карта интеграции и ТЗ"),
            ("Проектирование обмена", "Выбираем технологии — API, REST и SOAP, файловый обмен или шина данных — и проектируем логику обработки.", "Схема интеграции"),
            ("Разработка и тестирование", "Разрабатываем модули, настраиваем каналы передачи данных, проверяем безопасность и стабильность обмена.", "Проверенная интеграция"),
            ("Внедрение", "Подключаем обмен к рабочей инфраструктуре и синхронизируем данные — с минимальным влиянием на текущие процессы.", "Работающий обмен данными"),
            ("Поддержка и развитие", "Мониторим обмен, оптимизируем нагрузку и добавляем новые сценарии по мере роста бизнеса.", "Стабильный обмен и развитие"),
        ],
        "faq_heading": "об интеграции систем",
        "faq": [
            ("Почему важна интеграция систем?", "Она объединяет разрозненные приложения, автоматизирует передачу данных и убирает ручной перенос. Бизнес получает единую картину, меньше ошибок и быстрее принимает решения."),
            ("Сколько времени занимает интеграция?", "Простые обмены — от нескольких недель, крупные проекты с несколькими системами — месяцы. Точные сроки определяем после аудита систем и согласования архитектуры."),
            ("Можно ли расширять интеграцию после внедрения?", "Да: добавляем новые сервисы и сценарии, меняем логику обмена и увеличиваем объёмы данных без остановки рабочих процессов. Архитектуру закладываем с запасом."),
            ("Что влияет на сложность интеграции?", "Количество систем и их технические ограничения, наличие API, объёмы и скорость обмена, требования безопасности и степень несогласованности данных."),
            ("Насколько безопасен обмен данными?", "Используем защищённые протоколы и шифрование, многоуровневую аутентификацию, контроль доступа, журналирование операций и мониторинг обмена."),
        ],
    },

    "service-web-services-podderzhka": {
        "title": "Техническая поддержка ПО — от 9 000 ₽/мес | Итач-софт",
        "meta_desc": "Техническая поддержка ПО и веб-сервисов: мониторинг, обновления, устранение сбоев, консультации пользователей и доработки по SLA. Тарифы от 9 000 ₽/мес, режим 24/7.",
        "service_name": "Техническая поддержка ПО",
        "short_name": "Поддержка ПО",
        "offers": [("Техническая поддержка ПО — стандарт", 9000)],
        "h1": 'Техническая поддержка <span class="section-title__muted">ПО</span>',
        "lead": "Берём на сопровождение веб-сервисы и корпоративное ПО: мониторинг, обновления, устранение сбоев, консультации пользователей и доработки функционала. Работаем по SLA с фиксированным временем реакции — вплоть до режима 24/7.",
        "problems": [
            ("Сбои", "Сервис падает или работает медленно — и некому быстро починить"),
            ("Сопровождение", "Прежний подрядчик пропал: код, доступы и документация утеряны"),
            ("Обновления", "Версии не обновляются: уязвимости и несовместимость с окружением"),
            ("Правки", "Мелкая доработка висит неделями: некому внести изменения"),
            ("Мониторинг", "Об инцидентах узнают от пользователей, а не от специалистов"),
            ("Развитие", "Новые функции не появляются: продукт стоит на месте"),
        ],
        "stats": [
            ("от 9 000 ₽", "стоимость поддержки в месяц"),
            ("до 1", "часа — реакция на критические ошибки"),
            ("24/7", "режим по договору"),
        ],
        "cases": ["case-e2e4", "case-atrium", "case-gadzhettreyd", "case-a100-support", "case-helix"],
        "cases_heading": "сопровождения",
        "formats": [
            ("Стандарт", "Мониторинг, обновления, консультации и устранение сбоев в рабочие часы, заявки в личном кабинете, реакция на критические ошибки до 6 часов.", "от 9 000 ₽/мес"),
            ("По SLA 24/7", "Круглосуточный режим, выделенная команда, включённые часы доработок и реакция на критические ошибки до 1 часа.", "по проекту"),
        ],
        "price_label": "Стоимость тарифа",
        "process": [
            ("Подключение и аудит", "Проводим аудит кода и инфраструктуры, собираем доступы и документацию, настраиваем мониторинг и регламент реакции.", "Аудит системы и подключённый тариф"),
            ("Мониторинг", "Следим за доступностью, производительностью и стабильностью сервиса — об инцидентах узнаём раньше пользователей.", "Стабильная работа системы"),
            ("Работы по тарифу", "Устанавливаем обновления, устраняем ошибки, консультируем пользователей и выполняем доработки в рамках часов тарифа.", "Выполненные задачи по графику"),
            ("Отчётность", "Ежемесячно отчитываемся о работах, инцидентах и состоянии системы и даём рекомендации по развитию.", "Прозрачная отчётность"),
            ("Развитие", "Оптимизируем производительность, добавляем функции и масштабируем систему по мере роста нагрузки.", "Продукт, который развивается"),
        ],
        "faq_heading": "о поддержке ПО",
        "faq": [
            ("Что входит в техническую поддержку ПО?", "Мониторинг состояния систем, установка обновлений, устранение ошибок и сбоев, консультации пользователей, диагностика производительности и работа с заявками. На тарифах с доработками — включённые часы на изменения."),
            ("Что будет, если не обновлять ПО?", "Растёт риск уязвимостей и сбоев, появляется несовместимость с новыми технологиями и снижается эффективность. В худшем случае — утечки данных, простои и репутационные потери."),
            ("Как быстро реагируете на сбои?", "Зависит от тарифа: критичные ошибки — от 6 часов в рабочее время до 1 часа на тарифе с SLA и круглосуточным режимом. Мониторинг фиксирует проблемы раньше пользователей."),
            ("Берёте ли на поддержку чужие проекты?", "Да: проводим аудит кода и инфраструктуры, восстанавливаем документацию и доступы, настраиваем мониторинг и берём систему на сопровождение."),
            ("Как устроены тарифы?", "Тарифы отличаются режимом работы, временем реакции и часами доработок — от стандартной поддержки в рабочие часы до круглосуточного сопровождения с выделенной командой. Тариф можно менять заранее."),
        ],
    },
}


def generate(slug, c):
    s = TEMPLATE.read_text(encoding="utf-8")

    # Шапка: title, описание, JSON-LD
    s = replace_one(
        s,
        "<title>Разработка веб-сервисов под ключ — от 600 000 ₽ | Итач-софт</title>",
        f"<title>{c['title']}</title>",
        "title",
    )
    s = replace_one(
        s,
        'content="Проектируем и разрабатываем веб-сервисы: автоматизация процессов, интеграция систем, личные кабинеты и порталы. От 600 000 ₽, гарантия до 24 месяцев."',
        f'content="{c["meta_desc"]}"',
        "meta description",
    )
    ld = list(re.finditer(r'    <script type="application/ld\+json">.*?</script>', s, re.DOTALL))
    assert len(ld) == 2, f"JSON-LD blocks: {len(ld)}"
    s = s[: ld[0].start()] + build_service_jsonld(c["service_name"], c["offers"]) + s[ld[0].end():]
    ld = list(re.finditer(r'    <script type="application/ld\+json">.*?</script>', s, re.DOTALL))
    s = s[: ld[1].start()] + build_faq_jsonld(c["faq"]) + s[ld[1].end():]

    # В подменю «Услуги» текущим разделом должен быть «Веб-сервисы»
    s = s.replace(
        '<a class="nav__submenu-link" href="service-sites.html" aria-current="page"><span>Сайты</span></a>',
        '<a class="nav__submenu-link" href="service-sites.html"><span>Сайты</span></a>',
    )
    s = s.replace(
        '<a class="nav__submenu-link" href="service-web-services.html"><span>Разработка веб-сервисов</span></a>',
        '<a class="nav__submenu-link" href="service-web-services.html" aria-current="page"><span>Разработка веб-сервисов</span></a>',
    )

    # Хлебные крошки: добавляем ссылку на страницу направления
    s = replace_one(
        s,
        '<span class="breadcrumbs__current" aria-current="page">Разработка веб-сервисов</span>',
        '<a class="breadcrumbs__link" href="service-web-services.html">Разработка веб-сервисов</a>\n'
        '            <svg class="icon breadcrumbs__sep" aria-hidden="true"><use href="#icon-chevron-down" /></svg>\n'
        f'            <span class="breadcrumbs__current" aria-current="page">{c["short_name"]}</span>',
        "breadcrumbs",
    )

    # H1 и лид
    s = replace_one(
        s,
        'Разработка веб-сервисов <span class="section-title__muted">под ключ</span>',
        c["h1"],
        "h1",
    )
    s = replace_one(
        s,
        "Проектируем и разрабатываем веб-сервисы, которые автоматизируют ключевые процессы и связывают данные из CRM, 1С и внутренних систем. Сопровождаем проект от идеи до поддержки.",
        c["lead"],
        "lead",
    )

    # Цифры
    s = re.sub(
        r'          <ul class="page-stats page-stats--tall" data-reveal-stagger>.*?</ul>',
        build_stats(c["stats"]),
        s,
        count=1,
        flags=re.DOTALL,
    )

    # Проблемы, которые решаем — только на подстраницах
    s = replace_one(
        s,
        '      <div class="service-sections">\n        <!-- 2. Кейсы -->',
        '      <div class="service-sections">\n'
        + build_problems_section(c["problems"])
        + "\n\n        <!-- 2. Кейсы -->",
        "problems insert",
    )

    # Кейсы
    s = replace_one(
        s,
        'Кейсы <span class="section-title__muted">разработки</span>',
        f'Кейсы <span class="section-title__muted">{c["cases_heading"]}</span>',
        "cases heading",
    )
    cards = [b.build_card(cid) for cid in c["cases"]]
    start = s.index('<ul class="case-grid" data-reveal-stagger>') + len('<ul class="case-grid" data-reveal-stagger>')
    end = s.index("</ul>", start)
    s = s[:start] + "\n" + "\n".join(cards) + "\n            " + s[end:]

    # «Почему нам доверяют» — после блока кейсов, только если задан
    if c.get("why"):
        s = replace_one(
            s,
            "        <!-- Услуги и стоимость -->",
            build_why_section(c["why"]) + "\n\n        <!-- Услуги и стоимость -->",
            "why insert",
        )

    # Форматы и стоимость
    s = replace_one(
        s,
        'Услуги и <span class="section-title__muted">стоимость</span>',
        'Форматы и <span class="section-title__muted">стоимость</span>',
        "formats title",
    )
    s = replace_one(
        s,
        "Выберите услугу — покажем ориентировочные цены. Точную смету фиксируем в договоре.",
        "Стоимость зависит от масштаба и задач. Точную смету фиксируем в договоре — до начала работ.",
        "formats note",
    )
    # закрывающий тег списка — на отступе секции: внутри карточек есть вложенные ul цен
    s = re.sub(
        r'<ul class="format-grid"[^>]*>.*?\n            </ul>',
        lambda m: '<ul class="format-grid" data-reveal-stagger data-reveal-pair>\n'
        + build_formats(c["formats"], c["price_label"])
        + "\n            </ul>",
        s,
        count=1,
        flags=re.DOTALL,
    )

    # Процесс
    s = re.sub(
        r'(<ol class="process-steps" data-process-steps>).*?(</ol>)',
        lambda m: m.group(1) + "\n" + build_steps(c["process"]) + "\n            " + m.group(2),
        s,
        count=1,
        flags=re.DOTALL,
    )

    # Способы интеграции — перед блоком команды, только если задан
    if c.get("methods"):
        s = replace_one(
            s,
            "        <!-- 5. Команда -->",
            build_methods_section(c["methods"]) + "\n\n        <!-- 5. Команда -->",
            "methods insert",
        )

    # FAQ
    s = replace_one(
        s,
        'Частые вопросы <span class="section-title__muted">о веб-сервисах</span>',
        f'Частые вопросы <span class="section-title__muted">{c["faq_heading"]}</span>',
        "faq heading",
    )
    s = re.sub(
        r'<ul class="faq__list" data-reveal-stagger>.*?</ul>',
        lambda m: '<ul class="faq__list" data-reveal-stagger>\n' + build_faq(c["faq"]) + "\n            </ul>",
        s,
        count=1,
        flags=re.DOTALL,
    )

    # Перелинковка: услуги направления
    s = replace_one(
        s,
        'Другие <span class="section-title__muted">направления</span>',
        'Другие <span class="section-title__muted">услуги направления</span>',
        "related title",
    )
    s = re.sub(
        r'<ul class="related__list" data-reveal-stagger>.*?</ul>',
        lambda m: '<ul class="related__list" data-reveal-stagger>\n'
        + build_related(WS_RELATED, slug)
        + "\n          </ul>",
        s,
        count=1,
        flags=re.DOTALL,
    )

    # Модалки кейсов
    templates = [b.build_template(cid, with_site=True) for cid in c["cases"]]
    tpl_start = s.index("    <!-- Содержимое детальных окон кейсов")
    tpl_end = s.index("  </body>")
    s = (
        s[:tpl_start]
        + "    <!-- Содержимое детальных окон кейсов: тексты и ссылки взяты с itach.by -->\n"
        + "\n\n".join(templates)
        + "\n\n"
        + s[tpl_end:]
    )

    out = b.ROOT / f"{slug}.html"
    out.write_text(s, encoding="utf-8")
    print(f"built {out.name}: {len(cards)} кейсов")


if __name__ == "__main__":
    for slug, content in PAGES.items():
        generate(slug, content)
