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

  const servicesToggle = header.querySelector("[data-services-submenu-toggle]");
  const servicesSubmenu = header.querySelector("[data-services-submenu]");
  if (servicesToggle && servicesSubmenu) {
    servicesToggle.addEventListener("click", (event) => {
      event.stopPropagation();
      const open = servicesToggle.getAttribute("aria-expanded") !== "true";
      servicesToggle.setAttribute("aria-expanded", String(open));
      servicesSubmenu.hidden = !open;
    });

    // Клик по категории закрывает всё меню, как остальные пункты
    servicesSubmenu.addEventListener("click", () => setMenuOpen(false));
  }

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
  if (!window.matchMedia("(hover: none)").matches) return;

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
  const targets = document.querySelectorAll("[data-reveal], [data-reveal-stagger]");

  document.querySelectorAll("[data-reveal-stagger]").forEach((group) => {
    [...group.children].forEach((child, index) => child.style.setProperty("--i", index));
  });

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
  targets.forEach((target) => observer.observe(target));
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
    if (!trigger || modal.contains(trigger)) return;
    event.preventDefault();
    root.resetCalculator?.();
    modal.showModal();
    // Открытое мобильное меню не должно остаться поверх попапа
    const menuToggle = document.querySelector("[data-menu-toggle]");
    if (menuToggle?.getAttribute("aria-expanded") === "true") menuToggle.click();
  });
}

// Блок «Стоимость»: секция растянута на экран плюс дистанцию прокручивания и прилипает
// (sticky). Пока она на экране, вертикальный скролл сдвигает строку карточек по
// горизонтали — дальше страница не прокрутится, пока строка не проедет целиком.
// При prefers-reduced-motion — обычная горизонтальная прокрутка без прилипания
function initFormatsScroll() {
  const section = document.querySelector("[data-formats]");
  if (!section) return;
  const pin = section.querySelector(".formats__pin");
  const track = section.querySelector("[data-format-track]");
  if (!pin || !track) return;
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)");

  const setNative = () => {
    section.classList.add("formats--native");
    section.style.blockSize = "";
    track.style.transform = "";
  };

  if (reduced.matches) {
    setNative();
    return;
  }

  const overflow = () => Math.max(0, track.scrollWidth - document.documentElement.clientWidth);

  // Горизонтальный прогресс считается по «липкому» диапазону: пока пин прилиплен
  // (sectionH − pinH пикселей скролла), строка проезжает целиком
  const update = () => {
    const stickyRange = section.offsetHeight - pin.offsetHeight;
    if (stickyRange <= 0) return;
    const progress = Math.min(1, Math.max(0, -section.getBoundingClientRect().top / stickyRange));
    track.style.transform = `translate3d(${-progress * overflow()}px, 0, 0)`;
  };

  // Секция = высота пина + дистанция прокручивания: пустого хвоста под пином
  // не остаётся, поэтому до следующего блока ровно padding пина (96px)
  const layout = () => {
    const distance = Math.max(overflow() * 1.2, window.innerHeight * 0.5);
    section.style.blockSize = `${pin.offsetHeight + distance}px`;
    update();
  };

  window.addEventListener("scroll", update, { passive: true });
  window.addEventListener("resize", layout);
  reduced.addEventListener?.("change", (event) => {
    if (event.matches) setNative();
    else layout();
  });
  layout();
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

// Липкая мобильная CTA «Рассчитать стоимость»: появляется после прокрутки hero,
// прячется, когда форма заявки на экране, чтобы не перекрывать её
function initLeadCta() {
  const cta = document.querySelector("[data-lead-cta]");
  if (!cta) return;
  const lead = document.querySelector(cta.dataset.leadCtaTarget || "#lead");
  let leadVisible = false;

  const update = () => {
    cta.classList.toggle("is-visible", window.scrollY > 480 && !leadVisible);
  };

  if (lead) {
    new IntersectionObserver(
      ([entry]) => {
        leadVisible = entry.isIntersecting;
        update();
      },
      { rootMargin: "0px 0px -25% 0px" }
    ).observe(lead);
  }

  window.addEventListener("scroll", update, { passive: true });
  update();
}

// Папка с технологиями: контур створок — это путь по фактическим размерам карточки,
// поэтому язычки и скругления не деформируются; здесь же веер иконок раскладывается
// по доступной ширине и папка появляется при прокрутке
function initTechFolder() {
  const folders = document.querySelectorAll("[data-tech-folder]");
  if (!folders.length) return;

  const folderPath = (w, h, tabSide) => {
    const r = 24;
    const d = 24;
    const tw = Math.round(w * (tabSide === "left" ? 0.42 : 0.4));
    const s = 46;
    if (tabSide === "left") {
      return `M0 ${r}A${r} ${r} 0 0 1 ${r} 0L${tw} 0C${tw + s * 0.55} 0 ${tw + s * 0.45} ${d} ${tw + s} ${d}L${w - r} ${d}A${r} ${r} 0 0 1 ${w} ${d + r}L${w} ${h - r}A${r} ${r} 0 0 1 ${w - r} ${h}L${r} ${h}A${r} ${r} 0 0 1 0 ${h - r}Z`;
    }
    const x = w - tw;
    return `M0 ${d + r}A${r} ${r} 0 0 1 ${r} ${d}L${x - s} ${d}C${x - s * 0.45} ${d} ${x - s * 0.55} 0 ${x} 0L${w - r} 0A${r} ${r} 0 0 1 ${w} ${r}L${w} ${h - r}A${r} ${r} 0 0 1 ${w - r} ${h}L${r} ${h}A${r} ${r} 0 0 1 0 ${h - r}Z`;
  };

  folders.forEach((folder) => {
    const front = folder.querySelector("[data-tech-folder-front]");
    const back = folder.querySelector("[data-tech-folder-back]");
    const icons = folder.querySelectorAll(".tech-folder__icon");
    if (!front || !back) return;

    const layout = () => {
      const w = folder.clientWidth;
      const tile = w < 380 ? 40 : w < 460 ? 52 : w < 620 ? 64 : 72;
      const spread = Math.min(
        64,
        Math.max(20, (w - tile - 36) / Math.max(icons.length - 1, 1))
      );
      folder.style.setProperty("--tech-tile", `${tile}px`);
      folder.style.setProperty("--tech-spread", `${spread.toFixed(1)}px`);

      [
        [front, "left"],
        [back, "right"],
      ].forEach(([el, side]) => {
        const d = folderPath(el.clientWidth, el.clientHeight, side);
        el.style.clipPath = `path('${d}')`;
        el.querySelector("[data-tech-folder-path]")?.setAttribute("d", d);
      });
    };

    layout();
    new ResizeObserver(layout).observe(folder);

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (!entry.isIntersecting) return;
        folder.classList.add("is-shown");
        observer.disconnect();
      },
      { threshold: 0.25 }
    );
    observer.observe(folder);
  });
}

initHeader();
initServicesMegaMenu();
initMobileServicesNav();
initScrollReveal();
initGlowCards();
initGlowFocus();
initSites();
initServiceStack();
document.querySelectorAll("[data-drag-scroll]").forEach(initDragScroll);
initServiceTabs(document.querySelector("[data-service-stack]"));
initProcess();
// Четыре инициализации живут в подключаемых на отдельных страницах скриптах
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
initFormatsScroll();
initDetail(document.querySelector("[data-detail-modal]"));
initCookieBanner(document.querySelector("[data-cookie]"));
initLeadCta();
initTechFolder();
