from __future__ import annotations


CATALOG = {
    "en": {
        "processed": "Document processed successfully. You can now ask questions.",
        "not_found": "Not enough information in the uploaded document.",
        "upload": "Upload",
        "ask": "Ask",
    },
    "hi": {
        "processed": "दस्तावेज सफलतापूर्वक संसाधित हुआ। अब आप प्रश्न पूछ सकते हैं।",
        "not_found": "अपलोड किए गए दस्तावेज में पर्याप्त जानकारी नहीं है।",
        "upload": "अपलोड",
        "ask": "पूछें",
    },
    "te": {
        "processed": "పత్రం విజయవంతంగా ప్రాసెస్ అయింది. ఇప్పుడు మీరు ప్రశ్నలు అడగవచ్చు.",
        "not_found": "అప్లోడ్ చేసిన పత్రంలో సరిపడ సమాచారం లేదు.",
        "upload": "అప్లోడ్",
        "ask": "అడగండి",
    },
}


def translate(key: str, language: str = "en") -> str:
    return CATALOG.get(language, CATALOG["en"]).get(key, CATALOG["en"].get(key, key))
