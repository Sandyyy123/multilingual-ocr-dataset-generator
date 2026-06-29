"""
degrade.py - scan-degradation pipeline.

Turns a clean PDF into N realistic "scanned" image variants so the OCR benchmark
sees the kind of noise real documents have: lower DPI, JPEG artefacts, slight
rotation, blur and salt-and-pepper speckle. Each variant is written as a separate
image so M3 produces ~3 images per document.
"""
import os

from pdf2image import convert_from_path
from PIL import Image, ImageFilter
import random


def _add_noise(img, amount=0.02):
    px = img.load()
    w, h = img.size
    n = int(w * h * amount)
    for _ in range(n):
        x, y = random.randint(0, w - 1), random.randint(0, h - 1)
        px[x, y] = (0, 0, 0) if random.random() < 0.5 else (255, 255, 255)
    return img


# Three named degradation profiles -> 3 variants per document.
PROFILES = {
    "clean_scan":   dict(dpi=200, rotate=0.0, blur=0.0, noise=0.0,   quality=92),
    "office_copier": dict(dpi=150, rotate=0.4, blur=0.6, noise=0.01, quality=70),
    "phone_photo":  dict(dpi=120, rotate=1.2, blur=1.0, noise=0.025, quality=55),
}


def degrade_pdf(pdf_path, out_dir, seed=0):
    """Render `pdf_path` and emit one image per profile. Returns list of image paths."""
    os.makedirs(out_dir, exist_ok=True)
    random.seed(seed)
    base = os.path.splitext(os.path.basename(pdf_path))[0]
    paths = []
    for name, p in PROFILES.items():
        pages = convert_from_path(pdf_path, dpi=p["dpi"])
        img = pages[0].convert("RGB")
        if p["rotate"]:
            img = img.rotate(random.uniform(-p["rotate"], p["rotate"]),
                             expand=False, fillcolor=(255, 255, 255))
        if p["blur"]:
            img = img.filter(ImageFilter.GaussianBlur(p["blur"]))
        if p["noise"]:
            img = _add_noise(img, p["noise"])
        out = os.path.join(out_dir, f"{base}__{name}.jpg")
        img.save(out, "JPEG", quality=p["quality"])
        paths.append(out)
    return paths
