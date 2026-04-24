# ==========================================
# ROLE 3: OBSERVABILITY & QA ENGINEER
# ==========================================
# Task: Implement quality gates to reject corrupt data or logic discrepancies.

TOXIC_PATTERNS = [
    'Null pointer exception',
    'null pointer',
    'NullPointerException',
    'Null',
    'undefined',
    'NaN',
    'Error: ',
    'Exception:',
    'Stack trace',
    'Traceback (most recent call last)',
]


def run_quality_gate(document_dict):
    content = document_dict.get('content', '')
    if len(content) < 20:
        return False

    for pattern in TOXIC_PATTERNS:
        if pattern.lower() in content.lower():
            return False

    return True
