// Конструктор задачи: услуга → что нужно → подробности → контакты.
// Вопросы и варианты ответов взяты с itach-soft.ru. Стоимость не считается: заявка с ответами уходит менеджерам.

const CALC_LAST_STEP = 3;
const CALC_ADVANCE_DELAY = 260;

const calcRadio = (text, ...options) => ({ text, type: "radio", options });
const calcCheck = (text, ...options) => ({ text, type: "checkbox", options });
const calcFree = (text) => ({ text, type: "text", options: [] });

const SUPPORT_HOURS = calcRadio("Какое количество часов технической поддержки необходимо?", "до 10 ч/месяц", "10–20 ч/месяц", "свыше 20 ч/месяц");
const SUPPORT_SLA = calcRadio(
  "Какой уровень SLA (уровень обслуживания) необходим для вашего бизнеса?",
  "поддержка в рабочее время",
  "поддержка в рабочее время и разовые обращения во внерабочее время",
  "поддержка 24/7, включая выходные и праздничные дни",
);
const SUPPORT_TOPICS = (first) =>
  calcCheck("Какие конкретные проблемы или вопросы требуют решения?", first, "исправление ошибок", "консультации", "доработки функционала", "все вышеперечисленное");
const SITE_FUNCTIONS = calcCheck("Какой функционал должен быть на сайте?", "форма обратной связи", "онлайн-чат", "несколько языковых версий", "другое");
const SITE_DESIGN = calcRadio("Рассматриваете разработку с уникальным дизайном или на шаблоне?", "на шаблоне", "с уникальным дизайном", "не определено");
const PBX_FUNCTIONS = (text) =>
  calcCheck(text, "многоканальность", "автообзвон", "запись звонков", "мониторинг загруженности линий", "переадресация и удержание вызова", "голосовой помощник", "отчётность и статистика");
const SITE_SECTIONS = (...options) => calcRadio("Сколько разделов будет на сайте?", ...options);

