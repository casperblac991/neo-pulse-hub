#!/bin/bash
# =====================================================
# 🔄 جدول التنزيل اليومي التلقائي للمقالات
# يعمل يومياً الساعة 8 صباحاً
# =====================================================

# المتغيرات
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/daily_article_generator.py"
LOG_FILE="$SCRIPT_DIR/daily_articles.log"

# دالة التشغيل
run_daily() {
    echo "============================================================" >> "$LOG_FILE"
    echo "🚀 بدء التنزيل اليومي - $(date)" >> "$LOG_FILE"
    echo "============================================================" >> "$LOG_FILE"
    
    cd "$SCRIPT_DIR"
    python3 "$PYTHON_SCRIPT" >> "$LOG_FILE" 2>&1
    
    echo "✅ заверى التنزيل - $(date)" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
}

# تشغيل الآن (للاختبار)
echo "🔄 تشغيل اختبار التنزيل اليومي..."
cd "$SCRIPT_DIR"
python3 "$PYTHON_SCRIPT"