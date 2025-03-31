import React, { useState } from 'react';
import '../TaskBar/task-bar.css';
import PopUp from '../PopUp/pop-up';
import './trend-jobs.css';

const JobsTable = ({ roles = [], loading = false }) => {
  const [isPopUpOpen, setIsPopUpOpen] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);

  // Open the modal and set the job data
  const openPopUp = (jobData) => {
    setSelectedJob(jobData);
    setIsPopUpOpen(true);
  };

  // Close the modal
  const closePopUp = () => {
    setIsPopUpOpen(false);
    setSelectedJob({});
  };

  if (loading) {
    return <div className="loading-spinner">Loading popular roles...</div>;
  }

  if (roles.length === 0 && !loading) {
    return (
      <div className="no-selection-message">
        Please select an industry to view trending roles.
      </div>
    );
  }

  return (
    <div>
      <table>
        <thead>
          <tr>
            <th>Role Title</th>
            <th>Number of Open Roles</th>
            <th>Companies Hiring</th>
          </tr>
        </thead>
        <tbody>
          {roles.map((job, index) => (
            <tr key={index} onClick={() => openPopUp(job)}>
              <td>{job.title}</td>
              <td>{job.roles}</td>
              <td>{job.companies}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <PopUp isOpen={isPopUpOpen} close={closePopUp} jobData={selectedJob} />
    </div>
  );
};

export default JobsTable;