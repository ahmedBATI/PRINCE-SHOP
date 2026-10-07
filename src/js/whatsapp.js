// Générateur de messages WhatsApp.
// Le numéro et les formules viennent de data/config.json (contact.WHATSAPP_NUMBER, messages).
import { CONFIG } from './site-data.js';
import { money, plural } from './utils.js';

// En mode démonstration, chaque message commence par un avertissement : la boutique sait que c'est un test.
const withNotice = (text) => (CONFIG.demo && CONFIG.demoOrderNotice ? `${CONFIG.demoOrderNotice}\n\n${text}` : text);

export const waUrl = (text) => `https://wa.me/${CONFIG.whatsapp}?text=${encodeURIComponent(withNotice(text))}`;

const sizeLabel = (product) => CONFIG.categories.find((c) => c.id === product.category)?.sizeLabel || 'Taille';

// • Mocassin Signature (réf. PS-101)
// Couleur : Camel
// Pointure : 42
// Quantité : 1
// Prix : 349 DH
function orderLine(line) {
  const out = [`• ${line.product.name} (réf. ${line.product.ref})`];
  if (line.color) out.push(`Couleur : ${line.color}`);
  if (line.size) out.push(`${sizeLabel(line.product)} : ${line.size}`);
  out.push(`Quantité : ${line.qty}`);
  if (line.total == null) out.push('Prix : à confirmer');
  else out.push(`Prix : ${money(line.total)}${line.qty > 1 ? ` (${money(line.unitPrice)} l'unité)` : ''}`);
  return out.join('\n');
}

export function subtotalText(totals) {
  if (!totals.unpriced) return money(totals.subtotal);
  const pending = `${plural(totals.unpriced, 'article')} à confirmer`;
  return totals.subtotal > 0 ? `${money(totals.subtotal)} + ${pending}` : pending;
}

// Commande complète : articles, sous-total, coordonnées, note. Toujours construite à partir du panier réel.
export function orderMessage(lines, totals, customer) {
  const m = CONFIG.messages;
  const out = [m.greeting, '', m.orderIntro, '', lines.map(orderLine).join('\n\n'), ''];
  out.push(`Sous-total : ${subtotalText(totals)}`);
  out.push(`Livraison : ${CONFIG.deliveryFee == null ? 'à confirmer' : money(CONFIG.deliveryFee)}`);
  out.push('', 'Informations client :');
  out.push(`Nom : ${customer.name}`, `Téléphone : ${customer.phone}`, `Ville : ${customer.city}`, `Adresse : ${customer.address}`);
  if (customer.note) out.push('', 'Note :', customer.note);
  out.push('', m.orderClosing);
  return out.join('\n');
}

// Message tel qu'il part réellement (avec l'avertissement de démonstration le cas échéant).
export const fullMessage = (text) => withNotice(text);

// Question sur un article précis, depuis sa fiche.
export function productMessage(product, { color, size } = {}) {
  const m = CONFIG.messages;
  const parts = [product.name];
  if (color) parts.push(color);
  if (size) parts.push(size);
  return `${m.greeting}\n\n${m.productIntro}\n• ${parts.join(' — ')} (réf. ${product.ref})\n\n${m.productClosing}`;
}
