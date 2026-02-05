
document.addEventListener('alpine:init', () => {
    Alpine.store('cart', {
        items: JSON.parse(localStorage.getItem('cart')) || [],
        open: false,
        toggle() { 
            this.open = !this.open; 
            document.body.classList.toggle('drawer-open'); 
        },
        add(product) {
            const existing = this.items.find(i => i.id === product.id);
            if (existing) { 
                existing.qty++; 
            } else { 
                this.items.push({...product, qty: 1}); 
            }
            this.save();
            if (navigator.vibrate) navigator.vibrate(50);
        },
        remove(id) { 
            this.items = this.items.filter(i => i.id !== id); 
            this.save(); 
        },
        save() { 
            localStorage.setItem('cart', JSON.stringify(this.items)); 
        },
        get total() { 
            return this.items.reduce((sum, i) => sum + (i.price * i.qty), 0).toFixed(2); 
        },
        get count() { 
            return this.items.reduce((sum, i) => sum + i.qty, 0); 
        },
        checkout() {
            if (this.items.length === 0) { 
                alert('السلة فارغة!'); 
                return; 
            }
            
            let msg = `🛒 *طلب جديد من سوق الكويت*\n`;
            msg += `━━━━━━━━━━━━━━━━━━━━━━━\n\n`;
            
            this.items.forEach((item, idx) => {
                msg += `*${idx + 1}.* ${item.title}\n`;
                msg += `   📦 الكمية: ${item.qty}\n`;
                msg += `   💰 السعر: ${item.price} د.ك\n`;
                msg += `   💵 الإجمالي: ${(item.price * item.qty).toFixed(2)} د.ك\n\n`;
            });
            
            msg += `━━━━━━━━━━━━━━━━━━━━━━━\n`;
            msg += `💵 *المجموع الكلي: ${this.total} د.ك*\n\n`;
            msg += `📍 *يرجى إرسال العنوان وطريقة الدفع*`;
            
            window.open(`https://wa.me/201110760081?text=${encodeURIComponent(msg)}`, '_blank');
        }
    });
    
    Alpine.data('productPage', () => ({
        product: null,
        loading: true,
        selectedImage: '',
        
        async init() {
            const params = new URLSearchParams(window.location.search);
            const id = params.get('id');
            const kw = params.get('kw');
            
            if (!id) {
                console.error('Product ID missing');
                return;
            }
            
            try {
                const res = await fetch('products_data_cleaned.json');
                if (!res.ok) throw new Error('Failed to load products');
                
                const data = await res.json();
                this.product = data.find(p => p.id == id);
                
                if (this.product) {
                    this.selectedImage = this.product.media.main_image;
                    this.loading = false;
                    
                    if (kw) {
                        const keyword = decodeURIComponent(kw).replace(/-/g, ' ');
                        document.title = `${keyword} | سوق الكويت`;
                        
                        const metaDesc = document.querySelector('meta[name="description"]');
                        if (metaDesc) {
                            metaDesc.content = `اشتري ${keyword} بأفضل سعر في الكويت. ${this.product.title} - ${this.product.pricing.sale} د.ك. توصيل سريع ودفع عند الاستلام.`;
                        }
                        
                        const banner = document.getElementById('seo-banner');
                        if (banner) {
                            banner.innerHTML = `
                                <div class="seo-banner">
                                    <h1>🔍 ${keyword}</h1>
                                    <p>وجدنا لك أفضل عرض متاح في السوق الكويتي. تصفح التفاصيل واطلب الآن مع توصيل سريع!</p>
                                </div>
                            `;
                        }
                    } else {
                        document.title = `${this.product.title} - سوق الكويت`;
                    }
                    
                    this.injectSchema();
                } else {
                    console.error('Product not found');
                }
            } catch(e) { 
                console.error('Error loading product:', e); 
            }
        },
        
        selectImage(url) { 
            this.selectedImage = url; 
        },
        
        injectSchema() {
            const schema = {
                "@context": "https://schema.org/",
                "@type": "Product",
                "name": this.product.title,
                "image": [this.product.media.main_image, ...(this.product.media.gallery || [])],
                "description": this.product.description,
                "sku": String(this.product.id),
                "brand": { "@type": "Brand", "name": "سوق الكويت" },
                "offers": {
                    "@type": "Offer",
                    "url": window.location.href,
                    "priceCurrency": "KWD",
                    "price": this.product.pricing.sale,
                    "priceValidUntil": "2026-12-31",
                    "availability": "https://schema.org/InStock",
                    "itemCondition": "https://schema.org/NewCondition"
                }
            };
            
            const script = document.createElement('script');
            script.type = 'application/ld+json';
            script.text = JSON.stringify(schema);
            document.head.appendChild(script);
        },
        
        get waLink() {
            if (!this.product) return '#';
            
            const pageUrl = window.location.href;
            let msg = `👋 *استفسار عن منتج*\n\n`;
            msg += `📦 *المنتج:* ${this.product.title}\n`;
            msg += `💰 *السعر:* ${this.product.pricing.sale} د.ك\n`;
            msg += `🔖 *الكود:* #${this.product.id}\n\n`;
            msg += `🔗 *الرابط:*\n${pageUrl}\n\n`;
            msg += `❓ *هل المنتج متوفر حالياً؟*`;
            
            return `https://wa.me/201110760081?text=${encodeURIComponent(msg)}`;
        }
    }));
});
