"""Gabarits HTML du site Prince Shop.

Tout le balisage vit ici ; les données viennent de data/*.json (voir build.py).
Chaque fonction `page_*` renvoie le HTML complet d'une page.
"""
import json
import re
from datetime import date
from html import escape as _escape
from urllib.parse import quote


def e(value):
    return _escape(str(value), quote=True)


TAG = re.compile(r"(<[^>]+>)")
NNBSP, NBSP, APOSTROPHE = " ", " ", "’"


def french_spaces(html):
    """Typographie française, appliquée au texte visible uniquement (jamais aux attributs) :
    espaces insécables avant « ? », « ! », « : » et dans les guillemets, apostrophes courbes."""
    parts = TAG.split(html)
    for i in range(0, len(parts), 2):  # indices pairs = texte, impairs = balises
        text = parts[i]
        if not text.strip():
            continue
        text = text.replace(" ?", NNBSP + "?").replace(" !", NNBSP + "!").replace(" :", NBSP + ":")
        text = text.replace("« ", "«" + NBSP).replace(" »", NBSP + "»")
        parts[i] = re.sub(r"(?<=\w)(?:'|&#x27;)(?=\w)", APOSTROPHE, text)
    return "".join(parts)


def digits(number):
    """« +212 662 520 130 » → « 212662520130 » (format attendu par wa.me et tel:)."""
    return re.sub(r"\D", "", str(number))


# --------------------------------------------------------------------------
# Icônes (symboles SVG, tracé fin). Utilisées côté gabarits et côté JS via <use>.
# --------------------------------------------------------------------------
STROKE = 'fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"'
ICONS = {
    "menu": f'<path {STROKE} d="M3 8.5h18M3 15.5h18"/>',
    "close": f'<path {STROKE} d="M5.5 5.5l13 13M18.5 5.5l-13 13"/>',
    "search": f'<circle {STROKE} cx="11" cy="11" r="6.25"/><path {STROKE} d="M15.75 15.75L20.5 20.5"/>',
    "bag": f'<path {STROKE} d="M5 8.25h14l-.9 12.25H5.9L5 8.25z"/><path {STROKE} d="M9 8.25V6.9a3 3 0 0 1 6 0v1.35"/>',
    "home": f'<path {STROKE} d="M4 10.75L12 4l8 6.75V20h-5.25v-5.5h-5.5V20H4v-9.25z"/>',
    "grid": f'<path {STROKE} d="M4.5 4.5h6v6h-6zM13.5 4.5h6v6h-6zM4.5 13.5h6v6h-6zM13.5 13.5h6v6h-6z"/>',
    "plus": f'<path {STROKE} d="M12 5.5v13M5.5 12h13"/>',
    "minus": f'<path {STROKE} d="M5.5 12h13"/>',
    "arrow": f'<path {STROKE} d="M4 12h15.5M14 6.5l5.5 5.5-5.5 5.5"/>',
    "arrow-out": f'<path {STROKE} d="M7.5 16.5l9-9M9 7.5h7.5V15"/>',
    "chevron": f'<path {STROKE} d="M6.5 9.5l5.5 5.5 5.5-5.5"/>',
    "check": f'<path {STROKE} d="M5 12.5l4.5 4.5L19 7.5"/>',
    "expand": f'<path {STROKE} d="M4.5 9.5v-5h5M19.5 14.5v5h-5M4.5 4.5l6 6M19.5 19.5l-6-6"/>',
    "pin": f'<path {STROKE} d="M12 21s6.5-5.7 6.5-11a6.5 6.5 0 1 0-13 0c0 5.3 6.5 11 6.5 11z"/><circle {STROKE} cx="12" cy="10" r="2.3"/>',
    "phone": f'<path {STROKE} d="M6.6 3.75h2.9l1.4 3.9-1.9 1.4a10.6 10.6 0 0 0 5.9 5.9l1.4-1.9 3.9 1.4v2.9a1.9 1.9 0 0 1-1.9 1.9A15.6 15.6 0 0 1 4.7 5.65a1.9 1.9 0 0 1 1.9-1.9z"/>',
    "truck": f'<path {STROKE} d="M2.75 6.75h10.5v9.5H2.75zM13.25 10h3.9l3.1 3.1v3.15h-7"/><circle {STROKE} cx="7" cy="17.75" r="1.75"/><circle {STROKE} cx="16.75" cy="17.75" r="1.75"/>',
    "filter": f'<path {STROKE} d="M4 7.5h16M7 12h10M10 16.5h4"/>',
    "play": '<path fill="currentColor" d="M8.5 6v12l10-6z"/>',
    "instagram": f'<rect {STROKE} x="3.75" y="3.75" width="16.5" height="16.5" rx="4.5"/><circle {STROKE} cx="12" cy="12" r="3.9"/><circle fill="currentColor" cx="17" cy="7" r="1"/>',
    "whatsapp": '<path fill="currentColor" d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>',
}


def sprite():
    symbols = "".join(f'<symbol id="i-{name}" viewBox="0 0 24 24">{body}</symbol>' for name, body in ICONS.items())
    return f'<svg width="0" height="0" style="position:absolute" aria-hidden="true">{symbols}</svg>'


def icon(name, cls=""):
    return f'<svg class="icon{" " + cls if cls else ""}" width="24" height="24" aria-hidden="true" focusable="false"><use href="#i-{name}"/></svg>'


