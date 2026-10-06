// Petites aides partagées par tous les modules.
import { CONFIG } from './site-data.js';

export const $ = (selector, root = document) => root.querySelector(selector);
export const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

const ENTITIES = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
export const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (c) => ENTITIES[c]);

// Minuscules sans accents : « Crème » et « creme » donnent le même résultat.
export const norm = (value) => String(value ?? '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().trim();

const numberFormat = new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 2 });
export const money = (amount) => `${numberFormat.format(amount)} ${CONFIG.currency}`;
export const priceLabel = (amount) => (amount == null ? CONFIG.priceOnRequest : money(amount));
export const plural = (n, one, many = `${one}s`) => `${n} ${n > 1 ? many : one}`;

export const icon = (name) =>
  `<svg class="icon" width="24" height="24" aria-hidden="true" focusable="false"><use href="#i-${name}"/></svg>`;

export function priceHTML(product) {
  if (product.price == null) return `<span class="price price--ask">${esc(CONFIG.priceOnRequest)}</span>`;
  const old = product.compareAtPrice > product.price ? ` <s>${money(product.compareAtPrice)}</s>` : '';
  return `<span class="price">${money(product.price)}${old}</span>`;
}

// Photo du produit, ou l'échantillon de couleur tant qu'aucune photo n'est fournie.
export function mediaHTML(product, color, alt = '') {
  const c = color || product.colors[0];
  const src = c?.images[0] || product.images[0] || product.colors.find((x) => x.images.length)?.images[0];
  if (src) return `<img src="${esc(src)}" alt="${esc(alt)}" width="1200" height="1500" loading="lazy" decoding="async">`;
  const label = alt ? ` role="img" aria-label="${esc(alt)} — photo à venir"` : ' aria-hidden="true"';
  return `<div class="ph ph--${c ? c.tone : 'light'}" style="--c:${esc(c ? c.hex : '#CFC8BB')}"${label}>` +
    `<span class="ph__chip"></span><span class="ph__cap"><em>${esc(c ? c.name : product.word)}</em><small>Photo à venir</small></span></div>`;
}

// Stockage tolérant : navigation privée ou stockage bloqué ne doivent jamais casser la page.
function area(session) {
  try { return session ? window.sessionStorage : window.localStorage; } catch { return null; }
}
export const storage = {
  read(key, fallback, session = false) {
    try { const raw = area(session)?.getItem(key); return raw ? JSON.parse(raw) : fallback; } catch { return fallback; }
  },
  write(key, value, session = false) {
    try { area(session)?.setItem(key, JSON.stringify(value)); } catch { /* stockage indisponible */ }
  },
  remove(key, session = false) {
    try { area(session)?.removeItem(key); } catch { /* stockage indisponible */ }
  },
};

let toastTimer;
export function toast(message) {
  const el = $('[data-toast]');
  if (!el) return;
  el.textContent = message;
  el.classList.add('is-on');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('is-on'), 2600);
}

export const reducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;
