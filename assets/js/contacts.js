// Копирование телефонов, адресов и реквизитов: кнопка с data-copy и общее уведомление внизу экрана
const COPY_TOAST_DELAY = 2200;
const COPY_ICON_DELAY = 1600;

async function copyText(value) {
  if (navigator.clipboard && window.isSecureContext) {
    try {
      await navigator.clipboard.writeText(value);
      return true;
    } catch {
      // Ниже — запасной способ: Clipboard API может быть недоступен без разрешения
    }
  }

  const area = document.createElement("textarea");
  area.value = value;
  area.setAttribute("readonly", "");
  area.style.position = "fixed";
  area.style.opacity = "0";
  document.body.append(area);
  area.focus();
  area.select();
  area.setSelectionRange(0, value.length);

  let copied = false;
  try {
    copied = document.execCommand("copy");
  } catch {
    copied = false;
  }
  area.remove();
  return copied;
}

function initCopyButtons() {
  const toast = document.querySelector("[data-copy-toast]");
  const buttons = document.querySelectorAll("[data-copy]");
  if (!toast || !buttons.length) return;

  let toastTimer;
  const showToast = (message, state) => {
    toast.textContent = message;
    toast.classList.toggle("is-error", state === "error");
    toast.classList.add("is-visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("is-visible"), COPY_TOAST_DELAY);
  };

  buttons.forEach((button) => {
    button.addEventListener("click", async () => {
      const copied = await copyText(button.dataset.copy);
      const use = button.querySelector("use");
      const icon = use?.getAttribute("href");

      if (!copied) {
        showToast("Не удалось скопировать — выделите текст вручную", "error");
        return;
      }

      showToast(button.dataset.copyDone || "Скопировано");

      if (!use || !icon) return;
      use.setAttribute("href", "#icon-check");
      button.classList.add("is-copied");
      setTimeout(() => {
        use.setAttribute("href", icon);
        button.classList.remove("is-copied");
      }, COPY_ICON_DELAY);
    });
  });
}

// Карта офисов: Яндекс.Карты загружаются только при подходе к блоку, метка — фирменный пин
const CONTACTS_MAP_ZOOM = 16;
const CONTACTS_MAP_CITIES = {
  smolensk: {
    center: [54.783103, 32.053075],
    title: "Смоленск",
    mapsUrl: "https://yandex.ru/maps/?ll=32.053075,54.783103&z=17&pt=32.053075,54.783103",
  },
  minsk: {
    center: [53.860652, 27.478875],
    title: "Минск",
    mapsUrl: "https://yandex.ru/maps/?ll=27.478875,53.860652&z=17&pt=27.478875,53.860652",
  },
};

let yandexMapsLoader;

function loadYandexMaps() {
  if (window.ymaps) return new Promise((resolve) => window.ymaps.ready(resolve));
  if (yandexMapsLoader) return yandexMapsLoader;

  yandexMapsLoader = new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = "https://api-maps.yandex.ru/2.0/?load=package.standard,package.geoObjects&lang=ru-RU";
    script.async = true;
    script.onload = () => (window.ymaps ? window.ymaps.ready(resolve) : reject(new Error("ymaps")));
    script.onerror = () => reject(new Error("Yandex Maps"));
    document.head.append(script);
  });
  return yandexMapsLoader;
}

function initContactsMap() {
  const canvas = document.querySelector("[data-contacts-map]");
  if (!canvas) return;

  const buttons = [...document.querySelectorAll("[data-map-city]")];
  const link = document.querySelector("[data-map-link]");
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let activeCity = canvas.dataset.mapCity || "smolensk";
  let map = null;
  let placemark = null;

  const updateControls = () => {
    const city = CONTACTS_MAP_CITIES[activeCity];
    buttons.forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.mapCity === activeCity));
    });
    canvas.setAttribute("aria-label", `Карта: офис в ${city.title}`);
    if (link) {
      link.href = city.mapsUrl;
      link.setAttribute("aria-label", `Открыть офис в ${city.title} на Яндекс.Картах`);
    }
  };

  const showCity = (city, animate) => {
    const data = CONTACTS_MAP_CITIES[city];
    if (!data) return;
    activeCity = city;
    updateControls();
    if (!map || !placemark) return;
    map.setCenter(data.center, CONTACTS_MAP_ZOOM, { duration: animate && !reduceMotion ? 450 : 0 });
    placemark.geometry.setCoordinates(data.center);
    placemark.properties.set("hintContent", `Итач-софт, ${data.title}`);
  };

  const start = () => {
    loadYandexMaps()
      .then(() => {
        const data = CONTACTS_MAP_CITIES[activeCity];
        canvas.replaceChildren();
        map = new window.ymaps.Map(canvas, {
          center: data.center,
          zoom: CONTACTS_MAP_ZOOM,
          controls: ["zoomControl"],
          type: "yandex#map",
        });
        placemark = new window.ymaps.Placemark(
          data.center,
          { hintContent: `Итач-софт, ${data.title}` },
          {
            iconLayout: "default#image",
            iconImageHref: "assets/img/map-pin.svg",
            iconImageSize: [56, 68],
            iconImageOffset: [-28, -68],
          },
        );
        map.geoObjects.add(placemark);
        // Колесо мыши листает страницу, а не приближает карту
        map.behaviors.disable("scrollZoom");
        canvas.classList.add("is-ready");
        canvas.setAttribute("aria-busy", "false");
      })
      .catch(() => {
        canvas.classList.add("is-error");
        canvas.setAttribute("aria-busy", "false");
        canvas.textContent = "Карту не удалось загрузить. Адреса офисов — в карточках выше, а открыть точку можно по ссылке ниже.";
      });
  };

  buttons.forEach((button) => {
    button.addEventListener("click", () => showCity(button.dataset.mapCity, true));
  });
  updateControls();

  // API грузим только когда до карты осталось около 300px — не тормозим первую отрисовку
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries, instance) => {
        if (!entries.some((entry) => entry.isIntersecting)) return;
        instance.disconnect();
        start();
      },
      { rootMargin: "300px 0px" },
    );
    observer.observe(canvas);
  } else {
    start();
  }
}

initCopyButtons();
initContactsMap();
