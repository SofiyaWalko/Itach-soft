// WebGL-фон hero: объёмная переливающаяся ткань. Шейдер трассирует лучи по карте высот
// (длинные плавные складки с тенями между ними), считает нормали, мягкий свет, блики по краю
// и цвет по наклону поверхности. К левому краю складки сходят на нет. Без библиотек и без
// реакции на курсор: ткань медленно течёт сама.

const VERTEX_SHADER = `
attribute vec2 aPosition;
void main() {
  gl_Position = vec4(aPosition, 0.0, 1.0);
}`;

const FRAGMENT_SHADER = `
#ifdef GL_FRAGMENT_PRECISION_HIGH
precision highp float;
#else
precision mediump float;
#endif

uniform vec2 uResolution;
uniform float uTime;

// Палитра бренда
const vec3 PEACH = vec3(1.00, 0.80, 0.66);
const vec3 ORANGE = vec3(1.00, 0.38, 0.16);
const vec3 CORAL = vec3(1.00, 0.54, 0.46);
const vec3 PINK = vec3(1.00, 0.64, 0.78);
const vec3 BLUE = vec3(0.60, 0.77, 1.00);

// Высота ткани в точке пола p: длинные диагональные волны с плавным изгибом
float cloth(vec2 p, float t) {
  float along = dot(p, vec2(0.86, 0.50));
  float across = dot(p, vec2(-0.50, 0.86));

  float w1 = sin(along * 1.75 + 0.9 * sin(across * 0.75 + t * 0.18) + t * 0.22) * 0.5 + 0.5;
  float w2 = sin(along * 3.40 - across * 0.50 + t * 0.27 + w1 * 2.0) * 0.5 + 0.5;
  float w3 = sin(along * 6.40 + 1.3 * sin(across * 1.40 - t * 0.20) - t * 0.35) * 0.5 + 0.5;
  float waves = w1 * 0.66 + w2 * 0.26 + w3 * 0.08;

  // Слева складки тают до нуля, вдали тоже
  // Граница слева идёт по диагонали: складки спускаются к нижнему краю экрана и уходят за него,
  // а не обрываются вертикальной линией
  float envelope = smoothstep(-3.2, -0.8, p.x - 0.55 * p.y) * (1.0 - smoothstep(5.0, 9.0, p.y));
  return envelope * (0.22 + 1.45 * waves);
}

float hash(vec2 p) {
  return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

void main() {
  vec2 uv = (gl_FragCoord.xy - 0.5 * uResolution) / uResolution.y;
  // Сдвигаем всю сцену вниз на 17% высоты: верхний край ткани на уровне подзаголовка
  uv.y += 0.17;
  float t = uTime;

  // Камера смотрит вдоль пола сверху вниз под небольшим углом; цель левее, поэтому ткань уходит вправо
  vec3 ro = vec3(-0.6, 2.1, -3.4);
  vec3 target = vec3(1.0, 0.55, 1.4);
  vec3 forward = normalize(target - ro);
  vec3 right = normalize(cross(vec3(0.0, 1.0, 0.0), forward));
  vec3 up = cross(forward, right);
  vec3 rd = normalize(forward + right * uv.x * 1.45 + up * uv.y * 1.45);

  float distanceAlong = 0.4;
  float previousDistance = 0.4;
  float hitDistance = -1.0;
  for (int i = 0; i < 80; i++) {
    vec3 pos = ro + rd * distanceAlong;
    float gap = pos.y - cloth(pos.xz, t);
    if (gap < 0.003) {
      hitDistance = distanceAlong;
      break;
    }
    if (pos.y > 1.6 && rd.y > 0.0) break;
    previousDistance = distanceAlong;
    distanceAlong += gap * 0.5 + 0.004 * distanceAlong;
    if (distanceAlong > 26.0) break;
  }

  if (hitDistance < 0.0) {
    gl_FragColor = vec4(0.0);
    return;
  }

  // Уточняем точку попадания бисекцией: без неё на гребнях видны ступеньки
  float low = previousDistance;
  float high = hitDistance;
  for (int i = 0; i < 5; i++) {
    float mid = 0.5 * (low + high);
    vec3 midPos = ro + rd * mid;
    if (midPos.y - cloth(midPos.xz, t) < 0.0) high = mid;
    else low = mid;
  }
  hitDistance = high;

  vec3 pos = ro + rd * hitDistance;
  float h = cloth(pos.xz, t);

  float e = 0.02;
  vec3 normal = normalize(vec3(
    cloth(pos.xz - vec2(e, 0.0), t) - cloth(pos.xz + vec2(e, 0.0), t),
    2.0 * e,
    cloth(pos.xz - vec2(0.0, e), t) - cloth(pos.xz + vec2(0.0, e), t)
  ));

  vec3 light = normalize(vec3(-0.7, 0.45, -0.2));
  float lit = clamp(0.5 + 0.5 * dot(normal, light), 0.0, 1.0);
  float facing = max(dot(normal, -rd), 0.0);

  // Тональный градиент как на шёлке: впадины насыщенные оранжево-коралловые, освещённые гребни бледно-розовые.
  // Медленный дрейф оттенка по поверхности даёт перелив без пестроты
  float drift = 0.5 + 0.5 * sin(pos.x * 0.6 + pos.z * 0.4 - t * 0.25);
  // Впадины между складками насыщенные, гребни бледные
  float tone = smoothstep(0.45, 1.35, h + 0.18 * drift);
  vec3 deep = mix(ORANGE, CORAL, lit * 0.4);
  // Бледные гребни: тёплый персиковый, розовый только лёгким оттенком
  vec3 pale = mix(vec3(1.0, 0.91, 0.85), PEACH, 0.35 + 0.35 * drift);
  pale = mix(pale, PINK, 0.15 * drift);
  vec3 color = mix(deep, pale, tone);

  // Холодные переливы на бледных гребнях: местами розовые, местами голубые
  float coolShift = 0.5 + 0.5 * sin(pos.x * 0.9 - pos.z * 0.5 + h * 2.0 - t * 0.2);
  color = mix(color, mix(PINK, BLUE, coolShift), 0.30 * tone);

  // Тонкая светлая сетка в координатах ткани: повторяет рельеф и перспективу, едет вместе с волнами.
  // Толщина линии пропорциональна расстоянию, то есть постоянна на экране; вдали сетка гаснет
  const float GRID_SPACING = 0.25;
  vec2 gridPos = (pos.xz + vec2(0.86, 0.50) * 0.126 * t) / GRID_SPACING;
  vec2 gridDistance = abs(fract(gridPos - 0.5) - 0.5) * GRID_SPACING;
  float lineHalfWidth = hitDistance / 2400.0;
  float lineSoftness = hitDistance / 1000.0;
  vec2 gridLines = 1.0 - smoothstep(lineHalfWidth, lineHalfWidth + lineSoftness, gridDistance);
  float grid = max(gridLines.x, gridLines.y) * (1.0 - smoothstep(8.0, 12.0, hitDistance));
  color = mix(color, vec3(1.0), grid * 0.22);

  // Стеклянное свечение по краю складок и блик
  float fresnel = pow(1.0 - facing, 4.0);
  color = mix(color, vec3(1.0), fresnel * 0.25);
  color += pow(max(dot(reflect(rd, normal), light), 0.0), 26.0) * 0.5;
  // Светящиеся линии по гребням складок
  color += pow(clamp(normal.y, 0.0, 1.0), 14.0) * 0.28;
  color = mix(color, vec3(1.0), 0.10);

  // Прозрачность: тонкие края и дальние участки растворяются
  float alpha = smoothstep(0.03, 0.22, h) * (1.0 - smoothstep(9.0, 15.0, hitDistance));
  alpha *= mix(0.86, 1.0, lit);

  color += (hash(gl_FragCoord.xy + t) - 0.5) / 255.0;
  gl_FragColor = vec4(color * alpha, alpha);
}`;

