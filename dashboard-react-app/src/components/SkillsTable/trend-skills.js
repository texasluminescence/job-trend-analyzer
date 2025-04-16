import React, { useState, useEffect } from 'react';
import '../shared/table-styles.css'; // Using shared CSS
import PopUp from '../PopUp/pop-up';

const SkillsTable = ({ industry = '', loading = false, popularSkills = [] }) => {
  const [isPopUpOpen, setIsPopUpOpen] = useState(false);
  const [selectedSkill, setSelectedSkill] = useState(null);
  const [skillDetails, setSkillDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  const limitedSkills = Array.isArray(popularSkills) ? popularSkills.slice(0, 5) : [];

  // Open the modal and fetch detailed skill data
  const openPopUp = async (skillData) => {
    setSelectedSkill(skillData);
    setIsPopUpOpen(true);
    
    // If we have a skill name, fetch more details
    if (skillData.skill_name || skillData.skill) {
      setLoadingDetails(true);
      try {
        const skillName = skillData.skill_name || skillData.skill;
        const response = await fetch(`http://127.0.0.1:8000/skills/${encodeURIComponent(skillName)}`);
        
        if (response.ok) {
          const details = await response.json();
          setSkillDetails(details);
        } else {
          // If detailed API fails, we'll just use what we have
          setSkillDetails(null);
        }
      } catch (error) {
        console.error("Error fetching skill details:", error);
        setSkillDetails(null);
      } finally {
        setLoadingDetails(false);
      }
    }
  };

  // Close the modal
  const closePopUp = () => {
    setIsPopUpOpen(false);
    setSelectedSkill(null);
    setSkillDetails(null);
  };

  if (loading) {
    return <div className="loading-spinner">Loading popular skills...</div>;
  }

  // Only show the no selection message if popularSkills is an empty array AND we're not loading
  if (!loading && Array.isArray(limitedSkills) && limitedSkills.length === 0) {
    return (
      <div className="no-selection-message">
        No skills found for this industry. Please try another industry.
      </div>
    );
  }

  return (
    <div className="skills-table-container">
      <table className="skills-table">
        <thead>
          <tr>
            <th>Skill</th>
            <th>Jobs Looking for This Skill</th>
            <th>Number of Job Postings</th>
          </tr>
        </thead>
        <tbody>
          {Array.isArray(limitedSkills) && limitedSkills.map((skillItem, index) => {
            // Handle both simple string array and object array from API
            const skillName = typeof skillItem === 'string' ? skillItem : (skillItem.skill_name || skillItem.skill);
            const jobs = typeof skillItem === 'string' ? 'Various positions' : (skillItem.jobs || 'Various positions');
            const number = typeof skillItem === 'string' ? 'N/A' : (skillItem.number || skillItem.job_postings_count || 'N/A');
            
            return (
              <tr key={index} onClick={() => openPopUp(skillItem)} className="skill-row">
                <td>{skillName}</td>
                <td>{jobs}</td>
                <td>{number}</td>
              </tr>
            );
          })}
        </tbody>
      </table>

      {isPopUpOpen && selectedSkill && (
        <PopUp 
          isOpen={isPopUpOpen} 
          close={closePopUp} 
          jobData={{
            title: skillDetails?.skill_name || selectedSkill.skill_name || selectedSkill.skill || (typeof selectedSkill === 'string' ? selectedSkill : ''),
            description: skillDetails?.description || selectedSkill.description || 
              `${skillDetails?.skill_name || selectedSkill.skill_name || selectedSkill.skill || ''} is a popular skill in the ${industry} industry.`,
            resources: skillDetails?.learning_resources || [],
            industries: skillDetails?.industries || [industry],
            isLoading: loadingDetails
          }} 
        />
      )}
    </div>
  );
};

export default SkillsTable;