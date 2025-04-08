import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './AccountPage.css';

const AccountPage = () => {
    const [userData, setUserData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [editMode, setEditMode] = useState({
        profile: false,
        experience: false,
        industries: false,
        roles: false,
        skills: false
    });
    const [formData, setFormData] = useState({});
    const navigate = useNavigate();

    useEffect(() => {
        const fetchUserData = async () => {
            try {
                const userEmail = localStorage.getItem('userEmail');
                
                if (!userEmail) {
                    navigate('/login');
                    return;
                }

                const response = await fetch(`http://localhost:8000/user/?email=${userEmail}`);
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Failed to fetch user data');
                }

                const data = await response.json();
                setUserData(data);
                setFormData(data);
                setLoading(false);
            } catch (err) {
                console.error('Error fetching user data:', err);
                setError(err.message);
                setLoading(false);
            }
        };

        fetchUserData();
    }, [navigate]);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSkillChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            skills: {
                ...prev.skills,
                [name]: value
            }
        }));
    };

    const handleIndustryChange = (e) => {
        const value = e.target.value;
        setFormData(prev => ({
            ...prev,
            industries: value
        }));
    };

    const handleRoleChange = (e) => {
        const value = e.target.value;
        setFormData(prev => ({
            ...prev,
            interested_roles: value
        }));
    };

    const toggleEditMode = (section) => {
        setEditMode(prev => ({
            ...prev,
            [section]: !prev[section]
        }));
    };

    const saveChanges = async (section) => {
        try {
            let updateData = {
                email: userData.email
            };

            if (section === 'profile') {
                updateData.profile = {
                    education_level: formData.education_level,
                    graduation_date: formData.graduation_date,
                    degree: formData.degree
                };
            } else if (section === 'experience') {
                updateData.experience = {
                    yoe: formData.yoe,
                    type_of_work: formData.type_of_work,
                    current_job: formData.current_job
                };
            } else if (section === 'industries') {
                let industriesArray = [];
                
                if (typeof formData.industries === 'string') {
                    industriesArray = formData.industries
                        .split(',')
                        .map(item => item.trim())
                        .filter(item => item);
                } else if (Array.isArray(formData.industries)) {
                    industriesArray = formData.industries;
                }
                
                // Restoring the original nested format
                updateData.industries = {
                    industries: industriesArray
                };
                
                // Keep track of the processed array for local state update
                const processedIndustriesArray = [...industriesArray];
                
                setFormData(prev => ({
                    ...prev,
                    industries: processedIndustriesArray
                }));
            } else if (section === 'roles') {
                let rolesArray = [];
                
                if (typeof formData.interested_roles === 'string') {
                    rolesArray = formData.interested_roles
                        .split(',')
                        .map(item => item.trim())
                        .filter(item => item);
                } else if (Array.isArray(formData.interested_roles)) {
                    rolesArray = formData.interested_roles;
                }
                
                // Restoring the original nested format
                updateData.interested_roles = {
                    interested_roles: rolesArray
                };
                
                // Keep track of the processed array for local state update
                const processedRolesArray = [...rolesArray];
                
                setFormData(prev => ({
                    ...prev,
                    interested_roles: processedRolesArray
                }));
            } else if (section === 'skills') {
                updateData.skills = {
                    skills: formData.skills
                };
            }

            console.log('Sending update data:', JSON.stringify(updateData)); // Debug log

            const response = await fetch('http://localhost:8000/update-user/', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updateData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error('API error response:', errorData); // Debug log
                throw new Error(`Failed to update user data: ${JSON.stringify(errorData)}`);
            }

            // After successful update, refresh the user data
            const refreshResponse = await fetch(`http://localhost:8000/user/?email=${userData.email}`);
            if (!refreshResponse.ok) {
                throw new Error('Failed to refresh user data');
            }
            
            const refreshedData = await refreshResponse.json();
            setUserData(refreshedData);
            setFormData(refreshedData);
            
            toggleEditMode(section);

        } catch (err) {
            console.error('Error updating user data:', err);
            alert(`Failed to save changes: ${err.message}`);
        }
    };

    if (loading) {
        return <div className="loading-container">
            <div className="loader"></div>
            <p>Loading your account information...</p>
        </div>;
    }

    if (error) {
        return (
            <div className="error-container">
                <h2>Error Loading Account</h2>
                <p>{error}</p>
                <button onClick={() => navigate('/login')}>Return to Login</button>
            </div>
        );
    }

    return (
        <div className="account-wrapper">
            <section className="account-section">
                <div className="account-header">
                    <div className="account-section-headers">
                        <h1>Welcome, {userData?.first_name} {userData?.last_name}</h1>
                        <span className="account-email">{userData?.email}</span>
                    </div>
                </div>

                <div className="info-boxes-area">
                    <div className="info-text-box">
                        <div className="box-header">
                            <h3>Professional Details</h3>
                            <button 
                                className="toggle-edit" 
                                onClick={() => toggleEditMode('profile')}
                            >
                                {editMode.profile ? 'Cancel' : 'Edit'}
                            </button>
                        </div>
                        
                        {!editMode.profile ? (
                            <div className="info-content">
                                <div className="info-item">
                                    <span className="info-label">Education Level:</span>
                                    <span className="info-value">{userData?.education_level || 'Not specified'}</span>
                                </div>
                                <div className="info-item">
                                    <span className="info-label">Graduation Date:</span>
                                    <span className="info-value">{userData?.graduation_date || 'Not specified'}</span>
                                </div>
                                <div className="info-item">
                                    <span className="info-label">Degree:</span>
                                    <span className="info-value">{userData?.degree || 'Not specified'}</span>
                                </div>
                            </div>
                        ) : (
                            <div className="edit-form">
                                <div className="form-group">
                                    <label>Education Level</label>
                                    <select 
                                        name="education_level" 
                                        value={formData.education_level || ''} 
                                        onChange={handleInputChange}
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
                                    <label>Graduation Date</label>
                                    <input 
                                        type="date" 
                                        name="graduation_date" 
                                        value={formData.graduation_date || ''} 
                                        onChange={handleInputChange}
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Degree</label>
                                    <input 
                                        type="text" 
                                        name="degree" 
                                        value={formData.degree || ''} 
                                        onChange={handleInputChange}
                                        placeholder="e.g., Computer Science, Business, etc."
                                    />
                                </div>
                                <button 
                                    className="save-button" 
                                    onClick={() => saveChanges('profile')}
                                >
                                    Save Changes
                                </button>
                            </div>
                        )}
                    </div>

                    <div className="info-text-box">
                        <div className="box-header">
                            <h3>Work Experience</h3>
                            <button 
                                className="toggle-edit" 
                                onClick={() => toggleEditMode('experience')}
                            >
                                {editMode.experience ? 'Cancel' : 'Edit'}
                            </button>
                        </div>
                        
                        {!editMode.experience ? (
                            <div className="info-content">
                                <div className="info-item">
                                    <span className="info-label">Current Job:</span>
                                    <span className="info-value">{userData?.current_job || 'Not specified'}</span>
                                </div>
                                <div className="info-item">
                                    <span className="info-label">Years of Experience:</span>
                                    <span className="info-value">{userData?.yoe || '0'}</span>
                                </div>
                                <div className="info-item">
                                    <span className="info-label">Type of Work:</span>
                                    <span className="info-value">{userData?.type_of_work || 'Not specified'}</span>
                                </div>
                            </div>
                        ) : (
                            <div className="edit-form">
                                <div className="form-group">
                                    <label>Current Job</label>
                                    <input 
                                        type="text" 
                                        name="current_job" 
                                        value={formData.current_job || ''} 
                                        onChange={handleInputChange}
                                        placeholder="e.g., Software Developer at Tech Company"
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Years of Experience</label>
                                    <input 
                                        type="number" 
                                        name="yoe" 
                                        min="0" 
                                        value={formData.yoe || 0} 
                                        onChange={handleInputChange}
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Type of Work</label>
                                    <select 
                                        name="type_of_work" 
                                        value={formData.type_of_work || ''} 
                                        onChange={handleInputChange}
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
                                <button 
                                    className="save-button" 
                                    onClick={() => saveChanges('experience')}
                                >
                                    Save Changes
                                </button>
                            </div>
                        )}
                    </div>

                    <div className="info-text-box">
                        <div className="box-header">
                            <h3>Industries of Interest</h3>
                            <button 
                                className="toggle-edit" 
                                onClick={() => toggleEditMode('industries')}
                            >
                                {editMode.industries ? 'Cancel' : 'Edit'}
                            </button>
                        </div>
                        
                        {!editMode.industries ? (
                            <div className="info-content">
                                <div className="info-item">
                                    <div className="tag-container">
                                        {Array.isArray(userData?.industries) && userData.industries.length > 0 
                                            ? userData.industries.map((industry, index) => (
                                                <span key={index} className="tag">{industry}</span>
                                            ))
                                            : <span className="no-data">No industries specified</span>
                                        }
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="edit-form">
                                <div className="form-group">
                                    <label>Industries (comma-separated)</label>
                                    <textarea
                                        name="industries"
                                        value={Array.isArray(formData.industries) 
                                            ? formData.industries.join(', ') 
                                            : formData.industries || ''}
                                        onChange={handleIndustryChange}
                                        placeholder="Tech, Healthcare, Financial Services, etc."
                                    ></textarea>
                                    <p className="help-text">Enter multiple industries separated by commas (e.g., "Artificial Intelligence, Cloud Computing, Finance")</p>
                                </div>
                                <button 
                                    className="save-button" 
                                    onClick={() => saveChanges('industries')}
                                >
                                    Save Changes
                                </button>
                            </div>
                        )}
                    </div>

                    <div className="info-text-box">
                        <div className="box-header">
                            <h3>Roles of Interest</h3>
                            <button 
                                className="toggle-edit" 
                                onClick={() => toggleEditMode('roles')}
                            >
                                {editMode.roles ? 'Cancel' : 'Edit'}
                            </button>
                        </div>
                        
                        {!editMode.roles ? (
                            <div className="info-content">
                                <div className="info-item">
                                    <div className="tag-container">
                                        {Array.isArray(userData?.interested_roles) && userData.interested_roles.length > 0 
                                            ? userData.interested_roles.map((role, index) => (
                                                <span key={index} className="tag role-tag">{role}</span>
                                            ))
                                            : <span className="no-data">No roles specified</span>
                                        }
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="edit-form">
                                <div className="form-group">
                                    <label>Roles (comma-separated)</label>
                                    <textarea
                                        name="interested_roles"
                                        value={Array.isArray(formData.interested_roles) 
                                            ? formData.interested_roles.join(', ') 
                                            : formData.interested_roles || ''}
                                        onChange={handleRoleChange}
                                        placeholder="Software Engineer, Data Scientist, Product Manager, etc."
                                    ></textarea>
                                    <p className="help-text">Enter multiple roles separated by commas (e.g., "Machine Learning Engineer, Full Stack Developer")</p>
                                </div>
                                <button 
                                    className="save-button" 
                                    onClick={() => saveChanges('roles')}
                                >
                                    Save Changes
                                </button>
                            </div>
                        )}
                    </div>

                    <div className="info-text-box">
                        <div className="box-header">
                            <h3>Skills</h3>
                            <button 
                                className="toggle-edit" 
                                onClick={() => toggleEditMode('skills')}
                            >
                                {editMode.skills ? 'Cancel' : 'Edit'}
                            </button>
                        </div>
                        
                        {!editMode.skills ? (
                            <div className="info-content">
                                <div className="info-item">
                                    <div className="skills-tag-container">
                                        {userData?.skills && typeof userData.skills === 'object' && Object.keys(userData.skills).length > 0 
                                            ? Object.entries(userData.skills).map(([skill, level], index) => (
                                                <span key={index} className="compact-skill-tag">{skill} <span className="skill-level">({level})</span></span>
                                            ))
                                            : <span className="no-data">No skills added</span>
                                        }
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="edit-form">
                                <div className="form-group">
                                    <label>Skills</label>
                                    <div className="skill-input">
                                        <input 
                                            type="text" 
                                            placeholder="New skill name" 
                                            name="newSkillName"
                                            value={formData.newSkillName || ''}
                                            onChange={handleInputChange}
                                        />
                                        <select 
                                            name="newSkillLevel"
                                            value={formData.newSkillLevel || ''}
                                            onChange={handleInputChange}
                                        >
                                            <option value="">Level</option>
                                            <option value="1">1 - Beginner</option>
                                            <option value="2">2 - Basic</option>
                                            <option value="3">3 - Intermediate</option>
                                            <option value="4">4 - Advanced</option>
                                            <option value="5">5 - Expert</option>
                                        </select>
                                        <button 
                                            className="add-skill-button"
                                            onClick={() => {
                                                if (formData.newSkillName && formData.newSkillLevel) {
                                                    setFormData(prev => ({
                                                        ...prev,
                                                        skills: {
                                                            ...prev.skills,
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
                                    <div className="skills-tag-container">
                                    {formData.skills && typeof formData.skills === 'object' && Object.keys(formData.skills).length > 0 
                                            ? Object.entries(formData.skills).map(([skill, level], index) => (
                                                <div key={index} className="compact-skill-tag">
                                                    {skill}<span className="skill-level">({level})</span>
                                                    <button 
                                                        type="button"
                                                        className="remove-skill-btn"
                                                        onClick={() => {
                                                            const { [skill]: removedSkill, ...remainingSkills } = formData.skills;
                                                            setFormData(prev => ({
                                                                ...prev,
                                                                skills: remainingSkills
                                                            }));
                                                        }}
                                                    >
                                                        ×
                                                    </button>
                                                </div>
                                            ))
                                            : <span className="no-data">No skills added yet</span>
                                        }
                                    </div>
                                </div>
                                <button 
                                    className="save-button" 
                                    onClick={() => saveChanges('skills')}
                                >
                                    Save Changes
                                </button>
                            </div>
                        )}
                    </div>
                </div>

                <div className="action-buttons">
                    <button className="primary-button" onClick={() => navigate('/personalized')}>
                        View Personalized Insights
                    </button>
                    <button className="secondary-button" onClick={() => {
                        localStorage.removeItem('userEmail');
                        navigate('/login');
                    }}>
                        Logout
                    </button>
                </div>
            </section>
        </div>
    );
};

export default AccountPage;