# -*- coding: utf-8 -*-
"""Разметка блока «Кому подходит» — карусель со слайдами.

Блок одинаковый на всех подстраницах услуг: один слайд во всю ширину
контейнера, следующий выглядывает справа, снизу индикатора нет. Меняется
только контент: сегменты передаются списком (tag, title, text).

Изображение пока одно на все слайды и страницы: фотографии аудиторий
заказчик пришлёт позже.
"""
import re

IMAGE = "assets/img/audience/ai-audience.webp"
COMMENT = (
    "        <!-- Кому подходит: карусель в стиле «What's new?». Слайды листаются\n"
    "             автоматически и перетаскиванием; изображение пока общее для всех страниц -->"
)
LINK = (
    '<a class="audience-slide__link" href="#lead">Обсудить проект '
    '<svg class="icon icon--gradient" aria-hidden="true"><use href="#icon-arrow-up-right" /></svg></a>'
)


def plain(html):
    """Заголовок без разметки: в старых панелях вторая половина была обёрнута
    в span, а перенос строки после дефиса давал «Интернет- магазины»."""
    html = re.sub(r"<[^>]+>", "", html)
    html = re.sub(r"([-—])\s+", r"\1", html)
    return re.sub(r"\s+", " ", html).strip()


def build_section(segments):
    """Возвращает <section> целиком. segments: [(tag, title, text), ...]."""
    slides = []
    total = len(segments)
    for i, (tag, title, text) in enumerate(segments, 1):
        slides.append(
            f'                <li class="audience-slide glow-card" role="group" aria-roledescription="слайд" aria-label="{i} из {total}">\n'
            '                  <div class="audience-slide__media">\n'
            f'                    <img src="{IMAGE}" alt="" aria-hidden="true" loading="lazy" decoding="async" />\n'
            '                  </div>\n'
            '                  <div class="audience-slide__body">\n'
            f'                    <span class="audience-slide__tag">{plain(tag)}</span>\n'
            f'                    <h3 class="audience-slide__title">{plain(title)}</h3>\n'
            f'                    <p class="audience-slide__text">{text}</p>\n'
            f'                    {LINK}\n'
            '                  </div>\n'
            '                </li>'
        )
    return (
        '        <section class="audience" aria-labelledby="segments-title">\n'
        '          <div class="container">\n'
        '            <h2 class="section-title" data-reveal id="segments-title">\n'
        '              Кому <span class="section-title__muted">подходит</span>\n'
        '            </h2>\n'
        '          </div>\n'
        '          <div class="audience-carousel" data-audience-carousel data-reveal>\n'
        '            <div class="audience-carousel__viewport" data-audience-viewport tabindex="0" role="region" aria-roledescription="карусель" aria-label="Кому подходит">\n'
        '              <ul class="audience-carousel__track" data-audience-track>\n'
        + "\n".join(slides)
        + "\n              </ul>\n"
        "            </div>\n"
        "          </div>\n"
        "        </section>"
    )
