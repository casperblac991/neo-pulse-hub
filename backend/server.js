async function updateProducts() {
  console.log('🔄 Fetching products from CJ API...');
  try {
    const response = await fetch('https://developers.cjdropshipping.com/api2.0/v1/product/list', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.CJ_API_KEY}`, // استخدام Bearer Token
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        pageNum: 1,
        pageSize: 20,
        category: "Consumer Electronics"
      })
    });
    
    const data = await response.json();
    
    if (data && data.data && data.data.length > 0) {
      fs.writeFileSync('./products.json', JSON.stringify(data.data, null, 2));
      console.log(`✅ Products updated: ${data.data.length} products`);
    } else {
      console.log('⚠️ No products found:', data);
      fs.writeFileSync('./products.json', JSON.stringify([], null, 2));
    }
  } catch (error) {
    console.error('❌ Update failed:', error);
  }
}
