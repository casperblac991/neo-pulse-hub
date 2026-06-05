import json
import urllib.parse

def fix_catalog():
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        print(f"Loaded {len(products)} products.")
        
        # Mapping categories to reliable fallback images
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

        tag = "neopulsehub-20"
        
        for p in products:
            # 1. Standardize name and get search query
            name_ar = ""
            name_en = ""
            
            if isinstance(p.get("name"), dict):
                name_ar = p["name"].get("ar", "")
                name_en = p["name"].get("en", "")
            elif isinstance(p.get("name"), str):
                name_ar = name_en = p["name"]
            
            if not name_ar and p.get("title"):
                name_ar = name_en = p["title"]
            
            search_query = name_en or name_ar or "electronics"
            encoded_query = urllib.parse.quote(search_query)

            # 2. Fix Affiliate Links - Use Search by default to guarantee the link works
            # Direct DP links often fail if ASIN is old/wrong. Search links always show results.
            p["affiliate_amazon"] = f"https://www.amazon.com/s?k={encoded_query}&tag={tag}"
            
            # 3. Fix Image URLs
            image = p.get("image", "")
            # If image is a placeholder or missing, use category fallback
            if not image or any(x in image.lower() for x in ["placeholder", "via.placeholder", "unsplash.com"]):
                cat = p.get("category", "smartwatch")
                p["image"] = category_images.get(cat, category_images["smartwatch"])
            
            # 4. Ensure name is a dictionary for the frontend
            p["name"] = {"ar": name_ar, "en": name_en}
            
            # 5. Fix price
            if isinstance(p.get("price"), str):
                try:
                    p["price"] = float(p["price"].replace("$", "").replace(",", ""))
                except:
                    p["price"] = 99.99

        with open('products.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
            
        print(f"Successfully processed and fixed {len(products)} products with guaranteed search links.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_catalog()
