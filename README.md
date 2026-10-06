# Prince Shop — boutique en ligne

Site statique, mobile d'abord, en français. Le client parcourt le catalogue, remplit un panier,
et envoie sa commande **déjà rédigée** sur WhatsApp. Pas de compte, pas de serveur, pas de base de données.

```
Instagram / Google → accueil ou fiche produit → panier → 4 champs → vérification → WhatsApp
```

## Démarrer

Aucune dépendance : Python 3.9+ suffit.

```bash
python build.py --serve
```

Le site est généré dans `dist/` et servi sur http://localhost:4173.
Pour générer sans serveur : `python build.py`.

À chaque exécution, le script valide les données et liste ce qui reste **à compléter avant la mise en ligne**.

## Où modifier quoi

| Je veux…                                              | Fichier                 |
| ----------------------------------------------------- | ----------------------- |
| Ajouter / retirer un produit, changer un prix         | `data/products.json`    |
| Changer le numéro WhatsApp, le téléphone, l'adresse   | `data/config.json`      |
| Changer la livraison, le paiement, les horaires       | `data/config.json`      |
| Changer le texte du hero, la barre de réassurance     | `data/config.json`      |
| Changer la FAQ, les étapes de commande, les mentions  | `data/content.json`     |
| Ajouter des photos                                    | `assets/products/…`     |
| Changer le design                                     | `src/css/main.css`      |
| Changer une page                                      | `src/pages.py`          |
| Changer le message WhatsApp                           | `data/config.json` › `messages`, puis `src/js/whatsapp.js` |

Les deux numéros (WhatsApp et téléphone) ne sont écrits qu'à **un seul endroit** : `data/config.json` › `contact`.

## Ajouter un produit

Copier un bloc dans `data/products.json` et l'adapter :

```json
{
  "id": "mocassin-breloques",
  "ref": "PS-101",
  "name": "Mocassin à breloques",
  "category": "chaussures",
  "type": "mocassins",
  "price": 399,
  "compareAtPrice": null,
  "images": ["shoes/mocassin-1.jpg", "shoes/mocassin-2.jpg"],
  "colors": [
    { "name": "Camel", "hex": "#B58A5F", "images": ["shoes/mocassin-camel-1.jpg"] }
  ],
  "sizes": ["36", "37", "38", "39", "40"],
  "unavailableSizes": ["36"],
  "description": "Une phrase courte.",
  "details": ["Un détail par ligne"],
  "tags": ["mots", "pour", "la recherche"],
  "badge": "Nouveau",
  "featured": false,
  "available": true,
  "dateAdded": "2026-10-06",
  "instagramUrl": ""
}
```

- `id` devient l'adresse de la page : `/produit/mocassin-breloques/`.
- `price: null` → le site affiche « Prix sur demande » et le message WhatsApp dit « prix à confirmer ».
- `compareAtPrice` : uniquement pour une **vraie** promotion.
- `badge` : `"Nouveau"` ou `null`. Pas de « Best-seller » sans chiffres de vente.
- `available: false` → article grisé, impossible à commander.
- Les catégories, filtres (couleur, pointure, prix) et le menu se construisent seuls à partir du catalogue :
  une catégorie sans produit n'apparaît pas. « Accessoires » est déjà déclarée dans `config.json` et
  s'affichera dès qu'un produit l'utilisera.
- Le filtre par prix apparaît quand au moins 60 % des articles affichés ont un prix.

## Photos

Voir `assets/products/LISEZ-MOI.txt`. En bref : portrait **4:5** (1200 × 1500 px), JPG ou WebP, moins de 250 Ko.
Tant qu'un produit n'a pas de photo, le site montre un échantillon de sa couleur avec « Photo à venir ».

- Photos du hero : `config.json` › `hero.images` (chemins relatifs à `assets/`, ex. `"home/hero-1.jpg"`).
- Visuel d'une catégorie : ajouter `"image": "home/chaussures.jpg"` à la catégorie dans `config.json`.
- Vignettes Instagram : `config.json` › `instagram.posts[].image` (format 9:16).
- Aperçu des liens partagés (WhatsApp, Instagram) : déposer `assets/brand/og.png` (1200 × 630).
  Sans ce fichier, le script génère une image aux couleurs du catalogue.

