// Point d'entrée : ce qui est commun à toutes les pages, puis le module propre à la page.
import { initCartDrawer } from './cart-drawer.js';
import { initSheets } from './dialogs.js';
import { initQuickAdd } from './quick-add.js';
import { initSearch } from './search.js';
import { $$, reducedMotion } from './utils.js';

const root = document.documentElement;

// L'en-tête s'efface quand on descend, revient dès qu'on remonte.
function initHeader() {
  const header = document.querySelector('[data-header]');
  if (!header) return;
  let last = window.scrollY;
  let ticking = false;
  window.addEventListener('scroll', () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      const y = window.scrollY;
      if (Math.abs(y - last) > 8) {
        const hide = y > last && y > 240 && !header.contains(document.activeElement) && !root.classList.contains('is-locked');
        root.classList.toggle('header-hidden', hide);
        last = y;
      }
      ticking = false;
    });
  }, { passive: true });
}

// Apparition douce des blocs à l'arrivée dans l'écran. Ce qui est déjà visible ne bouge pas.
function initReveal() {
  if (reducedMotion() || !('IntersectionObserver' in window)) return;
  const targets = $$('.section__head, .card, .cat, .spot__grid > *, .insta__grid > *, .store__grid > *, .how__list > li, .faq__grid > *');
  if (!targets.length) return;
  const viewport = window.innerHeight;
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-in');
      observer.unobserve(entry.target);
    });
  }, { rootMargin: '0px 0px -8% 0px' });
  targets.forEach((el) => {
    el.setAttribute('data-reveal', '');
    if (el.getBoundingClientRect().top < viewport) {
      el.classList.add('is-in');
      return;
    }
    const index = [...el.parentElement.children].indexOf(el);
    el.style.setProperty('--d', `${Math.min(index % 4, 3) * 70}ms`);
    observer.observe(el);
  });
  root.classList.add('reveal-ready');
}

// Le bouton WhatsApp flottant n'apparaît qu'après un peu de défilement, et s'efface devant le pied de page.
function initWhatsAppFloat() {
  const button = document.querySelector('[data-wa-float]');
  const footer = document.querySelector('.footer');
  if (!button) return;
  let footerVisible = false;
  const update = () => button.classList.toggle('is-on', window.scrollY > 480 && !footerVisible);
  if (footer && 'IntersectionObserver' in window) {
    new IntersectionObserver(([entry]) => { footerVisible = entry.isIntersecting; update(); }).observe(footer);
  }
  window.addEventListener('scroll', update, { passive: true });
  update();
}

initSheets();
initCartDrawer();
initSearch();
initQuickAdd();
initHeader();
initReveal();
initWhatsAppFloat();

const page = document.body.dataset.page;
if (page === 'collection') import('./collection.js').then((m) => m.init());
if (page === 'product') import('./product.js').then((m) => m.init());
if (page === 'checkout') import('./checkout.js').then((m) => m.init());
