// Page collection : filtres, tri et recherche — le tout reflété dans l'adresse
// (un lien filtré peut être partagé, et « retour » / « actualiser » gardent l'état).
import { CONFIG, PRODUCTS } from './site-data.js?v=0312c297';
import { searchProducts } from './search.js?v=0312c297';
import { $, $$, esc, icon, money } from './utils.js?v=0312c297';

export function init() {
  const grid = $('[data-grid]');
  if (!grid) return;
  const scope = JSON.parse(grid.dataset.scope || '{}');
  const cards = new Map($$('.card', grid).map((card) => [card.dataset.id, card]));
  const products = PRODUCTS.filter((p) => cards.has(p.id));
  const title = $('[data-plp-title]');
  const baseTitle = title.textContent;

  // ---- Facettes disponibles, déduites des produits réellement présents
  const facets = { cats: [], colors: [], sizes: [], prices: [] };
  if (!scope.category) {
    facets.cats = CONFIG.categories.filter((c) => products.some((p) => p.category === c.id));
    if (facets.cats.length < 2) facets.cats = [];
  }
  const colorMap = new Map();
  products.forEach((p) => p.colors.forEach((c) => { if (!colorMap.has(c.slug)) colorMap.set(c.slug, c); }));
  facets.colors = [...colorMap.values()].sort((a, b) => a.name.localeCompare(b.name, 'fr'));
  facets.sizes = [...new Set(products.flatMap((p) => p.sizes))].sort((a, b) => parseFloat(a) - parseFloat(b) || a.localeCompare(b));
  const priced = products.filter((p) => p.price != null);
  if (products.length && priced.length / products.length >= CONFIG.priceFilterMinShare) {
    facets.prices = CONFIG.priceRanges
      .map(([min, max], index) => ({ index: String(index), min, max, label: max == null ? `Plus de ${money(min)}` : min === 0 ? `Moins de ${money(max)}` : `${min} – ${money(max)}` }))
      .filter((r) => priced.some((p) => p.price >= r.min && (r.max == null || p.price < r.max)));
  }

  // ---- État, lu depuis l'adresse
  const params = new URLSearchParams(location.search);
  const list = (name) => new Set((params.get(name) || '').split(',').filter(Boolean));
  const state = {
    type: params.get('type') || '',
    cats: list('cat'),
    colors: list('couleur'),
    sizes: list('pointure'),
    prices: list('prix'),
    sort: params.get('tri') || 'nouveautes',
    q: (params.get('q') || '').trim(),
  };

  const sortSelect = $('[data-sort]');
  if (![...sortSelect.options].some((o) => o.value === state.sort)) state.sort = 'nouveautes';
  sortSelect.value = state.sort;

  // ---- Panneau de filtres
  const panel = $('[data-filters]');
  const option = (group, value, label, extra = '', cls = '') =>
    `<label class="fopt ${cls}"><input type="checkbox" data-group="${group}" value="${esc(value)}"><span>${extra}${esc(label)}</span></label>`;
  const fieldset = (legend, html) => `<fieldset><legend class="label">${legend}</legend><div class="fopts">${html}</div></fieldset>`;
  let panelHTML = '';
  if (facets.cats.length) panelHTML += fieldset('Catégorie', facets.cats.map((c) => option('cats', c.id, c.label)).join(''));
  if (facets.colors.length > 1) {
    panelHTML += fieldset('Couleur', facets.colors.map((c) =>
      option('colors', c.slug, c.name, `<i class="dot dot--${c.tone}" style="--c:${esc(c.hex)}"></i>`)).join(''));
  }
  if (facets.sizes.length > 1) panelHTML += fieldset('Pointure', facets.sizes.map((s) => option('sizes', s, s, '', 'fopt--size')).join(''));
  if (facets.prices.length > 1) panelHTML += fieldset('Prix', facets.prices.map((r) => option('prices', r.index, r.label)).join(''));
  panel.innerHTML = panelHTML || '<p class="picker__note">Pas de filtre disponible pour cette sélection.</p>';
  const filterButton = $('[data-open="filters"]');
  if (!panelHTML) filterButton.hidden = true;

  // ---- Application
  const sorters = {
    nouveautes: (a, b) => b.date.localeCompare(a.date),
    'prix-asc': (a, b) => (a.price ?? Infinity) - (b.price ?? Infinity),
    'prix-desc': (a, b) => (b.price ?? -Infinity) - (a.price ?? -Infinity),
  };
  const inPrice = (p) => [...state.prices].some((index) => {
    const range = facets.prices.find((r) => r.index === index);
    return range && p.price != null && p.price >= range.min && (range.max == null || p.price < range.max);
  });

  function apply({ updateUrl = true } = {}) {
    const searched = state.q ? new Set(searchProducts(state.q, products).map((p) => p.id)) : null;
    const visible = products.filter((p) =>
      (!state.type || p.type === state.type) &&
      (!state.cats.size || state.cats.has(p.category)) &&
      (!state.colors.size || p.colors.some((c) => state.colors.has(c.slug))) &&
      (!state.sizes.size || p.sizes.some((s) => state.sizes.has(s) && !p.unavailableSizes.includes(s))) &&
      (!state.prices.size || inPrice(p)) &&
      (!searched || searched.has(p.id)));
    const order = [...visible].sort(sorters[state.sort]);
    const shown = new Set(order.map((p) => p.id));

    order.forEach((p) => grid.appendChild(cards.get(p.id)));
    cards.forEach((card, id) => card.classList.toggle('is-hidden', !shown.has(id)));

    $$('[data-count]').forEach((el) => { el.textContent = order.length; });
    $$('[data-count-label]').forEach((el) => { el.textContent = order.length > 1 ? 'articles' : 'article'; });
    $('[data-empty]').hidden = order.length > 0;
    grid.hidden = order.length === 0;
    title.textContent = state.q ? `« ${state.q} »` : baseTitle;

    // Puces de type + cases du panneau
    $$('[data-type]').forEach((chip) => {
      const on = chip.dataset.type === state.type;
      chip.classList.toggle('is-active', on);
      chip.setAttribute('aria-pressed', String(on));
    });
    $$('input[data-group]', panel).forEach((input) => { input.checked = state[input.dataset.group].has(input.value); });

    // Filtres actifs
    const tags = [];
    if (state.q) tags.push({ group: 'q', value: '', label: `Recherche : ${state.q}` });
    state.cats.forEach((id) => tags.push({ group: 'cats', value: id, label: facets.cats.find((c) => c.id === id)?.label || id }));
    state.colors.forEach((slug) => tags.push({ group: 'colors', value: slug, label: colorMap.get(slug)?.name || slug }));
    state.sizes.forEach((s) => tags.push({ group: 'sizes', value: s, label: `Pointure ${s}` }));
    state.prices.forEach((i) => tags.push({ group: 'prices', value: i, label: facets.prices.find((r) => r.index === i)?.label || '' }));
    const active = $('[data-active]');
    active.hidden = tags.length === 0;
    active.innerHTML = tags.map((t) =>
      `<span class="tag">${esc(t.label)}<button type="button" data-untag="${t.group}" data-value="${esc(t.value)}" aria-label="Retirer le filtre ${esc(t.label)}">${icon('close')}</button></span>`).join('') +
      (tags.length > 1 ? '<button class="link" type="button" data-clear>Tout effacer</button>' : '');
    const n = state.cats.size + state.colors.size + state.sizes.size + state.prices.size;
    const badge = $('[data-filter-count]');
    badge.hidden = n === 0;
    badge.textContent = n;

    if (updateUrl) {
      const next = new URLSearchParams();
      if (state.q) next.set('q', state.q);
      if (state.type) next.set('type', state.type);
      if (state.cats.size) next.set('cat', [...state.cats].join(','));
      if (state.colors.size) next.set('couleur', [...state.colors].join(','));
      if (state.sizes.size) next.set('pointure', [...state.sizes].join(','));
      if (state.prices.size) next.set('prix', [...state.prices].join(','));
      if (state.sort !== 'nouveautes') next.set('tri', state.sort);
      const query = next.toString().replace(/%2C/g, ',');
      history.replaceState(null, '', query ? `${location.pathname}?${query}` : location.pathname);
    }
  }

  function clearAll() {
    state.type = '';
    state.q = '';
    ['cats', 'colors', 'sizes', 'prices'].forEach((group) => state[group].clear());
    apply();
  }

  // ---- Événements
  document.addEventListener('click', (event) => {
    const chip = event.target.closest('[data-type]');
    if (chip) {
      state.type = chip.dataset.type;
      apply();
      return;
    }
    const untag = event.target.closest('[data-untag]');
    if (untag) {
      if (untag.dataset.untag === 'q') state.q = '';
      else state[untag.dataset.untag].delete(untag.dataset.value);
      apply();
      return;
    }
    if (event.target.closest('[data-clear]')) clearAll();
  });
  panel.addEventListener('change', (event) => {
    const input = event.target.closest('input[data-group]');
    if (!input) return;
    const set = state[input.dataset.group];
    if (input.checked) set.add(input.value);
    else set.delete(input.value);
    apply();
  });
  sortSelect.addEventListener('change', () => {
    state.sort = sortSelect.value;
    apply();
  });

  // Valeurs inconnues dans l'adresse (lien ancien, faute de frappe) : on les ignore.
  if (state.type && !products.some((p) => p.type === state.type)) state.type = '';
  [['cats', facets.cats.map((c) => c.id)], ['colors', [...colorMap.keys()]], ['sizes', facets.sizes], ['prices', facets.prices.map((r) => r.index)]]
    .forEach(([group, known]) => state[group].forEach((value) => { if (!known.includes(value)) state[group].delete(value); }));

  apply({ updateUrl: false });
}
