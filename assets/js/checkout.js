// Page de commande : formulaire court → vérification → envoi sur WhatsApp.
// Rien n'est envoyé à un serveur : la commande part dans le message WhatsApp du client.
import { cart } from './cart.js?v=0312c297';
import { linePrice, lineVariant, totalsHTML } from './cart-drawer.js?v=0312c297';
import { fullMessage, orderMessage, waUrl } from './whatsapp.js?v=0312c297';
import { $, $$, esc, icon, mediaHTML, money, plural, storage, toast } from './utils.js?v=0312c297';

const DRAFT_KEY = 'princeshop.order.v1'; // brouillon du formulaire, gardé le temps de l'onglet
const FIELDS = ['name', 'phone', 'city', 'address', 'note'];
const STEPS = ['form', 'review', 'sent', 'done'];

// 06 12 34 56 78, 0612345678, +212 6 12 34 56 78, 00212612345678 → « 06 12 34 56 78 »
export function normalizePhone(value) {
  const raw = String(value).replace(/[^\d+]/g, '');
  const local = raw.match(/^(?:\+212|00212|212|0)([5-7]\d{8})$/);
  if (local) return `0${local[1]}`.replace(/(\d{2})(?=\d)/g, '$1 ');
  if (/^(?:\+|00)\d{8,15}$/.test(raw)) return raw.replace(/^00/, '+'); // numéro étranger
  return null;
}

const RULES = {
  name: (v) => (v.trim().length >= 3 ? '' : 'Indiquez votre nom complet.'),
  phone: (v) => (normalizePhone(v) ? '' : 'Entrez un numéro valide, par exemple 06 12 34 56 78.'),
  city: (v) => (v.trim().length >= 2 ? '' : 'Indiquez votre ville.'),
  address: (v) => (v.trim().length >= 5 ? '' : 'Indiquez votre adresse de livraison.'),
};