const CALC_SERVICES = [
  {
    name: "Битрикс24",
    needs: [
      {
        name: "Внедрение Битрикс24",
        questions: [
          calcRadio("Требуется внедрение облачной или коробочной версии Битрикс24?", "облачная версия", "коробочная версия", "не определено"),
          calcRadio("Какое количество сотрудников будет пользоваться Битрикс24?", "5", "50–100", "250–500", "более 1000"),
          calcRadio("Есть ли требования безопасности в части размещения Битрикс24 на собственном сервере?", "да", "нет", "не определено"),
        ],
      },
      {
        name: "Настройка Битрикс24",
        questions: [
          calcCheck(
            "Какие бизнес-процессы и рабочие потоки нужно оптимизировать?",
            "процесс продаж",
            "согласование документов",
            "отчётность",
            "внутренние процессы компании (задачи, уведомления, статусы)",
            "все вышеперечисленное",
            "другие процессы",
          ),
          calcCheck("С какими сервисами требуется интегрировать Битрикс24?", "IP-телефония", "1С", "сайт", "иные"),
        ],
      },
      {
        name: "Техническая поддержка Битрикс24",
        questions: [SUPPORT_TOPICS("мониторинг работоспособности Битрикс24"), SUPPORT_HOURS, SUPPORT_SLA],
      },
      {
        name: "Обучение Битрикс24",
        questions: [
          calcRadio("Требуется ли составление инструкции по работе с Битрикс24 и его отдельными модулями?", "да", "нет", "не определено"),
          calcRadio("Сколько сотрудников требуется обучить?", "до 5", "5–15", "15–30", "более 30"),
          calcRadio("Необходимо ли проведение обучения в офисе компании или онлайн?", "онлайн", "в офисе компании"),
        ],
      },
      {
        name: "Доработка Битрикс24",
        questions: [
          calcCheck("Какого рода доработки необходимы?", "настройка интеграций", "устранение ошибок", "улучшение производительности", "доработка модулей и функционала Битрикс24", "все вышеперечисленное"),
          calcRadio("Есть ли техническое задание (перечень доработок)?", "да", "нет"),
        ],
      },
      {
        name: "Автоматизация бизнес-процессов в Битрикс24",
        questions: [
          calcCheck("Какие бизнес-процессы требуют автоматизации?", "управление продажами", "управление маркетингом", "управление финансами", "HR-процессы", "все вышеперечисленное"),
          calcRadio("Есть ли у вас техническое задание на автоматизацию бизнес-процессов?", "да", "нет"),
        ],
      },
      {
        name: "Установка коробочной версии Битрикс24",
        questions: [
          calcRadio("Сколько сотрудников будет пользоваться Битрикс24?", "12–50", "100–250", "500–1000", "более 1000"),
          calcRadio(
            "Необходимо ли дополнительное обучение или консультации по управлению и администрированию коробочной версии Битрикс24?",
            "да",
            "нет",
            "не определено",
          ),
        ],
      },
    ],
  },
  {
    name: "IP-АТС на базе Asterisk",
    needs: [
      {
        name: "Возможности и решения VoIP-АТС под ключ",
        questions: [
          calcRadio("Сколько пользователей будет включено в систему IP-АТС?", "до 5", "5–10", "10–30", "30–50", "свыше 50"),
          calcRadio("Есть ли у вас необходимое оборудование для IP-телефонии?", "да", "нет"),
          PBX_FUNCTIONS("Какие функции и возможности требуются: маршрутизация вызовов, автоматическое распределение, мультиконференции и т. д.?"),
        ],
      },
      {
        name: "Настройка VoIP Asterisk",
        questions: [
          calcRadio("Сколько пользователей будет использовать VoIP-связь на сервере?", "до 5", "5–10", "10–30", "30–50", "свыше 50"),
          PBX_FUNCTIONS("Какие функции и возможности требуются: маршрутизация вызовов, интерактивное меню, запись разговоров и т. д.?"),
          calcRadio("Есть ли специфические требования к интеграции с другими системами или оборудованием?", "да", "нет"),
        ],
      },
      {
        name: "Обеспечение безопасности VoIP-АТС",
        questions: [
          calcFree("От каких уязвимостей и угроз безопасности требуется защититься?"),
          calcFree("Какие методы аутентификации и шифрования должны быть реализованы?"),
          calcFree("Есть ли специфические требования к обеспечению безопасности, учитывая особенности вашей инфраструктуры?"),
        ],
      },
      {
        name: "Техническая поддержка VoIP-телефонных станций",
        questions: [SUPPORT_TOPICS("мониторинг работоспособности"), SUPPORT_HOURS, SUPPORT_SLA],
      },
    ],
  },
  {
    name: "Создание сайтов",
    needs: [
      { name: "Сайт-визитка", questions: [SITE_SECTIONS("2", "2–3", "3–5"), SITE_FUNCTIONS, SITE_DESIGN] },
      { name: "Корпоративный сайт", questions: [SITE_SECTIONS("до 5", "5–10", "10–15"), SITE_FUNCTIONS, SITE_DESIGN] },
      {
        name: "Интернет-магазин",
        questions: [
          SITE_SECTIONS("до 5", "5–10", "10–15"),
          calcCheck("Какой функционал должен быть на сайте?", "промокоды и скидки", "личный кабинет", "корзина", "онлайн-оплата", "несколько языковых версий", "онлайн-чат", "форма обратной связи"),
          calcCheck("С какими сервисами требуется интеграция?", "платёжные системы", "службы доставки", "CSV/XLS файлы", "1С", "другое"),
          calcRadio("Рассматриваете разработку с уникальным дизайном или на шаблоне?", "на шаблоне", "с уникальным дизайном", "не определено"),
        ],
      },
      {
        name: "Лендинг",
        questions: [calcRadio("Требуется ли административная панель для управления контентом на сайте?", "да", "нет", "не определено"), SITE_FUNCTIONS, SITE_DESIGN],
      },
      {
        name: "Обслуживание сайтов",
        questions: [SUPPORT_TOPICS("мониторинг работоспособности"), SUPPORT_HOURS, SUPPORT_SLA],
      },
      {
        name: "Сайты государственных организаций и органов управления",
        questions: [
          SITE_SECTIONS("до 5", "5–10", "10–15"),
          calcCheck("Какой функционал должен быть на сайте?", "форма обратной связи", "версия для слабовидящих", "несколько языковых версий", "другое"),
          SITE_DESIGN,
        ],
      },
    ],
  },
  {
    name: "Аутстаффинг и IT-услуги",
    needs: [
      {
        name: "IT-аутстаффинг",
        questions: [
          calcCheck("Какие специалисты нужны?", "разработчики", "аналитики", "тестировщики", "системные инженеры и DevOps", "менеджеры проектов"),
          calcRadio("Какая загрузка требуется?", "полная занятость", "частичная занятость", "не определено"),
          calcRadio("На какой срок нужен специалист?", "до 1 месяца", "1–3 месяца", "3–6 месяцев", "более 6 месяцев"),
        ],
      },
      {
        name: "Предоставление IT-специалистов под задачи бизнеса",
        questions: [
          calcCheck("Каких специалистов требуется подобрать?", "разработчики", "аналитики", "UX/UI-дизайнеры", "тестировщики", "системные инженеры и DevOps"),
          calcRadio("На какой срок нужен специалист?", "до 1 месяца", "1–3 месяца", "3–6 месяцев", "более 6 месяцев"),
          calcFree("Опишите задачу, стек и требования к специалисту"),
        ],
      },
      {
        name: "IT-консультации",
        questions: [
          calcCheck("Какая консультация требуется?", "аудит решения или кода", "оценка сроков и бюджета", "выбор платформы или подрядчика", "план развития"),
          calcRadio("В каком формате удобны консультации?", "онлайн", "в офисе компании", "гибридный формат"),
          calcFree("Какой результат консультации вам нужен?"),
        ],
      },
    ],
  },
  {
    name: "AI-разработка",
    needs: [
      {
        name: "AI-чат-боты и виртуальные ассистенты",
        questions: [
          calcCheck("Где должен работать бот?", "на сайте", "в мессенджерах", "в Битрикс24", "в нескольких каналах"),
          calcRadio("Какой объём обращений в месяц?", "до 500", "500–2 000", "2 000–10 000", "более 10 000"),
          calcRadio("Откуда бот берёт ответы?", "из базы знаний компании", "из данных CRM", "по заданному сценарию", "не определено"),
        ],
      },
      {
        name: "Корпоративные AI-ассистенты",
        questions: [
          calcCheck("Какие данные должен знать ассистент?", "регламенты и инструкции", "договоры", "техническая документация", "данные внутренних систем"),
          calcRadio("Сколько сотрудников будет пользоваться ассистентом?", "до 10", "10–50", "50–200", "более 200"),
          calcFree("Какие задачи ассистент должен закрывать в первую очередь?"),
        ],
      },
      {
        name: "AI-интеграции с CRM Битрикс24",
        questions: [
          calcCheck("Какие процессы нужно автоматизировать?", "обработка лидов", "подсказки менеджеру", "подготовка ответов клиентам", "постановка задач", "все вышеперечисленное"),
          calcRadio("Какая версия Битрикс24 используется?", "облачная", "коробочная", "не определено"),
          calcRadio("Требуется ли доступ к переписке и звонкам клиентов?", "да", "нет", "не определено"),
        ],
      },
      {
        name: "Интеллектуальный поиск по документам",
        questions: [
          calcCheck("По каким документам нужен поиск?", "договоры", "регламенты и инструкции", "техническая документация", "база знаний поддержки"),
          calcRadio("Сколько документов в базе?", "до 1 000", "1 000–10 000", "10 000–100 000", "более 100 000"),
          calcRadio("Нужно ли разграничение доступа к документам?", "да", "нет", "не определено"),
        ],
      },
      {
        name: "AI для обработки документов",
        questions: [
          calcCheck("Какие типы документов нужно обрабатывать?", "счета и акты", "договоры", "заявления и заявки", "сканы и фотографии"),
          calcCheck("Какие данные нужно извлекать?", "реквизиты", "суммы", "даты", "позиции и номенклатуру", "другое"),
          calcRadio("Куда передавать результат?", "в 1С", "в Битрикс24", "в собственную систему", "не определено"),
        ],
      },
      {
        name: "Предиктивная аналитика",
        questions: [
          calcRadio("Что нужно прогнозировать?", "продажи", "спрос", "загрузку", "отток клиентов", "несколько показателей"),
          calcRadio("За какой период есть исторические данные?", "до 6 месяцев", "6–12 месяцев", "1–3 года", "более 3 лет"),
          calcFree("Какие системы хранят данные для анализа?"),
        ],
      },
      {
        name: "Рекомендательные системы",
        questions: [
          calcRadio("Где должны показываться рекомендации?", "на сайте", "в приложении", "в личном кабинете", "в рассылках"),
          calcRadio("Сколько товаров или услуг в каталоге?", "до 1 000", "1 000–10 000", "10 000–100 000", "более 100 000"),
          calcRadio("Есть ли история покупок или поведения клиентов?", "да", "нет", "не определено"),
        ],
      },
      {
        name: "AI-модули для сайтов и веб-сервисов",
        questions: [
          calcCheck("Какие функции нужны?", "умный поиск", "подсказки и персональные блоки", "обработка заявок", "автоматические ответы в чате"),
          calcRadio("На какой платформе работает сайт или сервис?", "1С-Битрикс", "собственная разработка", "другая CMS", "не определено"),
          calcFree("Опишите, как функция должна работать в интерфейсе"),
        ],
      },
      {
        name: "Компьютерное зрение",
        questions: [
          calcCheck("Что нужно распознавать?", "объекты на фото", "дефекты", "номера", "текст на изображениях", "другое"),
          calcRadio("Откуда поступают изображения?", "с камер", "из загружаемых фото", "из видеоархива", "из мобильного приложения"),
          calcRadio("Нужна ли работа в реальном времени?", "да", "нет", "не определено"),
        ],
      },
      {
        name: "AI для анализа обращений и коммуникаций",
        questions: [
          calcCheck("Что нужно анализировать?", "переписки и чаты", "звонки и расшифровки", "отзывы", "заявки и обращения"),
          calcCheck("Какие результаты нужны?", "тема обращения", "срочность", "эмоциональная окраска", "контроль качества", "маршрутизация"),
          calcRadio("Что делать с результатами?", "отчёт для руководителей", "автоматическая маршрутизация", "оповещения в реальном времени", "не определено"),
        ],
      },
    ],
  },
];

