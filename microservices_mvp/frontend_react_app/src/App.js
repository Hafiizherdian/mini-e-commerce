import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom'; // Outlet dihilangkan jika tidak dipakai langsung di sini
import LoginPage from './components/LoginPage';
import RegisterPage from './components/RegisterPage';
import ProductsPage from './components/ProductsPage'; // Impor ProductsPage
import './App.css';

// Placeholder for HomePage
function HomePage() {
    return <h2>Selamat Datang di MVP Microservices!</h2>;
}

// Placeholder ProductsPage DIHAPUS karena sekarang diimpor dari file terpisah

// Komponen untuk menangani logout
function LogoutButton() {
    const navigate = useNavigate();
    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
        // Anda mungkin ingin memberi tahu App.js atau state global bahwa pengguna telah logout
    };

    return <button onClick={handleLogout}>Logout</button>;
}


function App() {
    // State untuk memantau status login, bisa diperluas nanti
    const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('token'));

    // Efek untuk memantau perubahan token di localStorage (opsional, tergantung kebutuhan)
    useEffect(() => {
        const handleStorageChange = () => {
            setIsLoggedIn(!!localStorage.getItem('token'));
        };
        window.addEventListener('storage', handleStorageChange); // Untuk perubahan di tab lain
        // Cek saat komponen dimuat
        setIsLoggedIn(!!localStorage.getItem('token'));
        return () => window.removeEventListener('storage', handleStorageChange);
    }, []);


    return (
        <Router>
            <div>
                <nav>
                    <ul>
                        <li><Link to="/">Home</Link></li>
                        {!isLoggedIn ? (
                            <>
                                <li><Link to="/login">Login</Link></li>
                                <li><Link to="/register">Register</Link></li>
                            </>
                        ) : (
                            <li><LogoutButton /></li>
                        )}
                        <li><Link to="/products">Produk</Link></li>
                    </ul>
                </nav>
                <hr />
                <div className="content">
                    <Routes>
                        <Route path="/" element={<HomePage />} />
                        <Route path="/login" element={<LoginPage />} />
                        <Route path="/register" element={<RegisterPage />} />
                        <Route path="/products" element={<ProductsPage />} />
                        {/* Anda bisa menambahkan route lain di sini */}
                    </Routes>
                </div>
            </div>
        </Router>
    );
}

export default App;
