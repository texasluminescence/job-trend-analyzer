import React, { useState, useEffect } from 'react';
import '../shared/table-styles.css'; // Using shared CSS
import PopUp from '../PopUp/pop-up';

const JobsTable = ({ roles = [], loading = false }) => {
  const [isPopUpOpen, setIsPopUpOpen] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  const [jobDetails, setJobDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  // Debug log to see what's happening
  useEffect(() => {
    console.log("JobsTable updated. Roles:", roles, "Loading:", loading);
  }, [roles, loading]);

  // Open the modal and fetch detailed job data
  const openPopUp = async (jobData) => {
    setSelectedJob(jobData);
    setIsPopUpOpen(true);
    
    // If we have a role name, fetch more details
    if (jobData.role_name || jobData.title) {
      setLoadingDetails(true);
      try {
        const roleName = jobData.role_name || jobData.title;
        const response = await fetch(`http://127.0.0.1:8000/roles/${encodeURIComponent(roleName)}`);
        
        if (response.ok) {
          const details = await response.json();
          setJobDetails(details);
        } else {
          // If detailed API fails, we'll just use what we have
          setJobDetails(null);
        }
      } catch (error) {
        console.error("Error fetching role details:", error);
        setJobDetails(null);
      } finally {
        setLoadingDetails(false);
      }
    }
  };

  // Close the modal
  const closePopUp = () => {
    setIsPopUpOpen(false);
    setSelectedJob(null);
    setJobDetails(null);
  };

  if (loading) {
    return <div className="loading-spinner">Loading popular roles...</div>;
  }

  // Only show the no selection message if roles is an empty array AND we're not loading
  if (!loading && Array.isArray(roles) && roles.length === 0) {
    return (
      <div className="no-selection-message">
        No roles found for this industry. Please try another industry.
      </div>
    );
  }

  return (
    <div className="jobs-table-container">
      <table className="jobs-table">
        <thead>
          <tr>
            <th>Role Title</th>
            <th>Number of Open Roles</th>
            <th>Companies Hiring</th>
          </tr>
        </thead>
        <tbody>
          {Array.isArray(roles) && roles.map((job, index) => {
            // Handle both simple string array and object array from API
            const title = typeof job === 'string' ? job : (job.role_name || job.title);
            const openRoles = typeof job === 'string' ? 'N/A' : (job.roles || job.open_positions_count || 'N/A');
            const companies = typeof job === 'string' ? 'Various companies' : (job.companies || 'Various companies');
            
            return (
              <tr key={index} onClick={() => openPopUp(job)} className="job-row">
                <td>{title}</td>
                <td>{openRoles}</td>
                <td>{companies}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      
      {isPopUpOpen && selectedJob && (
        <PopUp 
          isOpen={isPopUpOpen} 
          close={closePopUp} 
          jobData={{
            title: jobDetails?.role_name || selectedJob.role_name || selectedJob.title || (typeof selectedJob === 'string' ? selectedJob : ''),
            description: jobDetails?.description || selectedJob.description || 
              `${jobDetails?.role_name || selectedJob.role_name || selectedJob.title || ''} is a popular role with many opportunities.`,
            requiredSkills: jobDetails?.required_skills || [],
            industries: jobDetails?.industries || [],
            isLoading: loadingDetails
          }} 
        />
      )}
    </div>
  );
};

export default JobsTable;