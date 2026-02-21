import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import '../styles/Profile.css';

function Profile() {
  const { user, logout, token, refreshUser } = useAuth(); 
  const [showDropdown, setShowDropdown] = useState(false);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (file) {
      const formData = new FormData();
      formData.append('file', file); 
      try {
        await axios.post('http://localhost:8000/upload-profile', formData, {
          headers: { 
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${token}` 
          }
        });
        alert('Profile picture updated successfully!');
        refreshUser();
      } catch (error) {
        console.error('Upload error:', error.response?.data || error.message);
        alert('Failed to upload profile picture');
      }
    }
  };
  
  return (
    <div className="profile">
      <div className="profile-header" onClick={() => setShowDropdown(!showDropdown)}>
        <div className="profile-picture">
          {user?.profilePicture ? (
            <img src={user.profilePicture} alt="Profile" />
          ) : (
            <div className="profile-initials">
              {user?.name?.charAt(0) || user?.email?.charAt(0) || 'U'}
            </div>
          )}
          <span className="online-indicator"></span>
        </div>
        <div className="profile-info">
          <h3>{user?.name || 'User'}</h3>
          <p>{user?.email || 'user@example.com'}</p>
        </div>
        <span className="dropdown-arrow">▼</span>
      </div>

      {showDropdown && (
        <div className="profile-dropdown">
          <label className="dropdown-item">
             Upload Photo
            <input
              type="file"
              accept="image/*"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
          </label>
          <button className="dropdown-item" onClick={logout}>
            Logout
          </button>
        </div>
      )}
    </div>
  );
}

export default Profile;