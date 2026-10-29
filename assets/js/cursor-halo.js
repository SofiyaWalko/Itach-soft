// Стеклянный круг вместо системного курсора: следует за мышью почти без задержки
// Только для точного указателя и без reduced motion.

const FOLLOW_SPEED = 0.38;
const SETTLE_DISTANCE = 0.1;
const TEXT_FIELD_SELECTOR = "input, textarea, select";

function initCursorHalo(halo) {
  const canTrack = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!canTrack || reducedMotion) return;

  document.documentElement.classList.add("has-custom-cursor");

  // Открытые окна лежат в верхнем слое поверх всего; кружок тоже там и поднимается над каждым новым окном
  halo.popover = "manual";
  function raiseHalo() {
    if (halo.matches(":popover-open")) halo.hidePopover();
    halo.showPopover();
  }
  raiseHalo();
  const dialogWatcher = new MutationObserver((records) => {
    if (records.some((record) => record.target.open)) raiseHalo();
  });
  document.querySelectorAll("dialog").forEach((dialog) => {
    dialogWatcher.observe(dialog, { attributes: true, attributeFilter: ["open"] });
  });

  let targetX = 0;
  let targetY = 0;
  let currentX = 0;
  let currentY = 0;
  let frame = 0;
  let isPlaced = false;

  function render() {
    currentX += (targetX - currentX) * FOLLOW_SPEED;
    currentY += (targetY - currentY) * FOLLOW_SPEED;
    halo.style.transform = `translate3d(${currentX}px, ${currentY}px, 0) translate(-50%, -50%)`;

    const isSettled =
      Math.abs(targetX - currentX) < SETTLE_DISTANCE && Math.abs(targetY - currentY) < SETTLE_DISTANCE;
    frame = isSettled ? 0 : requestAnimationFrame(render);
  }

  // Над полями ввода кружок прячется: там нужен системный курсор-текст
  function updateState(element) {
    halo.classList.toggle("is-hidden", Boolean(element?.closest(TEXT_FIELD_SELECTOR)));
  }

  // Страница может уехать из-под неподвижного курсора, и pointermove не придёт: состояние
  // пересчитываем по тому, что сейчас лежит под курсором
  function syncState() {
    if (!isPlaced) return;
    updateState(document.elementFromPoint(targetX, targetY));
  }

  let syncFrame = 0;
  window.addEventListener(
    "scroll",
    () => {
      if (syncFrame) return;
      syncFrame = requestAnimationFrame(() => {
        syncFrame = 0;
        syncState();
      });
    },
    { passive: true },
  );

  window.addEventListener(
    "pointermove",
    (event) => {
      targetX = event.clientX;
      targetY = event.clientY;
      if (!isPlaced) {
        // Первое появление: без пролёта через весь экран из угла
        currentX = targetX;
        currentY = targetY;
        isPlaced = true;
        halo.classList.add("is-visible");
      }
      updateState(event.target);
      if (!frame) frame = requestAnimationFrame(render);
    },
    { passive: true },
  );

  document.documentElement.addEventListener("pointerleave", () => {
    halo.classList.remove("is-visible");
    isPlaced = false;
  });
}

window.initCursorHalo = initCursorHalo;
