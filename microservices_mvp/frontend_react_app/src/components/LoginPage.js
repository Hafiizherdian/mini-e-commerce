import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (event) => {
        event.preventDefault();
        setMessage('');

        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        try {
            // Nginx will be at http://localhost (port 80 by default)
            // The /auth/ prefix is handled by Nginx reverse proxy
            const response = await axios.post('${process.env.REACT_APP_API_BASE_URL}/auth/login', formData, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            });

            if (response.status === 200 && response.data.access_token) {
                localStorage.setItem('token', response.data.access_token);
                setMessage('Login berhasil! Mengarahkan ke halaman utama...');
                // Redirect to home or a protected page, e.g., /products
                navigate('/'); 
            } else {
                setMessage('Login gagal. Respons tidak valid.');
            }
        } catch (error) {
            if (error.response) {
                setMessage(`Error: ${error.response.data.detail || 'Username atau password salah.'}`);
            } else if (error.request) {
                setMessage('Error: Tidak ada respons dari server. Cek koneksi atau server backend.');
            } else {
                setMessage(`Error: ${error.message}`);
            }
        }
    };

    return (
        <div>
            <h2>Login Pengguna</h2>
            <form onSubmit={handleSubmit}>
                <div>
                    <label htmlFor="username">Username:</label>
                    <input
                        type="text"
                        id="username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label htmlFor="password">Password:</label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <button type="submit">Login</button>
            </form>
            {message && <p>{message}</p>}
        </div>
    );
}

export default LoginPage;
