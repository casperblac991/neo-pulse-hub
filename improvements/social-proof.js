/**
 * NEO PULSE HUB - نظام Social Proof
 * ===================================
 * يعرض مؤشرات اجتماعية لزيادة الثقة والتحويل:
 * - عدد المشاهدات الحالية
 * - عدد المبيعات
 * - تقييمات العملاء
 * - إحصائيات الموقع
 */

const NPHSocialProof = {
    // إعدادات
    config: {
        showViews: true,
        showSales: true,
        showRatings: true,
        showSiteStats: true,
        updateInterval: 30000, // 30 ثانية
        animationEnabled: true
    },
    
    // بيانات مزيفة للعرض (يمكن تحديثها من API حقيقي)
    fakeData: {
        siteStats: {
            visitors: 12543,
            sales: 3421,
            rating: 4.8
        }
    },
    
    /**
     * إنشاء badge Social Proof للمنتج
     * @param {Object} product - بيانات المنتج
     * @returns {string} - HTML
     */
    createProductBadge(product) {
        const views = this.getRandomViews(product.id);
        const sales = this.getRandomSales(product.id);
        
        let html = '<div class="social-proof-badges">';
        
        // عدد المشاهدين الحاليين
        if (this.config.showViews && views > 0) {
            html += `
                <div class="sp-badge sp-views">
                    <span class="sp-icon">👀</span>
                    <span class="sp-value">${views} يشاهدون الآن</span>
                </div>
            `;
        }
        
        // عدد المبيعات
        if (this.config.showSales && sales > 0) {
            html += `
                <div class="sp-badge sp-sales">
                    <span class="sp-icon">🔥</span>
                    <span class="sp-value">${sales} بيع هذا الأسبوع</span>
                </div>
            `;
        }
        
        html += '</div>';
        return html;
    },
    
    /**
     * إنشاء شريط Social Proof العلوي
     * @returns {string} - HTML
     */
    createTopBar() {
        const stats = this.fakeData.siteStats;
        
        return `
            <div class="social-proof-topbar">
                <div class="sp-container">
                    <div class="sp-item">
                        <span class="sp-icon">👥</span>
                        <span class="sp-text">انضم <strong>${this.formatNumber(stats.visitors)}+</strong> زبون سعيد</span>
                    </div>
                    <div class="sp-divider">|</div>
                    <div class="sp-item">
                        <span class="sp-icon">⭐</span>
                        <span class="sp-text">تقييم <strong>${stats.rating}/5</strong> من ${this.formatNumber(stats.sales)}+ تقييم</span>
                    </div>
                    <div class="sp-divider">|</div>
                    <div class="sp-item sp-highlight">
                        <span class="sp-icon">🎉</span>
                        <span class="sp-text">خصم <strong>25%</strong> على جميع الساعات!</span>
                    </div>
                </div>
            </div>
        `;
    },
    
    /**
     * إنشاء نافذة "شخص يشاهد الآن"
     * @param {number} count - عدد المشاهدين
     * @returns {string} - HTML
     */
    createLiveViewers(count) {
        const names = ['أحمد', 'محمد', 'سارة', 'نورة', 'خالد', 'فاطمة', 'عمر', 'ليلى', 'يوسف', 'مريم'];
        const randomName = names[Math.floor(Math.random() * names.length)];
        
        return `
            <div class="live-viewer-popup" id="liveViewerPopup">
                <div class="lv-avatar">👤</div>
                <div class="lv-content">
                    <span class="lv-name">${randomName}</span>
                    <span class="lv-action">اشاهد الآن</span>
                </div>
                <div class="lv-dot"></div>
            </div>
        `;
    },
    
    /**
     * إنشاء badge "الأكثر مبيعاً"
     * @param {number} rank - الترتيب
     * @returns {string} - HTML
     */
    createBestSellerBadge(rank) {
        const badges = {
            1: { text: '🥇 الأكثر مبيعاً', color: '#fbbf24' },
            2: { text: '🥈 الثاني', color: '#9ca3af' },
            3: { text: '🥉 الثالث', color: '#cd7f32' }
        };
        
        const badge = badges[rank] || null;
        if (!badge) return '';
        
        return `
            <div class="best-seller-badge" style="background: ${badge.color}">
                ${badge.text}
            </div>
        `;
    },
    
    /**
     * إنشاء شريط "آخر من اشترى"
     * @param {Object} product - بيانات المنتج
     * @returns {string} - HTML
     */
    createRecentBuyer(product) {
        const countries = ['السعودية', 'الإمارات', 'الكويت', 'مصر', 'الأردن'];
        const country = countries[Math.floor(Math.random() * countries.length)];
        const time = this.getRandomTime();
        
        return `
            <div class="recent-buyer-bar" id="recentBuyer-${product.id}">
                <span class="rb-avatar">🛒</span>
                <span class="rb-text">
                    <strong>شخص من ${country}</strong> اشترى هذا المنتج ${time}
                </span>
            </div>
        `;
    },
    
    /**
     * إنشاء شريط الثقة (Trust Bar)
     * @returns {string} - HTML
     */
    createTrustBar() {
        return `
            <div class="trust-bar">
                <div class="trust-item">
                    <span class="trust-icon">🔒</span>
                    <span class="trust-text">دفع آمن 100%</span>
                </div>
                <div class="trust-item">
                    <span class="trust-icon">🚚</span>
                    <span class="trust-text">شحن مجاني + توصيل سريع</span>
                </div>
                <div class="trust-item">
                    <span class="trust-icon">↩️</span>
                    <span class="trust-text">إرجاع خلال 30 يوم</span>
                </div>
                <div class="trust-item">
                    <span class="trust-icon">💬</span>
                    <span class="trust-text">دعم 24/7</span>
                </div>
            </div>
        `;
    },
    
    /**
     * إنشاء إحصائيات الفوتر
     * @returns {string} - HTML
     */
    createFooterStats() {
        const stats = this.fakeData.siteStats;
        
        return `
            <div class="footer-stats">
                <div class="stat-item">
                    <span class="stat-number" data-countup="${stats.visitors}">0</span>
                    <span class="stat-label">زائر شهرياً</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number" data-countup="${stats.sales}">0</span>
                    <span class="stat-label">منتج مباع</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">${stats.rating}</span>
                    <span class="stat-label">تقييم moyenne</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">682</span>
                    <span class="stat-label">منتج متوفر</span>
                </div>
            </div>
        `;
    },
    
    // Helper functions
    getRandomViews(productId) {
        // تحويل الـ ID إلى رقم ثابت لتثبيت النتائج
        const hash = productId.split('').reduce((a, b) => a + b.charCodeAt(0), 0);
        return (hash % 50) + 5; // 5-55 مشاهد
    },
    
    getRandomSales(productId) {
        const hash = productId.split('').reduce((a, b) => a + b.charCodeAt(0), 0);
        return (hash % 100) + 10; // 10-110 مبيعات
    },
    
    getRandomTime() {
        const times = ['الآن', 'منذ 5 دقائق', 'منذ 10 دقائق', 'منذ ساعة'];
        return times[Math.floor(Math.random() * times.length)];
    },
    
    formatNumber(num) {
        if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    },
    
    /**
     * تفعيل تأثيرات الأنيميشن
     */
    enableAnimations() {
        // CountUp animation للأرقام
        const countupElements = document.querySelectorAll('[data-countup]');
        countupElements.forEach(el => {
            const target = parseInt(el.dataset.countup);
            let current = 0;
            const increment = target / 50;
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    el.textContent = this.formatNumber(target);
                    clearInterval(timer);
                } else {
                    el.textContent = this.formatNumber(Math.floor(current));
                }
            }, 30);
        });
        
        // Pulsing للـ live viewers
        if (this.config.animationEnabled) {
            setInterval(() => {
                const popup = document.getElementById('liveViewerPopup');
                if (popup) {
                    popup.classList.add('show');
                    setTimeout(() => popup.classList.remove('show'), 3000);
                }
            }, this.config.updateInterval);
        }
    }
};

