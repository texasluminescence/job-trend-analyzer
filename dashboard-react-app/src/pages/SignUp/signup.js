import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './signup.css';

const SignUpPage = () => {
    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        email: '',
        password: '',
        education_level: '',
        graduation_date: '',
        degree: '',
        industries: [],
        interested_roles: [],
        current_job: '',
        yoe: 0,
        skills: {},
        type_of_work: ''
    });
    const [error, setError] = useState('');
    const [activeSection, setActiveSection] = useState('basic');
    const navigate = useNavigate();

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prevState => ({
            ...prevState,
            [name]: value
        }));
    };

    const handleIndustryChange = (e) => {
        const { value, checked } = e.target;
        setFormData(prevState => ({
            ...prevState,
            industries: checked 
                ? [...prevState.industries, value]
                : prevState.industries.filter(industry => industry !== value)
        }));
    };

    const handleRoleChange = (e) => {
        const { value, checked } = e.target;
        setFormData(prevState => ({
            ...prevState,
            interested_roles: checked 
                ? [...prevState.interested_roles, value]
                : prevState.interested_roles.filter(role => role !== value)
        }));
    };

    const handleSkillChange = (e) => {
        const { name, value } = e.target;
        setFormData(prevState => ({
            ...prevState,
            skills: {
                ...prevState.skills,
                [name]: value
            }
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        // Check if email and password are provided
        if (!formData.email || !formData.password) {
            setError('Email and password are required');
            return;
        }

        try {
            const response = await fetch('http://localhost:8000/user/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Signup failed');
            }

            const data = await response.json();
            
            // Store email in local storage
            localStorage.setItem('userEmail', formData.email);
            
            // Redirect to account page
            navigate('/account');
        } catch (err) {
            setError(err.message);
            console.error('Signup error:', err);
        }
    };

    const nextSection = () => {
        if (activeSection === 'basic') {
            if (!formData.email || !formData.password) {
                setError('Email and password are required');
                return;
            }
            setActiveSection('education');
        } else if (activeSection === 'education') {
            setActiveSection('professional');
        }
        setError('');
    };

    const prevSection = () => {
        if (activeSection === 'education') {
            setActiveSection('basic');
        } else if (activeSection === 'professional') {
            setActiveSection('education');
        }
        setError('');
    };

    // Common job roles
    const commonRoles = [
        'Software Engineer', 
        'Data Scientist', 
        'Product Manager', 
        'UX Designer', 
        'Financial Analyst', 
        'Marketing Specialist',
        'Project Manager',
        'Business Analyst',
        'Sales Representative',
        'Operations Manager'
    ];

    return (
        <div className="signup-container">
            <div className="signup-form-container">
                <form className="signup-form" onSubmit={handleSubmit}>
                    <h2>Create Your JobSense Account</h2>
                    {error && <div className="error-message">{error}</div>}
                    
                    <div className="form-progress">
                        <div className={`progress-step ${activeSection === 'basic' ? 'active' : activeSection === 'education' || activeSection === 'professional' ? 'completed' : ''}`}>1</div>
                        <div className="progress-line"></div>
                        <div className={`progress-step ${activeSection === 'education' ? 'active' : activeSection === 'professional' ? 'completed' : ''}`}>2</div>
                        <div className="progress-line"></div>
                        <div className={`progress-step ${activeSection === 'professional' ? 'active' : ''}`}>3</div>
                    </div>

                    {activeSection === 'basic' && (
                        <div className="form-section">
                            <h3>Basic Information</h3>
                            <div className="form-row">
                                <div className="form-group">
                                    <label htmlFor="first_name">First Name</label>
                                    <input 
                                        type="text" 
                                        id="first_name"
                                        name="first_name"
                                        value={formData.first_name}
                                        onChange={handleChange}
                                        placeholder="Your first name"
                                    />
                                </div>
                                <div className="form-group">
                                    <label htmlFor="last_name">Last Name</label>
                                    <input 
                                        type="text" 
                                        id="last_name"
                                        name="last_name"
                                        value={formData.last_name}
                                        onChange={handleChange}
                                        placeholder="Your last name"
                                    />
                                </div>
                            </div>

                            <div className="form-group">
                                <label htmlFor="email">Email <span className="required">*</span></label>
                                <input 
                                    type="email" 
                                    id="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    required 
                                    className="required-field"
                                    placeholder="your.email@example.com"
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="password">Password <span className="required">*</span></label>
                                <input 
                                    type="password" 
                                    id="password"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    required 
                                    className="required-field"
                                    placeholder="Create a secure password"
                                />
                                <span className="password-hint">Use at least 8 characters with letters and numbers</span>
                            </div>

                            <div className="nav-buttons">
                                <button type="button" className="next-button" onClick={nextSection}>Next</button>
                            </div>
                        </div>
                    )}

                    {activeSection === 'education' && (
                        <div className="form-section">
                            <h3>Education Details</h3>
                            <div className="form-group">
                                <label htmlFor="education_level">Education Level</label>
                                <select 
                                    id="education_level"
                                    name="education_level"
                                    value={formData.education_level}
                                    onChange={handleChange}
                                >
                                    <option value="">Select Education Level</option>
                                    <option value="High School">High School</option>
                                    <option value="Associate Degree">Associate Degree</option>
                                    <option value="Bachelor's Degree">Bachelor's Degree</option>
                                    <option value="Master's Degree">Master's Degree</option>
                                    <option value="Doctoral Degree">Doctoral Degree</option>
                                </select>
                            </div>

                            <div className="form-group">
                                <label htmlFor="graduation_date">Graduation Date</label>
                                <input 
                                    type="date" 
                                    id="graduation_date"
                                    name="graduation_date"
                                    value={formData.graduation_date}
                                    onChange={handleChange}
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="degree">Degree</label>
                                <input 
                                    type="text" 
                                    id="degree"
                                    name="degree"
                                    value={formData.degree}
                                    onChange={handleChange}
                                    placeholder="e.g., Computer Science, Business, etc."
                                />
                            </div>

                            <div className="nav-buttons">
                                <button type="button" className="back-button" onClick={prevSection}>Back</button>
                                <button type="button" className="next-button" onClick={nextSection}>Next</button>
                            </div>
                        </div>
                    )}

                    {activeSection === 'professional' && (
                        <div className="form-section">
                            <h3>Professional Information</h3>
                            
                            <div className="form-group">
                                <label htmlFor="current_job">Current Job (if any)</label>
                                <input 
                                    type="text" 
                                    id="current_job"
                                    name="current_job"
                                    value={formData.current_job}
                                    onChange={handleChange}
                                    placeholder="e.g., Software Developer at Tech Company"
                                />
                            </div>

                            <div className="form-group">
                                <label>Industries of Interest</label>
                                <div className="checkbox-grid">
                                    {['Technology', 'Finance', 'Healthcare', 'Education', 'Marketing', 'Engineering', 
                                      'Retail', 'Hospitality', 'Construction', 'Entertainment', 'Automotive', 'Manufacturing'].map(industry => (
                                        <label key={industry} className="checkbox-label">
                                            <input 
                                                type="checkbox" 
                                                name="industries"
                                                value={industry}
                                                checked={formData.industries.includes(industry)}
                                                onChange={handleIndustryChange}
                                            />
                                            <span>{industry}</span>
                                        </label>
                                    ))}
                                </div>
                            </div>

                            <div className="form-group">
                                <label>Roles of Interest</label>
                                <div className="checkbox-grid">
                                    {commonRoles.map(role => (
                                        <label key={role} className="checkbox-label">
                                            <input 
                                                type="checkbox" 
                                                name="interested_roles"
                                                value={role}
                                                checked={formData.interested_roles.includes(role)}
                                                onChange={handleRoleChange}
                                            />
                                            <span>{role}</span>
                                        </label>
                                    ))}
                                </div>
                            </div>

                            <div className="form-group">
                                <label htmlFor="yoe">Years of Experience</label>
                                <input 
                                    type="number" 
                                    id="yoe"
                                    name="yoe"
                                    value={formData.yoe}
                                    onChange={handleChange}
                                    min="0"
                                    placeholder="0"
                                />
                            </div>

                            <div className="form-group">
                                <label>Skills</label>
                                <div className="skill-input">
                                    <input 
                                        type="text" 
                                        placeholder="Skill Name"
                                        id="skillName"
                                        name="newSkillName"
                                        value={formData.newSkillName || ''}
                                        onChange={handleChange}
                                    />
                                    <select
                                        id="skillLevel"
                                        name="newSkillLevel"
                                        value={formData.newSkillLevel || ''}
                                        onChange={handleChange}
                                    >
                                        <option value="">Proficiency</option>
                                        <option value="1">1 - Beginner</option>
                                        <option value="2">2 - Basic</option>
                                        <option value="3">3 - Intermediate</option>
                                        <option value="4">4 - Advanced</option>
                                        <option value="5">5 - Expert</option>
                                    </select>
                                    <button 
                                        type="button" 
                                        className="add-skill-button"
                                        onClick={() => {
                                            if (formData.newSkillName && formData.newSkillLevel) {
                                                setFormData(prevState => ({
                                                    ...prevState,
                                                    skills: {
                                                        ...prevState.skills,
                                                        [formData.newSkillName]: parseInt(formData.newSkillLevel)
                                                    },
                                                    newSkillName: '',
                                                    newSkillLevel: ''
                                                }));
                                            }
                                        }}
                                    >
                                        Add
                                    </button>
                                </div>
                                <div className="added-skills">
                                    {Object.entries(formData.skills).map(([skill, level]) => (
                                        <div key={skill} className="skill-tag">
                                            {skill}: {level}
                                            <button 
                                                type="button"
                                                className="remove-skill-button"
                                                onClick={() => {
                                                    const { [skill]: removedSkill, ...remainingSkills } = formData.skills;
                                                    setFormData(prevState => ({
                                                        ...prevState,
                                                        skills: remainingSkills
                                                    }));
                                                }}
                                            >
                                                ×
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div className="form-group">
                                <label htmlFor="type_of_work">Type of Work</label>
                                <select 
                                    id="type_of_work"
                                    name="type_of_work"
                                    value={formData.type_of_work}
                                    onChange={handleChange}
                                >
                                    <option value="">Select Work Type</option>
                                    <option value="Full-time">Full-time</option>
                                    <option value="Part-time">Part-time</option>
                                    <option value="Contract">Contract</option>
                                    <option value="Remote">Remote</option>
                                    <option value="Hybrid">Hybrid</option>
                                    <option value="Freelance">Freelance</option>
                                </select>
                            </div>

                            <div className="nav-buttons">
                                <button type="button" className="back-button" onClick={prevSection}>Back</button>
                                <button type="submit" className="signup-button">Create Account</button>
                            </div>
                        </div>
                    )}
                    
                    <div className="login-link">
                        Already have an account? <a href="/login">Log In</a>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default SignUpPage;