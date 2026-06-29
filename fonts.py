"""
fonts.py - locale -> font mapping and registration for multilingual PDF generation.

Maps every in-scope locale/script to a Unicode font that actually shapes the glyphs
correctly. Latin, Cyrillic, CJK, Indic (9 scripts), Arabic, Hebrew and Thai are all
covered. Fonts are registered once with reportlab's pdfmetrics on first use.

The font files used here are the freely-licensed Noto family (SIL OFL), which ships
on most Linux distros under /usr/share/fonts/truetype/noto. If a font is missing the
caller is told explicitly rather than silently rendering tofu (.notdef boxes).
"""
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Common Noto locations across distros.
_FONT_DIRS = [
    "/usr/share/fonts/truetype/noto",
    "/usr/share/fonts/noto",
    "/usr/share/fonts/opentype/noto",
    "/Library/Fonts",
    "C:/Windows/Fonts",
]

# Script -> candidate Noto font files (first one found wins). One regular weight per
# script is enough for ground-truth generation; the OCR target is the text, not the
# typeface. CJK ships under several names across distros, so we list the common ones.
_SCRIPT_FONT = {
    "latin":      ["NotoSans-Regular.ttf"],
    "cyrillic":   ["NotoSans-Regular.ttf"],   # Noto Sans covers Cyrillic too
    "devanagari": ["NotoSansDevanagari-Regular.ttf"],   # Hindi, Marathi
    "bengali":    ["NotoSansBengali-Regular.ttf"],
    "tamil":      ["NotoSansTamil-Regular.ttf"],
    "telugu":     ["NotoSansTelugu-Regular.ttf"],
    "kannada":    ["NotoSansKannada-Regular.ttf"],
    "malayalam":  ["NotoSansMalayalam-Regular.ttf"],
    "gurmukhi":   ["NotoSansGurmukhi-Regular.ttf"],      # Punjabi
    "gujarati":   ["NotoSansGujarati-Regular.ttf"],
    "odia":       ["NotoSansOriya-Regular.ttf"],
    "arabic":     ["NotoNaskhArabic-Regular.ttf"],       # Arabic, Urdu
    "hebrew":     ["NotoSansHebrew-Regular.ttf"],
    "thai":       ["NotoSansThai-Regular.ttf"],
    "cjk":        ["NotoSansCJK-Regular.ttc", "NotoSansCJKsc-Regular.otf",
                   "NotoSansSC-Regular.otf", "NotoSansSC-Regular.ttf",
                   "NotoSansJP-Regular.otf", "NotoSerifCJK-Regular.ttc"],
}

# Locale code -> script. Drives both the font and the RTL decision.
LOCALE_SCRIPT = {
    # Europe (Latin / Cyrillic)
    "en_US": "latin", "en_GB": "latin", "fr_FR": "latin", "de_DE": "latin",
    "it_IT": "latin", "es_ES": "latin", "pt_PT": "latin", "nl_NL": "latin",
    "pl_PL": "latin", "ro_RO": "latin", "cs_CZ": "latin", "sv_SE": "latin",
    "no_NO": "latin", "ru_RU": "cyrillic", "uk_UA": "cyrillic",
    # Latin America
    "es_MX": "latin", "es_AR": "latin", "es_CO": "latin", "pt_BR": "latin",
    # India - 9 distinct scripts
    "hi_IN": "devanagari", "mr_IN": "devanagari", "bn_IN": "bengali",
    "ta_IN": "tamil", "te_IN": "telugu", "kn_IN": "kannada",
    "ml_IN": "malayalam", "pa_IN": "gurmukhi", "gu_IN": "gujarati",
    "or_IN": "odia", "ur_IN": "arabic",
    # China & Japan
    "zh_CN": "cjk", "zh_TW": "cjk", "ja_JP": "cjk",
    # Supplementary
    "ar_SA": "arabic", "he_IL": "hebrew", "th_TH": "thai",
}

# Scripts that render right-to-left.
RTL_SCRIPTS = {"arabic", "hebrew"}

_registered = {}  # font_name -> bool


def _find_font_file(candidates):
    # also look in a repo-local fonts/ dir so the client can vendor fonts if needed
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
    for filename in candidates:
        for d in [here] + _FONT_DIRS:
            path = os.path.join(d, filename)
            if os.path.exists(path):
                return path
    return None


def font_for_locale(locale):
    """Return a registered reportlab font name for the locale, or raise with a clear
    message naming the missing font file so the operator can install it."""
    script = LOCALE_SCRIPT.get(locale, "latin")
    candidates = _SCRIPT_FONT[script]
    font_name = os.path.splitext(candidates[0])[0]

    if _registered.get(font_name):
        return font_name

    path = _find_font_file(candidates)
    if not path:
        raise FileNotFoundError(
            f"No font for script '{script}' (locale {locale}). Tried {candidates}. "
            f"Install Noto fonts (e.g. `apt-get install fonts-noto fonts-noto-cjk`) "
            f"or drop a .ttf/.otf into one of: {_FONT_DIRS}"
        )
    # .ttc collections need a subfont index.
    if path.endswith(".ttc"):
        pdfmetrics.registerFont(TTFont(font_name, path, subfontIndex=0))
    else:
        pdfmetrics.registerFont(TTFont(font_name, path))
    _registered[font_name] = True
    return font_name


def latin_font():
    """A Latin/ASCII-capable font for field labels (which are English in this schema).
    Indic/Arabic Noto fonts do NOT carry Latin glyphs, so labels must use this."""
    return font_for_locale("en_US")


def is_rtl(locale):
    return LOCALE_SCRIPT.get(locale, "latin") in RTL_SCRIPTS