const MAX_PIXEL_RATIO = 1.5;
// Поверхность мягкая, поэтому считаем её в сниженном разрешении: быстрее и без потери вида
const RENDER_SCALE = 0.85;
const TIME_SPEED = 1.0;
const STATIC_FRAME_TIME = 6.0;

function compileShader(gl, type, source) {
  const shader = gl.createShader(type);
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    console.warn(gl.getShaderInfoLog(shader));
    return null;
  }
  return shader;
}

function initHeroGl(canvas) {
  const gl = canvas.getContext("webgl", { alpha: true, premultipliedAlpha: true, antialias: false });
  if (!gl) return;

  const vertex = compileShader(gl, gl.VERTEX_SHADER, VERTEX_SHADER);
  const fragment = compileShader(gl, gl.FRAGMENT_SHADER, FRAGMENT_SHADER);
  if (!vertex || !fragment) return;

  const program = gl.createProgram();
  gl.attachShader(program, vertex);
  gl.attachShader(program, fragment);
  gl.linkProgram(program);
  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
    console.warn(gl.getProgramInfoLog(program));
    return;
  }
  gl.useProgram(program);

  // Один треугольник на весь экран
  gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  const position = gl.getAttribLocation(program, "aPosition");
  gl.enableVertexAttribArray(position);
  gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 0, 0);

  const resolutionUniform = gl.getUniformLocation(program, "uResolution");
  const timeUniform = gl.getUniformLocation(program, "uTime");
  gl.clearColor(0, 0, 0, 0);

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let frame = 0;

  function render(seconds) {
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.uniform1f(timeUniform, seconds);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }

  function resize() {
    const ratio = Math.min(window.devicePixelRatio || 1, MAX_PIXEL_RATIO) * RENDER_SCALE;
    const { width, height } = canvas.getBoundingClientRect();
    canvas.width = Math.max(1, Math.round(width * ratio));
    canvas.height = Math.max(1, Math.round(height * ratio));
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.uniform2f(resolutionUniform, canvas.width, canvas.height);
    if (reducedMotion) render(STATIC_FRAME_TIME);
  }

  function loop(now) {
    render((now / 1000) * TIME_SPEED);
    frame = requestAnimationFrame(loop);
  }

  resize();
  new ResizeObserver(resize).observe(canvas);

  if (reducedMotion) return;

  // Не тратим кадры, пока hero за пределами экрана
  new IntersectionObserver(([entry]) => {
    cancelAnimationFrame(frame);
    frame = entry.isIntersecting ? requestAnimationFrame(loop) : 0;
  }).observe(canvas);
}

// Обычный скрипт, а не ES-модуль: модули не загружаются при открытии index.html через file://
window.initHeroGl = initHeroGl;