# --------------------------------------------------------------------------
# Couleurs
# --------------------------------------------------------------------------
def luminance(hex_color):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

    def lin(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def tone(hex_color):
    """'dark' = couleur foncée (texte clair par-dessus), 'light' = couleur claire."""
    return "dark" if luminance(hex_color) < 0.4 else "light"


def slug(text):
    table = str.maketrans("àâäéèêëîïôöùûüçÀÂÄÉÈÊËÎÏÔÖÙÛÜÇ", "aaaeeeeiioouuucAAAEEEEIIOOUUUC")
    out = "".join(ch if ch.isalnum() else "-" for ch in text.translate(table).lower())
    return "-".join(part for part in out.split("-") if part)


# --------------------------------------------------------------------------
# Images : fichiers locaux (assets/…) ou adresses web. Les photos Unsplash de la démo
# sont servies par leur CDN, recadrées et redimensionnées à la volée (AVIF/WebP).
# --------------------------------------------------------------------------
UNSPLASH = "https://images.unsplash.com/"
WIDTHS = (320, 480, 640, 800, 1200)


def as_image(image):
    return {"src": image} if isinstance(image, str) else image


def is_remote(src):
    return src.startswith(("http://", "https://"))


# --------------------------------------------------------------------------
# Site : accès aux données + petites aides partagées par les gabarits
# --------------------------------------------------------------------------
class Site:
    def __init__(self, config, products, content, version):
        self.c = config
        self.products = products
        self.content = content
        self.v = version
        self.demo = bool(config.get("DEMO_MODE"))
        self.base = config["site"]["basePath"].rstrip("/")
        self.origin = config["site"]["url"].rstrip("/")
        self.whatsapp = digits(config["contact"]["WHATSAPP_NUMBER"])
        self.phone = digits(config["contact"]["PHONE_NUMBER"])
        self.by_id = {p["id"]: p for p in products}
        self.cat_by_id = {c["id"]: c for c in config["categories"]}
        # Catégories réellement présentes dans le catalogue (jamais de catégorie vide).
        self.cats = []
        for c in config["categories"]:
            items = [p for p in products if p["category"] == c["id"]]
            if not items:
                continue
            types = []
            for t in c.get("types", []):
                n = sum(1 for p in items if p.get("type") == t["id"])
                if n:
                    types.append({**t, "count": n})
            self.cats.append({**c, "count": len(items), "types": types})
        self.new_products = [p for p in self.by_date() if p.get("badge") == "Nouveau"]

    # -- URLs
    def url(self, path):
        return self.base + path

    def abs(self, path):
        return self.origin + self.base + path

    def asset(self, path):
        return f"{self.base}/assets/{path}?v={self.v}"

    def product_url(self, p):
        return self.url(f"/produit/{p['id']}/")

    def cat_url(self, cat_id, type_id=None):
        u = self.url(f"/collection/{cat_id}/")
        return f"{u}?type={type_id}" if type_id else u

    def wa(self, text=None):
        if text is None:
            text = f'{self.c["messages"]["greeting"]}\n\n{self.c["messages"]["help"]}'
        if self.demo:  # la boutique doit savoir qu'un message vient de la version de démonstration
            text = f'{self.c["demo"]["orderNotice"]}\n\n{text}'
        return f"https://wa.me/{self.whatsapp}?text={quote(text)}"

    def sources(self, image, ratio=(4, 5), folder="products"):
        """Adresses d'une image : {src, srcset, thumb, full}. ratio=None garde les proportions d'origine."""
        image = as_image(image)
        src = image["src"]
        if src.startswith(UNSPLASH):
            base = src.split("?")[0]
            focus = ""
            if "zoom" in image or "x" in image or "y" in image:
                focus = f'&crop=focalpoint&fp-x={image.get("x", 0.5)}&fp-y={image.get("y", 0.5)}&fp-z={image.get("zoom", 1)}'

            def at(width, quality=72):
                size = f"&w={width}&h={round(width * ratio[1] / ratio[0])}&fit=crop" if ratio else f"&w={width}&fit=max"
                return f"{base}?auto=format&q={quality}{size}{focus}"

            return {"src": at(800), "srcset": ", ".join(f"{at(w)} {w}w" for w in WIDTHS), "thumb": at(160, 60), "full": at(1600, 80)}
        url = src if is_remote(src) else f'{self.base}/assets/{folder + "/" if folder else ""}{quote(src)}'
        return {"src": url, "srcset": "", "thumb": url, "full": url}

    def img(self, image, alt="", sizes="100vw", eager=False, ratio=(4, 5), folder="products", cls=""):
        s = self.sources(image, ratio, folder)
        w, h = (1200, round(1200 * ratio[1] / ratio[0])) if ratio else (1200, 1500)
        srcset = f' srcset="{e(s["srcset"])}" sizes="{e(sizes)}"' if s["srcset"] else ""
        load = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
        klass = f' class="{cls}"' if cls else ""
        return f'<img{klass} src="{e(s["src"])}"{srcset} alt="{e(alt)}" width="{w}" height="{h}" {load} decoding="async">'

    # -- Données
    def by_date(self):
        return sorted(self.products, key=lambda p: p.get("dateAdded", ""), reverse=True)

    def type_of(self, p):
        cat = self.cat_by_id[p["category"]]
        for t in cat.get("types", []):
            if t["id"] == p.get("type"):
                return t
        return {"id": "", "label": cat["label"], "word": cat.get("singular", cat["label"])}

    def images_for(self, p, color=None):
        if color and color.get("images"):
            return color["images"]
        if p.get("images"):
            return p["images"]
        for c in p.get("colors", []):
            if c.get("images"):
                return c["images"]
        return []

    def is_demo(self, p):
        return self.demo and p.get("demo", False)

    def price_html(self, p, cls="price"):
        if p.get("price") is None:
            return f'<span class="{cls} {cls}--ask">{e(self.c["site"]["priceOnRequest"])}</span>'
        cur = e(self.c["site"]["currency"])
        now = f'{fmt_price(p["price"])} {cur}'
        old = p.get("compareAtPrice")
        if old and old > p["price"]:
            return (f'<span class="{cls}"><span class="sr-only">Prix actuel :</span> {now} '
                    f'<s><span class="sr-only">Ancien prix :</span> {fmt_price(old)} {cur}</s></span>')
        return f'<span class="{cls}">{now}</span>'

    def fill(self, text):
        s, k = self.c["store"], self.c["contact"]
        return (text.replace("{whatsapp}", k["whatsappDisplay"]).replace("{phone}", k["phoneDisplay"])
                .replace("{address}", f'{s["addressLine1"]}, {s["addressLine2"]}')
                .replace("{hours}", s["hours"]["label"]).replace("{instagram}", "@" + k["instagramHandle"])
                .replace("{maps}", s["mapsUrl"]))


def fmt_price(n):
    n = float(n)
    text = f"{n:,.2f}" if n != int(n) else f"{int(n):,}"
    return text.replace(",", NNBSP).replace(".", ",")


def json_ld(data):
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace("</", "<\\/") + "</script>"


# --------------------------------------------------------------------------
# Composants
# --------------------------------------------------------------------------
def placeholder(word, hex_color, label, caption=None):
    """Visuel d'attente quand un produit n'a pas encore de photo : un échantillon de sa couleur."""
    cap = f"<em>{e(caption or word)}</em>"
    return (f'<div class="ph ph--{tone(hex_color)}" style="--c:{e(hex_color)}" role="img" aria-label="{e(label)} — photo à venir">'
            f'<span class="ph__chip"></span><span class="ph__cap">{cap}<small>Photo à venir</small></span></div>')


CARD_SIZES = "(min-width:1100px) 25vw, (min-width:768px) 33vw, 50vw"


def media(S, p, color=None, index=0, eager=False, sizes=CARD_SIZES, ratio=(4, 5)):
    color = color or (p["colors"][0] if p.get("colors") else None)
    images = S.images_for(p, color)
    label = p["name"] + (f' — {color["name"]}' if color else "")
    if images and index < len(images):
        return S.img(images[index], alt=label, sizes=sizes, eager=eager, ratio=ratio)
    t = S.type_of(p)
    hex_color = color["hex"] if color else "#CFC8BB"
    return placeholder(t["word"], hex_color, label, caption=color["name"] if color else t["word"])


def color_dots(p, limit=5):
    colors = p.get("colors", [])
    if len(colors) < 2:
        return ""
    dots = "".join(f'<li class="dot dot--{tone(c["hex"])}" style="--c:{e(c["hex"])}"></li>' for c in colors[:limit])
    more = f'<li class="dots__more">+{len(colors) - limit}</li>' if len(colors) > limit else ""
    return f'<ul class="dots" aria-label="{len(colors)} couleurs">{dots}{more}</ul>'


def card(S, p, eager=False, cls="", sizes=CARD_SIZES):
    href = S.product_url(p)
    t = S.type_of(p)
    images = S.images_for(p)
    available = p.get("available", True)
    second = S.img(images[1], sizes=sizes, cls="card__alt") if len(images) > 1 else ""
    badge = ""
    if not available:
        badge = '<span class="card__badge card__badge--off">Indisponible</span>'
    elif p.get("badge"):
        badge = f'<span class="card__badge">{e(p["badge"])}</span>'
    add = ""
    if available:
        add = (f'<div class="card__add" data-add="{e(p["id"])}"><button class="add__btn" type="button" data-add-btn '
               f'aria-label="Ajouter au panier : {e(p["name"])}">{icon("plus")}</button></div>')
    classes = "card" + ("" if available else " card--off") + (f" {cls}" if cls else "")
    return f'''<article class="{classes}" data-id="{e(p["id"])}">
  <div class="card__frame">
    <a class="card__media" href="{href}" tabindex="-1" aria-hidden="true">{media(S, p, eager=eager, sizes=sizes)}{second}</a>
    {badge}{add}
  </div>
  <div class="card__body">
    <p class="card__cat">{e(t["label"])}</p>
    <h3 class="card__name"><a href="{href}">{e(p["name"])}</a></h3>
    <p class="card__price">{S.price_html(p)}</p>
    {color_dots(p)}
  </div>
</article>'''


def crumbs(S, trail):
    """trail = [(label, url ou None)]"""
    items = []
    for i, (label, href) in enumerate(trail):
        if href and i < len(trail) - 1:
            items.append(f'<li><a href="{href}">{e(label)}</a></li>')
        else:
            items.append(f'<li aria-current="page">{e(label)}</li>')
    return f'<nav class="crumbs" aria-label="Fil d\'Ariane"><ol>{"".join(items)}</ol></nav>'


def crumbs_ld(S, trail, path):
    elements = []
    for i, (label, href) in enumerate(trail, 1):
        item = {"@type": "ListItem", "position": i, "name": label}
        item["item"] = S.origin + href if href else S.abs(path)
        elements.append(item)
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": elements}


def section_head(title, link=None, label=None):
    more = f'<a class="link" href="{link[1]}">{e(link[0])}{icon("arrow")}</a>' if link else ""
    eyebrow = f'<p class="label">{e(label)}</p>' if label else ""
    return f'<header class="section__head"><div>{eyebrow}<h2 class="section__title">{e(title)}</h2></div>{more}</header>'


# --------------------------------------------------------------------------
# Ossature commune
# --------------------------------------------------------------------------
FONTS = ("https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@100..125,400..700"
         "&family=Cormorant+Garamond:ital,wght@1,500&display=swap")


def nav_links(S):
    links = [("Accueil", S.url("/"))]
    links += [(c["label"], S.cat_url(c["id"])) for c in S.cats]
    if S.new_products:
        links.append(("Nouveautés", S.url("/collection/nouveautes/")))
    return links


def header(S):
    k = S.c["contact"]
    nav = "".join(f'<li><a href="{href}">{e(label)}</a></li>' for label, href in nav_links(S))
    demo = (f'<div class="demo-strip"><p><span class="announce__short">{e(S.c["demo"].get("noticeShort", S.c["demo"]["notice"]))}</span>'
            f'<span class="announce__long">{e(S.c["demo"]["notice"])}</span></p></div>') if S.demo else ""
    return f'''<div class="announce"><p><span class="announce__short">{e(S.c["announcement"]["short"])}</span><span class="announce__long">{e(S.c["announcement"]["long"])}</span></p></div>
{demo}
<header class="header" data-header>
  <div class="header__inner">
    <div class="header__left">
      <button class="header__btn header__burger" type="button" data-open="menu" aria-label="Ouvrir le menu">{icon("menu")}</button>
      <nav class="header__nav" aria-label="Navigation principale"><ul>{nav}</ul></nav>
    </div>
    <a class="logo" href="{S.url("/")}" aria-label="Prince Shop — accueil">Prince Shop</a>
    <div class="header__right">
      <a class="header__text" href="{e(k["instagramUrl"])}" target="_blank" rel="noopener">Instagram</a>
      <button class="header__btn" type="button" data-open="search" aria-label="Rechercher">{icon("search")}<span class="header__label">Recherche</span></button>
      <button class="header__btn header__cart" type="button" data-open="cart" data-cart-button aria-label="Panier">{icon("bag")}<span class="header__label">Panier</span><span class="header__count" data-cart-count hidden>0</span></button>
    </div>
  </div>
</header>'''


def tabbar(S, page_id):
    """Navigation basse sur mobile : tout ce qui compte sous le pouce."""
    def current(name):
        return ' aria-current="page"' if name == page_id else ""
    return f'''<nav class="tabbar" aria-label="Navigation rapide">
  <a class="tabbar__item" href="{S.url("/")}"{current("home")}>{icon("home")}<span>Accueil</span></a>
  <a class="tabbar__item" href="{S.url("/collection/")}"{current("collection")}>{icon("grid")}<span>Boutique</span></a>
  <button class="tabbar__item" type="button" data-open="search">{icon("search")}<span>Recherche</span></button>
  <a class="tabbar__item" href="{e(S.wa())}" target="_blank" rel="noopener">{icon("whatsapp")}<span>WhatsApp</span></a>
  <button class="tabbar__item" type="button" data-open="cart" data-cart-button aria-label="Panier">{icon("bag")}<span>Panier</span><span class="tabbar__count" data-cart-count hidden>0</span></button>
</nav>'''


def footer(S):
    k, s = S.c["contact"], S.c["store"]
    cats = "".join(f'<li><a href="{S.cat_url(c["id"])}">{e(c["label"])}</a></li>' for c in S.cats)
    if S.new_products:
        cats += f'<li><a href="{S.url("/collection/nouveautes/")}">Nouveautés</a></li>'
    legal = f'<li><a href="{S.url("/informations/")}#questions">Questions fréquentes</a></li>'
    legal += "".join(f'<li><a href="{S.url("/informations/")}#{e(l["id"])}">{e(l["title"])}</a></li>' for l in S.content["legal"])
    year = date.today().year
    demo = f'<p class="footer__demo">{e(S.c["demo"]["notice"])}.</p>' if S.demo else ""
    return f'''<footer class="footer">
  <div class="wrap">
    <div class="footer__cta">
      <p class="footer__ask">Une question, une pointure, <em>une couleur ?</em></p>
      <a class="btn btn--light" href="{e(S.wa())}" target="_blank" rel="noopener">{icon("whatsapp")}Écrire sur WhatsApp</a>
    </div>
    <div class="footer__cols">
      <div>
        <h2 class="label">La boutique</h2>
        <p>{e(s["addressLine1"])}<br>{e(s["addressLine2"])}</p>
        <p>{e(s["hours"]["label"])}</p>
        <p><a class="link" href="{e(s["mapsUrl"])}" target="_blank" rel="noopener">Itinéraire{icon("arrow-out")}</a></p>
      </div>
      <div>
        <h2 class="label">Contact</h2>
        <ul>
          <li><a href="{e(S.wa())}" target="_blank" rel="noopener">WhatsApp · <span class="nw">{e(k["whatsappDisplay"])}</span></a></li>
          <li><a href="tel:+{S.phone}">Téléphone · <span class="nw">{e(k["phoneDisplay"])}</span></a></li>
          <li><a href="{e(k["instagramUrl"])}" target="_blank" rel="noopener">Instagram · <span class="nw">@{e(k["instagramHandle"])}</span></a></li>
        </ul>
      </div>
      <div>
        <h2 class="label">Collection</h2>
        <ul>{cats}<li><a href="{S.url("/collection/")}">Tout voir</a></li></ul>
      </div>
      <div>
        <h2 class="label">Informations</h2>
        <ul>{legal}</ul>
      </div>
    </div>
    <p class="footer__mark" aria-hidden="true">Prince Shop</p>
    <p class="footer__legal">© {year} Prince Shop · Fès, Maroc</p>
    {demo}
  </div>
</footer>'''


def dialogs(S):
    k, s = S.c["contact"], S.c["store"]
    menu_cats = ""
    for c in S.cats:
        types = "".join(f'<li><a href="{S.cat_url(c["id"], t["id"])}">{e(t["label"])}</a></li>' for t in c["types"])
        menu_cats += (f'<li><a class="menu__link" href="{S.cat_url(c["id"])}">{e(c["label"])}</a>'
                      f'{"<ul class=menu__sub>" + types + "</ul>" if types else ""}</li>')
    new = f'<li><a class="menu__link" href="{S.url("/collection/nouveautes/")}">Nouveautés</a></li>' if S.new_products else ""
    quick_links = "".join(f'<li><a href="{S.cat_url(c["id"], t["id"])}">{e(t["label"])}</a></li>' for c in S.cats for t in c["types"])
    return f'''<dialog class="sheet sheet--menu" id="menu" aria-label="Menu">
  <div class="sheet__panel">
    <div class="sheet__top"><span class="logo logo--static">Prince Shop</span><button class="header__btn" type="button" data-close aria-label="Fermer le menu">{icon("close")}</button></div>
    <nav class="menu" aria-label="Menu">
      <ul class="menu__list">
        <li><a class="menu__link" href="{S.url("/")}">Accueil</a></li>
        {menu_cats}{new}
        <li><a class="menu__link" href="{S.url("/")}#boutique">La boutique</a></li>
      </ul>
    </nav>
    <div class="menu__foot">
      <a class="btn btn--primary btn--block" href="{e(S.wa())}" target="_blank" rel="noopener">{icon("whatsapp")}Écrire sur WhatsApp</a>
      <ul class="menu__meta">
        <li><a href="{e(k["instagramUrl"])}" target="_blank" rel="noopener">Instagram · @{e(k["instagramHandle"])}</a></li>
        <li><a href="tel:+{S.phone}">Téléphone · {e(k["phoneDisplay"])}</a></li>
        <li><a href="{e(s["mapsUrl"])}" target="_blank" rel="noopener">{e(s["addressLine1"])}, {e(s["city"])}</a></li>
      </ul>
    </div>
  </div>
</dialog>

<dialog class="sheet sheet--search" id="search" aria-label="Recherche">
  <div class="sheet__panel">
    <form class="search" role="search" action="{S.url("/collection/")}" method="get" data-search-form>
      {icon("search")}
      <label class="sr-only" for="q">Rechercher un article</label>
      <input id="q" name="q" type="search" placeholder="Mocassin, basket, sac…" autocomplete="off" autocapitalize="off" spellcheck="false" enterkeyhint="search" data-search-input>
      <button class="header__btn" type="button" data-close aria-label="Fermer la recherche">{icon("close")}</button>
    </form>
    <div class="search__body" data-search-body>
      <div class="search__idle" data-search-idle>
        <p class="label">Parcourir</p>
        <ul class="search__links">{quick_links}</ul>
      </div>
      <div data-search-results aria-live="polite"></div>
    </div>
  </div>
</dialog>

<dialog class="sheet sheet--drawer" id="cart" aria-labelledby="cart-title">
  <div class="sheet__panel">
    <div class="sheet__top"><h2 class="sheet__title" id="cart-title">Votre sélection <span data-cart-title-count></span></h2><button class="header__btn" type="button" data-close aria-label="Fermer le panier">{icon("close")}</button></div>
    <div class="cart" data-cart-body></div>
  </div>
</dialog>

<dialog class="sheet sheet--pop" id="quick" aria-label="Ajout rapide">
  <div class="sheet__panel" data-quick-body></div>
</dialog>'''


def layout(S, *, page_id, title, description, path, body, ld=(), og_image=None, noindex=False, og_type="website", bar=True):
    site = S.c["site"]
    canonical = S.abs(path)
    image = og_image or S.abs("/assets/brand/og.png")
    robots = '<meta name="robots" content="noindex, follow">' if noindex or site.get("noindex") else ""
    ld_html = "\n".join(json_ld(x) for x in ld)
    preconnect = '<link rel="preconnect" href="https://images.unsplash.com">' if any(
        as_image(i)["src"].startswith(UNSPLASH) for p in S.products for i in S.images_for(p)) else ""
    bottom = tabbar(S, page_id) if bar else ""
    return f'''<!doctype html>
<html lang="{e(site["lang"])}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{e(canonical)}">
{robots}
<meta name="theme-color" content="#F5F2EC">
<meta name="format-detection" content="telephone=no">
<meta property="og:site_name" content="{e(site["name"])}">
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="fr_MA">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{e(canonical)}">
<meta property="og:image" content="{e(image)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{S.url("/assets/brand/favicon.svg")}" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{preconnect}
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{S.asset("css/main.css")}">
<script>document.documentElement.classList.add("js")</script>
<script type="module" src="{S.asset("js/main.js")}"></script>
{ld_html}
</head>
<body data-page="{page_id}" data-base="{e(S.base)}"{" data-tabbar" if bar else ""}>
<a class="skip" href="#contenu">Aller au contenu</a>
{sprite()}
{french_spaces(header(S) + body + footer(S) + dialogs(S) + bottom)}
<a class="wa-float" href="{e(S.wa())}" target="_blank" rel="noopener" aria-label="Écrire à Prince Shop sur WhatsApp" data-wa-float>{icon("whatsapp")}</a>
<div class="toast" data-toast role="status" aria-live="polite"></div>
</body>
</html>
'''


# --------------------------------------------------------------------------
# Accueil
# --------------------------------------------------------------------------
def store_ld(S):
    site, s = S.c["site"], S.c["store"]
    data = {
        "@context": "https://schema.org",
        "@type": "Store",
        "@id": S.abs("/") + "#boutique",
        "name": site["name"],
        "url": S.abs("/"),
        "telephone": "+" + S.phone,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": s["addressLine1"],
            "addressLocality": s["city"],
            "addressCountry": s["countryCode"],
        },
        "geo": {"@type": "GeoCoordinates", "latitude": s["lat"], "longitude": s["lng"]},
        "hasMap": s["mapsUrl"],
        "sameAs": [S.c["contact"]["instagramUrl"]],
        "areaServed": {"@type": "Country", "name": "Maroc"},
    }
    if s["hours"].get("confirmed") and s["hours"].get("opens"):
        data["openingHoursSpecification"] = [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "opens": s["hours"]["opens"], "closes": s["hours"]["closes"],
        }]
    return data


