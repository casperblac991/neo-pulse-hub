import json
import os
import urllib.parse

# Paths
JSON_STORE = 'data/products.json'
JSON_POOL = 'data/products_pool.json'

def get_smart_link(name, tag="neopulsehub-20"):
    encoded_query = urllib.parse.quote(name)
    return f"https://www.amazon.com/s?k={encoded_query}&tag={tag}"

def get_reliable_image(category):
    images = {
        "smartwatch": "https://m.media-amazon.com/images/I/71rSQvzS8QL._AC_SL1500_.jpg",
        "earbuds": "https://m.media-amazon.com/images/I/65bsB9JfUvL._AC_SL1500_.jpg",
        "headphones": "https://m.media-amazon.com/images/I/72TpY5M8JRL._AC_SL1500_.jpg",
        "smart-home": "https://m.media-amazon.com/images/I/61ERwZ1H8eL._AC_SL1500_.jpg",
        "health": "https://m.media-amazon.com/images/I/71X-4ycOHBL._AC_SL1500_.jpg",
        "productivity": "https://m.media-amazon.com/images/I/61GN5Y+k8XL._AC_SL1500_.jpg",
        "gaming": "https://m.media-amazon.com/images/I/81tCtIXGKFL._AC_SL1500_.jpg",
        "cameras": "https://m.media-amazon.com/images/I/51KzXhX+L0L._AC_SL1500_.jpg",
        "smart-glasses": "https://m.media-amazon.com/images/I/71p0U-c1D9L._AC_SL1500_.jpg",
        "car": "https://m.media-amazon.com/images/I/71J8TZ3V3VL._AC_SL1500_.jpg",
        "kids": "https://m.media-amazon.com/images/I/714fP0K2VXL._AC_SL1500_.jpg",
    }
    return images.get(category, images["smartwatch"])

def sync():
    print("🚀 Starting Store & Warehouse Sync...")
    
    # 1. Update Store (products.json)
    if os.path.exists(JSON_STORE):
        with open(JSON_STORE, 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        for p in products:
            name_en = p.get("name", {}).get("en") or p.get("title") or "electronics"
            p["affiliate_amazon"] = get_smart_link(name_en)
            p["image"] = get_reliable_image(p.get("category", "smartwatch"))
            
        with open(JSON_STORE, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        print(f"✅ Updated {len(products)} products in Store.")

    # 2. Update Warehouse (products_pool.json)
    if os.path.exists(JSON_POOL):
        with open(JSON_POOL, 'r', encoding='utf-8') as f:
            pool = json.load(f)
        
        for p in pool:
            name_en = p.get("name_en") or p.get("title") or "electronics"
            p["affiliate_amazon"] = get_smart_link(name_en)
            p["image"] = get_reliable_image(p.get("category", "smartwatch"))
            
        with open(JSON_POOL, 'w', encoding='utf-8') as f:
            json.dump(pool, f, ensure_ascii=False, indent=2)
        print(f"✅ Updated {len(pool)} products in Warehouse.")

if __name__ == "__main__":
    sync()
