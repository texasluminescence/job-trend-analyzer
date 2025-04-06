import pandas as pd
import re
from collections import Counter

def load_job_data(file_path='filtered_linkedin_jobs.csv'):
    """Load job data from the filtered LinkedIn jobs CSV file"""
    try:
        df = pd.read_csv(file_path)
        print(f"Loaded {len(df)} job listings from {file_path}")
        return df
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return None

def extract_tech_skills(description, tech_skills, special_case_skills):
    """Extract mentioned tech skills from a job description with proper word boundary checks"""
    if not isinstance(description, str):
        return []
    
    description = description.lower()
    mentioned_skills = []
    
    # First handle special case skills that need strict word boundary checks
    for skill in special_case_skills:
        skill_lower = skill.lower()
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        if re.search(pattern, description):
            mentioned_skills.append(skill)
    
    # For other skills, check with more context
    for skill in tech_skills:
        if skill in special_case_skills:
            continue  # Already handled
            
        skill_lower = skill.lower()
        
        # For very short skills, skip unless in special cases
        if len(skill_lower) <= 3 and skill not in special_case_skills:
            continue
            
        # For multi-word skills, check if entire phrase is present
        if " " in skill_lower:
            if skill_lower in description:
                mentioned_skills.append(skill)
        # For single-word skills, check with word boundaries
        else:
            pattern = r'\b' + re.escape(skill_lower) + r'\b'
            if re.search(pattern, description):
                mentioned_skills.append(skill)
    
    return mentioned_skills

def standardize_job_title(title):
    """Standardize job titles to consolidate similar roles"""
    if not isinstance(title, str):
        return "Unknown Role"
        
    # Clean and normalize title
    title = title.lower()
    
    # Remove job IDs, locations and other prefixes
    title = re.sub(r'^#\d+\s*-\s*', '', title)
    title = re.sub(r'\(USA\)\s*', '', title)
    title = re.sub(r'\d{4}\s+', '', title)  # Remove year prefixes like "2025 "
    
    # Pattern-based role standardization
    role_patterns = {
        # Software Engineering roles
        r'(?i)(^|[^\w])(sr\.?\s*|senior\s+|junior\s+|jr\.?\s*|associate\s+|staff\s+)?software\s*(engineer|developer)(\s+i+)?': 'Software Engineer',
        
        # Data Science roles
        r'(?i)(^|[^\w])(sr\.?\s*|senior\s+|junior\s+|jr\.?\s*|associate\s+|staff\s+)?data\s+scientist(\s+i+)?': 'Data Scientist',
        
        # Data Engineering roles
        r'(?i)(^|[^\w])(sr\.?\s*|senior\s+|junior\s+|jr\.?\s*|associate\s+|staff\s+)?data\s+engineer(\s+i+)?': 'Data Engineer',
        
        # Full Stack roles
        r'(?i)(^|[^\w])(full\s*stack|fullstack)(\s+(engineer|developer|web\s*developer))?': 'Full Stack Developer',
        
        # Frontend roles
        r'(?i)(^|[^\w])(front\s*end|frontend)(\s+(engineer|developer|web\s*developer))?': 'Frontend Developer',
        
        # Backend roles
        r'(?i)(^|[^\w])(back\s*end|backend)(\s+(engineer|developer|web\s*developer))?': 'Backend Developer',
        
        # Web Developer roles
        r'(?i)(^|[^\w])(sr\.?\s*|senior\s+|junior\s+|jr\.?\s*)?web\s+(developer|engineer)': 'Web Developer',
        
        # AI/ML Engineering roles
        r'(?i)(^|[^\w])(ai(\s+&\s+|\s+and\s+|\s+)ml|machine\s+learning|artificial\s*intelligence)(\s+(engineer|developer))?': 'AI/ML Engineer',
        
        # Machine Learning roles
        r'(?i)(^|[^\w])(sr\.?\s*|senior\s+|junior\s+|jr\.?\s*|associate\s+|staff\s+)?machine\s+learning(\s+(engineer|scientist))?': 'Machine Learning Engineer',
        
        # Research Scientist roles
        r'(?i)(^|[^\w])(research\s+scientist|ai\s+researcher)': 'Research Scientist',
        
        # Data Analyst roles
        r'(?i)(^|[^\w])(sr\.?\s*|senior\s+|junior\s+|jr\.?\s*|associate\s+)?data\s+analyst': 'Data Analyst',
        
        # DevOps/SRE roles
        r'(?i)(^|[^\w])(devops|site\s+reliability)(\s+engineer)?': 'DevOps Engineer',
        
        # JavaScript/React Developer roles
        r'(?i)(^|[^\w])(react|javascript)(\s+developer|\s+engineer)': 'JavaScript/React Developer',
    }
    
    # Try to match with each pattern
    for pattern, role_name in role_patterns.items():
        if re.search(pattern, title):
            return role_name
    
    # If no specific match, return a cleaned version of the original title
    simplified = re.sub(r'[\(\,].*$', '', title).strip()
    
    # Capitalize properly
    simplified = ' '.join(word.capitalize() if word not in ['and', 'or', 'the', 'in', 'on', 'at', 'for'] 
                     else word for word in simplified.split())
    
    return simplified

