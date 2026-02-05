import os
import json
import urllib.parse
import re
import zipfile
import xml.sax.saxutils as xml_escape

# ==========================================
# تعديل اسم المشروع ليطابق Cloudflare
# ==========================================
PROJECT_NAME = "sooq-alkuwait-pro"
CLOUDFLARE_URL = "https://sooq-alkuwait-pro.pages.dev"
INPUT_JSON = "products_data_cleaned.json"
OUTPUT_DIR = "dist_sooq"
GA_ID = "G-ENJFWMT5T0"
WHATSAPP_NUMBER = "201110760081"

# ==========================================
# 1. STYLES
# ==========================================
COMMON_HEAD = f"""
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="theme-color" content="#83b735">
    
    <!-- Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA_ID}');
    </script>

    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/alpinejs/3.12.0/cdn.min.js" defer></script>

    <style>
        :root {{
            --wood-primary: #83b735;
            --wood-dark: #2d2a2a;
            --wood-gray: #f9f9f9;
            --border-color: #e6e6e6;
            --kuwait-green: #007a3d;
        }}
        
        * {{ box-sizing: border-box; }}
        body {{ font-family: 'Cairo', sans-serif; background-color: white; color: #333; margin: 0; padding-bottom: 60px; }}
        a {{ text-decoration: none; color: inherit; transition: 0.3s; }}
        ul {{ list-style: none; padding: 0; margin: 0; }}
        
        .container {{ max-width: 1240px; margin: 0 auto; padding: 0 15px; }}
        
        .top-bar {{ background: #2d2a2a; color: rgba(255,255,255,0.8); font-size: 12px; padding: 8px 0; }}
        .header-main {{ padding: 25px 0; border-bottom: 1px solid var(--border-color); }}
        
        .logo {{ display: flex; align-items: center; gap: 12px; font-size: 24px; font-weight: 900; color: var(--wood-dark); }}
        .logo-icon {{ width: 45px; height: 45px; background: linear-gradient(135deg, var(--kuwait-green), var(--wood-primary)); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; font-size: 22px; box-shadow: 0 4px 12px rgba(0,122,61,0.2); position: relative; overflow: hidden; }}
        .logo-icon::before {{ content: ''; position: absolute; top: -50%; right: -50%; width: 200%; height: 200%; background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent); transform: rotate(45deg); }}
        .logo-text {{ display: flex; flex-direction: column; line-height: 1; }}
        .logo-text .main {{ font-size: 22px; font-weight: 900; color: var(--wood-dark); letter-spacing: -0.5px; }}
        .logo-text .sub {{ font-size: 11px; font-weight: 600; color: var(--kuwait-green); letter-spacing: 1px; margin-top: 2px; text-transform: uppercase; }}
        
        .wood-search {{ flex: 1; max-width: 600px; margin: 0 30px; position: relative; }}
        .wood-search input {{ width: 100%; border: 2px solid var(--border-color); padding: 12px 20px; border-radius: 30px; outline: none; font-family: 'Cairo'; transition: 0.3s; }}
        .wood-search input:focus {{ border-color: var(--wood-primary); }}
        .wood-search button {{ position: absolute; left: 5px; top: 5px; background: transparent; border: none; width: 40px; height: 40px; cursor: pointer; color: #999; }}
        
        .header-actions {{ display: flex; gap: 20px; align-items: center; }}
        .icon-link {{ display: flex; flex-direction: column; align-items: center; font-size: 12px; font-weight: 600; color: var(--wood-dark); cursor: pointer; position: relative; }}
        .icon-link i {{ font-size: 24px; margin-bottom: 3px; }}
        .cart-count {{ position: absolute; top: -5px; right: 0; background: var(--wood-primary); color: white; border-radius: 50%; width: 18px; height: 18px; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold; }}

        .products-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; padding: 40px 0; }}
        @media(min-width: 768px) {{ .products-grid {{ grid-template-columns: repeat(4, 1fr); gap: 25px; }} }}

        .product-card {{ position: relative; border: 1px solid #f0f0f0; padding: 15px; transition: 0.3s; background: white; border-radius: 10px; }}
        .product-card:hover {{ border-color: var(--wood-primary); box-shadow: 0 8px 25px rgba(0,0,0,0.08); transform: translateY(-3px); }}
        
        .prod-img-wrap {{ position: relative; overflow: hidden; margin-bottom: 15px; height: 250px; display: flex; align-items: center; justify-content: center; background: #fafafa; border-radius: 8px; }}
        .prod-img {{ max-width: 100%; max-height: 100%; transition: 0.3s; object-fit: contain; }}
        .product-card:hover .prod-img {{ transform: scale(1.05); }}
        
        .prod-title {{ font-size: 14px; font-weight: 700; color: #2d2a2a; margin-bottom: 8px; line-height: 1.4; height: 40px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }}
        .prod-price {{ font-size: 17px; font-weight: 900; color: var(--wood-primary); }}
        .old-price {{ font-size: 13px; color: #bbb; text-decoration: line-through; margin-left: 8px; }}
        
        .wood-btn {{ width: 100%; background: #f5f5f5; color: #333; border: none; padding: 11px; font-weight: 700; font-size: 13px; cursor: pointer; transition: 0.3s; border-radius: 8px; margin-top: 10px; font-family: 'Cairo'; }}
        .wood-btn:hover {{ background: var(--wood-primary); color: white; transform: translateY(-2px); }}
        .wood-btn-primary {{ background: var(--wood-primary); color: white; }}
        .wood-btn-primary:hover {{ background: #6da022; }}

        .product-gallery {{ display: grid; gap: 15px; }}
        .main-image {{ width: 100%; border: 1px solid #eee; border-radius: 12px; padding: 30px; background: #fafafa; }}
        .main-image img {{ width: 100%; height: auto; display: block; }}
        
        .thumbnails {{ display: flex; gap: 10px; overflow-x: auto; padding: 10px 0; }}
        .thumbnails::-webkit-scrollbar {{ height: 6px; }}
        .thumbnails::-webkit-scrollbar-thumb {{ background: #ddd; border-radius: 10px; }}
        .thumb {{ width: 80px; height: 80px; border: 2px solid #e0e0e0; border-radius: 8px; overflow: hidden; cursor: pointer; transition: 0.3s; flex-shrink: 0; background: #fafafa; }}
        .thumb:hover {{ border-color: var(--wood-primary); transform: scale(1.05); }}
        .thumb.active {{ border-color: var(--wood-primary); box-shadow: 0 0 0 2px rgba(131,183,53,0.2); }}
        .thumb img {{ width: 100%; height: 100%; object-fit: cover; }}
        
        .specs-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background: white; border-radius: 8px; overflow: hidden; }}
        .specs-table tr {{ border-bottom: 1px solid #f0f0f0; }}
        .specs-table tr:last-child {{ border-bottom: none; }}
        .specs-table td {{ padding: 14px 16px; font-size: 14px; }}
        .specs-table td:first-child {{ font-weight: 700; width: 40%; background: #f9f9f9; color: #555; }}
        
        .floating-buttons {{ position: fixed; bottom: 20px; right: 20px; z-index: 1000; display: flex; flex-direction: column; gap: 15px; }}
        .float-btn {{ width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 24px; box-shadow: 0 8px 20px rgba(0,0,0,0.2); cursor: pointer; transition: all 0.3s; position: relative; }}
        .float-btn:hover {{ transform: translateY(-5px); box-shadow: 0 12px 30px rgba(0,0,0,0.3); }}
        .float-btn:active {{ transform: translateY(-2px); }}
        .float-whatsapp {{ background: linear-gradient(135deg, #25D366, #128C7E); }}
        .float-cart {{ background: linear-gradient(135deg, var(--wood-primary), #6da022); }}
        .float-badge {{ position: absolute; top: -5px; right: -5px; background: #ff4444; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; border: 2px solid white; animation: pulse 2s infinite; }}
        
        @keyframes pulse {{ 0%, 100% {{ transform: scale(1); }} 50% {{ transform: scale(1.1); }} }}

        .seo-banner {{ background: linear-gradient(135deg, #f0f9ff, #e0f2fe); border: 2px solid #0ea5e9; border-radius: 12px; padding: 20px; margin-bottom: 30px; }}
        .seo-banner h1 {{ color: #0369a1; font-size: 24px; margin-bottom: 10px; font-weight: 900; line-height: 1.3; }}
        .seo-banner p {{ color: #0c4a6e; font-size: 14px; line-height: 1.6; margin: 0; }}
        
        .drawer-overlay {{ position: fixed; inset: 0; background: rgba(0,0,0,0.7); z-index: 200; display: none; }}
        .drawer-open .drawer-overlay {{ display: block; }}
        .cart-drawer {{ position: fixed; top: 0; left: 0; width: 360px; max-width: 90vw; height: 100%; background: white; z-index: 201; transform: translateX(-100%); transition: 0.3s; padding: 20px; display: flex; flex-direction: column; box-shadow: 2px 0 20px rgba(0,0,0,0.2); }}
        .drawer-open .cart-drawer {{ transform: translateX(0); }}
        .cart-item {{ display: flex; gap: 15px; border-bottom: 1px solid #eee; padding-bottom: 15px; margin-bottom: 15px; }}
        
        [x-cloak] {{ display: none !important; }}
        
        @media(max-width: 767px) {{
            .floating-buttons {{ bottom: 80px; right: 15px; }}
            .float-btn {{ width: 55px; height: 55px; font-size: 22px; }}
            .logo-text .main {{ font-size: 18px; }}
            .logo-icon {{ width: 38px; height: 38px; font-size: 18px; }}
            .prod-img-wrap {{ height: 200px; }}
        }}
    </style>
"""

