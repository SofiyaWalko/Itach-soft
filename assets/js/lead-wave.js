// Абстрактная волна из тонких линий за формой заявки (как в блоке «Scale with confidence» у Stripe):
// пучок линий поднимается слева направо, то сходясь в узел, то расходясь веером, и медленно течёт.
// Цвета берутся из токенов сайта. При reduced motion рисуется один статичный кадр.

const LEAD_WAVE_LINES = 44;
const LEAD_WAVE_STEP = 8;
const LEAD_WAVE_SPEED = 0.00035;
const LEAD_WAVE_MAX_DPR = 2;
const LEAD_WAVE_LINE_ALPHA = 0.8;

// Цвет токена в виде «r, g, b»: градиент с прозрачностью должен таять в тот же цвет, а не в серый
function leadWaveChannels(value) {
  const probe = document.createElement("canvas").getContext("2d");
  probe.fillStyle = value;
  probe.fillRect(0, 0, 1, 1);
  return probe.getImageData(0, 0, 1, 1).data.slice(0, 3).join(", ");
}

function initLeadWave(canvas) {
  const context = canvas?.getContext("2d");
  if (!context) return;

  const styles = getComputedStyle(document.documentElement);
  const orange = leadWaveChannels(styles.getPropertyValue("--color-drop-orange").trim());
  const pink = leadWaveChannels(styles.getPropertyValue("--color-drop-pink").trim());
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  let width = 0;
  let height = 0;
  let stroke = "";
  let frame = 0;

  function resize() {
    const ratio = Math.min(window.devicePixelRatio || 1, LEAD_WAVE_MAX_DPR);
    width = canvas.clientWidth;
    height = canvas.clientHeight;
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    context.setTransform(ratio, 0, 0, ratio, 0, 0);

    // Под текстом слева линии еле заметны, к форме набирают яркость, у правого края растворяются
    stroke = context.createLinearGradient(0, 0, width, 0);
    stroke.addColorStop(0, `rgba(${orange}, 0)`);
    stroke.addColorStop(0.2, `rgba(${orange}, 0.22)`);
    stroke.addColorStop(0.5, `rgba(${pink}, 0.7)`);
    stroke.addColorStop(0.75, `rgba(${orange}, 1)`);
    stroke.addColorStop(0.92, `rgba(${pink}, 1)`);
    stroke.addColorStop(1, `rgba(${pink}, 0)`);
  }

  function draw(time) {
    context.clearRect(0, 0, width, height);
    context.strokeStyle = stroke;
    context.lineWidth = 1;
    context.globalAlpha = LEAD_WAVE_LINE_ALPHA;

    for (let line = 0; line < LEAD_WAVE_LINES; line += 1) {
      const offset = line / (LEAD_WAVE_LINES - 1) - 0.5;
      context.beginPath();
      for (let x = 0; x <= width + LEAD_WAVE_STEP; x += LEAD_WAVE_STEP) {
        const t = x / width;
        // Гребень поднимается слева направо; размах пучка меняет знак: линии сходятся в узел и расходятся
        const rise = t * t * (3 - 2 * t);
        const ridge = height * (0.9 - 0.4 * rise + 0.04 * Math.sin(t * 5 + time * 0.6));
        const spread = Math.sin(t * 3 + 0.9 + time * 0.8) * (0.12 + 0.88 * rise) * height * 0.95;
        const ripple = Math.sin(t * 7 + offset * 4 + time * 1.4) * height * 0.012 * t;
        const y = ridge + offset * spread + ripple;
        if (x === 0) context.moveTo(x, y);
        else context.lineTo(x, y);
      }
      context.stroke();
    }
  }

  function tick(now) {
    draw(now * LEAD_WAVE_SPEED);
    frame = requestAnimationFrame(tick);
  }

  resize();
  new ResizeObserver(() => {
    resize();
    if (!frame) draw(0);
  }).observe(canvas);

  if (reducedMotion) {
    draw(0);
    return;
  }

  // Рисуем только пока блок на экране
  new IntersectionObserver(([entry]) => {
    if (entry.isIntersecting && !frame) frame = requestAnimationFrame(tick);
    else if (!entry.isIntersecting && frame) {
      cancelAnimationFrame(frame);
      frame = 0;
    }
  }).observe(canvas);
}

window.initLeadWave = initLeadWave;
