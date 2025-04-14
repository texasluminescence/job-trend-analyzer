import React, { useState, useEffect } from "react";
import { Link } from 'react-router-dom';
import BarChart from "./personalized-bar-graph";
import "./personalized.css";
import arima from '../../assets/2 Year Salary Progression Forecast.png';

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
  const [userSkills, setUserSkills] = useState([]);

  // Check login status
  const isLoggedIn = !!localStorage.getItem('userEmail');
  const userEmail = localStorage.getItem('userEmail');

  // flag for ARIMA
  const [useArima, setUseArima] = useState(false);

  useEffect(() => {
    // Only fetch data if logged in
    if (isLoggedIn) {
      // Fetch personalized skill recommendations
      const fetchSuggestedSkills = async () => {
        try {
          setSkillsLoading(true);
          // Add a timestamp parameter to prevent caching
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
          
          // Filter out skills the user already has
          const filteredSkills = data.filter(skill => {
            // Normalize skill name to lowercase for case-insensitive comparison
            const skillName = skill.name.toLowerCase();
            // Check if this skill is already in the user's skill set
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

      // Fetch job postings that match the user's skills
      const fetchJobPostings = async () => {
        try {
          setLoading(true);
          
          // Get user data first to extract skills
          console.log("Fetching user data for email:", userEmail);
          // Add a timestamp parameter to prevent caching
          const timestamp = new Date().getTime();
          const userResponse = await fetch(`http://localhost:8000/user?email=${encodeURIComponent(userEmail)}&t=${timestamp}`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            }
          });
          
          if (!userResponse.ok) {
            console.error("User data fetch failed with status:", userResponse.status);
            throw new Error(`Failed to fetch user data: ${userResponse.status}`);
          }
          
          const userData = await userResponse.json();
          console.log("User data retrieved:", userData);
          
          // Check if user has completed profile
          const userIndustries = userData.industries || [];
          if (userIndustries.length === 0) {
            console.log("User has no industries defined");
            setJobPostings([]);
            setError("Please add industries to your profile to see job recommendations.");
            setLoading(false);
            return;
          }
          
          // Extract user skills from their profile
          const extractedSkills = [];
          const skillsDict = userData.skills || {};
          
          console.log("Skills data structure:", JSON.stringify(skillsDict));
          
          // Extract skills based on the actual structure
          if (typeof skillsDict === 'object') {
            // If skills is directly an array
            if (Array.isArray(skillsDict)) {
              skillsDict.forEach(skill => {
                if (skill && skill !== "None") extractedSkills.push(skill);
              });
            } else {
              // If skills is nested in categories
              Object.entries(skillsDict).forEach(([category, skills]) => {
                if (Array.isArray(skills)) {
                  // If category contains an array of skills
                  skills.forEach(skill => {
                    if (skill && skill !== "None") extractedSkills.push(skill);
                  });
                } else if (typeof skills === 'object' && skills !== null) {
                  // If category contains an object with skill names as keys
                  Object.keys(skills).forEach(skill => {
                    if (skill !== "None" && skill) extractedSkills.push(skill);
                  });
                } else if (typeof skills === 'string' && skills && skills !== "None") {
                  // If category directly contains a skill as string
                  extractedSkills.push(skills);
                }
              });
            }
          }
          
          console.log("Extracted skills:", extractedSkills);
          setUserSkills(extractedSkills);
          
          // If user has no skills, fetch popular jobs instead
          if (extractedSkills.length === 0) {
            console.log("No skills found, fetching popular jobs instead");
            await fetchPopularJobsWithCompanies();
            return;
          }
          
          // Build the query string for the skills
          const skillsQuery = extractedSkills
            .filter(skill => skill) // Remove empty skills
            .map(skill => `skills=${encodeURIComponent(skill)}`)
            .join('&');
          
          const url = `http://localhost:8000/job-postings-by-skills?${skillsQuery}&limit=10&t=${timestamp}`;
          
          console.log("Fetching job postings from:", url);
          
          const response = await fetch(url, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            }
          });
          
          if (!response.ok) {
            const errorText = await response.text();
            console.error("Job postings API failed:", errorText);
            throw new Error(`API request failed with status ${response.status}: ${errorText}`);
          }
          
          const data = await response.json();
          console.log("Job postings API response:", data);
          
          // Validate the data
          if (!Array.isArray(data)) {
            console.error("API returned non-array data:", data);
            throw new Error("API returned invalid data format");
          }
          
          if (data.length === 0) {
            console.log("No matching jobs found, trying popular jobs instead");
            await fetchPopularJobsWithCompanies();
            return;
          }
          
          // Filter for postings from the last year
          const currentDate = new Date();
          const oneYearAgo = new Date();
          oneYearAgo.setFullYear(currentDate.getFullYear() - 1);
          
          const filteredData = data.filter(posting => {
            // Check if posting has date field
            if (!posting.date_posted && !posting.posted_date) {
              return true; // Include if no date available (default behavior)
            }
            
            // Parse the date (handle different possible field names)
            const postingDate = new Date(posting.date_posted || posting.posted_date);
            
            // Only include if date is valid and within the last year
            return !isNaN(postingDate.getTime()) && postingDate >= oneYearAgo;
          });
          
          // Format the data for display
          const formattedData = filteredData.map((posting, index) => ({
            letter: (index + 1).toString(),
            ...posting,
            match_score: posting.match_score !== undefined ? Number(posting.match_score) : null,
            description: posting.description || `${posting.title || "Job"} at ${posting.company || "Company"}`,
            recommended: true // Mark as recommended since these are matched jobs
          }));
          
          setJobPostings(formattedData);
          setError(formattedData.length === 0 ? "No recent job postings found. Try updating your profile." : null);
        } catch (err) {
          console.error("Error in primary job fetching:", err);
          
          // If error occurs, try to fetch popular jobs instead
          try {
            console.log("Attempting to fetch popular jobs as fallback");
            await fetchPopularJobsWithCompanies();
          } catch (fallbackErr) {
            console.error("Error in fallback popular jobs fetch:", fallbackErr);
            setError("Please add industries to your profile to see job recommendations.");
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
          
          console.log("User industries for popular jobs:", userIndustries);
          
          // If user has no industries, show appropriate message
          if (userIndustries.length === 0) {
            console.log("User has no industries defined");
            setJobPostings([]);
            setError("Please add industries to your profile to see job recommendations.");
            return;
          }
          
          let jobsData = [];
          
          // Just use the first industry for simplicity
          const industryName = userIndustries[0];
          
          console.log("Fetching roles for industry:", industryName);
          
          // First fetch detailed popular roles to get role names
          const popularRolesUrl = `http://localhost:8000/detailed-popular-roles?industry=${encodeURIComponent(industryName)}&t=${timestamp}`;
          const rolesResponse = await fetch(popularRolesUrl, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            }
          });
          
          if (!rolesResponse.ok) {
            console.error("Failed to fetch popular roles:", rolesResponse.status);
            setJobPostings([]);
            setError("Please add industries to your profile to see job recommendations.");
            return;
          }
          
          const rolesData = await rolesResponse.json();
          console.log("Roles data received:", rolesData);
          
          if (!Array.isArray(rolesData) || rolesData.length === 0) {
            console.log("No roles found for industry:", industryName);
            setJobPostings([]);
            setError(`No job roles found for ${industryName}. Try a different industry.`);
            return;
          }
          
          // For each role, create a job posting
          for (const role of rolesData) {
            try {
              console.log("Processing role:", role.role_name);
              
              // Try to fetch an actual job posting for this role
              let job = null;
              
              try {
                const jobPostingUrl = `http://localhost:8000/job-postings?role=${encodeURIComponent(role.role_name)}&industry=${encodeURIComponent(industryName)}&limit=1&t=${timestamp}`;
                console.log("Fetching job from:", jobPostingUrl);
                
                const jobResponse = await fetch(jobPostingUrl);
                
                if (jobResponse.ok) {
                  const jobsForRole = await jobResponse.json();
                  
                  if (jobsForRole && Array.isArray(jobsForRole) && jobsForRole.length > 0) {
                    job = jobsForRole[0];
                    console.log("Found actual job posting for role:", role.role_name);
                  }
                }
              } catch (jobErr) {
                console.error("Error fetching job posting:", jobErr);
                // Continue with role data only
              }
              
              // Filter for jobs from the last year
              const currentDate = new Date();
              const oneYearAgo = new Date();
              oneYearAgo.setFullYear(currentDate.getFullYear() - 1);
              
              // Check if job posting is from within the last year
              const isRecentJob = (job) => {
                if (!job || (!job.date_posted && !job.posted_date)) {
                  return true; // Include if no date available
                }
                
                const postingDate = new Date(job.date_posted || job.posted_date);
                return !isNaN(postingDate.getTime()) && postingDate >= oneYearAgo;
              };
              
              // Use job posting if found and recent, otherwise use role data
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
                  recommended: false, // Mark as not specifically recommended based on skills
                  match_score: null,
                  posting_url: job.posting_url || null,
                  date_posted: job.date_posted || job.posted_date || new Date().toISOString()
                });
              } else {
                // Create entry with role info only
                jobsData.push({
                  letter: (jobsData.length + 1).toString(),
                  title: role.role_name,
                  company: role.top_hiring_companies?.[0] || "Various Companies",
                  location: "Multiple Locations",
                  description: role.description || 
                             `This ${role.role_name} position is in high demand in the ${industryName} industry.`,
                  industry: industryName,
                  skills: role.required_skills || [],
                  recommended: false, // Mark as not specifically recommended based on skills
                  match_score: null,
                  date_posted: new Date().toISOString()
                });
              }
              
              // Limit to 5 roles
              if (jobsData.length >= 5) break;
            } catch (roleErr) {
              console.error("Error processing role:", roleErr);
              // Continue with next role
            }
          }
          
          // Check if we found any jobs
          if (jobsData.length === 0) {
            console.log("No jobs found for any roles");
            setJobPostings([]);
            setError("No job recommendations found. Try updating your profile.");
            return;
          }
          
          console.log("Setting job postings:", jobsData);
          setJobPostings(jobsData);
          setError(null);
        } catch (err) {
          console.error("Error in fetchPopularJobsWithCompanies:", err);
          setJobPostings([]);
          setError("Please add industries to your profile to see job recommendations.");
        }
      };
      
      // Fetch user's selected job roles and check for conditional ARIMA model
      const checkArima = async () => {
        try {
          // Get user data first to extract roles
          console.log("Fetching user data for email:", userEmail);
          const timestamp = new Date().getTime();
          const userResponse = await fetch(`http://localhost:8000/user?email=${encodeURIComponent(userEmail)}&t=${timestamp}`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            }
          });
          
          if (!userResponse.ok) {
            console.error("User data fetch failed with status:", userResponse.status);
            throw new Error(`Failed to fetch user data: ${userResponse.status}`);
          }
          
          const userData = await userResponse.json();
          
          // Extract user roles from their profile 
          const rolesDict = userData.interested_roles || {};  
          rolesDict.forEach(role => {
            if (role && role === "Data Scientist") {
              setUseArima(true); 
            }
          })

        }
        catch (err) {
          console.error("Error fetching user profile:", err);
          setError("Error loading user profile. Please try again later.");
          setLoading(false);
        }
      };

      checkArima(); 




      // First fetch user skills, then fetch suggested skills
      const fetchUserProfileAndData = async () => {
        try {
          // Get user data first to extract skills
          console.log("Fetching user data for email:", userEmail);
          const timestamp = new Date().getTime();
          const userResponse = await fetch(`http://localhost:8000/user?email=${encodeURIComponent(userEmail)}&t=${timestamp}`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            }
          });
          
          if (!userResponse.ok) {
            console.error("User data fetch failed with status:", userResponse.status);
            throw new Error(`Failed to fetch user data: ${userResponse.status}`);
          }
          
          const userData = await userResponse.json();
          
          // Extract user skills from their profile
          const extractedSkills = [];
          const skillsDict = userData.skills || {}; 
          
          // Extract skills based on the actual structure
          if (typeof skillsDict === 'object') {
            // If skills is directly an array
            if (Array.isArray(skillsDict)) {
              skillsDict.forEach(skill => {
                if (skill && skill !== "None") extractedSkills.push(skill);
              });
            } else {
              // If skills is nested in categories
              Object.entries(skillsDict).forEach(([category, skills]) => {
                if (Array.isArray(skills)) {
                  // If category contains an array of skills
                  skills.forEach(skill => {
                    if (skill && skill !== "None") extractedSkills.push(skill);
                  });
                } else if (typeof skills === 'object' && skills !== null) {
                  // If category contains an object with skill names as keys
                  Object.keys(skills).forEach(skill => {
                    if (skill !== "None" && skill) extractedSkills.push(skill);
                  });
                } else if (typeof skills === 'string' && skills && skills !== "None") {
                  // If category directly contains a skill as string
                  extractedSkills.push(skills);
                }
              });
            }
          }
          
          console.log("Extracted user skills:", extractedSkills);
          setUserSkills(extractedSkills);
          
          // Now fetch suggested skills and job postings
          await fetchSuggestedSkills();
          await fetchJobPostings();
          
        } catch (err) {
          console.error("Error fetching user profile:", err);
          setError("Error loading user profile. Please try again later.");
          setLoading(false);
        }
      };

      fetchUserProfileAndData();
    }
  }, [isLoggedIn, userEmail]);

  const openModal = (job) => {
    setSelectedJob(job);
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
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
                <p>
                  <strong>Match: </strong> {Math.round(selectedJob.match_score)}%
                </p>
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
                <button className="close-button" onClick={closeModal}>Close</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Personalized;