# ==========================================
# 2. ALPINE LOGIC
# ==========================================
APP_JS = f"""
document.addEventListener('alpine:init', () => {{
    Alpine.store('cart', {{
        items: JSON.parse(localStorage.getItem('cart')) || [],
        open: false,
        toggle() {{ 
            this.open = !this.open; 
            document.body.classList.toggle('drawer-open'); 
        }},
        add(product) {{
            const existing = this.items.find(i => i.id === product.id);
            if (existing) {{ 
                existing.qty++; 
            }} else {{ 
                this.items.push({{...product, qty: 1}}); 
            }}
            this.save();
            if (navigator.vibrate) navigator.vibrate(50);
        }},
        remove(id) {{ 
            this.items = this.items.filter(i => i.id !== id); 
            this.save(); 
        }},
        save() {{ 
            localStorage.setItem('cart', JSON.stringify(this.items)); 
        }},
        get total() {{ 
            return this.items.reduce((sum, i) => sum + (i.price * i.qty), 0).toFixed(2); 
        }},
        get count() {{ 
            return this.items.reduce((sum, i) => sum + i.qty, 0); 
        }},
        checkout() {{
            if (this.items.length === 0) {{ 
                alert('السلة فارغة!'); 
                return; 
            }}
            
            let msg = `🛒 *طلب جديد من سوق الكويت*\\n`;
            msg += `━━━━━━━━━━━━━━━━━━━━━━━\\n\\n`;
            
            this.items.forEach((item, idx) => {{
                msg += `*${{idx + 1}}.* ${{item.title}}\\n`;
                msg += `   📦 الكمية: ${{item.qty}}\\n`;
                msg += `   💰 السعر: ${{item.price}} د.ك\\n`;
                msg += `   💵 الإجمالي: ${{(item.price * item.qty).toFixed(2)}} د.ك\\n\\n`;
            }});
            
            msg += `━━━━━━━━━━━━━━━━━━━━━━━\\n`;
            msg += `💵 *المجموع الكلي: ${{this.total}} د.ك*\\n\\n`;
            msg += `📍 *يرجى إرسال العنوان وطريقة الدفع*`;
            
            window.open(`https://wa.me/{WHATSAPP_NUMBER}?text=${{encodeURIComponent(msg)}}`, '_blank');
        }}
    }});
    
    Alpine.data('productPage', () => ({{
        product: null,
        loading: true,
        selectedImage: '',
        
        async init() {{
            const params = new URLSearchParams(window.location.search);
            const id = params.get('id');
            const kw = params.get('kw');
            
            if (!id) {{
                console.error('Product ID missing');
                return;
            }}
            
            try {{
                const res = await fetch('products_data_cleaned.json');
                if (!res.ok) throw new Error('Failed to load products');
                
                const data = await res.json();
                this.product = data.find(p => p.id == id);
                
                if (this.product) {{
                    this.selectedImage = this.product.media.main_image;
                    this.loading = false;
                    
                    if (kw) {{
                        const keyword = decodeURIComponent(kw).replace(/-/g, ' ');
                        document.title = `${{keyword}} | سوق الكويت`;
                        
                        const metaDesc = document.querySelector('meta[name="description"]');
                        if (metaDesc) {{
                            metaDesc.content = `اشتري ${{keyword}} بأفضل سعر في الكويت. ${{this.product.title}} - ${{this.product.pricing.sale}} د.ك. توصيل سريع ودفع عند الاستلام.`;
                        }}
                        
                        const banner = document.getElementById('seo-banner');
                        if (banner) {{
                            banner.innerHTML = `
                                <div class="seo-banner">
                                    <h1>🔍 ${{keyword}}</h1>
                                    <p>وجدنا لك أفضل عرض متاح في السوق الكويتي. تصفح التفاصيل واطلب الآن مع توصيل سريع!</p>
                                </div>
                            `;
                        }}
                    }} else {{
                        document.title = `${{this.product.title}} - سوق الكويت`;
                    }}
                    
                    this.injectSchema();
                }} else {{
                    console.error('Product not found');
                }}
            }} catch(e) {{ 
                console.error('Error loading product:', e); 
            }}
        }},
        
        selectImage(url) {{ 
            this.selectedImage = url; 
        }},
        
        injectSchema() {{
            const schema = {{
                "@context": "https://schema.org/",
                "@type": "Product",
                "name": this.product.title,
                "image": [this.product.media.main_image, ...(this.product.media.gallery || [])],
                "description": this.product.description,
                "sku": String(this.product.id),
                "brand": {{ "@type": "Brand", "name": "سوق الكويت" }},
                "offers": {{
                    "@type": "Offer",
                    "url": window.location.href,
                    "priceCurrency": "KWD",
                    "price": this.product.pricing.sale,
                    "priceValidUntil": "2026-12-31",
                    "availability": "https://schema.org/InStock",
                    "itemCondition": "https://schema.org/NewCondition"
                }}
            }};
            
            const script = document.createElement('script');
            script.type = 'application/ld+json';
            script.text = JSON.stringify(schema);
            document.head.appendChild(script);
        }},
        
        get waLink() {{
            if (!this.product) return '#';
            
            const pageUrl = window.location.href;
            let msg = `👋 *استفسار عن منتج*\\n\\n`;
            msg += `📦 *المنتج:* ${{this.product.title}}\\n`;
            msg += `💰 *السعر:* ${{this.product.pricing.sale}} د.ك\\n`;
            msg += `🔖 *الكود:* #${{this.product.id}}\\n\\n`;
            msg += `🔗 *الرابط:*\\n${{pageUrl}}\\n\\n`;
            msg += `❓ *هل المنتج متوفر حالياً؟*`;
            
            return `https://wa.me/{WHATSAPP_NUMBER}?text=${{encodeURIComponent(msg)}}`;
        }}
    }}));
}});
"""

