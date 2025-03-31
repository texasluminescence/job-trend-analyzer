
import React, { useState, useEffect } from 'react';
import './search-bar.css';

const SearchBar = ({ onSearch, placeholder }) => {
  const [industries, setIndustries] = useState([]);
  const [selectedIndustry, setSelectedIndustry] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch('http://127.0.0.1:8000/industries')
      .then(response => response.json())
      .then(data => {
        setIndustries(data);
        setLoading(false);
      })
      .catch(error => {
        console.error("Error fetching industries:", error);
        setError("Failed to load industries. Please try again later.");
        setLoading(false);
      });
  }, []);

  const handleSelectChange = (e) => {
    setSelectedIndustry(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (selectedIndustry) {
      onSearch(selectedIndustry);
    }
  };

  return (
    <div className="search-bar">
      {loading ? (
        <div className="loading">Loading industries...</div>
      ) : error ? (
        <div className="error">{error}</div>
      ) : (
        <form onSubmit={handleSubmit}>
          <select 
            value={selectedIndustry} 
            onChange={handleSelectChange}
            className="industry-dropdown"
          >
            <option value="">Select an industry</option>
            console.log(industries)
            {industries.map((industry, index) => (
              <option key={index} value={industry.name}>
                {industry.name}
              </option>
            ))}
          </select>
          <button type="submit">View Industry</button>
        </form>
      )}
    </div>
  );
};

export default SearchBar;