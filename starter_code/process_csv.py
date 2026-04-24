import pandas as pd
import re
from datetime import datetime


# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Process sales records, handling type traps and duplicates.

def _parse_price(price_str):
    """Convert various price formats to float (in original currency)."""
    if pd.isna(price_str) or price_str is None:
        return None
    s = str(price_str).strip()
    if s in ('N/A', 'Liên hệ', '', 'NULL', 'null', 'None'):
        return None
    s = s.replace(',', '')
    number_word_map = {
        'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
        'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
    }
    lower_s = s.lower()
    for word, num in number_word_map.items():
        if lower_s == f'{word} dollars' or lower_s == f'{word} dollar' or lower_s == f'{word} dolars':
            return float(num)
    try:
        return float(re.sub(r'[^\d.\-]', '', s))
    except ValueError:
        return None


def _parse_date(date_str):
    """Normalize various date formats to YYYY-MM-DD."""
    if pd.isna(date_str) or date_str is None:
        return None
    s = str(date_str).strip()
    fmts = [
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%d-%m-%Y',
        '%Y/%m/%d',
        '%d %b %Y',
        '%B %dth %Y',
    ]
    for fmt in fmts:
        try:
            return datetime.strptime(s, fmt).strftime('%Y-%m-%d')
        except ValueError:
            pass
    return None


def process_sales_csv(file_path):
    df = pd.read_csv(file_path)

    df = df.drop_duplicates(subset=['id'], keep='first')

    df['price'] = df['price'].apply(_parse_price)
    df['date_of_sale'] = df['date_of_sale'].apply(_parse_date)

    df = df[df['price'].notna() & (df['price'] > 0)]
    df = df[df['date_of_sale'].notna()]

    result = []
    for _, row in df.iterrows():
        doc = {
            'document_id': f"csv-{int(row['id']):03d}",
            'content': f"{row['product_name']} | {row['category']} | Price: {row['price']} {row['currency']} | Sold: {row['date_of_sale']}",
            'source_type': 'CSV',
            'author': row.get('seller_id', 'Unknown'),
            'timestamp': row['date_of_sale'],
            'source_metadata': {
                'product_name': row['product_name'],
                'category': row['category'],
                'price': row['price'],
                'currency': row['currency'],
                'date_of_sale': row['date_of_sale'],
                'seller_id': row['seller_id'],
                'stock_quantity': row['stock_quantity'],
            }
        }
        result.append(doc)

    return result
