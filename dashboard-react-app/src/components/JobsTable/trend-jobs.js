import React, { useState } from 'react';
import '../TaskBar/task-bar.css';
import SearchBar from '../SearchBar/search-bar';
import BlackCircle from '../../assets/BlackCircle.png';


const JobsTable = () => {
    return(
        <table>
          <tr>
            <th>Role Title</th>
            <th>Number of Open Roles</th>
            <th>Companies Hiring</th>
          </tr>
          <tr>
            <td>Data Engineer</td>
            <td>10000</td>
            <td>Meta, Google</td>
          </tr>
          <tr>
            <td>Product Manager</td>
            <td>5000</td>
            <td>Oracle</td>
          </tr>
            <tr>
            <td>Data Engineer</td>
            <td>10000</td>
            <td>Meta, Google</td>
          </tr>
          <tr>
            <td>Product Manager</td>
            <td>5000</td>
            <td>Oracle</td>
          </tr>
                      <tr>
            <td>Data Engineer</td>
            <td>10000</td>
            <td>Meta, Google</td>
          </tr>
          <tr>
            <td>Product Manager</td>
            <td>5000</td>
            <td>Oracle</td>
          </tr>
        </table>
    );
};

export default JobsTable;