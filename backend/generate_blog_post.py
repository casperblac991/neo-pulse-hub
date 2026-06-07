import json
import os
from datetime import datetime

BLOG_INDEX_AR = 'blog_index_ar.html'

def update_blog():
    print("📝 Updating Blog with new report...")
    if not os.path.exists(BLOG_INDEX_AR):
        print("❌ blog_index_ar.html not found!")
        return

    with open(BLOG_INDEX_AR, 'r', encoding='utf-8') as f:
        content = f.read()

    new_post = {
        "id": 5,
        "title": "تقرير تحديث Neo Pulse Hub الشامل",
        "description": "تفاصيل عملية إعادة الهيكلة الكبرى، تحسين الأمان، وتحديث نظام المنتجات لعام 2026.",
        "category": "news",
        "categoryName": "أخبار المتجر",
        "rating": 5.0,
        "link": "blog/update-report-2026.html",
        "icon": "🚀",
        "date": datetime.now().strftime("%d %B %Y")
    }

    # Find the articles array in JS
    pattern = r'const articles = \[(.*?)\];'
    import re
    match = re.search(pattern, content, re.DOTALL)
    if match:
        articles_json = "[" + match.group(1) + "]"
        # This is JS, not pure JSON, but for simple structures it might work or we use string manipulation
        insertion = f"""\n            {{
                id: 5,
                title: "{new_post['title']}",
                description: "{new_post['description']}",
                category: "{new_post['category']}",
                categoryName: "{new_post['categoryName']}",
                rating: {new_post['rating']},
                link: "{new_post['link']}",
                icon: "{new_post['icon']}",
                date: "{new_post['date']}"
            }},"""
        new_content = content.replace('const articles = [', 'const articles = [' + insertion)
        
        with open(BLOG_INDEX_AR, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ Blog index updated.")

if __name__ == "__main__":
    update_blog()
