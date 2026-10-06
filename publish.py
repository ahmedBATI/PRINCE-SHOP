#!/usr/bin/env python3
"""Publie le site sur GitHub Pages (branche gh-pages du dépôt « origin »).

    python publish.py

Le lien obtenu est https://<compte>.github.io/<dépôt>/ — une version de démonstration,
marquée « noindex » pour ne pas apparaître dans Google tant que le contenu n'est pas validé.
Aucune dépendance : Python et git suffisent.
"""
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def git(*args, cwd=ROOT, capture=False):
    result = subprocess.run(["git", *args], cwd=cwd, text=True, encoding="utf-8",
                            capture_output=capture, check=False)
    if result.returncode != 0:
        detail = (result.stderr or "").strip() if capture else ""
        sys.exit(f"\n✗ git {' '.join(args[:2])} a échoué. {detail}\n")
    return (result.stdout or "").strip()


def remove(path):
    """Supprime un dossier, y compris les fichiers en lecture seule que git crée sous Windows."""
    def unlock(func, target, _info):
        os.chmod(target, stat.S_IWRITE)
        func(target)
    if path.exists():
        shutil.rmtree(path, onerror=unlock)  # noqa: onerror reste accepté par Python 3.9 à 3.13


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    remote = git("remote", "get-url", "origin", capture=True)
    match = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$", remote)
    if not match:
        sys.exit(f"\n✗ Le dépôt « origin » n'est pas un dépôt GitHub : {remote}\n")
    owner, repo = match.groups()
    user_site = repo.lower() == f"{owner.lower()}.github.io"
    base = "" if user_site else f"/{repo}"
    origin = f"https://{owner.lower()}.github.io"

    # Dossier temporaire au chemin court : sous Windows, git et les chemins de plus de 260 caractères font mauvais ménage.
    out = Path(tempfile.mkdtemp(prefix="pshop-"))
    build = subprocess.run([sys.executable, str(ROOT / "build.py"), f"--out={out}",
                            f"--url={origin}", f"--base={base}", "--noindex"], cwd=ROOT)
    if build.returncode != 0:
        remove(out)
        sys.exit(build.returncode)

    message = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--message=")), "Publication du site")
    name = git("config", "user.name", capture=True)
    email = git("config", "user.email", capture=True)
    identity = ["-c", f"user.name={name}", "-c", f"user.email={email}"]
    try:
        git("init", "--quiet", "--initial-branch=gh-pages", cwd=out)
        git("add", "--all", cwd=out)
        git(*identity, "commit", "--quiet", "-m", message, cwd=out)
        git("push", "--force", remote, "gh-pages", cwd=out)
    finally:
        remove(out)

    print(f"\n✓ Publié. Le lien à partager (compter une à deux minutes la première fois) :\n\n   {origin}{base}/\n")


if __name__ == "__main__":
    main()
