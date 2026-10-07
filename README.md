# Prince Shop — boutique en ligne

Site statique, mobile d'abord, en français. Le client parcourt le catalogue, remplit un panier,
et envoie sa commande **déjà rédigée** sur WhatsApp. Pas de compte, pas de serveur, pas de base de données.

```
Instagram / Google → accueil ou fiche produit → panier → 4 champs → vérification → WhatsApp
```

**Le site est aujourd'hui une boutique de démonstration** : 16 produits d'exemple, avec des photos libres de droits
et des prix d'exemple, pour montrer l'expérience finale. Chaque produit se remplace ensuite par un vrai, un par un.

## Démarrer

Aucune dépendance : Python 3.9+ suffit.

```bash
python build.py --serve
```

Le site est généré dans `dist/` et servi sur http://localhost:4173.
Pour générer sans serveur : `python build.py`.

À chaque exécution, le script valide les données et liste ce qui reste **à compléter avant la mise en ligne**.

## Mode démonstration

Un seul interrupteur, en haut de `data/config.json` :

```json
"DEMO_MODE": true
```

| `DEMO_MODE: true` (aujourd'hui)                                    | `DEMO_MODE: false` (site réel)                                   |
| ------------------------------------------------------------------ | ---------------------------------------------------------------- |
| Bandeau « Version de démonstration » sous la barre de livraison    | Plus aucune mention « démo »                                     |
| « Visuel démo » sur les photos et « Prix d'exemple » sur les fiches | Les produits encore marqués `"demo": true` **ne sont pas publiés** |
| Chaque message WhatsApp commence par « ⚠️ TEST … »                  | Messages normaux                                                 |
| Pas de prix dans les données envoyées à Google                     | Prix publiés dans les données structurées                        |

Le numéro WhatsApp du site est celui de la vraie boutique : l'avertissement « TEST » évite qu'un essai
soit pris pour une commande.

Passer à `false` ne publie jamais un faux produit : le script refuse de générer le site si tous les produits
sont encore des démos, et signale ceux qui restent à remplacer (ainsi que les photos de démonstration encore
utilisées pour le hero et les catégories).

## Remplacer un produit démo par un vrai

Tout se passe dans **`data/products.json`**, un bloc par produit :

1. `images` → vos photos (chemin dans `assets/products/`, ex. `"shoes/mocassin-1.jpg"`, ou adresse web).
2. `name`, `price` → le vrai nom, le vrai prix en dirhams.
3. `colors`, `sizes`, `description`, `details`, `available` → les vraies informations.
4. `"demo": false`.
5. `python build.py`.

Aucune mise en page à retoucher : cartes, filtres, recherche, fiche, panier et message WhatsApp suivent les données.

```json
{
  "id": "mocassin-signature",
  "ref": "PS-101",
  "demo": false,
  "name": "Mocassin Signature",
  "category": "chaussures",
  "type": "mocassins",
  "price": 349,
  "compareAtPrice": null,
  "images": ["shoes/mocassin-1.jpg", "shoes/mocassin-2.jpg"],
  "colors": [
    { "name": "Camel", "hex": "#B58A5F", "images": [] },
    { "name": "Bleu gris", "hex": "#7F8FA6", "images": ["shoes/mocassin-bleu-1.jpg"] }
  ],
  "sizes": ["36", "37", "38", "39", "40"],
  "unavailableSizes": ["36"],
  "description": "Une phrase courte.",
  "details": ["Un détail par ligne"],
  "tags": ["mots", "pour", "la recherche"],
  "badge": "Nouveau",
  "featured": true,
  "available": true,
  "dateAdded": "2026-10-06"
}
```

- `id` devient l'adresse de la page : `/produit/mocassin-signature/`.
- La 1re image est la photo principale, la 2e apparaît au survol de la carte.
- Une couleur avec ses propres `images` change la galerie quand on la choisit. Sans photo propre, la fiche précise « Photo présentée en … ».
- `price: null` → « Prix sur demande », et « prix à confirmer » dans le message WhatsApp.
- `compareAtPrice` : uniquement pour une **vraie** promotion.
- `badge` : `"Nouveau"` ou `null`. Pas de « Best-seller » sans chiffres de vente.
- `available: false` → article grisé, impossible à commander. `unavailableSizes` → pointures barrées.
- Un sélecteur n'apparaît que s'il sert : pas de pointure pour un sac, pas de couleur s'il n'y en a qu'une.
- Catégories, menu, filtres (couleur, pointure, prix) et recherche se construisent seuls à partir du catalogue :
  une catégorie sans produit n'apparaît pas.

## Où modifier quoi

| Je veux…                                                | Fichier                                  |
| ------------------------------------------------------- | ---------------------------------------- |
| Ajouter / retirer un produit, changer un prix           | `data/products.json`                     |
| Activer / couper le mode démonstration                  | `data/config.json` › `DEMO_MODE`         |
| Changer le numéro WhatsApp ou le téléphone              | `data/config.json` › `contact` (`WHATSAPP_NUMBER`, `PHONE_NUMBER`) |
| Changer l'adresse, les horaires, le lien Google Maps    | `data/config.json` › `store`             |
| Changer la livraison ou le paiement                     | `data/config.json` › `delivery`, `payment` |
| Changer le hero, les photos de catégories, la sélection | `data/config.json` › `hero`, `categories`, `home`, `spotlight` |
| Changer la FAQ, les étapes de commande, les mentions    | `data/content.json`                      |
| Changer le message WhatsApp                             | `data/config.json` › `messages`, puis `src/js/whatsapp.js` |
| Changer le design                                       | `src/css/main.css`                       |
| Changer une page                                        | `src/pages.py`                           |

Les deux numéros ne sont écrits qu'à **un seul endroit** : `data/config.json` › `contact`.

## Photos

Voir `assets/products/LISEZ-MOI.txt`. En bref : portrait **4:5** (1200 × 1500 px), JPG ou WebP, moins de 250 Ko,
fond simple, produit au centre.

- Hero : `config.json` › `hero.images` (deux images : la grande, puis la petite) et `hero.links` (produits liés).
- Catégories : `config.json` › `categories[].image`.
- Mosaïque Instagram : `config.json` › `instagram.posts[].image` (vignettes de reels) ; sinon elle reprend des visuels du catalogue.
- Aperçu des liens partagés : déposer `assets/brand/og.png` (1200 × 630). Sans ce fichier, le script génère une image aux couleurs du catalogue.
- Un produit sans photo affiche un échantillon de sa couleur avec « Photo à venir ».

### Photos de la démonstration

Les visuels actuels viennent d'[Unsplash](https://unsplash.com/license) (licence libre, usage commercial autorisé) et sont
chargés depuis leur serveur d'images, recadrés au bon format. Ils ne montrent **pas** les articles de la boutique.
Photographes : Nelibar Shoes, Mattia Occhi, Melvin Peter, Jia Ye, Mojtaba Fahiminia, Adrian Regeci, Alexander Mass,
Massimo P, Pablo Figueroa, GLOBALDSIO IT SOLUTION, Maryam Nemati, Mobina Ghazazani, Remi Eris, Zulfugar Karimov,
Habib Dadkhah, Anton Be, Ranurte, Davide Zacchello, Latico Leathers, Colin Lloyd.

## Mise en ligne

Le dossier `dist/` est un site statique complet : Netlify, Cloudflare Pages, Vercel, GitHub Pages ou un hébergement mutualisé.
Commande de build : `python build.py` · dossier publié : `dist`.

Avant de publier, régler `config.json` › `site.url` (nom de domaine réel) : il sert aux liens canoniques,
au sitemap et aux aperçus de liens. Si le site vit dans un sous-dossier, renseigner aussi `site.basePath` (ex. `"/boutique"`).

### Lien de démonstration (GitHub Pages)

```bash
python publish.py
```

Le script génère le site pour l'adresse `https://<compte>.github.io/<dépôt>/`, le pousse sur la branche
`gh-pages` du dépôt GitHub « origin » et affiche le lien. Cette version est marquée `noindex` : elle
n'apparaît pas dans Google. Relancer la commande après chaque modification pour mettre le lien à jour.

## À confirmer avec la boutique avant le lancement

Ces points viennent d'Instagram ou de Google Maps, pas de la boutique elle-même.

- [ ] **Catalogue réel** — remplacer les 16 produits de démonstration (photos, noms, prix, couleurs, pointures).
- [ ] **Numéro WhatsApp** — 06 62 52 01 30 d'après la bio Instagram. Vérifier que c'est bien celui qui reçoit les commandes.
- [ ] **Paiement** — le site dit « les modalités de paiement sont confirmées lors de la commande ». La bio Instagram indique « Payement avant » : préciser les moyens acceptés (`config.json` › `payment`).
- [ ] **Livraison** — frais et délais inconnus : le site dit « à confirmer sur WhatsApp ». Renseigner `delivery.fee` pour afficher un tarif fixe.
- [ ] **Adresse** — le site affiche l'adresse donnée par la boutique (Av. Oran, Montfleuri 1, Zohour). La fiche Google Maps liée depuis sa bio situe le même point « Rue d'Alep, Fès 30050 ». Les deux sont gardées séparément dans `config.json` › `store` ; l'itinéraire utilise le lien Google Maps.
- [ ] **Horaires** — « tous les jours, 10h – 22h30 » vient de Google Maps (fiche non revendiquée) et est signalé comme tel. Passer `store.hours.confirmed` à `true` une fois validé.
- [ ] **Échanges, retours, conditions de vente, confidentialité** — textes à fournir dans `content.json` › `legal`.
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
src/js/         main · cart · cart-drawer · card-add · quick-add · picker · product · collection · search · checkout · whatsapp · dialogs · utils
build.py        validation + génération de dist/
publish.py      lien de démonstration GitHub Pages
dist/           site généré (ne pas modifier à la main)
```

## Pistes pour la suite

- Héberger les polices localement (elles viennent de Google Fonts aujourd'hui).
- Générer des variantes d'images responsives au build pour les photos locales de la boutique.
- Mesure d'audience respectueuse de la vie privée, et suivi des clics « Envoyer sur WhatsApp ».
- Version arabe / darija si la clientèle le demande.
