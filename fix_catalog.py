import json
import re

def fix_catalog():
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        print(f"Loaded {len(products)} products.")
        
        fixed_count = 0
        
        # Mapping categories to fallback images (Amazon official images)
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

        for p in products:
            # 1. Fix Image URLs
            image = p.get("image", "")
            if not image or "placeholder" in image or "unsplash" in image or "via.placeholder" in image:
                cat = p.get("category", "smartwatch")
                p["image"] = category_images.get(cat, category_images["smartwatch"])
                fixed_count += 1
            
            # 2. Fix Affiliate Links
            # Ensure the tag is correct
            tag = "neopulsehub-20"
            url = p.get("affiliate_amazon") or p.get("url") or ""
            asin = p.get("asin", "")
            
            if asin and len(asin) == 10:
                # Reconstruct direct DP link
                p["affiliate_amazon"] = f"https://www.amazon.com/dp/{asin}?tag={tag}"
            elif url:
                # Ensure existing URL has the correct tag
                if "tag=" in url:
                    url = re.sub(r'tag=[^&]+', f'tag={tag}', url)
                else:
                    sep = '&' if '?' in url else '?'
                    url = f"{url}{sep}tag={tag}"
                p["affiliate_amazon"] = url
            else:
                # Fallback to search if no ASIN or URL
                name = p.get("name", {}).get("en") or p.get("title") or "electronics"
                query = name.replace(" ", "+")
                p["affiliate_amazon"] = f"https://www.amazon.com/s?k={query}&tag={tag}"
            
            # Standardize field names for the storefront
            if "name" not in p and "title" in p:
                p["name"] = {"ar": p["title"], "en": p["title"]}
            
            # Ensure price is a number
            if isinstance(p.get("price"), str):
                try:
                    p["price"] = float(p["price"].replace("$", "").replace(",", ""))
                except:
                    p["price"] = 99.99

        with open('products.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
            
        print(f"Successfully fixed {len(products)} products.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_catalog()
