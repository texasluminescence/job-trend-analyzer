import React, { useState, useEffect } from 'react';
import '../TaskBar/task-bar.css';
import PopUp from '../PopUp/pop-up';

const SkillsTable = ({ industry = '', loading = false }) => {
  const [isPopUpOpen, setIsPopUpOpen] = useState(false);
  const [selectedSkill, setSelectedSkill] = useState(null);
  const [popularSkills, setPopularSkills] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (industry) {
      fetchPopularSkills(industry);
    } else {
      setPopularSkills([]);
    }
  }, [industry]);

  const fetchPopularSkills = (industryName) => {
    setIsLoading(true);
    setError('');
    
    fetch(`http://127.0.0.1:8000/popular-skills?industry=${encodeURIComponent(industryName)}`)
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to fetch skills for this industry');
        }
        return response.json();
      })
      .then(data => {
        setPopularSkills(data);
        setIsLoading(false);
      })
      .catch(error => {
        console.error("Error fetching popular skills:", error);
        setPopularSkills([]);
        setIsLoading(false);
        setError("Could not load skills for the selected industry.");
      });
  };

  // Open the modal and set the skill data
  const openPopUp = (skillData) => {
    setSelectedSkill(skillData);
    setIsPopUpOpen(true);
  };

  // Close the modal
  const closePopUp = () => {
    setIsPopUpOpen(false);
    setSelectedSkill(null);
  };

  if (isLoading) {
    return <div className="loading-spinner">Loading popular skills...</div>;
  }

  if (popularSkills.length === 0 && !isLoading) {
    return (
      <div className="no-selection-message">
        {industry ? "No skills found for this industry." : "Please select an industry to view trending skills."}
      </div>
    );
  }

  return (
    <div>
      <table>
        <thead>
          <tr>
            <th>Skill</th>
            <th>Jobs Looking for This Skill</th>
            <th>Number of Job Postings Including This Skill</th>
          </tr>
        </thead>
        <tbody>
          {popularSkills.map((skill, index) => (
            <tr key={index} onClick={() => openPopUp(skill)}>
              <td>{skill.skill}</td>
              <td>{skill.jobs}</td>
              <td>{skill.number}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <PopUp 
        isOpen={isPopUpOpen} 
        close={closePopUp} 
        jobData={selectedSkill} 
      />
    </div>
  );
};

export default SkillsTable;