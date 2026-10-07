"""Sugere a cor da marca a partir do logo: python scripts/brand_palette.py assets/logo.png.

Pillow é dependência de build, não precisa integrar requirements de produção.
A saída é JSON; não altera o logo nem arquivos do projeto.
"""
from __future__ import annotations

import argparse
import colorsys
import json


def extract_primary(path: str) -> dict:
    from PIL import Image

    with Image.open(path) as source:
        image = source.convert("RGBA")
        image.thumbnail((160, 160))
        pixels = []
        for r, g, b, alpha in image.getdata():
            if alpha < 200:
                continue
            _, saturation, value = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if saturation >= 0.25 and value >= 0.15:
                pixels.append((r, g, b))
        if not pixels:
            return {"primary": None, "source": "logo", "warning": "Logo neutro ou sem cor utilizável; informar primary explicitamente."}
        strip = Image.new("RGB", (len(pixels), 1))
        strip.putdata(pixels)
        palette = strip.quantize(colors=8)
        count, index = max(palette.getcolors(), key=lambda item: item[0])
        rgb = palette.getpalette()[index * 3:index * 3 + 3]
        return {"primary": "#{:02X}{:02X}{:02X}".format(*rgb), "source": "logo",
                "dominant_share": round(count / len(pixels), 3),
                "warning": "Cor estimada do arquivo, não confirmação da identidade oficial."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logo")
    args = parser.parse_args()
    print(json.dumps(extract_primary(args.logo), ensure_ascii=False, indent=2))
