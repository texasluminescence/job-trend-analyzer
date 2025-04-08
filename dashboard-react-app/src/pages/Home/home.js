import React, { useState, useEffect } from 'react';
import './home.css';
import TaskBar from '../../components/TaskBar/task-bar';
import JobsTable from '../../components/JobsTable/trend-jobs';
import SearchBar from '../../components/SearchBar/search-bar';
import SkillsTable from '../../components/SkillsTable/trend-skills';
import PopUp from '../../components/PopUp/pop-up';

function Home() {
  const [selectedIndustry, setSelectedIndustry] = useState('');
  const [popularRoles, setPopularRoles] = useState([]);
  const [popularSkills, setPopularSkills] = useState([]);
  const [industries, setIndustries] = useState([]);
  const [industryData, setIndustryData] = useState(null);
  const [industryMetrics, setIndustryMetrics] = useState(null);
  const [topCompanies, setTopCompanies] = useState([]);
  const [loadingRoles, setLoadingRoles] = useState(false);
  const [loadingSkills, setLoadingSkills] = useState(false);
  const [loadingIndustry, setLoadingIndustry] = useState(false);
  const [loadingMetrics, setLoadingMetrics] = useState(false);
  const [loadingCompanies, setLoadingCompanies] = useState(false);
  const [error, setError] = useState('');

  // Base API URL
  const API_BASE_URL = 'http://127.0.0.1:8000';

  // Debug log to trace state changes
  useEffect(() => {
    console.log("Selected Industry:", selectedIndustry);
    console.log("Popular Roles:", popularRoles);
    console.log("Popular Skills:", popularSkills);
    console.log("Loading Roles:", loadingRoles);
    console.log("Loading Skills:", loadingSkills);
  }, [selectedIndustry, popularRoles, popularSkills, loadingRoles, loadingSkills]);

  useEffect(() => { 
    fetchIndustries();
  }, []);

  useEffect(() => {
    // Reset states when industry changes to avoid showing old data
    if (selectedIndustry) {
      // Reset data states first
      setPopularRoles([]);
      setPopularSkills([]);
      setIndustryData(null);
      setIndustryMetrics(null);
      setTopCompanies([]);
      
      // Set loading states to true
      setLoadingRoles(true);
      setLoadingSkills(true);
      setLoadingIndustry(true);
      setLoadingMetrics(true);
      setLoadingCompanies(true);
      
      // Then fetch new data
      fetchDetailedPopularRoles(selectedIndustry);
      fetchDetailedPopularSkills(selectedIndustry);
      fetchIndustryDetails(selectedIndustry);
      fetchIndustryMetrics(selectedIndustry);
      fetchTopCompanies(selectedIndustry);
    } else {
      // Clear all data if no industry is selected
      setPopularRoles([]);
      setPopularSkills([]);
      setIndustryData(null);
      setIndustryMetrics(null);
      setTopCompanies([]);
      
      // Reset loading states
      setLoadingRoles(false);
      setLoadingSkills(false);
      setLoadingIndustry(false);
      setLoadingMetrics(false);
      setLoadingCompanies(false);
    }
  }, [selectedIndustry]);

  const fetchIndustries = () => {
    fetch(`${API_BASE_URL}/industries`)
      .then(response => response.json())
      .then(data => {
        console.log("Fetched industries:", data);
        setIndustries(data);
      })
      .catch(error => {
        console.error("Error fetching industries:", error);
        setError("Failed to load industries. Please try again later.");
      });
  };

  const fetchIndustryDetails = (industry) => {
    console.log(`Fetching industry details for ${industry}...`);
    fetch(`${API_BASE_URL}/industries/${encodeURIComponent(industry)}`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Industry details not found (Status: ${response.status})`);
        }
        return response.json();
      })
      .then(data => {
        console.log("Fetched industry details:", data);
        setIndustryData(data);
        setLoadingIndustry(false);
      })
      .catch(error => {
        console.error("Error fetching industry details:", error);
        setIndustryData(null);
        setLoadingIndustry(false);
        setError("Failed to load industry details. Please try again later.");
      });
  };

  const fetchIndustryMetrics = (industry) => {
    console.log(`Fetching industry metrics for ${industry}...`);
    fetch(`${API_BASE_URL}/industry-metrics?industry=${encodeURIComponent(industry)}`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Industry metrics not found (Status: ${response.status})`);
        }
        return response.json();
      })
      .then(data => {
        console.log("Fetched industry metrics:", data);
        setIndustryMetrics(data);
        setLoadingMetrics(false);
      })
      .catch(error => {
        console.error("Error fetching industry metrics:", error);
        setIndustryMetrics(null);
        setLoadingMetrics(false);
      });
  };

  const fetchTopCompanies = (industry) => {
    console.log(`Fetching top companies for ${industry}...`);
    fetch(`${API_BASE_URL}/top-companies?industry=${encodeURIComponent(industry)}`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Top companies not found (Status: ${response.status})`);
        }
        return response.json();
      })
      .then(data => {
        console.log("Fetched top companies:", data);
        setTopCompanies(data);
        setLoadingCompanies(false);
      })
      .catch(error => {
        console.error("Error fetching top companies:", error);
        setTopCompanies([]);
        setLoadingCompanies(false);
      });
  };

  const fetchDetailedPopularRoles = (industry) => {
    console.log(`Fetching detailed popular roles for ${industry}...`);
    // Call the enhanced API endpoint for detailed roles
    fetch(`${API_BASE_URL}/detailed-popular-roles?industry=${encodeURIComponent(industry)}`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Detailed roles not found (Status: ${response.status})`);
        }
        return response.json();
      })
      .then(data => {
        console.log("Fetched detailed popular roles:", data);
        setPopularRoles(data || []); // Ensure we set an empty array if data is null/undefined
        setLoadingRoles(false);
      })
      .catch(error => {
        console.error("Error fetching detailed popular roles:", error);
        // Fallback to the basic endpoint if enhanced endpoint fails
        fetchPopularRoles(industry);
      });
  };

  const fetchDetailedPopularSkills = (industry) => {
    console.log(`Fetching detailed popular skills for ${industry}...`);
    // Call the enhanced API endpoint for detailed skills
    fetch(`${API_BASE_URL}/detailed-popular-skills?industry=${encodeURIComponent(industry)}`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Detailed skills not found (Status: ${response.status})`);
        }
        return response.json();
      })
      .then(data => {
        console.log("Fetched detailed popular skills:", data);
        setPopularSkills(data || []); // Ensure we set an empty array if data is null/undefined
        setLoadingSkills(false);
      })
      .catch(error => {
        console.error("Error fetching detailed popular skills:", error);
        // Fallback to the basic endpoint if enhanced endpoint fails
        fetchPopularSkills(industry);
      });
  };

  // Fallback functions
  const fetchPopularRoles = (industry) => {
    console.log(`Falling back to basic popular roles for ${industry}...`);
    fetch(`${API_BASE_URL}/popular-roles?industry=${encodeURIComponent(industry)}`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Popular roles not found (Status: ${response.status})`);
        }
        return response.json();
      })
      .then(data => {
        console.log("Fetched fallback popular roles:", data);
        // Convert string array to object array for compatibility
        const formattedData = data.map(role => ({
          title: role,
          roles: 'N/A',
          companies: 'Various companies'
        }));
        setPopularRoles(formattedData || []);
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
    console.log(`Falling back to basic popular skills for ${industry}...`);
    fetch(`${API_BASE_URL}/popular-skills?industry=${encodeURIComponent(industry)}`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Popular skills not found (Status: ${response.status})`);
        }
        return response.json();
      })
      .then(data => {
        console.log("Fetched fallback popular skills:", data);
        // Convert string array to object array for compatibility
        const formattedData = data.map(skill => ({
          skill: skill,
          jobs: 'Various positions',
          number: 'N/A'
        }));
        setPopularSkills(formattedData || []);
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
    console.log(`Industry selected: ${industryName}`);
    setSelectedIndustry(industryName);
    setError('');
  };

  return (
    <div className="App">
      <section className="industry-selection-section">
        <h2>Select an Industry</h2>
        <p className="description-text">Explore detailed information about roles and skills in your industry</p>
        <SearchBar 
          onSearch={handleIndustrySelect} 
          placeholder="Select an industry" 
          options={industries.map(industry => industry.name)} 
        />

        {error && <div className="error-message">{error}</div>}
      </section>

      {selectedIndustry && (
        <>
          <section className="industry-overview-section">
            <div className="industry-header">
              <h2>Industry Overview: <span className="industry-name">{selectedIndustry}</span></h2>
            </div>
            
            {loadingMetrics ? (
              <div className="loading-spinner">Loading industry metrics...</div>
            ) : (
              <>
                <div className="industry-metrics">
                  <div className="metric-card">
                    <h3>Job Postings</h3>
                    <p className="metric-value">{industryMetrics?.job_count?.toLocaleString() || 'N/A'}</p>
                  </div>
                  <div className="metric-card">
                    <h3>Companies Hiring</h3>
                    <p className="metric-value">{industryMetrics?.company_count?.toLocaleString() || 'N/A'}</p>
                  </div>
                  <div className="metric-card">
                    <h3>In-Demand Skills</h3>
                    <p className="metric-value">{industryMetrics?.skill_count?.toLocaleString() || 'N/A'}</p>
                  </div>
                  <div className="metric-card">
                    <h3>Average Salary</h3>
                    <p className="metric-value">{industryMetrics?.average_salary || 'N/A'}</p>
                  </div>
                </div>

                {industryMetrics?.top_locations?.length > 0 && (
                  <div className="top-locations">
                    <h3>Top Hiring Locations</h3>
                    <div className="location-tags">
                      {industryMetrics.top_locations.map((location, idx) => (
                        <span key={idx} className="location-tag">{location}</span>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </section>

          <div className="data-sections-container">
            <section className="data-section roles-section">
              <h2>Trending Roles in {selectedIndustry}</h2>
              <p className="description-text">Click each role for detailed information</p>
              <JobsTable roles={popularRoles} loading={loadingRoles} />
            </section>

            <section className="data-section skills-section">
              <h2>In-Demand Skills in {selectedIndustry}</h2>
              <p className="description-text">Click each skill for detailed information</p>
              <SkillsTable 
                industry={selectedIndustry} 
                loading={loadingSkills} 
                popularSkills={popularSkills}
              />
            </section>
          </div>

          {topCompanies.length > 0 && (
            <section className="companies-section">
              <h2>Top Hiring Companies in {selectedIndustry}</h2>
              <div className="companies-list">
                {loadingCompanies ? (
                  <div className="loading-spinner">Loading top companies...</div>
                ) : (
                  <div className="company-cards">
                    {topCompanies.map((company, idx) => (
                      <div key={idx} className="company-card">
                        <h3>{company.name}</h3>
                        <p><strong>Job Postings:</strong> {company.job_postings}</p>
                        {company.roles && company.roles.length > 0 && (
                          <p><strong>Hiring for:</strong> {company.roles.slice(0, 3).join(', ')}{company.roles.length > 3 ? '...' : ''}</p>
                        )}
                        {company.size && <p><strong>Size:</strong> {company.size}</p>}
                        {company.type && <p><strong>Type:</strong> {company.type}</p>}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </section>
          )}
        </>
      )}

      {!selectedIndustry && (
        <div className="welcome-section">
          <h2>Welcome to the Industry Insights Dashboard</h2>
          <p>Select an industry above to explore job market insights, trending roles, and in-demand skills.</p>
          <div className="industry-list">
            {industries.slice(0, 6).map((industry, index) => (
              <button 
                key={index} 
                className="industry-button" 
                onClick={() => handleIndustrySelect(industry.name)}
              >
                {industry.name}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default Home;