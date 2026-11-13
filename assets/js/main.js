const header = document.querySelector("[data-header]");
const menuToggle = document.querySelector("[data-menu-toggle]");

const SCROLLED_OFFSET = 8;
const SITES_SCROLL_RATIO = 0.6;
// Сдвиг указателя дольше этого — перетаскивание ленты, а не клик по карточке
const SITES_CLICK_SLOP = 6;
const SITES_FOLLOW = 0.14;
const SITES_FRICTION = 0.94;
const SITES_STOP_SPEED = 0.1;
const SITES_WHEEL_LINE_PX = 16;
const DESKTOP_QUERY = window.matchMedia("(min-width: 1024px)");

function updateHeaderState() {
  header.classList.toggle("is-scrolled", window.scrollY > SCROLLED_OFFSET);
}

function setMenuOpen(isOpen) {
  header.classList.toggle("is-menu-open", isOpen);
  // Полноэкранное меню: прокрутка страницы за ним блокируется
  document.body.classList.toggle("menu-locked", isOpen);
  menuToggle.setAttribute("aria-expanded", String(isOpen));
  menuToggle.setAttribute("aria-label", isOpen ? "Закрыть меню" : "Открыть меню");
}

function initHeader() {
  updateHeaderState();
  window.addEventListener("scroll", updateHeaderState, { passive: true });

  menuToggle.addEventListener("click", () => {
    setMenuOpen(menuToggle.getAttribute("aria-expanded") !== "true");
  });

  // Аккордеоны бургер-меню («Услуги», «Компания»): список раскрывается под пунктом
  header.querySelectorAll("[data-submenu-toggle]").forEach((toggle) => {
    const submenu = document.getElementById(toggle.getAttribute("aria-controls"));
    if (!submenu) return;

    toggle.addEventListener("click", (event) => {
      event.stopPropagation();
      const open = toggle.getAttribute("aria-expanded") !== "true";
      toggle.setAttribute("aria-expanded", String(open));
      submenu.hidden = !open;
    });

    // Клик по пункту списка закрывает всё меню, как остальные пункты
    submenu.addEventListener("click", () => setMenuOpen(false));
  });

  header.addEventListener("click", (event) => {
    if (event.target.closest(".nav__link, .nav__phone")) setMenuOpen(false);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && header.classList.contains("is-menu-open")) {
      setMenuOpen(false);
      menuToggle.focus();
    }
  });

  DESKTOP_QUERY.addEventListener("change", (event) => {
    if (event.matches) setMenuOpen(false);
  });
}

// Градиентный контур карточек следует за курсором; координаты переводим в систему самой карточки
// (она может быть уменьшена transform: scale, как в стопке услуг)
function initGlowCards() {
  // Один обработчик на документ: карточки в окнах кейсов появляются позже, при открытии
  document.addEventListener(
    "pointermove",
    (event) => {
      const card = event.target.closest?.(".glow-card");
      if (!card) return;
      const rect = card.getBoundingClientRect();
      const scale = card.offsetWidth / rect.width;
      card.style.setProperty("--mx", `${(event.clientX - rect.left) * scale}px`);
      card.style.setProperty("--my", `${(event.clientY - rect.top) * scale}px`);
    },
    { passive: true },
  );
}

// «Кому подходит»: селектор аудиторий. Панель переключается наведением на десктопе
// и кликом везде; стрелки двигают выбранный таб
function initTabPicker(picker) {
  const tabs = [...picker.querySelectorAll("[role='tab']")];
  const panels = [...picker.querySelectorAll("[role='tabpanel']")];
  // Переключение наведением — только если пикер явно не просил клик
  const hoverSwitch =
    window.matchMedia("(hover: hover)").matches &&
    !picker.hasAttribute("data-no-hover-switch");

  function select(index, focusTab = false) {
    tabs.forEach((tab, i) => {
      const on = i === index;
      tab.classList.toggle("is-active", on);
      tab.setAttribute("aria-selected", String(on));
      tab.tabIndex = on ? 0 : -1;
    });
    panels.forEach((panel, i) => panel.classList.toggle("is-active", i === index));
    if (focusTab) tabs[index].focus();
  }

  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => {
      select(index);
      // На узком экране выбранный таб может уйти за край ленты — докручиваем
      tab.scrollIntoView({ block: "nearest", inline: "center", behavior: "smooth" });
    });
    if (hoverSwitch) {
      tab.addEventListener("pointerenter", () => select(index));
    }
    tab.addEventListener("keydown", (event) => {
      const step = { ArrowDown: 1, ArrowUp: -1, ArrowRight: 1, ArrowLeft: -1 }[event.key];
      if (!step) return;
      event.preventDefault();
      select((index + step + tabs.length) % tabs.length, true);
    });
  });

  select(0);
}

function initAudiencePicker() {
  // Селектор аудиторий «Кому подходит» и селектор инструментов — один паттерн табов
  document
    .querySelectorAll("[data-audience-picker], [data-tools-picker]")
    .forEach(initTabPicker);
}

// Стопка карточек услуг: чем больше карточек легло сверху, тем сильнее нижняя уменьшается и темнеет
function initServiceStack() {
  const stack = document.querySelector("[data-service-stack]");
  if (!stack) return;
  const cards = [...stack.querySelectorAll(".service-card")];
  let frame = 0;
  let stackWidth = 0;

  // Все карточки одной высоты: по самой высокой при текущей ширине
  function equalizeHeights() {
    stack.style.removeProperty("--card-height");
    const tallest = Math.max(...cards.map((card) => card.offsetHeight));
    stack.style.setProperty("--card-height", `${tallest}px`);
  }

  new ResizeObserver(([entry]) => {
    if (entry.contentRect.width === stackWidth) return;
    stackWidth = entry.contentRect.width;
    equalizeHeights();
  }).observe(stack);

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  function update() {
    frame = 0;
    // q — насколько карточка уже наехала на предыдущую (0 — ещё внизу, 1 — закреплена)
    const covered = cards.map((card, index) => {
      if (index === 0) return 0;
      const previousHeight = cards[index - 1].offsetHeight;
      const stickyTop = parseFloat(getComputedStyle(card).top);
      const offset = card.getBoundingClientRect().top - stickyTop;
      return Math.min(Math.max(1 - offset / previousHeight, 0), 1);
    });
    cards.forEach((card, index) => {
      const depth = covered.slice(index + 1).reduce((sum, value) => sum + value, 0);
      card.style.setProperty("--depth", depth.toFixed(3));
    });
  }

  window.addEventListener(
    "scroll",
    () => {
      if (!frame) frame = requestAnimationFrame(update);
    },
    { passive: true },
  );
  update();
}

