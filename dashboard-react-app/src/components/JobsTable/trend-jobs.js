import React, { useState } from 'react';
import '../TaskBar/task-bar.css';
import SearchBar from '../SearchBar/search-bar';
import BlackCircle from '../../assets/BlackCircle.png';
import PopUp from '../PopUp/pop-up';


const JobsTable = () => {

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

    const jobs = [
      { title: "Data Engineer", roles: 10000, companies: "Meta, Google" },
      { title: "Product Manager", roles: 5000, companies: "Oracle" },
      { title: "Data Engineer", roles: 10000, companies: "Meta, Google" },
      { title: "Product Manager", roles: 5000, companies: "Oracle" },
      { title: "Data Engineer", roles: 10000, companies: "Meta, Google" },
      { title: "Product Manager", roles: 5000, companies: "Oracle" }
    ];

    return(
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
          {jobs.map((job, index) => (
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