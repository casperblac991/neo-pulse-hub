import json
import re
import urllib.parse

def get_smart_link(name, tag="neopulsehub-20"):
    encoded_query = urllib.parse.quote(name)
    return f"https://www.amazon.com/s?k={encoded_query}&tag={tag}"

def get_fallback_image(category):
    category_images = {
        "smartwatch": "https://m.media-amazon.com/images/I/71rSQvzS8QL._AC_SY679_.jpg",
        "earbuds": "https://m.media-amazon.com/images/I/65bsB9JfUvL._AC_SY679_.jpg",
        "headphones": "https://m.media-amazon.com/images/I/72TpY5M8JRL._AC_SY679_.jpg",
        "smart-home": "https://m.media-amazon.com/images/I/61ERwZ1H8eL._AC_SY679_.jpg",
        "health": "https://m.media-amazon.com/images/I/71X-4ycOHBL._AC_SY679_.jpg",
        "productivity": "https://m.media-amazon.com/images/I/61GN5Y+k8XL._AC_SY679_.jpg",
        "gaming": "https://m.media-amazon.com/images/I/81tCtIXGKFL._AC_SY679_.jpg",
        "cameras": "https://m.media-amazon.com/images/I/51KzXhX+L0L._AC_SY679_.jpg",
        "smart-glasses": "https://m.media-amazon.com/images/I/71p0U-c1D9L._AC_SY679_.jpg",
        "car": "https://m.media-amazon.com/images/I/71J8TZ3V3VL._AC_SY679_.jpg",
        "kids": "https://m.media-amazon.com/images/I/714fP0K2VXL._AC_SY679_.jpg",
    }
    return category_images.get(category, category_images["smartwatch"])

def fix_json():
    print("Fixing products.json...")
    with open('products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    for p in products:
        name_en = p.get("name", {}).get("en") or p.get("title") or "electronics"
        p["affiliate_amazon"] = get_smart_link(name_en)
        
        image = p.get("image", "")
        if not image or any(x in image.lower() for x in ["placeholder", "unsplash.com"]):
            p["image"] = get_fallback_image(p.get("category", "smartwatch"))
            
    with open('products.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"Fixed {len(products)} products in JSON.")

def fix_html_inline():
    print("Fixing products.html inline products...")
    with open('products.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # This is a bit complex due to JS object format, but we can target the image URLs and add links
    # Actually, a better way is to update the normalization function in JS if it exists, 
    # but let's try to fix the data directly.
    
    # Replace Unsplash images with fallbacks based on category
    def replace_image(match):
        obj_str = match.group(0)
        cat_match = re.search(r'category:\s*["\']([^"\']+)["\']', obj_str)
        if cat_match:
            cat = cat_match.group(1)
            fallback = get_fallback_image(cat)
            # Replace image line
            obj_str = re.sub(r'image:\s*["\']https://images\.unsplash\.com/[^"\']+["\']', f'image: "{fallback}"', obj_str)
        return obj_str

    # Find all product objects in the array
    new_content = re.sub(r'\{\s*id:\s*["\']NPH-EXP-\d+["\'].*?\}', replace_image, content, flags=re.DOTALL)
    
    with open('products.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Fixed inline products in products.html.")

if __name__ == "__main__":
    fix_json()
    fix_html_inline()
