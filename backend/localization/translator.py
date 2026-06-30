from __future__ import annotations

LANGUAGE_NAMES = {
    "English": "en",
    "Hindi": "hi",
    "Telugu": "te",
}
LANGUAGE_LABELS = {value: key for key, value in LANGUAGE_NAMES.items()}
NATIVE_LANGUAGE_NAMES = {
    "en": "English",
    "hi": "हिन्दी",
    "te": "తెలుగు",
}
PLACEHOLDER_VALUES = {
    "not specified in document",
    "not specified",
    "not enough information in the uploaded document.",
    "this question is outside the scope of the uploaded document.",
}

CATALOG = {
    "en": {
        "app_title": "Yojana Mitra",
        "navigation": "Navigation",
        "welcome_title": "Welcome to Yojana Mitra",
        "welcome_body": ("Upload a scheme document, choose your language, and ask questions in plain language."),
        "settings_title": "Settings",
        "settings_language_home": "Language selection is available on the Home page.",
        "language": "Language",
        "choose_language": "Choose Your Language",
        "save_settings": "Save Settings",
        "settings_saved": "Language preference saved.",
        "chat_title": "Chat",
        "chat_tab": "Chat",
        "structured_data": "Structured Data",
        "structured_missing": "Structured data is not available for this document yet.",
        "offline_secure": "Offline • Local • Secure",
        "category": "Category",
        "source_file": "Source file",
        "benefits": "Benefits",
        "eligibility": "Eligibility",
        "required_documents": "Required Documents",
        "application_process": "Application Process",
        "not_specified_short": "Not specified in document",
        "document": "Document",
        "upload_first": "Upload and process a document before asking questions.",
        "type_message": "Type your message",
        "voice_message": "Voice message",
        "send": "Send",
        "recorded": "Audio recorded. Transcribing...",
        "transcribed": "Question added from voice input.",
        "voice_unavailable": "Voice input requires Streamlit 1.38 or newer.",
        "voice_failed": "Voice transcription failed",
        "empty_message": "Type a message or record your voice before sending.",
        "need_document": "Please upload and process a document first, then ask your question.",
        "searching": "Searching the document...",
        "processing_failed": "Sorry, I could not answer that because processing failed",
        "sources": "Sources",
        "page": "page",
        "upload_title": "Upload",
        "upload_body": "Upload one or more files to get started.",
        "choose_files": "Choose file(s)",
        "uploaded": "Uploaded {count} file(s) successfully.",
        "file_type": "Type",
        "file_size": "Size",
        "continue_processing": "Continue to Processing",
        "no_files": "No files uploaded yet.",
        "processing_title": "Processing",
        "no_files_found": "No files found. Please upload files first.",
        "go_upload": "Go to Upload",
        "processing_files": "Processing {count} file(s)...",
        "processing_file": "Processing: {name}",
        "process_failed": "Failed to process {name}",
        "check_logs": "Please check the application logs for details.",
        "processing_complete": "Processing complete!",
        "continue_chat": "Continue to Chat",
        "history_title": "History",
        "no_history": "No history yet. Start a chat to see your history here.",
        "you": "You",
        "assistant": "Assistant",
        "clear_history": "Clear History",
        "processed": "Document processed successfully. You can now ask questions.",
        "not_found": "Not enough information in the uploaded document.",
        "outside_scope": "This question is outside the scope of the uploaded document.",
        "upload": "Upload",
        "ask": "Ask",
        "home_upload": "Upload PDF/Image",
        "ask_question": "Ask your question",
    },
    "hi": {
        "app_title": "योजना मित्र",
        "navigation": "नेविगेशन",
        "welcome_title": "योजना मित्र में आपका स्वागत है",
        "welcome_body": "योजना दस्तावेज़ अपलोड करें, भाषा चुनें, और सरल भाषा में प्रश्न पूछें.",
        "settings_title": "सेटिंग्स",
        "settings_language_home": "भाषा चयन होम पेज पर उपलब्ध है.",
        "language": "भाषा",
        "choose_language": "अपनी भाषा चुनें",
        "save_settings": "सेटिंग्स सेव करें",
        "settings_saved": "भाषा सेटिंग सेव हो गई.",
        "chat_title": "चैट",
        "chat_tab": "चैट",
        "structured_data": "संरचित डेटा",
        "structured_missing": "इस दस्तावेज़ के लिए संरचित डेटा अभी उपलब्ध नहीं है.",
        "offline_secure": "ऑफलाइन • स्थानीय • सुरक्षित",
        "category": "श्रेणी",
        "source_file": "स्रोत फ़ाइल",
        "benefits": "लाभ",
        "eligibility": "पात्रता",
        "required_documents": "आवश्यक दस्तावेज़",
        "application_process": "आवेदन प्रक्रिया",
        "not_specified_short": "दस्तावेज़ में निर्दिष्ट नहीं",
        "document": "दस्तावेज़",
        "upload_first": "प्रश्न पूछने से पहले दस्तावेज़ अपलोड और प्रोसेस करें.",
        "type_message": "अपना संदेश लिखें",
        "voice_message": "वॉइस संदेश",
        "send": "भेजें",
        "recorded": "ऑडियो रिकॉर्ड हो गया. ट्रांसक्राइब हो रहा है...",
        "transcribed": "वॉइस इनपुट से प्रश्न जोड़ दिया गया.",
        "voice_unavailable": "वॉइस इनपुट के लिए Streamlit 1.38 या नया संस्करण चाहिए.",
        "voice_failed": "वॉइस ट्रांसक्रिप्शन विफल हुआ",
        "empty_message": "भेजने से पहले संदेश लिखें या आवाज रिकॉर्ड करें.",
        "need_document": "कृपया पहले दस्तावेज़ अपलोड और प्रोसेस करें, फिर प्रश्न पूछें.",
        "searching": "दस्तावेज़ में खोजा जा रहा है...",
        "processing_failed": "क्षमा करें, प्रोसेसिंग विफल होने के कारण उत्तर नहीं दे सका",
        "sources": "स्रोत",
        "page": "पृष्ठ",
        "upload_title": "अपलोड",
        "upload_body": "शुरू करने के लिए एक या अधिक फाइलें अपलोड करें.",
        "choose_files": "फाइल चुनें",
        "uploaded": "{count} फाइल सफलतापूर्वक अपलोड हुई.",
        "file_type": "प्रकार",
        "file_size": "आकार",
        "continue_processing": "प्रोसेसिंग पर जाएं",
        "no_files": "अभी कोई फाइल अपलोड नहीं हुई.",
        "processing_title": "प्रोसेसिंग",
        "no_files_found": "कोई फाइल नहीं मिली. कृपया पहले फाइल अपलोड करें.",
        "go_upload": "अपलोड पर जाएं",
        "processing_files": "{count} फाइल प्रोसेस हो रही है...",
        "processing_file": "प्रोसेसिंग: {name}",
        "process_failed": "{name} प्रोसेस नहीं हो सकी",
        "check_logs": "विवरण के लिए एप्लिकेशन लॉग देखें.",
        "processing_complete": "प्रोसेसिंग पूरी हुई!",
        "continue_chat": "चैट पर जाएं",
        "history_title": "इतिहास",
        "no_history": "अभी कोई इतिहास नहीं है. इतिहास देखने के लिए चैट शुरू करें.",
        "you": "आप",
        "assistant": "सहायक",
        "clear_history": "इतिहास साफ करें",
        "processed": "दस्तावेज़ सफलतापूर्वक प्रोसेस हो गया. अब आप प्रश्न पूछ सकते हैं.",
        "not_found": "अपलोड किए गए दस्तावेज़ में पर्याप्त जानकारी नहीं है.",
        "outside_scope": "यह प्रश्न अपलोड किए गए दस्तावेज़ के दायरे से बाहर है.",
        "upload": "अपलोड",
        "ask": "पूछें",
        "home_upload": "PDF/इमेज अपलोड करें",
        "ask_question": "अपना प्रश्न पूछें",
    },
    "te": {
        "app_title": "యోజన మిత్ర",
        "navigation": "నావిగేషన్",
        "welcome_title": "యోజన మిత్రకు స్వాగతం",
        "welcome_body": ("పథక పత్రాన్ని అప్లోడ్ చేయండి, భాషను ఎంచుకోండి, సులభమైన భాషలో ప్రశ్నలు అడగండి."),
        "settings_title": "సెట్టింగ్స్",
        "settings_language_home": "భాష ఎంపిక హోమ్ పేజీలో అందుబాటులో ఉంది.",
        "language": "భాష",
        "choose_language": "మీ భాషను ఎంచుకోండి",
        "save_settings": "సెట్టింగ్స్ సేవ్ చేయండి",
        "settings_saved": "భాషా ప్రాధాన్యత సేవ్ అయింది.",
        "chat_title": "చాట్",
        "chat_tab": "చాట్",
        "structured_data": "నిర్మిత డేటా",
        "structured_missing": "ఈ పత్రానికి నిర్మిత డేటా ఇంకా అందుబాటులో లేదు.",
        "offline_secure": "ఆఫ్‌లైన్ • స్థానికం • సురక్షితం",
        "category": "వర్గం",
        "source_file": "మూల ఫైల్",
        "benefits": "ప్రయోజనాలు",
        "eligibility": "అర్హత",
        "required_documents": "అవసరమైన పత్రాలు",
        "application_process": "దరఖాస్తు ప్రక్రియ",
        "not_specified_short": "పత్రంలో పేర్కొనలేదు",
        "document": "పత్రం",
        "upload_first": "ప్రశ్నలు అడగడానికి ముందు పత్రాన్ని అప్లోడ్ చేసి ప్రాసెస్ చేయండి.",
        "type_message": "మీ సందేశం టైప్ చేయండి",
        "voice_message": "వాయిస్ సందేశం",
        "send": "పంపండి",
        "recorded": "ఆడియో రికార్డ్ అయింది. ట్రాన్స్‌క్రైబ్ అవుతోంది...",
        "transcribed": "వాయిస్ ఇన్‌పుట్ నుంచి ప్రశ్న జోడించబడింది.",
        "voice_unavailable": "వాయిస్ ఇన్‌పుట్ కోసం Streamlit 1.38 లేదా కొత్త వెర్షన్ అవసరం.",
        "voice_failed": "వాయిస్ ట్రాన్స్‌క్రిప్షన్ విఫలమైంది",
        "empty_message": "పంపే ముందు సందేశం టైప్ చేయండి లేదా వాయిస్ రికార్డ్ చేయండి.",
        "need_document": ("దయచేసి ముందుగా పత్రాన్ని అప్లోడ్ చేసి ప్రాసెస్ చేసి, తరువాత ప్రశ్న అడగండి."),
        "searching": "పత్రంలో వెతుకుతోంది...",
        "processing_failed": "క్షమించండి, ప్రాసెసింగ్ విఫలమైనందున సమాధానం ఇవ్వలేకపోయాను",
        "sources": "మూలాలు",
        "page": "పేజీ",
        "upload_title": "అప్లోడ్",
        "upload_body": "ప్రారంభించడానికి ఒకటి లేదా అంతకంటే ఎక్కువ ఫైళ్లను అప్లోడ్ చేయండి.",
        "choose_files": "ఫైల్‌లను ఎంచుకోండి",
        "uploaded": "{count} ఫైల్‌లు విజయవంతంగా అప్లోడ్ అయ్యాయి.",
        "file_type": "రకం",
        "file_size": "పరిమాణం",
        "continue_processing": "ప్రాసెసింగ్‌కు వెళ్లండి",
        "no_files": "ఇంకా ఫైల్‌లు అప్లోడ్ కాలేదు.",
        "processing_title": "ప్రాసెసింగ్",
        "no_files_found": "ఫైల్‌లు కనబడలేదు. దయచేసి ముందుగా ఫైల్‌లు అప్లోడ్ చేయండి.",
        "go_upload": "అప్లోడ్‌కు వెళ్లండి",
        "processing_files": "{count} ఫైల్‌లు ప్రాసెస్ అవుతున్నాయి...",
        "processing_file": "ప్రాసెసింగ్: {name}",
        "process_failed": "{name} ప్రాసెస్ కాలేదు",
        "check_logs": "వివరాల కోసం అప్లికేషన్ లాగ్‌లను చూడండి.",
        "processing_complete": "ప్రాసెసింగ్ పూర్తయింది!",
        "continue_chat": "చాట్‌కు వెళ్లండి",
        "history_title": "చరిత్ర",
        "no_history": "ఇంకా చరిత్ర లేదు. చరిత్ర చూడడానికి చాట్ ప్రారంభించండి.",
        "you": "మీరు",
        "assistant": "సహాయకుడు",
        "clear_history": "చరిత్రను తొలగించండి",
        "processed": "పత్రం విజయవంతంగా ప్రాసెస్ అయింది. ఇప్పుడు మీరు ప్రశ్నలు అడగవచ్చు.",
        "not_found": "అప్లోడ్ చేసిన పత్రంలో సరిపడ సమాచారం లేదు.",
        "outside_scope": "ఈ ప్రశ్న అప్లోడ్ చేసిన పత్రం పరిధికి బయట ఉంది.",
        "upload": "అప్లోడ్",
        "ask": "అడగండి",
        "home_upload": "PDF/ఇమేజ్ అప్లోడ్ చేయండి",
        "ask_question": "మీ ప్రశ్న అడగండి",
    },
}


