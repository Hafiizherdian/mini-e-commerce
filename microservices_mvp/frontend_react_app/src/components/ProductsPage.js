import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Helper function to decode JWT (basic implementation)
// In a real app, consider using a library like jwt-decode
function decodeJwt(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    } catch (e) {
        console.error("Error decoding JWT:", e);
        return null;
    }
}


function ProductsPage() {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [orderMessage, setOrderMessage] = useState('');
    // State to hold quantity for each product: { productId: quantity }
    const [quantities, setQuantities] = useState({});

    useEffect(() => {
        const fetchProducts = async () => {
            setLoading(true);
            setError('');
            setOrderMessage('');
            try {
                const response = await axios.get('${process.env.REACT_APP_API_BASE_URL}/products');
                if (response.status === 200) {
                    setProducts(response.data);
                    // Initialize quantities to 1 for each product
                    const initialQuantities = {};
                    response.data.forEach(product => {
                        initialQuantities[product.id] = 1;
                    });
                    setQuantities(initialQuantities);
                } else {
                    setError(`Gagal memuat produk. Status: ${response.status}`);
                }
            } catch (err) {
                if (err.response) {
                    setError(`Error: ${err.response.data.detail || 'Gagal mengambil data produk.'}`);
                } else if (err.request) {
                    setError('Error: Tidak ada respons dari server. Cek koneksi atau server backend.');
                } else {
                    setError(`Error: ${err.message}`);
                }
            } finally {
                setLoading(false);
            }
        };
        fetchProducts();
    }, []);

    const handleQuantityChange = (productId, value) => {
        const quantity = parseInt(value, 10);
        setQuantities(prevQuantities => ({
            ...prevQuantities,
            [productId]: quantity > 0 ? quantity : 1 // Ensure quantity is at least 1
        }));
    };

    const handleOrder = async (productId) => {
        setOrderMessage('');
        const token = localStorage.getItem('token');
        if (!token) {
            setOrderMessage('Anda harus login untuk membuat pesanan.');
            alert('Anda harus login untuk membuat pesanan.');
            return;
        }

        const decodedToken = decodeJwt(token);
        let userId = null;
        if (decodedToken && decodedToken.sub) {
            userId = decodedToken.sub; // Using 'sub' claim (username) as a placeholder for user_id
        } else {
            setOrderMessage('Gagal mendapatkan ID pengguna dari token. Silakan login kembali.');
            alert('Gagal mendapatkan ID pengguna dari token. Silakan login kembali.');
            return;
        }

        const quantity = quantities[productId] || 1;

        const orderData = {
            user_id: userId, 
            items: [
                {
                    product_id: productId,
                    quantity: quantity
                }
            ]
        };

        try {
            const response = await axios.post('http://localhost/orders', orderData, {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.status === 201) {
                setOrderMessage(`Pesanan untuk produk ID ${productId} berhasil dibuat! (ID Pesanan: ${response.data.id})`);
                alert(`Pesanan berhasil dibuat! ID Pesanan: ${response.data.id}`);
            } else {
                setOrderMessage(`Gagal membuat pesanan. Status: ${response.status}`);
            }
        } catch (err) {
            if (err.response) {
                setOrderMessage(`Error membuat pesanan: ${err.response.data.detail || 'Terjadi kesalahan.'}`);
            } else if (err.request) {
                setOrderMessage('Error membuat pesanan: Tidak ada respons dari server.');
            } else {
                setOrderMessage(`Error membuat pesanan: ${err.message}`);
            }
        }
    };

    if (loading) {
        return <p>Memuat produk...</p>;
    }

    if (error) {
        return <p style={{ color: 'red' }}>{error}</p>;
    }

    if (products.length === 0) {
        return <p>Tidak ada produk yang tersedia saat ini.</p>;
    }

    return (
        <div>
            <h2>Daftar Produk</h2>
            {orderMessage && <p style={{ color: orderMessage.startsWith('Error') ? 'red' : 'green' }}>{orderMessage}</p>}
            <ul style={{ listStyleType: 'none', padding: 0 }}>
                {products.map(product => (
                    <li key={product.id} style={{ border: '1px solid #ccc', margin: '10px', padding: '10px' }}>
                        <h3>{product.name}</h3>
                        <p>Harga: Rp {product.price ? product.price.toLocaleString('id-ID') : 'N/A'}</p>
                        <div>
                            <label htmlFor={`quantity-${product.id}`}>Jumlah: </label>
                            <input
                                type="number"
                                id={`quantity-${product.id}`}
                                value={quantities[product.id] || 1}
                                onChange={(e) => handleQuantityChange(product.id, e.target.value)}
                                min="1"
                                style={{ width: '60px', marginRight: '10px' }}
                            />
                            <button onClick={() => handleOrder(product.id)}>
                                Pesan Sekarang
                            </button>
                        </div>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default ProductsPage;
