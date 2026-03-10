#!/usr/bin/env python3
"""
يجيب صور حقيقية لكل منتج ويرفعها على GitHub
الطريقة: Gemini يعطي روابط صور مباشرة من مواقع موثوقة
"""
import os, json, base64, requests, time, re, logging

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GITHUB_TOKEN   = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO    = os.environ.get("GITHUB_REPO", "casperblac991/neo-pulse-hub")
RAW_BASE       = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main"
GITHUB_API     = "https://api.github.com"

log = logging.getLogger("image_fetcher")

# ═══════════════════════════════════════════════════════
# مواقع صور منتجات تقنية موثوقة وتسمح بالتحميل
# ═══════════════════════════════════════════════════════
PRODUCT_IMAGES = {
    # SMARTWATCH
    "Apple Watch Series 9 45mm":        "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/watch-s9-digitalmat-gallery-1-202309_GEO_US?wid=800&hei=800&fmt=jpeg",
    "Samsung Galaxy Watch 7 44mm":      "https://image-us.samsung.com/SamsungUS/home/mobile/galaxy-watch/07112024/gallery/GW7-47mm-cream-front.jpg",
    "Garmin Fenix 7X Solar":            "https://res.garmin.com/transform/image/upload/b_rgb:FFFFFF,c_pad,dpr_2.0,f_auto,h_400,q_auto,w_400/c_pad,h_400,w_400/v1/Product_Images/en/products/010-02541-23/v/cf-xl-010-02541-23-front-left.png",
    "Apple Watch Ultra 2":              "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/watch-ultra2-digitalmat-gallery-1-202309_GEO_US?wid=800&hei=800&fmt=jpeg",
    "Google Pixel Watch 3 45mm":        "https://lh3.googleusercontent.com/iQJwCKa2I9v4s9LF9X8UoMNDqmHQGCGMoHAcKGVkMPM=w800",
    "Xiaomi Watch S3":                  "https://i01.appmifile.com/webfile/globalimg/products/m/xiaomi-watch-s3/section1.png",
    "Amazfit Balance":                  "https://cdn.amazfit.com/images/product/balance/balance-1.png",
    "Samsung Galaxy Watch Ultra":       "https://image-us.samsung.com/SamsungUS/home/mobile/galaxy-watch/07112024/gallery/GWU-titaniumwhite-front.jpg",
    "Fitbit Versa 4":                   "https://www.fitbit.com/global/content/assets/images/products/versa4/pdp/black-aluminum.png",
    "Garmin Venu 3S":                   "https://res.garmin.com/transform/image/upload/b_rgb:FFFFFF,c_pad,dpr_2.0,f_auto,h_400,q_auto,w_400/v1/Product_Images/en/products/010-02785-10/v/cf-xl-010-02785-10-front-left.png",
    "OnePlus Watch 3":                  "https://image.oneplus.net/mimage/oneplusstatic/static/img/product/watch3/kv.png",
    "Huawei Watch GT 5 Pro":            "https://consumer.huawei.com/content/dam/huawei-cbg-site/common/mkt/pdp/wearables/watch-gt5-pro/img/huawei-watch-gt5-pro-kv.png",
    "Withings ScanWatch 2":             "https://www.withings.com/medias/sys_master/root/hc4/h29/8832751616030.png",
    "TicWatch Pro 5 Enduro":            "https://www.mobvoi.com/cdn/shop/products/TicWatch-Pro-5-Enduro-01.png",
    "Coros Apex 2 Pro":                 "https://cdn.shopify.com/s/files/1/0598/8708/5119/files/APEX2Pro_Black_Front.png",

    # SMART GLASSES
    "Apple Vision Pro":                 "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/vision-pro-gallery-1-202401_GEO_US?wid=800&hei=800&fmt=jpeg",
    "Meta Quest 3 512GB":               "https://scontent.oculuscdn.com/v/t64.5771-25/355178527_10152234977050511_7870527032636952_n.jpg",
    "Ray-Ban Meta Wayfarer":            "https://static.lenscrafters.com/is/image/LensCrafters/0RB2140_901_58-png.png",
    "Meta Quest 3S 128GB":              "https://scontent.oculuscdn.com/v/t64.5771-25/quest3s.jpg",
    "XREAL Air 2 Pro":                  "https://www.xreal.com/assets/images/air2pro/air2pro-hero.png",
    "HTC Vive XR Elite":                "https://www.vive.com/medias/sys_master/htcviveroot/h8e/hf4/9543338082334.png",
    "Pico 4 Ultra VR":                  "https://www.picoxr.com/static/images/pico4ultra/kv.png",
    "Snap Spectacles 5th Gen":          "https://assets.snapchat.com/adscore/spectacles/spectacles5.png",
    "XREAL Beam Pro":                   "https://www.xreal.com/assets/images/beampro/beam-pro-hero.png",
    "TCL NXTWEAR S2 Plus":              "https://www.tcl.com/content/dam/tcl/product-images/nxtwear-s2-plus.png",
    "Rokid Max 2 AR":                   "https://www.rokid.com/images/max2/rokid-max2.png",
    "Viture One XR Glasses":            "https://www.viture.com/images/one-xr.png",

    # HEALTH
    "Oura Ring Gen 4":                  "https://ouraring.com/images/ring-gen4-silver.png",
    "WHOOP 4.0 Fitness Band":           "https://cdn.shopify.com/s/files/1/0261/4929/9423/files/whoop4-black.png",
    "Ultrahuman Ring AIR":              "https://cdn.shopify.com/s/files/1/0607/4956/9052/files/ultrahuman-ring-air.png",
    "Fitbit Charge 6 Tracker":          "https://www.fitbit.com/global/content/assets/images/products/charge6/pdp/black.png",
    "Samsung Galaxy Ring":              "https://image-us.samsung.com/SamsungUS/home/mobile/galaxy-ring/08062024/gallery/titanium-black.jpg",
    "Amazfit Helio Ring":               "https://cdn.amazfit.com/images/product/helio-ring/helio-ring-1.png",
    "Xiaomi Smart Band 9 Pro":          "https://i01.appmifile.com/webfile/globalimg/products/m/xiaomi-smart-band-9-pro/product.png",
    "RingConn Gen 2 Air Ring":          "https://ringconn.com/cdn/shop/products/gen2-air.png",

    # SMART HOME
    "Amazon Echo Show 10 3rd Gen":      "https://m.media-amazon.com/images/I/51VuJiHAVWL._AC_SX679_.jpg",
    "Apple HomePod 2nd Generation":     "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/homepod-2023-gallery-1-202302_GEO_US?wid=800&hei=800&fmt=jpeg",
    "Google Nest Hub Max Display":      "https://lh3.googleusercontent.com/nest-hub-max.jpg",
    "Philips Hue Color Starter Kit":    "https://www.philips-hue.com/content/dam/b2c/product-images/starter-kit.png",
    "Ring Video Doorbell Pro 2":        "https://m.media-amazon.com/images/I/41q7kFUKhPL._AC_SX679_.jpg",
    "Amazon Echo Dot 5th Gen":          "https://m.media-amazon.com/images/I/51CxiLCvJnL._AC_SX679_.jpg",
    "iRobot Roomba j9 Plus":            "https://d3gqasl9vmjfd8.cloudfront.net/roomba-j9-plus.png",
    "Sonos Era 300 Speaker":            "https://www.sonos.com/en-us/shop/era300",
    "Nanoleaf Shapes Hexagons Kit":     "https://images.nanoleaf.me/hexagons-kit.png",

    # EARBUDS
    "Apple AirPods Pro 2 USB-C":        "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/MQD83?wid=800&hei=800&fmt=jpeg",
    "Sony WF-1000XM5 Earbuds":          "https://www.sony.com/image/WF-1000XM5_front.png",
    "Bose QuietComfort Ultra Earbuds":  "https://assets.bose.com/content/dam/Bose_DAM/Web/consumer_electronics/qc-ultra-earbuds.png",
    "Samsung Galaxy Buds 3 Pro":        "https://image-us.samsung.com/SamsungUS/home/audio/galaxy-buds/08062024/gallery/buds3pro-silver.jpg",
    "Apple AirPods 4 with ANC":         "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/airpods4-anc?wid=800&hei=800&fmt=jpeg",
    "Sony WH-1000XM5 Headphones":       "https://www.sony.com/image/WH-1000XM5_Black_front.png",
    "Nothing Ear 3 Wireless":           "https://cdn.nothing.tech/images/ear3.png",
    "Google Pixel Buds Pro 2":          "https://lh3.googleusercontent.com/pixel-buds-pro2.jpg",
    "Anker Soundcore Liberty 4 Pro":    "https://cdn.soundcore.com/images/liberty4pro.png",
    "JBL Tour Pro 3 Earbuds":           "https://www.jbl.com/images/tour-pro-3.png",
    "Beats Studio Buds Plus":           "https://www.beatsbydre.com/content/dam/beats/web/product/earbuds/studio-buds-plus.png",

    # PRODUCTIVITY
    "Apple iPad Pro M4 13 inch":        "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/ipad-pro-13-202405?wid=800&hei=800&fmt=jpeg",
    "Samsung Galaxy Tab S10 Ultra":     "https://image-us.samsung.com/SamsungUS/home/mobile/galaxy-tab/08082024/gallery/tab-s10-ultra-gray.jpg",
    "Logitech MX Master 3S Mouse":      "https://resource.logitech.com/content/dam/logitech/en/products/mice/mx-master-3s/gallery/mx-master-3s-mouse-top-view-graphite.png",
    "Logitech MX Keys S Plus Keyboard": "https://resource.logitech.com/content/dam/logitech/en/products/keyboards/mx-keys-s/gallery/mx-keys-s-top-view.png",
    "Apple Pencil Pro Stylus":          "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/MUWY3?wid=800&hei=800&fmt=jpeg",
    "Steam Deck OLED 1TB Gaming":       "https://cdn.cloudflare.steamstatic.com/steamdeck/images/steamdeck-oled.png",
    "Samsung Odyssey OLED G9 Monitor":  "https://image-us.samsung.com/SamsungUS/home/computing/monitors/gaming/08072024/gallery/odyssey-oled-g9-front.jpg",
    "Wacom Intuos Pro Large Tablet":    "https://www.wacom.com/content/dam/product/intuos-pro-l.png",
}

