import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function RegisterPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [email, setEmail] = useState('');
    const [message, setMessage] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (event) => {
        event.preventDefault();
        setMessage('');

        const userData = {
            username: username,
            password: password,
            email: email
        };

        try {
            // Nginx will be at http://localhost (port 80 by default)
            // The /auth/ prefix is handled by Nginx reverse proxy
            const response = await axios.post('${process.env.REACT_APP_API_BASE_URL}/auth/register', userData, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.status === 201) {
                setMessage('Registrasi berhasil! Silakan login.');
                // Redirect to login page after a short delay or on button click
                setTimeout(() => {
                    navigate('/login');
                }, 2000); // Redirect after 2 seconds
            } else {
                setMessage('Registrasi gagal. Respons tidak valid.');
            }
        } catch (error) {
            if (error.response) {
                 setMessage(`Error: ${error.response.data.detail || 'Terjadi kesalahan saat registrasi.'}`);
            } else if (error.request) {
                setMessage('Error: Tidak ada respons dari server. Cek koneksi atau server backend.');
            } else {
                setMessage(`Error: ${error.message}`);
            }
        }
    };

    return (
        <div>
            <h2>Registrasi Pengguna Baru</h2>
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
                    <label htmlFor="email">Email:</label>
                    <input
                        type="email"
                        id="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
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
                <button type="submit">Register</button>
            </form>
            {message && <p>{message}</p>}
        </div>
    );
}

export default RegisterPage;
