// Recherche instantanée dans le catalogue (nom, catégorie, couleurs, mots-clés, référence).
import { CONFIG, PRODUCTS } from './site-data.js?v=0312c297';
import { waUrl } from './whatsapp.js?v=0312c297';
import { $, esc, icon, mediaHTML, norm, plural, priceHTML } from './utils.js?v=0312c297';

const MAX_RESULTS = 8;
const categoryLabel = new Map(CONFIG.categories.map((c) => [c.id, c.label]));

const haystacks = new Map(PRODUCTS.map((p) => [p.id, norm([
  p.name, p.typeLabel, categoryLabel.get(p.category), p.word, p.ref, ...p.tags, ...p.colors.map((c) => c.name),
].join(' '))]));

// Chaque mot tapé doit se retrouver quelque part ; « sac noir » trouve les sacs disponibles en noir.
export function searchProducts(query, list = PRODUCTS) {
  const tokens = norm(query).split(/\s+/).filter(Boolean).map((t) => (t.length > 3 ? t.replace(/s$/, '') : t));
  if (!tokens.length) return [];
  return list.filter((p) => tokens.every((t) => haystacks.get(p.id).includes(t)));
}

export function initSearch() {
  const dialog = document.getElementById('search');
  if (!dialog) return;
  const input = $('[data-search-input]', dialog);
  const form = $('[data-search-form]', dialog);
  const idle = $('[data-search-idle]', dialog);
  const results = $('[data-search-results]', dialog);

  const render = () => {
    const query = input.value.trim();
    idle.hidden = Boolean(query);
    if (!query) {
      results.innerHTML = '';
      return;
    }
    const found = searchProducts(query);
    if (!found.length) {
      const message = `${CONFIG.messages.greeting}\n\nJe cherche : ${query}. Vous l'avez en boutique ?`;
      results.innerHTML = `<div class="results__none">
        <strong>Aucun résultat pour « ${esc(query)} »</strong>
        <p>Tous les modèles ne sont pas encore en ligne. Demandez-nous directement.</p>
        <a class="btn btn--ghost" href="${esc(waUrl(message))}" target="_blank" rel="noopener">${icon('whatsapp')}Demander sur WhatsApp</a>
      </div>`;
      return;
    }
    // Catégories et types dont le nom correspond : un raccourci vers la bonne liste.
    const tokens = norm(query).split(/\s+/).filter(Boolean).map((t) => (t.length > 3 ? t.replace(/s$/, '') : t));
    const matches = (label) => tokens.every((t) => norm(label).includes(t));
    const shortcuts = [];
    CONFIG.categories.forEach((c) => {
      if (matches(c.label)) shortcuts.push({ label: c.label, url: `${CONFIG.base}/collection/${c.id}/`, n: PRODUCTS.filter((p) => p.category === c.id).length });
      c.types.forEach((t) => {
        if (matches(t.label)) shortcuts.push({ label: t.label, url: `${CONFIG.base}/collection/${c.id}/?type=${t.id}`, n: PRODUCTS.filter((p) => p.type === t.id).length });
      });
    });
    const cats = shortcuts.length
      ? `<div class="results__cats">${shortcuts.map((s) => `<a href="${esc(s.url)}">${esc(s.label)}<small>${s.n}</small></a>`).join('')}</div>`
      : '';
    const rows = found.slice(0, MAX_RESULTS).map((p) => `<li><a href="${esc(p.url)}">
        <span class="results__thumb">${mediaHTML(p)}</span>
        <span><span class="results__name">${esc(p.name)}</span><span class="results__cat">${esc(p.typeLabel)}</span></span>
        <span class="results__price">${priceHTML(p)}</span>
      </a></li>`).join('');
    const all = `${CONFIG.base}/collection/?q=${encodeURIComponent(query)}`;
    results.innerHTML = `${cats}<p class="label results__count">${plural(found.length, 'résultat')}</p>
      <ul class="results">${rows}</ul>
      ${found.length > MAX_RESULTS ? `<a class="link results__all" href="${esc(all)}">Voir les ${found.length} résultats${icon('arrow')}</a>` : ''}`;
  };

  input.addEventListener('input', render);
  form.addEventListener('submit', (event) => { if (!input.value.trim()) event.preventDefault(); });
  dialog.addEventListener('sheet:open', () => { input.focus(); input.select(); });
}
