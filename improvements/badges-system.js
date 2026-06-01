/**
 * NEO PULSE HUB - نظام Badges الديناميكية
 * ============================================
 * يضيف Badges مختلفة حسب حالة المنتج:
 * - 🏆 أفضل اختيار (Best Pick)
 * - 🔥 الأكثر مبيعاً (Best Seller)
 * - ⚡ عرض محدود (Limited Offer)
 * - 💸 وفّر XX (Save Money)
 * - 🆕 جديد (New)
 * - ⭐ قيمة ممتازة (Best Value)
 */

const BADGE_TYPES = {
    BEST_PICK: '🏆 أفضل اختيار',
    BEST_SELLER: '🔥 الأكثر مبيعاً',
    LIMITED_OFFER: '⚡ عرض محدود',
    SAVE_MONEY: '💸 وفّر',
    NEW: '🆕 جديد',
    BEST_VALUE: '⭐ قيمة ممتازة',
    EDITORS_CHOICE: '✨ اختيار المحرر',
    DEAL_OF_DAY: '🚨 عرض اليوم',
    ALMOST_GONE: '🚨 آخر قطع!'
};

const BADGE_COLORS = {
    BEST_PICK: 'linear-gradient(135deg, #f59e0b, #d97706)',
    BEST_SELLER: 'linear-gradient(135deg, #ef4444, #dc2626)',
    LIMITED_OFFER: 'linear-gradient(135deg, #8b5cf6, #7c3aed)',
    SAVE_MONEY: 'linear-gradient(135deg, #10b981, #059669)',
    NEW: 'linear-gradient(135deg, #3b82f6, #2563eb)',
    BEST_VALUE: 'linear-gradient(135deg, #06b6d4, #0891b2)',
    EDITORS_CHOICE: 'linear-gradient(135deg, #fbbf24, #f59e0b)',
    DEAL_OF_DAY: 'linear-gradient(135deg, #ec4899, #db2777)',
    ALMOST_GONE: 'linear-gradient(135deg, #ef4444, #b91c1c)'
};

/**
 * حساب الـ Badge المناسب للمنتج
 * @param {Object} product - بيانات المنتج
 * @param {number} index - ترتيب المنتج في القائمة
 * @param {number} total - إجمالي المنتجات
 * @returns {Object} - {text, color, position}
 */
function calculateBadge(product, index, total) {
    const price = product.price || 0;
    const originalPrice = product.original_price || price * 1.2;
    const discount = Math.round(((originalPrice - price) / originalPrice) * 100);
    const reviews = product.reviews || 0;
    
    // ترتيب المنتج حسب الفئة (الأول = أفضل اختيار)
    const position = index + 1;
    
    // منطق تحديد الـ Badge
    let badge = { text: '', color: '', position: 'top-right' };
    
    // 1. أفضل اختيار - أول منتج في كل فئة
    if (position === 1) {
        badge.text = BADGE_TYPES.BEST_PICK;
        badge.color = BADGE_COLORS.BEST_PICK;
    }
    // 2. الأكثر مبيعاً - منتجات بأكثر من 20000 مراجعة
    else if (reviews > 20000 && !badge.text) {
        badge.text = BADGE_TYPES.BEST_SELLER;
        badge.color = BADGE_COLORS.BEST_SELLER;
    }
    // 3. عرض محدود - خصم أكثر من 20%
    else if (discount > 20 && !badge.text) {
        badge.text = `${BADGE_TYPES.LIMITED_OFFER} -${discount}%`;
        badge.color = BADGE_COLORS.LIMITED_OFFER;
    }
    // 4. وفّر المال - خصم بين 10-20%
    else if (discount >= 10 && discount <= 20 && !badge.text) {
        const savedAmount = Math.round(originalPrice - price);
        badge.text = `${BADGE_TYPES.SAVE_MONEY} $${savedAmount}`;
        badge.color = BADGE_COLORS.SAVE_MONEY;
    }
    // 5. قيمة ممتازة - منتجات أقل من $100 مع خصم
    else if (price < 100 && discount > 15 && !badge.text) {
        badge.text = BADGE_TYPES.BEST_VALUE;
        badge.color = BADGE_COLORS.BEST_VALUE;
    }
    // 6. اختيار المحرر - تقييم 4.9+
    else if (product.rating >= 4.9 && !badge.text) {
        badge.text = BADGE_TYPES.EDITORS_CHOICE;
        badge.color = BADGE_COLORS.EDITORS_CHOICE;
    }
    // 7. جديد - المنتجات الأحدث (الفئة تحتوي أقل من 5 منتجات)
    else if (product.featured && !badge.text) {
        badge.text = BADGE_TYPES.NEW;
        badge.color = BADGE_COLORS.NEW;
    }
    // 8. عرض اليوم - خصم أكثر من 25%
    else if (discount > 25 && !badge.text) {
        badge.text = BADGE_TYPES.DEAL_OF_DAY;
        badge.color = BADGE_COLORS.DEAL_OF_DAY;
    }
    // 9. آخر قطع - منتجات بسعر منخفض جداً
    else if (price < 50 && discount > 30 && !badge.text) {
        badge.text = BADGE_TYPES.ALMOST_GONE;
        badge.color = BADGE_COLORS.ALMOST_GONE;
    }
    
    return badge;
}

/**
 * إنشاء عنصر Badge للعرض
 * @param {Object} badge - بيانات الـ Badge
 * @returns {string} - HTML للـ Badge
 */
function createBadgeHTML(badge) {
    if (!badge.text) return '';
    
    return `<span class="product-badge-dynamic" style="
        background: ${badge.color};
        color: #fff;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        position: absolute;
        ${badge.position === 'top-right' ? 'top: 0.75rem; right: 0.75rem;' : 'top: 0.75rem; left: 0.75rem;'}
        z-index: 10;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        animation: badgePulse 2s ease-in-out infinite;
    ">${badge.text}</span>`;
}

// Animation CSS
const BADGE_CSS = `
@keyframes badgePulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}

.product-badge-dynamic {
    transition: all 0.3s ease;
}

.product-badge-dynamic:hover {
    transform: scale(1.1);
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
`;

// Inject CSS
function injectBadgeCSS() {
    const style = document.createElement('style');
    style.textContent = BADGE_CSS;
    document.head.appendChild(style);
}

// Initialize
document.addEventListener('DOMContentLoaded', injectBadgeCSS);

// Export for use
window.NPHBadges = {
    calculateBadge,
    createBadgeHTML,
    BADGE_TYPES,
    BADGE_COLORS
};