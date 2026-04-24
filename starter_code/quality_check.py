# ==========================================
# ROLE 3: OBSERVABILITY & QA ENGINEER
# ==========================================
# Task: Implement quality gates to reject corrupt data or logic discrepancies.

TOXIC_STRINGS = [
    'null pointer exception',
    'nullPointerException',
    'NullPointerException',
    'java.lang.NullPointerException',
    'segmentation fault',
    'stack overflow',
    'out of memory',
    'exception in thread',
    'traceback (most recent call last call)',
    'error:',
    'fatal error',
]

MIN_CONTENT_LENGTH = 20


def run_quality_gate(document_dict):
    # Gate 1: Content too short
    content = document_dict.get('content', '')
    if len(content.strip()) < MIN_CONTENT_LENGTH:
        print(f"[QUALITY GATE FAIL] Content too short (< {MIN_CONTENT_LENGTH} chars): doc_id={document_dict.get('document_id')}")
        return False

    # Gate 2: Toxic / error strings
    content_lower = content.lower()
    for toxic in TOXIC_STRINGS:
        if toxic.lower() in content_lower:
            print(f"[QUALITY GATE FAIL] Toxic string '{toxic}' found in: doc_id={document_dict.get('document_id')}")
            return False

    # Gate 3: Logic discrepancy detection
    # If document is from Code source, check for tax discrepancy flag
    if document_dict.get('source_type') == 'Code':
        meta = document_dict.get('source_metadata', {})
        if meta.get('discrepancy'):
            print(f"[QUALITY GATE WARN] Logic discrepancy in code doc {document_dict.get('document_id')}: {meta['discrepancy']}")

    return True