export function init() {
  const root = $('[data-checkout]');
  if (!root) return;
  const main = $('[data-co-main]', root);
  const empty = $('[data-co-empty]', root);
  const form = $('[data-order-form]', root);
  const summary = $('[data-summary]', root);
  const sections = Object.fromEntries(STEPS.map((step) => [step, $(`[data-step="${step}"]`, root)]));
  const wide = window.matchMedia('(min-width: 900px)');
  let step = 'form';
  let message = '';

  // ---- Brouillon
  const draft = storage.read(DRAFT_KEY, {}, true);
  FIELDS.forEach((name) => { if (draft[name]) form.elements[name].value = draft[name]; });
  const values = () => Object.fromEntries(FIELDS.map((name) => [name, form.elements[name].value.trim()]));
  form.addEventListener('input', () => storage.write(DRAFT_KEY, values(), true));

  // ---- Validation
  function check(name) {
    const input = form.elements[name];
    const error = RULES[name]?.(input.value) || '';
    const slot = $(`[data-error="${name}"]`, form);
    input.closest('.field').classList.toggle('has-error', Boolean(error));
    input.setAttribute('aria-invalid', String(Boolean(error)));
    if (slot) {
      slot.textContent = error;
      slot.hidden = !error;
      slot.id = `error-${name}`;
      const described = (input.getAttribute('aria-describedby') || '').split(' ').filter((id) => id && id !== slot.id);
      if (error) described.push(slot.id);
      if (described.length) input.setAttribute('aria-describedby', described.join(' '));
      else input.removeAttribute('aria-describedby');
    }
    return !error;
  }
  Object.keys(RULES).forEach((name) => {
    const input = form.elements[name];
    input.addEventListener('blur', () => { if (input.value.trim() || input.closest('.field').classList.contains('has-error')) check(name); });
    input.addEventListener('input', () => { if (input.closest('.field').classList.contains('has-error')) check(name); });
  });
  form.elements.phone.addEventListener('blur', () => {
    const clean = normalizePhone(form.elements.phone.value);
    if (clean) form.elements.phone.value = clean;
  });

  // ---- Rendu
  const miniHTML = (line) => `<div class="mini">
      <div class="mini__thumb">${mediaHTML(line.product, line.colorData)}</div>
      <div><p class="mini__name">${esc(line.product.name)}</p><p class="mini__variant">${esc([lineVariant(line), `x${line.qty}`].filter(Boolean).join(' · '))}</p></div>
      <p class="mini__price">${linePrice(line)}</p>
    </div>`;

  function renderSummary() {
    const lines = cart.orderLines();
    const totals = cart.totals();
    const wasOpen = $('.sumbox', summary)?.open;
    summary.innerHTML = `<details class="sumbox"${wide.matches || wasOpen ? ' open' : ''}>
      <summary><span>Votre sélection · ${plural(totals.count, 'article')}</span><span>${esc(totals.unpriced ? (totals.subtotal ? `${money(totals.subtotal)} + ${totals.unpriced} à confirmer` : 'Prix à confirmer') : money(totals.subtotal))}${icon('chevron')}</span></summary>
      <div class="sumbox__body">
        ${lines.map(miniHTML).join('')}
        <dl>${totalsHTML(totals)}</dl>
        <p class="sumbox__note">Le total définitif (livraison comprise) vous est confirmé sur WhatsApp.</p>
      </div>
    </details>`;
  }

  function renderReview() {
    const customer = { ...values(), phone: normalizePhone(form.elements.phone.value) || form.elements.phone.value.trim() };
    const lines = cart.orderLines();
    const totals = cart.totals();
    const rows = [['Nom', customer.name], ['Téléphone', customer.phone], ['Ville', customer.city], ['Adresse', customer.address]];
    if (customer.note) rows.push(['Note', customer.note]);
    $('[data-review-customer]', root).innerHTML = rows.map(([k, v]) => `<div><dt>${k}</dt><dd>${esc(v)}</dd></div>`).join('');
    $('[data-review-items]', root).innerHTML = `${lines.map(miniHTML).join('')}<dl class="totals">${totalsHTML(totals)}</dl>`;
    const order = orderMessage(lines, totals, customer);
    message = fullMessage(order); // tel qu'il part : avec l'avertissement de démonstration le cas échéant
    $('[data-message]', root).textContent = message;
    const href = waUrl(order);
    $('[data-send]', root).href = href;
    $('[data-resend]', root).href = href;
  }

  function show(next, { focus = true } = {}) {
    step = next;
    STEPS.forEach((name) => { sections[name].hidden = name !== next; });
    summary.hidden = next !== 'form';
    $$('[data-step-dot]', root).forEach((dot) => {
      const index = STEPS.indexOf(dot.dataset.stepDot);
      const current = Math.min(STEPS.indexOf(next), 2);
      if (index === current) dot.setAttribute('aria-current', 'step');
      else dot.removeAttribute('aria-current');
      dot.classList.toggle('is-done', index < current);
    });
    if (focus) {
      window.scrollTo({ top: 0 });
      if (next !== 'form') sections[next].focus({ preventScroll: true });
    }
  }

  function refresh() {
    if (step === 'done') return;
    const hasItems = cart.orderLines().length > 0;
    main.hidden = !hasItems;
    empty.hidden = hasItems;
    if (!hasItems) return;
    renderSummary();
    if (step !== 'form') renderReview();
  }

  // ---- Étapes
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const invalid = Object.keys(RULES).filter((name) => !check(name));
    if (invalid.length) {
      const first = form.elements[invalid[0]];
      first.focus({ preventScroll: true });
      first.closest('.field').scrollIntoView({ block: 'center', behavior: 'smooth' });
      return;
    }
    form.elements.phone.value = normalizePhone(form.elements.phone.value);
    storage.write(DRAFT_KEY, values(), true);
    renderReview();
    history.pushState({ step: 'review' }, '', '#verification');
    show('review');
  });

  root.addEventListener('click', (event) => {
    if (event.target.closest('[data-edit]')) {
      if (step === 'sent') show('review');
      else if (history.state?.step === 'review') history.back();
      else show('form');
      return;
    }
    if (event.target.closest('[data-send]')) {
      // Le lien ouvre WhatsApp dans un nouvel onglet ; on affiche la suite juste après.
      setTimeout(() => show('sent'), 700);
      return;
    }
    if (event.target.closest('[data-copy]')) {
      const done = () => toast('Message copié');
      if (navigator.clipboard?.writeText) navigator.clipboard.writeText(message).then(done, () => toast('Copie impossible — sélectionnez le message à la main'));
      else toast('Copie impossible sur ce navigateur');
      return;
    }
    if (event.target.closest('[data-done]')) {
      step = 'done';
      storage.remove(DRAFT_KEY, true);
      cart.clear();
      history.replaceState(null, '', location.pathname);
      show('done');
    }
  });

  // Bouton « retour » du navigateur : de la vérification vers le formulaire.
  window.addEventListener('popstate', (event) => {
    if (step === 'done') return;
    show(event.state?.step === 'review' ? 'review' : 'form');
  });

  wide.addEventListener('change', renderSummary);
  cart.subscribe(refresh);
  refresh();

  // Page actualisée pendant la vérification : on y revient si tout est encore valide.
  const valid = Object.keys(RULES).every((name) => !RULES[name](form.elements[name].value));
  if (location.hash === '#verification' && valid && cart.orderLines().length) {
    history.replaceState({ step: 'review' }, '', '#verification');
    renderReview();
    show('review', { focus: false });
  } else if (location.hash) {
    history.replaceState(null, '', location.pathname);
  }
}
