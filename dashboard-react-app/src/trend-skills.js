import React, { useState } from 'react';
import './task-bar.css';


const SkillsTable = () => {
    return(
        <table>
          <tr>
            <th>Skill</th>
            <th>Jobs Looking for This Skill</th>
            <th>Number of Job Postings Including This Skill</th>
          </tr>
          <tr>
            <td>Python</td>
            <td>Data Engineer</td>
            <td>10000</td>
          </tr>
          <tr>
            <td>Python</td>
            <td>Data Engineer</td>
            <td>10000</td>
          </tr>
          <tr>
            <td>Python</td>
            <td>Data Engineer</td>
            <td>10000</td>
          </tr>
            <tr>
            <td>Python</td>
            <td>Data Engineer</td>
            <td>10000</td>
          </tr>
        </table>
    );
};

export default SkillsTable;