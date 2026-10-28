# Промпты для изображений

Изображения генерируете вы. Сохраняйте файлы по указанным путям, в макете и вёрстке они подключатся автоматически.

**Общие требования ко всем 3D-объектам**
- PNG с прозрачным фоном (если генератор не умеет прозрачность, генерируйте на чисто белом фоне и вырежьте).
- Квадрат, 2048×2048 px. Объект по центру, вокруг него запас не менее 10% свободного места.
- Без текста, без пола, без тени на полу, без водяных знаков.
- Палитра бренда: оранжево-красный, коралловый, тёплый розовый, персиковый. Холодный сиреневый и голубой допустимы только как лёгкие блики в преломлениях.
- Материал: полупрозрачное переливающееся стекло (iridescent translucent glass), мягкие каустики, тонкая контровая подсветка по краю.

---

## 1. Hero: стеклянная лента

**Файл:** `assets/img/3d/hero-ribbon.png`  
**Где:** первый экран, справа и частично под заголовком.

**Промпт (EN):**
> A single abstract 3D sculpture: a twisted flowing ribbon of translucent iridescent glass, folding into a smooth loop with soft thick rounded edges. Colors: warm orange-red, coral, soft pink and peach, with subtle hints of pale lilac and light cyan in the refractions. Glossy transmissive glass material, soft caustics, delicate rim light, subtle reflections. Clean studio lighting, high-end 3D render, Octane/Redshift quality, shallow depth. Isolated on a fully transparent background, no floor, no shadow, no text, centered with generous margin.

**Негативный (если поддерживается):** text, logo, floor, hard shadow, dark background, noise, metal rust.

---

## 2. Иконки направлений (понадобятся для блока «Специализации»)

**Файлы:** `assets/img/3d/icon-sites.png`, `icon-bitrix24.png`, `icon-asterisk.png`, `icon-webservices.png`, `icon-support.png`, `icon-outstaff.png`  
**Размер:** 1024×1024 px, прозрачный фон, один объект, единый стиль и ракурс (3/4 сверху).

Единая основа для всех шести:
> A small 3D icon-style object made of translucent iridescent glass with soft rounded forms, warm orange-red, coral and peach colors with subtle lilac highlights, glossy, soft caustics, rim light, clean studio lighting, high-end 3D render, isolated on transparent background, no text, no floor, centered.

Добавьте к основе предмет:
- **Сайты:** a floating browser window with a simple layout of blocks.
- **Битрикс24:** a rounded cube made of interlocking smaller cubes, like a CRM pipeline.
- **IP-АТС Asterisk:** a glass phone handset with soft sound waves around it.
- **Веб-сервисы:** three connected nodes linked by thin glass tubes, like an API graph.
- **Техподдержка:** a glass shield with a soft round headset shape.
- **Аутстаф:** three rounded abstract person-shaped figures standing together.

---

## 3. Обложки кейсов (блок «Портфолио»)

Лучше использовать реальные скриншоты проектов. Если их нет или нужен единый стиль, генерируйте обложки по промптам ниже. Без текста и без реальных логотипов: нейросети искажают надписи, а название клиента выводится в вёрстке.

