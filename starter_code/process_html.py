from bs4 import BeautifulSoup


# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Extract product data from the HTML table, ignoring boilerplate.

def parse_html_catalog(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    table = soup.find('table', id='main-catalog')
    if not table:
        return []

    rows = table.find_all('tr')[1:]
    result = []

    for i, row in enumerate(rows):
        cols = row.find_all('td')
        if len(cols) < 6:
            continue

        product_id = cols[0].get_text(strip=True)
        product_name = cols[1].get_text(strip=True)
        category = cols[2].get_text(strip=True)
        price_text = cols[3].get_text(strip=True)
        stock_text = cols[4].get_text(strip=True)
        rating_text = cols[5].get_text(strip=True)

        price_str = price_text.replace(' VND', '').replace(',', '').strip()
        try:
            price_val = float(price_str) if price_str not in ('N/A', 'Liên hệ', '') else None
        except ValueError:
            price_val = None

        try:
            stock_val = int(float(stock_text)) if stock_text.strip() not in ('', 'N/A') else 0
        except (ValueError, TypeError):
            stock_val = 0

        doc = {
            'document_id': f"html-{product_id}",
            'content': f"{product_name} | {category} | Price: {price_text} | Stock: {stock_val} | Rating: {rating_text}",
            'source_type': 'HTML',
            'author': 'Unknown',
            'timestamp': None,
            'source_metadata': {
                'product_id': product_id,
                'product_name': product_name,
                'category': category,
                'price': price_val,
                'price_display': price_text,
                'stock_quantity': stock_val,
                'rating': rating_text,
            }
        }
        result.append(doc)

    return result
