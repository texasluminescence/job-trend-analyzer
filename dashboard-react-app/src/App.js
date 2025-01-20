import logo from './logo.svg';
import './App.css';
import React, { useState, useEffect } from 'react';
import './trend-jobs.css'
import TaskBar from './task-bar';
import JobsTable from "./trend-jobs";
import SearchBar from "./search-bar";
import SkillsTable from "./trend-skills";


function App() {
  const [message, setMessage] = useState('');

  useEffect(() => {
    // Call the FastAPI backend
    fetch('http://127.0.0.1:8000/test')
      .then(response => response.text())
      .then(data => setMessage(data))
      .catch(error => console.error("Error fetching data:", error));
  }, []);

  const handleIndustrySearch = (query) => {
    // Console logs current industry user is searching
    console.log('Searching for industry: ${query}');
  }

  return (
    <div className="App">

        <section className = "task-bar">
          <TaskBar/>
        </section>

        <section className="jobs-section">
          <h2>Select an Industry</h2>
          <p className="description-text">Explore detailed information about roles in your industry</p>
          <SearchBar placeholder="Search for a industry" onSearch={handleIndustrySearch} />
        </section>

        <section className="jobs-section">
            <h2>These Jobs Are Currently Trending In Your Field</h2>
            <p className="description-text">Click Each Role For More Information</p>
            <JobsTable/>
        </section>

        <section className="jobs-section">
            <h2>These Skills Are Currently Trending In Your Field</h2>
            <p className="description-text">Click Each Skill For More Information</p>
            <SkillsTable/>
        </section>
    </div>
  );
}

export default App;
