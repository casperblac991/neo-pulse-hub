from pathlib import Path
from PIL import Image

paths = [
    'images/products/kgRdLhjYdmul.jpg',
    'images/products/z3EeMLnHoL92.jpg',
    'images/products/Lf6rD7HuugSb.jpg',
    'images/products/Nwz8VU3re2bv.jpg',
    'images/products/TvEXUBnP9BjG.jpg',
    'images/products/NLsOdopfrsBX.jpg',
    'images/products/rL6yuZKQseW1.jpg',
]

for raw_path in paths:
    path = Path(raw_path)
    with Image.open(path) as image:
        rgb = image.convert('RGB')
        rgb.save(path, format='JPEG', quality=90, optimize=True, progressive=True)
    print(f'normalized {path}')
