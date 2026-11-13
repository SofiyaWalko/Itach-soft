"""Собирает четыре страницы раздела «Компания» на общем каркасе главной.

Шапка, подвал и форма заявки берутся из index.html, поэтому правки в них
подхватываются при повторном запуске. Материалы — с itach.by.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
SERVICE_SITES = (ROOT / "service-sites.html").read_text(encoding="utf-8")
META = json.loads((ROOT / "tools" / "reviews_data.json").read_text(encoding="utf-8"))


def shell(title: str, description: str) -> tuple[str, str]:
    """Возвращает (голова с шапкой, подвал) страницы."""
    prefix = INDEX[: INDEX.index('    <main id="main">')]
    prefix = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", prefix, count=1, flags=re.S)
    prefix = re.sub(
        r'<meta\s+name="description"\s+content=".*?"\s*/>',
        f'<meta name="description" content="{description}" />',
        prefix,
        count=1,
        flags=re.S,
    )
    prefix = prefix.replace('<body class="home">', "<body>")
    # Главной нужны WebGL-лента и калькулятор, внутренним страницам — нет
    prefix = prefix.replace('    <script src="assets/js/hero-gl.js" defer></script>\n', "")
    prefix = prefix.replace('    <script src="assets/js/calculator.js" defer></script>\n', "")
    # На этих страницах нет калькулятора — кнопка в мега-меню ведёт к форме заявки
    prefix = prefix.replace('mega-menu__promo-link" href="#calculator"', 'mega-menu__promo-link" href="#lead"')

    footer_start = INDEX.index('    <footer class="site-footer">')
    # Диалог кейса и его шаблоны нужны только главной — отрезаем
    suffix = INDEX[footer_start : INDEX.index('    <dialog class="detail"')] + "  </body>\n</html>\n"
    return prefix, suffix


def lead_section() -> str:
    start = INDEX.index('<section class="lead" id="lead"')
    end = INDEX.index("</section>", start) + len("</section>")
    return INDEX[start:end]


def breadcrumbs(current: str) -> str:
    return f"""          <nav class="breadcrumbs" aria-label="Хлебные крошки" data-reveal-stagger>
            <a class="breadcrumbs__link" href="index.html">Главная</a>
            <svg class="icon breadcrumbs__sep" aria-hidden="true"><use href="#icon-chevron-down" /></svg>
            <span class="breadcrumbs__current" aria-current="page">{current}</span>
          </nav>"""


def page(title: str, description: str, content: str) -> str:
    prefix, suffix = shell(title, description)
    return prefix + '    <main id="main">\n' + content + "\n" + lead_section() + "\n    </main>\n\n" + suffix


# ---------- Гарантия ----------

GUARANTEE = (
    breadcrumbs("Гарантия")
    + """
          <div class="company-page__head">
            <h1 class="section-title" id="guarantee-title" data-reveal>
              Гарантия <span class="section-title__muted">до 24 месяцев</span>
            </h1>
            <p class="company-page__lead" data-reveal>
              Отвечаем за качество решений, которые разрабатываем и внедряем. Если в течение гарантийного срока
              обнаружится ошибка по нашей вине — исправим её бесплатно.
            </p>
          </div>

          <ul class="page-stats" data-reveal-stagger>
            <li class="page-stat glow-card">
              <span class="page-stat__value">24 мес</span>
              <p class="page-stat__text">гарантия с момента подписания акта</p>
            </li>
            <li class="page-stat glow-card">
              <span class="page-stat__value">3</span>
              <p class="page-stat__text">направления гарантии</p>
            </li>
            <li class="page-stat glow-card">
              <span class="page-stat__value">4 ч</span>
              <p class="page-stat__text">реакция поддержки на обращения</p>
            </li>
            <li class="page-stat glow-card">
              <span class="page-stat__value">24/7</span>
              <p class="page-stat__text">поддержка после запуска</p>
            </li>
          </ul>

          <section class="company-section" aria-labelledby="guarantee-directions-title">
            <h2 class="company-section__title" id="guarantee-directions-title" data-reveal>
              На что распространяется <span class="section-title__muted">гарантия</span>
            </h2>
            <div class="guarantee__grid" data-reveal-stagger>
              <article class="guarantee-card glow-card">
                <h3 class="guarantee-card__title">Сайты и веб-сервисы</h3>
                <p class="guarantee-card__text">
                  Разработка и доработка корпоративных сайтов, порталов, интернет-магазинов, лендингов и веб-приложений.
                </p>
              </article>
              <article class="guarantee-card glow-card">
                <h3 class="guarantee-card__title">Битрикс24</h3>
                <p class="guarantee-card__text">
                  Внедрение, настройка и доработка CRM: воронки, бизнес-процессы, интеграции и права доступа.
                </p>
              </article>
              <article class="guarantee-card glow-card">
                <h3 class="guarantee-card__title">IP-АТС на базе Asterisk</h3>
                <p class="guarantee-card__text">
                  Внедрение и доработка телефонной станции, настройка VoIP, интеграция с CRM и сценарии обработки звонков.
                </p>
              </article>
            </div>
          </section>

          <section class="company-section" aria-labelledby="guarantee-terms-title">
            <h2 class="company-section__title" id="guarantee-terms-title" data-reveal>
              Условия <span class="section-title__muted">и исключения</span>
            </h2>
            <div class="guarantee__terms" data-reveal-stagger>
              <div class="guarantee__panel glow-card">
                <h3 class="guarantee__panel-title">Что покрывает гарантия</h3>
                <ul class="guarantee__list">
                  <li>Срок — до 24 месяцев с момента подписания акта выполненных работ.</li>
                  <li>Гарантия действует, если в настройки системы не вмешивались третьи лица.</li>
                  <li>Распространяется только на ошибки, вызванные действиями исполнителя.</li>
                  <li>Если проблема возникла по вине заказчика, помогаем с устранением — в рамках отдельной задачи.</li>
                </ul>
              </div>
              <div class="guarantee__panel guarantee__panel--muted">
                <h3 class="guarantee__panel-title">Гарантия не распространяется на</h3>
                <ul class="guarantee__list guarantee__list--exceptions">
                  <li>Доработку и настройку программ сторонних разработчиков, если это не было отражено в договоре.</li>
                  <li>Случаи взлома или DOS-атак третьих лиц.</li>
                  <li>Орфографические и стилистические ошибки текста, не относящиеся к производственным дефектам.</li>
                  <li>Оптимизацию быстродействия ПО.</li>
                </ul>
              </div>
            </div>
          </section>"""
)

# ---------- Отзывы ----------

REVIEWS_CARDS = re.search(
    r'<ul class="reviews__list"[^>]*>(.*?)</ul>', INDEX, re.S
).group(1)

scan_cards = []
for item in META:
    name = item["name"].replace('"', "&quot;")
    service = item["service"]
    scan_cards.append(
        f"""            <li class="review-scan glow-card">
              <a class="review-scan__link" href="{item['pdf']}" target="_blank" rel="noopener">
                <span class="review-scan__media">
                  <img src="{item['thumb']}" width="283" height="400" alt="Отзыв компании {name}" loading="lazy" />
                </span>
                <span class="review-scan__body">
                  <span class="review-scan__name">{name}</span>
                  <span class="review-scan__service">{service}</span>
                </span>
              </a>
            </li>"""
    )

# Услуга для фильтра отзывов — по порядку карточек в ленте главной
REVIEW_SERVICES = ["sites", "sites", "support", "bitrix24", "bitrix24", "support", "sites"]
chunks = REVIEWS_CARDS.split('<li class="review-card glow-card">')
assert len(chunks) == len(REVIEW_SERVICES) + 1, "Изменилось число отзывов в ленте главной"
REVIEW_CARDS_TAGGED = chunks[0]
for service, chunk in zip(REVIEW_SERVICES, chunks[1:]):
    REVIEW_CARDS_TAGGED += (
        f'<li class="review-card glow-card" data-review-card data-service="{service}">' + chunk
    )

REVIEWS = (
    breadcrumbs("Отзывы")
    + """
          <div class="company-page__head">
            <h1 class="section-title" id="reviews-title" data-reveal>
              Отзывы <span class="section-title__muted">клиентов</span>
            </h1>
            <p class="company-page__lead" data-reveal>
              Банки, лизинговые компании, ритейл, образование и промышленность. Собрали отзывы клиентов
              о проектах, которые мы разработали и продолжаем поддерживать.
            </p>
          </div>

          <section class="letters" aria-label="Благодарственные письма">
            <div class="letters__scroller" data-drag-scroll tabindex="0" role="region" aria-label="Благодарственные письма, прокручиваются по горизонтали">
              <ul class="letters__list">
