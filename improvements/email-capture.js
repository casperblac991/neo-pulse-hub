/**
 * NEO PULSE HUB - نظام جمع الإيميلات
 * ===================================
 * نظام شامل لجمع الإيميلات من الزوار:
 * - Popup للاشتراك
 * - Lead magnets
 * - Welcome series
 * - Exit intent
 */

const NPHEmailCapture = {
    // إعدادات
    config: {
        popupDelay: 5000, // 5 ثواني
        exitIntentEnabled: true,
        scrollDepth: 70, // % من الصفحة
        cookieExpiry: 7, // أيام
        modalTitle: '🔥 لا تفوت أفضل العروض!',
        modalText: 'اشترك الآن واحصل على خصم 15% + دليل الساعات الذكية المجاني',
        buttonText: 'اشترك الآن',
        successMessage: '✅ تم! تحقق من بريدك الإلكتروني',
        leadMagnetTitle: '📖 دليل شراء الساعة الذكية 2026',
        leadMagnetDesc: 'دليل شامل + قائمة أفضل 20 ساعة ذكية + مقارنة الأسعار'
    },
    
    /**
     * إنشاء نافذة منبثقة للاشتراك
     * @returns {string} - HTML
     */
    createPopup() {
        return `
            <div class="email-popup-overlay" id="emailPopupOverlay">
                <div class="email-popup">
                    <button class="close-popup" onclick="NPHEmailCapture.closePopup()">✕</button>
                    
                    <div class="popup-header">
                        <span class="popup-icon">🎁</span>
                        <h2>${this.config.modalTitle}</h2>
                    </div>
                    
                    <p class="popup-text">${this.config.modalText}</p>
                    
                    <form class="email-form" onsubmit="NPHEmailCapture.submit(event)">
                        <input type="email" 
                               class="email-input" 
                               placeholder="أدخل بريدك الإلكتروني" 
                               required
                               id="emailInput">
                        
                        <button type="submit" class="submit-btn">
                            ${this.config.buttonText}
                            <span class="btn-arrow">←</span>
                        </button>
                    </form>
                    
                    <p class="popup-note">
                        🔒 لن نرسل لك spam. يمكنك إلغاء الاشتراك في أي وقت.
                    </p>
                    
                    <div class="lead-magnet-preview">
                        <span class="lm-icon">📖</span>
                        <div class="lm-info">
                            <strong>هدية مجانية:</strong>
                            <span>${this.config.leadMagnetTitle}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },
    
    /**
     * إنشاء Exit Intent Popup
     * @returns {string} - HTML
     */
    createExitIntent() {
        return `
            <div class="exit-intent-overlay" id="exitIntentOverlay">
                <div class="exit-intent-modal">
                    <button class="close-btn" onclick="NPHEmailCapture.closeExitIntent()">✕</button>
                    
                    <div class="exit-header">
                        <span class="wait-icon">⏳</span>
                        <h2>لحظة! قبل أن تذهب...</h2>
                    </div>
                    
                    <p class="exit-text">
                        احصل على <strong>خصم 20%</strong> على طلبك الأول + شحن مجاني!
                    </p>
                    
                    <form onsubmit="NPHEmailCapture.submitExit(event)">
                        <input type="email" 
                               placeholder="بريدك الإلكتروني" 
                               required
                               class="exit-input">
                        
                        <button type="submit" class="exit-btn">
                            🚀 احصل على الخصم الآن
                        </button>
                    </form>
                    
                    <p class="exit-note">
                        عرض محدود - ينتهي قريباً!
                    </p>
                </div>
            </div>
        `;
    },
    
    /**
     * إنشاء Floating Button للإشتراك
     * @returns {string} - HTML
     */
    createFloatingButton() {
        return `
            <div class="email-float-btn" id="emailFloatBtn" onclick="NPHEmailCapture.showPopup()">
                <span class="float-icon">✉️</span>
                <span class="float-text">اشترك</span>
                <span class="float-badge">-15%</span>
            </div>
        `;
    },
    
    /**
     * إنشاء Inline Signup Section
     * @param {string} position - where to place it
     * @returns {string} - HTML
     */
    createInlineSignup(position = 'below-hero') {
        const positions = {
            'below-hero': 'حصل على أفضل العروض مباشرة في بريدك',
            'mid-content': 'لا تريد أن تفوتك أفضل العروض؟',
            'footer': 'انضم لـ 5,000+ شخص يوصلون أفضل العروض'
        };
        
        return `
            <div class="inline-signup" data-position="${position}">
                <div class="is-content">
                    <span class="is-icon">📧</span>
                    <div class="is-text">
                        <h3>${positions[position] || positions['below-hero']}</h3>
                    </div>
                </div>
                
                <form class="is-form" onsubmit="NPHEmailCapture.submitInline(event)">
                    <input type="email" placeholder="بريدك الإلكتروني" required>
                    <button type="submit">اشترك</button>
                </form>
            </div>
        `;
    },
    
    /**
     * إضافة الـ CSS
     */
    injectStyles() {
        const css = `
            /* Popup Styles */
            .email-popup-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0,0,0,0.8);
                display: none;
                justify-content: center;
                align-items: center;
                z-index: 9999;
                animation: fadeIn 0.3s ease;
            }
            
            .email-popup-overlay.show {
                display: flex;
            }
            
            .email-popup {
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                border-radius: 20px;
                padding: 2.5rem;
                max-width: 450px;
                width: 90%;
                text-align: center;
                position: relative;
                border: 2px solid rgba(59,130,246,0.3);
                animation: slideUp 0.5s ease;
            }
            
            .close-popup {
                position: absolute;
                top: 1rem;
                left: 1rem;
                background: rgba(255,255,255,0.1);
                border: none;
                color: #fff;
                width: 30px;
                height: 30px;
                border-radius: 50%;
                cursor: pointer;
                font-size: 1rem;
            }
            
            .popup-header {
                margin-bottom: 1rem;
            }
            
            .popup-icon {
                font-size: 3rem;
                display: block;
                margin-bottom: 0.5rem;
            }
            
            .popup-header h2 {
                font-size: 1.5rem;
                color: #fff;
                margin: 0;
            }
            
            .popup-text {
                color: rgba(255,255,255,0.7);
                margin-bottom: 1.5rem;
                line-height: 1.6;
            }
            
            .email-form {
                display: flex;
                flex-direction: column;
                gap: 1rem;
            }
            
            .email-input {
                padding: 1rem;
                border-radius: 12px;
                border: 2px solid rgba(59,130,246,0.3);
                background: rgba(59,130,246,0.1);
                color: #fff;
                font-size: 1rem;
                text-align: center;
            }
            
            .email-input:focus {
                outline: none;
                border-color: #3b82f6;
            }
            
            .submit-btn {
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                color: #fff;
                padding: 1rem;
                border: none;
                border-radius: 12px;
                font-size: 1rem;
                font-weight: 700;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
                transition: all 0.3s ease;
            }
            
            .submit-btn:hover {
                transform: scale(1.02);
                box-shadow: 0 8px 25px rgba(59,130,246,0.4);
            }
            
            .btn-arrow {
                font-size: 1.2rem;
            }
            
            .popup-note {
                font-size: 0.75rem;
                color: rgba(255,255,255,0.4);
                margin-top: 1rem;
            }
            
            .lead-magnet-preview {
                background: rgba(245,158,11,0.1);
                border: 1px solid rgba(245,158,11,0.3);
                border-radius: 12px;
                padding: 1rem;
                margin-top: 1.5rem;
                display: flex;
                align-items: center;
                gap: 1rem;
                text-align: right;
            }
            
            .lm-icon {
                font-size: 2rem;
            }
            
            .lm-info strong {
                display: block;
                color: #f59e0b;
                font-size: 0.85rem;
            }
            
            .lm-info span {
                color: rgba(255,255,255,0.7);
                font-size: 0.9rem;
            }
            
            /* Exit Intent */
            .exit-intent-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0,0,0,0.85);
                display: none;
                justify-content: center;
                align-items: center;
                z-index: 10000;
            }
            
            .exit-intent-overlay.show {
                display: flex;
            }
            
            .exit-intent-modal {
                background: linear-gradient(135deg, #1f2937, #111827);
                border-radius: 20px;
                padding: 2.5rem;
                max-width: 500px;
                text-align: center;
                border: 3px solid #ef4444;
                position: relative;
            }
            
            .exit-header {
                margin-bottom: 1rem;
            }
            
            .wait-icon {
                font-size: 3rem;
                display: block;
            }
            
            .exit-header h2 {
                color: #ef4444;
                font-size: 1.75rem;
                margin: 0.5rem 0;
            }
            
            .exit-text {
                color: #fff;
                font-size: 1.1rem;
                margin-bottom: 1.5rem;
            }
            
            .exit-input {
                width: 100%;
                padding: 1rem;
                border-radius: 12px;
                border: 2px solid #ef4444;
                background: rgba(239,68,68,0.1);
                color: #fff;
                font-size: 1rem;
                text-align: center;
                margin-bottom: 1rem;
            }
            
            .exit-btn {
                width: 100%;
                background: linear-gradient(135deg, #ef4444, #dc2626);
                color: #fff;
                padding: 1rem;
                border: none;
                border-radius: 12px;
                font-size: 1rem;
                font-weight: 700;
                cursor: pointer;
            }
            
            .exit-note {
                color: rgba(255,255,255,0.5);
                font-size: 0.8rem;
                margin-top: 1rem;
            }
            
            /* Floating Button */
            .email-float-btn {
                position: fixed;
                bottom: 30px;
                left: 30px;
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                padding: 0.75rem 1.25rem;
                border-radius: 999px;
                color: #fff;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                cursor: pointer;
                box-shadow: 0 4px 20px rgba(59,130,246,0.4);
                z-index: 999;
                transition: all 0.3s ease;
            }
            
            .email-float-btn:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 30px rgba(59,130,246,0.6);
            }
            
            .float-icon {
                font-size: 1.25rem;
            }
            
            .float-text {
                font-weight: 600;
            }
            
            .float-badge {
                background: #ef4444;
                padding: 0.2rem 0.5rem;
                border-radius: 999px;
                font-size: 0.75rem;
                font-weight: 700;
            }
            
            /* Inline Signup */
            .inline-signup {
                background: linear-gradient(135deg, rgba(59,130,246,0.1), rgba(139,92,246,0.1));
                border: 2px solid rgba(59,130,246,0.2);
                border-radius: 16px;
                padding: 2rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 2rem;
                margin: 2rem 0;
                flex-wrap: wrap;
            }
            
            .is-content {
                display: flex;
                align-items: center;
                gap: 1rem;
            }
            
            .is-icon {
                font-size: 2rem;
            }
            
            .is-text h3 {
                color: #fff;
                margin: 0;
                font-size: 1.1rem;
            }
            
            .is-form {
                display: flex;
                gap: 0.5rem;
                flex: 1;
                min-width: 280px;
            }
            
            .is-form input {
                flex: 1;
                padding: 0.75rem 1rem;
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.2);
                background: rgba(0,0,0,0.3);
                color: #fff;
            }
            
            .is-form button {
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                color: #fff;
                border: none;
                padding: 0.75rem 1.5rem;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
            }
            
            /* Animations */
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            @keyframes slideUp {
                from { opacity: 0; transform: translateY(50px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            /* Success State */
            .email-popup.success .email-form,
            .email-popup.success .popup-note {
                display: none;
            }
            
            .success-message {
                display: none;
                padding: 2rem;
                text-align: center;
            }
            
            .email-popup.success .success-message {
                display: block;
            }
            
            .success-icon {
                font-size: 4rem;
                margin-bottom: 1rem;
            }
            
            .success-text {
                color: #10b981;
                font-size: 1.25rem;
                font-weight: 600;
            }
            
            @media (max-width: 768px) {
                .email-popup {
                    padding: 1.5rem;
                }
                
                .exit-intent-modal {
                    padding: 1.5rem;
                    margin: 1rem;
                }
                
                .inline-signup {
                    flex-direction: column;
                    text-align: center;
                }
            }
        `;
        
        const style = document.createElement('style');
        style.textContent = css;
        document.head.appendChild(style);
    },
    
    // Methods
    showPopup() {
        const overlay = document.getElementById('emailPopupOverlay');
        if (overlay) {
            overlay.classList.add('show');
            document.body.style.overflow = 'hidden';
        }
    },
    
    closePopup() {
        const overlay = document.getElementById('emailPopupOverlay');
        if (overlay) {
            overlay.classList.remove('show');
            document.body.style.overflow = '';
            // Set cookie
            this.setCookie('nph_popup_shown', '1', this.config.cookieExpiry);
        }
    },
    
    showExitIntent() {
        if (this.getCookie('nph_popup_shown')) return;
        if (this.getCookie('nph_exit_shown')) return;
        
        const overlay = document.getElementById('exitIntentOverlay');
        if (overlay) {
            overlay.classList.add('show');
            this.setCookie('nph_exit_shown', '1', 1); // Show once per day
        }
    },
    
    closeExitIntent() {
        const overlay = document.getElementById('exitIntentOverlay');
        if (overlay) {
            overlay.classList.remove('show');
        }
    },
    
    submit(event) {
        event.preventDefault();
        const email = document.getElementById('emailInput').value;
        this.saveEmail(email, 'popup');
        this.showSuccess();
    },
    
    submitExit(event) {
        event.preventDefault();
        const email = event.target.querySelector('input').value;
        this.saveEmail(email, 'exit-intent');
        this.closeExitIntent();
        alert('✅ تم! ستصلك رسالة على بريدك الإلكتروني');
    },
    
    submitInline(event) {
        event.preventDefault();
        const email = event.target.querySelector('input').value;
        this.saveEmail(email, 'inline');
        event.target.reset();
        alert('✅ شكراً! ستصلك أفضل العروض قريباً');
    },
    
    showSuccess() {
        const popup = document.querySelector('.email-popup');
        if (popup) {
            popup.classList.add('success');
            setTimeout(() => this.closePopup(), 3000);
        }
    },
    
    saveEmail(email, source) {
        // Save to localStorage (in real app, send to backend)
        const subscribers = JSON.parse(localStorage.getItem('nph_subscribers') || '[]');
        
        // Check if already subscribed
        const exists = subscribers.find(s => s.email === email);
        if (exists) return;
        
        subscribers.push({
            email,
            source,
            date: new Date().toISOString(),
            status: 'active'
        });
        
        localStorage.setItem('nph_subscribers', JSON.stringify(subscribers));
        console.log(`📧 New subscriber: ${email} from ${source}`);
    },
    
    // Cookie helpers
    setCookie(name, value, days) {
        const d = new Date();
        d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000));
        document.cookie = `${name}=${value};expires=${d.toUTCString()};path=/`;
    },
    
    getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    },
    
    // Initialize
    init() {
        // Check if popup should be shown
        if (this.getCookie('nph_popup_shown')) return;
        
        // Inject styles
        this.injectStyles();
        
        // Add popup to DOM
        document.body.insertAdjacentHTML('beforeend', this.createPopup());
        document.body.insertAdjacentHTML('beforeend', this.createExitIntent());
        document.body.insertAdjacentHTML('beforeend', this.createFloatingButton());
        
        // Show popup after delay
        setTimeout(() => {
            this.showPopup();
        }, this.config.popupDelay);
        
        // Exit intent detection
        if (this.config.exitIntentEnabled) {
            document.addEventListener('mouseout', (e) => {
                if (e.clientY < 10) {
                    this.showExitIntent();
                }
            });
        }
        
        // Scroll depth
        let scrolled = false;
        window.addEventListener('scroll', () => {
            if (scrolled) return;
            
            const scrollPercent = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
            if (scrollPercent > this.config.scrollDepth) {
                scrolled = true;
                // Show inline signup or mini popup
            }
        });
    }
};

// Auto-init
document.addEventListener('DOMContentLoaded', () => {
    NPHEmailCapture.init();
});

// Export
window.NPHEmailCapture = NPHEmailCapture;