def hero(S):
    h = S.c["hero"]
    links = [S.by_id[i] for i in h.get("links", []) if i in S.by_id]
    tiles = []
    if h.get("images"):
        for i, image in enumerate(h["images"][:2]):
            target = S.product_url(links[i]) if i < len(links) else S.url("/collection/")
            label = links[i]["name"] if i < len(links) else "Voir la collection"
            ratio = (4, 5) if i == 0 else (3, 4)
            tiles.append(f'<a class="hero__img hero__img--{"ab"[i]}" href="{target}" aria-label="{e(label)}">'
                         f'{S.img(image, sizes="(min-width:1024px) 40vw, 68vw", eager=True, ratio=ratio, folder="")}</a>')
    else:
        for i, p in enumerate(links[:2] or S.by_date()[:2]):
            tiles.append(f'<a class="hero__img hero__img--{"ab"[i]}" href="{S.product_url(p)}" aria-label="{e(p["name"])}">'
                         f'{media(S, p, eager=i == 0, sizes="(min-width:1024px) 40vw, 68vw")}</a>')
    facts = "".join(f"<li>{e(f)}</li>" for f in h.get("facts", []))
    return f'''<section class="hero">
  <div class="wrap hero__grid">
    <div class="hero__visual">{"".join(tiles)}</div>
    <div class="hero__text">
      <p class="label">{e(h["eyebrow"])}</p>
      <h1 class="hero__title">{e(h["title"])} <em>{e(h["titleAccent"])}</em></h1>
      <p class="hero__lede">{e(h["text"])}</p>
      <div class="hero__cta">
        <a class="btn btn--primary" href="{S.url("/collection/")}">Découvrir la collection</a>
        <a class="btn btn--ghost" href="{e(S.wa())}" target="_blank" rel="noopener">{icon("whatsapp")}Commander sur WhatsApp</a>
      </div>
      {f'<ul class="hero__facts">{facts}</ul>' if facts else ""}
    </div>
  </div>
</section>'''