"""
    + "\n".join(scan_cards)
    + """
              </ul>
            </div>
          </section>

          <section class="reviews-block" data-reviews-filter aria-label="Отзывы клиентов">
            <form class="reviews-filter" data-reveal>
              <fieldset class="reviews-filter__group">
                <legend class="visually-hidden">Фильтр отзывов по услуге</legend>
                <label class="calc-option"><input class="calc-option__input" type="radio" name="review-service" value="" checked /><span class="calc-option__text">Все</span></label>
                <label class="calc-option"><input class="calc-option__input" type="radio" name="review-service" value="sites" /><span class="calc-option__text">Сайты</span></label>
                <label class="calc-option"><input class="calc-option__input" type="radio" name="review-service" value="bitrix24" /><span class="calc-option__text">Битрикс24</span></label>
                <label class="calc-option"><input class="calc-option__input" type="radio" name="review-service" value="support" /><span class="calc-option__text">Поддержка</span></label>
              </fieldset>
              <p class="visually-hidden" role="status" data-reviews-status></p>
            </form>
            <ul class="reviews-page__grid" data-reveal-rows>"""
    + REVIEW_CARDS_TAGGED
    + """            </ul>
          </section>"""
)

# ---------- FAQ ----------

FAQ_DATA = [
    (
        "faq-company",
        "О компании и экспертизе",
        [
            ("Почему Итач-софт можно доверить сложный IT-проект?",
             "Работаем по выстроенным процессам: аналитика, проектирование, разработка, тестирование и поддержка. Под каждую задачу собираем команду с нужной экспертизой, а качество подтверждают повторные проекты и рекомендации клиентов."),
            ("Сколько лет компания работает на рынке и какой у вас опыт?",
             "Компания основана в 2013 году. За это время реализовали сотни проектов, а совокупный опыт команды — более 1 000 000 часов разработки, внедрения и сопровождения."),
            ("Чем занимается компания Итач-софт?",
             "Разрабатываем программное обеспечение и веб-сервисы, автоматизируем бизнес-процессы. Основные направления — Битрикс24, сайты и веб-приложения, контакт-центры и IP-телефония на базе Asterisk."),
            ("Можно ли дорабатывать уже внедрённые системы?",
             "Да. Подключаемся к действующим проектам, проводим аудит, находим узкие места и предлагаем план оптимизации и развития — без необходимости переписывать всё с нуля."),
            ("Вы работаете только с проектами «под ключ» или с отдельными задачами?",
             "В обоих форматах: можем взять проект целиком — от аналитики до запуска и поддержки, — либо выполнить точечную доработку CRM, сайта, веб-сервиса или телефонии."),
            ("Какие задачи бизнеса вы решаете?",
             "Автоматизируем продажи и клиентский сервис, снижаем ручной труд и количество ошибок, делаем процессы прозрачными, интегрируем системы между собой, создаём и развиваем цифровые продукты."),
            ("Настраиваете ли вы CRM под специфику бизнеса?",
             "Да, без шаблонных решений. Сначала разбираем реальные процессы компании и задачи сотрудников, затем настраиваем воронки, поля, права доступа и автоматизации под эту логику."),
        ],
    ),
    (
        "faq-bitrix24",
        "Битрикс24 и автоматизация",
        [
            ("Как проходит внедрение Битрикс24?",
             "Анализируем бизнес-процессы, проектируем структуру CRM, настраиваем воронки, права доступа и автоматизации, подключаем интеграции с сайтом, телефонией и почтой. Затем тестируем, запускаем и обучаем сотрудников. Базовая CRM обычно занимает до месяца."),
            ("Почему вы рекомендуете Битрикс24 для автоматизации бизнеса?",
             "Это универсальная платформа, которая объединяет CRM, задачи, коммуникации, аналитику и автоматизацию. При грамотной настройке она повышает управляемость бизнеса и прозрачность работы сотрудников."),
        ],
    ),
    (
        "faq-sites",
        "Сайты и веб-сервисы",
        [
            ("Предоставляете ли вы услуги по SEO-оптимизации для сайтов?",
             "Да, базовая SEO-оптимизация входит в процесс разработки: закладываем необходимые элементы, чтобы сайт корректно индексировался и был виден в поисковых системах."),
            ("Как проходит процесс разработки сайта?",
             "Обсуждаем требования и цели, проектируем структуру и внешний вид, разрабатываем функционал, тестируем и оптимизируем, запускаем проект. После передачи сайта остаёмся на поддержке и доработках."),
            ("Какие виды сайтов вы разрабатываете?",
             "Корпоративные сайты, интернет-магазины, лендинги, сложные веб-приложения и интерфейсы, а также специализированные сервисы под требования бизнеса."),
        ],
    ),
    (
        "faq-telephony",
        "IP-телефония",
        [
            ("Какие дополнительные услуги вы предоставляете по настройке IP-АТС?",
             "Интеграцию с CRM, мониторинг и регулярные обновления, автоматическую маршрутизацию звонков, голосовое меню и отчёты. Набор опций настраиваем индивидуально под задачи компании."),
            ("Включаете ли вы техническую поддержку в стоимость внедрения IP-АТС?",
             "Нет. После внедрения поддержка оформляется отдельным договором с ежемесячной абонентской платой: мониторинг, оперативное устранение неисправностей и консультации. Есть тарифы с обслуживанием 24/7 и неограниченным числом обращений."),
            ("Предоставляете ли вы обучение для сотрудников по работе с IP-АТС?",
             "Да, после внедрения. Показываем, как управлять звонками, пользоваться голосовой почтой и конференц-связью. Обучение проводим отдельно для администраторов и конечных пользователей."),
            ("Какие функции будут настроены в IP-АТС на базе Asterisk для моего бизнеса?",
             "Маршрутизация звонков, голосовая почта, автоответчики, конференц-связь, интеграция с CRM, голосовые меню IVR, отчётность и мониторинг. Дополнительно обеспечиваем безопасность VoIP-канала."),
        ],
    ),
    (
        "faq-support",
        "Гарантии, качество и поддержка",
        [
            ("Как работает техническая поддержка?",
             "Поддержка доступна 24/7. До 90% обращений закрываем в течение первых 4 часов."),
            ("Что происходит после запуска проекта?",
             "Остаёмся на связи: сопровождаем систему, консультируем сотрудников и оперативно решаем возникающие вопросы."),
            ("Какую гарантию вы предоставляете на выполненные работы?",
             'До 24 месяцев на разработанные и внедрённые решения. Гарантия распространяется на ошибки, возникшие по вине исполнителя. Подробные условия — на странице <a href="garantii.html">«Гарантия»</a>.'),
        ],
    ),
    (
        "faq-process",
        "Процесс работы",
        [
            ("Можно ли обратиться за консультацией без заказа услуг?",
             "Да. Можно задать вопрос через форму на сайте или получить консультацию специалиста до начала сотрудничества."),
            ("Как контролируются сроки и качество?",
             "Ведём проект поэтапно: фиксируем сроки, регулярно отчитываемся и используем современные системы управления проектами. Вы всегда понимаете, на каком этапе находится работа и что делается сейчас."),
            ("Как формируется команда под проект?",
             "За проектом закрепляется персональный менеджер. Он координирует выделенную команду аналитиков, разработчиков и интеграторов под задачи проекта."),
            ("С чего начинается сотрудничество?",
             "С первичной консультации и бесплатного экспресс-аудита бизнес-процессов. Это помогает определить объём работ и предложить оптимальное решение."),
        ],
    ),
]

nav_items = "\n".join(
    f"""              <button class="calc-option faq-page__tab" type="button" role="tab" id="faq-tab-{cid}" aria-selected="{'true' if index == 0 else 'false'}" aria-controls="{cid}" data-faq-tab="{cid}" tabindex="{0 if index == 0 else -1}">{title}</button>"""
    for index, (cid, title, _) in enumerate(FAQ_DATA)
)

group_html = []
q_num = 1
for index, (cid, title, questions) in enumerate(FAQ_DATA):
    items = []
    for question, answer in questions:
        items.append(
            f"""                <li class="faq__item glow-card">
                  <h3 class="faq__question">
                    <button class="faq__trigger" type="button" id="faq-q{q_num}" aria-expanded="false" aria-controls="faq-a{q_num}">
                      <span class="faq__text">{question}</span>
                      <span class="faq__toggle" aria-hidden="true"></span>
                    </button>
                  </h3>
                  <div class="faq__answer" id="faq-a{q_num}" role="region" aria-labelledby="faq-q{q_num}">
                    <div class="faq__answer-inner"><p>{answer}</p></div>
                  </div>
                </li>"""
        )
        q_num += 1
    group_html.append(
        f"""            <section class="faq-page__group{' is-active' if index == 0 else ''}" id="{cid}" role="tabpanel" aria-labelledby="faq-tab-{cid}">
              <ul class="faq__list">
