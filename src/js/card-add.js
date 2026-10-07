// Bouton d'ajout des cartes produit. Il montre toujours l'état réel du panier :
//   « + »        rien dans le panier
//   « − 1 + »    article sans option : on règle la quantité sur place
//   « 2 + »      article à options (couleur, pointure) : le chiffre = quantité au panier, un clic rouvre le choix
import { PRODUCTS } from './site-data.js';
import { cart } from './cart.js';
import { openQuickAdd } from './quick-add.js';
import { $$, esc, icon, mediaHTML, toast } from './utils.js';

const byId = new Map(PRODUCTS.map((p) => [p.id, p]));
const isSimple = (product) => !product.sizes.length && product.colors.length <= 1;
const qtyOf = (id) => cart.lines().filter((line) => line.product.id === id).reduce((n, line) => n + line.qty, 0);

// Confirmation discrète après un ajout, avec un accès direct au panier.
export function announceAdded(product, { color = '', size = '' } = {}) {
  const colorData = product.colors.find((c) => c.name === color) || null;
  const variant = [product.name, color, size].filter(Boolean).join(' · ');
  toast(
    `<span class="toast__thumb">${mediaHTML(product, colorData)}</span>` +
    `<span class="toast__text"><strong>Ajouté au panier</strong><small>${esc(variant)}</small></span>` +
    '<button class="toast__btn" type="button" data-open="cart">Voir le panier</button>',
    { html: true, duration: 4200 },
  );
}

function render(holder, { pop = false } = {}) {
  const product = byId.get(holder.dataset.add);
  if (!product) return;
  const n = qtyOf(product.id);
  if (holder.dataset.state === String(n)) return;
  const grew = n > Number(holder.dataset.state || 0);
  const role = holder.contains(document.activeElement) ? document.activeElement.dataset.role : null;
  holder.dataset.state = String(n);

  if (!n) {
    holder.innerHTML = `<button class="add__btn" type="button" data-add-btn data-role="add" aria-label="Ajouter au panier : ${esc(product.name)}">${icon('plus')}</button>`;
  } else if (isSimple(product)) {
    holder.innerHTML = `<div class="add__stepper" role="group" aria-label="${esc(product.name)} : quantité dans le panier">` +
      `<button type="button" data-add-dec data-role="dec" aria-label="Retirer un">${icon('minus')}</button><output>${n}</output>` +
      `<button type="button" data-add-inc data-role="inc" aria-label="Ajouter un"${n >= cart.MAX_QTY ? ' disabled' : ''}>${icon('plus')}</button></div>`;
  } else {
    holder.innerHTML = `<button class="add__btn is-in" type="button" data-add-btn data-role="add" aria-label="${esc(product.name)} : ${n} dans le panier. Ajouter une autre couleur ou pointure">` +
      `<span class="add__n">${n}${icon('plus')}</span></button>`;
  }

  if (role) (holder.querySelector(`[data-role="${role}"]:not(:disabled)`) || holder.querySelector('button'))?.focus({ preventScroll: true });
  if (pop && grew) {
    holder.classList.remove('is-pop');
    void holder.offsetWidth;
    holder.classList.add('is-pop');
  }
}

export function initCardAdd() {
  const sync = (options) => $$('[data-add]').forEach((holder) => render(holder, options));

  document.addEventListener('click', (event) => {
    const holder = event.target.closest('[data-add]');
    if (!holder) return;
    const product = byId.get(holder.dataset.add);
    if (!product || !product.available) return;
    const color = product.colors[0]?.name || '';

    if (event.target.closest('[data-add-btn]')) {
      if (isSimple(product)) {
        cart.add({ id: product.id, color });
        announceAdded(product, { color });
      } else {
        openQuickAdd(product, event.target.closest('[data-add-btn]'), announceAdded);
      }
    } else if (event.target.closest('[data-add-inc]')) {
      cart.add({ id: product.id, color });
    } else if (event.target.closest('[data-add-dec]')) {
      const line = cart.lines().find((l) => l.product.id === product.id);
      if (line) cart.setQty(line.key, line.qty - 1);
    }
  });

  cart.subscribe(() => sync({ pop: true }));
  sync();
}
