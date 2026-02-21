import { useAuth } from '../context/AuthContext';
import Profile from './Profile';
import '../styles/Sidebar.css';

function Sidebar({ onNewChat }) {
  const { user } = useAuth();

  const handleNewChat = () => {
    if (onNewChat) {
      onNewChat();
      alert('New chat started!'); 
    }
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h1>Support Agent</h1>
        <p className="tagline">AI-powered ticket resolution system</p>
      </div>
      
      <div className="profile-section">
        <Profile />
      </div>

      <div className="sidebar-menu">
        <button 
          className="menu-item active" 
          onClick={handleNewChat}
        >
          <span className="icon">💬</span>
          <span>New Chat</span>
        </button>
        
        <div className="section">
          <h3>ABOUT THIS CHATBOT</h3>
          <p className="description">
            This AI assistant helps resolve support tickets quickly. 
            Describe your issue clearly for the best assistance.
          </p>
        </div>
        </div>
        </div>
  );
}

export default Sidebar;