// Направления услуг на телефоне: табы с разделами, показывается карточка выбранного. На широких экранах табы скрыты стилями
function initServiceTabs(list) {
  if (!list) return;
  const cards = [...list.children];
  const tabs = document.createElement("div");
  tabs.className = "service-tabs";
  tabs.setAttribute("role", "tablist");
  tabs.setAttribute("aria-label", "Направления услуг");
  list.before(tabs);

  const buttons = cards.map((card, index) => {
    card.id = `service-panel-${index}`;
    card.setAttribute("role", "tabpanel");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "service-tab";
    button.setAttribute("role", "tab");
    button.setAttribute("aria-controls", card.id);
    button.textContent = card.querySelector(".service-card__title").textContent;
    button.addEventListener("click", () => {
      select(index);
      button.scrollIntoView({ block: "nearest", inline: "center", behavior: "smooth" });
    });
    tabs.append(button);
    return button;
  });

  function select(active) {
    cards.forEach((card, index) => card.classList.toggle("is-active", index === active));
    buttons.forEach((button, index) => button.setAttribute("aria-selected", String(index === active)));
  }

  select(0);
}

// «Проблемы, которые снимаем»: строки оживают по мере скролла — слово и штамп
// приходят в цвет, когда строка доезжает до линии фокуса (как шаги процесса)
function initProblemRows() {
  const list = document.querySelector("[data-problem-rows]");
  if (!list) return;
  const rows = [...list.querySelectorAll(".problem-row")];
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const FOCUS_LINE = 0.6;
  let frame = 0;

  function update() {
    frame = 0;
    const focusY = window.innerHeight * FOCUS_LINE;
    rows.forEach((row) => {
      const active = reducedMotion || row.getBoundingClientRect().top + 24 < focusY;
      row.classList.toggle("is-active", active);
    });
  }

  const schedule = () => {
    if (!frame) frame = requestAnimationFrame(update);
  };
  addEventListener("scroll", schedule, { passive: true });
  addEventListener("resize", schedule);
  update();
}

// «Как мы работаем»: линия рисуется по мере прокрутки, шаги оживают, когда линия до них дошла
function initProcess() {
  const list = document.querySelector("[data-process-steps]");
  if (!list) return;
  const steps = [...list.querySelectorAll(".process-step")];
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const FOCUS_LINE = 0.6;
  let frame = 0;

  function update() {
    frame = 0;
    const focusY = window.innerHeight * FOCUS_LINE;
    const { top, height } = list.getBoundingClientRect();
    // У самого низа страницы блок может не доехать до линии фокуса: считаем всё пройденным
    const isPageEnd = window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 2;
    const progress = isPageEnd ? 1 : Math.min(Math.max((focusY - top) / height, 0), 1);
    list.style.setProperty("--progress", reducedMotion ? 1 : progress.toFixed(4));
    steps.forEach((step) => {
      const active = reducedMotion || isPageEnd || step.getBoundingClientRect().top + 24 < focusY;
      step.classList.toggle("is-active", active);
    });
  }

  window.addEventListener(
    "scroll",
    () => {
      if (!frame) frame = requestAnimationFrame(update);
    },
    { passive: true },
  );
  window.addEventListener("resize", update);
  update();
}

// Горизонтальная лента с перетаскиванием мышью и инерцией (касание и трекпад прокручивают сами)
const DRAG_FRICTION = 0.95;
const DRAG_STOP_SPEED = 0.3;

function initDragScroll(scroller) {
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let isDragging = false;
  let startX = 0;
  let startScroll = 0;
  let lastX = 0;
  let velocity = 0;
  let frame = 0;

  function coast() {
    scroller.scrollLeft -= velocity;
    velocity *= DRAG_FRICTION;
    frame = Math.abs(velocity) > DRAG_STOP_SPEED ? requestAnimationFrame(coast) : 0;
  }

  scroller.addEventListener("pointerdown", (event) => {
    if (event.pointerType !== "mouse") return;
    cancelAnimationFrame(frame);
    isDragging = true;
    startX = lastX = event.clientX;
    startScroll = scroller.scrollLeft;
    velocity = 0;
    scroller.setPointerCapture(event.pointerId);
  });

  scroller.addEventListener("pointermove", (event) => {
    if (!isDragging) return;
    velocity = event.clientX - lastX;
    lastX = event.clientX;
    scroller.scrollLeft = startScroll - (event.clientX - startX);
  });

  const stop = () => {
    if (!isDragging) return;
    isDragging = false;
    if (!reducedMotion) frame = requestAnimationFrame(coast);
  };
  scroller.addEventListener("pointerup", stop);
  scroller.addEventListener("pointercancel", stop);
}