**Общая основа:**
> A soft-focus 3D-rendered scene on a warm off-white background (#F3EFEC), with soft peach and coral gradient light in the corner. A floating translucent frosted-glass interface panel at a slight angle, with abstract blocks, charts and rounded cards, no readable text, no logos. Warm orange-red accent details. Clean studio lighting, soft shadows, high-end product render, minimal.

**Файлы и размеры:**

| Файл | Размер | Добавить к основе |
|---|---|---|
| `assets/img/cases/erip.webp` (главный кейс) | 1400×540 | a call-center dashboard: headset icon, call timeline, small pipeline columns, a rising bar chart |
| `assets/img/cases/sberleasing.webp` | 880×1120 | a corporate website on a laptop screen with a calculator widget made of rounded sliders |
| `assets/img/cases/alcor.webp` | 880×1120 | a CRM pipeline board with draggable cards in columns, small diamond-shaped gem accents |

---

## 4. Обложки новостей

**Файлы:** `assets/img/news/award-2025.webp`, `rating-2025.webp`, `bitrix24-article.webp`  
**Размер:** 1000×500 px. Без текста.

**Основа:**
> Abstract 3D composition on a warm off-white background with soft coral and peach light, made of translucent iridescent glass shapes in warm orange-red and pink tones, soft caustics, rim light, clean studio lighting, high-end 3D render, plenty of empty space on the left, no text, no logos.

Добавить к основе предмет:
- **award-2025:** a glass trophy cup with a small star.
- **rating-2025:** a glass podium with three steps, the second step highlighted.
- **bitrix24-article:** interlocking glass cubes connected by thin glowing lines, like an automation flow.

---

## 5. Фавикон и превью для соцсетей

- **Фавикон:** берём из логотипа (треугольник «play» оранжево-красного цвета), генерировать не нужно.
- **OG-картинка** `assets/img/og-cover.jpg`, 1200×630:
  > Wide banner: on the right a twisted ribbon of translucent iridescent glass in warm orange-red, coral and pink tones, on a warm off-white background with soft peach glow, large empty space on the left for a headline, no text, high-end 3D render.
  Заголовок и логотип накладываем в макете, не в генерации.

---

## 6. Награда «Народный выбор 2025»

Берём официальный значок с текущего сайта (файл есть на itach-soft.ru), генерировать не нужно.

---

## 7. Объекты для карточек «Какие задачи решаем»

**Файлы:** `assets/img/3d/task-1.png` … `task-5.png`
**Где:** в нижней части светло-серых карточек блока «Какие задачи решаем», объект крупный, частично выходит за край карточки (как в референсе).

**Общие требования (отличаются от раздела выше)**
- Цвет: **только серый**, монохром. Светло-серый и средне-серый с мягкими тёмно-серыми тенями, светлые блики. Без оранжевого, розового и голубого, цвет добавим в вёрстке при наведении.
- Материал: матовый мягкий пластик или soft-touch (satin matte clay), без зеркальных бликов, мягкие скруглённые формы.
- Прозрачный фон PNG, квадрат 1600×1600 px, объект занимает ~85% кадра, можно слегка выходить за край.
- Один и тот же свет и стиль во всех пяти (свет сверху слева, мягкая тень), чтобы они смотрелись как набор.
- Без текста, пола, водяных знаков.

**Общая часть промпта (добавлять в начало каждого):**
> Single abstract 3D object, soft matte satin clay material in monochrome light and mid grey, smooth thick rounded forms, soft studio lighting from the top left, gentle ambient occlusion, subtle rim light, high-end 3D render, Octane quality. Isolated on a fully transparent background, no floor, no text, no logo, no colored hues.

**Негативный:** color, orange, pink, blue, text, floor, hard shadow, glossy mirror reflections, dark background, noise, humans.

### 1. «Заявки теряются, а менеджеры забывают о клиентах»
> *Идея: воронка, из которой уходят потери.*
> A chunky rounded funnel with several small smooth spheres dropping out of its side while a few remain inside; one sphere hangs in mid-air falling away. Playful tactile feel.

### 2. «Сотрудники тратят время на ручную работу»
> *Идея: шестерёнка, которая работает за людей.*
> A big thick soft-edged gear with a second smaller interlocking gear, slightly tilted and partly cropped at the edge of the frame, chunky toy-like proportions.

### 3. «Системы не обмениваются данными»
> *Идея: два блока, которые не соединяются.*
> Two separate rounded puzzle-piece blocks facing each other with a small gap between them and a thick soft cable loop trailing from one of them, ending unconnected. Slightly angled view.

### 4. «Сайт не справляется с задачами бизнеса»
> *Идея: окно браузера, которое трещит и перегружено.*
> A rounded browser window slab with a thick soft frame and three round buttons at the top, its surface overloaded and bulging, with a few soft cubes stacking and spilling out from the front. Slightly tilted.

### 5. «Не хватает ресурсов для развития IT-продукта»
> *Идея: растущая лестница или ракета, которой не хватает топлива.*
> A chunky rounded stair of stacked soft blocks rising diagonally upward, the top step missing, with a thick rounded arrow above it pointing up. Clean and simple.

**Если нужна «волнистая» абстракция как в референсе** (вместо предметов), замените вторую часть любого промпта на:
> thick smooth twisted ribbon with a soft loop and layered curves, flowing across the frame, partly cropped at the edge.

---

## 8. Интерфейсы для карточек «Наши кейсы»

**Файлы:** `assets/img/cases/erip.jpg`, `paritetbank.jpg`, `helix.jpg`, `imkliva.jpg`, `a-100.jpg`
**Размер:** 1440×940 px (ландшафт). Экспорт JPG до 200 КБ.

**Как они показываются.** Картинка стоит в нижней части карточки и обрезается нижним краем. В двух верхних карточках (ЕРИП, Паритетбанк) видна вся ширина. В трёх нижних (Helix, Imkliva, А-100) картинка сдвинута вправо и справа обрезается, поэтому главное держите в левых 70 % кадра, а в верхних 60 % по высоте.

**Стиль.** Интерфейсы в стиле Битрикс24 (кроме А-100, это отдельное приложение): светлый фон, голубой акцент, левая узкая панель с иконками. Цвета сайта здесь не используем, чтобы скриншоты выглядели как настоящий продукт.

**Общая часть Битрикс24 (в начало промптов 1–4):**
> Screenshot of a CRM web interface in the style of Bitrix24, flat front view, no browser frame, cropped to the app window. Light interface on a white and very light grey background, bright cyan-blue accent colour (#2fc6f6) with a deeper blue (#2067b0) for headers and active items, a narrow vertical left sidebar with outline icons and a rounded top bar with a search field and a user avatar. Rounded cards 8px, thin light grey borders, small coloured status chips (green, orange, red, blue), tidy tables and kanban cards. Clean sans-serif typeface. Realistic anonymous sample data, short labels in Russian, no lorem ipsum. Crisp, high resolution, 3:2 landscape.

**Негативный:** dark theme, orange or pink brand theme, browser address bar, window chrome, device frame, watermark, blurry, garbled text, stock photo people.

**Про текст.** Генераторы плохо рисуют кириллицу. Если подписи получаются искажёнными, добавьте в промпт: «all text lines rendered as neutral grey placeholder bars instead of readable text», крупные цифры и короткие слова можно оставить.

---

### 1. ЕРИП — контакт-центр на базе Asterisk и Битрикс24
**Лого:** ✅ нужно, `logos/erip.png`. Поставить в левый верхний угол шапки.

> [общая часть Битрикс24] Contact-centre operator workspace. Left: a live conversation queue with channel icons (phone, e-mail, Telegram, Viber, social networks), each item with a status dot and waiting timer. Centre: an open customer card (CRM contact) with name, phone, deals tab and history timeline of previous contacts. Right: an operator status panel with active calls, queue length and a small SLA gauge. A green call button. Top bar with the attached logo placed at the top left.

### 2. Паритетбанк — автоматизация B2B-направления
**Лого:** ✅ нужно, в `logos` его нет, пришлите свой файл.

> [общая часть Битрикс24] B2B sales pipeline for a bank: a CRM kanban of deals with 5 stages (new, qualification, proposal, contract, service), deal cards with company name, amount and responsible avatar, stage totals in column headers. On the right, a call widget with a live call timer, a recording waveform and a client snapshot. Above the kanban, a small flow strip with linked steps: telephony, CRM, back-office. Top bar with the attached logo at the top left.

### 3. Helix — доработка Битрикс24 для лаборатории
**Лого:** ✅ нужно, `logos/helix.png`.

> [общая часть Битрикс24] Customer complaints and requests list in a CRM for a medical laboratory network: a smart-process table with columns number, topic, branch, stage chip (new, in progress, resolved), responsible avatar and deadline. A filter row above the table, a small summary panel with a line chart of resolution time and two KPI numbers on the right. Top bar with the attached logo at the top left. Key content concentrated in the left 70 % of the frame.

### 4. Imkliva Insurance — обработка обращений в Битрикс24
**Лого:** ✅ нужно, `logos/imkliva.png`.

> [общая часть Битрикс24] Open-lines inbox for an insurance company: a vertical list of incoming requests with channel badges (e-mail, Viber, website chat, phone) and priority tags, a chat thread in the centre with a client policy summary card, and an automation rule chip like "auto-assigned to the claims team". A small routing diagram showing channels merging into one queue. Top bar with the attached logo at the top left. Key content concentrated in the left 70 % of the frame.

### 5. А-100 — Telegram и PWA-приложение для клиентов АЗС
**Лого:** ✅ нужно, `logos/a-100.png`. Это не Битрикс24, а приложение клиента, поэтому в цветах А-100 (оранжево-красный).

> Three smartphone screens side by side, slightly overlapping, cropped at the bottom, white UI with orange-red brand accent. Screen 1: map with fuel station pins and a bottom sheet with fuel prices. Screen 2: a loyalty card with a QR code and a points balance. Screen 3: a fuel order flow with a pump selector and a pay button. A small Telegram-style header bar on the first screen. The attached logo placed in the app header of the first screen. No hands, thin device bezels, clean flat shadows. Key content concentrated in the left 70 % of the frame.


---

## Советы по генерации

- Если нейросеть выдаёт тёмный фон или холодную палитру, добавьте в промпт: `warm color palette, light airy mood, no dark background`.
- Для единого стиля всех 3D-иконок генерируйте их подряд в одной сессии с одним и тем же seed или референсом.
- Прозрачность проверяйте на светло-сером фоне: белый ореол по краю означает, что объект плохо вырезан.
