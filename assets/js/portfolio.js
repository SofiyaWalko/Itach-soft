// Фильтры портфолио: категория и отрасль выбираются независимо, карточка показывается, если подходит под оба.
// Если новый выбор не сочетается с прежним выбором другой группы, тот сбрасывается;
// если кейсов под фильтр нет вовсе, вместо сетки показывается пояснение
function initPortfolio(root) {
  if (!root) return;

  const GROUPS = ["category", "industry"];
  const GROUP_FIELDS = { category: "categories", industry: "industries" };

  const form = root.querySelector("[data-portfolio-filters]");
  const cards = [...root.querySelectorAll("[data-portfolio-card]")];
  const count = root.querySelector("[data-portfolio-count]");
  const empty = root.querySelector("[data-portfolio-empty]");

  // Две группы фильтров под табами «Категории» и «Отрасли»: пилюли видит только выбранная группа.
  // Пилюли другой группы остаются в разметке с выбранным значением, поэтому её подпись показывается в счётчике
  const panels = Object.fromEntries(GROUPS.map((group) => [group, form.querySelector(`[data-portfolio-group="${group}"]`)]));
  const tabs = [...form.querySelectorAll("[data-portfolio-tab]")];

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      tabs.forEach((item) => item.setAttribute("aria-selected", String(item === tab)));
      GROUPS.forEach((group) => panels[group].hidden = group !== tab.dataset.portfolioTab);
    });
  });

  const tagsOf = (card, group) => card.dataset[GROUP_FIELDS[group]].split(" ");
  const matches = (card, selection) => GROUPS.every((group) => !selection[group] || tagsOf(card, group).includes(selection[group]));
  const readSelection = () => Object.fromEntries(GROUPS.map((group) => [group, form.elements[group].value]));

  function select(group, value) {
    form.querySelector(`input[name="${group}"][value="${value}"]`).checked = true;
  }

  function update(changedGroup, animate = true) {
    let selection = readSelection();

    // Выбранный раньше вариант другой группы мог перестать сочетаться с новым — тогда он сбрасывается
    const other = GROUPS.find((group) => group !== changedGroup);
    if (changedGroup && selection[other] && !cards.some((card) => matches(card, selection))) {
      select(other, "");
      selection = readSelection();
    }

    let shown = 0;
    const labels = [];
    GROUPS.forEach((group) => {
      const input = form.querySelector(`input[name="${group}"]:checked`);
      if (!input.value) return;
      labels.push(input.closest(".calc-option").querySelector(".calc-option__text").textContent);
    });
    cards.forEach((card) => {
      const isShown = matches(card, selection);
      card.hidden = !isShown;
      card.classList.remove("is-filtered");
      if (!isShown) return;
      card.style.setProperty("--n", shown++);
      if (animate) {
        // Перезапуск анимации появления: без перерасчёта стилей класс не сработает повторно
        void card.offsetWidth;
        card.classList.add("is-filtered");
      }
    });

    count.textContent = `Показано ${shown} из ${cards.length}${labels.length ? ` · ${labels.join(" · ")}` : ""}`;
    empty.hidden = shown > 0;
  }

  form.addEventListener("change", (event) => update(event.target.name));

  update(null, false);
}

initPortfolio(document.querySelector("[data-portfolio]"));
