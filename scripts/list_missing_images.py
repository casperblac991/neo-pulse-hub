import json
from pathlib import Path

products = json.loads(Path('products.json').read_text(encoding='utf-8'))
for product in products:
    image = product.get('image', '')
    if image and not image.startswith(('http://', 'https://')) and not Path(image).exists():
        name = product.get('name', {})
        print(f"{product.get('id')}\t{name.get('en', name)}\t{name.get('ar', '')}\t{product.get('category', '')}\t{image}")
