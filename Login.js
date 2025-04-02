import React, { useState, useContext } from 'react';
import { loginUser } from '../services/api';
import AuthContext from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const Login = () => {
    const { login } = useContext(AuthContext);
    const [credentials, setCredentials] = useState({ email: '', password: '' });
    const navigate = useNavigate();

    const handleChange = (e) => {
        setCredentials({ ...credentials, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await loginUser(credentials);
            login(response.data.token);
            navigate('/dashboard');
        } catch (error) {
            console.error("❌ Login failed", error);
            alert("⚠️ Invalid email or password.");
        }
    };

    const handleGoogleLogin = () => {
        window.location.href = `${process.env.REACT_APP_API_URL}/api/auth/google`;
    };

    return (
        <div>
            <h1>Login</h1>
            <form onSubmit={handleSubmit}>
                <input type="email" name="email" placeholder="Email" onChange={handleChange} required />
                <input type="password" name="password" placeholder="Password" onChange={handleChange} required />
                <button type="submit">Login</button>
            </form>
            
            {/* <button onClick={handleGoogleLogin} style={{ marginTop: '10px', padding: '10px', backgroundColor: '#4285F4', color: 'white', border: 'none', cursor: 'pointer' }}>
                Sign in with Google
            </button> */}
        </div>
    );
};

export default Login;