"""
        + "\n".join(items)
        + """
              </ul>
            </section>"""
    )

FAQ = (
    breadcrumbs("Ответы на вопросы")
    + """
          <div class="company-page__head">
            <h1 class="section-title" id="faq-page-title" data-reveal>
              Часто задаваемые <span class="section-title__muted">вопросы</span>
            </h1>
            <p class="company-page__lead" data-reveal>
              Собрали ответы на вопросы, которые чаще всего задают перед началом работы:
              о компании, сроках, гарантии и поддержке.
            </p>
          </div>

          <div class="faq-page__layout" data-faq data-faq-tabs>
            <div class="faq-page__nav" role="tablist" aria-label="Категории вопросов">
"""
    + nav_items
    + """
            </div>
"""
    + "\n".join(group_html)
    + """
          </div>"""
)

# ---------- Документы ----------

DOCS = [
    (
        "Сублицензионный договор (оферта)",
        "Публичный договор на предоставление права использования программ для ЭВМ · PDF",
        "https://itach.by/docs/public-contract-cloudbitrix24.pdf",
    ),
    (
        "Прейскурант цен на лицензионное вознаграждение",
        "Программа «1С-Битрикс24» · PDF",
        "https://itach.by/docs/price.pdf",
    ),
    (
        "Политика в отношении обработки персональных данных",
        "Порядок обработки и защиты персональных данных · PDF",
        "https://itach-soft.ru/upload/politika-v-otnoshenii-personalnih-dannih.pdf",
    ),
]

doc_cards = "\n".join(
    f"""            <li>
              <a class="doc-card glow-card" href="{url}" target="_blank" rel="noopener">
                <span class="doc-card__icon" aria-hidden="true">PDF</span>
                <span class="doc-card__body">
                  <span class="doc-card__title">{title}</span>
                  <span class="doc-card__meta">{meta}</span>
                </span>
                <span class="card-arrow" aria-hidden="true">
                  <svg class="icon"><use href="#icon-arrow-up-right" /></svg>
                </span>
              </a>
            </li>"""
    for title, meta, url in DOCS
)

DOCUMENTS = (
    breadcrumbs("Документы")
    + """
          <div class="company-page__head">
            <h1 class="section-title" id="documents-title" data-reveal>
              Документы <span class="section-title__muted">и оферты</span>
            </h1>
            <p class="company-page__lead" data-reveal>
              Договоры, прейскуранты и официальные документы для работы с Итач-софт.
              Все файлы открываются в формате PDF.
            </p>
          </div>

          <ul class="docs-list" data-glow-group data-reveal-stagger>