// CSS Styles
const SOCIAL_PROOF_CSS = `
/* Social Proof Badges */
.social-proof-badges {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}

.sp-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.35rem 0.7rem;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 600;
    animation: spFadeIn 0.5s ease;
}

.sp-views {
    background: rgba(59, 130, 246, 0.15);
    color: #60a5fa;
    border: 1px solid rgba(59, 130, 246, 0.3);
}

.sp-sales {
    background: rgba(239, 68, 68, 0.15);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.3);
}

.sp-icon {
    font-size: 0.9rem;
}

/* Top Bar */
.social-proof-topbar {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    padding: 0.75rem;
    text-align: center;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}

.sp-container {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
}

.sp-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: rgba(255,255,255,0.8);
    font-size: 0.85rem;
}

.sp-item strong {
    color: #fff;
}

.sp-item.sp-highlight {
    background: linear-gradient(135deg, #ef4444, #dc2626);
    padding: 0.35rem 0.75rem;
    border-radius: 999px;
    color: #fff;
}

.sp-divider {
    color: rgba(255,255,255,0.3);
}

/* Live Viewer Popup */
.live-viewer-popup {
    position: fixed;
    bottom: 100px;
    left: 20px;
    background: linear-gradient(135deg, #1f2937, #374151);
    padding: 0.75rem 1rem;
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    opacity: 0;
    transform: translateY(20px);
    transition: all 0.3s ease;
    z-index: 1000;
}

.live-viewer-popup.show {
    opacity: 1;
    transform: translateY(0);
}

.lv-avatar {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
}

.lv-content {
    display: flex;
    flex-direction: column;
}

.lv-name {
    color: #fff;
    font-weight: 600;
    font-size: 0.85rem;
}

.lv-action {
    color: rgba(255,255,255,0.6);
    font-size: 0.75rem;
}

.lv-dot {
    width: 8px;
    height: 8px;
    background: #10b981;
    border-radius: 50%;
    animation: livePulse 1.5s infinite;
}

@keyframes livePulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.8); }
}

/* Best Seller Badge */
.best-seller-badge {
    position: absolute;
    top: -10px;
    left: 50%;
    transform: translateX(-50%);
    padding: 0.25rem 1rem;
    border-radius: 0 0 12px 12px;
    color: #000;
    font-weight: 700;
    font-size: 0.75rem;
    z-index: 5;
}

/* Trust Bar */
.trust-bar {
    display: flex;
    justify-content: center;
    gap: 2rem;
    padding: 1rem;
    background: rgba(16, 185, 129, 0.1);
    border-top: 1px solid rgba(16, 185, 129, 0.2);
}

.trust-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #10b981;
    font-size: 0.85rem;
    font-weight: 500;
}

.trust-icon {
    font-size: 1.25rem;
}

/* Footer Stats */
.footer-stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    padding: 2rem;
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.1));
    border-top: 1px solid rgba(255,255,255,0.1);
}

.stat-item {
    text-align: center;
}

.stat-number {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.75rem;
    font-weight: 700;
    color: #3b82f6;
}

.stat-label {
    display: block;
    font-size: 0.75rem;
    color: rgba(255,255,255,0.6);
    margin-top: 0.25rem;
}

/* Animations */
@keyframes spFadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
    .trust-bar {
        flex-wrap: wrap;
        gap: 1rem;
    }
    
    .footer-stats {
        grid-template-columns: repeat(2, 1fr);
    }
}
`;

// Inject CSS
function injectSocialProofCSS() {
    const style = document.createElement('style');
    style.textContent = SOCIAL_PROOF_CSS;
    document.head.appendChild(style);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    injectSocialProofCSS();
    NPHSocialProof.enableAnimations();
});

// Export
window.NPHSocialProof = NPHSocialProof;