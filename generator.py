"""
generator.py - synthetic multilingual document generator.

Produces a realistic fake document (currently the `invoice` type) in ANY supported
locale using faker for the field values and reportlab for the PDF. Every PDF is
paired with a ground-truth JSON holding the EXACT field values drawn, so OCR output
can be scored field-by-field. RTL locales (Arabic, Hebrew, Urdu) are shaped with
arabic_reshaper + python-bidi before drawing so the glyphs join and order correctly.

A 'SAMPLE - TEST DATA' watermark is stamped on every page (client requirement). No
real personal/financial/medical data is ever used - everything comes from faker.
"""
import json
import os
import random

from faker import Faker
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from fonts import font_for_locale, is_rtl, latin_font, LOCALE_SCRIPT
import lexicon

# Optional RTL shaping. If the libs are absent we degrade loudly (see _shape).
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    _RTL_OK = True
except ImportError:  # pragma: no cover - environment dependent
    _RTL_OK = False

PAGE_W, PAGE_H = A4

# faker uses its own locale tags; a few of ours need remapping or fall back to a
# parent locale (faker has no data for e.g. Odia, so we still draw the script using
# a transliteration-free fallback: numbers/dates render fine, names use en_US).
_FAKER_LOCALE = {
    "en_GB": "en_GB", "fr_FR": "fr_FR", "de_DE": "de_DE", "it_IT": "it_IT",
    "es_ES": "es_ES", "pt_PT": "pt_PT", "nl_NL": "nl_NL", "pl_PL": "pl_PL",
    "ro_RO": "ro_RO", "cs_CZ": "cs_CZ", "sv_SE": "sv_SE", "no_NO": "no_NO",
    "ru_RU": "ru_RU", "uk_UA": "uk_UA", "es_MX": "es_MX", "es_AR": "es_AR",
    "es_CO": "es_CO", "pt_BR": "pt_BR", "hi_IN": "hi_IN", "bn_IN": "bn_IN",
    "ta_IN": "ta_IN", "zh_CN": "zh_CN", "zh_TW": "zh_TW", "ja_JP": "ja_JP",
    "ar_SA": "ar_AA", "he_IL": "he_IL", "th_TH": "th_TH",
}


def _faker(locale):
    """Return (faker, covered). `covered` is False when faker has no data for the
    locale and we fell back to en_US - the caller then sources native text from the
    lexicon so the script font is exercised with real glyphs instead of tofu."""
    want = _FAKER_LOCALE.get(locale, "en_US")
    try:
        return Faker(want), (want != "en_US")
    except (AttributeError, KeyError):
        return Faker("en_US"), False


def _shape(text, locale):
    """Reorder/join RTL text for correct visual rendering. LTR text is returned as-is."""
    if not is_rtl(locale):
        return text
    if not _RTL_OK:
        raise RuntimeError(
            "RTL locale requested but arabic_reshaper / python-bidi not installed. "
            "Run: pip install arabic-reshaper python-bidi"
        )
    return get_display(arabic_reshaper.reshape(text))


def _watermark(c, font):
    # Always Latin font - the watermark text is English and Indic/Arabic fonts
    # lack Latin glyphs (would render blank otherwise).
    c.saveState()
    c.setFont(font, 46)
    c.setFillGray(0.80)
    c.translate(PAGE_W / 2, PAGE_H / 2)
    c.rotate(45)
    c.drawCentredString(0, 0, "SAMPLE - TEST DATA")
    c.restoreState()


def generate_invoice(locale, seed, out_dir):
    """Generate one invoice PDF + matching ground-truth JSON for `locale`.

    Returns (pdf_path, json_path). `seed` makes the draw reproducible so the JSON
    always matches the PDF for the same (locale, seed)."""
    os.makedirs(out_dir, exist_ok=True)
    fake, covered = _faker(locale)
    fake.seed_instance(seed)
    Faker.seed(seed)
    rng = random.Random(seed)
    font = font_for_locale(locale)
    lat = latin_font()
    rtl = is_rtl(locale)
    script = LOCALE_SCRIPT.get(locale, "latin")

    # For scripts faker does not cover, draw the text fields from the native lexicon
    # so the script font renders real glyphs (not English-in-an-Indic-font tofu).
    use_lex = (not covered) and lexicon.has(script)

    def company():
        return lexicon.pick(script, "companies", rng) if use_lex else fake.company()

    def person():
        return lexicon.pick(script, "names", rng) if use_lex else fake.name()

    def address():
        if use_lex:
            return f"{rng.randint(1, 999)} {lexicon.pick(script, 'cities', rng)}"
        return fake.address().replace("\n", ", ")

    # --- ground truth: the EXACT values that go on the page ---
    gt = {
        "locale": locale,
        "doc_type": "invoice",
        "script": font,
        "rtl": rtl,
        "text_source": "lexicon" if use_lex else "faker",
        "fields": {
            "invoice_no": f"INV-{fake.random_int(10000, 99999)}",
            "date": fake.date(),
            "seller_name": company(),
            "buyer_name": person(),
            "buyer_address": address(),
            "subtotal": f"{fake.random_int(100, 9000)}.{fake.random_int(0, 99):02d}",
            "tax": f"{fake.random_int(10, 900)}.{fake.random_int(0, 99):02d}",
            "total": f"{fake.random_int(110, 9900)}.{fake.random_int(0, 99):02d}",
        },
    }
    f = gt["fields"]

    base = f"invoice_{locale}_{seed:04d}"
    pdf_path = os.path.join(out_dir, base + ".pdf")
    json_path = os.path.join(out_dir, base + ".json")

    c = canvas.Canvas(pdf_path, pagesize=A4)
    _watermark(c, lat)

    def field_row(key, value, y, size=12):
        """Draw an English label (Latin font) + a localized value (script font).
        Indic/Arabic Noto fonts lack Latin glyphs, so label and value need different
        fonts. RTL values are shaped and the row mirrors to the right margin."""
        label = f"{key}: "
        val = _shape(str(value), locale)
        if rtl:
            # label on the right, value flows leftward from it
            x = PAGE_W - 25 * mm
            c.setFont(lat, size)
            c.drawRightString(x, y, label)
            x -= c.stringWidth(label, lat, size)
            c.setFont(font, size)
            c.drawRightString(x, y, val)
        else:
            x = 25 * mm
            c.setFont(lat, size)
            c.drawString(x, y, label)
            x += c.stringWidth(label, lat, size)
            c.setFont(font, size)
            c.drawString(x, y, val)

    c.setFont(lat, 20)
    if rtl:
        c.drawRightString(PAGE_W - 25 * mm, PAGE_H - 30 * mm, "INVOICE")
    else:
        c.drawString(25 * mm, PAGE_H - 30 * mm, "INVOICE")

    y = PAGE_H - 50 * mm
    for key in ("invoice_no", "date", "seller_name", "buyer_name",
                "buyer_address", "subtotal", "tax", "total"):
        field_row(key, f[key], y)
        y -= 12 * mm

    c.showPage()
    c.save()

    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(gt, fh, ensure_ascii=False, indent=2)

    return pdf_path, json_path