# ==========================================
# 3. INDEX HTML
# ==========================================
INDEX_HTML = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    """ + COMMON_HEAD + """
    <title>سوق الكويت - أفضل العروض والأسعار التنافسية</title>
    <meta name="description" content="تسوق آلاف المنتجات بأفضل الأسعار في الكويت. توصيل سريع، دفع عند الاستلام، منتجات أصلية 100%.">
    <link rel="canonical" href=\"""" + CLOUDFLARE_URL + """\">
</head>
<body x-data="{ 
    products: [], search: '', limit: 12, loading: true,
    get filtered() { return this.search ? this.products.filter(p => p.title.includes(this.search)) : this.products; },
    loadMore() { this.limit += 12; }
}" x-init="fetch('products_data_cleaned.json').then(r=>r.json()).then(d=>{ products=d; loading=false; }).catch(e=>console.error('Error loading products:', e))">

    <div class="top-bar">
        <div class="container" style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:10px">
            <span><i class="fa-brands fa-whatsapp"></i> خدمة عملاء 24/7</span>
            <span>توصيل مجاني للطلبات فوق 20 د.ك 🚚</span>
        </div>
    </div>

    <div class="header-main">
        <div class="container" style="display:flex; align-items:center; width:100%; flex-wrap:wrap; gap:15px">
            <a href="index.html" class="logo">
                <div class="logo-icon"><i class="fa-solid fa-store"></i></div>
                <div class="logo-text">
                    <span class="main">سوق الكويت</span>
                    <span class="sub">Kuwait Market</span>
                </div>
            </a>
            
            <div class="wood-search" style="display:none">
                <input x-model="search" type="text" placeholder="ابحث عن المنتجات..." aria-label="بحث">
                <button type="button" aria-label="بحث"><i class="fa-solid fa-magnifying-glass"></i></button>
            </div>
            <style>@media(min-width: 768px) { .wood-search { display: block !important; } }</style>
            
            <div class="header-actions" style="margin-right: auto">
                <div class="icon-link" @click="$store.cart.toggle()">
                    <i class="fa-solid fa-basket-shopping"></i>
                    <span x-text="$store.cart.total + ' د.ك'"></span>
                    <span class="cart-count" x-text="$store.cart.count" x-show="$store.cart.count > 0" x-cloak></span>
                </div>
            </div>
        </div>
    </div>

    <div class="container" style="margin-top:20px">
        <div class="wood-search" style="margin:0; max-width:100%; display:block">
            <input x-model="search" type="text" placeholder="ابحث عن المنتجات..." aria-label="بحث">
            <button type="button" aria-label="بحث"><i class="fa-solid fa-magnifying-glass"></i></button>
        </div>
    </div>
    <style>@media(min-width: 768px) { .container > .wood-search { display: none !important; } }</style>

    <div class="container" style="margin-top: 40px; text-align:center" x-show="!search" x-cloak>
        <h1 style="font-size:32px; font-weight:900; color:#2d2a2a; margin-bottom:10px">منتجات حصرية بأسعار منافسة</h1>
        <div style="width:60px; height:3px; background:var(--wood-primary); margin:0 auto"></div>
        <p style="color:#777; margin-top:15px">تسوق الآن واستمتع بالتوصيل السريع</p>
    </div>

    <div class="container">
        <!-- Loading State -->
        <div x-show="loading" style="text-align:center; padding:60px 0">
            <div style="display:inline-block; width:50px; height:50px; border:5px solid #f3f3f3; border-top:5px solid var(--wood-primary); border-radius:50%; animation:spin 1s linear infinite"></div>
            <style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); }}</style>
        </div>

        <div class="products-grid" x-show="!loading" x-cloak>
            <template x-for="p in filtered.slice(0, limit)" :key="p.id">
                <div class="product-card">
                    <a :href="'product.html?id=' + p.id" class="prod-img-wrap">
                        <img :src="p.media.main_image" :alt="p.title" class="prod-img" loading="lazy">
                    </a>
                    <a :href="'product.html?id=' + p.id" class="prod-title" x-text="p.title"></a>
                    <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px">
                        <span class="prod-price" x-text="p.pricing.sale + ' د.ك'"></span>
                        <span class="old-price" x-text="p.pricing.regular + ' د.ك'"></span>
                    </div>
                    <button class="wood-btn" @click="$store.cart.add({id: p.id, title: p.title, price: p.pricing.sale})" type="button">
                        <i class="fa-solid fa-cart-shopping"></i> أضف للسلة
                    </button>
                </div>
            </template>
        </div>
        
        <div style="text-align:center; margin:50px 0" x-show="!loading && limit < filtered.length" x-cloak>
            <button @click="loadMore()" class="wood-btn" style="width:auto; padding:14px 50px; background:var(--wood-dark); color:white" type="button">
                تحميل المزيد
            </button>
        </div>

        <!-- No Results -->
        <div x-show="!loading && filtered.length === 0" style="text-align:center; padding:60px 20px; color:#999" x-cloak>
            <i class="fa-solid fa-box-open" style="font-size:60px; margin-bottom:20px; opacity:0.3"></i>
            <p style="font-size:18px; font-weight:bold">لا توجد نتائج</p>
        </div>
    </div>

    <div class="floating-buttons">
        <a href="https://wa.me/""" + WHATSAPP_NUMBER + """" class="float-btn float-whatsapp" title="تواصل معنا عبر واتساب" aria-label="واتساب">
            <i class="fa-brands fa-whatsapp"></i>
        </a>
        <div class="float-btn float-cart" @click="$store.cart.toggle()" title="عرض السلة" aria-label="السلة">
            <i class="fa-solid fa-cart-shopping"></i>
            <span class="float-badge" x-text="$store.cart.count" x-show="$store.cart.count > 0" x-cloak></span>
        </div>
    </div>

    <div class="drawer-overlay" @click="$store.cart.toggle()"></div>
    <div class="cart-drawer">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; padding-bottom:15px; border-bottom:2px solid #eee">
            <h3 style="font-weight:900; font-size:20px; margin:0">سلة المشتريات</h3>
            <button @click="$store.cart.toggle()" style="background:none; border:none; cursor:pointer; font-size:24px; color:#999" type="button" aria-label="إغلاق">
                <i class="fa-solid fa-xmark"></i>
            </button>
        </div>
        
        <div style="flex:1; overflow-y:auto">
            <template x-for="item in $store.cart.items" :key="item.id">
                <div class="cart-item">
                    <div style="width:70px; height:70px; background:#f5f5f5; border-radius:8px; display:flex; align-items:center; justify-content:center">
                        <i class="fa-solid fa-box" style="color:#ccc; font-size:24px"></i>
                    </div>
                    <div style="flex:1; min-width:0">
                        <div style="font-size:13px; font-weight:700; margin-bottom:5px; line-height:1.3" x-text="item.title"></div>
                        <div style="font-size:12px; color:#777">
                            <span x-text="item.qty"></span> × 
                            <span style="color:var(--wood-primary); font-weight:bold" x-text="item.price + ' د.ك'"></span>
                        </div>
                    </div>
                    <button @click="$store.cart.remove(item.id)" style="background:none; border:none; cursor:pointer; color:#ddd; font-size:16px; padding:5px" type="button" title="حذف" aria-label="حذف المنتج">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </div>
            </template>
            
            <div x-show="$store.cart.count === 0" style="text-align:center; margin-top:80px; color:#999" x-cloak>
                <i class="fa-solid fa-cart-shopping" style="font-size:60px; opacity:0.2; margin-bottom:15px"></i>
                <p style="font-size:16px">السلة فارغة</p>
            </div>
        </div>
        
        <div style="border-top:2px solid #eee; padding-top:20px; margin-top:20px">
            <div style="display:flex; justify-content:space-between; font-weight:900; font-size:20px; margin-bottom:20px">
                <span>المجموع:</span>
                <span style="color:var(--wood-primary)" x-text="$store.cart.total + ' د.ك'"></span>
            </div>
            <button class="wood-btn wood-btn-primary" @click="$store.cart.checkout()" type="button" style="padding:15px; font-size:15px; display:flex; align-items:center; justify-content:center; gap:8px">
                <i class="fa-brands fa-whatsapp"></i>
                <span>إتمام الطلب عبر واتساب</span>
            </button>
        </div>
    </div>

    <script src="app.js"></script>
</body>
</html>
"""