// ---------------------------------------------------------------- цены и расчёт
// База — опубликованные на сайте цены «от». Вилка ориентировочная:
// сложность поднимает верхнюю границу, интеграции и дизайн добавляют проценты.
const CALC_PRICES = {
  "Битрикс24|Внедрение Битрикс24": 90000,
  "Битрикс24|Настройка Битрикс24": 90000,
  "Битрикс24|Техническая поддержка Битрикс24": { price: 9000, unit: "monthly" },
  "Битрикс24|Обучение Битрикс24": 9000,
  "Битрикс24|Доработка Битрикс24": 60000,
  "Битрикс24|Автоматизация бизнес-процессов в Битрикс24": 60000,
  "Битрикс24|Установка коробочной версии Битрикс24": 90000,
  "IP-АТС на базе Asterisk|Возможности и решения VoIP-АТС под ключ": 90000,
  "IP-АТС на базе Asterisk|Настройка VoIP Asterisk": 45000,
  "IP-АТС на базе Asterisk|Обеспечение безопасности VoIP-АТС": 45000,
  "IP-АТС на базе Asterisk|Техническая поддержка VoIP-телефонных станций": { price: 9000, unit: "monthly" },
  "Создание сайтов|Сайт-визитка": 120000,
  "Создание сайтов|Корпоративный сайт": 195000,
  "Создание сайтов|Интернет-магазин": 290000,
  "Создание сайтов|Лендинг": 150000,
  "Создание сайтов|Обслуживание сайтов": { price: 9000, unit: "monthly" },
  "Создание сайтов|Сайты государственных организаций и органов управления": 350000,
  "Аутстаффинг и IT-услуги|IT-аутстаффинг": { price: 2880, unit: "hourly" },
  "Аутстаффинг и IT-услуги|Предоставление IT-специалистов под задачи бизнеса": { price: 2880, unit: "hourly" },
  "Аутстаффинг и IT-услуги|IT-консультации": { price: 2880, unit: "hourly" },
  "AI-разработка|AI-чат-боты и виртуальные ассистенты": 150000,
  "AI-разработка|Корпоративные AI-ассистенты": 300000,
  "AI-разработка|AI-интеграции с CRM Битрикс24": 240000,
  "AI-разработка|Интеллектуальный поиск по документам": 300000,
  "AI-разработка|AI для обработки документов": 300000,
  "AI-разработка|Предиктивная аналитика": 450000,
  "AI-разработка|Рекомендательные системы": 450000,
  "AI-разработка|AI-модули для сайтов и веб-сервисов": 150000,
  "AI-разработка|Компьютерное зрение": 300000,
  "AI-разработка|AI для анализа обращений и коммуникаций": 240000,
};

