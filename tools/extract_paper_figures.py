"""Render the cited PDF regions. Run with: uv run --with pymupdf python tools/extract_paper_figures.py /tmp/video-foundations-papers"""

import hashlib
import json
from pathlib import Path
import sys

import pymupdf


PAPERS = {
    "ddpm": "2006.11239v2",
    "transformer": "1706.03762v7",
    "ldm": "2112.10752v2",
    "dit": "2212.09748v2",
    "hunyuan": "2412.03603v1",
    "wan": "2503.20314v1",
}

# PDF page numbers are one-based; crop coordinates are points from the top left.
FIGURES = [
    ("ddpm", 2, "fig2", (105, 52, 506, 122)),
    ("ddpm", 4, "algorithms", (105, 82, 506, 178)),
    ("transformer", 3, "fig1", (185, 47, 430, 402)),
    ("transformer", 4, "fig2", (125, 45, 500, 273)),
    ("ldm", 4, "fig3", (303, 47, 550, 197)),
    ("dit", 3, "fig3", (45, 47, 563, 279)),
    ("hunyuan", 5, "fig5", (105, 66, 509, 242)),
    ("hunyuan", 6, "fig6", (105, 69, 509, 151)),
    ("hunyuan", 7, "fig8", (105, 306, 509, 516)),
    ("hunyuan", 9, "fig9", (105, 70, 509, 217)),
    ("wan", 10, "fig5", (100, 319, 514, 426)),
    ("wan", 11, "fig6", (100, 79, 514, 194)),
    ("wan", 13, "fig9", (100, 390, 514, 524)),
    ("wan", 14, "fig10", (345, 142, 514, 334)),
]


def main():
    source_dir = Path(sys.argv[1])
    output = Path(__file__).resolve().parents[1] / "docs/assets/video_generation"
    output.mkdir(parents=True, exist_ok=True)
    manifest = []
    pymupdf.TOOLS.mupdf_display_errors(False)
    for name, page_number, figure, bounds in FIGURES:
        path = source_dir / f"{name}.pdf"
        with pymupdf.open(path) as document:
            page = document[page_number - 1]
            pixmap = page.get_pixmap(
                matrix=pymupdf.Matrix(3, 3),
                clip=pymupdf.Rect(bounds),
                alpha=False,
                annots=False,
            )
            filename = f"{name}_{figure}.png"
            pixmap.save(output / filename)
        manifest.append({
            "file": filename,
            "source": f"https://arxiv.org/pdf/{PAPERS[name]}",
            "pdf_page": page_number,
            "figure": figure,
            "crop_points": bounds,
            "scale": 3,
            "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "retrieved": "2026-09-10",
            "kind": "paper_screenshot",
        })
        print(f"{filename}: {pixmap.width} x {pixmap.height}")
    (output / "paper_figures.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