// Сенсорные экраны: контур бежит по карточке, которая сейчас перед глазами. В каждом списке выбирается одна карточка:
// видна не меньше чем на 60% и ближе всех к центру экрана. Остальные остаются с серым контуром
function initGlowFocus() {
  // Тач-экраны, а также мобильная ширина окна (превью без эмуляции тача)
  const touch = window.matchMedia("(hover: none)").matches;
  const narrow = window.matchMedia("(max-width: 639px)").matches;
  if (!touch && !narrow) return;

  const MIN_VISIBLE_SHARE = 0.6;
  const SWITCH_MARGIN = 80;
  const lastActive = new WeakMap();
  // Вопросы FAQ подсвечиваются, когда открыты; остальные карточки — когда перед глазами
  const faqItems = [...document.querySelectorAll(".faq__item")];
  let frame = 0;

  function update() {
    frame = 0;
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    const best = new Map();
    const candidates = new Map();
    // Карточки ищем заново: плашки в окнах кейсов появляются в странице только при открытии окна
    const cards = [...document.querySelectorAll(".glow-card:not(.faq__item)")];

    cards.forEach((card) => {
      const rect = card.getBoundingClientRect();
      if (!rect.width || !rect.height) return;
      const visibleWidth = Math.min(rect.right, viewportWidth) - Math.max(rect.left, 0);
      const visibleHeight = Math.min(rect.bottom, viewportHeight) - Math.max(rect.top, 0);
      if (visibleWidth <= 0 || visibleHeight <= 0) return;
      // В стопке услуг карточка, которую уже накрыла следующая, не считается
      if (Number.parseFloat(card.style.getPropertyValue("--depth")) > 0.5) return;
      // Карточка выше экрана (например, направления услуг на телефоне) не может быть видна
      // на 60% целиком — для таких достаточно, чтобы она занимала бо́льшую часть экрана
      const visibleShare = (visibleWidth * visibleHeight) / (rect.width * rect.height);
      const coversScreen = rect.height > viewportHeight && visibleHeight / viewportHeight >= MIN_VISIBLE_SHARE;
      if (visibleShare < MIN_VISIBLE_SHARE && !coversScreen) return;
      const distance = Math.hypot(rect.left + rect.width / 2 - viewportWidth / 2, rect.top + rect.height / 2 - viewportHeight / 2);
      candidates.set(card, distance);
      const current = best.get(card.parentElement);
      if (!current || distance < current.distance) best.set(card.parentElement, { card, distance });
    });

    // Гистерезис: пока прежняя карточка списка ещё хорошо видна, контур с неё уходит только когда другая заметно ближе к центру
    best.forEach((entry, parent) => {
      const previous = lastActive.get(parent);
      if (previous && previous !== entry.card && candidates.has(previous) && candidates.get(previous) - entry.distance < SWITCH_MARGIN) {
        best.set(parent, { card: previous, distance: candidates.get(previous) });
      }
      lastActive.set(parent, best.get(parent).card);
    });

    const active = new Set([...best.values()].map((entry) => entry.card));
    cards.forEach((card) => card.classList.toggle("is-glow", active.has(card)));
    faqItems.forEach((item) => {
      item.classList.toggle("is-glow", item.querySelector(".faq__trigger").getAttribute("aria-expanded") === "true");
    });
  }

  const schedule = () => {
    if (!frame) frame = requestAnimationFrame(update);
  };

  // Прокрутка страницы, лент и окон (scroll не всплывает, поэтому слушаем в фазе перехвата)
  document.addEventListener("scroll", schedule, { capture: true, passive: true });
  window.addEventListener("resize", schedule);
  window.addEventListener("orientationchange", schedule);
  document.addEventListener("click", schedule);
  // Окна и вкладки появляются без прокрутки
  setInterval(schedule, 500);
  update();
}

// Лента сайтов: двигается перетаскиванием и прокруткой страницы, по кругу, без автопрокрутки
function initSites() {
  const viewport = document.querySelector("[data-sites]");
  const track = document.querySelector("[data-sites-track]");
  if (!viewport) return;
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const loopWidth = () => track.firstElementChild.offsetWidth;

  let target = 0;
  let current = 0;
  let velocity = 0;
  let isDragging = false;
  let lastPointerX = 0;
  let dragDistance = 0;
  let lastScrollY = window.scrollY;
  let frame = 0;

  function render() {
    current += (target - current) * (reducedMotion ? 1 : SITES_FOLLOW);
    if (!isDragging && Math.abs(velocity) > SITES_STOP_SPEED) {
      target += velocity;
      velocity *= SITES_FRICTION;
    } else if (!isDragging) {
      velocity = 0;
    }

    // Лента бесконечная: сдвиг приводим к одному кругу
    const width = loopWidth();
    const shift = ((current % width) - width) % width;
    track.style.transform = `translate3d(${shift}px, 0, 0)`;

    const isSettled = Math.abs(target - current) < 0.1 && velocity === 0 && !isDragging;
    frame = isSettled ? 0 : requestAnimationFrame(render);
  }

  function wake() {
    if (!frame) frame = requestAnimationFrame(render);
  }

  viewport.addEventListener("pointerdown", (event) => {
    isDragging = true;
    velocity = 0;
    lastPointerX = event.clientX;
    dragDistance = 0;
    viewport.setPointerCapture(event.pointerId);
    wake();
  });

  viewport.addEventListener("pointermove", (event) => {
    if (!isDragging) return;
    const delta = event.clientX - lastPointerX;
    lastPointerX = event.clientX;
    dragDistance += Math.abs(delta);
    target += delta;
    velocity = delta;
  });

  const stopDragging = () => {
    isDragging = false;
    if (reducedMotion) velocity = 0;
    wake();
  };
  viewport.addEventListener("pointerup", stopDragging);
  viewport.addEventListener("pointercancel", stopDragging);

  // Захват указателя переадресует клик на ленту, поэтому карточку под курсором ищем по координатам
  viewport.addEventListener("click", (event) => {
    if (event.detail === 0 || dragDistance > SITES_CLICK_SLOP) return;
    const card = document.elementsFromPoint(event.clientX, event.clientY).find((el) => el.matches("[data-site]"));
    if (card) document.querySelector(`[data-detail-open="${card.dataset.site}"]`)?.click();
  });

  // Горизонтальная прокрутка тачпадом или Shift + колесо двигает ленту; вертикальная прокручивает страницу как обычно
  viewport.addEventListener(
    "wheel",
    (event) => {
      if (Math.abs(event.deltaX) <= Math.abs(event.deltaY)) return;
      event.preventDefault();
      const lineHeight = event.deltaMode === WheelEvent.DOM_DELTA_LINE ? SITES_WHEEL_LINE_PX : 1;
      target -= event.deltaX * lineHeight;
      wake();
    },
    { passive: false },
  );

  if (!reducedMotion) {
    window.addEventListener(
      "scroll",
      () => {
        const delta = window.scrollY - lastScrollY;
        lastScrollY = window.scrollY;
        const { top, bottom } = viewport.getBoundingClientRect();
        if (bottom < 0 || top > window.innerHeight) return;
        target -= delta * SITES_SCROLL_RATIO;
        wake();
      },
      { passive: true },
    );
  }
}

