import React, { useState } from 'react';
import './pop-up.css';

const PopUp = ({ isOpen, close, jobData }) => {
    if (!isOpen) return null; 
  
    return (
        <div className="popup-overlay">
        <div className="popup-content">
          <h2>{jobData.title}</h2> {}
          <p><strong>Number of Open Roles:</strong> {jobData.roles}</p>
          <p><strong>Companies Hiring:</strong> {jobData.companies}</p>
          <button onClick={close}>Close</button>
        </div>
      </div>
    );
  };

  export default PopUp