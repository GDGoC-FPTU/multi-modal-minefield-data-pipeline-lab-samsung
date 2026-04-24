import ast
import re


# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Extract docstrings and comments from legacy Python code.

def extract_logic_from_code(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()

    tree = ast.parse(source_code)
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            docstring = ast.get_docstring(node)
            functions.append({
                'name': node.name,
                'docstring': docstring or '',
                'line': node.lineno,
            })

    business_rules = re.findall(
        r'#\s*(Business Logic Rule \d+.*?)(?:\n|$)',
        source_code, re.IGNORECASE
    )

    module_doc = ast.get_docstring(tree)

    functions_str = '; '.join(f"[{fn['name']}: {fn['docstring']}]" for fn in functions)
    doc = {
        'document_id': 'code-legacy-001',
        'content': f"Module: VinData Legacy Pipeline. Doc: {module_doc}. "
                   f"Functions: {functions_str}. "
                   f"Business Rules: {'; '.join(business_rules)}.",
        'source_type': 'Code',
        'author': 'Senior Dev (retired)',
        'timestamp': None,
        'source_metadata': {
            'filename': file_path,
            'functions': functions,
            'business_rules': business_rules,
        }
    }
    return doc
