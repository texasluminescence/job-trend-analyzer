import React, { useState } from 'react';
import './task-bar.css';
import SearchBar from './search-bar';
import BlackCircle from './BlackCircle.png';


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