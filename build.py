#!/usr/bin/env python3
"""Génère le site Prince Shop dans dist/ à partir de data/*.json.

    python build.py            # construit le site
    python build.py --serve    # construit puis sert dist/ sur http://localhost:4173

Options (utilisées par publish.py pour la mise en ligne de démonstration) :
    --out=dossier     dossier de sortie (dist par défaut)
    --url=https://…   remplace site.url
    --base=/chemin    remplace site.basePath
    --noindex         demande aux moteurs de recherche de ne pas indexer le site

Aucune dépendance : Python 3.9+ suffit.
"""
import hashlib
import json
import re
import shutil
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA, SRC, ASSETS, DIST = ROOT / "data", ROOT / "src", ROOT / "assets", ROOT / "dist"
sys.path.insert(0, str(SRC))
import pages  # noqa: E402

warnings, errors = [], []


def arg(name, default=None):
    """Valeur d'une option --nom=valeur passée en ligne de commande."""
    for item in sys.argv[1:]:
        if item.startswith(f"--{name}="):
            return item.split("=", 1)[1]
    return default


def read_json(name):
    try:
        return json.loads((DATA / name).read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        sys.exit(f"\n✗ data/{name} n'est pas un JSON valide — ligne {err.lineno}, colonne {err.colno} : {err.msg}\n")


def write(rel, text):
    out = DIST / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8", newline="\n")


# --------------------------------------------------------------------------
# Validation du catalogue
# --------------------------------------------------------------------------
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate(config, products):
    cats = {c["id"]: {t["id"] for t in c.get("types", [])} for c in config["categories"]}
    seen_ids, seen_refs = set(), set()
    no_photo, no_price = [], []
    for i, p in enumerate(products, 1):
        where = f'produit n°{i} « {p.get("name", "?")} »'
        for key in ("id", "ref", "name", "category"):
            if not p.get(key):
                errors.append(f"{where} : champ « {key} » manquant.")
        pid = p.get("id", "")
        if pid and not SLUG.match(pid):
            errors.append(f'{where} : id « {pid} » invalide (minuscules, chiffres et tirets uniquement).')
        if pid in seen_ids:
            errors.append(f'{where} : id « {pid} » déjà utilisé par un autre produit.')
        seen_ids.add(pid)
        if p.get("ref") in seen_refs:
            errors.append(f'{where} : référence « {p.get("ref")} » en double.')
        seen_refs.add(p.get("ref"))
        if p.get("category") not in cats:
            errors.append(f'{where} : catégorie « {p.get("category")} » absente de config.json.')
        elif p.get("type") and p["type"] not in cats[p["category"]]:
            errors.append(f'{where} : type « {p["type"]} » absent de la catégorie « {p["category"]} » dans config.json.')
        price, old = p.get("price"), p.get("compareAtPrice")
        if price is not None and (not isinstance(price, (int, float)) or price <= 0):
            errors.append(f"{where} : price doit être un nombre positif ou null.")
        if old is not None and (price is None or old <= price):
            warnings.append(f"{where} : compareAtPrice ignoré (il doit être supérieur à price).")
            p["compareAtPrice"] = None
        for c in p.get("colors", []):
            if not HEX.match(c.get("hex", "")):
                errors.append(f'{where} : couleur « {c.get("name")} » — code hex invalide « {c.get("hex")} ».')
        refs = list(p.get("images", [])) + [img for c in p.get("colors", []) for img in c.get("images", [])]
        for image in refs:
            src = pages.as_image(image).get("src", "")
            if not src:
                errors.append(f"{where} : une image n'a pas d'adresse (champ « src »).")
            elif not pages.is_remote(src) and not (ASSETS / "products" / src).is_file():
                errors.append(f"{where} : photo introuvable — assets/products/{src}")
        if not refs:
            no_photo.append(p.get("ref", "?"))
        if price is None:
            no_price.append(p.get("ref", "?"))
        p.setdefault("available", True)
        p.setdefault("tags", [])
        p.setdefault("sizes", [])
        p.setdefault("colors", [])
        p.setdefault("images", [])
        p["sizes"] = [str(s) for s in p["sizes"]]
        p["unavailableSizes"] = [str(s) for s in p.get("unavailableSizes", [])]

    demo_left = [p.get("ref", "?") for p in products if p.get("demo")]
    if config.get("DEMO_MODE") and demo_left:
        warnings.append(f"DEMO_MODE actif : {len(demo_left)} produit(s) de démonstration à remplacer ({', '.join(demo_left)}).")
    if not config.get("DEMO_MODE"):
        stock = [where for where, src in (
            [("hero.images", pages.as_image(i)["src"]) for i in config["hero"].get("images", [])]
            + [(f'categories › {c["label"]} › image', pages.as_image(c["image"])["src"]) for c in config["categories"] if c.get("image")]
        ) if src.startswith(pages.UNSPLASH)]
        if stock:
            warnings.append("DEMO_MODE désactivé mais config.json utilise encore des photos de démonstration : " + ", ".join(stock) + ".")
    if no_photo:
        warnings.append(f"{len(no_photo)} produit(s) sans photo, visuel d'attente affiché : {', '.join(no_photo)}")
    if no_price:
        warnings.append(f"{len(no_price)} produit(s) sans prix, « Prix sur demande » affiché : {', '.join(no_price)}")
    if "example" in config["site"]["url"]:
        warnings.append("config.json › site.url : remplacer par le vrai nom de domaine (liens canoniques, sitemap, aperçus WhatsApp).")
    if not config["store"]["hours"].get("confirmed"):
        warnings.append("config.json › store.hours : horaires repris de Google Maps, à confirmer.")
    if not config["payment"].get("confirmed"):
        warnings.append("config.json › payment : modalités de paiement à confirmer (la bio Instagram indique « Payement avant »).")


# --------------------------------------------------------------------------
# Données envoyées au navigateur (panier, recherche, filtres, WhatsApp)
# --------------------------------------------------------------------------
def client_data(S):
    c = S.c
    config = {
        "base": S.base,
        "currency": c["site"]["currency"],
        "priceOnRequest": c["site"]["priceOnRequest"],
        "whatsapp": S.whatsapp,
        "demo": S.demo,
        "demoOrderNotice": c["demo"]["orderNotice"] if S.demo else "",
        "demoImageLabel": c["demo"]["imageLabel"] if S.demo else "",
        "whatsappDisplay": c["contact"]["whatsappDisplay"],
        "messages": c["messages"],
        "deliveryLabel": c["delivery"]["feeLabel"],
        "deliveryFee": c["delivery"]["fee"],
        "priceRanges": c["filters"]["priceRanges"],
        "priceFilterMinShare": c["filters"]["priceFilterMinShare"],
        "categories": [{"id": x["id"], "label": x["label"], "sizeLabel": x.get("sizeLabel", "Taille"),
                        "types": [{"id": t["id"], "label": t["label"]} for t in x["types"]]} for x in S.cats],
    }
    products = []
    for p in S.products:
        t = S.type_of(p)
        colors = []
        for col in p["colors"]:
            colors.append({"name": col["name"], "hex": col["hex"], "tone": pages.tone(col["hex"]),
                           "slug": pages.slug(col["name"]), "images": [S.sources(i) for i in col.get("images", [])]})
        products.append({
            "id": p["id"], "ref": p["ref"], "name": p["name"], "url": S.product_url(p),
            "category": p["category"], "type": p.get("type", ""), "typeLabel": t["label"], "word": t["word"],
            "price": p.get("price"), "compareAtPrice": p.get("compareAtPrice"),
            "images": [S.sources(i) for i in S.images_for(p)], "demo": S.is_demo(p),
            "photoColor": next((col["name"] for col in p["colors"] if col.get("images")), p["colors"][0]["name"] if p["colors"] else "")
            if not p["images"] else (p["colors"][0]["name"] if p["colors"] else ""),
            "colors": colors, "sizes": p["sizes"], "unavailableSizes": p["unavailableSizes"],
            "tags": p["tags"], "badge": p.get("badge"), "available": p["available"], "date": p.get("dateAdded", ""),
        })
    dump = lambda x: json.dumps(x, ensure_ascii=False, separators=(",", ":"))  # noqa: E731
    return ("// Fichier généré par build.py — ne pas modifier. Source : data/config.json et data/products.json\n"
            f"export const CONFIG = {dump(config)};\nexport const PRODUCTS = {dump(products)};\n")


# --------------------------------------------------------------------------
# Image d'aperçu (liens partagés sur WhatsApp / Instagram) : bandes de couleurs du catalogue
# --------------------------------------------------------------------------
def write_og_png(path, colors, width=1200, height=630):
    rgb = [tuple(int(c.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)) for c in colors] or [(21, 19, 16)]
    stripe = width / len(rgb)
    row = bytearray([0])
    for x in range(width):
        row += bytes(rgb[min(int(x / stripe), len(rgb) - 1)])
    raw = bytes(row) * height

    def chunk(tag, data):
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


# --------------------------------------------------------------------------
# Construction
# --------------------------------------------------------------------------
def minify_css(css):
    """Allège la feuille de style (commentaires, retours à la ligne) sans outil externe."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r" ?([{};]) ?", r"\1", css)
    return css.replace(";}", "}").strip()


def version_hash():
    h = hashlib.sha1(Path(__file__).read_bytes())
    for folder in (DATA, SRC):
        for f in sorted(folder.rglob("*")):
            if f.is_file() and "__pycache__" not in f.parts:
                h.update(f.read_bytes())
    return h.hexdigest()[:8]


def build():
    config, content = read_json("config.json"), read_json("content.json")
    products = read_json("products.json")["products"]
    if arg("url"):
        config["site"]["url"] = arg("url")
    if arg("base") is not None:
        config["site"]["basePath"] = arg("base")
    config["site"]["noindex"] = "--noindex" in sys.argv
    if not config.get("DEMO_MODE"):
        hidden = [p for p in products if p.get("demo")]
        products = [p for p in products if not p.get("demo")]
        if hidden:
            warnings.append(f"DEMO_MODE désactivé : {len(hidden)} produit(s) encore marqués « demo » ne sont pas publiés "
                            f"({', '.join(p.get('ref', '?') for p in hidden)}). Passer « demo » à false une fois le produit réel.")
        if not products:
            errors.append("DEMO_MODE est désactivé mais tous les produits sont encore marqués « demo ». "
                          "Remplacez au moins un produit (\"demo\": false) ou repassez DEMO_MODE à true.")
    validate(config, products)
    if errors:
        print("\n✗ Le site n'a pas été généré. À corriger dans data/ :\n")
        for msg in errors:
            print("  •", msg)
        sys.exit(1)

    version = version_hash()
    S = pages.Site(config, products, content, version)

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()

    # Fichiers statiques
    shutil.copytree(ASSETS, DIST / "assets", ignore=shutil.ignore_patterns(".gitkeep", "LISEZ-MOI.txt"))
    write("assets/css/main.css", minify_css((SRC / "css" / "main.css").read_text(encoding="utf-8")))
    stamp = lambda m: f'{m.group(1)}{m.group(2)}?v={version}{m.group(3)}'  # noqa: E731
    for js in (SRC / "js").glob("*.js"):
        code = js.read_text(encoding="utf-8")
        code = re.sub(r"""(from\s+['"])(\./[\w.-]+\.js)(['"])""", stamp, code)
        code = re.sub(r"""(import\(\s*['"])(\./[\w.-]+\.js)(['"]\s*\))""", stamp, code)
        write(f"assets/js/{js.name}", code)
    write("assets/js/site-data.js", client_data(S))
    if not (ASSETS / "brand" / "og.png").is_file():
        palette = (S.by_id.get((config.get("spotlight") or {}).get("productId", "")) or products[0])["colors"]
        write_og_png(DIST / "assets" / "brand" / "og.png", [c["hex"] for c in palette])

    # Pages
    n_pages = 0
    sitemap = []

    def page(rel, html, index=True):
        nonlocal n_pages
        write(rel, html)
        n_pages += 1
        if index:
            sitemap.append("/" + rel.replace("index.html", ""))

    page("index.html", pages.page_home(S))

    home = ("Accueil", S.url("/"))
    page("collection/index.html", pages.page_collection(
        S, scope={}, path="/collection/", heading="Toute la collection",
        title="Toute la collection — Chaussures & Sacs | Prince Shop Fès",
        intro="Chaussures et sacs disponibles en boutique à Fès, livrés partout au Maroc.",
        items=S.by_date(), trail=[home, ("Collection", None)]))
    if S.new_products:
        page("collection/nouveautes/index.html", pages.page_collection(
            S, scope={"new": True}, path="/collection/nouveautes/", heading="Nouveautés",
            title="Nouveautés | Prince Shop Fès", intro="Les derniers arrivages de la boutique.",
            items=S.new_products, trail=[home, ("Nouveautés", None)]))
    for cat in S.cats:
        items = [p for p in S.by_date() if p["category"] == cat["id"]]
        page(f'collection/{cat["id"]}/index.html', pages.page_collection(
            S, scope={"category": cat["id"]}, path=f'/collection/{cat["id"]}/', heading=cat["label"],
            title=f'{cat["label"]} — {", ".join(t["label"] for t in cat["types"]) or cat["label"]} | Prince Shop Fès',
            intro=cat.get("intro", ""), items=items, trail=[home, (cat["label"], None)]))
    for p in products:
        page(f'produit/{p["id"]}/index.html', pages.page_product(S, p))
    page("commande/index.html", pages.page_checkout(S), index=False)
    legal_ready = all(s.get("confirmed") for s in content["legal"])
    page("informations/index.html", pages.page_legal(S), index=legal_ready)
    page("404.html", pages.page_404(S), index=False)

    urls = "".join(f"<url><loc>{S.origin}{S.base}{u}</loc></url>" for u in sitemap)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    if config["site"]["noindex"]:
        write("robots.txt", "User-agent: *\nDisallow: /\n")
    else:
        write("robots.txt", f"User-agent: *\nAllow: /\nDisallow: {S.base}/commande/\n\nSitemap: {S.origin}{S.base}/sitemap.xml\n")
    write(".nojekyll", "")  # GitHub Pages : servir les fichiers tels quels

    for sec in content["legal"]:
        if not sec.get("confirmed"):
            warnings.append(f'content.json › page « {sec["title"]} » : texte à confirmer par la boutique.')

    print(f"\n✓ Site généré : {n_pages} pages, {len(products)} produits → {DIST.name}/   (version {version})")
    if warnings:
        print(f"\n  À compléter avant la mise en ligne ({len(warnings)}) :")
        for msg in warnings:
            print("   ·", msg)
    print()


def serve(port=4173):
    import functools
    import http.server

    class Handler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def send_error(self, code, message=None, explain=None):
            if code == 404 and (DIST / "404.html").is_file():
                body = (DIST / "404.html").read_bytes()
                self.send_response(404)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            super().send_error(code, message, explain)

        def log_message(self, *args):
            pass

    handler = functools.partial(Handler, directory=str(DIST))
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        print(f"  Aperçu : http://localhost:{port}   (Ctrl+C pour arrêter)\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if arg("out"):
        DIST = ROOT / arg("out")
    build()
    if "--serve" in sys.argv:
        port = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--port=")), 4173)
        serve(port)
