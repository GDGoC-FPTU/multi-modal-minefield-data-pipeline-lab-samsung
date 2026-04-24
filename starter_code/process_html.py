from bs4 import BeautifulSoup
from schema import UnifiedDocument
from datetime import datetime


def parse_html_catalog(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    table = soup.find('table', id='main-catalog')
    if not table:
        return []

    products = []
    rows = table.find('tbody').find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 6:
            continue

        product_id = cells[0].get_text(strip=True)
        product_name = cells[1].get_text(strip=True)
        category = cells[2].get_text(strip=True)
        price_text = cells[3].get_text(strip=True)
        stock_text = cells[4].get_text(strip=True)
        rating_text = cells[5].get_text(strip=True)

        # Skip invalid rows (N/A price with 0 stock = unavailable product)
        if price_text in ('N/A', 'Liên hệ') or stock_text == '0':
            continue

        # Normalize price - extract numeric value
        price_clean = price_text.replace('VND', '').replace(',', '').strip()
        try:
            price_val = float(price_clean)
        except ValueError:
            continue

        # Skip negative stock
        try:
            stock_val = int(stock_text)
            if stock_val < 0:
                continue
        except ValueError:
            pass

        doc = UnifiedDocument(
            document_id=f"html-{product_id}",
            content=f"{product_name} | {category} | {price_text} | Stock: {stock_text} | Rating: {rating_text}",
            source_type="HTML",
            author="VinShop",
            timestamp=datetime.now().isoformat(),
            source_metadata={
                "original_file": "product_catalog.html",
                "product_id": product_id,
                "product_name": product_name,
                "category": category,
                "price": price_val,
                "currency": "VND",
                "stock_quantity": stock_val,
                "rating": rating_text,
            }
        )
        products.append(doc.model_dump(mode='json'))

    return products
