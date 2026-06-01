#!/usr/bin/env python3
"""
تحديث صور المنتجات - كل منتج يحصل على صورة فريدة
"""
import json

ALL_IMAGES = [
    "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&q=80",
    "https://images.unsplash.com/photo-1434056886845-dac89ffe9b56?w=600&q=80",
    "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=600&q=80",
    "https://images.unsplash.com/photo-1617043786394-f977fa12eddf?w=600&q=80",
    "https://images.unsplash.com/photo-1579586337278-3bef81640edd?w=600&q=80",
    "https://images.unsplash.com/photo-1551816230-ef5deaed4a26?w=600&q=80",
    "https://images.unsplash.com/photo-1584438784894-089d6a62b8fa?w=600&q=80",
    "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=600&q=80",
    "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&q=80",
    "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=600&q=80",
    "https://images.unsplash.com/photo-1590658268037-6bf12165a8ae?w=600&q=80",
    "https://images.unsplash.com/photo-1611930022073-b7a4ba5fcc75?w=600&q=80",
    "https://images.unsplash.com/photo-1510017803434-a899398429b3?w=600&q=80",
    "https://images.unsplash.com/photo-1505033575518-a36ea4c74989?w=600&q=80",
    "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=600&q=80",
    "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&q=80",
    "https://images.unsplash.com/photo-1572536147248-ac59a8abfa4b?w=600&q=80",
    "https://images.unsplash.com/photo-1585565804112-f201f68c48b4?w=600&q=80",
    "https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?w=600&q=80",
    "https://images.unsplash.com/photo-1524678606370-a47ad25cb82a?w=600&q=80",
    "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=600&q=80",
    "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&q=80",
    "https://images.unsplash.com/photo-1556909172-54557c7e4fb7?w=600&q=80",
    "https://images.unsplash.com/photo-1558002038-1055907df827?w=600&q=80",
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=600&q=80",
    "https://images.unsplash.com/photo-1567721913486-6585f069b332?w=600&q=80",
    "https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=600&q=80",
    "https://images.unsplash.com/photo-1576678927484-cc907957088c?w=600&q=80",
    "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=600&q=80",
    "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600&q=80",
    "https://images.unsplash.com/photo-1581287053822-fd7bf4f4bfec?w=600&q=80",
    "https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=600&q=80",
    "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=600&q=80",
    "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&q=80",
    "https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=600&q=80",
    "https://images.unsplash.com/photo-1593508512255-86ab42a8e620?w=600&q=80",
    "https://images.unsplash.com/photo-1600096194534-95cf5ece04cf?w=600&q=80",
    "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&q=80",
    "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=600&q=80",
    "https://images.unsplash.com/photo-1511367461989-f85a21fda167?w=600&q=80",
    "https://images.unsplash.com/photo-1574482620811-1aa16ffe3c82?w=600&q=80",
    "https://images.unsplash.com/photo-1626379953822-baec19c3accd?w=600&q=80",
    "https://images.unsplash.com/photo-1577803645773-f96470509666?w=600&q=80",
    "https://images.unsplash.com/photo-1558060370-d64edd50ad47?w=600&q=80",
    "https://images.unsplash.com/photo-1566576912321-d58ddd7a6088?w=600&q=80",
    "https://images.unsplash.com/photo-1517836357463-d25dfeac3408?w=600&q=80",
    "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=600&q=80",
    "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=600&q=80",
    "https://images.unsplash.com/photo-1497366216548-37526070297c?w=600&q=80",
    "https://images.unsplash.com/photo-1489824904134-891ab64532f1?w=600&q=80",
    "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=600&q=80",
    "https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=600&q=80",
    "https://images.unsplash.com/photo-1535070218759-3bef81640edd?w=600&q=80",
    "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=600&q=80",
    "https://images.unsplash.com/photo-1558466941-8f9a3f5a4a0c?w=600&q=80",
    "https://images.unsplash.com/photo-1584100936595-c0654b55a2e2?w=600&q=80",
    "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=600&q=80",
    "https://images.unsplash.com/photo-1585386959984-a4155224a1ad?w=600&q=80",
    "https://images.unsplash.com/photo-1558758864-4af60ea4de97?w=600&q=80",
    "https://images.unsplash.com/photo-1516280440614-379a5dc9db41?w=600&q=80",
    "https://images.unsplash.com/photo-1544117519-31a4b719223d?w=600&q=80",
    "https://images.unsplash.com/photo-1513060734089-75685bbb2b91?w=600&q=80",
    "https://images.unsplash.com/photo-1488731498841-5d74b77d3a70?w=600&q=80",
    "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=600&q=80",
    "https://images.unsplash.com/photo-1591378603223-15e1d3e4e5c6?w=600&q=80",
    "https://images.unsplash.com/photo-1546435770-a3be85d8d0ce?w=600&q=80",
]

def update_product_images():
    with open('products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"📦 تحديث {len(products)} منتج...")
    
    for i, product in enumerate(products):
        image_index = i % len(ALL_IMAGES)
        product['image'] = ALL_IMAGES[image_index]
    
    with open('products.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"✅ تم تحديث جميع {len(products)} منتج")
    
    from collections import Counter
    images = [p.get('image', '') for p in products]
    counts = Counter(images)
    repeated = {img: c for img, c in counts.items() if c > 1}
    
    print(f"📊 صور فريدة: {len(set(images))}")
    print(f"⚠️ صور متكررة: {len(repeated)}")
    
    if not repeated:
        print("✅ لا توجد صور متكررة!")

if __name__ == "__main__":
    update_product_images()
