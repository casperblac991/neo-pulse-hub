#!/bin/bash
# ══════════════════════════════════════════════════════════════════
# NEO PULSE HUB — تشغيل جميع البوتات
# الاستخدام: bash run_all.sh [start|stop|restart|status|logs]
# ══════════════════════════════════════════════════════════════════

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGS="$DIR/logs"
PIDS="$DIR/pids"

mkdir -p "$LOGS" "$PIDS"

# ── ألوان ──────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

banner() {
echo -e "${CYAN}${BOLD}"
cat << 'EOF'
╔══════════════════════════════════════════════════════════╗
║          NEO PULSE HUB — Bot Manager v2.0               ║
║       مدير بوتات المتجر الذكي — كل البوتات معاً         ║
╚══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"
}

# ── تعريف البوتات ──────────────────────────────────────────────────
declare -A BOTS
BOTS["customer"]="customer_bot.py"
BOTS["admin"]="admin_bot.py"
BOTS["recommendation"]="recommendation_bot.py"
BOTS["supplier"]="supplier_bot.py"
BOTS["webhook"]="webhook_server.py"

declare -A BOT_NAMES
BOT_NAMES["customer"]="🤖 خدمة العملاء"
BOT_NAMES["admin"]="👑 لوحة الإدارة"
BOT_NAMES["recommendation"]="🎯 التوصيات"
BOT_NAMES["supplier"]="📦 الموردين"
BOT_NAMES["webhook"]="🌐 API Server"

# ── دوال مساعدة ───────────────────────────────────────────────────

check_env() {
    if [ ! -f "$DIR/.env" ]; then
        echo -e "${YELLOW}⚠️  ملف .env غير موجود!${NC}"
        echo -e "   انسخ المثال: ${CYAN}cp .env.example .env${NC}"
        echo -e "   ثم عبّئ المتغيرات الضرورية"
        exit 1
    fi
    source "$DIR/.env"
    if [ -z "$TELEGRAM_TOKEN" ] && [ -z "$CUSTOMER_BOT_TOKEN" ]; then
        echo -e "${RED}❌ TELEGRAM_TOKEN غير موجود في .env${NC}"
        exit 1
    fi
    if [ -z "$GEMINI_API_KEY" ]; then
        echo -e "${YELLOW}⚠️  GEMINI_API_KEY غير موجود — ميزات AI ستكون معطلة${NC}"
    fi
}

is_running() {
    local name=$1
    local pid_file="$PIDS/${name}.pid"
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0  # running
        fi
    fi
    return 1  # not running
}

start_bot() {
    local name=$1
    local script="${BOTS[$name]}"
    local label="${BOT_NAMES[$name]}"
    local log_file="$LOGS/${name}.log"
    local pid_file="$PIDS/${name}.pid"

    if is_running "$name"; then
        echo -e "  ${YELLOW}⏭  $label — يعمل بالفعل${NC}"
        return
    fi

    # تشغيل في الخلفية
    if [ "$name" = "webhook" ]; then
        nohup python3 "$DIR/$script" >> "$log_file" 2>&1 &
    else
        nohup python3 "$DIR/$script" >> "$log_file" 2>&1 &
    fi

    local pid=$!
    echo $pid > "$pid_file"
    sleep 1

    if is_running "$name"; then
        echo -e "  ${GREEN}✅ $label — تشغيل (PID: $pid)${NC}"
    else
        echo -e "  ${RED}❌ $label — فشل التشغيل! راجع $log_file${NC}"
    fi
}

stop_bot() {
    local name=$1
    local label="${BOT_NAMES[$name]}"
    local pid_file="$PIDS/${name}.pid"

    if ! is_running "$name"; then
        echo -e "  ${YELLOW}⏹  $label — لا يعمل${NC}"
        return
    fi

    local pid=$(cat "$pid_file")
    kill "$pid" 2>/dev/null
    sleep 1

    if ! is_running "$name"; then
        rm -f "$pid_file"
        echo -e "  ${RED}⏹  $label — أُوقف${NC}"
    else
        kill -9 "$pid" 2>/dev/null
        rm -f "$pid_file"
        echo -e "  ${RED}🔴 $label — أُجبر على الإيقاف${NC}"
    fi
}

status_bot() {
    local name=$1
    local label="${BOT_NAMES[$name]}"
    local pid_file="$PIDS/${name}.pid"

    if is_running "$name"; then
        local pid=$(cat "$pid_file")
        local uptime=$(ps -p $pid -o etime= 2>/dev/null | xargs)
        echo -e "  ${GREEN}🟢 $label — يعمل (PID: $pid | مشغّل منذ: $uptime)${NC}"
    else
        echo -e "  ${RED}🔴 $label — متوقف${NC}"
    fi
}

# ══════════════════════════════════════════════════════════════════
# COMMANDS
# ══════════════════════════════════════════════════════════════════

