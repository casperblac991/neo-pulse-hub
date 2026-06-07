#!/usr/bin/env python3
"""
تحديث page.html و index.html لتحميل المنتجات من products.json
بدلاً من hardcoded inline products
"""

import json

def create_product_loader_js():
    """إنشاء JavaScript يحمّل المنتجات من JSON"""
    
    js_code = '''
// ============================================
// تحميل المنتجات من ملف JSON خارجي
// ============================================
let allProducts = [];
let filteredProducts = [];
let activeCategory = 'all';
let maxPrice = 700;
let sortBy = 'featured';
let cart = JSON.parse(localStorage.getItem('nph_cart') || '[]');

// تحميل المنتجات
async function loadProducts() {
    try {
        // محاولة تحميل من ملف JSON خارجي
        const response = await fetch('products.json?' + Date.now());
        if (response.ok) {
            const data = await response.json();
            allProducts = data.map(p => ({
                id: p.id,
                name_ar: p.name?.ar || p.name_ar || '',
                name_en: p.name?.en || p.name_en || '',
                category: p.category,
                category_ar: p.category_ar || getCategoryNameAr(p.category),
                category_en: p.category_en || getCategoryNameEn(p.category),
                price: typeof p.price === 'string' ? parseFloat(p.price.replace('$','')) : p.price,
                original_price: p.original_price || 0,
                discount: p.discount || 0,
                rating: p.rating || 4.5,
                reviews: p.reviews || 1000,
                image: p.image || 'https://placehold.co/400x400/1e3a5f/ffffff?text=Product',
                badge_ar: p.badge?.ar || p.badge_ar || '',
                badge_en: p.badge?.en || p.badge_en || '',
                in_stock: p.in_stock !== false,
                featured: p.featured || false
            }));
            console.log('✅ تم تحميل', allProducts.length, 'منتج من products.json');
            updateCategoryCounts();
            renderProducts();
        } else {
            throw new Error('Failed to fetch');
        }
    } catch (error) {
        console.log('⚠️ فشل تحميل products.json، استخدام البيانات المدمجة');
        loadInlineProducts();
    }
}

function getCategoryNameAr(cat) {
    const names = {
        'smartwatch': 'ساعات ذكية',
        'earbuds': 'سماعات لاسلكية',
        'headphones': 'سماعات رأس',
        'smart-home': 'المنزل الذكي',
        'health': 'الصحة الذكية',
        'productivity': 'الإنتاجية',
        'gaming': 'ألعاب وترفيه',
        'cameras': 'كاميرات',
        'smart-glasses': 'نظارات ذكية',
        'accessories': 'إكسسوارات',
        'kitchen': 'مطبخ ذكي',
        'sports': 'رياضة',
        'car': 'إلكترونيات سيارات',
        'kids': 'تقنية أطفال',
        'office': 'أدوات مكتبية'
    };
    return names[cat] || cat;
}

function getCategoryNameEn(cat) {
    const names = {
        'smartwatch': 'Smart Watch',
        'earbuds': 'Wireless Earbuds',
        'headphones': 'Headphones',
        'smart-home': 'Smart Home',
        'health': 'Smart Health',
        'productivity': 'Productivity',
        'gaming': 'Gaming',
        'cameras': 'Cameras',
        'smart-glasses': 'Smart Glasses',
        'accessories': 'Accessories',
        'kitchen': 'Smart Kitchen',
        'sports': 'Sports',
        'car': 'Car Electronics',
        'kids': 'Kids Tech',
        'office': 'Office'
    };
    return names[cat] || cat;
}

// تصفية المنتجات
function applyFilters() {
    const q = (document.getElementById('searchInput')?.value || '').trim().toLowerCase();
    
    filteredProducts = allProducts.filter(p => {
        const matchCat = activeCategory === 'all' || p.category === activeCategory;
        const matchPrice = p.price <= maxPrice;
        const name = (p.name_en || '').toLowerCase() + ' ' + (p.name_ar || '').toLowerCase();
        const matchQ = !q || name.includes(q);
        return matchCat && matchPrice && matchQ;
    });

    // ترتيب
    if (sortBy === 'price-asc') filteredProducts.sort((a,b) => a.price - b.price);
    if (sortBy === 'price-desc') filteredProducts.sort((a,b) => b.price - a.price);
    if (sortBy === 'rating') filteredProducts.sort((a,b) => b.rating - a.rating);
    if (sortBy === 'discount') filteredProducts.sort((a,b) => b.discount - a.discount);

    renderProducts();
    
    document.getElementById('resultsCount').textContent = filteredProducts.length + ' منتج';
}

// عرض المنتجات
function renderProducts() {
    const grid = document.getElementById('productsGrid');
    if (!grid) return;

    if (filteredProducts.length === 0) {
        grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:3rem"><h3>لا توجد منتجات</h3></div>';
        return;
    }

    const page = window._productsPage || 1;
    const perPage = 20;
    const visible = filteredProducts.slice(0, page * perPage);

    grid.innerHTML = visible.map((p, i) => {
        const name = (window.lang || 'ar') === 'en' ? p.name_en : p.name_ar;
        const badge = (window.lang || 'ar') === 'en' ? p.badge_en : p.badge_ar;
        const cat = (window.lang || 'ar') === 'en' ? p.category_en : p.category_ar;
        
        return `
        <div class="product-card" onclick="goProduct('${p.id}')">
            <div class="product-img">
                <img src="${p.image}" alt="${name}" loading="lazy">
                ${badge ? '<span class="badge">'+badge+'</span>' : ''}
                ${p.discount ? '<span class="discount-tag">-'+p.discount+'%</span>' : ''}
            </div>
            <div class="product-body">
                <div class="product-cat">${cat}</div>
                <div class="product-name">${name}</div>
                <div class="stars-row">
                    <span class="stars">${'★'.repeat(Math.floor(p.rating))}</span>
                    <span class="rev">${p.rating} (${p.reviews})</span>
                </div>
                <div class="price-row">
                    <div class="price">$${p.price}</div>
                    ${p.original_price ? '<div class="orig">$'+p.original_price+'</div>' : ''}
                </div>
            </div>
        </div>`;
    }).join('');

    // عرض المزيد
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    if (visible.length < filteredProducts.length) {
        loadMoreBtn.innerHTML = '<button onclick="loadMoreProducts()">عرض المزيد ('+ (filteredProducts.length - visible.length) +')</button>';
        loadMoreBtn.style.display = 'block';
    } else {
        loadMoreBtn.style.display = 'none';
    }
}

function loadMoreProducts() {
    window._productsPage = (window._productsPage || 1) + 1;
    renderProducts();
}

function updateCategoryCounts() {
    document.getElementById('count-all').textContent = allProducts.length;
    document.getElementById('count-smartwatch').textContent = allProducts.filter(p => p.category === 'smartwatch').length;
    document.getElementById('count-smart-glasses').textContent = allProducts.filter(p => p.category === 'smart-glasses').length;
    document.getElementById('count-health').textContent = allProducts.filter(p => p.category === 'health').length;
    document.getElementById('count-smart-home').textContent = allProducts.filter(p => p.category === 'smart-home').length;
    document.getElementById('count-earbuds').textContent = allProducts.filter(p => p.category === 'earbuds').length;
    document.getElementById('count-productivity').textContent = allProducts.filter(p => p.category === 'productivity').length;
}

function goProduct(id) {
    window.location.href = 'product-detail.html?id=' + id;
}

// بدء التحميل عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', loadProducts);
'''
    
    with open('product_loader.js', 'w', encoding='utf-8') as f:
        f.write(js_code)
    
    print("✅ تم إنشاء product_loader.js")
    return len(js_code)

if __name__ == "__main__":
    create_product_loader_js()
    print("\n🎯 يمكنك إضافة هذا الملف في products.html")
    print("أو استخدام التحديث المبني في الأسفل")