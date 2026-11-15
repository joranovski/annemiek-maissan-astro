#!/usr/bin/env python3
"""Zet de Kirby-content van annemiekmaissan.nl om naar Astro-content.

Gebruik:  python3 scripts/kirby2astro.py <pad-naar-kirby-site>

Leest <kirby>/content/ en schrijft:
  src/content/pages/<slug>/index.md   (frontmatter met een lijst blokken + foto's ernaast)
  src/data/site.json                  (naam, omschrijving, links)

Draai dit opnieuw op de backup van de live site: die is leidend.
Bestaande pagina-mappen worden eerst leeggemaakt.
"""
import json
import re
import shutil
import sys
from pathlib import Path

import yaml
from PIL import Image

MAX_FOTO = 2400  # langste zijde in px, gelijk aan de Sveltia-instelling


def _str_blok(dumper, data):
    """Tekst met enters als leesbaar YAML-blok (|) schrijven."""
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


yaml.SafeDumper.add_representer(str, _str_blok)

ROOT = Path(__file__).resolve().parent.parent
UIT_PAGINAS = ROOT / "src/content/pages"
UIT_DATA = ROOT / "src/data"


def lees_txt(pad: Path) -> dict:
    """Kirby .txt → dict met sleutels in kleine letters."""
    velden = {}
    for deel in re.split(r"\n----\s*\n", pad.read_text(encoding="utf-8")):
        m = re.match(r"^\s*(\w[\w-]*):\s*(.*)$", deel, re.S)
        if m:
            velden[m.group(1).lower()] = m.group(2).strip()
    return velden


def schone_naam(naam: str) -> str:
    """Bestandsnaam normaliseren: kleine letters, geen spaties."""
    stam, ext = naam.rsplit(".", 1)
    stam = re.sub(r"[^a-z0-9]+", "-", stam.lower()).strip("-")
    return f"{stam}.{ext.lower().replace('jpeg', 'jpg')}"


def schone_tekst(t: str) -> str:
    """Kirby-tekst opschonen: line separators eruit, harde enters als Markdown-regeleinde."""
    t = (t or "").replace(" ", "").replace("\r", "").strip()
    return t


def regels_naar_markdown(t: str) -> str:
    """Een enkele Enter was in Kirby een <br>; in Markdown wordt dat een backslash aan het regeleinde."""
    t = schone_tekst(t)
    uit = []
    for alinea in t.split("\n\n"):
        regels = [r.rstrip() for r in alinea.split("\n")]
        if all(r.startswith(("- ", "* ")) for r in regels if r):
            uit.append("\n".join(regels))
        else:
            uit.append("\\\n".join(regels))
    return "\n\n".join(uit)


class Fotos:
    """Houdt bij welke foto's een pagina gebruikt en kopieert ze (verkleind) mee."""

    def __init__(self, bron: Path, doel: Path, uuids: dict):
        self.bron, self.doel, self.uuids = bron, doel, uuids
        self.gekopieerd = {}

    def pak(self, ref):
        if isinstance(ref, list):
            ref = ref[0] if ref else None
        if not ref:
            return None
        pad = self.uuids.get(ref.replace("file://", ""))
        if not pad:
            print(f"  ! foto niet gevonden: {ref}")
            return None
        naam = schone_naam(pad.name)
        if naam not in self.gekopieerd:
            img = Image.open(pad)
            img = img.convert("RGB") if img.mode not in ("RGB", "L") else img
            img.thumbnail((MAX_FOTO, MAX_FOTO))
            img.save(self.doel / naam, quality=86, optimize=True)
            meta = lees_txt(pad.with_name(pad.name + ".txt")) if pad.with_name(pad.name + ".txt").exists() else {}
            self.gekopieerd[naam] = meta.get("alt", "")
        return naam