function initFaq(root) {
  root?.addEventListener("click", (event) => {
    const trigger = event.target.closest(".faq__trigger");
    trigger?.setAttribute("aria-expanded", String(trigger.getAttribute("aria-expanded") !== "true"));
  });
}

const LEAD_DEMO_DELAY = 700;

function initLeadForm(form) {
  if (!form) return;
  const status = form.querySelector("[data-lead-status]");
  const submit = form.querySelector('[type="submit"]');
  const submitLabel = submit.textContent;

  const setError = (control, message) => {
    const error = document.getElementById(control.getAttribute("aria-describedby"));
    if (message) control.setAttribute("aria-invalid", "true");
    else control.removeAttribute("aria-invalid");
    error.textContent = message;
  };

  const setStatus = (message, state) => {
    status.classList.remove("is-error", "is-success");
    if (state) status.classList.add(`is-${state}`);
    status.textContent = message;
  };

  // Адрес приёма заявок задаётся в data-endpoint. Пока он пуст, заявка никуда не уходит: показываем только сообщение об успехе
  const send = async () => {
    if (form.dataset.endpoint) {
      const response = await fetch(form.dataset.endpoint, { method: "POST", body: new FormData(form) });
      if (!response.ok) throw new Error(response.statusText);
      return;
    }
    console.warn("Форма заявки: не задан data-endpoint, заявка не отправлена.");
    await new Promise((resolve) => setTimeout(resolve, LEAD_DEMO_DELAY));
  };

  form.addEventListener("input", (event) => {
    if (event.target.hasAttribute("aria-invalid")) setError(event.target, "");
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    setStatus("");

    const invalid = [...form.elements].filter((control) => control.willValidate && !control.checkValidity());
    form.querySelectorAll(".lead-form__control").forEach((control) => {
      setError(control, invalid.includes(control) ? control.dataset.error : "");
    });
    if (invalid.length) {
      invalid[0].focus();
      return;
    }

    submit.disabled = true;
    submit.textContent = "Отправляем…";
    try {
      await send();
      form.reset();
      setStatus("Заявка отправлена. Мы свяжемся с вами в ближайшее время.", "success");
    } catch {
      setStatus("Не удалось отправить заявку. Попробуйте ещё раз или напишите на info@itach-soft.ru.", "error");
    } finally {
      submit.disabled = false;
      submit.textContent = submitLabel;
    }
  });
}

// Появление блоков и заголовков при прокрутке: одиночные [data-reveal] и группы [data-reveal-stagger]
function initScrollReveal() {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        // Блоки, которые остались выше экрана (перезагрузка посреди страницы), показываем сразу
        if (!entry.isIntersecting && entry.boundingClientRect.top >= 0) return;
        entry.target.classList.add("is-revealed");
        observer.unobserve(entry.target);
      });
    },
    { rootMargin: "0px 0px -10% 0px", threshold: 0.1 },
  );

  document.querySelectorAll("[data-reveal]").forEach((el) => observer.observe(el));

  document.querySelectorAll("[data-reveal-stagger]").forEach((group) => {
    // data-reveal-pair: карточки появляются по строке сетки (парами) и каждая пара сама,
    // когда до неё доскроллили — поэтому наблюдаем потомков, а не группу целиком
    const pair = group.hasAttribute("data-reveal-pair");
    [...group.children].forEach((child, index) => {
      child.style.setProperty("--i", pair ? Math.floor(index / 2) : index);
      if (pair) observer.observe(child);
    });
    if (!pair) observer.observe(group);
  });
}

// Попап с формой заявки: открывается по кнопкам и ссылкам на #lead. Без JS те же ссылки ведут к форме внизу страницы
function initLeadModal(modal) {
  if (!modal) return;

  document.querySelectorAll('a[href="#lead"]').forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      modal.showModal();
    });
  });

  modal.querySelector("[data-modal-close]").addEventListener("click", () => modal.close());

  // Клик по затемнению (целью становится сам dialog, панель занимает всю его область) закрывает попап
  modal.addEventListener("click", (event) => {
    if (event.target === modal) modal.close();
  });

  // Телефон: попап — шторка снизу, её можно смахнуть вниз, потянув за верхнюю часть
  initSwipeToClose(modal, modal.querySelector(".modal__panel"));

  modal.addEventListener("close", () => {
    if (modal.open) return;
  });
}

// Шторку на телефоне можно закрыть, потянув вниз за верхнюю часть панели
function initSwipeToClose(modal, panel) {
  const SWIPE_CLOSE_DISTANCE = 120;
  const SWIPE_ANIMATION_MS = 200;
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let swipeStartY = 0;
  let swipeDistance = 0;
  let isSwiping = false;

  const resetSwipe = () => {
    panel.style.transition = "";
    panel.style.transform = "";
  };

  modal.addEventListener(
    "touchstart",
    (event) => {
      isSwiping = panel.scrollTop <= 0 && event.touches[0].clientY < panel.getBoundingClientRect().top + 72;
      swipeStartY = event.touches[0].clientY;
      swipeDistance = 0;
      panel.style.transition = "none";
    },
    { passive: true },
  );

  modal.addEventListener(
    "touchmove",
    (event) => {
      if (!isSwiping) return;
      swipeDistance = event.touches[0].clientY - swipeStartY;
      if (swipeDistance <= 0) {
        // Палец идёт вверх — обычная прокрутка содержимого
        isSwiping = false;
        resetSwipe();
        return;
      }
      event.preventDefault();
      panel.style.transform = `translateY(${swipeDistance}px)`;
    },
    { passive: false },
  );

  modal.addEventListener("touchend", () => {
    if (!isSwiping) return;
    isSwiping = false;
    panel.style.transition = reducedMotion ? "none" : `transform ${SWIPE_ANIMATION_MS}ms var(--ease-out)`;
    if (swipeDistance > SWIPE_CLOSE_DISTANCE) {
      panel.style.transform = "translateY(100vh)";
      setTimeout(() => {
        modal.close();
        resetSwipe();
      }, reducedMotion ? 0 : SWIPE_ANIMATION_MS);
    } else {
      resetSwipe();
    }
  });

  // Событие приходит с задержкой: если за это время открыли другое окно, панель не трогаем
  modal.addEventListener("close", () => {
    if (modal.open) return;
    resetSwipe();
  });
}

