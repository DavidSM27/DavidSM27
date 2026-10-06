"""Genera info-card.svg, una tarjeta estilo neofetch.

Uso:  python scripts/make_info_card.py
      $env:STATIC = "1"   # (PowerShell) imagen fija sin animacion
Edita la seccion CONFIG con tus datos.
"""
import os
import textwrap
from html import escape
from pathlib import Path

# ---------------- CONFIG: edita esto ----------------
USER = "DavidSM27"
HOST = "github"
ROWS = [
    ("Now", "Tu puesto actual @ Tu empresa"),
    ("Prev", "Tu puesto anterior @ Otra empresa"),
    ("Stack", "Python, JavaScript, SQL, Git, Docker"),
    ("Highlights", "Un proyecto o logro que quieras destacar; otro mas aqui"),
    ("Location", "Madrid, Espana"),
]
# ----------------------------------------------------

OUT = Path("info-card.svg")
STATIC = os.environ.get("STATIC") == "1"
W, MIN_H = 490, 360
KEY_X, VAL_X = 28, 130
WRAP = 42
LINE_H = 21
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
COLORS = {"title": "#7ee787", "key": "#79c0ff", "val": "#c9d1d9", "dim": "#8b949e"}
SWATCH = ["#ff7b72", "#ffa657", "#e3b341", "#7ee787", "#79c0ff", "#d2a8ff"]


def build():
    els = []  # (svg_fragment)
    y = 92
    delay = 0.3
    step = 0.18

    def add(frag):
        nonlocal delay
        els.append(f'<g class="ln" style="animation-delay:{delay:.2f}s">{frag}</g>')
        delay += step

    head = f"{USER}@{HOST}"
    add(f'<text x="{KEY_X}" y="{y}" font-size="15" font-weight="bold" fill="{COLORS["title"]}">{escape(head)}</text>')
    y += 8
    add(f'<text x="{KEY_X}" y="{y + 8}" font-size="13" fill="{COLORS["dim"]}">{"-" * len(head)}</text>')
    y += 28

    for key, val in ROWS:
        lines = textwrap.wrap(val, WRAP) or [""]
        frag = f'<text x="{KEY_X}" y="{y}" font-size="13" font-weight="bold" fill="{COLORS["key"]}">{escape(key)}</text>'
        for j, ln in enumerate(lines):
            frag += (f'<text x="{VAL_X}" y="{y + j * LINE_H}" font-size="13" '
                     f'fill="{COLORS["val"]}">{escape(ln)}</text>')
        add(frag)
        y += len(lines) * LINE_H + 6

    y += 10
    sw = "".join(f'<rect x="{KEY_X + i * 26}" y="{y}" width="22" height="14" rx="3" fill="{c}"/>'
                 for i, c in enumerate(SWATCH))
    add(sw)
    y += 14

    height = max(MIN_H, y + 28)
    css = ("@keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:translateX(0)}}"
           + (".ln{opacity:1}" if STATIC else ".ln{opacity:0;animation:in .4s ease-out forwards}"))
    bar = (f'<rect width="{W}" height="36" rx="10" fill="#161b22"/>'
           f'<rect y="26" width="{W}" height="10" fill="#161b22"/>'
           '<circle cx="22" cy="18" r="6" fill="#ff5f56"/>'
           '<circle cx="42" cy="18" r="6" fill="#ffbd2e"/>'
           '<circle cx="62" cy="18" r="6" fill="#27c93f"/>'
           f'<text x="{W / 2}" y="22" font-size="12" text-anchor="middle" fill="{COLORS["dim"]}">'
           f'{escape(USER)}@{HOST}: ~</text>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" width="{W}" height="{height}" '
           f'font-family="{FONT}">'
           f'<style>{css}</style>'
           f'<rect width="{W}" height="{height}" rx="10" fill="#0d1117" stroke="#30363d"/>'
           f'{bar}{"".join(els)}</svg>')
    return svg


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print(f"Listo: {OUT}" + (" (estatico)" if STATIC else ""))