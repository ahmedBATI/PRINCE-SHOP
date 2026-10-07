// Point d'entrée : ce qui est commun à toutes les pages, puis le module propre à la page.
import { initCardAdd } from './card-add.js?v=0312c297';
import { initCartDrawer } from './cart-drawer.js?v=0312c297';
import { initSheets } from './dialogs.js?v=0312c297';
import { initQuickAdd } from './quick-add.js?v=0312c297';
import { initSearch } from './search.js?v=0312c297';
import { $$, reducedMotion } from './utils.js?v=0312c297';

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
  const targets = $$('.section__head, .grid > .card, .world, .spot__grid > *, .insta__grid > *, .insta__mosaic, .store__grid > *, .how__list > li');
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

// Rangées horizontales : flèches sur ordinateur, glissement au doigt sur mobile.
function initRails() {
  $$('[data-rail]').forEach((rail) => {
    const section = rail.closest('section');
    const prev = section.querySelector('[data-rail-prev]');
    const next = section.querySelector('[data-rail-next]');
    if (!prev || !next) return;
    const step = () => Math.max(rail.clientWidth * 0.8, 240);
    const update = () => {
      prev.disabled = rail.scrollLeft < 8;
      next.disabled = rail.scrollLeft + rail.clientWidth > rail.scrollWidth - 8;
    };
    prev.addEventListener('click', () => rail.scrollBy({ left: -step(), behavior: reducedMotion() ? 'auto' : 'smooth' }));
    next.addEventListener('click', () => rail.scrollBy({ left: step(), behavior: reducedMotion() ? 'auto' : 'smooth' }));
    rail.addEventListener('scroll', update, { passive: true });
    update();
  });
}

initSheets();
initCartDrawer();
initSearch();
initQuickAdd();
initCardAdd();
initRails();
initHeader();
initReveal();
initWhatsAppFloat();

const page = document.body.dataset.page;
if (page === 'collection') import('./collection.js?v=0312c297').then((m) => m.init());
if (page === 'product') import('./product.js?v=0312c297').then((m) => m.init());
if (page === 'checkout') import('./checkout.js?v=0312c297').then((m) => m.init());
