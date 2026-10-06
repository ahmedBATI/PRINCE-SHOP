// Fiche produit : choix de la variante, galerie, barre d'achat mobile, liens WhatsApp.
import { PRODUCTS } from './site-data.js';
import { cart } from './cart.js';
import { openSheet } from './dialogs.js';
import { bindPicker } from './picker.js';
import { productMessage, waUrl } from './whatsapp.js';
import { $, $$, esc, priceLabel } from './utils.js';

export function init() {
  const root = $('[data-product]');
  const product = PRODUCTS.find((p) => p.id === root?.dataset.product);
  if (!product) return;

  const form = $('[data-picker]', root);
  const gallery = $('[data-gallery]', root);
  const track = $('[data-track]', root);
  const counter = $('[data-gallery-count]', root);
  const buybar = $('[data-buybar]', root);
  const buybarVariant = $('[data-buybar-variant]', root);

  // ---- Galerie
  const first = product.colors[0];
  let shownImages = (first?.images.length ? first.images : product.images).join('|');
  function renderGallery(colorData) {
    const images = colorData?.images.length ? colorData.images : product.images;
    const label = `${product.name}${colorData ? ` — ${colorData.name}` : ''}`;
    if (!images.length) {
      const ph = $('.ph', track);
      if (!ph || !colorData) return;
      ph.style.setProperty('--c', colorData.hex);
      ph.className = `ph ph--${colorData.tone}`;
      ph.setAttribute('aria-label', `${label} — photo à venir`);
      const caption = $('.ph__cap em', ph);
      if (caption) caption.textContent = colorData.name;
      return;
    }
    const signature = images.join('|');
    if (signature === shownImages) return;
    track.innerHTML = images.map((src, i) =>
      `<figure class="gallery__slide"><img src="${esc(src)}" alt="${esc(label)}" width="1200" height="1500" ${i ? 'loading="lazy"' : ''} decoding="async"></figure>`).join('');
    track.scrollLeft = 0;
    gallery.className = `gallery gallery--${Math.min(images.length, 2)}`;
    counter.hidden = images.length < 2;
    counter.textContent = `1 / ${images.length}`;
    shownImages = signature;
  }
  track.addEventListener('scroll', () => {
    const total = track.children.length;
    if (total < 2) return;
    const index = Math.round(track.scrollLeft / track.clientWidth) + 1;
    counter.textContent = `${Math.min(index, total)} / ${total}`;
  }, { passive: true });

  // ---- Variante
  const picker = bindPicker(form, product, {
    onChange: ({ color, colorData, size }) => {
      renderGallery(colorData);
      const href = waUrl(productMessage(product, { color, size }));
      $$('[data-wa-product]', root).forEach((link) => { link.href = href; });
      const variant = [color, size].filter(Boolean).join(' · ');
      buybarVariant.textContent = [variant, priceLabel(product.price)].filter(Boolean).join(' — ');
    },
  });
  const wanted = new URLSearchParams(location.search).get('couleur');
  if (wanted) picker.setColor(wanted);
  picker.sync();

  // ---- Ajout au panier
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    if (!product.available || !picker.validate()) return;
    const { color, size } = picker.state();
    cart.add({ id: product.id, color, size });
    openSheet('cart');
  });

  // ---- Barre d'achat mobile : visible dès que le bouton principal sort de l'écran
  const actions = $('[data-actions]', root);
  if (buybar && actions && 'IntersectionObserver' in window) {
    buybar.hidden = false;
    new IntersectionObserver(([entry]) => {
      const on = !entry.isIntersecting;
      buybar.classList.toggle('is-on', on);
      buybar.inert = !on;
      document.body.classList.toggle('has-buybar', on && window.matchMedia('(max-width: 1023px)').matches);
    }, { threshold: 0.2 }).observe(actions);
    $('[data-buybar-add]', buybar).addEventListener('click', () => form.requestSubmit());
  }
}
