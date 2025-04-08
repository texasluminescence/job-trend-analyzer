import React, { useState, useEffect } from "react";
import BarChart from "./personalized-bar-graph";
import "./personalized.css";

const Personalized = () => {
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  const [jobPostings, setJobPostings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // User's skills - in a real app, you would get these from the user's profile
  const userSkills = ["Python", "JavaScript", "Machine Learning", "Data Analytics", "Git"];

  useEffect(() => {
    // Fetch job postings that match the user's skills
    const fetchJobPostings = async () => {
      try {
        setLoading(true);
        
        // Build the query string for the skills
        const skillsQuery = userSkills.map(skill => `skills=${encodeURIComponent(skill)}`).join('&');
        const url = `/api/job-postings-by-skills?${skillsQuery}&limit=10`;
        
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            // Add any other necessary headers like authorization if required
          }
        });
        
        // Check if the response is ok
        if (!response.ok) {
          // Try to get the error text for more detailed logging
          const errorText = await response.text();
          throw new Error(`API request failed with status ${response.status}: ${errorText}`);
        }
        
        // Try to parse the response as JSON
        const data = await response.json();
        
        // Format the data for display
        const formattedData = data.map((posting, index) => ({
          letter: (index + 1).toString(),
          ...posting // Preserve all original fields
        }));
        
        setJobPostings(formattedData);
        setError(null);
      } catch (err) {
        console.error("Detailed error fetching job postings:", err);
        setError(err.message);
        
        // Use sample data if the API call fails - with correct field names matching the backend
        setJobPostings([
          {
            letter: "1",
            title: "Software Engineer",
            company: "Example Corp", 
            location: "Austin, TX",
            description: "Example job description",
            match_score: 85.5,
            skills: ["Python", "JavaScript"],
            posting_url: "https://example.com/job"
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchJobPostings();
  }, []);

  const openModal = (job) => {
    setSelectedJob(job);
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
  };

  // Skills recommendations - in a real app, these would come from another API endpoint
  const recommendedSkills = [
    { letter: "1", name: "Python" },
    { letter: "2", name: "Java" },
    { letter: "3", name: "Machine Learning" },
    { letter: "4", name: "Data Analytics" },
    { letter: "5", name: "C++" },
    { letter: "6", name: "JavaScript" },
    { letter: "7", name: "Git" },
    { letter: "8", name: "Research" },
    { letter: "9", name: "UI design" },
    { letter: "10", name: "HTML/CSS" },
  ];

  // Format date function
  const formatDate = (dateString) => {
    if (!dateString) return "N/A";
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString();
    } catch (e) {
      return dateString;
    }
  };

  return (
    <div className="container">
      <h1 className="title">Your Personalized Job Trends</h1>
      <p className="para">Skill and role recommendations for you</p>
      
      <h1 className="title2">Based on Your Skills ...</h1>
      <p className="para2">Popular skills you may want to learn</p>
      <div className="list-bar">
        <ul className="list">
          {recommendedSkills.map((skill, index) => (
            <li className="list-item" key={index}>
              <div className="circle">{skill.letter}</div>
              <span className="text">{skill.name}</span>
            </li>
          ))}
        </ul>
        <div>
          <BarChart />
        </div>
      </div>
      
      <h1 className="title3">Jobs For You</h1>
      
      {loading ? (
        <p>Loading job recommendations...</p>
      ) : error ? (
        <div>
          <p>Error loading jobs: {error}</p>
          <p>Showing sample job data</p>
        </div>
      ) : (
        <ul className="list1">
          {jobPostings.map((job, index) => (
            <li
              className="list1-item"
              key={index}
              onClick={() => openModal(job)}
            >
              <div className="circle1">{job.letter}</div>
              <span className="text1">{job.company} - {job.title || job.role}</span>
            </li>
          ))}
        </ul>
      )}
      
      {modalOpen && selectedJob && (
        <div className="modal-overlay">
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>{selectedJob.company}</h2>

            <div className="company-details">
              <p>
                <strong>Job: </strong> {selectedJob.title || selectedJob.role}
              </p>
              <p>
                <strong>Location: </strong> {selectedJob.location || "Remote"}
              </p>
              <p>
                <strong>Industry: </strong> {selectedJob.industry || "Not specified"}
              </p>
              <p>
                <strong>Posted Date: </strong> {formatDate(selectedJob.posted_date)}
              </p>
              {selectedJob.salary_range && (
                <p>
                  <strong>Salary Range: </strong> {selectedJob.salary_range}
                </p>
              )}
              <p>
                <strong>Match Score: </strong> {Math.round(selectedJob.match_score || 0)}%
              </p>
              {selectedJob.matching_skills_count !== undefined && (
                <p>
                  <strong>Matching Skills: </strong> {selectedJob.matching_skills_count} out of {selectedJob.total_skills_count || 0}
                </p>
              )}
              {selectedJob.skills && selectedJob.skills.length > 0 && (
                <p>
                  <strong>Required Skills: </strong>
                  {selectedJob.skills.join(", ")}
                </p>
              )}
              <p>
                <strong>Description: </strong>
                <br /> {selectedJob.description || "No description available"}
              </p>
              {selectedJob.posting_url && (
                <p>
                  <a href={selectedJob.posting_url} target="_blank" rel="noopener noreferrer">
                    Apply Now
                  </a>
                </p>
              )}
            </div>
            <button onClick={closeModal}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Personalized;
