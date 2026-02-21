import React, { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import ChatInterface from './ChatInterface';
import '../styles/Dashboard.css';

function Dashboard() {
  const [chatReset, setChatReset] = useState(0);
  const handleNewChat = () => {
    setChatReset(prev => prev + 1);
  };
  
  return (
    <div className="dashboard">
      <Sidebar onNewChat={handleNewChat} />
      <div className="main-content">
        <div className="chat-header">
          <h2>Support Ticket Assistant</h2>
          <p>Describe your issue and I'll help resolve it in 2 attempts!</p>
        </div>
        <ChatInterface key={chatReset} />
      </div>
    </div>
  );
}
export default Dashboard;