def blok(b: dict, fotos: Fotos):
    """Eén Kirby-blok → één blok in het nieuwe model (of None)."""
    t, c = b["type"], b["content"]
    if b.get("isHidden"):
        return None
    if t == "hero":
        uit = {
            "type": "hero",
            "titel": schone_tekst(c.get("title")),
            "tekst": regels_naar_markdown(c.get("text")),
            "foto": fotos.pak(c.get("background_image")),
            "uitlijning": {"center": "midden", "right": "rechts"}.get(c.get("content_position"), "links"),
        }
    elif t == "text-points":
        uit = {
            "type": "punten",
            "kop": schone_tekst(c.get("headline")),
            "intro": regels_naar_markdown(c.get("intro")),
            "punten": [schone_tekst(i["title"]) for i in c.get("items", []) if i.get("title")],
            "afsluiting": regels_naar_markdown(c.get("ending")),
        }
    elif t == "feature":
        uit = {
            "type": "tekst",
            "kop": schone_tekst(c.get("heading")),
            "tekst": regels_naar_markdown(c.get("text")),
            "foto": fotos.pak(c.get("image")),
            "knoppen": [
                {"label": k.get("text", ""), "link": k.get("url", "")} for k in c.get("buttons", []) if k.get("text")
            ],
        }
    elif t == "image":
        naam = fotos.pak(c.get("image"))
        if not naam:
            return None
        uit = {"type": "fotos", "fotos": [{"src": naam, "alt": schone_tekst(c.get("alt")) or fotos.gekopieerd.get(naam, ""), "bijschrift": schone_tekst(c.get("caption"))}]}
    elif t == "pricingtable":
        uit = {
            "type": "prijzen",
            "kop": schone_tekst(c.get("title")),
            "subkop": schone_tekst(c.get("subtitle")),
            "pakketten": [
                {
                    "naam": p.get("name", ""),
                    "omschrijving": p.get("description", ""),
                    "prijs": p.get("price", ""),
                    "toelichting": p.get("details", ""),
                    "populair": p.get("popular") == "true",
                }
                for p in c.get("plans", [])
            ],
        }
    elif t == "form":
        uit = {"type": "formulier", "kop": "Contactformulier"}
    else:
        print(f"  ! bloktype '{t}' niet omgezet")
        return None
    # Lege velden weglaten, zodat de bestanden overzichtelijk blijven
    return {k: v for k, v in uit.items() if v not in ("", None, [])}


def main(kirby: Path):
    content = kirby / "content"
    # Alle bestanden met een UUID, zodat file://-verwijzingen opgelost kunnen worden
    uuids = {}
    for meta in content.rglob("*.txt"):
        if re.search(r"\.(jpe?g|png|webp)\.txt$", meta.name, re.I):
            u = lees_txt(meta).get("uuid")
            if u:
                uuids[u] = meta.with_name(meta.name[:-4])

    if UIT_PAGINAS.exists():
        shutil.rmtree(UIT_PAGINAS)
    UIT_PAGINAS.mkdir(parents=True)

    totaal_fotos = 0
    for map_ in sorted(p for p in content.iterdir() if p.is_dir() and p.name not in ("error", "forms")):
        m = re.match(r"^(\d+)_(.+)$", map_.name)
        order, slug = (int(m.group(1)), m.group(2)) if m else (None, map_.name)
        txt = next((f for f in map_.glob("*.txt") if not re.search(r"\.\w+\.txt$", f.name)), None)
        velden = lees_txt(txt)
        doel = UIT_PAGINAS / slug
        doel.mkdir()
        fotos = Fotos(map_, doel, uuids)

        blokken = []
        for rij in json.loads(velden.get("modules") or "[]"):
            for kolom in rij["columns"]:
                for b in kolom["blocks"]:
                    nieuw = blok(b, fotos)
                    if not nieuw:
                        continue
                    # Foto's naast elkaar in dezelfde rij worden één fotoblok
                    if nieuw["type"] == "fotos" and blokken and blokken[-1]["type"] == "fotos" and blokken[-1].get("_rij") == id(rij):
                        blokken[-1]["fotos"] += nieuw["fotos"]
                        continue
                    nieuw["_rij"] = id(rij)
                    blokken.append(nieuw)
        for b in blokken:
            b.pop("_rij", None)

        fm = {
            "title": velden.get("title", slug),
            "order": order,
            "listed": order is not None and slug != "home",
            "metaTitle": velden.get("metatitle") or None,
            "metaDescription": velden.get("metadescription") or velden.get("description") or None,
            "blocks": blokken,
        }
        fm = {k: v for k, v in fm.items() if v is not None}
        tekst = "---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n"
        (doel / "index.md").write_text(tekst, encoding="utf-8")
        totaal_fotos += len(fotos.gekopieerd)
        print(f"{slug}: {len(blokken)} blokken, {len(fotos.gekopieerd)} foto's ({', '.join(b['type'] for b in blokken)})")

    # Site-gegevens
    s = lees_txt(content / "site.txt")
    site = {
        "naam": re.sub(r"\s+-?\s*", " ", s.get("sitename") or s.get("title", "")).strip(),
        "titel": s.get("title", ""),
        "omschrijving": s.get("description", ""),
        "email": "info@annemiekmaissan.nl",
        "links": [
            {"label": label, "url": s.get(sleutel)}
            for sleutel, label in (("linkedin", "LinkedIn"), ("youtube", "YouTube"), ("facebook", "Facebook"), ("instagram", "Instagram"))
            if s.get(sleutel)
        ],
    }
    UIT_DATA.mkdir(parents=True, exist_ok=True)
    (UIT_DATA / "site.json").write_text(json.dumps(site, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"site.json geschreven; {totaal_fotos} foto's in totaal")
    if "sadfj" in s.get("footertext", ""):
        print("  ! footertekst in Kirby is opvultekst; niet overgenomen")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(Path(sys.argv[1]))