def worlds(S):
    """Les catégories comme des univers : grande image, nom en grand, un seul geste."""
    tiles = []
    for i, c in enumerate(S.cats):
        items = [p for p in S.by_date() if p["category"] == c["id"]]
        with_photo = next((p for p in items if S.images_for(p)), None)
        sizes = "(min-width:768px) 50vw, 100vw"
        if c.get("image"):
            visual = S.img(c["image"], sizes=sizes, ratio=None, folder="")
        elif with_photo:
            visual = S.img(S.images_for(with_photo)[0], sizes=sizes, ratio=None)
        else:
            seen = list(dict.fromkeys(col["hex"] for p in items for col in p.get("colors", [])[:2]))[:8]
            visual = '<div class="mosaic" aria-hidden="true">' + "".join(f'<span style="--c:{e(x)}"></span>' for x in seen) + "</div>"
        n = c["count"]
        tiles.append(f'''<a class="world world--{"abc"[min(i, 2)]}" href="{S.cat_url(c["id"])}">
  {visual}
  <span class="world__body">
    <span class="world__count">{n} modèle{"s" if n > 1 else ""}</span>
    <span class="world__name">{e(c["label"])}</span>
    <span class="world__cta">Voir la sélection{icon("arrow")}</span>
  </span>
</a>''')
    if not tiles:
        return ""
    return f'''<section class="section section--first">
  <div class="wrap">
    <h2 class="sr-only">Catégories</h2>
    <div class="worlds worlds--{min(len(tiles), 3)}">{"".join(tiles)}</div>
  </div>
</section>'''


def selection(S, picks):
    """Sélection du moment : un produit en grand, quatre autour."""
    if len(picks) < 2:
        return ""
    cards = "".join(
        card(S, p, eager=False, cls="card--xl" if i == 0 and len(picks) >= 5 else "",
             sizes="(min-width:768px) 50vw, 100vw" if i == 0 else CARD_SIZES)
        for i, p in enumerate(picks))
    return f'''<section class="section">
  <div class="wrap">
    {section_head("Sélection du moment", ("Toute la collection", S.url("/collection/")))}
    <div class="grid grid--feature">{cards}</div>
  </div>
</section>'''


