import React, { useState } from 'react';
import './task-bar.css';
import SearchBar from './search-bar';


const TaskBar = () => {
    const handleSearch = (query) => {
        console.log('Searching for: ' + query);
    };

    return(

        <div className="task-bar">
            <div className = "logo"></div>
            <div className = "name">
                <h2>OpenToWork</h2>
            </div>
            <ul className = "task-bar-links">
                <li> <a href = "/" >Home</a></li>
                <li> <a href = "/" >Industry Insights</a></li>
                <li> <a href = "/" >Company Insights</a></li>
                <li> <a href = "/" >Company Leaderboard</a></li>
            </ul>

            <div className = "task-search-bar">
                <SearchBar placeholder="Search in site" onSearch={handleSearch} showButton={false} />
            </div>
        </div>
    );
};

export default TaskBar;