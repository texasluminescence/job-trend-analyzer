import React, { useState } from 'react';
import './pop-up.css';

const PopUp = ({ isOpen, close, jobData }) => {
  const [showAllSkills, setShowAllSkills] = useState(false);
  
  const toggleSkillsDisplay = () => {
    setShowAllSkills(!showAllSkills);
  };
  
  if (!isOpen) return null;
  
  // Check if data is still loading
  if (jobData.isLoading) {
    return (
      <div className="popup-overlay">
        <div className="popup-content">
          <h2>Loading...</h2>
          <div className="loading-spinner"></div>
          <button onClick={close}>Close</button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="popup-overlay">
      <div className="popup-content">
        <h2 className="popup-title">{jobData.title}</h2>
        
        {jobData.description && (
          <div className="popup-section">
            <p className="popup-description">{jobData.description}</p>
          </div>
        )}
        
        <div className="popup-details">
          {jobData.roles && (
            <p><strong>Number of Open Roles:</strong> {jobData.roles}</p>
          )}
          
          {jobData.companies && (
            <p><strong>Companies Hiring:</strong> {jobData.companies}</p>
          )}
        </div>
        
        {jobData.industries && jobData.industries.length > 0 && (
          <div className="popup-section">
            <h3>Related Industries</h3>
            <div className="popup-tags">
              {jobData.industries.map((industry, index) => (
                <span key={index} className="popup-tag">{industry}</span>
              ))}
            </div>
          </div>
        )}
        
        {jobData.requiredSkills && jobData.requiredSkills.length > 0 && (
          <div className="popup-section">
            <h3>Required Skills</h3>
            <div className="popup-tags">
              {(showAllSkills ? jobData.requiredSkills : jobData.requiredSkills.slice(0, 10)).map((skill, index) => (
                <span key={index} className="popup-tag">{skill}</span>
              ))}
            </div>
            {jobData.requiredSkills.length > 10 && (
              <p 
                className="more-skills" 
                onClick={toggleSkillsDisplay}
              >
                {showAllSkills 
                  ? "Show fewer skills" 
                  : `+${jobData.requiredSkills.length - 10} more skills`}
              </p>
            )}
          </div>
        )}
        
        {jobData.resources && jobData.resources.length > 0 && (
          <div className="popup-section">
            <h3>Learning Resources</h3>
            <ul className="popup-list">
              {jobData.resources.map((resource, index) => (
                <li key={index}>{resource}</li>
              ))}
            </ul>
          </div>
        )}
        
        <button onClick={close}>Close</button>
      </div>
    </div>
  );
};

export default PopUp;