def spotlight(S):
    sp = S.c.get("spotlight") or {}
    p = S.by_id.get(sp.get("productId", ""))
    if not p:
        return ""
    colors = p.get("colors", [])
    palette = ""
    if len(colors) >= 3:
        stripes = "".join(
            f'<a class="stripe stripe--{tone(c["hex"])}" style="--c:{e(c["hex"])}" href="{S.product_url(p)}?couleur={slug(c["name"])}">'
            f'<span>{e(c["name"])}</span></a>' for c in colors)
        palette = f'<div class="palette" aria-label="Couleurs disponibles">{stripes}</div>'
    photo = ""
    if S.images_for(p):
        photo = (f'<a class="spot__photo" href="{S.product_url(p)}" tabindex="-1" aria-hidden="true">'
                 f'{media(S, p, sizes="(min-width:1024px) 34vw, 100vw")}</a>')
    return f'''<section class="spot{" spot--photo" if photo else ""}">
  <div class="wrap spot__grid">
    {photo}
    <div class="spot__text">
      <p class="label">{e(sp.get("eyebrow", "Le modèle du moment"))}</p>
      <h2 class="spot__title">{e(sp.get("title", p["name"]))} <em>{e(sp.get("titleAccent", ""))}</em></h2>
      <p class="spot__lede">{e(sp.get("text") or p.get("description", ""))}</p>
      <p class="spot__meta">{e(p["name"])} · {S.price_html(p)}</p>
      <a class="btn btn--light" href="{S.product_url(p)}">Voir le modèle</a>
    </div>
    {palette}
  </div>
</section>'''


def rail(S, title, items, link):
    """Rangée horizontale : beaucoup de produits, peu de hauteur."""
    if len(items) < 3:
        return ""
    cards = "".join(card(S, p, sizes="(min-width:1024px) 22vw, 46vw") for p in items)
    return f'''<section class="section section--rail">
  <div class="wrap">
    <header class="section__head">
      <div><h2 class="section__title">{e(title)}</h2></div>
      <div class="rail__nav">
        <a class="link" href="{link[1]}">{e(link[0])}{icon("arrow")}</a>
        <button class="rail__btn" type="button" data-rail-prev aria-label="Produits précédents">{icon("arrow")}</button>
        <button class="rail__btn" type="button" data-rail-next aria-label="Produits suivants">{icon("arrow")}</button>
      </div>
    </header>
  </div>
  <div class="rail" data-rail>{cards}</div>
</section>'''


MONTHS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]


def fr_date(iso):
    if not iso:
        return ""
    y, m, d = iso.split("-")
    return f"{int(d)} {MONTHS[int(m) - 1]} {y}"


def instagram(S):
    ig, k = S.c["instagram"], S.c["contact"]
    posts = ig.get("posts", [])
    rows = "".join(
        f'<li><a href="{e(p["url"])}" target="_blank" rel="noopener"><span class="reel-row__play">{icon("play")}</span>'
        f'<span class="reel-row__label">{e(p["label"])}</span><span class="reel-row__date">{e(fr_date(p.get("date")))}</span>{icon("arrow-out")}</a></li>'
        for p in posts)
    listing = f'<ul class="reel-rows">{rows}</ul>' if rows else ""
    # Mosaïque : les vignettes des reels si elles sont fournies, sinon des visuels du catalogue.
    tiles = [(S.img(p["image"], alt=p["label"], sizes="(min-width:900px) 16vw, 33vw", ratio=(1, 1), folder=""), p["url"])
             for p in posts if p.get("image")]
    if len(tiles) < 3:
        shown = set(S.c["hero"].get("links", []))
        pool = [p for p in S.products if p["id"] not in shown and S.images_for(p)]
        tiles = [(S.img(S.images_for(p)[0], sizes="(min-width:900px) 16vw, 33vw", ratio=(1, 1)), k["instagramUrl"]) for p in pool[1::2][:6]]
    mosaic = ""
    if len(tiles) >= 3:
        cells = "".join(f'<a href="{e(url)}" target="_blank" rel="noopener" tabindex="-1" aria-hidden="true">{image}</a>' for image, url in tiles[:6])
        mosaic = f'<div class="insta__mosaic">{cells}</div>'
    return f'''<section class="section insta">
  <div class="wrap">
    <div class="insta__grid">
      <div class="insta__text">
        <p class="label">{e(ig["title"])}</p>
        <h2 class="insta__handle"><a href="{e(k["instagramUrl"])}" target="_blank" rel="noopener">@{e(k["instagramHandle"])}</a></h2>
        <p class="insta__lede">{e(ig["text"])}</p>
        <a class="btn btn--ghost" href="{e(k["instagramUrl"])}" target="_blank" rel="noopener">{icon("instagram")}Voir sur Instagram</a>
      </div>
      {listing}
    </div>
    {mosaic}
  </div>
</section>'''


def how_to(S):
    how = S.content["howTo"]
    steps = "".join(f'<li><span class="how__n" aria-hidden="true">{i}</span><h3>{e(st["title"])}</h3><p>{e(st["text"])}</p></li>'
                    for i, st in enumerate(how["steps"], 1))
    return f'''<section class="section how">
  <div class="wrap">
    {section_head(how["title"])}
    <ol class="how__list">{steps}</ol>
  </div>
</section>'''


def store_section(S):
    s, k, about = S.c["store"], S.c["contact"], S.content["about"]
    hours_note = "" if s["hours"].get("confirmed") else f'<small>Horaires indiqués sur {e(s["hours"]["source"])}</small>'
    return f'''<section class="section store" id="boutique">
  <div class="wrap store__grid">
    <div class="store__intro">
      <p class="label">La boutique</p>
      <h2 class="section__title">{e(about["title"])}</h2>
      <p class="store__lede">{e(about["text"])}</p>
      <div class="store__cta">
        <a class="btn btn--primary" href="{e(s["mapsUrl"])}" target="_blank" rel="noopener">{icon("pin")}Itinéraire</a>
        <a class="btn btn--ghost" href="{e(S.wa())}" target="_blank" rel="noopener">{icon("whatsapp")}WhatsApp</a>
        <a class="btn btn--ghost" href="tel:+{S.phone}">{icon("phone")}Appeler</a>
      </div>
    </div>
    <dl class="facts">
      <div><dt class="label">Adresse</dt><dd>{e(s["addressLine1"])}<br>{e(s["addressLine2"])}<br><a class="link" href="{e(s["mapsUrl"])}" target="_blank" rel="noopener">Voir sur Google Maps{icon("arrow-out")}</a></dd></div>
      <div><dt class="label">Horaires</dt><dd>{e(s["hours"]["label"])}{hours_note}</dd></div>
      <div><dt class="label">Téléphone</dt><dd><a href="tel:+{S.phone}">{e(k["phoneDisplay"])}</a></dd></div>
      <div><dt class="label">WhatsApp</dt><dd><a href="{e(S.wa())}" target="_blank" rel="noopener">{e(k["whatsappDisplay"])}</a></dd></div>
    </dl>
  </div>
</section>'''


def page_home(S):
    home = S.c.get("home") or {}
    spot_id = (S.c.get("spotlight") or {}).get("productId")
    picks = [S.by_id[i] for i in home.get("selection", []) if i in S.by_id]
    if not picks:
        picks = [p for p in S.products if p.get("featured") and p["id"] != spot_id]
    picks = [p for p in picks if p.get("available", True)][:5]
    newest = S.new_products or S.by_date()
    body = f'''<main id="contenu">
{hero(S)}
{worlds(S)}
{selection(S, picks)}
{spotlight(S)}
{rail(S, "Nouveautés", newest[:10], ("Tout voir", S.url("/collection/nouveautes/") if S.new_products else S.url("/collection/")))}
{instagram(S)}
{how_to(S)}
{store_section(S)}
</main>'''
    site = S.c["site"]
    website = {"@context": "https://schema.org", "@type": "WebSite", "name": site["name"], "url": S.abs("/")}
    return layout(S, page_id="home", title=site["title"], description=site["description"], path="/",
                  body=body, ld=[website, store_ld(S)])


