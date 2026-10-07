// Choix de la couleur et de la pointure — utilisé par la fiche produit et par l'ajout rapide.
import { CONFIG } from './site-data.js';
import { $, $$, esc } from './utils.js';

export function sizeLabelFor(product) {
  return CONFIG.categories.find((c) => c.id === product.category)?.sizeLabel || 'Taille';
}

// Même balisage que celui généré côté serveur dans src/pages.py (page_product).
export function pickerHTML(product) {
  let html = '';
  if (product.colors.length === 1) {
    const c = product.colors[0];
    html += `<p class="picker__static"><span>Couleur</span><b>${esc(c.name)}</b><i class="dot dot--${c.tone}" style="--c:${esc(c.hex)}"></i>` +
      `<input type="hidden" name="color" value="${esc(c.name)}"></p>`;
  } else if (product.colors.length) {
    const swatches = product.colors.map((c, i) =>
      `<label class="swatch"><input type="radio" name="color" value="${esc(c.name)}"${i === 0 ? ' checked' : ''}>` +
      `<span class="swatch__dot dot--${c.tone}" style="--c:${esc(c.hex)}"></span><span class="sr-only">${esc(c.name)}</span></label>`).join('');
    html += `<fieldset class="picker__group"><legend><span>Couleur</span><b data-color-name>${esc(product.colors[0].name)}</b></legend>` +
      `<div class="swatches">${swatches}</div></fieldset>`;
  }
  if (product.sizes.length) {
    const label = sizeLabelFor(product);
    const chips = product.sizes.map((s) => {
      const off = product.unavailableSizes.includes(s);
      return `<label class="size${off ? ' size--off' : ''}"><input type="radio" name="size" value="${esc(s)}"${off ? ' disabled' : ''}>` +
        `<span>${esc(s)}</span>${off ? '<span class="sr-only"> (indisponible)</span>' : ''}</label>`;
    }).join('');
    html += `<fieldset class="picker__group" data-size-group><legend><span>${esc(label)}</span><b data-size-name>À choisir</b></legend>` +
      `<div class="sizes">${chips}</div>` +
      `<p class="picker__error" data-size-error role="alert" hidden>Choisissez votre ${esc(label.toLowerCase())} pour continuer.</p>` +
      '<p class="picker__note">Disponibilité confirmée sur WhatsApp.</p></fieldset>';
  }
  return html;
}

export function bindPicker(form, product, { onChange } = {}) {
  const state = () => {
    const colorName = form.elements.color ? new FormData(form).get('color') : '';
    const size = form.elements.size ? new FormData(form).get('size') : '';
    return {
      color: colorName || '',
      colorData: product.colors.find((c) => c.name === colorName) || null,
      size: size || '',
    };
  };

  const sync = () => {
    const current = state();
    const colorName = $('[data-color-name]', form);
    const sizeName = $('[data-size-name]', form);
    if (colorName) colorName.textContent = current.color;
    if (sizeName) sizeName.textContent = current.size || 'À choisir';
    if (current.size) clearError();
    onChange?.(current);
  };

  const clearError = () => {
    $('[data-size-group]', form)?.classList.remove('has-error');
    const error = $('[data-size-error]', form);
    if (error) error.hidden = true;
  };

  form.addEventListener('change', sync);

  return {
    state,
    sync,
    setColor(slug) {
      const match = product.colors.find((c) => c.slug === slug);
      const input = match && $$('input[name="color"]', form).find((el) => el.value === match.name);
      if (!input || input.disabled) return;
      input.checked = true;
      sync();
    },
    // Renvoie false (et montre quoi faire) tant qu'une pointure obligatoire manque.
    validate() {
      if (!product.sizes.length || state().size) return true;
      const group = $('[data-size-group]', form);
      const error = $('[data-size-error]', form);
      group?.classList.add('has-error');
      if (error) error.hidden = false;
      group?.scrollIntoView({ block: 'center', behavior: 'smooth' });
      $('input[name="size"]:not(:disabled)', form)?.focus({ preventScroll: true });
      return false;
    },
  };
}
