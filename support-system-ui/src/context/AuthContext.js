import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();  //This context will be used to store and share authentication-related data across the application.

//useAuth hook : which allows any component that calls this hook to access the authentication context
export const useAuth = () => {
  return useContext(AuthContext);   //(AuthContext). This provides easy access to the authentication data, such as user, token, login, logout, etc.
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      // Verify token and fetch user data
      fetchUserData();
    }
    setLoading(false);
  }, [token]);

  const fetchUserData = async () => {
    try {
      const response = await axios.get('http://localhost:8000/user', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user data:', error);
      logout();
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post('http://localhost:8000/login', {
        email,
        password
      });
      const { token, user } = response.data;
      localStorage.setItem('token', token);
      setToken(token);
      setUser(user);
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.message || 'Login failed' 
      };
    }
  };

  const signup = async (userData) => {
    try {
      const response = await axios.post('http://localhost:8000/signup', userData);
      const { token, user } = response.data;
      localStorage.setItem('token', token);
      setToken(token);
      setUser(user);
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.message || 'Signup failed' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  const refreshUser = async () => {
  if (token) {
    await fetchUserData(); 
  }
};

  const value = {
    user,
    token,
    login,
    signup,
    logout,
    loading,
    refreshUser
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
