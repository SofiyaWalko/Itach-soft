# -*- coding: utf-8 -*-
"""Досборка страницы «AI-разработка под ключ» под структуру других услуг.

1. «Проблемы, которые решаем» — после блока «О направлении».
2. «Почему нам доверяют» — после кейсов, карточки с отворотом.
3. «AI-решения и стоимость» — десять решений из блока itach.by
   «Какие AI-решения мы разрабатываем?»; карточки статичные, без ссылок.
4. «Технологии» — бегущая лента из стека itach.by; логотипы добавим позже.

Запуск: python tools/add_ai_blocks.py
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "service-ai.html"

PROBLEMS = [
    ("Ручная работа", "Сотрудники тратят часы на обработку и перенос данных"),
    ("Обращения", "Клиентские запросы обрабатываются медленно, ответы задерживаются"),
    ("Данные", "Решения принимаются на основе разрозненной информации из разных систем"),
    ("Типовые сценарии", "Готовая автоматизация не покрывает сложные случаи бизнеса"),
    ("Персонализация", "Без персональных предложений компания теряет продажи"),
    ("Масштабирование", "Процессы растут только вместе со штатом"),
]

WHY = [
    ("Опыт и статус", "Платиновый партнёр Битрикс24, золотой партнёр 1С-Битрикс и 10 лет работы с корпоративными системами.", ["10 лет", "Партнёр", "Статус"]),
    ("Реализованные проекты", "Более 150 проектов — от сайтов и CRM до телефонии и веб-сервисов; AI встраиваем в живые системы.", ["150+", "Практика", "Кейсы"]),
    ("Гарантия результата", "Гарантия 24 месяца на работы и сопровождение после запуска.", ["24 месяца", "Гарантия", "Поддержка"]),
    ("Персональный менеджер", "Один человек ведёт проект и отвечает на вопросы на всех этапах.", ["Менеджер", "Связь", "Этапы"]),
    ("Сертификаты и стандарты", "Сертификат крупных корпоративных внедрений и ISO 9001-2015.", ["ISO 9001", "Сертификат", "Качество"]),
    ("Пилот и измеримый эффект", "Начинаем с небольшого участка, считаем эффект и масштабируем только то, что работает.", ["Пилот", "Метрики", "Масштаб"]),
]

SOLUTIONS = [
    ("AI-чат-боты и виртуальные ассистенты", "Боты для сайта, мессенджеров и CRM: отвечают клиентам, собирают заявки и передают данные менеджерам.", "от 150 000 ₽"),
    ("Корпоративные AI-ассистенты", "Помогают сотрудникам находить информацию во внутренних документах, регламентах и базе знаний.", "от 300 000 ₽"),
    ("AI-интеграции с CRM Битрикс24", "Обрабатывают лиды, ставят задачи, готовят ответы и подсказывают менеджерам следующие шаги.", "от 240 000 ₽"),
    ("Интеллектуальный поиск по документам", "Поиск по документам, инструкциям и договорам обычным языком — без знания структуры хранения.", "от 300 000 ₽"),
    ("AI для обработки документов", "Распознавание, классификация и извлечение данных из счетов, актов, договоров и заявлений.", "от 300 000 ₽"),
    ("Предиктивная аналитика", "Прогнозы продаж, спроса, загрузки и оттока клиентов на основе исторических данных.", "от 450 000 ₽"),
    ("Рекомендательные системы", "Персональные рекомендации товаров, услуг и материалов для магазинов, сервисов и кабинетов.", "по запросу"),
    ("AI-модули для сайтов и веб-сервисов", "Умный поиск, подсказки, обработка заявок и персонализация контента в сайтах и сервисах.", "по запросу"),
    ("Компьютерное зрение", "Распознавание изображений, объектов, дефектов и номеров на фото и видео.", "по запросу"),
    ("AI для анализа обращений и коммуникаций", "Определение темы, срочности и эмоциональной окраски обращений, маршрутизация и контроль качества.", "по запросу"),
]

# (название, файл логотипа, ширина, высота) — логотипы лежат в assets/img/tech/ai/
# Команда AI-проекта: две новые роли (ML и данные) + четыре из общего штата
TEAM = [
    ("role-ml-engineer", 700, 600, "AI/ML-инженер", "Выбирает и настраивает модели, промпты и RAG, оценивает качество ответов на реальных примерах."),
    ("role-data-engineer", 610, 600, "Data-инженер", "Готовит данные: сбор, очистка, разметка и наполнение векторного хранилища."),
    ("role-backend", 600, 393, "Python-разработчик", "Пишет бэкенд и API, связывает модель с Битрикс24, сайтом и внутренними системами."),
    ("role-business-analyst", 564, 600, "Бизнес-аналитик", "Разбирает процессы, формулирует сценарии и метрики, по которым оцениваем эффект."),
    ("role-project-manager", 522, 600, "Проектный менеджер", "Ведёт пилот и внедрение: сроки, приоритеты и коммуникацию между заказчиком и командой."),
    ("role-devops", 538, 600, "DevOps-инженер", "Разворачивает решение, настраивает мониторинг, обновления и защиту данных."),
]

TECH = [
    ("Python", "python", 400, 400),
    ("OpenAI API", "openai", 400, 397),
    ("PyTorch", "pytorch", 331, 400),
    ("TensorFlow", "tensorflow", 357, 400),
    ("Scikit-learn", "scikit-learn", 400, 216),
    ("LangChain", "langchain", 400, 204),
    ("Векторные базы данных", "vector-db", 215, 400),
    ("REST API", "rest-api", 400, 383),
    ("Docker", "docker", 400, 318),
]


def build_problems():
    rows = []
    for keyword, desc in PROBLEMS:
        rows.append(
            f'              <li class="problem-row">\n'
            f'                <span class="problem-row__keyword">{keyword}</span>\n'
            f'                <p class="problem-row__desc">{desc}</p>\n'
            f'                <span class="problem-row__stamp" aria-hidden="true">\n'
            f'                  <svg class="icon icon--gradient"><use href="#icon-check" /></svg>\n'
            f'                  <span class="problem-row__stamp-text">Решим</span>\n'
            f'                </span>\n'
            f'              </li>'
        )
    return (
        '        <!-- Проблемы строками: ключевое слово слева серым, описание по центру,\n'
        '             справа — штамп «Решим». Каждая строка всплывает по мере скролла -->\n'
        '        <section class="problems" aria-labelledby="problems-title">\n'
        '          <div class="container">\n'
        '            <h2 class="section-title" data-reveal id="problems-title">\n'
        '              Проблемы, которые <span class="section-title__muted">решаем</span>\n'
        '            </h2>\n'
        '            <ul class="problem-rows" data-problem-rows>\n'
        + "\n".join(rows)
        + "\n            </ul>\n"
        "          </div>\n"
        "        </section>"
    )


def build_why():
    cards = []
    for title, text, facts in WHY:
        facts_html = "".join(f'<li class="why-card__fact">{fact}</li>' for fact in facts)
        cards.append(
            f'              <article class="why-card" tabindex="0">\n'
            f'                <div class="why-card__body">\n'
            f'                  <h3 class="why-card__title">{title}</h3>\n'
            f'                  <p class="why-card__text">{text}</p>\n'
            f'                </div>\n'
            f'                <span class="why-card__sheet" aria-hidden="true"></span>\n'
            f'                <ul class="why-card__facts">{facts_html}</ul>\n'
            f'                <span class="why-card__fold" aria-hidden="true"></span>\n'
            f'              </article>'
        )
    return (
        '        <!-- Почему нам доверяют: карточки с отворотом, раскрывается на наведении -->\n'
        '        <section class="why" id="why" aria-labelledby="why-title">\n'
        '          <div class="container">\n'
        '            <h2 class="section-title" data-reveal id="why-title">\n'
        '              Почему нам <span class="section-title__muted">доверяют</span>\n'
        '            </h2>\n'
        '            <div class="why__scroller">\n'
        '              <div class="why-cards" data-reveal-stagger>\n'
        + "\n".join(cards)
        + "\n              </div>\n            </div>\n          </div>\n        </section>"
    )


def build_formats():
    cards = []
    for title, desc, price in SOLUTIONS:
        cards.append(
            f'              <li class="format-card format-card--static glow-card">\n'
            f'                <div class="format-card__link">\n'
            f'                  <h3 class="format-card__title">{title}</h3>\n'
            f'                  <p class="format-card__desc">{desc}</p>\n'
            f'                  <ul class="format-card__prices">\n'
            f'                    <li class="format-card__price">\n'
            f'                      <span class="format-card__price-label">Стоимость</span>\n'
            f'                      <span class="format-card__price-value">{price}</span>\n'
            f'                    </li>\n'
            f'                  </ul>\n'
            f'                </div>\n'
            f'              </li>'
        )
    return (
        '<ul class="format-grid" data-reveal-stagger data-reveal-pair>\n'
        + "\n".join(cards)
        + "\n            </ul>"
    )


def build_tech():
    def items(rows):
        return "\n".join(
            f'                <li class="tech-marquee__tech">\n'
            f'                  <img class="tech-marquee__logo" src="assets/img/tech/ai/{file}.webp" alt="" width="{w}" height="{h}" loading="lazy">\n'
            f'                  <span class="tech-marquee__name">{name}</span>\n'
            f'                </li>'
            for name, file, w, h in rows
        )

    hidden = "\n".join(f"              <li>{name}</li>" for name, *_ in TECH)
    forward = items(TECH)
    reverse = items(list(reversed(TECH)))
    return (
        '        <!-- Технологии: логотипы серые, при наведении обретают цвет -->\n'
        '        <section class="tech" aria-labelledby="tech-title">\n'
        '          <div class="container tech__inner">\n'
        '            <h2 class="section-title" data-reveal id="tech-title">\n'
        '              Технологии <span class="section-title__muted">для AI-решений</span>\n'
        '            </h2>\n'
        '            <ul class="visually-hidden">\n'
        + hidden
        + "\n            </ul>\n"
        "          </div>\n\n"
        '          <div class="tech-marquee" data-reveal aria-hidden="true">\n'
        '            <div class="tech-marquee__track">\n'
        '              <ul class="tech-marquee__list">\n'
        + forward
        + "\n              </ul>\n"
        '              <ul class="tech-marquee__list">\n'
        + forward
        + "\n              </ul>\n"
        "            </div>\n"
        '            <div class="tech-marquee__track tech-marquee__track--reverse">\n'
        '              <ul class="tech-marquee__list">\n'
        + reverse
        + "\n              </ul>\n"
        '              <ul class="tech-marquee__list">\n'
        + reverse
        + "\n              </ul>\n"
        "            </div>\n"
        "          </div>\n"
        "        </section>"
    )


def build_team():
    rows = []
    for img, w, h, name, duty in TEAM:
        rows.append(
            f'              <li class="team-role glow-card">\n'
            f'                <img class="team-role__image" src="assets/img/team/{img}.webp" width="{w}" height="{h}" alt="" loading="lazy" />\n'
            f'                <span class="team-role__name">{name}</span>\n'
            f'                <span class="team-role__duty">{duty}</span>\n'
            f'              </li>'
        )
    return (
        '        <!-- 5. Команда: роли, из которых собирается AI-проект -->\n'
        '        <section class="team" aria-labelledby="team-title">\n'
        '          <div class="container">\n'
        '            <h2 class="section-title" data-reveal id="team-title">\n'
        '              Кто работает <span class="section-title__muted">над AI-проектом</span>\n'
        '            </h2>\n'
        '            <p class="team__lead" data-reveal>\n'
        '              Состав команды зависит от задачи: на пилот достаточно ML-инженера и аналитика, на внедрение подключаем разработку, данные и инфраструктуру.\n'
        '            </p>\n'
        '            <ul class="team__row" data-reveal-stagger>\n'
        + "\n".join(rows)
        + "\n            </ul>\n          </div>\n        </section>"
    )


def main():
    s = PAGE.read_text(encoding="utf-8")

    # 1. Проблемы — перед кейсами
    if 'class="problems"' not in s:
        anchor = "        <!-- 2. Кейсы -->"
        assert s.count(anchor) == 1
        s = s.replace(anchor, build_problems() + "\n\n" + anchor)
        print("added: problems")

    # 2. «Почему нам доверяют» — перед блоком услуг и стоимости
    if 'class="why"' not in s:
        anchor = "        <!-- Услуги и стоимость -->"
        assert s.count(anchor) == 1
        s = s.replace(anchor, build_why() + "\n\n" + anchor)
        print("added: why")

    # 3. Форматы — десять AI-решений
    start = s.index('<ul class="format-grid" data-reveal-stagger data-reveal-pair>')
    end = s.index("\n            </ul>", start) + len("\n            </ul>")
    s = s[:start] + build_formats() + s[end:]

    # 4. Технологии — только если блока ещё нет
    if 'class="tech"' not in s:
        anchor = "        <!-- Кому подходит"
        assert s.count(anchor) == 1
        s = s.replace(anchor, build_tech() + "\n\n" + anchor)
        print("added: tech")

    # 5. Команда — перед технологиями
    if 'class="team"' not in s:
        anchor = "        <!-- Технологии"
        assert s.count(anchor) == 1
        s = s.replace(anchor, build_team() + "\n\n" + anchor)
        print("added: team")

    PAGE.write_text(s, encoding="utf-8")
    print("AI page updated")


if __name__ == "__main__":
    main()
