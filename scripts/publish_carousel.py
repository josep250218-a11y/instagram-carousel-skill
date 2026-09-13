#!/usr/bin/env python3
"""
Renderiza un carousel con Open Carrusel y guarda los PNG en una carpeta local.

Uso:
    python3 publish_carousel.py <spec.json>
    python3 publish_carousel.py --overwrite <spec.json>
    python3 publish_carousel.py --config /ruta/config.json <spec.json>

Flags:
    --overwrite   Si la carpeta destino ya tiene PNG, los borra y escribe ahí.
                  Sin el flag, crea {slug}-v2, {slug}-v3, etc.
    --config      Ruta a un config.json alternativo.
                  Default: $CAROUSEL_CONFIG, luego <skill>/config.json,
                  luego <skill>/config.example.json.

Formato del spec:
{
    "title": "Llegó Nimbus 2.0",
    "format": "noticia",
    "template_tag": "card-pop",
    "caption": "...",
    "hashtags": ["productividad", "herramientas"],
    "style": "<style>...</style>",
    "slides": [
        {"body": "<article class=\\"slide\\">...</article>", "notes": "portada"},
        ...
    ]
}

Placeholders admitidos en style y body:
    {{HANDLE}}     → config.handle
    {{SIGNATURE}}  → config.signature

Salida (stdout, una línea key=value por línea):
    LOCAL_FOLDER=/Users/.../Carousels/llego-nimbus-20
    CAROUSEL_ID=abc-123
    TITLE_SLUG=llego-nimbus-20
    SLIDE_COUNT=5
    TOTAL_KB=246
"""

import io
import json
import os
import re
import subprocess
import sys
import unicodedata
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
VALID_TEMPLATES = {
    "card-pop",
    "tech-terminal",
    "numbered-steps",
    "sticky-note",
    "diary",
    "soft-poetic",
}
DEFAULT_FONT = "Outfit"
DEFAULT_FONT_MONO = "JetBrains Mono"


# ---------- config ----------


def load_config(explicit: str | None) -> dict:
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    if os.environ.get("CAROUSEL_CONFIG"):
        candidates.append(Path(os.environ["CAROUSEL_CONFIG"]))
    candidates.append(SKILL_DIR / "config.json")
    candidates.append(SKILL_DIR / "config.example.json")
    for path in candidates:
        if path.is_file():
            cfg = json.loads(path.read_text(encoding="utf-8"))
            cfg["_path"] = str(path)
            return cfg
    raise SystemExit("No se encontró config.json ni config.example.json")


def brand_override_css(brand: dict) -> str:
    """Convierte {"primary": "#123"} en <style>:root{--brand-primary:#123}</style>."""
    skip = {"font", "font_mono"}
    decls = []
    for key, value in brand.items():
        if key in skip or not value:
            continue
        css_key = "--brand-" + key.replace("_", "-")
        decls.append(f"{css_key}:{value}")
    if not decls:
        return ""
    return "<style>:root{" + ";".join(decls) + "}</style>"


FONT_DECL = re.compile(r"(font-family:\s*)(['\"]?)([^;'\"}]+?)\2(\s*,)")


def apply_placeholders(html: str, cfg: dict) -> str:
    brand = cfg.get("brand", {})
    html = html.replace("{{HANDLE}}", cfg.get("handle", ""))
    html = html.replace("{{SIGNATURE}}", cfg.get("signature", ""))
    font = brand.get("font") or DEFAULT_FONT
    mono = brand.get("font_mono") or DEFAULT_FONT_MONO

    def swap(m: re.Match) -> str:
        name = m.group(3).strip()
        if name == DEFAULT_FONT:
            name = font
        elif name == DEFAULT_FONT_MONO:
            name = mono
        # Sin comillas: el detector de Google Fonts de Open Carrusel no
        # reconoce "font-family: 'X', fallback" y renderiza sin la fuente.
        return f"{m.group(1)}{name}{m.group(4)}"

    return FONT_DECL.sub(swap, html)


# ---------- helpers ----------


def slugify(text: str) -> str:
    norm = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    norm = re.sub(r"[^a-zA-Z0-9\s-]", "", norm).strip().lower()
    return re.sub(r"[\s-]+", "-", norm) or "carousel"


class Api:
    def __init__(self, base: str):
        self.base = base.rstrip("/")

    def call(self, method: str, path: str, body=None, raw=False, timeout=120):
        url = f"{self.base}{path}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {"Content-Type": "application/json"} if body is not None else {}
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                content = r.read()
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            raise SystemExit(f"HTTP {e.code} en {method} {path}: {err_body}") from None
        except urllib.error.URLError as e:
            raise SystemExit(
                f"Open Carrusel no responde en {self.base} ({e.reason}). "
                "Ejecutar scripts/ensure_server.sh"
            ) from None
        if raw:
            return content
        return json.loads(content.decode("utf-8"))


