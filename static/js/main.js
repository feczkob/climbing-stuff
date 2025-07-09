const container = document.getElementById('discounts-container');
const select = document.getElementById('category-select');

async function renderProducts(category) {
    container.innerHTML = '<p>Loading...</p>';
    try {
        const resp = await fetch(`/discounts/${category}`);
        if (!resp.ok) {
            container.innerHTML = '<p>No discounts found.</p>';
            return;
        }
        const discounts = await resp.json();
        if (discounts.length === 0) {
            container.innerHTML = '<p>No discounts found.</p>';
            return;
        }
        container.innerHTML = '';
        discounts.forEach(d => {
            const div = document.createElement('div');
            div.className = 'product';
            div.innerHTML = `
                <div class="product-img">
                    <a href="${d.url}" target="_blank">
                        <img src="${d.image_url || ''}" alt="${d.product}">
                    </a>
                </div>
                <div class="product-details">
                    <div class="product-name">
                        <a href="${d.url}" target="_blank">${d.product}</a>
                        <span class="discount-percent">${d.discount_percent ? d.discount_percent : ''}${d.discount_percent ? '%' : ''}</span>
                    </div>
                    <div>
                        <span class="orig-price">${d.old_price || ''}</span>
                        <span class="disc-price">${d.new_price || ''}</span>
                    </div>
                    <div class="shop">${d.site || ''}</div>
                </div>
            `;
            container.appendChild(div);
        });
    } catch (e) {
        console.error(e)
        container.innerHTML = '<p>Error loading discounts.</p>';
    }
}

renderProducts(select.value);
select.addEventListener('change', function() {
    renderProducts(this.value);
});
