// Le panier : stocké dans le navigateur, sans compte ni serveur.
// On ne garde que { id, color, size, qty } ; nom et prix viennent toujours du catalogue à jour.
import { PRODUCTS } from './site-data.js';
import { storage } from './utils.js';

const KEY = 'princeshop.cart.v1';
const MAX_QTY = 10;
const byId = new Map(PRODUCTS.map((p) => [p.id, p]));
const listeners = new Set();

const keyOf = (item) => [item.id, item.color || '', item.size || ''].join('|');

function load() {
  const raw = storage.read(KEY, []);
  if (!Array.isArray(raw)) return [];
  return raw
    .filter((item) => item && byId.has(item.id))
    .map((item) => ({
      id: item.id,
      color: item.color || '',
      size: item.size || '',
      qty: Math.min(MAX_QTY, Math.max(1, parseInt(item.qty, 10) || 1)),
    }));
}

let items = load();

function commit() {
  storage.write(KEY, items);
  listeners.forEach((fn) => fn());
}

export const cart = {
  MAX_QTY,

  // Lignes prêtes à afficher : produit, variante, prix unitaire et total.
  lines() {
    return items.map((item) => {
      const product = byId.get(item.id);
      const color = product.colors.find((c) => c.name === item.color) || null;
      const sizeGone = Boolean(item.size) && (!product.sizes.includes(item.size) || product.unavailableSizes.includes(item.size));
      const available = product.available && !sizeGone;
      return {
        key: keyOf(item),
        product,
        color: item.color,
        colorData: color,
        size: item.size,
        qty: item.qty,
        available,
        unitPrice: product.price,
        total: product.price == null ? null : product.price * item.qty,
      };
    });
  },

  // Seules les lignes disponibles partent dans la commande.
  orderLines() {
    return this.lines().filter((line) => line.available);
  },

  totals() {
    const lines = this.orderLines();
    return {
      count: lines.reduce((n, line) => n + line.qty, 0),
      subtotal: lines.reduce((sum, line) => sum + (line.total || 0), 0),
      unpriced: lines.filter((line) => line.total == null).reduce((n, line) => n + line.qty, 0),
    };
  },

  count() {
    return items.reduce((n, item) => n + item.qty, 0);
  },

  add({ id, color = '', size = '', qty = 1 }) {
    if (!byId.has(id)) return;
    const key = keyOf({ id, color, size });
    const existing = items.find((item) => keyOf(item) === key);
    if (existing) existing.qty = Math.min(MAX_QTY, existing.qty + qty);
    else items.push({ id, color, size, qty: Math.min(MAX_QTY, qty) });
    commit();
  },

  setQty(key, qty) {
    const item = items.find((entry) => keyOf(entry) === key);
    if (!item) return;
    if (qty < 1) return this.remove(key);
    item.qty = Math.min(MAX_QTY, qty);
    commit();
  },

  remove(key) {
    items = items.filter((item) => keyOf(item) !== key);
    commit();
  },

  clear() {
    items = [];
    commit();
  },

  subscribe(fn) {
    listeners.add(fn);
    return () => listeners.delete(fn);
  },
};

// Autre onglet, ou retour arrière du navigateur : on relit le panier.
function refresh() {
  items = load();
  listeners.forEach((fn) => fn());
}
window.addEventListener('storage', (event) => { if (event.key === KEY) refresh(); });
window.addEventListener('pageshow', (event) => { if (event.persisted) refresh(); });