def unique_folder(base: Path, slug: str) -> Path:
    candidate = base / slug
    suffix = 2
    while candidate.exists() and any(candidate.glob("*.png")):
        candidate = base / f"{slug}-v{suffix}"
        suffix += 1
    candidate.mkdir(parents=True, exist_ok=True)
    return candidate


def overwrite_folder(base: Path, slug: str) -> Path:
    folder = base / slug
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob("*.png"):
        old.unlink()
    cap = folder / "caption.txt"
    if cap.exists():
        cap.unlink()
    return folder


# ---------- main ----------


def main() -> None:
    args = sys.argv[1:]
    overwrite = False
    config_path = None
    while args and args[0].startswith("--"):
        flag = args.pop(0)
        if flag == "--overwrite":
            overwrite = True
        elif flag == "--config":
            if not args:
                raise SystemExit("--config requiere una ruta")
            config_path = args.pop(0)
        else:
            raise SystemExit(f"Flag desconocido: {flag}\n{__doc__}")

    if len(args) != 1:
        raise SystemExit(__doc__)

    cfg = load_config(config_path)
    spec = json.loads(Path(args[0]).read_text(encoding="utf-8"))

    title = spec["title"]
    style = spec.get("style", "")
    slides = spec["slides"]
    caption = spec.get("caption", "")
    hashtags = spec.get("hashtags", [])
    template_tag = spec.get("template_tag", "")

    if template_tag and template_tag not in VALID_TEMPLATES:
        raise SystemExit(
            f"template_tag inválido: {template_tag!r}. "
            f"Válidos: {', '.join(sorted(VALID_TEMPLATES))}"
        )
    if not slides:
        raise SystemExit("spec.slides está vacío")
    if not (5 <= len(slides) <= 10):
        print(f"Aviso: {len(slides)} slides (esperado 5–10)", file=sys.stderr)

    api = Api(cfg.get("api_url", "http://localhost:3000"))
    api.call("GET", "/api/brand", timeout=5)

    output_base = Path(os.path.expanduser(cfg.get("output_dir", "~/Carousels")))
    output_base.mkdir(parents=True, exist_ok=True)

    override = brand_override_css(cfg.get("brand", {}))
    style = apply_placeholders(style, cfg)

    # 1) Crear carousel
    carousel = api.call("POST", "/api/carousels", {"name": title, "aspectRatio": "4:5"})
    carousel_id = carousel["id"]

    # 2) Agregar slides: style del template + override de marca + body
    for slide in slides:
        body = apply_placeholders(slide["body"], cfg)
        html = "\n".join(part for part in (style, override, body) if part)
        api.call(
            "POST",
            f"/api/carousels/{carousel_id}/slides",
            {"html": html, "notes": slide.get("notes", "")},
        )

    # 3) Caption (best-effort)
    if caption or hashtags:
        try:
            api.call(
                "PUT",
                f"/api/carousels/{carousel_id}/caption",
                {"caption": caption, "hashtags": hashtags},
            )
        except SystemExit as e:
            print(f"Aviso: caption no guardado ({e})", file=sys.stderr)

    # 4) Exportar ZIP
    zip_bytes = api.call("POST", f"/api/carousels/{carousel_id}/export", raw=True)

    # 5) Descomprimir en output_dir/slug
    slug = slugify(title)
    folder = overwrite_folder(output_base, slug) if overwrite else unique_folder(output_base, slug)

    total_bytes = 0
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for member in zf.namelist():
            data = zf.read(member)
            (folder / member).write_bytes(data)
            total_bytes += len(data)

    # 6) caption.txt
    if caption or hashtags:
        text = caption
        if hashtags:
            tags = " ".join(h if h.startswith("#") else f"#{h}" for h in hashtags)
            text = f"{caption}\n\n{tags}".strip()
        (folder / "caption.txt").write_text(text, encoding="utf-8")

    # 7) Hook opcional
    hook = (cfg.get("after_export") or "").strip()
    if hook:
        cmd = hook.replace("{folder}", str(folder)).replace("{title}", title)
        subprocess.run(cmd, shell=True, check=False)

    # 8) Salida parseable
    print(f"LOCAL_FOLDER={folder}")
    print(f"CAROUSEL_ID={carousel_id}")
    print(f"TITLE_SLUG={folder.name}")
    print(f"SLIDE_COUNT={len(slides)}")
    print(f"TOTAL_KB={total_bytes // 1024}")


if __name__ == "__main__":
    main()
