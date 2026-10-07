// Ajout rapide depuis une carte produit : couleur + pointure sans quitter la liste.
import { cart } from './cart.js';
import { closeSheet, openSheet } from './dialogs.js';
import { bindPicker, pickerHTML } from './picker.js';
import { $, esc, icon, mediaHTML, priceHTML } from './utils.js';

let body;

export function initQuickAdd() {
  body = $('[data-quick-body]');
}

// Ouvre la feuille de choix. `onAdded(product, { color, size })` est appelé une fois la feuille refermée.
export function openQuickAdd(product, trigger, onAdded) {
  if (!body || !product.available) return;

  body.innerHTML = `<div class="quick">
    <div class="quick__head">
      <div class="quick__thumb" data-quick-thumb>${mediaHTML(product)}</div>
      <div><p class="quick__name">${esc(product.name)}</p><p class="quick__price">${priceHTML(product)}</p></div>
      <button class="header__btn" type="button" data-close aria-label="Fermer">${icon('close')}</button>
    </div>
    <form class="quick__form" novalidate>
      <div class="quick__body"><div class="picker">${pickerHTML(product)}</div></div>
      <div class="quick__foot">
        <button class="btn btn--primary btn--block" type="submit">Ajouter au panier</button>
        <a class="link quick__more" href="${esc(product.url)}">Voir le produit${icon('arrow')}</a>
      </div>
    </form>
  </div>`;

  const form = $('form', body);
  const thumb = $('[data-quick-thumb]', body);
  const more = $('.quick__more', body);
  const picker = bindPicker(form, product, {
    onChange: ({ colorData }) => {
      thumb.innerHTML = mediaHTML(product, colorData);
      if (colorData) more.href = `${product.url}?couleur=${colorData.slug}`;
    },
  });

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    if (!picker.validate()) return;
    const { color, size } = picker.state();
    const dialog = form.closest('dialog');
    cart.add({ id: product.id, color, size });
    if (onAdded) dialog.addEventListener('sheet:close', () => onAdded(product, { color, size }), { once: true });
    closeSheet(dialog);
  });

  openSheet('quick', { returnFocus: trigger });
}