// Попап с калькулятором (разметку добавляет calculator.js): открывается кнопками
// «Рассчитать стоимость» — в мега-меню и где ещё встретится — на той же странице
function initCalcModal() {
  const modal = document.querySelector("[data-calc-modal]");
  if (!modal) return;
  const root = modal.querySelector("[data-calc]");

  modal.querySelector("[data-calc-modal-close]").addEventListener("click", () => modal.close());
  modal.addEventListener("click", (event) => {
    if (event.target === modal) modal.close();
  });
  initSwipeToClose(modal, modal.querySelector(".modal__panel"));

  document.addEventListener("click", (event) => {
    const trigger = event.target.closest('a[href="#calculator"], a[href$="index.html#calculator"], [data-calc-open]');
    // data-calc-scroll — ссылка ведёт якорем к встроенному калькулятору, попап не открываем
    if (!trigger || trigger.hasAttribute("data-calc-scroll") || modal.contains(trigger)) return;
    event.preventDefault();
    root.resetCalculator?.();
    modal.showModal();
    // Открытое мобильное меню не должно остаться поверх попапа
    const menuToggle = document.querySelector("[data-menu-toggle]");
    if (menuToggle?.getAttribute("aria-expanded") === "true") menuToggle.click();
  });
}


// Детальное окно кейса или новости: содержимое лежит в <template id="detail-…"> и копируется в диалог при открытии.
// Адрес страницы получает якорь (#case-erip), поэтому на окно можно дать ссылку
function initDetail(modal) {
  if (!modal) return;
  const content = modal.querySelector("[data-detail-content]");
  const panel = modal.querySelector("[data-detail-panel]");
  const closeButton = modal.querySelector("[data-detail-close]");
  const leadModal = document.querySelector("[data-lead-modal]");
  let currentId = "";

  function open(id) {
    const template = document.getElementById(`detail-${id}`);
    if (!template) return;
    currentId = id;
    content.replaceChildren(closeButton, template.content.cloneNode(true));
    if (!modal.open) modal.showModal();
    // Позиция прокрутки задаётся уже после показа: у скрытого диалога она не применяется
    modal.scrollTop = 0;
    content.scrollTop = 0;
    // Фокус на панели, а не на крестике: иначе при открытии крестик обведён рамкой фокуса
    panel.focus({ preventScroll: true });
    history.replaceState(null, "", `#${id}`);
  }

  document.querySelectorAll("[data-detail-open]").forEach((trigger) => {
    trigger.addEventListener("click", (event) => {
      event.preventDefault();
      open(trigger.dataset.detailOpen);
    });
  });

  // Карточка кейса и главная новость в блоге открываются кликом по любому месту, а не только по заголовку
  document.querySelectorAll(".case-card, .featured").forEach((card) => {
    card.addEventListener("click", (event) => {
      if (event.target.closest("a")) return;
      card.querySelector("[data-detail-open]").click();
    });
  });

  closeButton.addEventListener("click", () => modal.close());

  // Клик по затемнению рядом с панелью (целью становится сам dialog) закрывает окно
  modal.addEventListener("click", (event) => {
    if (event.target === modal) modal.close();
  });

  // Кнопка «Обсудить…» внутри окна: закрываем деталь и открываем форму заявки
  content.addEventListener("click", (event) => {
    if (!event.target.closest("[data-detail-lead]")) return;
    modal.close();
    leadModal?.showModal();
  });

  // Телефон: потянуть окно вниз за серую полоску сверху (или с самого верха содержимого), чтобы закрыть
  const SWIPE_CLOSE_DISTANCE = 120;
  const SWIPE_ANIMATION_MS = 200;
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let swipeStartY = 0;
  let swipeDistance = 0;
  let isSwiping = false;

  function resetSwipe() {
    panel.style.transition = "";
    panel.style.transform = "";
  }

  modal.addEventListener(
    "touchstart",
    (event) => {
      isSwiping = Boolean(event.target.closest("[data-detail-handle]")) || (content.contains(event.target) && content.scrollTop <= 0);
      swipeStartY = event.touches[0].clientY;
      swipeDistance = 0;
      panel.style.transition = "none";
    },
    { passive: true },
  );

  modal.addEventListener(
    "touchmove",
    (event) => {
      if (!isSwiping) return;
      swipeDistance = event.touches[0].clientY - swipeStartY;
      if (swipeDistance <= 0) {
        // Палец идёт вверх — это обычная прокрутка содержимого
        if (swipeDistance < 0) isSwiping = false;
        resetSwipe();
        return;
      }
      event.preventDefault();
      panel.style.transform = `translateY(${swipeDistance}px)`;
    },
    { passive: false },
  );

  modal.addEventListener("touchend", () => {
    if (!isSwiping) return;
    isSwiping = false;
    panel.style.transition = reducedMotion ? "none" : `transform ${SWIPE_ANIMATION_MS}ms var(--ease-out)`;
    if (swipeDistance > SWIPE_CLOSE_DISTANCE) {
      panel.style.transform = "translateY(100vh)";
      setTimeout(() => modal.close(), reducedMotion ? 0 : SWIPE_ANIMATION_MS);
    } else {
      resetSwipe();
    }
  });

  modal.addEventListener("close", () => {
    // Событие приходит с задержкой: если за это время уже открыли другое окно, адрес не трогаем
    if (modal.open) return;
    if (location.hash === `#${currentId}`) history.replaceState(null, "", location.pathname + location.search);
    currentId = "";
    resetSwipe();
  });

  if (location.hash.length > 1) open(location.hash.slice(1));
}

const COOKIE_CHOICE_KEY = "itach-cookie-choice";
const COOKIE_REVEAL_DELAY = 800;
const COOKIE_HIDE_DELAY = 250;