# --------------------------------------------------------------------------
# Collection
# --------------------------------------------------------------------------
def page_collection(S, *, scope, path, title, heading, intro, items, trail):
    """scope: {"category": id} | {"new": true} | {} (tout)."""
    if scope.get("category"):
        cat = next(c for c in S.cats if c["id"] == scope["category"])
        chips = ['<button class="chip is-active" type="button" data-type="">Tout</button>']
        chips += [f'<button class="chip" type="button" data-type="{e(t["id"])}">{e(t["label"])}</button>' for t in cat["types"]]
        chips_html = f'<div class="chips" role="group" aria-label="Type d\'article">{"".join(chips)}</div>' if len(cat["types"]) > 1 else ""
    else:
        links = [f'<a class="chip{" is-active" if not scope else ""}" href="{S.url("/collection/")}">Tout</a>']
        links += [f'<a class="chip" href="{S.cat_url(c["id"])}">{e(c["label"])}</a>' for c in S.cats]
        if S.new_products:
            links.append(f'<a class="chip{" is-active" if scope.get("new") else ""}" href="{S.url("/collection/nouveautes/")}">Nouveautés</a>')
        chips_html = f'<nav class="chips" aria-label="Catégories">{"".join(links)}</nav>'
    cards = "".join(card(S, p, eager=i < 4) for i, p in enumerate(items))
    n = len(items)
    body = f'''<main id="contenu" class="plp">
  <div class="wrap">
    {crumbs(S, trail)}
    <header class="plp__head">
      <h1 class="plp__title" data-plp-title>{e(heading)}</h1>
      {f'<p class="plp__intro">{e(intro)}</p>' if intro else ""}
    </header>
    <div class="toolbar" data-toolbar>
      {chips_html}
      <div class="toolbar__row">
        <p class="toolbar__count" aria-live="polite"><span data-count>{n}</span> <span data-count-label>article{"s" if n > 1 else ""}</span></p>
        <div class="toolbar__actions">
          <button class="toolbar__btn" type="button" data-open="filters">{icon("filter")}Filtrer<span class="toolbar__n" data-filter-count hidden></span></button>
          <label class="toolbar__sort"><span class="toolbar__sort-label">Trier</span>
            <select data-sort aria-label="Trier par">
              <option value="nouveautes">Nouveautés</option>
              <option value="prix-asc">Prix croissant</option>
              <option value="prix-desc">Prix décroissant</option>
            </select>{icon("chevron")}
          </label>
        </div>
      </div>
      <div class="active" data-active hidden></div>
    </div>
    <div class="grid grid--plp" data-grid data-scope="{e(json.dumps(scope))}">{cards}</div>
    <div class="empty" data-empty hidden>
      <p class="empty__title">Aucun article ne correspond.</p>
      <p>Essayez avec moins de filtres, ou demandez-nous directement sur WhatsApp.</p>
      <div class="empty__cta">
        <button class="btn btn--primary" type="button" data-clear>Effacer les filtres</button>
        <a class="btn btn--ghost" href="{e(S.wa())}" target="_blank" rel="noopener">{icon("whatsapp")}Demander sur WhatsApp</a>
      </div>
    </div>
  </div>
</main>
<dialog class="sheet sheet--drawer sheet--filters" id="filters" aria-labelledby="filters-title">
  <div class="sheet__panel">
    <div class="sheet__top"><h2 class="sheet__title" id="filters-title">Filtrer</h2><button class="header__btn" type="button" data-close aria-label="Fermer les filtres">{icon("close")}</button></div>
    <div class="filters" data-filters></div>
    <div class="sheet__foot">
      <button class="btn btn--ghost" type="button" data-clear>Effacer</button>
      <button class="btn btn--primary" type="button" data-close>Voir <span data-count>{n}</span> <span data-count-label>article{"s" if n > 1 else ""}</span></button>
    </div>
  </div>
</dialog>'''
    item_list = {
        "@context": "https://schema.org", "@type": "ItemList", "name": heading,
        "itemListElement": [{"@type": "ListItem", "position": i, "url": S.abs(f"/produit/{p['id']}/"), "name": p["name"]}
                            for i, p in enumerate(items, 1)],
    }
    desc = intro or S.c["site"]["description"]
    return layout(S, page_id="collection", title=title, description=desc, path=path, body=body,
                  ld=[crumbs_ld(S, trail, path), item_list])


# --------------------------------------------------------------------------
# Fiche produit
# --------------------------------------------------------------------------
PDP_SIZES = "(min-width:1024px) 45vw, 100vw"


def product_message(S, p, color=None, size=None):
    m = S.c["messages"]
    bits = [p["name"]]
    if color:
        bits.append(color)
    if size:
        bits.append(str(size))
    return f'{m["greeting"]}\n\n{m["productIntro"]}\n• {" — ".join(bits)} (réf. {p["ref"]})\n\n{m["productClosing"]}'


def gallery(S, p, color):
    images = S.images_for(p, color)
    label = p["name"] + (f' — {color["name"]}' if color else "")
    if images:
        slides = "".join(
            f'<figure class="gallery__slide"><button class="gallery__zoom" type="button" data-zoom="{i}" aria-label="Agrandir la photo {i + 1}">'
            f'{S.img(image, alt=label, sizes=PDP_SIZES, eager=i == 0)}{icon("expand")}</button></figure>'
            for i, image in enumerate(images))
        thumbs = "".join(
            f'<button type="button" data-thumb="{i}" aria-label="Photo {i + 1}"{" aria-current=true" if i == 0 else ""}>'
            f'<img src="{e(S.sources(image)["thumb"])}" alt="" width="64" height="80" loading="lazy" decoding="async"></button>'
            for i, image in enumerate(images))
    else:
        slides = f'<figure class="gallery__slide">{media(S, p, color, eager=True)}</figure>'
        thumbs = ""
    n = max(len(images), 1)
    demo = f'<span class="gallery__demo">{e(S.c["demo"]["imageLabel"])}</span>' if S.is_demo(p) and images else ""
    return f'''<div class="gallery gallery--{min(n, 2)}" data-gallery>
  <div class="gallery__track" data-track>{slides}</div>
  <p class="gallery__count" data-gallery-count aria-hidden="true"{" hidden" if n < 2 else ""}>1 / {n}</p>
  <div class="gallery__thumbs" data-thumbs{" hidden" if n < 2 else ""}>{thumbs}</div>
  {demo}
</div>'''


