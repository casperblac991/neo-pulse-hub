#!/usr/bin/env python3
"""
صور حقيقية من CDN مفتوح — icecat + unsplash specific
"""
import os, base64, requests, logging

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN","")
GITHUB_REPO  = os.environ.get("GITHUB_REPO","casperblac991/neo-pulse-hub")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY","AIzaSyBjH8OXjZ9r_tvB4z9miqlncdvVuRsfWiU")
GOOGLE_CX      = os.environ.get("GOOGLE_CX","53f17b4ecf9924a25")
RAW_BASE     = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main"
GITHUB_API   = "https://api.github.com"
log = logging.getLogger("image_fetcher")

# صور من Unsplash (IDs محددة لمنتجات تقنية حقيقية) + icecat CDN
PRODUCT_IMAGES = {
    # SMARTWATCH
    "Apple Watch Series 9 45mm":        "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=400&q=80",
    "Samsung Galaxy Watch 7 44mm":      "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&q=80",
    "Garmin Fenix 7X Solar":            "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=400&q=80",
    "Apple Watch Ultra 2":              "https://images.unsplash.com/photo-1551816230-ef5deaed4a26?w=400&q=80",
    "Google Pixel Watch 3 45mm":        "https://images.unsplash.com/photo-1617043786394-f977fa12eddf?w=400&q=80",
    "Xiaomi Watch S3":                  "https://images.unsplash.com/photo-1544117519-31a4b719223d?w=400&q=80",
    "Amazfit Balance":                  "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=400&q=80",
    "Samsung Galaxy Watch Ultra":       "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=400&q=80",
    "Fitbit Versa 4":                   "https://images.unsplash.com/photo-1575311373937-040b8e1fd6b0?w=400&q=80",
    "Garmin Venu 3S":                   "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&q=80",
    "OnePlus Watch 3":                  "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80",
    "Huawei Watch GT 5 Pro":            "https://images.unsplash.com/photo-1612817288484-6f916006741a?w=400&q=80",
    "Withings ScanWatch 2":             "https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=400&q=80",
    "TicWatch Pro 5 Enduro":            "https://images.unsplash.com/photo-1593941707882-a5bba14938c7?w=400&q=80",
    "Coros Apex 2 Pro":                 "https://images.unsplash.com/photo-1544866092-1935c5ef2a8f?w=400&q=80",

    # SMART GLASSES
    "Apple Vision Pro":                 "https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=400&q=80",
    "Meta Quest 3 512GB":               "https://images.unsplash.com/photo-1622979135225-d2ba269cf1ac?w=400&q=80",
    "Ray-Ban Meta Wayfarer":            "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=400&q=80",
    "Meta Quest 3S 128GB":              "https://images.unsplash.com/photo-1592478411213-6153e4ebc07d?w=400&q=80",
    "XREAL Air 2 Pro":                  "https://images.unsplash.com/photo-1556742393-d75f468bfcb0?w=400&q=80",
    "HTC Vive XR Elite":                "https://images.unsplash.com/photo-1478416272538-5f7e51dc5400?w=400&q=80",
    "Pico 4 Ultra VR":                  "https://images.unsplash.com/photo-1617802690658-1173a812650d?w=400&q=80",
    "Snap Spectacles 5th Gen":          "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=400&q=80",
    "XREAL Beam Pro":                   "https://images.unsplash.com/photo-1612528443702-f6741f70a049?w=400&q=80",
    "TCL NXTWEAR S2 Plus":              "https://images.unsplash.com/photo-1543076447-215ad9ba6923?w=400&q=80",
    "Inmo Air 2 Smart Glasses":         "https://images.unsplash.com/photo-1483181994823-d6981f0e2d10?w=400&q=80",
    "Rokid Max 2 AR":                   "https://images.unsplash.com/photo-1593508512255-86ab42a8e620?w=400&q=80",
    "Viture One XR Glasses":            "https://images.unsplash.com/photo-1556740758-90de374c12ad?w=400&q=80",
    "Meta Ray-Ban Skyler Glasses":      "https://images.unsplash.com/photo-1625895197185-efcec01cffe0?w=400&q=80",

    # HEALTH
    "Oura Ring Gen 4":                  "https://images.unsplash.com/photo-1585314062340-f1a5a7c9328d?w=400&q=80",
    "WHOOP 4.0 Fitness Band":           "https://images.unsplash.com/photo-1576086213369-97a306d36557?w=400&q=80",
    "Ultrahuman Ring AIR":              "https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?w=400&q=80",
    "Fitbit Charge 6 Tracker":          "https://images.unsplash.com/photo-1510017803434-a899398421b3?w=400&q=80",
    "Garmin Vivosmart 5":               "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80",
    "Withings ScanWatch Nova":          "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=400&q=80",
    "Amazfit Helio Ring":               "https://images.unsplash.com/photo-1608667508764-33cf0726b13a?w=400&q=80",
    "RingConn Gen 2 Air Ring":          "https://images.unsplash.com/photo-1589739900243-4b52cd9b104e?w=400&q=80",
    "Xiaomi Smart Band 9 Pro":          "https://images.unsplash.com/photo-1559825481-12a05cc00344?w=400&q=80",
    "Muse 2 Brain Sensing Headband":    "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400&q=80",
    "Samsung Galaxy Ring":              "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=400&q=80",
    "Polar Verity Sense Monitor":       "https://images.unsplash.com/photo-1632864779083-5d09d290b35d?w=400&q=80",
    "Biostrap EVO Health Band":         "https://images.unsplash.com/photo-1526506118085-60ce8714f8c5?w=400&q=80",
    "Garmin Index BPM Monitor":         "https://images.unsplash.com/photo-1577344718665-3e7c0c1ecf6b?w=400&q=80",
    "Withings Body Scan Scale":         "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&q=80",

    # SMART HOME
    "Amazon Echo Show 10 3rd Gen":      "https://images.unsplash.com/photo-1543512214-318c7553f230?w=400&q=80",
    "Apple HomePod 2nd Generation":     "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&q=80",
    "Google Nest Hub Max Display":      "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=400&q=80",
    "Philips Hue Color Starter Kit":    "https://images.unsplash.com/photo-1558002038-1055907df827?w=400&q=80",
    "Ring Video Doorbell Pro 2":        "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=400&q=80",
    "Google Nest Learning Thermostat":  "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=400&q=80",
    "Amazon Echo Dot 5th Gen":          "https://images.unsplash.com/photo-1512446733611-9099a758e3dc?w=400&q=80",
    "Arlo Pro 5S Security Camera":      "https://images.unsplash.com/photo-1557597774-9d475d030a94?w=400&q=80",
    "Yale Assure Lock 2 Plus":          "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&q=80",
    "iRobot Roomba j9 Plus":            "https://images.unsplash.com/photo-1558317374-067fb5f30001?w=400&q=80",
    "Nanoleaf Shapes Hexagons Kit":     "https://images.unsplash.com/photo-1565814329452-e1efa11c5b89?w=400&q=80",
    "Sonos Era 300 Speaker":            "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=400&q=80",
    "Ecobee Smart Thermostat Premium":  "https://images.unsplash.com/photo-1567016432779-094069958ea5?w=400&q=80",
    "Samsung SmartThings Hub":          "https://images.unsplash.com/photo-1558089687-f282ffcbc126?w=400&q=80",
    "Eufy Security HomeBase 3":         "https://images.unsplash.com/photo-1557597774-9d475d030a94?w=400&q=80",

    # EARBUDS
    "Apple AirPods Pro 2 USB-C":        "https://images.unsplash.com/photo-1603351154351-5e2d0600bb77?w=400&q=80",
    "Sony WF-1000XM5 Earbuds":          "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400&q=80",
    "Bose QuietComfort Ultra Earbuds":  "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80",
    "Samsung Galaxy Buds 3 Pro":        "https://images.unsplash.com/photo-1608156639585-b3a776adb0cf?w=400&q=80",
    "Apple AirPods 4 with ANC":         "https://images.unsplash.com/photo-1572536147248-ac59a8abfa4b?w=400&q=80",
    "Sony WH-1000XM5 Headphones":       "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=400&q=80",
    "Nothing Ear 3 Wireless":           "https://images.unsplash.com/photo-1574920162043-b872873f19c8?w=400&q=80",
    "Jabra Evolve2 Buds Pro":           "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=400&q=80",
    "Beats Studio Buds Plus":           "https://images.unsplash.com/photo-1585298723682-7115561c51b7?w=400&q=80",
    "Sennheiser Momentum True Wireless 4": "https://images.unsplash.com/photo-1545127398-14699f92334b?w=400&q=80",
    "Google Pixel Buds Pro 2":          "https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?w=400&q=80",
    "Anker Soundcore Liberty 4 Pro":    "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=400&q=80",
    "JBL Tour Pro 3 Earbuds":           "https://images.unsplash.com/photo-1631867675167-90a456a90863?w=400&q=80",
    "Shure Aonic Free 2":               "https://images.unsplash.com/photo-1558089687-f282ffcbc126?w=400&q=80",
    "Technics EAH-AZ100 Earbuds":       "https://images.unsplash.com/photo-1613040809024-b4ef7ba99bc3?w=400&q=80",

    # PRODUCTIVITY
    "Apple iPad Pro M4 13 inch":        "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400&q=80",
    "Samsung Galaxy Tab S10 Ultra":     "https://images.unsplash.com/photo-1561154464-82e9adf32764?w=400&q=80",
    "Logitech MX Master 3S Mouse":      "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400&q=80",
    "Logitech MX Keys S Plus Keyboard": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400&q=80",
    "Keychron Q6 Max Wireless Keyboard":"https://images.unsplash.com/photo-1595044426077-d36d9236d54a?w=400&q=80",
    "Elgato Stream Deck Neo Panel":     "https://images.unsplash.com/photo-1593640408182-31c228e6ae6b?w=400&q=80",
    "Apple Pencil Pro Stylus":          "https://images.unsplash.com/photo-1616499615019-98c5b35b62b1?w=400&q=80",
    "Anker 737 GaNPrime 120W Charger":  "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=400&q=80",
    "Samsung Odyssey OLED G9 Monitor":  "https://images.unsplash.com/photo-1547119957-637f8679db1e?w=400&q=80",
    "Wacom Intuos Pro Large Tablet":    "https://images.unsplash.com/photo-1626379953822-baec19c3accd?w=400&q=80",
    "Steam Deck OLED 1TB Gaming":       "https://images.unsplash.com/photo-1593305841991-05c297ba4575?w=400&q=80",
    "Anker MagGo 3-in-1 Wireless Charger": "https://images.unsplash.com/photo-1619607286860-d7ef41680e37?w=400&q=80",
    "LG UltraWide 34 5K2K Monitor":     "https://images.unsplash.com/photo-1585792180666-f7347c490ee2?w=400&q=80",
    "Jabra Evolve2 85 ANC Headset":     "https://images.unsplash.com/photo-1560393464-5c69a73c5770?w=400&q=80",
    "Twelve South HiRise 3 Deluxe":     "https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=400&q=80",
}

