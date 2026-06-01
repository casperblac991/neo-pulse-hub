/**
 * NEO PULSE HUB - نظام Countdown Timer للعروض
 * ============================================
 * يعرض وقت العد التنازلي للعروض المحدودة
 * لزيادة Urgency والتحويل
 */

const NPHCountdown = {
    // إعدادات افتراضية
    config: {
        endDate: null,
        autoRefresh: true,
        refreshInterval: 60000, // دقيقة واحدة
        theme: 'dark', // dark | light
        position: 'below-price', // below-price | inline | badge
        labels: {
            ar: { days: 'يوم', hours: 'ساعة', minutes: 'دقيقة', seconds: 'ثانية', ended: 'انتهى العرض!' },
            en: { days: 'd', hours: 'h', minutes: 'm', seconds: 's', ended: 'Offer ended!' }
        }
    },
    
    timers: [],
    
    /**
     * تهيئة Countdown لمنتج معين
     * @param {string} productId - معرف المنتج
     * @param {Date|string|number} endDate - تاريخ انتهاء العرض
     * @param {Object} options - إعدادات إضافية
     */
    init(productId, endDate, options = {}) {
        const config = { ...this.config, ...options };
        
        // تحويل التاريخ
        let end;
        if (typeof endDate === 'string') {
            end = new Date(endDate);
        } else if (typeof endDate === 'number') {
            end = new Date(Date.now() + endDate); // milliseconds from now
        } else {
            end = endDate;
        }
        
        // التحقق من صحة التاريخ
        if (isNaN(end.getTime())) {
            console.error('Invalid date for countdown:', endDate);
            return;
        }
        
        const timer = {
            id: productId,
            endDate: end,
            config,
            interval: null,
            element: null
        };
        
        this.timers.push(timer);
        return timer;
    },
    
    /**
     * إنشاء HTML للـ Countdown
     * @param {Object} timer - بيانات الـ Timer
     * @returns {string} - HTML
     */
    createCountdownHTML(timer) {
        const lang = document.documentElement.getAttribute('lang') || 'ar';
        const labels = timer.config.labels[lang] || timer.config.labels.ar;
        
        return `
            <div class="nph-countdown" id="countdown-${timer.id}" data-timer-id="${timer.id}">
                <div class="countdown-label">
                    ${lang === 'ar' ? '⏰ العرض ينتهي خلال:' : '⏰ Offer ends in:'}
                </div>
                <div class="countdown-timer">
                    <span class="countdown-unit" data-unit="days">
                        <span class="countdown-value" id="cd-days-${timer.id}">00</span>
                        <span class="countdown-unit-label">${labels.days}</span>
                    </span>
                    <span class="countdown-separator">:</span>
                    <span class="countdown-unit" data-unit="hours">
                        <span class="countdown-value" id="cd-hours-${timer.id}">00</span>
                        <span class="countdown-unit-label">${labels.hours}</span>
                    </span>
                    <span class="countdown-separator">:</span>
                    <span class="countdown-unit" data-unit="minutes">
                        <span class="countdown-value" id="cd-minutes-${timer.id}">00</span>
                        <span class="countdown-unit-label">${labels.minutes}</span>
                    </span>
                    <span class="countdown-separator">:</span>
                    <span class="countdown-unit" data-unit="seconds">
                        <span class="countdown-value" id="cd-seconds-${timer.id}">00</span>
                        <span class="countdown-unit-label">${labels.seconds}</span>
                    </span>
                </div>
                <div class="countdown-progress">
                    <div class="progress-bar" id="progress-${timer.id}"></div>
                </div>
            </div>
        `;
    },
    
    /**
     * تحديث الـ Countdown
     * @param {Object} timer - بيانات الـ Timer
     */
    updateCountdown(timer) {
        const now = new Date().getTime();
        const distance = timer.endDate.getTime() - now;
        
        if (distance < 0) {
            // انتهى العرض
            this.onTimerEnd(timer);
            return;
        }
        
        // حساب الوقت المتبقي
        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);
        
        // تحديث العنصر
        const el = document.getElementById(`countdown-${timer.id}`);
        if (el) {
            document.getElementById(`cd-days-${timer.id}`).textContent = String(days).padStart(2, '0');
            document.getElementById(`cd-hours-${timer.id}`).textContent = String(hours).padStart(2, '0');
            document.getElementById(`cd-minutes-${timer.id}`).textContent = String(minutes).padStart(2, '0');
            document.getElementById(`cd-seconds-${timer.id}`).textContent = String(seconds).padStart(2, '0');
            
            // تحديث شريط التقدم (افتراض 24 ساعة كحد أقصى)
            const progressBar = document.getElementById(`progress-${timer.id}`);
            if (progressBar) {
                const maxTime = 24 * 60 * 60 * 1000; // 24 hours
                const progress = Math.max(0, Math.min(100, (distance / maxTime) * 100));
                progressBar.style.width = `${progress}%`;
            }
        }
    },
    
    /**
     * عند انتهاء العرض
     * @param {Object} timer - بيانات الـ Timer
     */
    onTimerEnd(timer) {
        clearInterval(timer.interval);
        
        const el = document.getElementById(`countdown-${timer.id}`);
        if (el) {
            el.innerHTML = `
                <div class="countdown-ended">
                    <span class="ended-icon">🔔</span>
                    <span class="ended-text">انتهى العرض!</span>
                    <button class="notify-btn" onclick="NPHCountdown.notify('${timer.id}')">
                        🔔 أعلمني عند العرض القادم
                    </button>
                </div>
            `;
            el.classList.add('ended');
        }
    },
    
    /**
     * إضافة إشعار عند انتهاء العرض
     * @param {string} productId - معرف المنتج
     */
    notify(productId) {
        // حفظ في localStorage
        const notified = JSON.parse(localStorage.getItem('nph_notifications') || '[]');
        if (!notified.includes(productId)) {
            notified.push(productId);
            localStorage.setItem('nph_notifications', JSON.stringify(notified));
        }
        
        // إظهار رسالة
        const btn = event.target;
        btn.textContent = '✅ تم! سنخبرك';
        btn.disabled = true;
        btn.classList.add('success');
    },
    
    /**
     * بدء جميع الـ Timers
     */
    startAll() {
        this.timers.forEach(timer => {
            this.updateCountdown(timer);
            
            timer.interval = setInterval(() => {
                this.updateCountdown(timer);
            }, 1000);
        });
    },
    
    /**
     * إيقاف جميع الـ Timers
     */
    stopAll() {
        this.timers.forEach(timer => {
            if (timer.interval) {
                clearInterval(timer.interval);
            }
        });
        this.timers = [];
    }
};