"""
    + doc_cards
    + """
          </ul>"""
)

# ---------- О компании ----------

def section_from(source, start_marker):
    start = source.index(start_marker)
    end = source.index("      </section>", start) + len("      </section>")
    return source[start:end]


AWARDS = section_from(INDEX, "      <!-- Наши достижения")
CLIENTS = section_from(INDEX, '      <section class="clients"')
# Блок технологий переиспользуем со страницы услуги «Сайты»: две ленты
TECH = section_from(SERVICE_SITES, '        <section class="tech"')


def stat(value, text):
    return f"""            <li class="page-stat glow-card">
              <span class="page-stat__value">{value}</span>
              <p class="page-stat__text">{text}</p>
            </li>"""


def benefit(title, text, facts):
    chips = "".join(f'<li class="why-card__fact">{fact}</li>' for fact in facts)
    return f"""              <article class="why-card" tabindex="0">
                <div class="why-card__body">
                  <h3 class="why-card__title">{title}</h3>
                  <p class="why-card__text">{text}</p>
                </div>
                <span class="why-card__sheet" aria-hidden="true"></span>
                <ul class="why-card__facts">{chips}</ul>
                <span class="why-card__fold" aria-hidden="true"></span>
              </article>"""


HISTORY = [
    ("2013—2014", "Компания основана в Минске. Начали с аутсорсинга IT-инфраструктуры и продажи оборудования, запустили веб-разработку и установку контакт-центров."),
    ("2015", "«Айти-Монтаж» переименована в «Итач-Софт». Основной фокус — контакт-центры Asterisk и приложения."),
    ("2018", "Сфокусировались на внедрении Битрикс24 и контакт-центрах на Asterisk, закрыли направление аутсорсинга IT-инфраструктуры."),
    ("2019", "Усилили разработку сайтов, веб-сервисов, приложений для Битрикс24 и IP-АТС Asterisk."),
    ("2020—2026", "Вступили в Парк высоких технологий, открыли филиал в Варшаве и вышли на международный рынок."),
]


def history_event(year, text):
    return f"""                    <li class="history-event">
                      <span class="history-event__year">{year}</span>
                      <p class="history-event__text">{text}</p>
                    </li>"""


def history_points():
    return "\n".join('                    <span class="history__point"></span>' for _ in HISTORY)


def role(name, file, width, height, duty):
    return f"""              <li class="team-role glow-card">
                <img class="team-role__image" src="assets/img/team/{file}" width="{width}" height="{height}" alt="" loading="lazy" />
                <span class="team-role__name">{name}</span>
                <span class="team-role__duty">{duty}</span>
              </li>"""


LETTERS_CARDS = "\n".join(scan_cards)

ABOUT = f"""      <section class="about-hero" aria-labelledby="about-title">
        <div class="container">
{breadcrumbs("О компании")}
          <div class="company-page__head">
            <h1 class="section-title" id="about-title" data-reveal>
              О компании <span class="section-title__muted">Итач-софт</span>
            </h1>
            <p class="company-page__lead" data-reveal>
              IT-компания полного цикла: разрабатываем программное обеспечение, сайты и веб-сервисы,
              внедряем Битрикс24 и IP-телефонию на Asterisk. Работаем с 2013 года.
            </p>
          </div>

          <ul class="page-stats" data-reveal-stagger>
{stat("2013", "год основания компании")}
{stat("50+", "сертифицированных специалистов")}
{stat("1 млн+", "часов опыта команды")}
{stat("100+", "проектов на Битрикс24 в год")}
          </ul>
        </div>
      </section>

      <div class="about-sections">
        <section class="about-benefits" aria-labelledby="about-benefits-title">
          <div class="container">
            <h2 class="section-title" id="about-benefits-title" data-reveal>
              Что мы даём <span class="section-title__muted">бизнесу</span>
            </h2>
            <div class="why__scroller">
              <div class="why-cards why-cards--four" data-reveal-stagger>
{benefit("Рост продаж", "Помогаем увеличивать объём продаж и средний чек за счёт цифровых инструментов и автоматизации процессов.", ["Рост", "Выше чек", "Больше заявок"])}
{benefit("Скорость обслуживания", "Ускоряем работу с обращениями клиентов и повышаем их удовлетворённость — растёт CSI.", ["Быстрее", "Выше CSI", "Меньше ожидания"])}
{benefit("Меньше издержек", "Сокращаем ручной труд и потери из-за долгих согласований и ошибок в данных.", ["Экономия", "Точные данные", "Меньше рутины"])}
{benefit("Охват аудитории", "Объединяем каналы лидогенерации в одну систему и снижаем потери клиентов на пути к покупке.", ["Охват", "Все каналы", "Меньше потерь"])}
              </div>
            </div>
          </div>
        </section>

        <section class="about-history" aria-labelledby="about-history-title">
          <div class="history" data-history>
            <div class="history__sticky" data-history-sticky>
              <div class="container">
                <h2 class="section-title" id="about-history-title" data-reveal>
                  Наша <span class="section-title__muted">история</span>
                </h2>
              </div>
              <div class="history__viewport" data-history-viewport tabindex="0" role="region" aria-label="История компании, прокручивается по горизонтали">
                <div class="history__track" data-history-track>
                  <div class="history__rail" aria-hidden="true">
{history_points()}
                  </div>
                  <ol class="history__events">
{chr(10).join(history_event(year, text) for year, text in HISTORY)}
                  </ol>
                </div>
              </div>
            </div>
          </div>
        </section>