const CALC_COMPLEXITY = [
  { label: "Простая", min: 1, max: 1.3 },
  { label: "Средняя", min: 1, max: 1.8 },
  { label: "Высокая", min: 1.25, max: 2.5 },
];
const CALC_SERVICE_KEYS = ["bitrix24", "asterisk", "sites", "outstaff", "ai"];
const CALC_MONTHLY_TIERS = [9000, 13500, 16500];
const CALC_INTEGRATION_RATE = 0.05;
const CALC_INTEGRATION_RATE_MAX = 0.08;
const CALC_DESIGN_RATE = 0.2;
const CALC_DESIGN_RATE_MAX = 0.3;
const CALC_MONTHLY_MIN = 9000;
const CALC_MONTHLY_MAX = 16500;

let calcUid = 0;

const calcCapitalize = (text) => text.charAt(0).toUpperCase() + text.slice(1);

function calcEscape(text) {
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

const formatMoney = (value) => Math.round(value).toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");

const roundTo = (value, step) => Math.round(value / step) * step;

function calcPriceInfo(service, need) {
  const entry = CALC_PRICES[`${service.name}|${need.name}`];
  if (entry === undefined) return { price: 0, unit: "project" };
  if (typeof entry === "number") return { price: entry, unit: "project" };
  return { price: entry.price, unit: entry.unit || "project" };
}

function calcEstimate(state) {
  const service = CALC_SERVICES[state.service];
  const need = service.needs[state.need];
  const info = calcPriceInfo(service, need);
  const complexity = CALC_COMPLEXITY[state.complexity];
  if (!info.price) return null;

  if (info.unit === "monthly") {
    const monthly = CALC_MONTHLY_TIERS[state.complexity];
    return { unit: "monthly", low: monthly, high: monthly, monthlyLow: 0, monthlyHigh: 0, rows: [] };
  }

  if (info.unit === "hourly") {
    return {
      unit: "hourly",
      low: roundTo(info.price * complexity.min, 10),
      high: roundTo(info.price * complexity.max, 10),
      monthlyLow: 0,
      monthlyHigh: 0,
      rows: [],
    };
  }

  const integrations = state.integrations;
  const devLow = roundTo(info.price * complexity.min, 5000);
  const devHigh = roundTo(info.price * complexity.max, 5000);
  const intLow = roundTo(devLow * CALC_INTEGRATION_RATE * integrations, 1000);
  const intHigh = roundTo(devHigh * CALC_INTEGRATION_RATE_MAX * integrations, 1000);
  const designLow = state.design ? roundTo(devLow * CALC_DESIGN_RATE, 1000) : 0;
  const designHigh = state.design ? roundTo(devHigh * CALC_DESIGN_RATE_MAX, 1000) : 0;
  const monthlyLow = state.support ? Math.max(CALC_MONTHLY_MIN, roundTo(info.price * 0.03, 500)) : 0;
  const monthlyHigh = state.support ? Math.max(CALC_MONTHLY_MAX, roundTo(info.price * 0.05, 500)) : 0;

  const rows = [{ label: "Разработка", low: devLow, high: devHigh }];
  if (integrations > 0) rows.push({ label: "Интеграции", low: intLow, high: intHigh });
  if (state.design) rows.push({ label: "Дизайн", low: designLow, high: designHigh });
  if (state.support) rows.push({ label: "Поддержка", low: monthlyLow, high: monthlyHigh, suffix: " ₽/мес" });

  return {
    unit: "project",
    low: devLow + intLow + designLow,
    high: devHigh + intHigh + designHigh,
    monthlyLow,
    monthlyHigh,
    rows,
  };
}

const rangeText = (low, high, suffix) =>
  low === high ? `${formatMoney(low)}${suffix}` : `${formatMoney(low)} – ${formatMoney(high)}${suffix}`;

function calcShell(id) {
  return `
    <div class="calc__choices glow-card">
      <fieldset class="calc__group">
        <legend class="calc__question">Услуга</legend>
        <div class="calc__options calc__options--large" data-calc-services></div>
      </fieldset>
      <fieldset class="calc__group">
        <legend class="calc__question">Задача</legend>
        <div class="calc__options calc__options--large" data-calc-needs></div>
      </fieldset>
      <fieldset class="calc__group">
        <legend class="calc__question">Сложность</legend>
        <div class="calc__options" data-calc-complexity></div>
      </fieldset>
      <div class="calc__group" data-calc-integrations-field>
        <label class="calc__question" for="calc-integrations-${id}">
          Интеграции с другими системами
          <output class="calc__range-value" for="calc-integrations-${id}" data-calc-range-value>1</output>
        </label>
        <input class="calc__range" id="calc-integrations-${id}" type="range" min="0" max="10" step="1" value="1" data-calc-integrations />
      </div>
      <div class="calc__toggles" data-calc-toggles>
        <label class="calc-toggle">
          <input class="calc-toggle__input" type="checkbox" data-calc-design />
          <span class="calc-toggle__switch" aria-hidden="true"></span>
          <span class="calc-toggle__text">
            <span class="calc-toggle__title">Дизайн (UX/UI)</span>
            <span class="calc-toggle__desc">Прототип и дизайн экранов до разработки</span>
          </span>
        </label>
        <label class="calc-toggle">
          <input class="calc-toggle__input" type="checkbox" checked data-calc-support />
          <span class="calc-toggle__switch" aria-hidden="true"></span>
          <span class="calc-toggle__text">
            <span class="calc-toggle__title">Поддержка и развитие</span>
            <span class="calc-toggle__desc">Обновления, исправления и доработки каждый месяц</span>
          </span>
        </label>
      </div>
      <div class="calc__questions" data-calc-questions></div>
    </div>
    <aside class="calc__price" aria-label="Ориентировочная стоимость">
      <p class="calc__price-eyebrow">Ориентировочная стоимость</p>
      <p class="calc__price-value" data-calc-price-value aria-live="polite">—</p>
      <p class="calc__price-monthly" data-calc-monthly hidden></p>
      <div class="calc__breakdown" data-calc-breakdown>
        <dl data-calc-breakdown-rows></dl>
      </div>
      <a class="btn btn--primary calc__cta" href="#lead" data-calc-quote>Получить точную смету</a>
      <p class="calc__note">Ориентировочная цена по опубликованным тарифам. Точная смета — после обсуждения задачи.</p>
    </aside>`;
}

function initCalculator(root) {
  if (!root) return;
  const config = root.querySelector("[data-calc-config]");
  if (!config) return;

  const id = ++calcUid;
  // На подстранице услуги калькулятор открывается на её направлении
  const defaultService = Math.max(0, CALC_SERVICE_KEYS.indexOf(config.dataset.calcDefault || "bitrix24"));
  const defaultNeed = Math.min(
    Number(config.dataset.calcDefaultNeed || 0),
    CALC_SERVICES[defaultService].needs.length - 1,
  );
  const state = {
    service: defaultService,
    need: defaultNeed,
    complexity: 1,
    integrations: 1,
    design: false,
    support: true,
    answers: {},
  };

  config.innerHTML = calcShell(id);

  const servicesEl = config.querySelector("[data-calc-services]");
  const needsEl = config.querySelector("[data-calc-needs]");
  const complexityEl = config.querySelector("[data-calc-complexity]");
  const integrationsField = config.querySelector("[data-calc-integrations-field]");
  const integrationsInput = config.querySelector("[data-calc-integrations]");
  const rangeValue = config.querySelector("[data-calc-range-value]");
  const toggles = config.querySelector("[data-calc-toggles]");
  const questionsEl = config.querySelector("[data-calc-questions]");
  const priceValue = config.querySelector("[data-calc-price-value]");
  const monthlyEl = config.querySelector("[data-calc-monthly]");
  const breakdown = config.querySelector("[data-calc-breakdown]");
  const breakdownRows = config.querySelector("[data-calc-breakdown-rows]");

  const service = () => CALC_SERVICES[state.service];
  const need = () => service().needs[state.need];

  function optionHtml(type, name, value, label, checked) {
    return `<label class="calc-option calc-option--${type}">
      <input class="calc-option__input" type="${type}" name="${name}" value="${calcEscape(String(value))}"${checked ? " checked" : ""} />
      <span class="calc-option__text">${calcEscape(calcCapitalize(label))}</span>
    </label>`;
  }

  function renderChoices() {
    servicesEl.innerHTML = CALC_SERVICES.map((item, index) =>
      optionHtml("radio", `calc-${id}-service`, index, item.name, index === state.service),
    ).join("");
    renderNeeds();
    complexityEl.innerHTML = CALC_COMPLEXITY.map((item, index) =>
      optionHtml("radio", `calc-${id}-complexity`, index, item.label, index === state.complexity),
    ).join("");
    renderQuestions();
  }

  function renderNeeds() {
    needsEl.innerHTML = service().needs.map((item, index) =>
      optionHtml("radio", `calc-${id}-need`, index, item.name, index === state.need),
    ).join("");
  }

  function renderQuestions() {
    questionsEl.innerHTML = need().questions.map((question, index) => {
      const saved = state.answers[index];
      if (question.type === "text") {
        return `<div class="calc__group">
          <label class="calc__question" for="calc-${id}-text-${index}">${calcEscape(question.text)}</label>
          <textarea class="lead-form__control lead-form__control--area" id="calc-${id}-text-${index}" rows="2" data-calc-text="${index}">${calcEscape(saved || "")}</textarea>
        </div>`;
      }
      const options = question.options.map((label) =>
        optionHtml(
          question.type,
          `calc-${id}-q-${index}`,
          label,
          label,
          question.type === "radio" ? saved === label : Boolean(saved?.includes(label)),
        ),
      ).join("");
      return `<fieldset class="calc__group" data-calc-question="${index}">
        <legend class="calc__question">${calcEscape(question.text)}${question.type === "checkbox" ? '<span class="calc__hint">Можно выбрать несколько</span>' : ""}</legend>
        <div class="calc__options">${options}</div>
      </fieldset>`;
    }).join("");
  }

  function updateVisibility() {
    const isProject = calcPriceInfo(service(), need()).unit === "project";
    integrationsField.hidden = !isProject;
    toggles.hidden = !isProject;
  }

  function updatePrice() {
    const estimate = calcEstimate(state);
    if (!estimate) {
      priceValue.textContent = "По запросу";
      monthlyEl.hidden = true;
      breakdown.hidden = true;
      return;
    }

    if (estimate.unit === "monthly") {
      priceValue.textContent = rangeText(estimate.low, estimate.high, " ₽/мес");
      monthlyEl.hidden = true;
      breakdown.hidden = true;
    } else if (estimate.unit === "hourly") {
      priceValue.textContent = rangeText(estimate.low, estimate.high, " ₽/час");
      monthlyEl.hidden = true;
      breakdown.hidden = true;
    } else {
      priceValue.textContent = rangeText(estimate.low, estimate.high, " ₽");
      monthlyEl.hidden = !estimate.monthlyHigh;
      if (!monthlyEl.hidden) {
        monthlyEl.innerHTML = `<span>Поддержка</span> ${rangeText(estimate.monthlyLow, estimate.monthlyHigh, " ₽/мес")}`;
      }
      breakdown.hidden = false;
      breakdownRows.innerHTML = estimate.rows
        .map(
          (row) =>
            `<div><dt>${row.label}</dt><dd>${rangeText(row.low, row.high, row.suffix || " ₽")}</dd></div>`,
        )
        .join("");
    }
  }

  function briefLines() {
    const estimate = calcEstimate(state);
    const lines = [
      `Услуга: ${service().name}`,
      `Задача: ${need().name}`,
      `Сложность: ${CALC_COMPLEXITY[state.complexity].label}`,
    ];
    if (estimate?.unit === "project") {
      lines.push(`Интеграций: ${state.integrations}`, `Дизайн: ${state.design ? "да" : "нет"}`, `Поддержка: ${state.support ? "да" : "нет"}`);
    }
    if (estimate) {
      const suffix = estimate.unit === "monthly" ? " ₽/мес" : estimate.unit === "hourly" ? " ₽/час" : " ₽";
      lines.push(`Ориентировочная стоимость: ${rangeText(estimate.low, estimate.high, suffix)}`);
    }
    need().questions.forEach((question, index) => {
      const answer = state.answers[index];
      const text = Array.isArray(answer) ? answer.join(", ") : answer;
      if (text) lines.push(`${question.text} ${text}`);
    });
    return lines;
  }

  function syncRange() {
    const value = Number(integrationsInput.value);
    rangeValue.textContent = String(value);
    integrationsInput.style.setProperty("--range-fill", `${(value / Number(integrationsInput.max)) * 100}%`);
  }

  config.addEventListener("change", (event) => {
    const input = event.target;

    if (input.name === `calc-${id}-service`) {
      state.service = Number(input.value);
      state.need = 0;
      state.answers = {};
      renderNeeds();
      renderQuestions();
      updateVisibility();
      updatePrice();
      return;
    }

    if (input.name === `calc-${id}-need`) {
      state.need = Number(input.value);
      state.answers = {};
      renderQuestions();
      updateVisibility();
      updatePrice();
      return;
    }

    if (input.name === `calc-${id}-complexity`) {
      state.complexity = Number(input.value);
      updatePrice();
      return;
    }

    if (input.matches("[data-calc-design]")) {
      state.design = input.checked;
      updatePrice();
      return;
    }

    if (input.matches("[data-calc-support]")) {
      state.support = input.checked;
      updatePrice();
      return;
    }

    const group = input.closest("[data-calc-question]");
    if (!group) return;
    const index = Number(group.dataset.calcQuestion);
    state.answers[index] =
      input.type === "radio" ? input.value : [...group.querySelectorAll("input:checked")].map((item) => item.value);
  });

  config.addEventListener("input", (event) => {
    if (event.target.matches("[data-calc-integrations]")) {
      state.integrations = Number(event.target.value);
      syncRange();
      updatePrice();
      return;
    }
    if (event.target.matches("[data-calc-text]")) {
      state.answers[Number(event.target.dataset.calcText)] = event.target.value.trim();
    }
  });

  // CTA кладёт собранный бриф в поле задачи и открывает форму заявки.
  // Ссылку создаём после инициализации общей формы, поэтому обработчик свой
  config.addEventListener("click", (event) => {
    const cta = event.target.closest("[data-calc-quote]");
    if (!cta) return;
    const task = document.getElementById("modal-task");
    if (task) task.value = briefLines().join("\n");
    const modal = document.querySelector("[data-lead-modal]");
    if (modal && typeof modal.showModal === "function") {
      event.preventDefault();
      // Из попапа калькулятора не наслаиваем окна: сначала закрываем его
      const calcModal = cta.closest("[data-calc-modal]");
      if (calcModal?.open) calcModal.close();
      modal.showModal();
    }
  });

  renderChoices();
  syncRange();
  updateVisibility();
  updatePrice();

  root.resetCalculator = () => {
    state.service = defaultService;
    state.need = defaultNeed;
    state.complexity = 1;
    state.integrations = 1;
    state.design = false;
    state.support = true;
    state.answers = {};
    integrationsInput.value = "1";
    renderChoices();
    syncRange();
    updateVisibility();
    updatePrice();
  };
}

window.initCalculator = initCalculator;

// Попап с калькулятором: собирается здесь и добавляется на каждую страницу,
// чтобы кнопка «Рассчитать стоимость» в мега-меню открывала его на месте,
// а не вела на главную.
const CALC_POPUP_HTML = `
<dialog class="modal calc-modal" data-calc-modal aria-labelledby="calc-modal-title">
  <div class="modal__panel">
    <button class="modal__close" type="button" aria-label="Закрыть" data-calc-modal-close>
      <svg class="icon" aria-hidden="true"><use href="#icon-close" /></svg>
    </button>
    <h2 class="modal__title" id="calc-modal-title">Рассчитайте стоимость <span class="section-title__muted">за 2 минуты</span></h2>
    <div class="calc__panel" data-calc>
      <div class="calc__config" data-calc-config></div>
    </div>
  </div>
</dialog>`;

function buildCalcPopup() {
  if (document.querySelector("[data-calc-modal]")) return;
  document.body.insertAdjacentHTML("beforeend", CALC_POPUP_HTML);
}

buildCalcPopup();