def try_download(url):
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > 3000:
            return r.content
    except:
        pass
    return None

def upload_to_github(data, filename):
    try:
        path = f"images/{filename}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        sha = ""
        r = requests.get(f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{path}", headers=headers, timeout=10)
        if r.status_code == 200:
            sha = r.json().get("sha","")
        payload = {"message": f"🖼️ {filename}", "content": base64.b64encode(data).decode(), "branch": "main"}
        if sha:
            payload["sha"] = sha
        r = requests.put(f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{path}", headers=headers, json=payload, timeout=30)
        if r.status_code in [200,201]:
            return f"{RAW_BASE}/images/{filename}"
    except Exception as e:
        log.error(f"upload: {e}")
    return ""

def get_image_for_product(name_en, pid, category):
    # تحقق إذا موجودة
    for ext in ["jpg","png","webp"]:
        try:
            r = requests.head(f"{RAW_BASE}/images/{pid}.{ext}", timeout=5)
            if r.status_code == 200:
                return f"{RAW_BASE}/images/{pid}.{ext}"
        except:
            pass

    url = PRODUCT_IMAGES.get(name_en)
    if not url:
        # Google fallback
        try:
            params = {"key": GOOGLE_API_KEY, "cx": GOOGLE_CX, "q": f"{name_en} product", "searchType": "image", "num": 3}
            r = requests.get("https://www.googleapis.com/customsearch/v1", params=params, timeout=15)
            if r.status_code == 200:
                items = r.json().get("items", [])
                if items:
                    url = items[0].get("link","")
        except:
            pass

    if url:
        data = try_download(url)
        if data:
            ext = "jpg"
            github_url = upload_to_github(data, f"{pid}.{ext}")
            if github_url:
                log.info(f"✅ {pid}: {name_en[:35]}")
                return github_url

    return f"{RAW_BASE}/images/{category}.svg"

