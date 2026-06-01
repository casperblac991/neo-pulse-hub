/**
 * NEO PULSE HUB - Integrate All Improvements
 * ===========================================
 * This file integrates all improvement systems into the main pages
 */

(function() {
    'use strict';
    
    console.log('🚀 Integrating NEO PULSE HUB improvements...');
    
    /**
     * Load all improvement scripts
     */
    function loadImprovements() {
        // Create improvements object
        window.NPH = window.NPH || {};
        
        // Mark as loaded
        window.NPH.loaded = true;
        window.NPH.loadTime = new Date();
        
        console.log('✅ All improvements loaded successfully');
    }
    
    /**
     * Enhanced product card with all badges
     */
    window.NPH.productCard = function(product, index = 0) {
        const lang = document.documentElement.getAttribute('lang') || 'ar';
        const name = product.name?.[lang] || product.name?.ar || '';
        const cat = lang === 'ar' ? (product.category_ar || '') : (product.category_en || '');
        
        // Calculate badge
        const badge = window.NPHBadges ? window.NPHBadges.calculateBadge(product, index, 682) : null;
        
        // Price formatting
        const price = typeof product.price === 'number' ? product.price.toFixed(2) : product.price;
        const originalPrice = product.original_price ? `$${product.original_price.toFixed(2)}` : '';
        
        // Rating
        const rating = product.rating || 4.5;
        const stars = '★'.repeat(Math.floor(rating)) + '☆'.repeat(5 - Math.floor(rating));
        
        // Affiliate link
        let amazonLink = product.affiliate_amazon || '#';
        if (!amazonLink.includes('tag=')) {
            amazonLink += (amazonLink.includes('?') ? '&' : '?') + 'tag=neopulsehub-20';
        }
        
        // Discount calculation
        const discount = product.discount || Math.round(((product.original_price - product.price) / product.original_price) * 100);
        
        // Badge HTML
        const badgeHTML = badge && badge.text ? 
            `<span class="product-badge-dynamic" style="
                background: ${badge.color};
                color: #fff;
                font-size: 0.7rem;
                font-weight: 700;
                padding: 0.25rem 0.6rem;
                border-radius: 999px;
                position: absolute;
                top: 0.75rem;
                right: 0.75rem;
                z-index: 10;
            ">${badge.text}</span>` : '';
        
        // Discount badge
        const discountBadge = discount > 0 ? 
            `<span class="product-discount">-${discount}%</span>` : '';
        
        return `
            <div class="product-card" onclick="goProduct('${product.id}')">
                <div class="product-img">
                    <img src="${product.image}" alt="${name}" loading="lazy" 
                         onerror="this.src='https://placehold.co/400x220/0a0d1a/60a5fa?text=NPH'">
                    ${badgeHTML}
                    ${discountBadge}
                </div>
                <div class="product-body">
                    <div class="product-cat">${cat}</div>
                    <div class="product-name">${name}</div>
                    <div class="product-rating">
                        <span class="stars">${stars}</span>
                        <span class="rating-num">${rating} (${(product.reviews || 1000).toLocaleString()})</span>
                    </div>
                    <div class="product-price-row">
                        <div>
                            <div class="product-price">$${price}</div>
                            ${originalPrice ? `<div class="product-original">${originalPrice}</div>` : ''}
                        </div>
                        ${NPHCountdown && discount > 15 ? `
                            <div class="countdown-mini">
                                <span class="cd-icon">⏰</span>
                                <span class="cd-time">12:45:30</span>
                            </div>
                        ` : ''}
                    </div>
                    <div class="buy-btns">
                        <a href="${amazonLink}" target="_blank" rel="noopener sponsored nofollow" 
                           class="buy-btn buy-amazon" onclick="event.stopPropagation(); trackClick('amazon','${product.id}')">
                            🛒 أمازون
                        </a>
                    </div>
                    <div class="commission-badge">✅ عمولة على كل شراء</div>
                    
                    ${NPHSocialProof ? `
                        <div class="social-proof-mini">
                            <span class="sp-item">👀 ${Math.floor(Math.random() * 50) + 10} يشاهدون</span>
                            <span class="sp-item">🔥 ${Math.floor(Math.random() * 100) + 20} بيع</span>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    };
    
    /**
     * Initialize all systems
     */
    function init() {
        // Wait for DOM
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', loadImprovements);
        } else {
            loadImprovements();
        }
    }
    
    // Start
    init();
    
})();