## Mise en ligne

Le dossier `dist/` est un site statique complet : Netlify, Cloudflare Pages, Vercel, GitHub Pages ou un hébergement mutualisé.
Commande de build : `python build.py` · dossier publié : `dist`.

Avant de publier, régler `config.json` › `site.url` (nom de domaine réel) : il sert aux liens canoniques,
au sitemap et aux aperçus de liens. Si le site vit dans un sous-dossier, renseigner aussi `site.basePath` (ex. `"/boutique"`).

### Lien de démonstration (GitHub Pages)

Pour partager un aperçu avant le lancement :

```bash
python publish.py
```

Le script génère le site pour l'adresse `https://<compte>.github.io/<dépôt>/`, le pousse sur la branche
`gh-pages` du dépôt GitHub « origin » et affiche le lien. Cette version est marquée `noindex` : elle
n'apparaît pas dans Google. Relancer la commande après chaque modification pour mettre le lien à jour.

## À confirmer avec la boutique avant le lancement

Ces points viennent d'Instagram ou de Google Maps, pas de la boutique elle-même.

- [ ] **Prix** — un seul prix est public (basket running, 250 DH, reel du 7 sept. 2026). Tous les autres sont à renseigner.
- [ ] **Catalogue** — noms, couleurs et pointures du catalogue de départ sont à valider ou remplacer.
- [ ] **Photos** — aucune photo produit n'est incluse.
- [ ] **Paiement** — la bio Instagram dit « Payement avant ». Le site écrit « paiement à l'avance, modalités confirmées sur WhatsApp ». Préciser les moyens acceptés (`config.json` › `payment`, puis `confirmed: true`).
- [ ] **Livraison** — frais et délais inconnus : le site dit « à confirmer sur WhatsApp ». Renseigner `delivery.fee` pour afficher un tarif fixe.
- [ ] **Horaires** — « tous les jours, 10h – 22h30 » vient de Google Maps (fiche non revendiquée). Passer `store.hours.confirmed` à `true` une fois validé.
- [ ] **Adresse** — le site affiche l'adresse de la boutique (Av. Oran, Montfleuri 1). Google Maps indique « Rue d'Alep, Fès 30050 » pour le même point.
- [ ] **Numéro WhatsApp** — 06 62 52 01 30 d'après la bio. Vérifier que c'est bien le numéro qui reçoit les commandes.
- [ ] **Échanges, retours, conditions de vente, confidentialité** — textes à fournir dans `content.json` › `legal` (`confirmed: true` retire l'avertissement et rend la page indexable).
- [ ] **Nom de domaine** — `config.json` › `site.url`.

## Règles de contenu

- Aucun nom de marque tierce dans les noms ou descriptions de produits, et aucune mention « original », « authentique » ou « officiel ».
- Pas de matière, de garantie, de stock ni de délai qui ne soit confirmé par la boutique.
- Pas d'avis client inventé. La fiche Google Maps ne compte que 7 avis : le site renvoie vers Maps plutôt que de les citer.

## Structure

```
data/           config.json · products.json · content.json   ← tout le contenu
assets/         brand/ · products/{shoes,bags,accessories}/ · home/
src/pages.py    gabarits HTML
src/css/        main.css
src/js/         main · cart · cart-drawer · whatsapp · checkout · collection · product · picker · quick-add · search · dialogs · utils
build.py        validation + génération de dist/
dist/           site généré (ne pas modifier à la main)
```

## Pistes pour la suite

- Héberger les polices localement (elles viennent de Google Fonts aujourd'hui) pour gagner un aller-retour réseau.
- Générer des variantes d'images responsives au build une fois les photos fournies.
- Mesure d'audience respectueuse de la vie privée, et suivi des clics « Envoyer sur WhatsApp ».
- Version arabe / darija si la clientèle le demande.
