# Multilingual OCR Test-Dataset Generator

A `faker` + `reportlab` pipeline that generates realistic synthetic documents in **30+
locales across 15 scripts**, each paired with an exact-match **ground-truth JSON** for
OCR accuracy scoring, plus a **scan-degradation** stage that produces 3 image variants
per document. Right-to-left scripts (Arabic, Hebrew, Urdu) are shaped correctly.

Built as a working reference for multilingual document-AI benchmark datasets. Every
page carries a `SAMPLE - TEST DATA` watermark and uses only synthetic `faker`/lexicon
data - no real personal, financial, or medical content.

---

## What it does

```
locale ──► faker / native lexicon ──► reportlab PDF ──► ground-truth JSON
                                            │
                                            └──► pdf2image + Pillow ──► 3 degraded JPGs
```

1. **Field values** come from `faker` in the native locale where faker has data
   (Hindi, Tamil, Japanese, Chinese, Arabic, Hebrew, Thai, Russian, ...). For scripts
   faker does **not** cover (Bengali, Telugu, Kannada, Malayalam, Punjabi, Gujarati,
   Odia), values come from a bundled **native-script lexicon** so the script font
   always renders real glyphs instead of `.notdef` boxes.
2. **PDF rendering** uses the correct Noto font per script. English field labels are
   drawn in a Latin font; localized values in the script font (Indic/Arabic Noto fonts
   carry no Latin glyphs, so a single font would drop one or the other).
3. **RTL** (Arabic, Hebrew, Urdu) is reshaped with `arabic_reshaper` + `python-bidi`
   and right-aligned.
4. **Ground truth** JSON holds the exact field values drawn, keyed by field name, so
   OCR output can be scored field-by-field. Generation is seeded → reproducible.
5. **Scan degradation** renders the PDF and emits 3 variants (`clean_scan`,
   `office_copier`, `phone_photo`) with DPI drop, rotation, blur, JPEG artefacts and
   speckle.

---

## Languages & scripts covered

| Region | Locales | Script handling |
|---|---|---|
| Europe | en, fr, de, it, es, pt, nl, pl, ro, cs, sv, no | Latin (faker) |
| Europe | ru, uk | Cyrillic (faker) |
| Latin America | es_MX, es_AR, es_CO, pt_BR | Latin (faker) |
| India | **hi, mr** (Devanagari), **bn**, **ta**, **te**, **kn**, **ml**, **pa** (Gurmukhi), **gu**, **or**, **ur** | 9 distinct scripts — faker where available, lexicon otherwise |
| China & Japan | zh_CN, zh_TW, ja_JP | CJK (needs `fonts-noto-cjk`) |
| Supplementary | ar, he, th | Arabic/Hebrew (RTL), Thai |

---

## Quick start

```bash
pip install -r requirements.txt
# system deps:
sudo apt-get install poppler-utils fonts-noto fonts-noto-cjk

# one Hindi invoice + ground-truth JSON
python main.py --locales hi_IN --out out

# the hard Indic scripts + RTL, with 3 degraded images each
python main.py --locales hi_IN ta_IN te_IN ml_IN kn_IN pa_IN gu_IN or_IN ar_SA he_IL --degrade --out out

# everything in scope, one doc each
python main.py --all --out out

# QC: confirm every ground-truth JSON still matches its regenerated page
python verify_ground_truth.py out
```

Example ground-truth JSON (`invoice_hi_IN_0001.json`):

```json
{
  "locale": "hi_IN",
  "doc_type": "invoice",
  "script": "NotoSansDevanagari-Regular",
  "rtl": false,
  "text_source": "faker",
  "fields": {
    "invoice_no": "INV-27611",
    "date": "2002-02-26",
    "seller_name": "बोस",
    "buyer_name": "संमानित एषा झादव",
    "buyer_address": "706 त्रिवेदी, धारवाड-439150",
    "subtotal": "465.03", "tax": "675.69", "total": "260.48"
  }
}
```

---

## Files

| File | Role |
|---|---|
| `main.py` | CLI entry point — locale selection, batch count, degradation toggle |
| `generator.py` | invoice generation: faker/lexicon → reportlab PDF + ground-truth JSON |
| `fonts.py` | locale → script → Noto font mapping & registration; RTL flag |
| `lexicon.py` | native-script sample strings for the 7 scripts faker doesn't cover |
| `degrade.py` | scan-degradation pipeline (3 named profiles via pdf2image + Pillow) |
| `verify_ground_truth.py` | QC — regenerate & diff every JSON against its page |

---

## Scaling to the full benchmark

This reference implements the `invoice` document type. The same
`faker → reportlab → JSON → degrade` spine extends to the other 7 document types
(purchase order, contract, shipping, form, medical record, bank statement, immigration
form) by adding a layout function per type — field schemas and ground-truth emission
are unchanged. Running all locales × types × seeds × 3 degradation profiles produces
the full multi-thousand-image benchmark set.

For the Indic and other non-faker scripts, the bundled lexicon is the seed; in a
production run it is expanded per language and **reviewed by a native reader** so every
ground-truth label is confirmed correct against its glyphs.

---

*Synthetic test data only. No real personal, financial, or medical content. Not for
generating any real or government document.*