def page_product(S, p):
    cat = S.cat_by_id[p["category"]]
    t = S.type_of(p)
    path = f"/produit/{p['id']}/"
    colors = p.get("colors", [])
    first = colors[0] if colors else None
    available = p.get("available", True)
    trail = [("Accueil", S.url("/")), (cat["label"], S.cat_url(cat["id"])), (p["name"], None)]

    color_group = ""
    if len(colors) == 1:
        color_group = (f'<p class="picker__static"><span>Couleur</span><b>{e(first["name"])}</b>'
                       f'<i class="dot dot--{tone(first["hex"])}" style="--c:{e(first["hex"])}"></i>'
                       f'<input type="hidden" name="color" value="{e(first["name"])}"></p>')
    elif colors:
        swatches = "".join(
            f'<label class="swatch"><input type="radio" name="color" value="{e(c["name"])}"{" checked" if i == 0 else ""}{"" if available else " disabled"}>'
            f'<span class="swatch__dot dot--{tone(c["hex"])}" style="--c:{e(c["hex"])}"></span><span class="sr-only">{e(c["name"])}</span></label>'
            for i, c in enumerate(colors))
        note = f'<p class="picker__note">{e(p["colorNote"])}</p>' if p.get("colorNote") else ""
        color_group = f'''<fieldset class="picker__group">
  <legend><span>Couleur</span><b data-color-name>{e(first["name"])}</b></legend>
  <div class="swatches">{swatches}</div>
  <p class="picker__note picker__note--photo" data-photo-note hidden></p>
  {note}
</fieldset>'''

    size_group = ""
    sizes = p.get("sizes", [])
    if sizes:
        off = set(map(str, p.get("unavailableSizes", [])))
        size_label = cat.get("sizeLabel", "Taille")
        chips = "".join(
            f'<label class="size{" size--off" if str(s) in off else ""}"><input type="radio" name="size" value="{e(s)}"'
            f'{" disabled" if str(s) in off or not available else ""}><span>{e(s)}</span>'
            f'{"<span class=sr-only> (indisponible)</span>" if str(s) in off else ""}</label>' for s in sizes)
        size_group = f'''<fieldset class="picker__group" data-size-group>
  <legend><span>{e(size_label)}</span><b data-size-name>À choisir</b></legend>
  <div class="sizes">{chips}</div>
  <p class="picker__error" data-size-error role="alert" hidden>Choisissez votre {e(size_label.lower())} pour continuer.</p>
  <p class="picker__note">Disponibilité confirmée sur WhatsApp. Entre deux {e(size_label.lower())}s ? <a class="link" href="{e(S.wa(product_message(S, p)))}" target="_blank" rel="noopener" data-wa-product>Demandez-nous</a>.</p>
</fieldset>'''

    if available:
        add_btn = '<button class="btn btn--primary btn--block" type="submit" data-add><span data-add-label>Ajouter au panier</span></button>'
        wa_label = "Commander via WhatsApp"
    else:
        add_btn = '<button class="btn btn--primary btn--block" type="button" disabled>Indisponible pour le moment</button>'
        wa_label = "Demander sur WhatsApp"
    wa_href = S.wa(product_message(S, p, first["name"] if first else None))

    if p.get("price") is None:
        price_note = '<p class="pdp__note">Le prix vous est confirmé sur WhatsApp.</p>'
    elif S.is_demo(p):
        price_note = f'<p class="pdp__note">{e(S.c["demo"]["priceNote"])}</p>'
    else:
        price_note = ""
    details = ""
    if p.get("details"):
        lis = "".join(f"<li>{e(d)}</li>" for d in p["details"])
        details = f'<details class="acc__item" open><summary>Détails{icon("plus")}</summary><div class="acc__body"><ul class="bullets">{lis}</ul><p class="acc__ref">Réf. {e(p["ref"])}</p></div></details>'
    d, pay, s = S.c["delivery"], S.c["payment"], S.c["store"]
    insta = ""
    if p.get("instagramUrl"):
        insta = f'<a class="pdp__reel" href="{e(p["instagramUrl"])}" target="_blank" rel="noopener"><span class="pdp__reel-play">{icon("play")}</span><span><strong>Voir ce modèle en vidéo</strong><small>Reel sur @{e(S.c["contact"]["instagramHandle"])}</small></span>{icon("arrow-out")}</a>'

    related = [x for x in S.by_date() if x["id"] != p["id"] and x["category"] == p["category"]]
    related.sort(key=lambda x: x.get("type") != p.get("type"))
    related = related[:4]
    related_html = ""
    if len(related) >= 2:
        related_html = f'''<section class="section related">
  {section_head("Vous pourriez aussi aimer", (cat["label"], S.cat_url(cat["id"])))}
  <div class="grid">{"".join(card(S, x) for x in related)}</div>
</section>'''

    body = f'''<main id="contenu" class="pdp" data-product="{e(p["id"])}">
  <div class="wrap">
    {crumbs(S, trail)}
    <div class="pdp__grid">
      {gallery(S, p, first)}
      <div class="pdp__info">
        <p class="label">{e(t["label"])}{' · <span class="pdp__new">' + e(p["badge"]) + "</span>" if p.get("badge") and available else ""}</p>
        <h1 class="pdp__name">{e(p["name"])}</h1>
        <p class="pdp__price">{S.price_html(p)}</p>
        {price_note}
        <p class="pdp__desc">{e(p.get("description", ""))}</p>
        <form class="picker" data-picker novalidate>
          {color_group}
          {size_group}
          <div class="pdp__actions" data-actions>
            {add_btn}
            <a class="btn btn--ghost btn--block" href="{e(wa_href)}" target="_blank" rel="noopener" data-wa-product data-wa-main>{icon("whatsapp")}{wa_label}</a>
          </div>
        </form>
        <ul class="assure">
          <li>{icon("truck")}<p><strong>{e(d["headline"])}</strong><span>{e(d["note"])}</span></p></li>
          <li>{icon("check")}<p><strong>Disponibilité vérifiée avant validation</strong><span>Couleur et pointure confirmées avec vous sur WhatsApp.</span></p></li>
          <li>{icon("pin")}<p><strong>Boutique à {e(s["city"])}</strong><span>{e(s["addressLine1"])} · <a class="link" href="{e(s["mapsUrl"])}" target="_blank" rel="noopener">Google Maps</a></span></p></li>
        </ul>
        {insta}
        <div class="acc">
          {details}
          <details class="acc__item"><summary>Livraison &amp; paiement{icon("plus")}</summary><div class="acc__body"><p>{e(d["note"])}</p><p>{e(pay["note"])}</p></div></details>
        </div>
      </div>
    </div>
    {related_html}
  </div>
  <div class="buybar" data-buybar hidden>
    <button class="buybar__cart" type="button" data-open="cart" data-cart-button aria-label="Panier">{icon("bag")}<span class="buybar__count" data-cart-count hidden>0</span></button>
    <p class="buybar__info"><strong>{e(p["name"])}</strong><span data-buybar-variant>{S.price_html(p)}</span></p>
    <button class="btn btn--primary" type="button" data-buybar-add{"" if available else " disabled"}>{"Ajouter" if available else "Indisponible"}</button>
  </div>
</main>
<dialog class="sheet sheet--zoom" id="zoom" aria-label="Photo agrandie">
  <div class="sheet__panel zoom">
    <div class="zoom__bar">
      <p class="zoom__count" data-zoom-count></p>
      <button class="header__btn" type="button" data-close aria-label="Fermer la photo">{icon("close")}</button>
    </div>
    <div class="zoom__stage" data-zoom-stage><img data-zoom-img alt="" decoding="async"></div>
    <div class="zoom__nav">
      <button class="rail__btn" type="button" data-zoom-prev aria-label="Photo précédente">{icon("arrow")}</button>
      <p class="zoom__hint" data-zoom-hint>Touchez la photo pour zoomer</p>
      <button class="rail__btn" type="button" data-zoom-next aria-label="Photo suivante">{icon("arrow")}</button>
    </div>
  </div>
</dialog>'''

    ld = {
        "@context": "https://schema.org", "@type": "Product",
        "name": p["name"], "description": p.get("description", ""), "sku": p["ref"],
        "category": f'{cat["label"]} > {t["label"]}', "url": S.abs(path),
    }
    all_images = []
    for image in S.images_for(p):
        full = S.sources(image)["full"]
        all_images.append(full if is_remote(full) else S.origin + full)
    if all_images:
        ld["image"] = all_images
    if colors:
        ld["color"] = ", ".join(c["name"] for c in colors)
    if p.get("price") is not None and not S.is_demo(p):
        ld["offers"] = {
            "@type": "Offer", "price": str(p["price"]), "priceCurrency": S.c["site"]["currencyCode"],
            "url": S.abs(path), "seller": {"@id": S.abs("/") + "#boutique"},
        }
        if not available:
            ld["offers"]["availability"] = "https://schema.org/OutOfStock"
    price_txt = f' — {fmt_price(p["price"])} {S.c["site"]["currency"]}' if p.get("price") is not None else ""
    title = f'{p["name"]}{price_txt} | Prince Shop Fès'
    desc = f'{p.get("description", p["name"])} Livraison partout au Maroc, commande sur WhatsApp.'.strip()
    return layout(S, page_id="product", title=title, description=desc, path=path, body=body, bar=False,
                  ld=[crumbs_ld(S, trail, path), ld], og_image=all_images[0] if all_images else None, og_type="product")


