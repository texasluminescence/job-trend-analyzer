import React, { useState } from 'react';
import '../TaskBar/task-bar.css';
import PopUp from '../PopUp/pop-up';

const SkillsTable = () => {

  const [isPopUpOpen, setIsPopUpOpen] = useState(false);
    const [selectedSkill, setSelectedSkill] = useState(null);
  
      // Open the modal and set the job data
      const openPopUp = (skillData) => {
        setSelectedSkill(skillData);
        setIsPopUpOpen(true);
      };
    
      // Close the modal
      const closePopUp = () => {
        setIsPopUpOpen(false);
        setSelectedSkill(null);
      };
  
      const skills = [
        { skill: "Python", jobs: "Data Engineer", number: 10000 },
        { skill: "Python", jobs: "Data Engineer", number: 10000},
        { skill: "Python", jobs: "Data Engineer", number: 10000 },
        { skill: "Python", jobs: "Data Engineer", number:10000},
        { skill: "Python", jobs:"Data Engineer", number:10000 },
        { skill: "Python", jobs: "Data Engineer", number: 10000 }
      ];
    return(
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
          {skills.map((skill, index) => (
            <tr key={index} onClick={() => openPopUp(skill)}>
              <td>{skill.skill}</td>
              <td>{skill.jobs}</td>
              <td>{skill.number}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Pass isOpen and close functions to the PopUp component */}
      <PopUp 
        isOpen={isPopUpOpen} 
        close={closePopUp} 
        jobData={selectedSkill} 
      />
    </div>
        // <table>
        //   <tr>
        //     <th>Skill</th>
        //     <th>Jobs Looking for This Skill</th>
        //     <th>Number of Job Postings Including This Skill</th>
        //   </tr>
        //   <tr>
        //     <td>Python</td>
        //     <td>Data Engineer</td>
        //     <td>10000</td>
        //   </tr>
        //   <tr>
        //     <td>Python</td>
        //     <td>Data Engineer</td>
        //     <td>10000</td>
        //   </tr>
        //   <tr>
        //     <td>Python</td>
        //     <td>Data Engineer</td>
        //     <td>10000</td>
        //   </tr>
        //     <tr>
        //     <td>Python</td>
        //     <td>Data Engineer</td>
        //     <td>10000</td>
        //   </tr>
        // </table>
    );
};

export default SkillsTable;