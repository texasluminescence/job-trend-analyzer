import logo from './logo.svg';
import './App.css';
import React, { useState, useEffect } from 'react';

function App() {
  const [message, setMessage] = useState('');

  useEffect(() => {
    // Call the FastAPI backend
    fetch('http://127.0.0.1:8000/test')
      .then(response => response.text())
      .then(data => setMessage(data))
      .catch(error => console.error("Error fetching data:", error));
  }, []);

  return (
    <div className="App">
        <h1>Job Analyzer</h1>
        <p>Message from API: {message}</p>
    </div>
  );
}

export default App;
