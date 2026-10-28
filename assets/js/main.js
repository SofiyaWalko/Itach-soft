const header = document.querySelector("[data-header]");
const menuToggle = document.querySelector("[data-menu-toggle]");

const SCROLLED_OFFSET = 8;
const SITES_SCROLL_RATIO = 0.6;
const SITES_FOLLOW = 0.14;
const SITES_FRICTION = 0.94;
const SITES_STOP_SPEED = 0.1;
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
  for (const card of document.querySelectorAll(".glow-card")) {
    card.addEventListener("pointermove", (event) => {
      const rect = card.getBoundingClientRect();
      const scale = card.offsetWidth / rect.width;
      card.style.setProperty("--mx", `${(event.clientX - rect.left) * scale}px`);
      card.style.setProperty("--my", `${(event.clientY - rect.top) * scale}px`);
    });
  }
}

function initTaskSweep() {
  const list = document.querySelector("[data-task-list]");
  const observer = new IntersectionObserver(
    ([entry]) => {
      if (!entry.isIntersecting) return;
      list.classList.add("is-revealed");
      observer.disconnect();
    },
    { threshold: 0.4 },
  );
  observer.observe(list);
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
    viewport.setPointerCapture(event.pointerId);
    wake();
  });

  viewport.addEventListener("pointermove", (event) => {
    if (!isDragging) return;
    const delta = event.clientX - lastPointerX;
    lastPointerX = event.clientX;
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

initHeader();
initGlowCards();
initTaskSweep();
initSites();
initServiceStack();
initCursorHalo(document.querySelector("[data-cursor-halo]"));
initHeroGl(document.querySelector("[data-hero-gl]"));
