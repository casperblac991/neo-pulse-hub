# NEO PULSE HUB - bot fixes to apply (v3.1 -> v3.2)
# File: backend/customer_bot.py

# FIX 1 - /products crash (line ~190):
# catalog stores name as {"name": {"ar": "...", "en": "..."}} but code reads p['name_ar'] -> KeyError -> no reply.
# Replace in cmd_products:
OLD:
        f"• *{p['name_ar']}* — ${p['price']} ⭐{p.get('rating',0)}\n"
NEW:
        f"• *{product_name(p)}* — ${p['price']} ⭐{p.get('rating',0)}\n"

# And add this helper above cmd_products:
def product_name(p):
    name = p.get("name", {})
    if isinstance(name, dict):
        return name.get("ar") or name.get("en") or "منتج"
    return str(name or p.get("name_ar", "") or p.get("name_en", "") or "منتج")

# FIX 2 - users stuck on "thinking..." (line ~225):
# AI sometimes returns broken Markdown -> edit_text fails -> user gets NO reply forever.
# Replace:
OLD:
    await msg.edit_text(answer, parse_mode=ParseMode.MARKDOWN)
NEW:
    try:
        await msg.edit_text(answer, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        log.warning(f"Markdown edit failed ({e}) - plain text fallback")
        await msg.edit_text(answer)

# FIX 3 - never leave user with empty reply. Replace:
OLD:
    if not answer:
        answer = "عذراً، لم أستطع فهم ذلك. هل يمكنك توضيح سؤالك؟"
NEW:
    if not answer:
        answer = ("عذراً، تواجهني صعوبة مؤقتة. جرّب صياغة سؤالك بشكل آخر، "
                  f"أو تصفح منتجاتنا:\n{SITE_URL}/products.html")
