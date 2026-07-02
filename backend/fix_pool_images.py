import json
import os

def fix_images():
    pool_path = 'products_pool.json'
    if not os.path.exists(pool_path):
        print(f"Error: {pool_path} not found")
        return

    with open(pool_path, 'r', encoding='utf-8') as f:
        products = json.load(f)

    # Mapping categories to local high-quality images
    cat_images = {
        'smartwatch': 'images/products/cat_smartwatch.jpg',
        'earbuds': 'images/products/cat_earbuds.jpg',
        'smart-glasses': 'images/products/cat_smartglasses.jpg',
        'health': 'images/products/cat_smartwatch.jpg',
        'smart-home': 'images/products/cat_tech.jpg',
        'productivity': 'images/products/cat_tech.jpg'
    }

    fixed_count = 0
    for p in products:
        cat = p.get('category', 'tech')
        # If the image is one of the known overused Amazon URLs, replace it with a category-specific local image
        overused_urls = [
            "https://m.media-amazon.com/images/I/71rSQvzS8QL._AC_SL1500_.jpg",
            "https://m.media-amazon.com/images/I/71X-4ycOHBL._AC_SL1500_.jpg",
            "https://m.media-amazon.com/images/I/65bsB9JfUvL._AC_SL1500_.jpg",
            "https://m.media-amazon.com/images/I/61GN5Y+k8XL._AC_SL1500_.jpg",
            "https://m.media-amazon.com/images/I/61ERwZ1H8eL._AC_SL1500_.jpg"
        ]
        
        if p.get('image') in overused_urls or not p.get('image'):
            p['image'] = cat_images.get(cat, 'images/products/cat_tech.jpg')
            fixed_count += 1

    with open(pool_path, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    print(f"✅ Fixed {fixed_count} product images in products_pool.json")

if __name__ == "__main__":
    fix_images()
