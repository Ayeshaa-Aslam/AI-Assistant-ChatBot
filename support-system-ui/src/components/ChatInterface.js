import React, { useState, useEffect, useRef } from 'react';
import '../styles/ChatInterface.css';
import axios from 'axios';

function ChatInterface({ key }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [subject, setSubject] = useState('');
  const [description, setDescription] = useState('');
  const [attempts, setAttempts] = useState(0);
  const [isFirstMessage, setIsFirstMessage] = useState(true);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (key > 0) {
      setMessages([]);
      setInput('');
      setSubject('');
      setDescription('');
      setAttempts(0);
      setIsFirstMessage(true);
    }
  }, [key]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || attempts >= 3) return;
    
    const userMessage = {
      text: input,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, userMessage]);
    
    try {
      const response = await axios.post('http://localhost:8000/process-ticket', {
        subject: "Follow-up",
        description: input
      });
      
      const aiResponse = {
        text: response.data.response || "I understand your concern.",
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, aiResponse]);
      
    } catch (error) {
      const aiResponse = {
        text: "Having trouble connecting to AI. Please try again.",
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, aiResponse]);
    }
    
    const newAttempts = attempts + 1;
    setAttempts(newAttempts);
    
    if (newAttempts >= 3) {
      setTimeout(() => {
        const escalationMsg = {
          text: "Can't generate proper response after 3 attempts. Please contact human support.",
          sender: 'system',
          timestamp: new Date().toLocaleTimeString()
        };
        setMessages(prev => [...prev, escalationMsg]);
      }, 1500);
    }
    
    setInput('');
  };

  const createTicket = async () => {
    if (!subject || !description) {
      alert('Please enter subject and description');
      return;
    }

    try {
      const response = await axios.post('http://localhost:8000/process-ticket', {
        subject: subject,
        description: description
      });
      
      const userMessage = {
        text: `${subject}: ${description}`,
        sender: 'user',
        timestamp: new Date().toLocaleTimeString()
      };
      
      const aiResponse = {
        text: response.data.response || "Received your ticket.",
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };
      
      setMessages([userMessage, aiResponse]);
      setIsFirstMessage(false);
      setAttempts(1);
      
      setSubject('');
      setDescription('');
      
    } catch (error) {
      alert('Failed to create ticket: ' + error.message);
    }
  };

  return (
    <div className="chat-interface">
      {isFirstMessage ? (
        <div className="ticket-form">
          <h3>Create New Support Ticket</h3>
          <input
            type="text"
            placeholder="Enter ticket subject..."
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            className="form-input"
          />
          <textarea
            placeholder="Describe your issue in detail..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="form-textarea"
            rows="4"
          />
          <button onClick={createTicket} className="submit-btn">
            Submit Ticket
          </button>
        </div>
      ) : (
        <>
          <div className="chat-messages">
            {messages.map((msg, index) => (
              <div key={index} className={`message ${msg.sender}`}>
                <div className="message-content">
                  <span className="message-text">{msg.text}</span>
                  <span className="message-time">{msg.timestamp}</span>
                </div>
              </div>
            ))}
            {attempts >= 3 && (
              <div className="attempts-warning">
                Maximum attempts reached. A support agent will contact you shortly.
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          
          {attempts < 3 && (
            <form onSubmit={handleSubmit} className="chat-input-form">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your message..."
                className="chat-input"
                disabled={attempts >= 3}
              />
              <button type="submit" className="send-btn">
                Send
              </button>
            </form>
          )}
        </>
      )}
    </div>
  );
}

export default ChatInterface;