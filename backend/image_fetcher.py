#!/usr/bin/env python3
"""
صور حقيقية من DuckDuckGo Image Search — مجاني بدون API
"""
import os, base64, requests, logging, re, json

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN","")
GITHUB_REPO  = os.environ.get("GITHUB_REPO","casperblac991/neo-pulse-hub")
RAW_BASE     = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main"
GITHUB_API   = "https://api.github.com"
log = logging.getLogger("image_fetcher")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

def ddg_image_search(query: str) -> list:
    """يبحث في DuckDuckGo عن صور ويرجع قائمة روابط"""
    try:
        session = requests.Session()
        session.headers.update(HEADERS)

        # خطوة 1: جيب vqd token
        r = session.get(
            "https://duckduckgo.com/",
            params={"q": query},
            timeout=10
        )
        vqd = re.search(r'vqd=([\d-]+)', r.text)
        if not vqd:
            # جرب طريقة بديلة
            vqd = re.search(r'"vqd":"([\d-]+)"', r.text)
        if not vqd:
            log.warning("DuckDuckGo: no vqd token")
            return []

        vqd_token = vqd.group(1)

        # خطوة 2: ابحث عن الصور
        r2 = session.get(
            "https://duckduckgo.com/i.js",
            params={
                "l": "us-en",
                "o": "json",
                "q": query,
                "vqd": vqd_token,
                "f": ",,,",
                "p": "1",
            },
            headers={**HEADERS, "Referer": "https://duckduckgo.com/"},
            timeout=15
        )

        if r2.status_code == 200:
            data = r2.json()
            results = data.get("results", [])
            urls = []
            for item in results[:8]:
                url = item.get("image", "")
                width = item.get("width", 0)
                height = item.get("height", 0)
                # فلتر: صور مربعة أو شبه مربعة (صور المنتجات عادة مربعة)
                if url and width >= 200 and height >= 200:
                    urls.append(url)
            return urls
    except Exception as e:
        log.warning(f"DuckDuckGo error: {e}")
    return []


def try_download(url: str) -> bytes | None:
    """يحمّل الصورة"""
    try:
        r = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "image/*,*/*",
                "Referer": "https://duckduckgo.com/",
            },
            timeout=15,
            allow_redirects=True
        )
        if r.status_code == 200:
            ctype = r.headers.get("content-type", "")
            data = r.content
            if len(data) > 5000 and ("image" in ctype or url.lower().endswith((".jpg",".jpeg",".png",".webp"))):
                return data
    except Exception as e:
        log.debug(f"download error: {e}")
    return None


def upload_to_github(data: bytes, filename: str) -> str:
    """يرفع الصورة على GitHub"""
    try:
        path = f"images/{filename}"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        sha = ""
        r = requests.get(f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{path}", headers=headers, timeout=10)
        if r.status_code == 200:
            sha = r.json().get("sha", "")

        payload = {
            "message": f"🖼️ Product image: {filename}",
            "content": base64.b64encode(data).decode(),
            "branch": "main"
        }
        if sha:
            payload["sha"] = sha

        r = requests.put(
            f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{path}",
            headers=headers,
            json=payload,
            timeout=30
        )
        if r.status_code in [200, 201]:
            return f"{RAW_BASE}/images/{filename}"
    except Exception as e:
        log.error(f"GitHub upload error: {e}")
    return ""


def get_image_for_product(name_en: str, pid: str, category: str) -> str:
    """
    الوظيفة الرئيسية:
    1. يبحث في DuckDuckGo عن صورة حقيقية للمنتج
    2. يحمّل أفضل صورة
    3. يرفعها على GitHub
    4. يرجع raw URL مضمون
    """
    # تحقق إذا موجودة مسبقاً
    for ext in ["jpg", "png", "webp"]:
        try:
            r = requests.head(f"{RAW_BASE}/images/{pid}.{ext}", timeout=5)
            if r.status_code == 200:
                log.info(f"✅ Cached: {pid}")
                return f"{RAW_BASE}/images/{pid}.{ext}"
        except:
            pass

    # ابحث في DuckDuckGo
    queries = [
        f"{name_en} product photo official",
        f"{name_en} smartwatch earbuds official image",
        f"{name_en}",
    ]

    for query in queries:
        urls = ddg_image_search(query)
        for url in urls:
            # تجنب صور Pinterest وصور صغيرة
            if any(skip in url for skip in ["pinterest", "pinimg", "placeholder", "icon", "thumb"]):
                continue

            data = try_download(url)
            if data:
                ext = "png" if ".png" in url.lower() else "jpg"
                github_url = upload_to_github(data, f"{pid}.{ext}")
                if github_url:
                    log.info(f"✅ {pid}: {name_en[:35]} → {url[:50]}")
                    return github_url
            break  # جرب الرابط الأول فقط من كل query

    log.warning(f"⚠️ No image found for: {name_en}")
    return f"{RAW_BASE}/images/{category}.svg"

