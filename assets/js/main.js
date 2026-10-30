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
  menuToggle.setAttribute("aria-expanded", String(isOpen));
  menuToggle.setAttribute("aria-label", isOpen ? "Закрыть меню" : "Открыть меню");
}

function initHeader() {
  updateHeaderState();
  window.addEventListener("scroll", updateHeaderState, { passive: true });

  menuToggle.addEventListener("click", () => {
    setMenuOpen(menuToggle.getAttribute("aria-expanded") !== "true");
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

// Стопка карточек услуг: чем больше карточек легло сверху, тем сильнее нижняя уменьшается и темнеет
function initServiceStack() {
  const stack = document.querySelector("[data-service-stack]");
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

// Лента сайтов: двигается перетаскиванием и прокруткой страницы, по кругу, без автопрокрутки
function initSites() {
  const viewport = document.querySelector("[data-sites]");
  const track = document.querySelector("[data-sites-track]");
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

  // Карточка кейса открывается кликом по любому месту, а не только по заголовку
  document.querySelectorAll(".case-card").forEach((card) => {
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

initHeader();
initScrollReveal();
initGlowCards();
initSites();
initServiceStack();
document.querySelectorAll("[data-drag-scroll]").forEach(initDragScroll);
initServiceTabs(document.querySelector("[data-service-stack]"));
initProcess();
initCursorHalo(document.querySelector("[data-cursor-halo]"));
initHeroGl(document.querySelector("[data-hero-gl]"));
initFaq(document.querySelector("[data-faq]"));
document.querySelectorAll("[data-lead-form]").forEach(initLeadForm);
initLeadModal(document.querySelector("[data-lead-modal]"));
initLeadWave(document.querySelector("[data-lead-wave]"));
initCalculator(document.querySelector("[data-calc]"));
initDetail(document.querySelector("[data-detail-modal]"));
initCookieBanner(document.querySelector("[data-cookie]"));
