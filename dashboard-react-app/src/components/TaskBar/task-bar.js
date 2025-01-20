import React, { useState } from 'react';
import './task-bar.css';
import SearchBar from '../SearchBar/search-bar';
import BlackCircle from '../../assets/BlackCircle.png';


const TaskBar = () => {
    return(

        <div className="task-bar">
            <div className = "logo">
                <img src={BlackCircle}/>
            </div>
            <div className = "name">
                <h2>JobSense</h2>
            </div>
            <ul className = "task-bar-links">
                <li> <a href = "/" >Home</a></li>
                <li> <a href = "/personalized" >Personalized Insights</a></li>
                <li> <a href = "/account" >Your Account</a></li>
            </ul>
        </div>
    );
};

export default TaskBar;