// Fiche produit : choix de la variante, galerie (glisser, vignettes, zoom), barre d'achat mobile, liens WhatsApp.
import { PRODUCTS } from './site-data.js';
import { cart } from './cart.js';
import { openSheet } from './dialogs.js';
import { bindPicker } from './picker.js';
import { productMessage, waUrl } from './whatsapp.js';
import { $, $$, esc, icon, priceLabel } from './utils.js';

const SIZES = '(min-width:1024px) 45vw, 100vw';

export function init() {
  const root = $('[data-product]');
  const product = PRODUCTS.find((p) => p.id === root?.dataset.product);
  if (!product) return;

  const form = $('[data-picker]', root);
  const gallery = $('[data-gallery]', root);
  const track = $('[data-track]', root);
  const thumbs = $('[data-thumbs]', root);
  const counter = $('[data-gallery-count]', root);
  const photoNote = $('[data-photo-note]', root);
  const buybar = $('[data-buybar]', root);
  const buybarVariant = $('[data-buybar-variant]', root);

  // ---- Galerie
  const imagesFor = (colorData) => (colorData?.images.length ? colorData.images : product.images);
  let images = imagesFor(product.colors[0]);
  let label = product.name;
  let shown = images.map((i) => i.src).join('|');

  function renderGallery(colorData) {
    const next = imagesFor(colorData);
    label = `${product.name}${colorData ? ` — ${colorData.name}` : ''}`;

    // Photo d'une autre couleur que celle choisie : on le dit.
    if (photoNote) {
      const other = Boolean(next.length && colorData && !colorData.images.length && product.photoColor && colorData.name !== product.photoColor);
      photoNote.hidden = !other;
      if (other) photoNote.textContent = `Photo présentée en ${product.photoColor}.`;
    }

    if (!next.length) {
      const ph = $('.ph', track);
      if (!ph || !colorData) return;
      ph.style.setProperty('--c', colorData.hex);
      ph.className = `ph ph--${colorData.tone}`;
      ph.setAttribute('aria-label', `${label} — photo à venir`);
      const caption = $('.ph__cap em', ph);
      if (caption) caption.textContent = colorData.name;
      return;
    }

    const signature = next.map((i) => i.src).join('|');
    if (signature === shown) return;
    images = next;
    shown = signature;
    track.innerHTML = images.map((image, i) =>
      `<figure class="gallery__slide"><button class="gallery__zoom" type="button" data-zoom="${i}" aria-label="Agrandir la photo ${i + 1}">` +
      `<img src="${esc(image.src)}"${image.srcset ? ` srcset="${esc(image.srcset)}" sizes="${SIZES}"` : ''} alt="${esc(label)}" width="1200" height="1500" ${i ? 'loading="lazy"' : ''} decoding="async">` +
      `${icon('expand')}</button></figure>`).join('');
    thumbs.innerHTML = images.map((image, i) =>
      `<button type="button" data-thumb="${i}" aria-label="Photo ${i + 1}"${i === 0 ? ' aria-current="true"' : ''}>` +
      `<img src="${esc(image.thumb)}" alt="" width="64" height="80" loading="lazy" decoding="async"></button>`).join('');
    track.scrollLeft = 0;
    gallery.className = `gallery gallery--${Math.min(images.length, 2)}`;
    thumbs.hidden = counter.hidden = images.length < 2;
    counter.textContent = `1 / ${images.length}`;
  }

  const setCurrent = (index) => {
    counter.textContent = `${index + 1} / ${track.children.length}`;
    $$('[data-thumb]', thumbs).forEach((button, i) => {
      if (i === index) button.setAttribute('aria-current', 'true');
      else button.removeAttribute('aria-current');
    });
  };
  track.addEventListener('scroll', () => {
    if (track.children.length < 2 || !track.clientWidth) return;
    setCurrent(Math.min(Math.round(track.scrollLeft / track.clientWidth), track.children.length - 1));
  }, { passive: true });
  thumbs.addEventListener('click', (event) => {
    const button = event.target.closest('[data-thumb]');
    if (!button) return;
    const index = Number(button.dataset.thumb);
    track.scrollTo({ left: index * track.clientWidth, behavior: 'smooth' });
    setCurrent(index);
  });

  // ---- Zoom plein écran : un toucher pour agrandir, on se déplace en glissant (ou à la souris)
  const zoom = document.getElementById('zoom');
  if (zoom) {
    const stage = $('[data-zoom-stage]', zoom);
    const picture = $('[data-zoom-img]', zoom);
    const count = $('[data-zoom-count]', zoom);
    const hint = $('[data-zoom-hint]', zoom);
    const prev = $('[data-zoom-prev]', zoom);
    const next = $('[data-zoom-next]', zoom);
    let current = 0;

    const show = (index) => {
      current = (index + images.length) % images.length;
      stage.classList.remove('is-zoomed');
      stage.scrollTo(0, 0);
      picture.src = images[current].full;
      picture.alt = label;
      count.textContent = images.length > 1 ? `${current + 1} / ${images.length}` : '';
      hint.textContent = 'Touchez la photo pour zoomer';
      prev.hidden = next.hidden = images.length < 2;
    };
    const pan = (event) => {
      const box = stage.getBoundingClientRect();
      stage.scrollLeft = (stage.scrollWidth - stage.clientWidth) * ((event.clientX - box.left) / box.width);
      stage.scrollTop = (stage.scrollHeight - stage.clientHeight) * ((event.clientY - box.top) / box.height);
    };

    track.addEventListener('click', (event) => {
      const button = event.target.closest('[data-zoom]');
      if (!button || !images.length) return;
      show(Number(button.dataset.zoom));
      openSheet('zoom', { returnFocus: button });
    });
    stage.addEventListener('click', (event) => {
      const zoomed = stage.classList.toggle('is-zoomed');
      hint.textContent = zoomed ? 'Glissez pour vous déplacer' : 'Touchez la photo pour zoomer';
      if (zoomed) pan(event);
    });
    stage.addEventListener('mousemove', (event) => {
      if (stage.classList.contains('is-zoomed') && window.matchMedia('(pointer: fine)').matches) pan(event);
    });
    prev.addEventListener('click', () => show(current - 1));
    next.addEventListener('click', () => show(current + 1));
    zoom.addEventListener('keydown', (event) => {
      if (event.key === 'ArrowLeft') show(current - 1);
      if (event.key === 'ArrowRight') show(current + 1);
    });
  }

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

  // ---- Ajout au panier : le bouton confirme, puis le panier s'ouvre
  const addLabel = $('[data-add-label]', form);
  let labelTimer;
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    if (!product.available || !picker.validate()) return;
    const { color, size } = picker.state();
    cart.add({ id: product.id, color, size });
    if (addLabel) {
      const button = addLabel.closest('button');
      addLabel.textContent = 'Ajouté ✓';
      button.classList.add('is-done');
      clearTimeout(labelTimer);
      labelTimer = setTimeout(() => {
        addLabel.textContent = 'Ajouter au panier';
        button.classList.remove('is-done');
      }, 1800);
    }
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
    }, { threshold: 0.2 }).observe(actions);
    $('[data-buybar-add]', buybar).addEventListener('click', () => form.requestSubmit());
  }
}
