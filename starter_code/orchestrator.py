import json
import time
import os

# Robust path handling
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "raw_data")


# Import role-specific modules
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
# Task: Orchestrate the ingestion pipeline and handle errors/SLA.

def main():
    start_time = time.time()
    final_kb = []

    # --- FILE PATH SETUP (Handled for students) ---
    pdf_path = os.path.join(RAW_DATA_DIR, "lecture_notes.pdf")
    trans_path = os.path.join(RAW_DATA_DIR, "demo_transcript.txt")
    html_path = os.path.join(RAW_DATA_DIR, "product_catalog.html")
    csv_path = os.path.join(RAW_DATA_DIR, "sales_records.csv")
    code_path = os.path.join(RAW_DATA_DIR, "legacy_pipeline.py")

    output_path = os.path.join(os.path.dirname(SCRIPT_DIR), "processed_knowledge_base.json")
    # ----------------------------------------------

    # --- Process CSV ---
    print("[1/5] Processing CSV...")
    csv_docs = process_sales_csv(csv_path)
    for doc in csv_docs:
        if run_quality_gate(doc):
            final_kb.append(doc)
            print(f"  Added CSV doc: {doc['document_id']}")
        else:
            print(f"  Rejected CSV doc: {doc['document_id']}")

    # --- Process HTML ---
    print("[2/5] Processing HTML catalog...")
    html_docs = parse_html_catalog(html_path)
    for doc in html_docs:
        if run_quality_gate(doc):
            final_kb.append(doc)
            print(f"  Added HTML doc: {doc['document_id']}")
        else:
            print(f"  Rejected HTML doc: {doc['document_id']}")

    # --- Process Transcript ---
    print("[3/5] Processing transcript...")
    transcript_doc = clean_transcript(trans_path)
    if transcript_doc and run_quality_gate(transcript_doc):
        final_kb.append(transcript_doc)
        print(f"  Added transcript: {transcript_doc['document_id']}")
    else:
        print("  Rejected transcript.")

    # --- Process Legacy Code ---
    print("[4/5] Processing legacy code...")
    code_doc = extract_logic_from_code(code_path)
    if code_doc and run_quality_gate(code_doc):
        final_kb.append(code_doc)
        print(f"  Added code doc: {code_doc['document_id']}")
    else:
        print("  Rejected code doc.")

    # --- Process PDF (Gemini) ---
    print("[5/5] Processing PDF with Gemini...")
    if os.path.exists(pdf_path):
        pdf_doc = extract_pdf_data(pdf_path)
        if pdf_doc and run_quality_gate(pdf_doc):
            final_kb.append(pdf_doc)
            print(f"  Added PDF doc: {pdf_doc['document_id']}")
        else:
            print("  Rejected or skipped PDF doc.")
    else:
        print(f"  PDF not found at {pdf_path}, skipping...")

    # --- Save output ---
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_kb, f, ensure_ascii=False, indent=2)

    end_time = time.time()
    print(f"\nPipeline finished in {end_time - start_time:.2f} seconds.")
    print(f"Total valid documents stored: {len(final_kb)}")


if __name__ == "__main__":
    main()
