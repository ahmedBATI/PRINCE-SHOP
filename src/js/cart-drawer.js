// Tiroir du panier + compteur de l'en-tête.
import { CONFIG } from './site-data.js';
import { cart } from './cart.js';
import { subtotalText } from './whatsapp.js';
import { $, $$, esc, icon, mediaHTML, money, plural } from './utils.js';

const base = CONFIG.base;

export function lineVariant(line) {
  return [line.color, line.size && `${line.size}`].filter(Boolean).join(' · ');
}

export function linePrice(line) {
  if (line.total == null) return `<span class="price price--ask">${esc(CONFIG.priceOnRequest)}</span>`;
  const unit = line.qty > 1 ? `<small>${money(line.unitPrice)} l’unité</small>` : '';
  return `<span class="price">${money(line.total)}</span>${unit}`;
}

// Bloc « Sous-total / Livraison » réutilisé par le tiroir et la page de commande.
export function totalsHTML(totals) {
  const pending = totals.unpriced
    ? `<div class="sum sum--soft"><dt>${plural(totals.unpriced, 'article')} sur demande</dt><dd>prix à confirmer</dd></div>`
    : '';
  const subtotal = totals.unpriced && !totals.subtotal ? 'à confirmer' : money(totals.subtotal);
  const delivery = CONFIG.deliveryFee == null ? esc(CONFIG.deliveryLabel) : money(CONFIG.deliveryFee);
  return `<div class="sum sum--total"><dt>Sous-total produits</dt><dd>${subtotal}</dd></div>${pending}` +
    `<div class="sum sum--soft"><dt>Livraison</dt><dd>${delivery}</dd></div>`;
}

function lineHTML(line) {
  const p = line.product;
  const variant = lineVariant(line);
  const label = `${p.name}${variant ? `, ${variant}` : ''}`;
  const warn = line.available ? '' : '<p class="line__warn">Indisponible — cet article ne sera pas commandé.</p>';
  const controls = line.available
    ? `<div class="qty" role="group" aria-label="Quantité — ${esc(label)}">
        <button type="button" data-qty="-1" data-key="${esc(line.key)}" aria-label="Diminuer la quantité">${icon('minus')}</button>
        <output aria-live="off">${line.qty}</output>
        <button type="button" data-qty="1" data-key="${esc(line.key)}" aria-label="Augmenter la quantité"${line.qty >= cart.MAX_QTY ? ' disabled' : ''}>${icon('plus')}</button>
      </div>`
    : '<span></span>';
  return `<li class="line">
    <a class="line__thumb" href="${esc(p.url)}" tabindex="-1" aria-hidden="true">${mediaHTML(p, line.colorData)}</a>
    <div class="line__info">
      <div class="line__top">
        <div><p class="line__name"><a href="${esc(p.url)}">${esc(p.name)}</a></p>${variant ? `<p class="line__variant">${esc(variant)}</p>` : ''}${warn}</div>
        <p class="line__price">${line.available ? linePrice(line) : ''}</p>
      </div>
      <div class="line__bottom">
        ${controls}
        <button class="line__remove" type="button" data-remove data-key="${esc(line.key)}" aria-label="Retirer ${esc(label)}">Retirer</button>
      </div>
    </div>
  </li>`;
}

function emptyHTML() {
  const links = CONFIG.categories
    .map((c) => `<a class="link" href="${base}/collection/${c.id}/">${esc(c.label)}</a>`).join('');
  return `<div class="cart__empty">
    <strong>Votre sélection est vide</strong>
    <p>Parcourez la collection et ajoutez les modèles qui vous plaisent.</p>
    <a class="btn btn--primary" href="${base}/collection/">Découvrir la collection</a>
    <div class="cart__links">${links}</div>
  </div>`;
}

export function initCartDrawer() {
  const body = $('[data-cart-body]');
  if (!body) return;
  const content = body;
  const live = document.createElement('p');
  live.className = 'sr-only';
  live.setAttribute('role', 'status');
  content.after(live);

  let previousCount = cart.count();

  const render = () => {
    const lines = cart.lines();
    const totals = cart.totals();
    const count = cart.count();

    // Compteur de l'en-tête
    $$('[data-cart-count]').forEach((el) => {
      el.textContent = count;
      el.hidden = count === 0;
      if (count !== previousCount) {
        el.classList.remove('is-bump');
        void el.offsetWidth;
        el.classList.add('is-bump');
      }
    });
    $$('[data-cart-button]').forEach((el) => el.setAttribute('aria-label', count ? `Panier, ${plural(count, 'article')}` : 'Panier, vide'));
    const titleCount = $('[data-cart-title-count]');
    if (titleCount) titleCount.textContent = count ? `(${count})` : '';

    // On garde le focus sur le même bouton après le nouveau rendu.
    const active = document.activeElement;
    const focusKey = content.contains(active) ? active.dataset.key : null;
    const focusAttr = focusKey && (active.hasAttribute('data-remove') ? '[data-remove]' : `[data-qty="${active.dataset.qty}"]`);

    if (!lines.length) {
      content.innerHTML = emptyHTML();
    } else {
      const ready = totals.count > 0;
      content.innerHTML = `<ul class="cart__items">${lines.map(lineHTML).join('')}</ul>
        <div class="cart__foot">
          <dl>${totalsHTML(totals)}</dl>
          ${ready
            ? `<a class="btn btn--primary btn--block" href="${base}/commande/">Passer commande</a>`
            : '<button class="btn btn--primary btn--block" type="button" disabled>Passer commande</button>'}
          <p class="cart__note">Vous vérifiez tout avant l’envoi sur WhatsApp. Aucun compte à créer.</p>
        </div>`;
    }

    if (focusKey) {
      const same = $$(focusAttr, content).find((el) => el.dataset.key === focusKey && !el.disabled);
      (same || $('[data-close]', content.closest('dialog')))?.focus({ preventScroll: true });
    }
    if (count !== previousCount) {
      live.textContent = count ? `Panier mis à jour : ${plural(count, 'article')}, sous-total ${subtotalText(totals)}.` : 'Votre panier est vide.';
    }
    previousCount = count;
  };

  content.addEventListener('click', (event) => {
    const qtyButton = event.target.closest('[data-qty]');
    if (qtyButton) {
      const line = cart.lines().find((l) => l.key === qtyButton.dataset.key);
      if (line) cart.setQty(line.key, line.qty + Number(qtyButton.dataset.qty));
      return;
    }
    const removeButton = event.target.closest('[data-remove]');
    if (removeButton) cart.remove(removeButton.dataset.key);
  });

  cart.subscribe(render);
  render();
}
