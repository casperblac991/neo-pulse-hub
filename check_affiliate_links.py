import os
import re
from bs4 import BeautifulSoup

def check_and_update_affiliate_links(html_file_path, amazon_tag='neopulsehub-20'):
    with open(html_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    updated = False

    # Check Amazon links
    for a_tag in soup.find_all('a', href=re.compile(r'amazon\.com')):
        original_href = a_tag['href']
        if 'tag=' not in original_href:
            if '?' in original_href:
                a_tag['href'] = f"{original_href}&tag={amazon_tag}"
            else:
                a_tag['href'] = f"{original_href}?tag={amazon_tag}"
            updated = True
        elif f'tag={amazon_tag}' not in original_href:
            a_tag['href'] = re.sub(r'tag=[^&]*', f'tag={amazon_tag}', original_href)
            updated = True

    # Check AliExpress links (simple check for now, can be expanded)
    for a_tag in soup.find_all('a', href=re.compile(r'aliexpress\.com')):
        # For AliExpress, we'll just ensure the link is present and valid
        # More advanced validation might involve checking specific affiliate parameters
        if a_tag['href']:
            # Placeholder for future AliExpress tag insertion if needed
            pass

    if updated:
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print(f"✅ Updated affiliate links in: {html_file_path}")
    else:
        print(f"ℹ️ No changes needed for affiliate links in: {html_file_path}")

def main():
    html_files = []
    for root, _, files in os.walk('/home/ubuntu/neo-pulse-hub'):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))

    for html_file in html_files:
        check_and_update_affiliate_links(html_file)

if __name__ == '__main__':
    main()
