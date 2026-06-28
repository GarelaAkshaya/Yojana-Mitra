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
