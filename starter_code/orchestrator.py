import json
import time
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "raw_data")

from schema import UnifiedDocument
from process_pdf import extract_pdf_data
from process_transcript import clean_transcript
from process_html import parse_html_catalog
from process_csv import process_sales_csv
from process_legacy_code import extract_logic_from_code
from quality_check import run_quality_gate

# ==========================================
# ROLE 4: DEVOPS & INTEGRATION SPECIALIST
# ==========================================

def main():
    start_time = time.time()
    final_kb = []

    pdf_path = os.path.join(RAW_DATA_DIR, "lecture_notes.pdf")
    trans_path = os.path.join(RAW_DATA_DIR, "demo_transcript.txt")
    html_path = os.path.join(RAW_DATA_DIR, "product_catalog.html")
    csv_path = os.path.join(RAW_DATA_DIR, "sales_records.csv")
    code_path = os.path.join(RAW_DATA_DIR, "legacy_pipeline.py")
    output_path = os.path.join(os.path.dirname(SCRIPT_DIR), "processed_knowledge_base.json")

    # --- Process PDF ---
    print("Processing PDF...")
    doc = extract_pdf_data(pdf_path)
    if doc and run_quality_gate(doc):
        final_kb.append(doc)
        print(f"  [OK] PDF document added: {doc['document_id']}")
    else:
        print(f"  [SKIP] PDF document rejected by quality gate.")

    # --- Process Transcript ---
    print("Processing Transcript...")
    doc = clean_transcript(trans_path)
    if doc and run_quality_gate(doc):
        final_kb.append(doc)
        print(f"  [OK] Transcript document added: {doc['document_id']}")
    else:
        print(f"  [SKIP] Transcript document rejected by quality gate.")

    # --- Process HTML Catalog ---
    print("Processing HTML Catalog...")
    docs = parse_html_catalog(html_path)
    for doc in docs:
        if run_quality_gate(doc):
            final_kb.append(doc)
            print(f"  [OK] HTML product added: {doc['document_id']}")
        else:
            print(f"  [SKIP] HTML product rejected: {doc['document_id']}")

    # --- Process Sales CSV ---
    print("Processing Sales CSV...")
    docs = process_sales_csv(csv_path)
    for doc in docs:
        if run_quality_gate(doc):
            final_kb.append(doc)
        else:
            print(f"  [SKIP] CSV record rejected: {doc['document_id']}")

    # --- Process Legacy Code ---
    print("Processing Legacy Code...")
    doc = extract_logic_from_code(code_path)
    if doc and run_quality_gate(doc):
        final_kb.append(doc)
        print(f"  [OK] Legacy code document added: {doc['document_id']}")
    else:
        print(f"  [SKIP] Legacy code document rejected by quality gate.")

    # --- Save output ---
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_kb, f, ensure_ascii=False, indent=2)

    end_time = time.time()
    print(f"\nPipeline finished in {end_time - start_time:.2f} seconds.")
    print(f"Total valid documents stored: {len(final_kb)}")
    print(f"Output saved to: {output_path}")


if __name__ == "__main__":
    main()