// CSS Styles
const COUNTDOWN_CSS = `
.nph-countdown {
    font-family: 'Cairo', sans-serif;
    padding: 0.75rem;
    background: linear-gradient(135deg, rgba(239,68,68,0.1), rgba(139,92,246,0.1));
    border: 1px solid rgba(239,68,68,0.3);
    border-radius: 12px;
    margin: 0.5rem 0;
}

.nph-countdown.ended {
    background: rgba(239,68,68,0.05);
    border-color: rgba(239,68,68,0.2);
}

.countdown-label {
    font-size: 0.75rem;
    color: #ef4444;
    font-weight: 600;
    margin-bottom: 0.5rem;
    text-align: center;
}

.countdown-timer {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 0.25rem;
}

.countdown-unit {
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 40px;
}

.countdown-value {
    font-size: 1.25rem;
    font-weight: 700;
    color: #fff;
    background: rgba(239,68,68,0.2);
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
    font-family: 'Orbitron', monospace;
}

.countdown-unit-label {
    font-size: 0.6rem;
    color: rgba(255,255,255,0.6);
    margin-top: 2px;
}

.countdown-separator {
    font-size: 1.5rem;
    font-weight: 700;
    color: #ef4444;
    animation: blink 1s ease-in-out infinite;
}

@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

.countdown-progress {
    height: 4px;
    background: rgba(255,255,255,0.1);
    border-radius: 2px;
    margin-top: 0.5rem;
    overflow: hidden;
}

.progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #ef4444, #f59e0b);
    border-radius: 2px;
    transition: width 1s linear;
}

.countdown-ended {
    text-align: center;
    padding: 0.5rem;
}

.ended-icon {
    font-size: 1.5rem;
}

.ended-text {
    display: block;
    color: #ef4444;
    font-weight: 600;
    margin: 0.25rem 0;
}

.notify-btn {
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    color: #fff;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    font-size: 0.8rem;
    cursor: pointer;
    transition: all 0.3s ease;
}

.notify-btn:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(59,130,246,0.4);
}

.notify-btn.success {
    background: linear-gradient(135deg, #10b981, #059669);
}
`;

// Inject CSS
function injectCountdownCSS() {
    const style = document.createElement('style');
    style.textContent = COUNTDOWN_CSS;
    document.head.appendChild(style);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    injectCountdownCSS();
    NPHCountdown.startAll();
});

// Auto-start on load
window.addEventListener('load', () => {
    // إضافة Countdown افتراضي لمدة 24 ساعة لجميع المنتجات
    const products = window.PRODUCTS || [];
    products.forEach((product, index) => {
        if (product.discount && product.discount > 10) {
            // إضافة 24-48 ساعة متغيرة لكل منتج
            const hours = 24 + (index % 24);
            NPHCountdown.init(`product-${product.id}`, hours * 60 * 60 * 1000);
        }
    });
});

// Export
window.NPHCountdown = NPHCountdown;