// Баннер cookie: показываем один раз, выбор храним в localStorage. Настройки cookie не выставляются:
// баннер фиксирует только решение пользователя и больше не появляется
function initCookieBanner(banner) {
  if (!banner) return;

  const readChoice = () => {
    try {
      return localStorage.getItem(COOKIE_CHOICE_KEY);
    } catch {
      return null;
    }
  };

  const saveChoice = (choice) => {
    try {
      localStorage.setItem(COOKIE_CHOICE_KEY, choice);
    } catch {
      // Приватный режим или file://: решение запомнится только до конца визита
    }
  };

  if (readChoice()) return;

  const reveal = () => {
    banner.hidden = false;
    requestAnimationFrame(() => banner.classList.add("is-visible"));
  };

  const timer = setTimeout(reveal, COOKIE_REVEAL_DELAY);

  banner.querySelectorAll("[data-cookie-choice]").forEach((button) => {
    button.addEventListener("click", () => {
      clearTimeout(timer);
      saveChoice(button.dataset.cookieChoice);
      banner.classList.remove("is-visible");
      setTimeout(() => {
        banner.hidden = true;
      }, COOKIE_HIDE_DELAY);
    });
  });
}

// Мега-меню услуг: открывается по наведению на «Услуги», правая колонка с услугами следует за категорией.
// На сенсорных устройствах не показывается (меню-шторка остаётся основным способом навигации)
function initServicesMegaMenu() {
  const header = document.querySelector("[data-header]");
  const menu = document.querySelector("[data-services-menu]");
  const trigger = document.querySelector("[data-services-menu-trigger]");
  const categories = menu?.querySelectorAll("[data-mega-category]") ?? [];
  const lists = menu?.querySelectorAll("[data-mega-items]") ?? [];
  if (!menu || !trigger || !categories.length) return;

  const touch = window.matchMedia("(hover: none)").matches;
  if (touch) return;

  let openTimer;
  let closeTimer;

  const activate = (key) => {
    categories.forEach((category) => {
      category.classList.toggle("is-active", category.dataset.megaCategory === key);
    });
    lists.forEach((list) => {
      list.hidden = list.dataset.megaItems !== key;
    });
  };

  const openMenu = () => {
    clearTimeout(closeTimer);
    clearTimeout(openTimer);
    openTimer = setTimeout(() => {
      menu.hidden = false;
      trigger.setAttribute("aria-expanded", "true");
    }, 60);
  };

  const closeMenu = () => {
    clearTimeout(openTimer);
    clearTimeout(closeTimer);
    closeTimer = setTimeout(() => {
      menu.hidden = true;
      trigger.setAttribute("aria-expanded", "false");
    }, 160);
  };

  header.addEventListener("mouseenter", (event) => {
    if (event.target.closest(".nav__link--services")) openMenu();
    // Ушли с «Услуг» на другой пункт шапки, не заходя в само мега-меню — закрываем.
    // Задержка closeMenu даёт время перевести курсор из пункта вниз, в панель меню
    else if (!event.target.closest("[data-services-menu]")) closeMenu();
  }, true);

  menu.addEventListener("mouseenter", openMenu);
  menu.addEventListener("mouseleave", closeMenu);

  menu.addEventListener("focusin", () => {
    clearTimeout(closeTimer);
    menu.hidden = false;
    trigger.setAttribute("aria-expanded", "true");
  });

  menu.addEventListener("focusout", (event) => {
    if (menu.contains(event.relatedTarget)) return;
    closeMenu();
  });

  // Услуги укладываются максимум в два столбца: заполняется первый сверху вниз,
  // переполнение уходит во второй. Строк — половина от самого длинного списка.
  const sizeToLargest = () => {
    const maxCount = Math.max(...[...lists].map((list) => list.children.length));
    menu.style.setProperty("--mega-rows", String(Math.ceil(maxCount / 2)));
  };

  sizeToLargest();

  categories.forEach((category) => {
    category.addEventListener("mouseenter", () => activate(category.dataset.megaCategory));
    category.addEventListener("focus", () => activate(category.dataset.megaCategory));
  });

  // Мега-меню открывается по наведению; клик по «Услуги» — обычный переход на страницу услуг

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !menu.hidden) {
      closeMenu();
      trigger.focus();
    }
  });

  activate(categories[0].dataset.megaCategory);
}

// «Компания»: компактный выпадающий список под пунктом, открывается по наведению.
// На сенсорных и мобильных его заменяет аккордеон бургер-меню (см. initHeader)
function initCompanyDropdown() {
  const item = document.querySelector("[data-company-item]");
  const menu = item?.querySelector("[data-company-menu]");
  const trigger = item?.querySelector("[data-company-menu-trigger]");
  if (!item || !menu || !trigger) return;
  if (window.matchMedia("(hover: none), (max-width: 1023px)").matches) return;

  let openTimer;
  let closeTimer;
  // Возврат фокуса на пункт после Escape не должен снова открывать список
  let ignoreFocusOpen = false;

  const setOpen = (open) => {
    menu.hidden = !open;
    trigger.setAttribute("aria-expanded", String(open));
  };

  const openMenu = () => {
    clearTimeout(closeTimer);
    clearTimeout(openTimer);
    openTimer = setTimeout(() => setOpen(true), 60);
  };

  const closeMenu = () => {
    clearTimeout(openTimer);
    clearTimeout(closeTimer);
    closeTimer = setTimeout(() => setOpen(false), 160);
  };

  item.addEventListener("mouseenter", openMenu);
  item.addEventListener("mouseleave", closeMenu);

  // Переход по ссылке (в том числе на якорь) убирает список с экрана
  menu.addEventListener("click", (event) => {
    if (event.target.closest(".nav-dropdown__link")) setOpen(false);
  });

  item.addEventListener("focusin", () => {
    if (ignoreFocusOpen) {
      ignoreFocusOpen = false;
      return;
    }
    clearTimeout(closeTimer);
    setOpen(true);
  });

  item.addEventListener("focusout", (event) => {
    if (item.contains(event.relatedTarget)) return;
    closeMenu();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape" || menu.hidden) return;
    clearTimeout(openTimer);
    clearTimeout(closeTimer);
    ignoreFocusOpen = true;
    setOpen(false);
    trigger.focus();
  });
}

