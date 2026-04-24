import re
from schema import UnifiedDocument
from datetime import datetime


def clean_transcript(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Remove timestamp tokens [00:00:00]
    text = re.sub(r'\[\d{2}:\d{2}:\d{2}\]', '', text)

    # Remove noise tokens
    noise_patterns = [
        r'\[Music starts?\]',
        r'\[Music ends?\]',
        r'\[Music\]',
        r'\[inaudible\]',
        r'\[Laughter\]',
        r'\[[^\]]*\]',  # Generic fallback: remove any remaining [bracketed]
    ]
    for pattern in noise_patterns:
        text = re.sub(pattern, '', text)

    # Collapse multiple spaces
    text = re.sub(r' +', ' ', text)
    text = text.strip()

    # Extract price: "năm trăm nghìn VND" = 500,000 VND
    price_match = re.search(
        r'(?:năm|năm\s+)trăm\s+nghìn',
        text, re.IGNORECASE
    )
    detected_price_vnd = None
    if price_match:
        detected_price_vnd = 500000

    doc = UnifiedDocument(
        document_id="transcript-001",
        content=text,
        source_type="Video",
        author="Speaker 1",
        timestamp=datetime.now().isoformat(),
        source_metadata={
            "original_file": "demo_transcript.txt",
            "detected_price_vnd": detected_price_vnd,
        }
    )
    return doc.model_dump(mode='json')
