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
];

const CALC_STEP_TITLES = ["Выберите услугу", "Что конкретно необходимо?", "Подробности проекта"];

const calcCapitalize = (text) => text.charAt(0).toUpperCase() + text.slice(1);

function calcEscape(text) {
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function initCalculator(root) {
  if (!root) return;

  const stage = root.querySelector("[data-calc-stage]");
  const body = root.querySelector("[data-calc-body]");
  const title = root.querySelector("[data-calc-title]");
  const contact = root.querySelector("[data-calc-contact]");
  const summary = root.querySelector("[data-calc-summary]");
  const brief = root.querySelector("[data-calc-brief]");
  const counter = root.querySelector("[data-calc-counter]");
  const back = root.querySelector("[data-calc-back]");
  const next = root.querySelector("[data-calc-next]");
  const backFromContact = root.querySelector("[data-calc-back-contact]");
  const nav = root.querySelector(".calc__nav");
  const trackerItems = [...root.querySelectorAll("[data-calc-tracker] > li")];

  const state = { step: 0, service: null, need: null, answers: {} };
  let advanceTimer = 0;

  const service = () => CALC_SERVICES[state.service];
  const need = () => service()?.needs[state.need];
  const isStepDone = () => (state.step === 0 ? state.service !== null : state.step === 1 ? state.need !== null : true);

  function optionHtml({ type, name, value, label, checked }) {
    return `<label class="calc-option calc-option--${type}">
      <input class="calc-option__input" type="${type}" name="${name}" value="${calcEscape(String(value))}"${checked ? " checked" : ""} />
      <span class="calc-option__text">${calcEscape(calcCapitalize(label))}</span>
    </label>`;
  }

  function renderChoice(kind, items, selected) {
    const options = items
      .map((label, index) => optionHtml({ type: "radio", name: `calc-${kind}`, value: index, label, checked: index === selected }))
      .join("");
    return `<fieldset class="calc__group" data-calc-kind="${kind}">
      <legend class="visually-hidden">${calcEscape(CALC_STEP_TITLES[state.step])}</legend>
      <div class="calc__options calc__options--large">${options}</div>
    </fieldset>`;
  }

  function renderQuestion(question, index) {
    const saved = state.answers[index];
    if (question.type === "text") {
      return `<div class="calc__group">
        <label class="calc__question" for="calc-text-${index}">${calcEscape(question.text)}</label>
        <textarea class="lead-form__control lead-form__control--area" id="calc-text-${index}" rows="2" data-calc-text="${index}">${calcEscape(saved || "")}</textarea>
      </div>`;
    }
    const options = question.options
      .map((label) =>
        optionHtml({
          type: question.type,
          name: `calc-q-${index}`,
          value: label,
          label,
          checked: question.type === "radio" ? saved === label : Boolean(saved?.includes(label)),
        }),
      )
      .join("");
    return `<fieldset class="calc__group" data-calc-question="${index}">
      <legend class="calc__question">${calcEscape(question.text)}${question.type === "checkbox" ? '<span class="calc__hint">Можно выбрать несколько</span>' : ""}</legend>
      <div class="calc__options">${options}</div>
    </fieldset>`;
  }

  function briefLines() {
    const lines = [`Услуга: ${service().name}`, `Что необходимо: ${need().name}`];
    need().questions.forEach((question, index) => {
      const answer = state.answers[index];
      const text = Array.isArray(answer) ? answer.join(", ") : answer;
      if (text) lines.push(`${question.text} ${text}`);
    });
    return lines;
  }

  function render() {
    const onContact = state.step === CALC_LAST_STEP;
    title.hidden = onContact;
    body.hidden = onContact;
    contact.hidden = !onContact;

    if (state.step === 0) {
      body.innerHTML = renderChoice("service", CALC_SERVICES.map((item) => item.name), state.service);
    } else if (state.step === 1) {
      body.innerHTML = renderChoice("need", service().needs.map((item) => item.name), state.need);
    } else if (state.step === 2) {
      body.innerHTML = need().questions.map(renderQuestion).join("");
    } else {
      summary.textContent = `${service().name} → ${need().name}`;
      brief.value = briefLines().join("\n");
    }
    if (!onContact) title.textContent = CALC_STEP_TITLES[state.step];

    counter.textContent = `Шаг ${state.step + 1} из ${CALC_LAST_STEP + 1}`;
    back.hidden = state.step === 0;
    // На последнем шаге «Назад» стоит рядом с кнопкой отправки внутри формы
    nav.hidden = onContact;
    next.disabled = !isStepDone();
    trackerItems.forEach((item, index) => {
      item.classList.toggle("is-done", index < state.step);
      item.classList.toggle("is-current", index === state.step);
      if (index === state.step) item.setAttribute("aria-current", "step");
      else item.removeAttribute("aria-current");
    });
  }

  function go(step, { moveFocus = true } = {}) {
    clearTimeout(advanceTimer);
    state.step = step;
    render();
    // Перезапуск анимации появления шага
    stage.classList.remove("is-entering");
    void stage.offsetWidth;
    stage.classList.add("is-entering");
    if (moveFocus) stage.focus({ preventScroll: true });
  }

  stage.addEventListener("change", (event) => {
    const input = event.target;
    const group = input.closest("[data-calc-kind], [data-calc-question]");
    if (!group) return;

    if (group.dataset.calcKind === "service") {
      if (state.service !== Number(input.value)) {
        state.service = Number(input.value);
        state.need = null;
        state.answers = {};
      }
    } else if (group.dataset.calcKind === "need") {
      if (state.need !== Number(input.value)) {
        state.need = Number(input.value);
        state.answers = {};
      }
    } else {
      const index = Number(group.dataset.calcQuestion);
      state.answers[index] =
        input.type === "radio" ? input.value : [...group.querySelectorAll("input:checked")].map((item) => item.value);
      return;
    }

    next.disabled = !isStepDone();
    // Выбор услуги и задачи сразу ведёт дальше; короткая пауза, чтобы успеть увидеть выбранный вариант
    advanceTimer = setTimeout(() => go(state.step + 1), CALC_ADVANCE_DELAY);
  });

  stage.addEventListener("input", (event) => {
    if (event.target.dataset.calcText === undefined) return;
    state.answers[Number(event.target.dataset.calcText)] = event.target.value.trim();
  });

  back.addEventListener("click", () => go(state.step - 1));
  backFromContact.addEventListener("click", () => go(state.step - 1));
  next.addEventListener("click", () => go(state.step + 1));

  render();
}

window.initCalculator = initCalculator;