def try_download(url: str) -> bytes | None:
    """يحاول يحمّل الصورة"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
        }
        r = requests.get(url, headers=headers, timeout=20, stream=True, allow_redirects=True)
        if r.status_code == 200:
            ctype = r.headers.get("content-type","")
            if "image" in ctype or url.endswith((".jpg",".jpeg",".png",".webp")):
                data = r.content
                if len(data) > 3000:
                    return data
    except Exception as e:
        log.debug(f"download failed: {e}")
    return None

def upload_to_github(data: bytes, filename: str) -> str:
    """يرفع الصورة على GitHub"""
    try:
        path = f"images/{filename}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        sha = ""
        r = requests.get(f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{path}", headers=headers, timeout=10)
        if r.status_code == 200:
            sha = r.json().get("sha","")
        payload = {
            "message": f"🖼️ {filename}",
            "content": base64.b64encode(data).decode(),
            "branch": "main"
        }
        if sha:
            payload["sha"] = sha
        r = requests.put(f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{path}", headers=headers, json=payload, timeout=30)
        if r.status_code in [200,201]:
            return f"{RAW_BASE}/images/{filename}"
    except Exception as e:
        log.error(f"upload error: {e}")
    return ""

def get_image_for_product(name_en: str, pid: str, category: str) -> str:
    """يجيب صورة حقيقية للمنتج ويرفعها GitHub"""
    
    # 1. جرب الرابط المحدد في القاموس
    if name_en in PRODUCT_IMAGES:
        url = PRODUCT_IMAGES[name_en]
        data = try_download(url)
        if data:
            ext = "jpg" if "jpg" in url or "jpeg" in url else "png"
            filename = f"{pid}.{ext}"
            github_url = upload_to_github(data, filename)
            if github_url:
                log.info(f"✅ {pid}: {name_en[:30]}")
                return github_url

    # 2. جرب Google Custom Search
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY","")
    GOOGLE_CX = os.environ.get("GOOGLE_CX","")
    if GOOGLE_API_KEY and GOOGLE_CX:
        try:
            params = {
                "key": GOOGLE_API_KEY, "cx": GOOGLE_CX,
                "q": f"{name_en} product transparent background",
                "searchType": "image", "num": 5,
                "imgSize": "large", "imgType": "photo",
            }
            r = requests.get("https://www.googleapis.com/customsearch/v1", params=params, timeout=15)
            if r.status_code == 200:
                for item in r.json().get("items",[]):
                    url = item.get("link","")
                    if url and url.startswith("http"):
                        data = try_download(url)
                        if data:
                            filename = f"{pid}.jpg"
                            github_url = upload_to_github(data, filename)
                            if github_url:
                                log.info(f"✅ Google: {pid}: {name_en[:30]}")
                                return github_url
        except Exception as e:
            log.warning(f"Google search error: {e}")

    # 3. SVG fallback من GitHub
    return f"{RAW_BASE}/images/{category}.svg"