{AWARDS}

        <!-- Чем занимается компания: табы по направлениям, под ними — карточки работ -->
        <section class="tools" aria-labelledby="works-title">
          <div class="container">
            <h2 class="section-title" data-reveal id="works-title">
              Чем занимается <span class="section-title__muted">компания Итач-софт?</span>
            </h2>
            <div class="tools-picker" data-tools-picker data-no-hover-switch data-reveal>
              <div class="tools-tabs" role="tablist" aria-label="Направления работы">
                <button class="tools-tab is-active" type="button" role="tab" id="works-tab-1" aria-selected="true" aria-controls="works-panel-1">
                  <span>Сайты</span>
                </button>
                <button class="tools-tab" type="button" role="tab" id="works-tab-2" aria-selected="false" aria-controls="works-panel-2" tabindex="-1">
                  <span>Битрикс24 и веб-сервисы</span>
                </button>
                <button class="tools-tab" type="button" role="tab" id="works-tab-3" aria-selected="false" aria-controls="works-panel-3" tabindex="-1">
                  <span>AI-разработка</span>
                </button>
                <button class="tools-tab" type="button" role="tab" id="works-tab-4" aria-selected="false" aria-controls="works-panel-4" tabindex="-1">
                  <span>IT-инфраструктура</span>
                </button>
              </div>
              <div class="tools-panels">
                <div class="tools-panel is-active" role="tabpanel" id="works-panel-1" aria-labelledby="works-tab-1">
                  <ul class="tools-list">
                    <li class="tools-item glow-card"><h3 class="tools-item__name">Корпоративные <span class="section-title__muted">сайты</span></h3><p class="tools-item__text">Проектируем и разрабатываем сайты для компаний: структура, дизайн, вёрстка, наполнение и запуск под ключ.</p></li>
                    <li class="tools-item glow-card"><h3 class="tools-item__name">Сайты-визитки <span class="section-title__muted">и лендинги</span></h3><p class="tools-item__text">Быстрые страницы для презентации услуги или запуска рекламной кампании — с заявками и аналитикой.</p></li>
                    <li class="tools-item glow-card"><h3 class="tools-item__name">Интернет-<span class="section-title__muted">магазины</span></h3><p class="tools-item__text">Каталог, корзина, оплата и доставка, интеграции с 1С и CRM — магазин, готовый к продажам.</p></li>
                  </ul>
                </div>
                <div class="tools-panel" role="tabpanel" id="works-panel-2" aria-labelledby="works-tab-2">
                  <ul class="tools-list">
                    <li class="tools-item glow-card"><h3 class="tools-item__name">Веб-сервисы и ПО <span class="section-title__muted">с нуля</span></h3><p class="tools-item__text">Разрабатываем сервисы и приложения под задачи бизнеса: от прототипа и архитектуры до запуска и поддержки.</p></li>
                    <li class="tools-item glow-card"><h3 class="tools-item__name">Внедрение <span class="section-title__muted">Битрикс24</span></h3><p class="tools-item__text">Настраиваем CRM, задачи, телефонию и интеграции, переносим данные и обучаем сотрудников.</p></li>
                    <li class="tools-item glow-card"><h3 class="tools-item__name">Доработка и поддержка <span class="section-title__muted">Битрикс24</span></h3><p class="tools-item__text">Развиваем существующую систему: новые сценарии, интеграции, обновления и техподдержка по SLA.</p></li>
                  </ul>
                </div>
                <div class="tools-panel" role="tabpanel" id="works-panel-3" aria-labelledby="works-tab-3">
                  <ul class="tools-list">
                    <li class="tools-item glow-card"><h3 class="tools-item__name">AI-ассистенты <span class="section-title__muted">и чат-боты</span></h3><p class="tools-item__text">Разрабатываем виртуальных помощников и корпоративных ассистентов: отвечают клиентам, оформляют заказы и помогают сотрудникам.</p></li>
                    <li class="tools-item glow-card"><h3 class="tools-item__name">AI-интеграции <span class="section-title__muted">с Битрикс24</span></h3><p class="tools-item__text">Встраиваем модели в CRM и бизнес-процессы: подсказки менеджерам, автообработка обращений и документов.</p></li>
                    <li class="tools-item glow-card"><h3 class="tools-item__name">Интеллектуальный поиск <span class="section-title__muted">и аналитика</span></h3><p class="tools-item__text">Ищем по документам и базе знаний, анализируем обращения и строим прогнозы на основе данных.</p></li>
                  </ul>
                </div>
                <div class="tools-panel" role="tabpanel" id="works-panel-4" aria-labelledby="works-tab-4">
                  <ul class="tools-list">
                    <li class="tools-item glow-card"><h3 class="tools-item__name">VoIP Asterisk <span class="section-title__muted">и IP-телефония</span></h3><p class="tools-item__text">Проектируем и настраиваем IP-АТС, подключаем операторов и интегрируем телефонию с CRM.</p></li>
                    <li class="tools-item glow-card"><h3 class="tools-item__name">IT-услуги <span class="section-title__muted">и аутстафф</span></h3><p class="tools-item__text">Берём на себя поддержку IT-инфраструктуры или выделяем специалистов в вашу команду.</p></li>
                    <li class="tools-item glow-card"><h3 class="tools-item__name">Тестирование <span class="section-title__muted">ПО</span></h3><p class="tools-item__text">Проверяем функциональность, нагрузку и безопасность продукта до запуска и после обновлений.</p></li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section class="team" aria-labelledby="team-title">
          <div class="container">
            <h2 class="section-title" data-reveal id="team-title">
              Команда <span class="section-title__muted">Итач-софт</span>
            </h2>
            <p class="team__lead" data-reveal>
              Более 50 сертифицированных специалистов. 70% новых клиентов приходят по рекомендации:
              собираем команду под задачу и оставляем персонального менеджера на связи.
            </p>
            <ul class="team__row" data-reveal-stagger>
{role("Проектный менеджер", "role-project-manager.webp", 522, 600, "Координирует работу команды, контролирует сроки, коммуникацию и выполнение задач по проекту.")}
{role("Бизнес-аналитик", "role-business-analyst.webp", 564, 600, "Изучает задачи бизнеса, собирает требования и помогает определить структуру, функции и приоритеты проекта.")}
{role("UX/UI дизайнер", "role-ux-ui-designer.webp", 530, 600, "Проектирует пользовательские сценарии, прототипы и визуальную концепцию сайта, чтобы он был удобным и понятным.")}
{role("Фронтенд-разработчик", "role-frontend.webp", 600, 401, "Реализует интерфейсы, адаптивность и интерактивные элементы, обеспечивая корректную работу сайта на всех устройствах.")}
{role("Бэкенд-разработчик", "role-backend.webp", 600, 393, "Отвечает за серверную логику, интеграции, базы данных и стабильную работу функционала сайта.")}
{role("QA-инженер (тестировщик)", "role-qa.webp", 575, 600, "Проверяет функциональность, находит ошибки и контролирует качество проекта перед запуском.")}
{role("Контент-менеджер / копирайтер", "role-copywriter.webp", 578, 600, "Готовит и структурирует тексты, помогает раскрыть преимущества компании и сделать страницы понятными для клиентов.")}
{role("DevOps-инженер", "role-devops.webp", 538, 600, "Настраивает окружение, мониторинг, резервное копирование и обеспечивает надёжную работу проекта.")}
{role("Аккаунт-менеджер", "role-account-manager.webp", 594, 600, "Сопровождает клиента после запуска, помогает с новыми задачами, приоритетами и дальнейшим развитием сайта.")}
            </ul>
          </div>
        </section>

