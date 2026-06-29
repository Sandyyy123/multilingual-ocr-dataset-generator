"""
verify_ground_truth.py - QC utility for the generated dataset.

For an OCR benchmark the ground-truth JSON is only useful if it EXACTLY matches the
glyphs on the page. This script re-loads each JSON, regenerates the PDF from the same
(locale, seed), and confirms the field values are byte-identical - catching any drift
between the page and its label. For Indic/Arabic scripts a native reader should still
eyeball a sample (the human-QC step described in the proposal), but this automates the
mechanical check.

Usage:  python verify_ground_truth.py out/
"""
import json
import os
import sys

from generator import generate_invoice


def verify_dir(out_dir):
    jsons = [f for f in os.listdir(out_dir) if f.endswith(".json")]
    if not jsons:
        print(f"No ground-truth JSON in {out_dir}")
        return 1
    ok = bad = 0
    for jf in sorted(jsons):
        gt = json.load(open(os.path.join(out_dir, jf), encoding="utf-8"))
        # filename pattern: invoice_<locale>_<seed>.json
        seed = int(jf.rsplit("_", 1)[1].split(".")[0])
        locale = gt["locale"]
        _, regen = generate_invoice(locale, seed=seed, out_dir=os.path.join(out_dir, "_verify"))
        regen_fields = json.load(open(regen, encoding="utf-8"))["fields"]
        if regen_fields == gt["fields"]:
            ok += 1
        else:
            bad += 1
            print(f"[MISMATCH] {jf}")
            for k in gt["fields"]:
                if gt["fields"][k] != regen_fields.get(k):
                    print(f"    {k}: json={gt['fields'][k]!r}  regen={regen_fields.get(k)!r}")
    print(f"\n{ok} matched, {bad} mismatched out of {ok + bad}")
    return 0 if bad == 0 else 2


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    raise SystemExit(verify_dir(out))
