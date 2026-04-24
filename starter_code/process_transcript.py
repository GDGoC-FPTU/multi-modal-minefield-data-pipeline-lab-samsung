import re
from datetime import datetime


# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Clean the transcript text and extract key information.

def clean_transcript(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    noise_pattern = re.compile(
        r'\[Music\s*(starts|ends)?\]|\[Music\]|\[inaudible\]|\[Laughter\]|\[Speaker\s*\d?\]',
        re.IGNORECASE
    )
    cleaned = noise_pattern.sub('', text)
    cleaned = re.sub(r'\[\d{2}:\d{2}:\d{2}\]', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    vietnamese_price_map = {
        'một trăm': 100000, 'hai trăm': 200000, 'ba trăm': 300000,
        'bốn trăm': 400000, 'năm trăm': 500000, 'sáu trăm': 600000,
        'bảy trăm': 700000, 'tám trăm': 800000, 'chín trăm': 900000,
    }
    detected_price = None
    for word, value in vietnamese_price_map.items():
        if word in cleaned.lower() and 'nghìn' in cleaned.lower():
            detected_price = value
            break

    doc = {
        'document_id': 'video-transcript-001',
        'content': cleaned,
        'source_type': 'Video',
        'author': 'Unknown',
        'timestamp': None,
        'source_metadata': {
            'detected_price_vnd': detected_price if detected_price else 0,
            'topic': 'Data Pipeline Engineering',
            'original_language': 'Vietnamese',
        }
    }
    return doc