{TECH}

        <section class="about-letters" aria-labelledby="about-letters-title">
          <div class="container">
            <h2 class="section-title" id="about-letters-title" data-reveal>
              Благодарственные <span class="section-title__muted">письма</span>
            </h2>
          </div>
          <div class="letters__scroller" data-drag-scroll tabindex="0" role="region" aria-label="Благодарственные письма, прокручиваются по горизонтали">
            <ul class="letters__list">
{LETTERS_CARDS}
            </ul>
          </div>
        </section>

{CLIENTS}
      </div>"""

PAGES = [
    (
        "garantii.html",
        "Гарантия до 24 месяцев — Итач-софт",
        "Гарантия до 24 месяцев на разработку сайтов, внедрение Битрикс24 и IP-АТС на базе Asterisk: условия, направления и исключения.",
        GUARANTEE,
    ),
    (
        "otzyvy.html",
        "Отзывы клиентов — Итач-софт",
        "Отзывы и благодарственные письма клиентов Итач-софт: банки, лизинг, ритейл, образование и промышленность. Сканы документов в PDF.",
        REVIEWS,
    ),
    (
        "faq.html",
        "Ответы на часто задаваемые вопросы — Итач-софт",
        "Ответы на частые вопросы о работе с Итач-софт: опыт компании, внедрение Битрикс24, разработка сайтов, IP-телефония, гарантия и поддержка.",
        FAQ,
    ),
    (
        "dokumenty.html",
        "Документы — Итач-софт",
        "Договоры, прейскуранты и официальные документы Итач-софт для работы с сайтами, Битрикс24 и IP-телефонией.",
        DOCUMENTS,
    ),
]

for filename, title, description, content in PAGES:
    wrapper = (
        '      <section class="company-page" aria-labelledby="'
        + ("guarantee-title" if filename == "garantii.html" else
           "reviews-title" if filename == "otzyvy.html" else
           "faq-page-title" if filename == "faq.html" else "documents-title")
        + '">\n        <div class="container">\n'
        + content
        + "\n        </div>\n      </section>"
    )
    (ROOT / filename).write_text(page(title, description, wrapper), encoding="utf-8")
    print("written", filename)

(ROOT / "about.html").write_text(
    page(
        "О компании — Итач-софт",
        "Итач-софт — IT-компания полного цикла из Минска: разработка ПО, сайтов, внедрение Битрикс24 и IP-телефонии на Asterisk с 2013 года. 50+ специалистов и 1 млн часов опыта.",
        ABOUT,
    ),
    encoding="utf-8",
)
print("written about.html")