def language_code(language: str | None) -> str:
    if not language:
        return "en"
    normalized = language.strip()
    if normalized in CATALOG:
        return normalized
    return LANGUAGE_NAMES.get(normalized, "en")


def language_name(language: str | None) -> str:
    return LANGUAGE_LABELS.get(language_code(language), "English")


def translate(key: str, language: str = "en", **kwargs: object) -> str:
    code = language_code(language)
    text = CATALOG.get(code, CATALOG["en"]).get(key, CATALOG["en"].get(key, key))
    return text.format(**kwargs) if kwargs else text


def localize_value(value: object, language: str = "en") -> str:
    text = str(value or "").strip()
    if text.lower() in PLACEHOLDER_VALUES:
        if text.lower().startswith("not enough"):
            return translate("not_found", language)
        if text.lower().startswith("this question"):
            return translate("outside_scope", language)
        return translate("not_specified_short", language)
    category_map = {
        "hi": {
            "education": "शिक्षा",
            "agriculture": "कृषि",
            "health": "स्वास्थ्य",
            "employment": "रोज़गार",
            "housing": "आवास",
        },
        "te": {
            "education": "విద్య",
            "agriculture": "వ్యవసాయం",
            "health": "ఆరోగ్యం",
            "employment": "ఉపాధి",
            "housing": "గృహనిర్మాణం",
        },
    }
    return category_map.get(language_code(language), {}).get(text.lower(), text)


def localize_items(items: object, language: str = "en") -> list[str]:
    if not isinstance(items, list):
        return []
    return [localize_value(item, language) for item in items]
