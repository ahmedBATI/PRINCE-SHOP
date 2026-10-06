// Ajout rapide depuis une carte produit : couleur + pointure sans quitter la liste.
import { PRODUCTS } from './site-data.js';
import { cart } from './cart.js';
import { closeSheet, openSheet } from './dialogs.js';
import { bindPicker, pickerHTML } from './picker.js';
import { $, esc, icon, mediaHTML, priceHTML } from './utils.js';

const byId = new Map(PRODUCTS.map((p) => [p.id, p]));

export function initQuickAdd() {
  const body = $('[data-quick-body]');
  if (!body) return;

  document.addEventListener('click', (event) => {
    const trigger = event.target.closest('[data-quick]');
    if (!trigger) return;
    const product = byId.get(trigger.dataset.quick);
    if (!product || !product.available) return;

    // Rien à choisir : on ajoute directement.
    if (!product.sizes.length && product.colors.length <= 1) {
      cart.add({ id: product.id, color: product.colors[0]?.name || '' });
      openSheet('cart', { returnFocus: trigger });
      return;
    }

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
          <a class="link quick__more" href="${esc(product.url)}">Voir la fiche complète${icon('arrow')}</a>
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
    form.addEventListener('submit', (submitEvent) => {
      submitEvent.preventDefault();
      if (!picker.validate()) return;
      const { color, size } = picker.state();
      cart.add({ id: product.id, color, size });
      const dialog = form.closest('dialog');
      const returnFocus = dialog._returnFocus;
      closeSheet(dialog);
      openSheet('cart', { returnFocus });
    });

    openSheet('quick', { returnFocus: trigger });
  });
}
