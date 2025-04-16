import React, { useState, useEffect } from "react";
import { Link } from 'react-router-dom';
import BarChart from "./personalized-bar-graph";
import "./personalized.css";
import arima from '../../assets/2 Year Salary Progression Forecast.png';

const Personalized = () => {
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  const [jobPostings, setJobPostings] = useState([]);
  const [suggestedSkills, setSuggestedSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [skillsLoading, setSkillsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [skillsError, setSkillsError] = useState(null);
  const [userSkills, setUserSkills] = useState([]);
  const [skillModalOpen, setSkillModalOpen] = useState(false);
  const [selectedSkill, setSelectedSkill] = useState(null);
  const [skillDetails, setSkillDetails] = useState(null);
  const [skillDetailsLoading, setSkillDetailsLoading] = useState(false);
  const [skillDetailsError, setSkillDetailsError] = useState(null);
  const isLoggedIn = !!localStorage.getItem('userEmail');
  const userEmail = localStorage.getItem('userEmail');
  const [useArima, setUseArima] = useState(false);
  const [hasIndustries, setHasIndustries] = useState(true); // New state to track if user has industries

  useEffect(() => {
    if (isLoggedIn) {
      const fetchSuggestedSkills = async () => {
        try {
          setSkillsLoading(true);
          const timestamp = new Date().getTime();
          const url = `http://localhost:8000/suggested-skills?email=${encodeURIComponent(userEmail)}&limit=10&t=${timestamp}`;
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
          const filteredSkills = data.filter(skill => {
            const skillName = skill.name.toLowerCase();
            return !userSkills.some(userSkill => userSkill.toLowerCase() === skillName);
          });
          setSuggestedSkills(filteredSkills);
          setSkillsError(null);
        } catch (err) {
          console.error("Error fetching skill suggestions:", err);
          setSkillsError(err.message);
          setSuggestedSkills([]);
        } finally {
          setSkillsLoading(false);
        }
      };

      const fetchJobPostings = async () => {
        console.log("Starting fetchJobPostings");
        try {
          setLoading(true);
          const timestamp = new Date().getTime();
          console.log("Fetching user data for email:", userEmail);
          const userResponse = await fetch(`http://localhost:8000/user?email=${encodeURIComponent(userEmail)}&t=${timestamp}`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            }
          });
          console.log("User response status:", userResponse.status);
          if (!userResponse.ok) {
            const errorText = await userResponse.text();
            throw new Error(`Failed to fetch user data: ${userResponse.status} - ${errorText}`);
          }
          const userData = await userResponse.json();
          console.log("User data:", userData);
          
          const userIndustries = userData.industries || [];
          console.log("User industries:", userIndustries);
          if (userIndustries.length === 0) {
            console.log("No industries found, setting error and exiting");
            setJobPostings([]);
            setError("Please add industries to your profile to see job recommendations.");
            setHasIndustries(false); // Set flag to indicate no industries
            setLoading(false);
            return;
          }
          
          // User has industries, set flag to true
          setHasIndustries(true);
      
          const extractedSkills = [];
          const skillsDict = userData.skills || {};
          console.log("Raw skills data:", skillsDict);
          
          if (typeof skillsDict === 'object' && skillsDict !== null && !Array.isArray(skillsDict)) {
            Object.keys(skillsDict).forEach(skill => {
              if (skill && skill.toLowerCase() !== "none") {
                extractedSkills.push(skill.trim());
                console.log("Added skill:", skill);
              }
            });
          } else {
            console.warn("Unexpected skills format. Skipping skill extraction.");
          }
          
          console.log("Extracted skills:", extractedSkills);
          setUserSkills(extractedSkills);
          
      
          if (extractedSkills.length === 0) {
            console.log("No skills extracted, falling back to fetchPopularJobsWithCompanies");
            await fetchPopularJobsWithCompanies();
            return;
          }
      
          const skillsQuery = extractedSkills
            .filter(skill => skill)
            .map(skill => `skills=${encodeURIComponent(skill)}`)
            .join('&');
          const url = `http://localhost:8000/job-postings-by-skills?${skillsQuery}&limit=10&t=${timestamp}`;
          console.log("Attempting to fetch job postings with URL:", url);
          
          const response = await fetch(url, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            }
          });
          console.log("Job postings response status:", response.status, "OK:", response.ok);
          
          if (!response.ok) {
            const errorText = await response.text();
            console.error("Job postings API error:", errorText);
            throw new Error(`API request failed with status ${response.status}: ${errorText}`);
          }
          
          const data = await response.json();
          console.log("Job postings data:", data);
          
          if (!Array.isArray(data)) {
            console.error("Invalid data format:", data);
            throw new Error("API returned invalid data format");
          }
          
          if (data.length === 0) {
            console.log("No job postings found, falling back to fetchPopularJobsWithCompanies");
            await fetchPopularJobsWithCompanies();
            return;
          }
      
          const currentDate = new Date();
          const oneYearAgo = new Date();
          oneYearAgo.setFullYear(currentDate.getFullYear() - 1);
          const filteredData = data.filter(posting => {
            if (!posting.date_posted && !posting.posted_date) {
              return true;
            }
            const postingDate = new Date(posting.date_posted || posting.posted_date);
            return !isNaN(postingDate.getTime()) && postingDate >= oneYearAgo;
          });
          console.log("Filtered postings:", filteredData);
      
          const formattedData = filteredData.map((posting, index) => ({
            letter: (index + 1).toString(),
            ...posting,
            match_score: posting.match_score !== undefined && posting.match_score !== null 
              ? Number(posting.match_score) 
              : null,
            posting_url: posting.posting_url || null,
            description: posting.description || `${posting.title || "Job"} at ${posting.company || "Company"}`,
            recommended: posting.recommended !== undefined ? posting.recommended : true
          }));
          console.log("Formatted postings:", formattedData);
      
          setJobPostings(formattedData);
          setError(formattedData.length === 0 ? "No recent job postings found. Try updating your profile." : null);
        } catch (err) {
          console.error("Error in fetchJobPostings:", err);
          try {
            console.log("Attempting fallback to fetchPopularJobsWithCompanies");
            await fetchPopularJobsWithCompanies();
          } catch (fallbackErr) {
            console.error("Fallback error:", fallbackErr);
            setError("Please add industries to your profile to see job recommendations.");
            setJobPostings([]);
          }
        } finally {
          setLoading(false);
          console.log("fetchJobPostings completed");
        }
      };

      const fetchPopularJobsWithCompanies = async () => {
        try {
          const timestamp = new Date().getTime();
          const userResponse = await fetch(`http://localhost:8000/user?email=${encodeURIComponent(userEmail)}&t=${timestamp}`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            }
          });
          if (!userResponse.ok) {
            throw new Error(`Failed to fetch user data: ${userResponse.status}`);
          }
          const userData = await userResponse.json();
          const userIndustries = userData.industries || [];
          if (userIndustries.length === 0) {
            setJobPostings([]);
            setError("Please add industries to your profile to see job recommendations.");
            setHasIndustries(false); // Set flag to indicate no industries
            return;
          }
          
          // User has industries, set flag to true
          setHasIndustries(true);
          
          let jobsData = [];
          const industryName = userIndustries[0];
          const popularRolesUrl = `http://localhost:8000/detailed-popular-roles?industry=${encodeURIComponent(industryName)}&t=${timestamp}`;
          const rolesResponse = await fetch(popularRolesUrl, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            }
          });
          if (!rolesResponse.ok) {
            setJobPostings([]);
            setError("Please add industries to your profile to see job recommendations.");
            return;
          }
          const rolesData = await rolesResponse.json();
          if (!Array.isArray(rolesData) || rolesData.length === 0) {
            setJobPostings([]);
            setError(`No job roles found for ${industryName}. Try a different industry.`);
            return;
          }
          for (const role of rolesData) {
            try {
              let job = null;
              try {
                const jobPostingUrl = `http://localhost:8000/job-postings?role=${encodeURIComponent(role.role_name)}&industry=${encodeURIComponent(industryName)}&limit=1&t=${timestamp}`;
                const jobResponse = await fetch(jobPostingUrl);
                if (jobResponse.ok) {
                  const jobsForRole = await jobResponse.json();
                  if (jobsForRole && Array.isArray(jobsForRole) && jobsForRole.length > 0) {
                    job = jobsForRole[0];
                  }
                }
              } catch (jobErr) {
                console.error("Error fetching job posting:", jobErr);
              }
              const currentDate = new Date();
              const oneYearAgo = new Date();
              oneYearAgo.setFullYear(currentDate.getFullYear() - 1);
              const isRecentJob = (job) => {
                if (!job || (!job.date_posted && !job.posted_date)) {
                  return true;
                }
                const postingDate = new Date(job.date_posted || job.posted_date);
                return !isNaN(postingDate.getTime()) && postingDate >= oneYearAgo;
              };
              if (job && isRecentJob(job)) {
                jobsData.push({
                  letter: (jobsData.length + 1).toString(),
                  title: job.title || role.role_name,
                  company: job.company || "Various Companies",
                  location: job.location || "Remote",
                  description: job.description || role.description || 
                             `This is a popular ${role.role_name} role in the ${industryName} industry.`,
                  industry: industryName,
                  skills: job.skills || role.required_skills || [],
                  recommended: false,
                  match_score: null,
                  posting_url: job.posting_url || null,
                  date_posted: job.date_posted || job.posted_date || new Date().toISOString()
                });
              } else {
                jobsData.push({
                  letter: (jobsData.length + 1).toString(),
                  title: role.role_name,
                  company: role.top_hiring_companies?.[0] || "Various Companies",
                  location: "Multiple Locations",
                  description: role.description || 
                             `This ${role.role_name} position is in high demand in the ${industryName} industry.`,
                  industry: industryName,
                  skills: role.required_skills || [],
                  recommended: false,
                  match_score: null,
                  date_posted: new Date().toISOString()
                });
              }
              if (jobsData.length >= 5) break;
            } catch (roleErr) {
              console.error("Error processing role:", roleErr);
            }
          }
          if (jobsData.length === 0) {
            setJobPostings([]);
            setError("No job recommendations found. Try updating your profile.");
            return;
          }
          setJobPostings(jobsData);
          setError(null);
        } catch (err) {
          setJobPostings([]);
          setError("Please add industries to your profile to see job recommendations.");
        }
      };

      const checkArima = async () => {
        try {
          const timestamp = new Date().getTime();
          const userResponse = await fetch(`http://localhost:8000/user?email=${encodeURIComponent(userEmail)}&t=${timestamp}`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            }
          });
          if (!userResponse.ok) {
            throw new Error(`Failed to fetch user data: ${userResponse.status}`);
          }
          const userData = await userResponse.json();
          const rolesDict = userData.interested_roles || [];
          rolesDict.forEach(role => {
            if (role && role === "Data Scientist") {
              setUseArima(true);
            }
          });
        } catch (err) {
          setError("Error loading user profile. Please try again later.");
          setLoading(false);
        }
      };

      const fetchUserProfileAndData = async () => {
        try {
          const timestamp = new Date().getTime();
          const userResponse = await fetch(`http://localhost:8000/user?email=${encodeURIComponent(userEmail)}&t=${timestamp}`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            }
          });
          if (!userResponse.ok) {
            throw new Error(`Failed to fetch user data: ${userResponse.status}`);
          }
          const userData = await userResponse.json();
          
          // Check if user has industries
          const userIndustries = userData.industries || [];
          if (userIndustries.length === 0) {
            setHasIndustries(false);
            setError("Please add industries to your profile to see job recommendations.");
            setLoading(false);
            return;
          }
          
          setHasIndustries(true);
          
          const extractedSkills = [];
          const skillsDict = userData.skills || {};
          if (typeof skillsDict === 'object') {
            if (Array.isArray(skillsDict)) {
              skillsDict.forEach(skill => {
                if (skill && skill !== "None") extractedSkills.push(skill);
              });
            } else {
              Object.entries(skillsDict).forEach(([category, skills]) => {
                if (Array.isArray(skills)) {
                  skills.forEach(skill => {
                    if (skill && skill !== "None") extractedSkills.push(skill);
                  });
                } else if (typeof skills === 'object' && skills !== null) {
                  Object.keys(skills).forEach(skill => {
                    if (skill !== "None" && skill) extractedSkills.push(skill);
                  });
                } else if (typeof skills === 'string' && skills && skills !== "None") {
                  extractedSkills.push(skills);
                }
              });
            }
          }
          setUserSkills(extractedSkills);
          await fetchSuggestedSkills();
          await fetchJobPostings();
        } catch (err) {
          setError("Error loading user profile. Please try again later.");
          setLoading(false);
        }
      };

      checkArima();
      fetchUserProfileAndData();
    }
  }, [isLoggedIn, userEmail]);

  const fetchSkillDetails = async (skillName) => {
    if (!skillName) return;
    try {
      setSkillDetailsLoading(true);
      const timestamp = new Date().getTime();
      const url = `http://localhost:8000/skill-details?name=${encodeURIComponent(skillName)}&t=${timestamp}`;
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
      setSkillDetails(data);
      setSkillDetailsError(null);
    } catch (err) {
      console.error("Error fetching skill details:", err);
      setSkillDetailsError(err.message);
      setSkillDetails(null);
    } finally {
      setSkillDetailsLoading(false);
    }
  };

  const openJobModal = (job) => {
    setSelectedJob(job);
    setModalOpen(true);
  };

  const closeJobModal = () => {
    setModalOpen(false);
  };

  const openSkillModal = (skill) => {
    setSelectedSkill(skill);
    setSkillModalOpen(true);
    fetchSkillDetails(skill.name);
  };

  const closeSkillModal = () => {
    setSkillModalOpen(false);
    setSelectedSkill(null);
    setSkillDetails(null);
  };

  const handleApply = (url) => {
    if (url) {
      window.open(url, '_blank', 'noopener,noreferrer');
    }
  };

  if (!isLoggedIn) {
    return (
      <div className="personalized-login-prompt">
        <h2>Personalized Insights</h2>
        <p>Please <Link to="/login">login</Link> to view your personalized job insights.</p>
        <p>Don't have an account? <Link to="/signup">Sign up</Link> now!</p>
      </div>
    );
  }

  // If user has no industries, show a single error message for the entire page
  if (!hasIndustries) {
    return (
      <div className="container">
        <h1 className="title">Your Personalized Job Trends</h1>
        <p className="para">Skill and role recommendations for you</p>
        
        <div className="recommendation-note" style={{ width: '80%', maxWidth: '800px', margin: '20px 0' }}>
          <p>To see personalized job trends and skill recommendations, you need to update your profile.</p>
          <p>
            <Link to="/account" className="update-profile-link">Add industries to your profile</Link> to discover jobs and skills matching your interests.
          </p>
        </div>
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
            <li className="list-item">No new skill suggestions found. You're already proficient in the key skills!</li>
          ) : (
            suggestedSkills.map((skill, index) => (
              <li 
                className="list-item" 
                key={index}
                onClick={() => openSkillModal(skill)}
                style={{ cursor: 'pointer' }}
              >
                <div className="circle">{index+1}</div>
                <span className="text">{skill.name ? skill.name.charAt(0).toUpperCase() + skill.name.slice(1) : ''}</span>
                <span className="hover-text">Click for details</span>
              </li>
            ))
          )}
        </ul>
        <div>
          <BarChart suggestedSkills={suggestedSkills} />
        </div>
      </div>

      {useArima && (
        <>
          <h1 className="ARIMA display">Data Science Salary Progression Prediction</h1>
          <p className="para">Predicted for 2025–2027 using time-series ARIMA analysis</p>
          <div className="ARIMA model">
            <img
              alt="arima"
              src={arima}
              width={850}
              height={500}
              style={{ paddingBottom: 75, display: 'block' }}
            />
          </div>
        </>
      )}
      
      <h1 className="title3">Jobs For You</h1>
      
      {loading ? (
        <p>Loading job recommendations...</p>
      ) : error ? (
        <div className="recommendation-note">
          <p>To see job recommendations, you need to update your profile.</p>
          <p>
            <Link to="/account" className="update-profile-link">Add industries to your profile</Link> to discover jobs matching your interests.
          </p>
        </div>
      ) : jobPostings.length === 0 ? (
        <div className="recommendation-note">
          <p>No job recommendations found.</p>
          <p>
            <Link to="/account" className="update-profile-link">Update your profile with more skills</Link> to see matching jobs.
          </p>
        </div>
      ) : (
        <>
          {!jobPostings.some(job => job.recommended) && (
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
                onClick={() => openJobModal(job)}
              >
                <div className="circle1">{job.letter}</div>
                <span className="text1">{job.company} - {(job.title || job.role) ? (job.title || job.role).charAt(0).toUpperCase() + (job.title || job.role).slice(1) : ''}</span>
              </li>
            ))}
          </ul>
        </>
      )}
      
      {/* Job Modal */}
      {modalOpen && selectedJob && (
        <div className="modal-overlay">
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>{(selectedJob.title || selectedJob.role) ? (selectedJob.title || selectedJob.role).charAt(0).toUpperCase() + (selectedJob.title || selectedJob.role).slice(1) : ''}</h2>
            <div className="company-details">
              <p><strong>Company: </strong> {selectedJob.company}</p>
              <p><strong>Location: </strong> {selectedJob.location || "Remote"}</p>
              <div className="job-description">
                <strong>Description: </strong>
                <p>{selectedJob.description || `${selectedJob.title || "This position"} at ${selectedJob.company || "this company"}.`}</p>
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
              {(selectedJob.recommended && selectedJob.match_score !== undefined && selectedJob.match_score !== null) ? (
                <p><strong>Match: </strong> {Math.round(selectedJob.match_score)}%</p>
              ) : (
                <p className="match-prompt">
                  <strong>Match: </strong> <em>Add more skills to your profile to see match percentage</em>
                </p>
              )}
              <div className="modal-buttons">
                {selectedJob.posting_url && (
                  <button 
                    className="apply-button" 
                    onClick={() => handleApply(selectedJob.posting_url)}
                  >
                    Apply Now
                  </button>
                )}
                <button className="close-button" onClick={closeJobModal}>Close</button>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Skill Modal - Styled to match roles modal */}
      {skillModalOpen && selectedSkill && (
        <div className="modal-overlay">
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>{selectedSkill.name ? selectedSkill.name.charAt(0).toUpperCase() + selectedSkill.name.slice(1) : 'Skill Details'}</h2>
            <div className="company-details">
              {skillDetailsLoading ? (
                <p>Loading skill details...</p>
              ) : skillDetailsError ? (
                <p>Error loading skill details: {skillDetailsError}</p>
              ) : skillDetails ? (
                <>
                  <div className="job-description">
                    <strong>Description: </strong>
                    <p>{skillDetails.description || `${selectedSkill.name} is a valuable skill in today's job market.`}</p>
                  </div>
                  {skillDetails.industries && skillDetails.industries.length > 0 && (
                    <p>
                      <strong>Industries: </strong>
                      {skillDetails.industries.slice(0, 5).join(", ")}
                      {skillDetails.industries.length > 5 && " and more"}
                    </p>
                  )}
                  {skillDetails.job_postings_count !== undefined && (
                    <p>
                      <strong>Job Postings: </strong>
                      {skillDetails.job_postings_count} recent postings mention this skill
                    </p>
                  )}
                  {skillDetails.related_roles && skillDetails.related_roles.length > 0 && (
                    <p>
                      <strong>Related Roles: </strong>
                      {skillDetails.related_roles.slice(0, 3).join(", ")}
                      {skillDetails.related_roles.length > 3 && " and more"}
                    </p>
                  )}
                  {skillDetails.learning_resources && skillDetails.learning_resources.length > 0 && (
                    <p>
                      <strong>Learning Resources: </strong>
                      {skillDetails.learning_resources.slice(0, 3).map((resource, idx) => (
                        <span key={idx}>
                          {resource.title || resource.url || `Resource ${idx + 1}`}
                          {resource.url && (
                            <a 
                              href={resource.url} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              style={{ marginLeft: '5px', fontSize: '0.9rem' }}
                            >
                              (Link)
                            </a>
                          )}
                          {idx < skillDetails.learning_resources.slice(0, 3).length - 1 ? ", " : ""}
                        </span>
                      ))}
                    </p>
                  )}
                  {skillDetails.salary_metrics?.mean && (
                    <p>
                      <strong>Average Salary (Roles using this skill): </strong>
                      ${Math.round(skillDetails.salary_metrics.mean).toLocaleString()}
                    </p>
                  )}

                  {skillDetails.salary_metrics?.min && skillDetails.salary_metrics?.max && (
                    <p>
                      <strong>Salary Range: </strong>
                      ${Math.round(skillDetails.salary_metrics.min).toLocaleString()} - ${Math.round(skillDetails.salary_metrics.max).toLocaleString()}
                    </p>
                  )}
                </>
              ) : (
                <p>No detailed information available for {selectedSkill.name}.</p>
              )}
              <div className="modal-buttons">
                {skillDetails?.learning_resources?.[0]?.url && (
                  <button 
                    className="apply-button" 
                    onClick={() => handleApply(skillDetails.learning_resources[0].url)}
                  >
                    Learn More
                  </button>
                )}
                <button className="close-button" onClick={closeSkillModal}>Close</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Personalized;
