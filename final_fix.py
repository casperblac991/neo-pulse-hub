import json
import re
import urllib.parse

def get_smart_link(name, tag="neopulsehub-20"):
    encoded_query = urllib.parse.quote(name)
    return f"https://www.amazon.com/s?k={encoded_query}&tag={tag}"

def get_reliable_image(category):
    # Using specific Amazon image IDs that are known to be stable
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

def fix_json():
    print("Fixing products.json...")
    with open('products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    for p in products:
        name_en = p.get("name", {}).get("en") or p.get("title") or "electronics"
        p["affiliate_amazon"] = get_smart_link(name_en)
        p["image"] = get_reliable_image(p.get("category", "smartwatch"))
            
    with open('products.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"Fixed {len(products)} products in JSON.")

def fix_html_files():
    files = ['index.html', 'products.html']
    for filename in files:
        print(f"Fixing {filename}...")
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. Fix broken images in JS/HTML
        def replace_img(match):
            obj_str = match.group(0)
            cat_match = re.search(r'category:\s*["\']([^"\']+)["\']', obj_str)
            cat = cat_match.group(1) if cat_match else "smartwatch"
            fallback = get_reliable_image(cat)
            return re.sub(r'image:\s*["\']https?://[^"\']+["\']', f'image: "{fallback}"', obj_str)

        content = re.sub(r'\{\s*id:\s*["\']NPH-EXP-\d+["\'].*?\}', replace_img, content, flags=re.DOTALL)
        
        # 2. Fix search links in JS logic if any
        # (The search links are already in products.json which is loaded dynamically)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {filename}.")

if __name__ == "__main__":
    fix_json()
    fix_html_files()
