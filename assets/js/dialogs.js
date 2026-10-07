// Panneaux (menu, recherche, panier, ajout rapide, filtres) bâtis sur <dialog> :
// le navigateur gère le piège à focus, la touche Échap et l'arrière-plan inerte.
import { $$, reducedMotion } from './utils.js?v=0312c297';

const CLOSE_MS = 420;
const root = document.documentElement;

export function openSheet(id, { returnFocus } = {}) {
  const dialog = document.getElementById(id);
  if (!dialog || dialog.open) return dialog;
  dialog._returnFocus = returnFocus || document.activeElement;
  dialog.showModal();
  root.classList.add('is-locked');
  root.classList.remove('header-hidden');
  // Deux images d'attente pour que la transition d'entrée se joue.
  requestAnimationFrame(() => requestAnimationFrame(() => dialog.classList.add('is-open')));
  dialog.dispatchEvent(new CustomEvent('sheet:open'));
  return dialog;
}

export function closeSheet(target, { instant = false } = {}) {
  const dialog = typeof target === 'string' ? document.getElementById(target) : target;
  if (!dialog || !dialog.open || dialog._closing) return;
  dialog._closing = true;
  dialog.classList.remove('is-open');
  const finish = () => {
    dialog._closing = false;
    dialog.close();
    if (!document.querySelector('dialog[open]')) root.classList.remove('is-locked');
    const back = dialog._returnFocus;
    if (back && back.isConnected && !back.closest('dialog:not([open])')) back.focus({ preventScroll: true });
    dialog.dispatchEvent(new CustomEvent('sheet:close'));
  };
  if (instant || reducedMotion()) finish();
  else setTimeout(finish, CLOSE_MS);
}

export function initSheets() {
  let pressedOn = null;
  document.addEventListener('pointerdown', (event) => { pressedOn = event.target; });

  document.addEventListener('click', (event) => {
    const opener = event.target.closest('[data-open]');
    if (opener) {
      event.preventDefault();
      const current = opener.closest('dialog[open]');
      const id = opener.dataset.open;
      if (current && current.id !== id) {
        closeSheet(current);
        openSheet(id, { returnFocus: current._returnFocus });
      } else {
        openSheet(id);
      }
      return;
    }
    const closer = event.target.closest('[data-close]');
    if (closer) {
      closeSheet(closer.closest('dialog'));
      return;
    }
    // Lien vers une ancre de la page courante depuis un panneau : on ferme d'abord.
    const link = event.target.closest('dialog.sheet a[href*="#"]');
    if (link && link.pathname === location.pathname && link.hash) {
      closeSheet(link.closest('dialog'), { instant: true });
      return;
    }
    // Clic sur l'arrière-plan (la cible est alors le <dialog> lui-même).
    const dialog = event.target;
    if (dialog instanceof HTMLDialogElement && dialog.classList.contains('sheet') && pressedOn === dialog) closeSheet(dialog);
  });

  $$('dialog.sheet').forEach((dialog) => {
    dialog.addEventListener('cancel', (event) => {
      event.preventDefault();
      closeSheet(dialog);
    });
  });
}