// Услуги в мобильном меню: аккордеон «направления → услуги» собирается из данных мега-меню,
// чтобы список услуг правился в одном месте
function initMobileServicesNav() {
  const menu = document.querySelector("[data-services-menu]");
  const container = document.querySelector("[data-nav-services]");
  const toggle = document.querySelector("[data-nav-services-toggle]");
  if (!menu || !container || !toggle) return;

  const setExpanded = (button, expanded) => button.setAttribute("aria-expanded", String(expanded));

  const build = () => {
    const list = document.createElement("ul");
    list.className = "nav-sub";

    menu.querySelectorAll("[data-mega-category]").forEach((category) => {
      const key = category.dataset.megaCategory;
      const title = category.querySelector(".mega-menu__category-title").textContent;
      const sourceList = menu.querySelector(`[data-mega-items="${key}"]`);

      const item = document.createElement("li");
      item.className = "nav-sub__item";

      const row = document.createElement("div");
      row.className = "nav-sub__row";

      const link = document.createElement("a");
      link.className = "nav-sub__link";
      link.href = category.getAttribute("href");
      link.textContent = title;

      const subToggle = document.createElement("button");
      subToggle.type = "button";
      subToggle.className = "nav-sub__toggle";
      subToggle.setAttribute("aria-expanded", "false");
      subToggle.setAttribute("aria-label", `Показать услуги: ${title}`);
      subToggle.innerHTML = '<svg class="icon" aria-hidden="true"><use href="#icon-chevron-down" /></svg>';

      const panel = document.createElement("div");
      panel.className = "nav-sub__panel";
      panel.hidden = true;

      const services = document.createElement("ul");
      services.className = "nav-sub__services";
      sourceList.querySelectorAll("a").forEach((source) => {
        const serviceItem = document.createElement("li");
        const service = source.cloneNode(true);
        service.className = "nav-sub__service";
        serviceItem.appendChild(service);
        services.appendChild(serviceItem);
      });
      panel.appendChild(services);

      // Открыто только одно направление за раз
      subToggle.addEventListener("click", () => {
        const willOpen = panel.hidden;
        list.querySelectorAll(".nav-sub__panel").forEach((other) => {
          other.hidden = true;
        });
        list.querySelectorAll(".nav-sub__toggle").forEach((other) => {
          setExpanded(other, false);
        });
        panel.hidden = !willOpen;
        setExpanded(subToggle, willOpen);
      });

      row.append(link, subToggle);
      item.append(row, panel);
      list.appendChild(item);
    });

    container.appendChild(list);
  };

  build();

  toggle.addEventListener("click", () => {
    const willOpen = container.hidden;
    container.hidden = !willOpen;
    setExpanded(toggle, willOpen);
  });
}

// Лента технологий: скорость постоянная независимо от числа логотипов.
// Ширина трека у страниц разная, а анимация в CSS идёт фиксированные 90 s —
// поэтому длительность считаем от ширины списка (тот же темп, что на «Сайтах»)
function initTechMarquee() {
  const PX_PER_SECOND = 30;
  document.querySelectorAll(".tech-marquee__track").forEach((track) => {
    const list = track.querySelector(".tech-marquee__list");
    if (!list) return;
    track.style.animationDuration = `${Math.round(list.offsetWidth / PX_PER_SECOND)}s`;
  });
}

// Сертификаты и награды: центральная карточка и две боковые под ней.
// Клик по боковой переносит её сертификат в центр, очередь круговая
function initAwards() {
  const section = document.querySelector("[data-awards]");
  if (!section) return;
  const dataEl = section.querySelector("[data-awards-data]");
  const stage = section.querySelector("[data-awards-stage]");
  if (!dataEl || !stage) return;

  const data = JSON.parse(dataEl.textContent);
  const total = data.length;
  // Роли мигрируют между карточками, поэтому элементы берём по актуальному классу
  const leftEl = () => stage.querySelector(".is-left");
  const centerEl = () => stage.querySelector(".is-center");
  const rightEl = () => stage.querySelector(".is-right");
  const caption = section.querySelector("[data-awards-caption]");
  const dotsBox = section.querySelector("[data-awards-dots]");
  // Круговая очередь: слева — предыдущий, справа — следующий; клик по боковой крутит её
  let positions = { left: total - 1, center: 0, right: 1 };
  let busy = false;

  const setImage = (el, index) => {
    el.querySelector("img").src = data[index].src;
    el.querySelector("img").alt = data[index].alt;
  };

  const dots = data.map((cert, dotIndex) => {
    const dot = document.createElement("button");
    dot.type = "button";
    dot.setAttribute("aria-label", cert.caption);
    dot.addEventListener("click", () => goTo(dotIndex));
    dotsBox.append(dot);
    return dot;
  });

  const updateDots = () => {
    dots.forEach((dot, dotIndex) => {
      if (dotIndex === positions.center) dot.setAttribute("aria-current", "true");
      else dot.removeAttribute("aria-current");
    });
  };

  const render = () => {
    setImage(leftEl(), positions.left);
    setImage(centerEl(), positions.center);
    setImage(rightEl(), positions.right);
    caption.textContent = data[positions.center].caption;
    updateDots();
  };

  // Переход к конкретному сертификату по индикатору: картинки гаснут и проявляются уже новыми
  const FADE_MS = 150; // совпадает с --duration-fast у .awards-show.is-switching img
  const goTo = (index) => {
    if (busy || index === positions.center) return;
    busy = true;
    const cards = [leftEl(), centerEl(), rightEl()];
    cards.forEach((card) => card.classList.add("is-switching"));
    setTimeout(() => {
      positions = { left: (index - 1 + total) % total, center: index, right: (index + 1) % total };
      render();
      cards.forEach((card) => card.classList.remove("is-switching"));
      setTimeout(() => {
        busy = false;
      }, 220);
    }, FADE_MS);
  };

  // direction: 1 — клик по правой карточке, -1 — по левой
  const rotate = (direction) => {
    if (busy) return;
    busy = true;
    const left = leftEl();
    const center = centerEl();
    const right = rightEl();
    const jumping = direction === 1 ? left : right;
    const current = { ...positions };

    // Скрываем перелетающую карточку до смены ролей: перенос мгновенный и незаметный
    jumping.classList.add("is-jumping");
    void jumping.offsetWidth; // фиксируем скрытое состояние, чтобы transform не анимировался

    if (direction === 1) {
      right.classList.replace("is-right", "is-center");
      center.classList.replace("is-center", "is-left");
      left.classList.replace("is-left", "is-right");
      positions = { left: current.center, center: current.right, right: (current.right + 1) % total };
    } else {
      left.classList.replace("is-left", "is-center");
      center.classList.replace("is-center", "is-right");
      right.classList.replace("is-right", "is-left");
      positions = { left: (current.left - 1 + total) % total, center: current.left, right: current.center };
    }
    setImage(jumping, direction === 1 ? positions.right : positions.left);
    caption.textContent = data[positions.center].caption;
    updateDots();

    // Проявляем карточку уже на новом месте
    requestAnimationFrame(() => {
      requestAnimationFrame(() => jumping.classList.remove("is-jumping"));
    });
    setTimeout(() => {
      busy = false;
    }, 450);
  };

  // Роли карточек (классы) мигрируют между элементами — направление берём из класса на момент клика
  stage.addEventListener("click", (event) => {
    const card = event.target.closest(".awards-show");
    if (!card) return;
    if (card.classList.contains("is-left")) rotate(-1);
    else if (card.classList.contains("is-right")) rotate(1);
  });

  // На телефоне виден один сертификат: листаем свайпом, смена — тем же кроссфейдом, что по индикаторам
  const narrow = window.matchMedia("(max-width: 639px)");
  const SWIPE_THRESHOLD = 40;
  let touchStartX = 0;
  let touchStartY = 0;

  stage.addEventListener(
    "touchstart",
    (event) => {
      if (!narrow.matches) return;
      touchStartX = event.touches[0].clientX;
      touchStartY = event.touches[0].clientY;
    },
    { passive: true },
  );

  stage.addEventListener(
    "touchend",
    (event) => {
      if (!narrow.matches) return;
      const dx = event.changedTouches[0].clientX - touchStartX;
      const dy = event.changedTouches[0].clientY - touchStartY;
      // Вертикальный жест — это прокрутка страницы, а не листание
      if (Math.abs(dx) < SWIPE_THRESHOLD || Math.abs(dx) <= Math.abs(dy)) return;
      // Свайп влево — следующий, вправо — предыдущий
      goTo((positions.center + (dx < 0 ? 1 : -1) + total) % total);
    },
    { passive: true },
  );

  render();
}

