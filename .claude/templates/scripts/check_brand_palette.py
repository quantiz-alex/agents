"""Verificação de regressão do extrator, sem arquivos temporários."""
import ast
import io
from pathlib import Path

from PIL import Image
from brand_palette import extract_primary


def main():
    root = Path(__file__).resolve().parents[1]
    for path in [root / "components-library.py", root / "scripts/brand_palette.py", root / "scripts/ui_smoke.py"]:
        ast.parse(path.read_text(encoding="utf-8-sig"))
    for rgba, expected in [
        ((180, 30, 60, 255), "#B41E3C"),
        ((255, 0, 0, 255), "#FF0000"),
        ((255, 255, 255, 255), None),
        ((180, 30, 60, 0), None),
    ]:
        stream = io.BytesIO()
        Image.new("RGBA", (40, 40), rgba).save(stream, format="PNG")
        stream.seek(0)
        assert extract_primary(stream)["primary"] == expected
    print("OK: sintaxe de 3 arquivos; 4 casos de extração da paleta")


if __name__ == "__main__":
    main()
