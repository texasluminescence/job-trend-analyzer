import React, { useState, useEffect } from 'react';
import '../../components/JobsTable/trend-jobs.css';
import './home.css';
import TaskBar from '../../components/TaskBar/task-bar';
import JobsTable from "../../components/JobsTable/trend-jobs";
import SearchBar from "../../components/SearchBar/search-bar";
import SkillsTable from "../../components/SkillsTable/trend-skills";
import PopUp from "../../components/PopUp/pop-up";

function Home() {
  const [message, setMessage] = useState('');
  const [selectedIndustry, setSelectedIndustry] = useState('');
  const [popularRoles, setPopularRoles] = useState([]);
  const [popularSkills, setPopularSkills] = useState([]);
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
      fetchDetailedPopularRoles(selectedIndustry);
      fetchDetailedPopularSkills(selectedIndustry);
    } else {
      setPopularRoles([]);
      setPopularSkills([]);
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

  const fetchDetailedPopularRoles = (industry) => {
    setLoadingRoles(true);
    setError('');
    // Call the enhanced API endpoint for detailed roles
    fetch(`http://127.0.0.1:8000/detailed-popular-roles?industry=${encodeURIComponent(industry)}`)
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
        console.error("Error fetching detailed popular roles:", error);
        // Fallback to the basic endpoint if enhanced endpoint fails
        fetchPopularRoles(industry);
      });
  };

  const fetchDetailedPopularSkills = (industry) => {
    setLoadingSkills(true);
    setError('');
    // Call the enhanced API endpoint for detailed skills
    fetch(`http://127.0.0.1:8000/detailed-popular-skills?industry=${encodeURIComponent(industry)}`)
      .then(response => {
        if (!response.ok) {
          throw new Error('Industry not found or no skills available');
        }
        return response.json();
      })
      .then(data => {
        setPopularSkills(data);
        setLoadingSkills(false);
      })
      .catch(error => {
        console.error("Error fetching detailed popular skills:", error);
        // Fallback to the basic endpoint if enhanced endpoint fails
        fetchPopularSkills(industry);
      });
  };

  // Fallback functions in case the enhanced endpoints are not available
  const fetchPopularRoles = (industry) => {
    fetch(`http://127.0.0.1:8000/popular-roles?industry=${encodeURIComponent(industry)}`)
      .then(response => {
        if (!response.ok) {
          throw new Error('Industry not found or no roles available');
        }
        return response.json();
      })
      .then(data => {
        // Convert string array to object array for compatibility
        const formattedData = data.map(role => ({
          title: role,
          roles: 'N/A',
          companies: 'Various companies'
        }));
        setPopularRoles(formattedData);
        setLoadingRoles(false);
      })
      .catch(error => {
        console.error("Error fetching popular roles:", error);
        setPopularRoles([]);
        setLoadingRoles(false);
        setError("Could not find roles for the selected industry.");
      });
  };

  const fetchPopularSkills = (industry) => {
    fetch(`http://127.0.0.1:8000/popular-skills?industry=${encodeURIComponent(industry)}`)
      .then(response => {
        if (!response.ok) {
          throw new Error('Industry not found or no skills available');
        }
        return response.json();
      })
      .then(data => {
        // Convert string array to object array for compatibility
        const formattedData = data.map(skill => ({
          skill: skill,
          jobs: 'Various positions',
          number: 'N/A'
        }));
        setPopularSkills(formattedData);
        setLoadingSkills(false);
      })
      .catch(error => {
        console.error("Error fetching popular skills:", error);
        setPopularSkills([]);
        setLoadingSkills(false);
        setError("Could not find skills for the selected industry.");
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
        <SearchBar 
          onSearch={handleIndustrySelect} 
          placeholder="Select an industry" 
          options={industries.map(industry => industry.name)} 
        />

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
        <SkillsTable 
          industry={selectedIndustry} 
          loading={loadingSkills} 
          popularSkills={popularSkills}
        />
      </section>
    </div>
  );
}

export default Home;