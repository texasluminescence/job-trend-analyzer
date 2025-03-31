import React, { useState, useEffect } from 'react';
import '../../components/JobsTable/trend-jobs.css'
import './home.css'
import TaskBar from '../../components/TaskBar/task-bar';
import JobsTable from "../../components/JobsTable/trend-jobs";
import SearchBar from "../../components/SearchBar/search-bar";
import SkillsTable from "../../components/SkillsTable/trend-skills";
import PopUp from "../../components/PopUp/pop-up";

function Home() {
  const [message, setMessage] = useState('');
  const [selectedIndustry, setSelectedIndustry] = useState('');
  const [popularRoles, setPopularRoles] = useState([]);
  const [industries, setIndustries] = useState([]);
  const [loadingRoles, setLoadingRoles] = useState(false);
  const [loadingSkills, setLoadingSkills] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => { 
    fetchIndustries();
  }, []);

  useEffect(() => {
    // Fetch popular roles when industry changes
    if (selectedIndustry) {
      fetchPopularRoles(selectedIndustry);
    } else {
      setPopularRoles([]);
    }
  }, [selectedIndustry]);

  const fetchIndustries = () => {
    fetch('http://127.0.0.1:8000/industries')
      .then(response => response.json())
      .then(data => setIndustries(data))
      .catch(error => {
        console.error("Error fetching industries:", error);
        setError("Failed to load industries. Please try again later.");
      });
  };

  const fetchPopularRoles = (industry) => {
    setLoadingRoles(true);
    setError('');
    // Call the API endpoint to fetch roles based on industry
    fetch(`http://127.0.0.1:8000/popular-roles?industry=${encodeURIComponent(industry)}`)
      .then(response => {
        if (!response.ok) {
          throw new Error('Industry not found or no roles available');
        }
        return response.json();
      })
      .then(data => {
        setPopularRoles(data);
        setLoadingRoles(false);
      })
      .catch(error => {
        console.error("Error fetching popular roles:", error);
        setPopularRoles([]);
        setLoadingRoles(false);
        setError("Could not find roles for the selected industry.");
      });
  };

  const handleIndustrySelect = (industryName) => {
    setSelectedIndustry(industryName);
    setError('');
  };

  return (
    <div className="App">
      <section className="jobs-section">
        <h2>Select an Industry</h2>
        <p className="description-text">Explore detailed information about roles in your industry</p>
        <SearchBar onSearch={handleIndustrySelect} placeholder="Select an industry" />
        
        {error && <div className="error-message">{error}</div>}
        
        {selectedIndustry && (
          <div className="selected-industry">
            <h3>Currently Viewing: <span className="industry-name">{selectedIndustry}</span></h3>
          </div>
        )}
      </section>

      <section className="jobs-section">
        <h2>These Jobs Are Currently Trending In {selectedIndustry || "Your Field"}</h2>
        <p className="description-text">Click Each Role For More Information</p>
        <JobsTable roles={popularRoles} loading={loadingRoles} />
      </section>

      <section className="jobs-section">
        <h2>These Skills Are Currently Trending In {selectedIndustry || "Your Field"}</h2>
        <p className="description-text">Click Each Skill For More Information</p>
        <SkillsTable industry={selectedIndustry} loading={loadingSkills} />
      </section>
    </div>
  );
}

export default Home;