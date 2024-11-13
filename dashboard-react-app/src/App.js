import logo from './logo.svg';
import './App.css';
import React, { useState, useEffect } from 'react';
import SearchBar from './search-bar';
import TaskBar from './task-bar';


function App() {
  const [message, setMessage] = useState('');

  useEffect(() => {
    // Call the FastAPI backend
    fetch('http://127.0.0.1:8000/test')
      .then(response => response.text())
      .then(data => setMessage(data))
      .catch(error => console.error("Error fetching data:", error));
  }, []);

  // Employer search bar
  const handleEmployerSearch = (query) => {
    // Console logs current employer user is searching
    console.log('Searching for employer: ' + query);
  };

  // Industry search bar - Will add soon
  const handleIndustrySearch = (query) => {
    // Console logs current industry user is searching
    console.log('Searching for industry: ${query}');
  }

  return (
    <div className="App">

        <section className = "task-bar">
          <TaskBar/>
        </section>

        <section className="search-section">
          <h2>Select an Employer</h2>
          <p className="description-text">Explore detailed information about different companies</p>
          <SearchBar placeholder="Search for a company" onSearch={handleEmployerSearch} />
        </section>
    </div>
  );
}

export default App;
