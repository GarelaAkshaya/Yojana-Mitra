from backend.structuring.scheme_parser import extract_scheme_fields


def test_rule_parser_extracts_core_sections():
    text = """
    Scheme Name: Student Scholarship Yojana
    Department: Education Department
    State: Telangana

    Eligibility:
    - Student
    - Annual income below Rs 200000

    Benefits:
    - Scholarship amount

    Documents:
    - Aadhaar
    - Income Certificate
    """
    scheme = extract_scheme_fields(text)
    assert scheme.scheme_name == "Student Scholarship Yojana"
    assert scheme.department == "Education Department"
    assert "Student" in scheme.eligibility
    assert "Aadhaar" in scheme.documents


def test_rule_parser_extracts_hindi_sections():
    text = """
    ग्रामीण कौशल विकास योजना

    लाभ:
    - निःशुल्क प्रशिक्षण
    - रोजगार सहायता

    पात्रता:
    - ग्रामीण युवा

    आवश्यक दस्तावेज:
    - आधार कार्ड
    """
    scheme = extract_scheme_fields(text)
    assert "निःशुल्क प्रशिक्षण" in scheme.benefits
    assert "ग्रामीण युवा" in scheme.eligibility
    assert "आधार कार्ड" in scheme.documents


def test_rule_parser_extracts_telugu_sections():
    text = """
    రైతు బంధు సహాయ పథకం

    ప్రయోజనాలు:
    - రైతులకు ఆర్థిక సహాయం

    అర్హత:
    - తెలంగాణ రైతులు

    అవసరమైన పత్రాలు:
    - పట్టాదారు పాస్‌బుక్
    """
    scheme = extract_scheme_fields(text)
    assert "రైతులకు ఆర్థిక సహాయం" in scheme.benefits
    assert "తెలంగాణ రైతులు" in scheme.eligibility
    assert "పట్టాదారు పాస్‌బుక్" in scheme.documents
