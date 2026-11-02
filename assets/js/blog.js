// Блог: фильтр по тегам и сортировка публикаций по дате.
// Тег один, как и категория в портфолио; публикация может нести несколько тегов (data-tags)
function initBlog(root) {
  if (!root) return;

  const form = root.querySelector("[data-blog-filters]");
  const grid = root.querySelector("[data-blog-grid]");
  const cards = [...grid.querySelectorAll("[data-blog-card]")];
  const count = root.querySelector("[data-blog-count]");
  const empty = root.querySelector("[data-blog-empty]");

  const tagsOf = (card) => card.dataset.tags.split(" ");

  function apply() {
    const tag = form.elements.tag.value;
    const direction = sort.getDirection();

    // Перестановка в DOM задаёт порядок в сетке
    [...cards]
      .sort((a, b) => a.dataset.date.localeCompare(b.dataset.date) * direction)
      .forEach((card) => grid.append(card));

    let shown = 0;
    cards.forEach((card) => {
      const isShown = !tag || tagsOf(card).includes(tag);
      card.hidden = !isShown;
      if (isShown) shown += 1;
    });

    count.textContent = `Показано публикаций: ${shown} из ${cards.length}`;
    empty.hidden = shown > 0;
  }

  // Селект сортировки: кнопка-пилюля и список, чтобы вид не зависел от оформления системного списка
  const sort = initSortSelect(root.querySelector("[data-blog-sort]"), apply);

  form.addEventListener("change", apply);
  apply();
}

function initSortSelect(wrapper, onChange) {
  if (!wrapper) return { getDirection: () => -1 };

  const button = wrapper.querySelector("[data-blog-sort-button]");
  const label = wrapper.querySelector("[data-blog-sort-value]");
  const menu = wrapper.querySelector("[data-blog-sort-menu]");
  const options = [...menu.querySelectorAll(".blog__sort-option")];
  let opened = false;

  function setOpen(isOpen) {
    opened = isOpen;
    menu.hidden = !isOpen;
    button.setAttribute("aria-expanded", String(isOpen));
    if (isOpen) options.find((option) => option.getAttribute("aria-selected") === "true")?.focus();
  }

  function select(option) {
    options.forEach((item) => item.setAttribute("aria-selected", String(item === option)));
    label.textContent = option.textContent;
    setOpen(false);
    button.focus();
    onChange();
  }

  button.addEventListener("click", () => setOpen(!opened));

  options.forEach((option) => {
    option.addEventListener("click", () => select(option));
    option.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        select(option);
      }
      if (event.key === "ArrowDown" || event.key === "ArrowUp") {
        event.preventDefault();
        const index = options.indexOf(option);
        const next = options[(index + (event.key === "ArrowDown" ? 1 : -1) + options.length) % options.length];
        next.focus();
      }
    });
  });

  button.addEventListener("keydown", (event) => {
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      setOpen(true);
    }
  });

  wrapper.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && opened) {
      setOpen(false);
      button.focus();
    }
  });

  document.addEventListener("click", (event) => {
    if (opened && !wrapper.contains(event.target)) setOpen(false);
  });

  return {
    getDirection() {
      return menu.querySelector('[aria-selected="true"]').dataset.value === "asc" ? 1 : -1;
    },
  };
}

initBlog(document.querySelector(".blog"));
