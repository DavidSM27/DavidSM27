"""Prepara la foto para convertirla en ASCII: quita fondo, sube contraste, fondo blanco.

Uso:  python scripts/prep_photo.py foto.png
Salida: source-prepped.png (escala de grises)
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

OUT = Path("source-prepped.png")


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("foto.png")
    if not src.exists():
        sys.exit(f"No encuentro la foto: {src}")

    img = Image.open(src).convert("RGB")

    # 1) Quitar el fondo (si rembg no esta instalado, se usa la foto entera)
    try:
        from rembg import remove

        cut = remove(img).convert("RGBA")
    except ImportError:
        print("Aviso: rembg no esta instalado, no se quita el fondo.")
        cut = img.convert("RGBA")

    arr = np.array(cut)
    alpha = arr[:, :, 3].astype(np.float32) / 255.0

    # 2) Contraste local con CLAHE
    gray = cv2.cvtColor(arr[:, :, :3], cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray).astype(np.float32)

    # 3) Componer sobre blanco puro
    out = gray * alpha + 255.0 * (1.0 - alpha)
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "L").save(OUT)
    print(f"Listo: {OUT}")


if __name__ == "__main__":
    main()