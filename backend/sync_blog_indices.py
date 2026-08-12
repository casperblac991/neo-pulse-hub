import json
import re
from pathlib import Path

def sync_indices():
    articles_data_file = Path("articles_data.json")
    if not articles_data_file.exists():
        print("Error: articles_data.json not found")
        return

    with open(articles_data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both formats (list or dict)
    if isinstance(data, list):
        ar_articles = data
        en_articles = []
    else:
        ar_articles = data.get('ar', [])
        en_articles = data.get('en', [])

    # Function to update a specific index file
    def update_index(file_path, articles, lang='ar'):
        if not Path(file_path).exists():
            print(f"Warning: {file_path} not found")
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Format articles for JS array
        js_articles = []
        for i, a in enumerate(reversed(articles)):
            # Map icons based on category
            icons = {
                'smartwatch': '⌚',
                'earbuds': '🎧',
                'smart-home': '🏠',
                'health': '❤️',
                'productivity': '💼',
                'gaming': '🎮',
                'cameras': '📷',
                'news': '🚀'
            }
            
            # Map category names
            cat_names = {
                'ar': {
                    'smartwatch': 'ساعات ذكية',
                    'earbuds': 'سماعات',
                    'smart-home': 'منزل ذكي',
                    'health': 'صحة ذكية',
                    'productivity': 'إنتاجية',
                    'gaming': 'ألعاب',
                    'cameras': 'كاميرات',
                    'news': 'أخبار'
                },
                'en': {
                    'smartwatch': 'Smart Watches',
                    'earbuds': 'Earbuds',
                    'smart-home': 'Smart Home',
                    'health': 'Health Tech',
                    'productivity': 'Productivity',
                    'gaming': 'Gaming',
                    'cameras': 'Cameras',
                    'news': 'News'
                }
            }

            cat = a.get('category', 'news')
            article_obj = {
                "id": len(articles) - i,
                "title": a.get('title', ''),
                "description": f"مراجعة شاملة لـ {a.get('product_name', '')}" if lang == 'ar' else f"Comprehensive review of {a.get('product_name', '')}",
                "category": cat,
                "categoryName": cat_names[lang].get(cat, cat),
                "rating": a.get('rating', 4.5),
                "link": a.get('path', ''),
                "icon": icons.get(cat, '📝'),
                "date": a.get('date', '')
            }
            js_articles.append(article_obj)

        # Use regex to replace the articles array in the HTML file
        articles_json = json.dumps(js_articles, ensure_ascii=False, indent=12)
        # Fix indentation for the final ]
        articles_json = articles_json.replace('            ]', '        ]')
        
        pattern = r'const articles = \[.*?\];'
        replacement = f'const articles = {articles_json};'
        
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        # Update last update date
        date_pattern = r'تحديث آخر:.*?</p>' if lang == 'ar' else r'Last update:.*?</p>'
        from datetime import datetime
        today = datetime.now().strftime('%d %B %Y')
        date_replacement = f'تحديث آخر: {today}</p>' if lang == 'ar' else f'Last update: {today}</p>'
        new_content = re.sub(date_pattern, date_replacement, new_content)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Updated {file_path} with {len(articles)} articles")

    # Update both indices
    update_index("blog_index_ar.html", ar_articles, 'ar')
    update_index("blog_index_en.html", en_articles, 'en')

if __name__ == "__main__":
    sync_indices()