# --------------------------------------------------------------------------
# Commande
# --------------------------------------------------------------------------
def page_checkout(S):
    k, pay = S.c["contact"], S.c["payment"]
    cities = "".join(f'<option value="{e(c)}">' for c in S.c["cities"])
    demo = f'<p class="co__demo">{e(S.c["demo"]["checkoutNote"])}</p>' if S.demo else ""
    body = f'''<main id="contenu" class="co" data-checkout>
  <div class="wrap co__wrap">
    <header class="co__head">
      <a class="link link--back" href="{S.url("/collection/")}" data-back>{icon("arrow")}Continuer mes achats</a>
      <h1 class="co__title">Finaliser ma commande</h1>
      <ol class="co__steps" aria-label="Étapes">
        <li data-step-dot="form" aria-current="step"><span>1</span>Vos informations</li>
        <li data-step-dot="review"><span>2</span>Vérification</li>
        <li data-step-dot="sent"><span>3</span>WhatsApp</li>
      </ol>
    </header>

    <div class="co__grid" data-co-main hidden>
      <div class="co__main">
        <section data-step="form">
          <form class="form" data-order-form novalidate>
            <div class="field">
              <label for="f-name">Nom complet</label>
              <input id="f-name" name="name" type="text" autocomplete="name" autocapitalize="words" enterkeyhint="next" required>
              <p class="field__error" data-error="name" hidden></p>
            </div>
            <div class="field">
              <label for="f-phone">Téléphone</label>
              <input id="f-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="06 12 34 56 78" enterkeyhint="next" required aria-describedby="f-phone-hint">
              <p class="field__hint" id="f-phone-hint">Le numéro sur lequel on peut vous joindre pour la livraison.</p>
              <p class="field__error" data-error="phone" hidden></p>
            </div>
            <div class="field">
              <label for="f-city">Ville</label>
              <input id="f-city" name="city" type="text" list="villes" autocomplete="address-level2" autocapitalize="words" enterkeyhint="next" required>
              <datalist id="villes">{cities}</datalist>
              <p class="field__error" data-error="city" hidden></p>
            </div>
            <div class="field">
              <label for="f-address">Adresse de livraison</label>
              <textarea id="f-address" name="address" rows="2" autocomplete="street-address" placeholder="Quartier, rue, numéro, étage…" required></textarea>
              <p class="field__error" data-error="address" hidden></p>
            </div>
            <div class="field">
              <label for="f-note">Note <span class="field__opt">facultatif</span></label>
              <textarea id="f-note" name="note" rows="2" placeholder="Une précision sur la pointure, la couleur, un horaire…"></textarea>
            </div>
            <button class="btn btn--primary btn--block" type="submit">Vérifier ma commande</button>
            <p class="form__privacy">Aucun compte à créer. Vos informations ne sont pas enregistrées sur ce site : elles partent uniquement dans votre message WhatsApp à Prince Shop.</p>
          </form>
        </section>

        <section data-step="review" tabindex="-1" hidden>
          <h2 class="co__h2">Confirmer la commande</h2>
          <div class="review">
            <div class="review__block">
              <div class="review__top"><h3 class="label">Votre sélection</h3><button class="link" type="button" data-open="cart">Modifier</button></div>
              <div data-review-items></div>
            </div>
            <div class="review__block">
              <div class="review__top"><h3 class="label">Vos informations</h3><button class="link" type="button" data-edit>Modifier</button></div>
              <dl class="review__dl" data-review-customer></dl>
            </div>
          </div>
          <div class="next">
            <h3 class="label">Ce qui se passe ensuite</h3>
            <ol>
              <li>WhatsApp s'ouvre avec votre commande déjà rédigée : il vous reste à appuyer sur <strong>Envoyer</strong>.</li>
              <li>Prince Shop vous répond pour confirmer la disponibilité, le prix et la livraison.</li>
              <li>{e(pay["note"])}</li>
            </ol>
          </div>
          {demo}
          <a class="btn btn--wa btn--block" href="#" target="_blank" rel="noopener" data-send>{icon("whatsapp")}Envoyer la commande sur WhatsApp</a>
          <details class="msg"><summary>Voir le message qui sera envoyé</summary><pre data-message></pre></details>
        </section>

        <section data-step="sent" tabindex="-1" hidden>
          <p class="sent__mark">{icon("whatsapp")}</p>
          <h2 class="co__h2">Dernière étape : appuyez sur « Envoyer » dans WhatsApp</h2>
          <p class="sent__lede">Votre commande est rédigée dans la conversation avec Prince Shop ({e(k["whatsappDisplay"])}). Tant que le message n'est pas envoyé, la boutique ne la reçoit pas.</p>
          <div class="sent__cta">
            <a class="btn btn--ghost" href="#" target="_blank" rel="noopener" data-resend>{icon("whatsapp")}Rouvrir WhatsApp</a>
            <button class="btn btn--ghost" type="button" data-copy>Copier le message</button>
          </div>
          <p class="sent__help">WhatsApp ne s'ouvre pas ? Copiez le message et envoyez-le au {e(k["whatsappDisplay"])}, ou appelez le <a class="link" href="tel:+{S.phone}">{e(k["phoneDisplay"])}</a>.</p>
          <div class="sent__done">
            <button class="btn btn--primary" type="button" data-done>C'est envoyé — vider mon panier</button>
            <button class="link" type="button" data-edit>Revenir à ma commande</button>
          </div>
        </section>

        <section data-step="done" tabindex="-1" hidden>
          <p class="sent__mark">{icon("check")}</p>
          <h2 class="co__h2">Merci, à tout de suite sur WhatsApp.</h2>
          <p class="sent__lede">Prince Shop vous répond pour confirmer la disponibilité, le prix et la livraison. Gardez votre téléphone à portée de main.</p>
          <div class="sent__cta">
            <a class="btn btn--primary" href="{S.url("/collection/")}">Retour à la collection</a>
            <a class="btn btn--ghost" href="{e(k["instagramUrl"])}" target="_blank" rel="noopener">{icon("instagram")}Suivre sur Instagram</a>
          </div>
        </section>
      </div>

      <aside class="co__aside" aria-label="Récapitulatif" data-summary></aside>
    </div>

    <section class="empty empty--page" data-co-empty hidden>
      <p class="empty__title">Votre sélection est vide.</p>
      <p>Ajoutez un article pour passer commande, ou écrivez-nous directement.</p>
      <div class="empty__cta">
        <a class="btn btn--primary" href="{S.url("/collection/")}">Découvrir la collection</a>
        <a class="btn btn--ghost" href="{e(S.wa())}" target="_blank" rel="noopener">{icon("whatsapp")}WhatsApp</a>
      </div>
    </section>

    <noscript><p class="empty__title">Pour commander sans JavaScript, écrivez-nous sur WhatsApp au {e(k["whatsappDisplay"])}.</p></noscript>
  </div>
</main>'''
    return layout(S, page_id="checkout", title="Finaliser ma commande | Prince Shop", path="/commande/", bar=False,
                  description="Envoyez votre commande à Prince Shop sur WhatsApp en quelques secondes.", body=body, noindex=True)


# --------------------------------------------------------------------------
# Informations : questions fréquentes + livraison, paiement, échanges, conditions, confidentialité
# --------------------------------------------------------------------------
def page_legal(S):
    faq_items = "".join(
        f'<details class="acc__item"><summary>{e(f["q"])}{icon("plus")}</summary><div class="acc__body"><p>{e(S.fill(f["a"]))}</p></div></details>'
        for f in S.content["faq"])
    blocks = [f'<section class="info__sec" id="questions"><h2 class="section__title">Questions fréquentes</h2><div class="acc">{faq_items}</div></section>']
    toc = ['<li><a href="#questions">Questions fréquentes</a></li>']
    for sec in S.content["legal"]:
        toc.append(f'<li><a href="#{e(sec["id"])}">{e(sec["title"])}</a></li>')
        paras = "".join(f"<p>{e(S.fill(p))}</p>" for p in sec.get("body", []))
        warn = ""
        if not sec.get("confirmed"):
            warn = (f'<p class="draft"><strong>À confirmer par la boutique avant la mise en ligne.</strong> '
                    f'À préciser : {e(sec.get("todo", ""))}</p>')
        blocks.append(f'<section class="info__sec" id="{e(sec["id"])}"><h2 class="section__title">{e(sec["title"])}</h2>{paras}{warn}</section>')
    trail = [("Accueil", S.url("/")), ("Informations", None)]
    body = f'''<main id="contenu" class="info">
  <div class="wrap">
    {crumbs(S, trail)}
    <div class="info__grid">
      <aside class="info__toc"><h1 class="plp__title">Informations</h1><ul>{"".join(toc)}</ul>
        <a class="btn btn--ghost" href="{e(S.wa())}" target="_blank" rel="noopener">{icon("whatsapp")}Une question ?</a></aside>
      <div class="info__body">{"".join(blocks)}</div>
    </div>
  </div>
</main>'''
    pending = any(not s.get("confirmed") for s in S.content["legal"])
    return layout(S, page_id="info", title="Questions, livraison & informations | Prince Shop", path="/informations/",
                  description="Questions fréquentes, livraison partout au Maroc, paiement, échanges et conditions de vente de Prince Shop.",
                  body=body, noindex=pending)


def page_404(S):
    body = f'''<main id="contenu">
  <div class="wrap">
    <section class="empty empty--page">
      <p class="label">Erreur 404</p>
      <p class="empty__title">Cette page n'existe pas, ou plus.</p>
      <p>L'article a peut-être été retiré. La collection, elle, est toujours là.</p>
      <div class="empty__cta">
        <a class="btn btn--primary" href="{S.url("/collection/")}">Voir la collection</a>
        <a class="btn btn--ghost" href="{e(S.wa())}" target="_blank" rel="noopener">{icon("whatsapp")}WhatsApp</a>
      </div>
    </section>
  </div>
</main>'''
    return layout(S, page_id="404", title="Page introuvable | Prince Shop", path="/404.html",
                  description="Page introuvable.", body=body, noindex=True)