# ==========================================
# 4. PRODUCT PAGE
# ==========================================
PRODUCT_HTML = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    """ + COMMON_HEAD + """
    <title>تفاصيل المنتج - سوق الكويت</title>
    <meta name="description" content="تفاصيل كاملة عن المنتج مع الصور والمواصفات والأسعار التنافسية.">
</head>
<body x-data="productPage">
    
    <div class="header-main">
        <div class="container" style="display:flex; justify-content:space-between; align-items:center">
            <a href="index.html" class="logo">
                <div class="logo-icon"><i class="fa-solid fa-store"></i></div>
                <div class="logo-text">
                    <span class="main">سوق الكويت</span>
                    <span class="sub">Kuwait Market</span>
                </div>
            </a>
            <div class="icon-link" @click="$store.cart.toggle()">
                <i class="fa-solid fa-basket-shopping"></i>
                <span class="cart-count" x-text="$store.cart.count" x-show="$store.cart.count > 0" x-cloak></span>
            </div>
        </div>
    </div>

    <!-- Loading State -->
    <div x-show="loading" style="text-align:center; padding:100px 0">
        <div style="display:inline-block; width:50px; height:50px; border:5px solid #f3f3f3; border-top:5px solid var(--wood-primary); border-radius:50%; animation:spin 1s linear infinite"></div>
    </div>

    <div class="container" style="padding-top:30px; padding-bottom:100px" x-show="!loading" x-cloak>
        
        <div id="seo-banner"></div>
        
        <div style="display:grid; grid-template-columns: 1fr; gap:40px">
            <style>@media(min-width:768px) { .container > div:last-of-type { grid-template-columns: 1fr 1fr !important; } }</style>
            
            <div class="product-gallery">
                <div class="main-image">
                    <img :src="selectedImage" :alt="product?.title" loading="eager">
                </div>
                <div class="thumbnails">
                    <div class="thumb" :class="{'active': selectedImage === product?.media.main_image}" @click="selectImage(product.media.main_image)" role="button" tabindex="0">
                        <img :src="product?.media.main_image" :alt="product?.title">
                    </div>
                    <template x-for="(img, idx) in product?.media?.gallery" :key="idx">
                        <div class="thumb" :class="{'active': selectedImage === img}" @click="selectImage(img)" role="button" tabindex="0">
                            <img :src="img" :alt="product?.title + ' - صورة ' + (idx + 2)">
                        </div>
                    </template>
                </div>
            </div>
            
            <div>
                <h1 style="font-size:28px; font-weight:900; margin-bottom:15px; line-height:1.3" x-text="product?.title"></h1>
                
                <div style="display:flex; align-items:center; margin-bottom:20px; padding-bottom:20px; border-bottom:1px solid #eee; flex-wrap:wrap; gap:10px">
                    <span style="font-size:32px; font-weight:900; color:var(--wood-primary)" x-text="product?.pricing.sale + ' د.ك'"></span>
                    <span style="font-size:18px; color:#bbb; text-decoration:line-through" x-text="product?.pricing.regular + ' د.ك'"></span>
                    <span style="background:#ff4444; color:white; padding:5px 12px; border-radius:20px; font-size:12px; font-weight:bold">
                        وفّر <span x-text="Math.round(((product?.pricing.regular - product?.pricing.sale) / product?.pricing.regular) * 100) + '%'"></span>
                    </span>
                </div>
                
                <div style="margin-bottom:30px">
                    <h2 style="font-weight:900; margin-bottom:10px; font-size:17px">📝 وصف المنتج</h2>
                    <p style="color:#666; line-height:1.8; font-size:14px" x-html="product?.description?.replace(/\\n/g, '<br>')"></p>
                </div>
                
                <div style="margin-bottom:30px">
                    <h3 style="font-weight:900; margin-bottom:15px; font-size:17px">📊 المواصفات والتفاصيل</h3>
                    <table class="specs-table">
                        <tr><td>🔖 رقم المنتج</td><td x-text="'#' + product?.id"></td></tr>
                        <tr><td>✅ الحالة</td><td style="color:#22c55e; font-weight:700">متوفر في المخزون</td></tr>
                        <tr><td>💰 السعر الأصلي</td><td x-text="product?.pricing.regular + ' د.ك'"></td></tr>
                        <tr><td>🔥 السعر الحالي</td><td style="color:var(--wood-primary); font-weight:700" x-text="product?.pricing.sale + ' د.ك'"></td></tr>
                        <tr><td>🚚 التوصيل</td><td>مجاني للطلبات فوق 20 د.ك</td></tr>
                        <tr><td>💳 الدفع</td><td>عند الاستلام أو أونلاين</td></tr>
                        <tr><td>🔒 الضمان</td><td>ضمان الجودة من المتجر</td></tr>
                    </table>
                </div>
                
                <button class="wood-btn wood-btn-primary" style="padding:16px; font-size:16px" type="button"
                        @click="$store.cart.add({id: product.id, title: product.title, price: product.pricing.sale}); $store.cart.toggle()">
                    <i class="fa-solid fa-cart-shopping"></i> إضافة إلى السلة
                </button>
                
                <a :href="waLink" class="wood-btn" style="background:#25D366; color:white; display:block; text-align:center; margin-top:12px; padding:16px; font-size:16px">
                    <i class="fa-brands fa-whatsapp"></i> استفسار مباشر عبر واتساب
                </a>
            </div>
        </div>
    </div>

    <div class="floating-buttons">
        <a :href="waLink" class="float-btn float-whatsapp" title="استفسار واتساب" aria-label="واتساب">
            <i class="fa-brands fa-whatsapp"></i>
        </a>
        <div class="float-btn float-cart" @click="$store.cart.toggle()" title="السلة" aria-label="السلة">
            <i class="fa-solid fa-cart-shopping"></i>
            <span class="float-badge" x-text="$store.cart.count" x-show="$store.cart.count > 0" x-cloak></span>
        </div>
    </div>

    <div class="drawer-overlay" @click="$store.cart.toggle()"></div>
    <div class="cart-drawer">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; border-bottom:2px solid #eee; padding-bottom:15px">
            <h3 style="font-weight:900; font-size:20px; margin:0">السلة</h3>
            <button @click="$store.cart.toggle()" style="background:none; border:none; cursor:pointer; font-size:24px; color:#999" type="button" aria-label="إغلاق">
                <i class="fa-solid fa-xmark"></i>
            </button>
        </div>
        <div style="flex:1; overflow-y:auto">
            <template x-for="item in $store.cart.items">
                <div class="cart-item">
                    <div style="width:70px; height:70px; background:#f5f5f5; border-radius:8px; display:flex; align-items:center; justify-content:center">
                        <i class="fa-solid fa-box" style="color:#ccc; font-size:24px"></i>
                    </div>
                    <div style="flex:1; min-width:0">
                        <div style="font-size:13px; font-weight:700; line-height:1.3" x-text="item.title"></div>
                        <div style="font-size:12px; color:#777; margin-top:5px">
                            <span x-text="item.qty"></span> × 
                            <span style="color:var(--wood-primary); font-weight:bold" x-text="item.price"></span>
                        </div>
                    </div>
                    <button @click="$store.cart.remove(item.id)" style="background:none; border:none; cursor:pointer; color:#ddd; font-size:16px" type="button" title="حذف" aria-label="حذف">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </div>
            </template>
        </div>
        <div style="border-top:2px solid #eee; padding-top:20px; margin-top:20px">
            <div style="display:flex; justify-content:space-between; font-weight:900; font-size:20px; margin-bottom:20px">
                <span>المجموع:</span>
                <span style="color:var(--wood-primary)" x-text="$store.cart.total + ' د.ك'"></span>
            </div>
            <button class="wood-btn wood-btn-primary" @click="$store.cart.checkout()" type="button" style="padding:15px">
                <i class="fa-brands fa-whatsapp"></i> إتمام الطلب
            </button>
        </div>
    </div>
    
    <script src="app.js"></script>
