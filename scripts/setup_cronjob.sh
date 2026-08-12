#!/bin/bash
# =====================================================
# 📅 إعداد Cronjob للتنزيل اليومي التلقائي
# =====================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/../backend/daily_article_generator.py"

# ألوان
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}==============================================${NC}"
echo -e "${GREEN}  🚀 إعداد التنزيل اليومي التلقائي للمقالات${NC}"
echo -e "${GREEN}==============================================${NC}"
echo ""

# 1. عرض Cronjob الحالي
echo -e "${YELLOW}📋 Cronjob الحالي:${NC}"
crontab -l 2>/dev/null || echo "   لا يوجد cronjob حالياً"
echo ""

# 2. إعداد Cronjob جديد
echo -e "${YELLOW}⏰ إعداد Cronjob جديد...${NC}"

# حذف أي cronjob قديم لنفس السكريبت
crontab -l 2>/dev/null | grep -v "daily_article_generator" > /tmp/current_cron

# إضافة Cronjob جديد (يومياً الساعة 8 صباحاً)
cat >> /tmp/current_cron <<EOF
# =============================================
# التنزيل اليومي التلقائي للمقالات
# يعمل يومياً الساعة 8:00 صباحاً
# =============================================
0 8 * * * cd $SCRIPT_DIR && /usr/bin/python3 $PYTHON_SCRIPT >> $SCRIPT_DIR/daily_articles.log 2>&1
EOF

# تطبيق Cronjob
crontab /tmp/current_cron
rm /tmp/current_cron

echo ""
echo -e "${GREEN}✅ تم إعداد Cronjob بنجاح!${NC}"
echo ""

# 3. عرض Cronjob الجديد
echo -e "${YELLOW}📋 Cronjob الجديد:${NC}"
crontab -l
echo ""

echo -e "${GREEN}==============================================${NC}"
echo -e "${GREEN}  ✅ تم تفعيل التنزيل اليومي!${NC}"
echo -e "${GREEN}==============================================${NC}"
echo ""
echo "📅 الجدول: يومياً الساعة 8:00 صباحاً"
echo "📁 السجل: $SCRIPT_DIR/daily_articles.log"
echo "🔧 الأوامر:"
echo "   • عرض السجل: tail -f $SCRIPT_DIR/daily_articles.log"
echo "   • حذف Cron: crontab -e (احذف السطور المتعلقة)"
echo ""