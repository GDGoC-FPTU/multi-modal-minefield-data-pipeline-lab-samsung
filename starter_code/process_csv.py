import pandas as pd
import re
from schema import UnifiedDocument
from datetime import datetime


def _parse_price(price_str):
    """Convert various price formats to float (VND-normalized)."""
    if pd.isna(price_str) or str(price_str).strip() == '':
        return None
    s = str(price_str).strip()

    # Handle obvious invalid values
    invalid = {'n/a', 'na', 'null', 'liên hệ', '-', 'contact'}
    if s.lower() in invalid:
        return None

    # Check if it's already a plain number
    try:
        val = float(s.replace(',', ''))
        return val
    except ValueError:
        pass

    # Handle "$1200" or "1200 USD"
    usd_match = re.search(r'\$?\s*([\d,]+)\s*(?:USD)?', s, re.IGNORECASE)
    if usd_match:
        val = float(usd_match.group(1).replace(',', ''))
        return val

    # Handle wordy numbers like "five dollars"
    word_to_num = {
        'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
        'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
        'ten': 10, 'eleven': 11, 'twelve': 12, 'fifteen': 15,
    }
    for word, num in word_to_num.items():
        pattern = rf'\b{word}\b'
        if re.search(pattern, s, re.IGNORECASE):
            return float(num)

    return None


def _parse_date(date_str):
    """Convert various date formats to YYYY-MM-DD."""
    if pd.isna(date_str) or str(date_str).strip() == '':
        return None
    s = str(date_str).strip()

    formats = [
        '%Y-%m-%d',       # 2026-01-15
        '%d/%m/%Y',       # 15/01/2026, 17-01-2026
        '%d-%m-%Y',       # 17-01-2026
        '%Y/%m/%d',       # 2026/01/19
        '%d %b %Y',       # 19 Jan 2026
        '%B %d, %Y',      # January 16th 2026
    ]

    for fmt in formats:
        try:
            return datetime.strptime(s, fmt).strftime('%Y-%m-%d')
        except ValueError:
            pass

    # Try stripping ordinal suffix like "th" or "nd" from "January 16th 2026"
    s2 = re.sub(r'(\d+)(st|nd|rd|th)\b', r'\1', s)
    for fmt in ['%B %d %Y', '%b %d %Y']:
        try:
            return datetime.strptime(s2, fmt).strftime('%Y-%m-%d')
        except ValueError:
            pass

    return s


def process_sales_csv(file_path):
    df = pd.read_csv(file_path)

    # Drop duplicate rows based on 'id' - keep first occurrence
    df = df.drop_duplicates(subset=['id'], keep='first')

    documents = []
    for _, row in df.iterrows():
        price = _parse_price(row['price'])
        if price is None:
            continue  # Skip invalid prices

        date_str = _parse_date(row.get('date_of_sale', ''))
        seller = str(row.get('seller_id', 'Unknown')).strip()
        stock = row.get('stock_quantity', 0)
        try:
            stock_val = int(stock) if not pd.isna(stock) else None
        except (ValueError, TypeError):
            stock_val = None

        # Skip negative stock
        if stock_val is not None and stock_val < 0:
            continue

        doc = UnifiedDocument(
            document_id=f"csv-{int(row['id'])}",
            content=(
                f"Product: {row['product_name']} | Category: {row['category']} | "
                f"Price: {price} {row['currency']} | Date: {date_str} | "
                f"Seller: {seller} | Stock: {stock_val}"
            ),
            source_type="CSV",
            author=seller,
            timestamp=date_str,
            source_metadata={
                "original_file": "sales_records.csv",
                "product_name": str(row['product_name']).strip(),
                "category": str(row['category']).strip(),
                "price": price,
                "currency": str(row['currency']).strip(),
                "date_of_sale": date_str,
                "seller_id": seller,
                "stock_quantity": stock_val,
            }
        )
        documents.append(doc.model_dump(mode='json'))

    return documents