cmd_start() {
    banner
    check_env
    echo -e "${BOLD}▶ تشغيل جميع البوتات...${NC}\n"
    for name in customer admin recommendation supplier webhook; do
        start_bot "$name"
    done
    echo -e "\n${GREEN}${BOLD}✅ اكتمل التشغيل!${NC}"
    echo -e "${CYAN}📋 عرض السجلات: ${NC}bash run_all.sh logs"
    echo -e "${CYAN}📊 الحالة:       ${NC}bash run_all.sh status"
}

cmd_stop() {
    banner
    echo -e "${BOLD}⏹ إيقاف جميع البوتات...${NC}\n"
    for name in customer admin recommendation supplier webhook; do
        stop_bot "$name"
    done
    echo -e "\n${YELLOW}${BOLD}⏹ تم إيقاف الكل.${NC}"
}

cmd_restart() {
    banner
    check_env
    echo -e "${BOLD}🔄 إعادة تشغيل جميع البوتات...${NC}\n"
    for name in customer admin recommendation supplier webhook; do
        stop_bot "$name"
    done
    echo ""
    sleep 2
    for name in customer admin recommendation supplier webhook; do
        start_bot "$name"
    done
    echo -e "\n${GREEN}${BOLD}✅ إعادة التشغيل اكتملت!${NC}"
}

cmd_status() {
    banner
    echo -e "${BOLD}📊 حالة البوتات:${NC}\n"
    for name in customer admin recommendation supplier webhook; do
        status_bot "$name"
    done
    echo ""
    echo -e "${BOLD}💾 قاعدة البيانات:${NC}"
    for f in products orders leads analytics carts reviews newsletter; do
        FILE="$DIR/../${f}.json"
        if [ -f "$FILE" ]; then
            SIZE=$(du -h "$FILE" 2>/dev/null | cut -f1)
            echo -e "  ${GREEN}✅ ${f}.json${NC} (${SIZE})"
        else
            echo -e "  ${YELLOW}⚠️  ${f}.json — غير موجود${NC}"
        fi
    done
}

cmd_logs() {
    local target=${2:-all}
    if [ "$target" = "all" ]; then
        echo -e "${BOLD}📋 آخر سجلات جميع البوتات:${NC}\n"
        for name in customer admin recommendation supplier webhook; do
            local log_file="$LOGS/${name}.log"
            if [ -f "$log_file" ]; then
                echo -e "${CYAN}── ${BOT_NAMES[$name]} ──${NC}"
                tail -5 "$log_file"
                echo ""
            fi
        done
    else
        local log_file="$LOGS/${target}.log"
        if [ -f "$log_file" ]; then
            echo -e "${BOLD}📋 سجل ${BOT_NAMES[$target]}:${NC}"
            tail -f "$log_file"
        else
            echo -e "${RED}❌ لا يوجد سجل لـ $target${NC}"
        fi
    fi
}

cmd_init() {
    banner
    echo -e "${BOLD}🔧 تهيئة المشروع...${NC}\n"

    # Install requirements
    echo -e "${CYAN}📦 تثبيت المكتبات...${NC}"
    pip install -r "$DIR/requirements.txt" -q
    echo -e "${GREEN}✅ تم تثبيت المكتبات${NC}"

    # Initialize DB
    echo -e "${CYAN}🗄️  تهيئة قاعدة البيانات...${NC}"
    python3 -c "
import sys; sys.path.insert(0,'$DIR')
from shared_db import init_db
init_db()
print('✅ قاعدة البيانات جاهزة')
"

    # Create .env if not exists
    if [ ! -f "$DIR/.env" ]; then
        cp "$DIR/.env.example" "$DIR/.env"
        echo -e "${YELLOW}📝 تم إنشاء .env — عبّئ المتغيرات قبل التشغيل${NC}"
    fi

    echo -e "\n${GREEN}${BOLD}✅ التهيئة اكتملت!${NC}"
    echo -e "${YELLOW}⚡ الخطوة التالية: عبّئ .env ثم: ${NC}bash run_all.sh start"
}

# ══════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════

CMD=${1:-status}

case "$CMD" in
    start)   cmd_start ;;
    stop)    cmd_stop ;;
    restart) cmd_restart ;;
    status)  cmd_status ;;
    logs)    cmd_logs "$@" ;;
    init)    cmd_init ;;
    *)
        echo -e "${BOLD}الاستخدام:${NC} bash run_all.sh [أمر]"
        echo ""
        echo "  init     — تهيئة المشروع وتثبيت المكتبات"
        echo "  start    — تشغيل جميع البوتات"
        echo "  stop     — إيقاف جميع البوتات"
        echo "  restart  — إعادة تشغيل الكل"
        echo "  status   — عرض حالة كل بوت"
        echo "  logs     — عرض آخر السجلات"
        echo "  logs [bot_name] — سجل بوت محدد (مثال: logs customer)"
        ;;
esac
