import React, { useState, useEffect } from "react";
import { Link } from 'react-router-dom';
import BarChart from "./personalized-bar-graph";
import "./personalized.css";

const Personalized = () => {
  // Always declare hooks at the top, regardless of login status
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  const [jobPostings, setJobPostings] = useState([]);
  const [suggestedSkills, setSuggestedSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [skillsLoading, setSkillsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [skillsError, setSkillsError] = useState(null);

  // Check login status
  const isLoggedIn = !!localStorage.getItem('userEmail');
  const userEmail = localStorage.getItem('userEmail');

  useEffect(() => {
    // Only fetch data if logged in
    if (isLoggedIn) {
      // Fetch personalized skill recommendations
      const fetchSuggestedSkills = async () => {
        try {
          setSkillsLoading(true);
          const url = `http://localhost:8000/suggested-skills?email=${encodeURIComponent(userEmail)}&limit=10`;
          
          const response = await fetch(url, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            }
          });
          
          if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API request failed with status ${response.status}: ${errorText}`);
          }
          
          const data = await response.json();
          setSuggestedSkills(data);
          setSkillsError(null);
        } catch (err) {
          console.error("Error fetching skill suggestions:", err);
          setSkillsError(err.message);
          setSuggestedSkills([]);
        } finally {
          setSkillsLoading(false);
        }
      };

      // Fetch job postings that match the user's skills
      const fetchJobPostings = async () => {
        try {
          setLoading(true);
          
          // Get user data first to extract skills
          const userResponse = await fetch(`http://localhost:8000/user?email=${encodeURIComponent(userEmail)}`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            }
          });
          
          if (!userResponse.ok) {
            throw new Error(`Failed to fetch user data: ${userResponse.status}`);
          }
          
          const userData = await userResponse.json();
          
          // Extract user skills from their profile
          const userSkills = [];
          const skillsDict = userData.skills || {};
          
          // Handle different skill storage formats
          Object.values(skillsDict).forEach(skillItem => {
            if (Array.isArray(skillItem)) {
              userSkills.push(...skillItem);
            } else if (typeof skillItem === 'object') {
              Object.keys(skillItem).forEach(skill => {
                if (skill !== "None" && skill) {
                  userSkills.push(skill);
                }
              });
            }
          });
          
          // Check if user has skills defined
          if (userSkills.length === 0) {
            // No skills found, fetch popular jobs/roles instead
            await fetchPopularJobsWithCompanies();
            return;
          }
          
          // Build the query string for the skills
          const skillsQuery = userSkills
            .filter(skill => skill) // Remove empty skills
            .map(skill => `skills=${encodeURIComponent(skill)}`)
            .join('&');
          
          const url = `http://localhost:8000/job-postings-by-skills?${skillsQuery}&limit=10`;
          
          const response = await fetch(url, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            }
          });
          
          if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API request failed with status ${response.status}: ${errorText}`);
          }
          
          const data = await response.json();
          
          // Format the data for display
          const formattedData = data.map((posting, index) => ({
            letter: (index + 1).toString(),
            ...posting
          }));
          
          setJobPostings(formattedData);
          setError(null);
        } catch (err) {
          console.error("Error fetching job postings:", err);
          
          // If error occurs, try to fetch popular jobs instead
          try {
            await fetchPopularJobsWithCompanies();
          } catch (fallbackErr) {
            console.error("Error fetching popular jobs:", fallbackErr);
            setError("Failed to load job recommendations. Please try again later.");
            setJobPostings([]);
          }
        } finally {
          setLoading(false);
        }
      };

      // Fetch popular jobs with actual company listings when user has no skills
      const fetchPopularJobsWithCompanies = async () => {
        try {
          // Get user industry preferences
          const userResponse = await fetch(`http://localhost:8000/user?email=${encodeURIComponent(userEmail)}`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            }
          });
          
          const userData = await userResponse.json();
          const userIndustries = userData.industries || [];
          
          let jobsData = [];
          
          // If user has industry preferences, fetch popular jobs for those industries
          if (userIndustries.length > 0) {
            // Just use the first industry for simplicity
            const industryName = userIndustries[0];
            
            // First fetch detailed popular roles to get role names
            const popularRolesUrl = `http://localhost:8000/detailed-popular-roles?industry=${encodeURIComponent(industryName)}`;
            const rolesResponse = await fetch(popularRolesUrl, {
              method: 'GET',
              headers: {
                'Content-Type': 'application/json',
              }
            });
            
            if (rolesResponse.ok) {
              const rolesData = await rolesResponse.json();
              
              // For each role, fetch one actual job posting
              for (const role of rolesData) {
                try {
                  // Fetch a single job posting for this role
                  const jobPostingUrl = `http://localhost:8000/job-postings?role=${encodeURIComponent(role.role_name)}&industry=${encodeURIComponent(industryName)}&limit=1`;
                  const jobResponse = await fetch(jobPostingUrl);
                  
                  if (jobResponse.ok) {
                    const jobsForRole = await jobResponse.json();
                    
                    if (jobsForRole && jobsForRole.length > 0) {
                      // Add this job posting to our list
                      const job = jobsForRole[0];
                      jobsData.push({
                        letter: (jobsData.length + 1).toString(),
                        title: job.title || role.role_name,
                        company: job.company || "Example Company",
                        location: job.location || "Remote",
                        description: job.description || role.description || `Popular ${role.role_name} role in the ${industryName} industry.`,
                        industry: industryName,
                        skills: job.skills || role.required_skills || [],
                        match_score: 100,
                        posting_url: job.posting_url || null,
                        recommended: true
                      });
                    } else {
                      // No actual job found, create a sample with role info but a real company
                      jobsData.push({
                        letter: (jobsData.length + 1).toString(),
                        title: role.role_name,
                        company: role.top_hiring_companies?.[0] || "Tech Leaders Inc.",
                        location: "Multiple Locations",
                        description: role.description || `Popular ${role.role_name} role in the ${industryName} industry.`,
                        industry: industryName,
                        skills: role.required_skills || [],
                        match_score: 100,
                        recommended: true
                      });
                    }
                    
                    // Limit to 5 roles
                    if (jobsData.length >= 5) break;
                  }
                } catch (roleErr) {
                  console.error(`Error fetching job for role ${role.role_name}:`, roleErr);
                  // Continue with next role
                }
              }
            }
          }
          
          // If we couldn't get industry-specific jobs or user has no industry preferences
          if (jobsData.length === 0) {
            throw new Error("No industry-specific jobs found.");
          }
          
          setJobPostings(jobsData);
          setError(null);
        } catch (fallbackErr) {
          console.error("Error fetching popular jobs:", fallbackErr);
          throw fallbackErr; // Let the parent function handle this error
        }
      };

      fetchSuggestedSkills();
      fetchJobPostings();
    }
  }, [isLoggedIn, userEmail]);

  const openModal = (job) => {
    setSelectedJob(job);
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
  };

  // If not logged in, show login prompt
  if (!isLoggedIn) {
    return (
      <div className="personalized-login-prompt">
        <h2>Personalized Insights</h2>
        <p>Please <Link to="/login">login</Link> to view your personalized job insights.</p>
        <p>Don't have an account? <Link to="/signup">Sign up</Link> now!</p>
      </div>
    );
  }

  return (
    <div className="container">
      <h1 className="title">Your Personalized Job Trends</h1>
      <p className="para">Skill and role recommendations for you</p>
      
      <h1 className="title2">Based on Your Skills ...</h1>
      <p className="para2">Popular skills you may want to learn</p>
      <div className="list-bar">
        <ul className="list">
          {skillsLoading ? (
            <li className="list-item">Loading skill suggestions...</li>
          ) : skillsError ? (
            <li className="list-item">Error loading skills: {skillsError}</li>
          ) : suggestedSkills.length === 0 ? (
            <li className="list-item">No skill suggestions found. Try updating your profile.</li>
          ) : (
            suggestedSkills.map((skill, index) => (
              <li className="list-item" key={index}>
                <div className="circle">{skill.letter}</div>
                <span className="text">{skill.name ? skill.name.charAt(0).toUpperCase() + skill.name.slice(1) : ''}</span>
              </li>
            ))
          )}
        </ul>
        <div>
          <BarChart />
        </div>
      </div>
      
      <h1 className="title3">Jobs For You</h1>
      
      {loading ? (
        <p>Loading job recommendations...</p>
      ) : error ? (
        <p>Error loading job recommendations: {error}</p>
      ) : jobPostings.length === 0 ? (
        <p>No job recommendations found. Try updating your profile with more skills.</p>
      ) : (
        <>
          {jobPostings.some(job => job.recommended) && (
            <div className="recommendation-note">
              <p>Showing popular job roles based on industry trends.</p>
              <p>To receive more personalized job recommendations and match percentages, 
                <Link to="/account" className="update-profile-link"> update your profile with your skills</Link>.
              </p>
            </div>
          )}
          <ul className="list1">
            {jobPostings.map((job, index) => (
              <li
                className="list1-item"
                key={index}
                onClick={() => openModal(job)}
              >
                <div className="circle1">{job.letter}</div>
                <span className="text1">{job.company} - {(job.title || job.role) ? (job.title || job.role).charAt(0).toUpperCase() + (job.title || job.role).slice(1) : ''}</span>
              </li>
            ))}
          </ul>
        </>
      )}
      
      {modalOpen && selectedJob && (
        <div className="modal-overlay">
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>{(selectedJob.title || selectedJob.role) ? (selectedJob.title || selectedJob.role).charAt(0).toUpperCase() + (selectedJob.title || selectedJob.role).slice(1) : ''}</h2>

            <div className="company-details">
              <p>
                <strong>Company: </strong> {selectedJob.company}
              </p>
              <p>
                <strong>Location: </strong> {selectedJob.location || "Remote"}
              </p>
              
              <div className="job-description">
                <strong>Description: </strong>
                <p>{selectedJob.description || "No description available"}</p>
              </div>
              
              {selectedJob.skills && selectedJob.skills.length > 0 && (
                <p>
                  <strong>Key Skills: </strong>
                  {selectedJob.skills.slice(0, 3).map(skill => 
                    skill ? skill.charAt(0).toUpperCase() + skill.slice(1) : ''
                  ).join(", ")}
                  {selectedJob.skills.length > 3 && " and more"}
                </p>
              )}

              {selectedJob.match_score && !selectedJob.recommended && (
                <p>
                  <strong>Match: </strong> {Math.round(selectedJob.match_score)}%
                </p>
              )}
              
              {selectedJob.recommended && (
                <p className="match-prompt">
                  <strong>Match: </strong> <em>Add skills to your profile to see match percentage</em>
                </p>
              )}
              
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
