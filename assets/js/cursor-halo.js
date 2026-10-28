// Стеклянный круг вместо системного курсора: следует за мышью почти без задержки
// Только для точного указателя и без reduced motion.

const FOLLOW_SPEED = 0.38;
const SETTLE_DISTANCE = 0.1;

function initCursorHalo(halo) {
  const canTrack = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!canTrack || reducedMotion) return;

  document.documentElement.classList.add("has-custom-cursor");

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

  // Страница может уехать из-под неподвижного курсора, и pointermove не придёт: состояние над лентой
  // пересчитываем по тому, что сейчас лежит под курсором
  function syncDragState() {
    if (!isPlaced) return;
    const element = document.elementFromPoint(targetX, targetY);
    halo.classList.toggle("is-drag", Boolean(element?.closest("[data-drag-cursor]")));
  }

  let syncFrame = 0;
  window.addEventListener(
    "scroll",
    () => {
      if (syncFrame) return;
      syncFrame = requestAnimationFrame(() => {
        syncFrame = 0;
        syncDragState();
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
      halo.classList.toggle("is-drag", Boolean(event.target.closest("[data-drag-cursor]")));
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
