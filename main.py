"""
main.py - CLI entry point for the multilingual OCR test-dataset generator.

Examples
--------
# One Hindi invoice + ground-truth JSON:
    python main.py --locales hi_IN --out out

# A multilingual batch with scan-degradation (3 image variants each):
    python main.py --locales hi_IN ar_SA ta_IN de_DE --per-locale 2 --degrade --out out

# Everything in scope, one doc each:
    python main.py --all --out out
"""
import argparse
import os
import sys

from fonts import LOCALE_SCRIPT
from generator import generate_invoice

ALL_LOCALES = list(LOCALE_SCRIPT.keys())


def main(argv=None):
    ap = argparse.ArgumentParser(description="Synthetic multilingual OCR document generator")
    ap.add_argument("--locales", nargs="+", help="locale codes, e.g. hi_IN ar_SA de_DE")
    ap.add_argument("--all", action="store_true", help="generate for every supported locale")
    ap.add_argument("--per-locale", type=int, default=1, help="documents per locale")
    ap.add_argument("--degrade", action="store_true", help="also emit 3 scan-degraded image variants")
    ap.add_argument("--out", default="out", help="output directory")
    args = ap.parse_args(argv)

    locales = ALL_LOCALES if args.all else (args.locales or ["en_US"])
    bad = [l for l in locales if l not in LOCALE_SCRIPT]
    if bad:
        ap.error(f"unsupported locale(s): {bad}. Supported: {ALL_LOCALES}")

    made_pdfs = made_imgs = 0
    for locale in locales:
        for i in range(args.per_locale):
            try:
                pdf, js = generate_invoice(locale, seed=i + 1, out_dir=args.out)
            except FileNotFoundError as e:
                print(f"[SKIP] {locale}: {e}", file=sys.stderr)
                continue
            made_pdfs += 1
            print(f"[OK] {os.path.basename(pdf)}  +  {os.path.basename(js)}")
            if args.degrade:
                from degrade import degrade_pdf  # lazy: only needs poppler if used
                imgs = degrade_pdf(pdf, out_dir=os.path.join(args.out, "images"), seed=i + 1)
                made_imgs += len(imgs)
                for im in imgs:
                    print(f"       -> {os.path.basename(im)}")

    print(f"\nDone. {made_pdfs} PDF(+JSON) pairs, {made_imgs} degraded images -> {args.out}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
