#!/usr/bin/env python3
"""إخبار محركات البحث بوجود محتوى جديد"""
import urllib.request, urllib.parse

SITEMAP = "https://neo-pulse-hub.it.com/sitemap.xml"

engines = [
    f"https://www.google.com/ping?sitemap={urllib.parse.quote(SITEMAP)}",
    f"https://www.bing.com/ping?sitemap={urllib.parse.quote(SITEMAP)}",
]

for url in engines:
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            print(f"✅ Pinged: {url[:50]}... → {r.status}")
    except Exception as e:
        print(f"⚠️  {url[:50]}... → {e}")

print("✅ Done — search engines notified")
