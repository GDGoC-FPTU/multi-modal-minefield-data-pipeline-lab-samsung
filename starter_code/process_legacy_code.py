import ast
import re
from schema import UnifiedDocument
from datetime import datetime


def extract_logic_from_code(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()

    tree = ast.parse(source_code)

    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            docstring = ast.get_docstring(node)
            functions.append({
                "name": node.name,
                "docstring": docstring or "",
            })

    # Extract business logic rules from comments
    business_rules = []
    rule_pattern = re.compile(r'#\s*(Business Logic Rule \d+.*)', re.IGNORECASE)
    for line in source_code.splitlines():
        m = rule_pattern.search(line)
        if m:
            business_rules.append(m.group(1).strip())

    # Detect discrepancies: comment says 8%, code says 10%
    tax_comment_match = re.search(r'#\s*(?:calculates VAT at|does)\s*(\d+)%', source_code, re.IGNORECASE)
    tax_code_match = re.search(r'tax_rate\s*=\s*(0\.\d+)', source_code)

    discrepancy = None
    if tax_comment_match and tax_code_match:
        comment_pct = int(tax_comment_match.group(1))
        code_pct = int(float(tax_code_match.group(1)) * 100)
        if comment_pct != code_pct:
            discrepancy = f"Comment says {comment_pct}% but code calculates {code_pct}%"

    content_parts = [f"Business Logic extracted from {file_path}:"]
    for rule in business_rules:
        content_parts.append(f"- {rule}")
    content_parts.append("Functions documented:")
    for fn in functions:
        if fn['docstring']:
            content_parts.append(f"- {fn['name']}: {fn['docstring'][:100]}")
    if discrepancy:
        content_parts.append(f"DISCREPANCY DETECTED: {discrepancy}")

    content = " ".join(content_parts)

    doc = UnifiedDocument(
        document_id="code-legacy-001",
        content=content,
        source_type="Code",
        author="Senior Dev (retired)",
        timestamp=datetime.now().isoformat(),
        source_metadata={
            "original_file": "legacy_pipeline.py",
            "functions": functions,
            "business_rules": business_rules,
            "discrepancy": discrepancy,
        }
    )
    return doc.model_dump(mode='json')
