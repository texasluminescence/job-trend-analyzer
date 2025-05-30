import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import './task-bar.css';
import BlackCircle from '../../assets/BlackCircle.png';

const TaskBar = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();

    // Check login status whenever the component renders or location changes
    useEffect(() => {
        const userEmail = localStorage.getItem('userEmail');
        setIsLoggedIn(!!userEmail);
        console.log('Login status checked, isLoggedIn:', !!userEmail);
    }, [location]);

    // Create a custom event listener for login/logout actions
    useEffect(() => {
        const handleLoginStatusChange = () => {
            const userEmail = localStorage.getItem('userEmail');
            setIsLoggedIn(!!userEmail);
            console.log('Login status event triggered, isLoggedIn:', !!userEmail);
        };

        // Listen for custom login/logout events
        window.addEventListener('loginStatusChange', handleLoginStatusChange);
        
        // Initial check
        handleLoginStatusChange();
        
        return () => {
            window.removeEventListener('loginStatusChange', handleLoginStatusChange);
        };
    }, []);

    const handleLogout = () => {
        // Remove user email from local storage
        localStorage.removeItem('userEmail');
        setIsLoggedIn(false);
        
        // Dispatch a custom event to notify other components
        window.dispatchEvent(new Event('loginStatusChange'));
        
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