// Карточки инструментов («Ключевые инструменты внедрения»): когда карточка доходит
// до экрана, по её контуру один раз пробегает градиентная волна (класс is-swept)
function initToolsSweep() {
  const items = document.querySelectorAll(".tools-item");
  if (!items.length || !("IntersectionObserver" in window)) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting || entry.target.classList.contains("is-swept")) return;
        entry.target.classList.add("is-swept");
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.5 },
  );

  items.forEach((item) => observer.observe(item));
}

initHeader();
initServicesMegaMenu();
initCompanyDropdown();
initMobileServicesNav();
initScrollReveal();
initGlowCards();
initGlowFocus();
initToolsSweep();
initAudiencePicker();
initSites();
initServiceStack();
document.querySelectorAll("[data-drag-scroll]").forEach(initDragScroll);
initServiceTabs(document.querySelector("[data-service-stack]"));
initProcess();
initProblemRows();
// Четыре инициализации живут в подключаемых на отдельных страницах скриптах
// Заявления на страницах подуслуг ([data-text-fill]): слова серые и при скролле
// по очереди закрашиваются в тёмный — прогресс считается от позиции блока в вьюпорте
function initTextFill() {
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  document.querySelectorAll("[data-text-fill]").forEach((el) => {
    const words = el.textContent.trim().split(/\s+/);
    el.textContent = "";
    const spans = words.map((word) => {
      const span = document.createElement("span");
      span.className = "text-fill__word";
      span.textContent = word;
      el.append(span, " ");
      return span;
    });
    if (reduced) {
      spans.forEach((span) => span.style.setProperty("--p", 1));
      return;
    }

    let frame = 0;
    const update = () => {
      frame = 0;
      const rect = el.getBoundingClientRect();
      const viewport = innerHeight;
      // 0 — блок только вошёл снизу, 1 — почти ушёл за верхнюю кромку экрана.
      // На телефоне окно шире (2 высоты экрана): заявление читается дольше,
      // и весь текст за один экран прокрутки не успевает закраситься
      const travel = viewport * (innerWidth < 640 ? 2 : 1.1);
      const progress = Math.min(1, Math.max(0, (viewport * 0.9 - rect.top) / travel));
      spans.forEach((span, index) => {
        // +4 слова перекрытия: соседние слова темнеют почти одновременно, без «лесенки»
        const local = Math.min(1, Math.max(0, progress * (spans.length + 4) - index));
        span.style.setProperty("--p", local.toFixed(2));
      });
    };
    const onScroll = () => {
      if (!frame) frame = requestAnimationFrame(update);
    };
    addEventListener("scroll", onScroll, { passive: true });
    addEventListener("resize", onScroll);
    update();
  });
}

// (cursor-halo.js, hero-gl.js, lead-wave.js, calculator.js) — не всякая страница
// их подключает, поэтому вызов через window с опциональной цепочкой: иначе
// ReferenceError рвал всю оставшуюся инициализацию страницы
window.initCursorHalo?.(document.querySelector("[data-cursor-halo]"));
window.initHeroGl?.(document.querySelector("[data-hero-gl]"));
initFaq(document.querySelector("[data-faq]"));
document.querySelectorAll("[data-lead-form]").forEach(initLeadForm);
initLeadModal(document.querySelector("[data-lead-modal]"));
window.initLeadWave?.(document.querySelector("[data-lead-wave]"));
document.querySelectorAll("[data-calc]").forEach((el) => window.initCalculator?.(el));
initCalcModal();
initDetail(document.querySelector("[data-detail-modal]"));
initCookieBanner(document.querySelector("[data-cookie]"));
initTechMarquee();
// После загрузки шрифтов ширина списка может измениться — пересчитываем длительность
document.fonts?.ready.then(initTechMarquee);
initAwards();
initTextFill();