def main():
    print("LinkedIn Jobs Skills & Roles Analyzer")
    print("--------------------------------------")
    
    # Load job data
    df = load_job_data()
    if df is None or len(df) == 0:
        print("No job data to analyze.")
        return
    
    # Define tech skills list
    tech_skills = [
        'HTML', 'CSS', 'JavaScript', 'TypeScript', 'React', 'Angular', 'Vue.js', 'jQuery', 'Python',
        'Java', 'C#', 'C++', 'Ruby', 'PHP', 'Swift', 'Kotlin', 'Go', 'Rust', 'SQL', 'PostgreSQL', 
        'MySQL', 'MongoDB', 'Redis', 'AWS', 'Azure', 'Google Cloud Platform', 'Docker', 'Kubernetes',
        'Jenkins', 'Git', 'Linux', 'Node.js', 'Express', 'Django', 'Flask', 'Spring', '.NET',
        'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'AI', 'Artificial Intelligence',
        'Data Science', 'Data Analysis', 'Big Data', 'Hadoop', 'Spark', 'Tableau', 'Power BI',
        'R', 'Scala', 'GraphQL', 'REST API', 'Microservices', 'DevOps', 'CI/CD', 'Agile', 'Scrum',
        'Jira', 'GitHub', 'GitLab', 'Bash', 'PowerShell', 'Object-Oriented Programming', 'OOP',
        'Functional Programming', 'Test-Driven Development', 'TDD', 'Unit Testing', 'Jest',
        'Mocha', 'Cypress', 'Selenium', 'Pandas', 'NumPy', 'SciPy', 'scikit-learn', 'Keras',
        'Natural Language Processing', 'NLP', 'Computer Vision', 'OpenCV', 'Redux', 'Webpack',
        'Babel', 'ESLint', 'Bootstrap', 'Tailwind CSS', 'SASS', 'LESS', 'WebSockets',
        'OAuth', 'JWT', 'SAML', 'Serverless', 'Lambda', 'Terraform', 'Ansible', 'Kafka',
        'Elasticsearch', 'ELK Stack', 'Prometheus', 'Grafana', 'Datadog', 'Splunk',
        'Infrastructure as Code', 'IaC', 'SRE', 'Site Reliability Engineering',
        'Continuous Integration', 'Continuous Deployment', 'Continuous Delivery', 'GitHub Actions',
        'Large Language Models', 'LLM', 'GenAI', 'Generative AI', 'Snowflake', 'Databricks',
        'Docker Compose', 'Kubernetes Helm', 'ETL', 'Data Warehousing', 'Data Engineering',
        'Data Modeling', 'Data Visualization', 'Business Intelligence', 'BI', 'C'
    ]
    
    # Special case skills that need careful word boundary checks
    special_case_skills = ['C', 'R', 'Go', 'D', '.NET', 'J']
    
    # 1. ANALYZE SKILLS
    print("\nAnalyzing tech skills from job descriptions...")
    all_skills = []
    
    for _, row in df.iterrows():
        job_skills = extract_tech_skills(row['job_description'], tech_skills, special_case_skills)
        all_skills.extend(job_skills)
    
    # Count skills
    skill_counts = Counter(all_skills)
    
    # Print the top 10 skills
    print("\nTop 10 Most In-Demand Technical Skills:")
    for i, (skill, count) in enumerate(skill_counts.most_common(10), 1):
        print(f"{i}. {skill}: {count} mentions")
    
    # Save top 10 skills to CSV
    skill_df = pd.DataFrame({
        'Skill': [skill for skill, _ in skill_counts.most_common(10)],
        'Count': [count for _, count in skill_counts.most_common(10)]
    })
    
    skill_output_file = "top_10_skills.csv"
    skill_df.to_csv(skill_output_file, index=False)
    print(f"\nTop 10 skills saved to '{skill_output_file}'")
    
    # 2. ANALYZE JOB ROLES
    print("\nAnalyzing job roles...")
    
    # Standardize job titles
    standardized_titles = [standardize_job_title(title) for title in df['title']]
    
    # Count roles
    role_counts = Counter(standardized_titles)
    
    # Print the top 10 roles
    print("\nTop 10 Most Common Job Roles:")
    for i, (role, count) in enumerate(role_counts.most_common(10), 1):
        print(f"{i}. {role}: {count} positions")
    
    # Save top 10 roles to CSV
    role_df = pd.DataFrame({
        'Job Role': [role for role, _ in role_counts.most_common(10)],
        'Count': [count for _, count in role_counts.most_common(10)]
    })
    
    role_output_file = "top_10_roles.csv"
    role_df.to_csv(role_output_file, index=False)
    print(f"\nTop 10 roles saved to '{role_output_file}'")
    
    print("\nAnalysis completed!")

if __name__ == "__main__":
    main()