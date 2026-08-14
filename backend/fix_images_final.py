import json
import os
import random
from pathlib import Path

# قائمة موسعة من صور المنتجات التقنية عالية الجودة (Unsplash/Pexels)
TECH_IMAGES = {
    "smartwatch": [
        "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&q=80",
        "https://images.unsplash.com/photo-1434056886845-dac89ffe9b56?w=800&q=80",
        "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=800&q=80",
        "https://images.unsplash.com/photo-1617043786394-f977fa12eddf?w=800&q=80",
        "https://images.unsplash.com/photo-1579586337278-3bef81640edd?w=800&q=80",
        "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=800&q=80",
        "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=800&q=80",
        "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=800&q=80",
        "https://images.unsplash.com/photo-1517502474097-f9b30659dadb?w=800&q=80",
        "https://images.unsplash.com/photo-1523395243481-163f8f6155ab?w=800&q=80"
    ],
    "headphones": [
        "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80",
        "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=800&q=80",
        "https://images.unsplash.com/photo-1590658268037-6bf12165a8ae?w=800&q=80",
        "https://images.unsplash.com/photo-1611930022073-b7a4ba5fcc75?w=800&q=80",
        "https://images.unsplash.com/photo-1558466941-8f9a3f5a4a0c?w=800&q=80",
        "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800&q=80",
        "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=800&q=80",
        "https://images.unsplash.com/photo-1516280440614-379a5dc9db41?w=800&q=80",
        "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=800&q=80",
        "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800&q=80"
    ],
    "smart-home": [
        "https://images.unsplash.com/photo-1558002038-1055907df827?w=800&q=80",
        "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&q=80",
        "https://images.unsplash.com/photo-1567721913486-6585f069b332?w=800&q=80",
        "https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=800&q=80",
        "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80",
        "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800&q=80",
        "https://images.unsplash.com/photo-1556911229-8d3734527a3d?w=800&q=80",
        "https://images.unsplash.com/photo-1585338107529-13afc5f02586?w=800&q=80",
        "https://images.unsplash.com/photo-1558002038-1055907df827?w=800&q=80",
        "https://images.unsplash.com/photo-1527018601619-a508a2be00cd?w=800&q=80"
    ],
    "laptop": [
        "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80",
        "https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=800&q=80",
        "https://images.unsplash.com/photo-1517336712468-07c1482b0513?w=800&q=80",
        "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=800&q=80",
        "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800&q=80",
        "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=800&q=80",
        "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=800&q=80",
        "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=800&q=80"
    ],
    "camera": [
        "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800&q=80",
        "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=800&q=80",
        "https://images.unsplash.com/photo-1511367461989-f85a21fda167?w=800&q=80",
        "https://images.unsplash.com/photo-1574482620811-1aa16ffe3c82?w=800&q=80",
        "https://images.unsplash.com/photo-1626379953822-baec19c3accd?w=800&q=80"
    ],
    "other": [
        "https://images.unsplash.com/photo-1550009158-9ebf69173e03?w=800&q=80",
        "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&q=80",
        "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=800&q=80",
        "https://images.unsplash.com/photo-1526738549149-8e07eca270b4?w=800&q=80",
        "https://images.unsplash.com/photo-1535303311164-664fc9ec6532?w=800&q=80"
    ]
}

# إضافة روابط الصور المحلية المكتشفة سابقاً
LOCAL_IMAGES = [
    "images/products/5AjtpPKrp8e3.jpg",
    "images/products/Gq2JNMnegXco.jpg",
    "images/products/kgRdLhjYdmul.jpg",
    "images/products/z3EeMLnHoL92.jpg",
    "images/products/Lf6rD7HuugSb.jpg",
    "images/products/Nwz8VU3re2bv.jpg",
    "images/products/TvEXUBnP9BjG.jpg",
    "images/products/NLsOdopfrsBX.jpg",
    "images/products/rL6yuZKQseW1.jpg"
]

def get_category_key(category_str):
    c = str(category_str).lower()
    if "watch" in c or "wearable" in c: return "smartwatch"
    if "headphone" in c or "earbud" in c or "audio" in c: return "headphones"
    if "home" in c or "living" in c: return "smart-home"
    if "laptop" in c or "pc" in c or "computer" in c: return "laptop"
    if "camera" in c or "security" in c: return "camera"
    return "other"

def fix_images():
    p_path = Path("products.json")
    if not p_path.exists():
        print("❌ products.json not found")
        return

    with open(p_path, "r", encoding="utf-8") as f:
        products = json.load(f)

    print(f"🔄 Processing {len(products)} products...")
    
    used_images = set()
    
    for i, p in enumerate(products):
        cat = get_category_key(p.get("category", "other"))
        pool = TECH_IMAGES.get(cat, TECH_IMAGES["other"])
        
        # محاولة العثور على صورة فريدة من المسبح
        available = [img for img in pool if img not in used_images]
        if not available:
            # إذا نفدت الصور الفريدة، نستخدم مولد صور عالي الجودة مع نص فريد
            name_en = p.get("name", {}).get("en", f"Product {i}")
            image_url = f"https://placehold.co/800x800/0a0d1a/60a5fa?text={name_en.replace(' ', '+')}"
        else:
            image_url = random.choice(available)
        
        # أحياناً نستخدم الصور المحلية لزيادة المصداقية
        if i < len(LOCAL_IMAGES) and LOCAL_IMAGES[i] not in used_images:
            image_url = LOCAL_IMAGES[i]
            
        p["image"] = image_url
        used_images.add(image_url)
        
        # تحديث المعرض أيضاً ليكون فريداً
        p["gallery"] = [
            image_url,
            f"https://placehold.co/800x800/0a0d1a/60a5fa?text={cat.replace('-', '+')}+View+1",
            f"https://placehold.co/800x800/0a0d1a/60a5fa?text={cat.replace('-', '+')}+View+2"
        ]

    with open(p_path, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    # تحديث مجمع المنتجات أيضاً
    pool_path = Path("products_pool.json")
    if pool_path.exists():
        with open(pool_path, "r", encoding="utf-8") as f:
            pool_data = json.load(f)
        
        for p in pool_data:
            cat = get_category_key(p.get("category", "other"))
            p["image"] = random.choice(TECH_IMAGES.get(cat, TECH_IMAGES["other"]))
            
        with open(pool_path, "w", encoding="utf-8") as f:
            json.dump(pool_data, f, ensure_ascii=False, indent=2)
        print("✅ products_pool.json updated")

    print(f"✅ Finished. Assigned {len(used_images)} unique images.")

if __name__ == "__main__":
    fix_images()
