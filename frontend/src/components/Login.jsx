// ./frontend/src/components/Login.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Login = () => {
  const clientId = import.meta.env.VITE_GITHUB_CLIENT_ID;
  const redirectUri = 'http://localhost:5173/login';
  const githubAuthUrl = `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=user:email`;

  const [user, setUser] = useState(null);

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');

    if (code) {
      axios
        .post(`${import.meta.env.VITE_API_URL}/api/auth/github/`, { code })
        .then((response) => {
          setUser(response.data.user);
          localStorage.setItem('access_token', response.data.access);
          localStorage.setItem('refresh_token', response.data.refresh);
          window.history.replaceState({}, document.title, '/login');
        })
        .catch((error) => {
          console.error('Login error:', error.response?.data?.error);
        });
    }
  }, []);

  if (user) {
    return (
      <div>
        <h2>Welcome, {user.username}!</h2>
        <p>Email: {user.email}</p>
      </div>
    );
  }

  return (
    <div>
      <h2>Login</h2>
      <a href={githubAuthUrl}>
        <button>Login with GitHub</button>
      </a>
    </div>
  );
};

export default Login;