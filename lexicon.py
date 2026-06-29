"""
lexicon.py - native-script sample strings for scripts faker does not cover.

faker only ships data for a handful of our locales (hi_IN, ja_JP, zh_CN, ar, he_IL,
th_TH, ru_RU, ...). For the rest - Bengali, Tamil, Telugu, Kannada, Malayalam,
Gurmukhi/Punjabi, Gujarati, Odia and others - faker falls back to English, which would
render as .notdef boxes in the script font. This module supplies a small, correct
native-script lexicon so EVERY in-scope script is exercised with real glyphs.

These are short, generic, non-personal sample tokens (common given names, a city, a
business word) - synthetic test data, no real individuals. In the production dataset
this list is expanded per language with native-writer review (the M4 QC step).
"""

# script -> {names: [...], companies: [...], cities: [...]}
LEXICON = {
    "devanagari": {  # Hindi / Marathi
        "names": ["आरव शर्मा", "प्रिया वर्मा", "रोहित कुमार", "अंजली सिंह"],
        "companies": ["भारत व्यापार लिमिटेड", "सूर्या उद्योग", "गंगा ट्रेडर्स"],
        "cities": ["नई दिल्ली", "मुंबई", "पुणे", "जयपुर"],
    },
    "bengali": {
        "names": ["অর্ণব দাস", "রিয়া ঘোষ", "সৌরভ রায়", "মিতা সেন"],
        "companies": ["বাংলা বাণিজ্য লিমিটেড", "পদ্মা শিল্প"],
        "cities": ["কলকাতা", "ঢাকা", "হাওড়া"],
    },
    "tamil": {
        "names": ["அருண் குமார்", "மீனா ராஜா", "கார்த்திக் வேல்"],
        "companies": ["தமிழ் வர்த்தகம் லிமிடெட்", "செந்தில் தொழில்"],
        "cities": ["சென்னை", "மதுரை", "கோயம்புத்தூர்"],
    },
    "telugu": {
        "names": ["రవి తేజ", "స్వాతి రెడ్డి", "కిరణ్ కుమార్"],
        "companies": ["ఆంధ్ర వాణిజ్యం లిమిటెడ్", "గోదావరి పరిశ్రమ"],
        "cities": ["హైదరాబాద్", "విజయవాడ", "విశాఖపట్నం"],
    },
    "kannada": {
        "names": ["ಅರ್ಜುನ್ ರಾವ್", "ಪ್ರಿಯಾ ಶೆಟ್ಟಿ", "ಸಂತೋಷ್ ಗೌಡ"],
        "companies": ["ಕನ್ನಡ ವಾಣಿಜ್ಯ ಲಿಮಿಟೆಡ್", "ಕಾವೇರಿ ಉದ್ಯಮ"],
        "cities": ["ಬೆಂಗಳೂರು", "ಮೈಸೂರು", "ಮಂಗಳೂರು"],
    },
    "malayalam": {
        "names": ["അരുൺ നായർ", "മീര മേനോൻ", "സജു തോമസ്"],
        "companies": ["കേരള വ്യാപാരം ലിമിറ്റഡ്", "നിള വ്യവസായം"],
        "cities": ["കൊച്ചി", "തിരുവനന്തപുരം", "കോഴിക്കോട്"],
    },
    "gurmukhi": {  # Punjabi
        "names": ["ਗੁਰਪ੍ਰੀਤ ਸਿੰਘ", "ਸਿਮਰਨ ਕੌਰ", "ਹਰਜੀਤ ਸਿੰਘ"],
        "companies": ["ਪੰਜਾਬ ਵਪਾਰ ਲਿਮਿਟੇਡ", "ਸਤਲੁਜ ਉਦਯੋਗ"],
        "cities": ["ਅੰਮ੍ਰਿਤਸਰ", "ਲੁਧਿਆਣਾ", "ਜਲੰਧਰ"],
    },
    "gujarati": {
        "names": ["રાજ પટેલ", "નેહા શાહ", "મિતેશ દેસાઈ"],
        "companies": ["ગુજરાત વેપાર લિમિટેડ", "નર્મદા ઉદ્યોગ"],
        "cities": ["અમદાવાદ", "સુરત", "વડોદરા"],
    },
    "odia": {
        "names": ["ସୁବ୍ରତ ସାହୁ", "ପ୍ରିୟଙ୍କା ଦାସ", "ମନୋଜ ପଟ୍ଟନାୟକ"],
        "companies": ["ଓଡ଼ିଶା ବାଣିଜ୍ୟ ଲିମିଟେଡ", "ମହାନଦୀ ଶିଳ୍ପ"],
        "cities": ["ଭୁବନେଶ୍ୱର", "କଟକ", "ପୁରୀ"],
    },
    "arabic": {  # Arabic / Urdu fallback
        "names": ["محمد علي", "فاطمة حسن", "أحمد خان"],
        "companies": ["شركة التجارة المحدودة", "مصنع النور"],
        "cities": ["الرياض", "دبي", "القاهرة"],
    },
    "hebrew": {
        "names": ["דוד כהן", "מיכל לוי", "יוסי מזרחי"],
        "companies": ["חברת המסחר בעמ", "תעשיות גליל"],
        "cities": ["תל אביב", "ירושלים", "חיפה"],
    },
    "thai": {
        "names": ["สมชาย ใจดี", "สุดา แสงทอง", "วิชัย พรหม"],
        "companies": ["บริษัท การค้า จำกัด", "อุตสาหกรรมแม่น้ำ"],
        "cities": ["กรุงเทพ", "เชียงใหม่", "ภูเก็ต"],
    },
}


def has(script):
    return script in LEXICON


def pick(script, kind, rng):
    """kind in {names, companies, cities}. rng is a seeded random.Random."""
    return rng.choice(LEXICON[script][kind])
