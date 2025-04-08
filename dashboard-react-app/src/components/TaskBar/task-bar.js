import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './task-bar.css';
import BlackCircle from '../../assets/BlackCircle.png';

const TaskBar = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        // Check if user is logged in by checking local storage
        const userEmail = localStorage.getItem('userEmail');
        setIsLoggedIn(!!userEmail);
    }, []);

    useEffect(() => {
        const checkLoginStatus = () => {
            const userEmail = localStorage.getItem('userEmail');
            console.log('Storage event detected, userEmail:', userEmail);
            setIsLoggedIn(!!userEmail);
        };
    
        window.addEventListener('storage', checkLoginStatus);
        
        checkLoginStatus();
        
        return () => {
            window.removeEventListener('storage', checkLoginStatus);
        };
    }, []);

    const handleLogout = () => {
        // Remove user email from local storage
        localStorage.removeItem('userEmail');
        setIsLoggedIn(false);
        // Redirect to home page
        navigate('/');
    };

    return (
        <div className="task-bar">
            <div className="logo-container">
                <div className="logo">
                    <img src={BlackCircle} alt="JobSense Logo"/>
                </div>
                <div className="name">
                    <h2>JobSense</h2>
                </div>
            </div>
            
            <ul className="task-bar-links">
                <li><Link to="/">Home</Link></li>
                <li><Link to="/personalized">Personalized Insights</Link></li>
                {isLoggedIn ? (
                    <>
                        <li><Link to="/account">Your Account</Link></li>
                        <li><button onClick={handleLogout} className="logout-button">Logout</button></li>
                    </>
                ) : (
                    <li><Link to="/login">Login</Link></li>
                )}
            </ul>
        </div>
    );
};

export default TaskBar;