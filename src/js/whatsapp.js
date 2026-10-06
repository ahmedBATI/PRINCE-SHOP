// Générateur de messages WhatsApp.
// Le numéro et les formules viennent de data/config.json (contact.whatsapp, messages).
import { CONFIG } from './site-data.js';
import { money, plural } from './utils.js';

export const waUrl = (text) => `https://wa.me/${CONFIG.whatsapp}?text=${encodeURIComponent(text)}`;

// « • Mocassin à breloques (réf. PS-101) — Camel — 42 — x1 — 250 DH »
function orderLine(line) {
  const parts = [`${line.product.name} (réf. ${line.product.ref})`];
  if (line.color) parts.push(line.color);
  if (line.size) parts.push(line.size);
  parts.push(`x${line.qty}`);
  if (line.total == null) parts.push('prix à confirmer');
  else parts.push(line.qty > 1 ? `${money(line.total)} (${money(line.unitPrice)} l'unité)` : money(line.total));
  return `• ${parts.join(' — ')}`;
}

export function subtotalText(totals) {
  if (!totals.unpriced) return money(totals.subtotal);
  const pending = `${plural(totals.unpriced, 'article')} à confirmer`;
  return totals.subtotal > 0 ? `${money(totals.subtotal)} + ${pending}` : pending;
}

// Commande complète : articles, sous-total, coordonnées, note.
export function orderMessage(lines, totals, customer) {
  const m = CONFIG.messages;
  const out = [m.greeting, '', m.orderIntro, '', ...lines.map(orderLine), ''];
  out.push(`Sous-total produits : ${subtotalText(totals)}`);
  out.push(`Livraison : ${CONFIG.deliveryFee == null ? 'à confirmer' : money(CONFIG.deliveryFee)}`);
  out.push('', 'Informations client :');
  out.push(`Nom : ${customer.name}`, `Téléphone : ${customer.phone}`, `Ville : ${customer.city}`, `Adresse : ${customer.address}`);
  if (customer.note) out.push('', 'Note :', customer.note);
  out.push('', m.orderClosing);
  return out.join('\n');
}

// Question sur un article précis, depuis sa fiche.
export function productMessage(product, { color, size } = {}) {
  const m = CONFIG.messages;
  const parts = [product.name];
  if (color) parts.push(color);
  if (size) parts.push(size);
  return `${m.greeting}\n\n${m.productIntro}\n• ${parts.join(' — ')} (réf. ${product.ref})\n\n${m.productClosing}`;
}