</body>
</html>
"""

# ==========================================
# 5. SITEMAP GENERATOR (FIXED)
# ==========================================
def generate_mass_seo_sitemap():
    """
    توليد Sitemap احترافي مع encoding صحيح
    """
    print("⏳ جاري إنشاء Sitemap...")
    
    try:
        with open(INPUT_JSON, 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        with open(f"{OUTPUT_DIR}/{INPUT_JSON}", 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
    
    except FileNotFoundError:
        print(f"❌ خطأ: {INPUT_JSON} غير موجود")
        return
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return

    urls = []
    
    def clean_slug(text):
        text = re.sub(r'[^\w\s\u0600-\u06FF-]', '', text)
        text = text.strip().replace(' ', '-')
        text = re.sub(r'-+', '-', text)
        return text

    seo_templates = [
        "شراء {title} اونلاين الكويت",
        "سعر {title} توصيل سريع",
        "افضل {title} اصلية الكويت",
        "{title} عرض خاص محدود",
        "{title} بسعر مخفض الكويت",
        "طلب {title} دفع عند الاستلام",
        "{title} توصيل مجاني",
        "احدث {title} 2026",
    ]

    for product in products:
        pid = product.get('id')
        title = product.get('title', '').strip()
        
        if not pid or not title:
            continue

        for template in seo_templates:
            keyword = template.format(title=title)
            slug = clean_slug(keyword)
            encoded_slug = urllib.parse.quote(slug, safe='')
            full_url = f"{CLOUDFLARE_URL}/product.html?id={pid}&kw={encoded_slug}"
            urls.append(full_url)

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    
    xml_lines.append('  <url>')
    xml_lines.append(f'    <loc>{xml_escape.escape(CLOUDFLARE_URL)}/</loc>')
    xml_lines.append('    <changefreq>daily</changefreq>')
    xml_lines.append('    <priority>1.0</priority>')
    xml_lines.append('  </url>')
    
    for url in urls:
        escaped_url = xml_escape.escape(url)
        xml_lines.append('  <url>')
        xml_lines.append(f'    <loc>{escaped_url}</loc>')
        xml_lines.append('    <changefreq>daily</changefreq>')
        xml_lines.append('    <priority>0.8</priority>')
        xml_lines.append('  </url>')
    
    xml_lines.append('</urlset>')

    sitemap_path = f"{OUTPUT_DIR}/sitemap.xml"
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write("\n".join(xml_lines))
    
    print(f"✅ تم إنشاء {len(urls):,} رابط SEO!")
    print(f"📄 الملف: {sitemap_path}")

# ==========================================
# 6. BUILD
# ==========================================
def main():
    print("🚀 بدء البناء...")
    print(f"📦 اسم المشروع: {PROJECT_NAME}")
    print(f"🌐 الرابط: {CLOUDFLARE_URL}")
    print(f"📱 واتساب: +{WHATSAPP_NUMBER}")
    print("━" * 50)
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"✅ مجلد: {OUTPUT_DIR}")
    
    print("📝 كتابة الملفات...")
    with open(f"{OUTPUT_DIR}/index.html", "w", encoding="utf-8") as f:
        f.write(INDEX_HTML)
    print("   ✓ index.html")
    
    with open(f"{OUTPUT_DIR}/product.html", "w", encoding="utf-8") as f:
        f.write(PRODUCT_HTML)
    print("   ✓ product.html")
    
    with open(f"{OUTPUT_DIR}/app.js", "w", encoding="utf-8") as f:
        f.write(APP_JS)
    print("   ✓ app.js")
    
    with open(f"{OUTPUT_DIR}/robots.txt", "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {CLOUDFLARE_URL}/sitemap.xml\n")
    print("   ✓ robots.txt")
    
    with open(f"{OUTPUT_DIR}/_headers", "w", encoding="utf-8") as f:
        f.write("/*\n  Cache-Control: public, max-age=3600\n  X-Robots-Tag: all\n\n/sitemap.xml\n  Content-Type: application/xml; charset=utf-8\n")
    print("   ✓ _headers")
    
    generate_mass_seo_sitemap()
    
    print("\n📦 إنشاء ZIP...")
    zip_filename = f"{PROJECT_NAME}_READY.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(OUTPUT_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, OUTPUT_DIR)
                zipf.write(file_path, arcname)
    
    print("\n" + "━" * 50)
    print("✅ تم البناء بنجاح!")
    print(f"📦 الملف: {zip_filename}")
    print(f"🌐 الموقع: {CLOUDFLARE_URL}")
    print(f"📱 واتساب: +{WHATSAPP_NUMBER}")
    print("━" * 50)
    print("\n📋 خطوات الرفع:")
    print("1. استخرج محتويات مجلد dist_sooq")
    print("2. اذهب إلى Cloudflare Pages Dashboard")
    print("3. افتح مشروع sooq-alkuwait-pro")
    print("4. اضغط Create deployment")
    print("5. ارفع جميع الملفات من dist_sooq")
    print("6. اضغط Deploy")
    print("━" * 50)

if __name__ == "__main__":
    main()
