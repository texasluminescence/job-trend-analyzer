import sys
import pandas as pd
import re
from collections import Counter

print("Starting Tech Skill Extraction and Matching Script...")

if len(sys.argv) != 2:
    print("Usage: python tech_skill_matcher.py <path_to_csv>")
    sys.exit(1)

csv_path = sys.argv[1]

try:
    df = pd.read_csv(csv_path)
    print(f"Successfully loaded CSV file: {csv_path}")
except Exception as e:
    print(f"Error loading CSV file: {e}")
    sys.exit(1)

if 'job_description' not in df.columns or 'title' not in df.columns:
    print("Error: 'job_description' or 'title' column not found in CSV.")
    sys.exit(1)

# Define tech skills list with special handling for ambiguous skills
tech_skills = [
    'HTML', 'CSS', 'JavaScript', 'TypeScript', 'React', 'Angular', 'Vue.js', 'Svelte', 'jQuery', 'Bootstrap', 
    'Tailwind CSS', 'Material UI', 'Redux', 'MobX', 'React Router', 'Webpack', 'Babel', 'ESLint', 'Prettier', 
    'Jest', 'Mocha', 'Chai', 'Enzyme', 'Cypress', 'React Testing Library', 'Selenium', 'Puppeteer', 'Node.js', 
    'Express.js', 'NestJS', 'Fastify', 'Koa', 'Hapi', 'Django', 'Flask', 'Ruby on Rails', 'Laravel', 
    'Spring Boot', 'ASP.NET Core', 'Phoenix', 'FastAPI', 'Symfony', 'CodeIgniter', 'PostgreSQL', 'MySQL', 
    'SQLite', 'Oracle Database', 'Microsoft SQL Server', 'MongoDB', 'Redis', 'Cassandra', 'DynamoDB', 'Firebase', 
    'Elasticsearch', 'Neo4j', 'CouchDB', 'InfluxDB', 'MariaDB', 'RabbitMQ', 'Kafka', 'GraphQL', 'REST API', 
    'SOAP', 'gRPC', 'WebSockets', 'OAuth', 'JWT', 'SAML', 'Microservices', 'Docker', 'Kubernetes', 
    'Docker Compose', 'Podman', 'AWS', 'Azure', 'Google Cloud Platform', 'Heroku', 'DigitalOcean', 'Netlify', 
    'Vercel', 'AWS Lambda', 'Azure Functions', 'Google Cloud Functions', 'AWS S3', 'AWS EC2', 'AWS RDS', 
    'AWS DynamoDB', 'Azure Blob Storage', 'Firebase Hosting', 'GitHub Actions', 'Jenkins', 'CircleCI', 
    'Travis CI', 'TeamCity', 'GitLab CI/CD', 'ArgoCD', 'Ansible', 'Terraform', 'Pulumi', 'CloudFormation', 
    'Chef', 'Puppet', 'Git', 'GitHub', 'GitLab', 'Bitbucket', 'SVN', 'Linux', 'Unix', 'Windows Server', 
    'Bash scripting', 'PowerShell', 'Python', 'Java', 'C#', 'Rust', 'C++', 'PHP', 'Ruby', 'Swift', 
    'Kotlin', 'Scala', 'Elixir', 'Haskell', 'Clojure', 'Groovy', 'Perl', 'Dart', 'Objective-C', 'MATLAB', 
    'Assembly', 'Solidity', 'WebAssembly', 'SQL', 'PL/SQL', 'T-SQL', 'Apache Spark', 'Apache Hadoop', 
    'Apache Airflow', 'Apache Beam', 'Apache Kafka', 'Elasticsearch', 'Logstash', 'Kibana', 'Prometheus', 
    'Grafana', 'Datadog', 'New Relic', 'Splunk', 'Jaeger', 'Zipkin', 'OpenTelemetry', 'Pandas', 'NumPy', 
    'TensorFlow', 'PyTorch', 'scikit-learn', 'Keras', 'NLTK', 'OpenCV', 'Matplotlib', 'Jupyter', 'Dask', 
    'Snowflake', 'BigQuery', 'Redshift', 'Databricks', 'Data Warehousing', 'ETL pipelines', 
    'Continuous Integration', 'Continuous Deployment', 'Infrastructure as Code', 'DevOps', 'SRE', 
    'Agile methodologies', 'Scrum', 'Kanban', 'Test-Driven Development', 'Behavior-Driven Development', 
    'Machine Learning', 'Natural Language Processing', 'Computer Vision', 'AI', 'Artificial Intelligence', 
    'LLM', 'Large Language Models', 'GenAI', 'Generative AI', 'Deep Learning'
]

# Special case skills that need word boundary checks
special_case_skills = ['C', 'R', 'Go', 'D', 'J']

print(f"Tech skills list loaded with {len(tech_skills)} skills.")

# Function to standardize job titles to avoid duplicates
def standardize_title(title):
    if not isinstance(title, str):
        return "Unknown Role"
        
    # Convert to lowercase initially for better matching
    title = title.lower()
    
    # Remove remote/location designations
    title = re.sub(r'\s*-\s*.*remote.*', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\s*\(.*remote.*\)', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\s*remote\s*', '', title, flags=re.IGNORECASE)
    
    # Standardize common variations
    title = title.replace("front-end", "frontend")
    title = title.replace("front end", "frontend")
    title = title.replace("back-end", "backend")
    title = title.replace("back end", "backend")
    title = title.replace("full-stack", "full stack")
    title = title.replace("fullstack", "full stack")
    
    # Create standard categories
    if "software engineer" in title:
        # Handle levels for Software Engineer: collapse level I to default
        if re.search(r'\bii+\b', title):  # Roman numeral II
            title = "software engineer ii"
        elif re.search(r'\biii+\b', title):  # Roman numeral III
            title = "software engineer iii"
        elif "senior" in title or "sr" in title:
            title = "senior software engineer"
        elif "junior" in title or "jr" in title:
            title = "junior software engineer"
        elif "staff" in title or "principal" in title:
            title = "staff software engineer"
        elif "associate" in title:
            title = "associate software engineer"
        else:
            # This covers Software Engineer I and the default case
            title = "software engineer"
    
    elif "data scientist" in title:
        # Handle levels for Data Scientist: collapse level I to default
        if re.search(r'\bii+\b', title):
            title = "data scientist ii"
        elif re.search(r'\biii+\b', title):
            title = "data scientist iii"
        elif "senior" in title or "sr" in title:
            title = "senior data scientist"
        elif "junior" in title or "jr" in title:
            title = "junior data scientist"
        elif "staff" in title or "principal" in title:
            title = "staff data scientist"
        elif "associate" in title:
            title = "associate data scientist"
        else:
            title = "data scientist"
            
    elif "data engineer" in title:
        if re.search(r'\bi+\b', title):
            title = "data engineer"
        elif re.search(r'\bii+\b', title):
            title = "data engineer ii"
        elif re.search(r'\biii+\b', title):
            title = "data engineer iii"
        elif "senior" in title or "sr" in title:
            title = "senior data engineer"
        elif "junior" in title or "jr" in title:
            title = "junior data engineer"
        elif "staff" in title or "principal" in title:
            title = "staff data engineer"
        elif "associate" in title:
            title = "associate data engineer"
        else:
            title = "data engineer"
    
    elif "web developer" in title:
        if "frontend" in title or "front" in title:
            title = "frontend web developer"
        elif "backend" in title or "back" in title:
            title = "backend web developer"
        elif "full stack" in title:
            title = "full stack web developer"
        elif "senior" in title or "sr" in title:
            title = "senior web developer"
        elif "junior" in title or "jr" in title:
            title = "junior web developer"
        else:
            title = "web developer"
    
    elif "machine learning" in title:
        if "senior" in title or "sr" in title:
            title = "senior machine learning engineer"
        elif "junior" in title or "jr" in title:
            title = "junior machine learning engineer"
        elif "scientist" in title:
            title = "machine learning scientist"
        else:
            title = "machine learning engineer"
    
    # Remove trailing commas and what follows
    if "," in title:
        title = title.split(",")[0]
    
    # Remove parenthetical additions except for certain departments
    departments_to_keep = ["orion", "starlink", "components"]
    match = re.search(r'\s*\((.*?)\)', title)
    if match and match.group(1).lower() not in departments_to_keep:
        title = re.sub(r'\s*\(.*?\)', '', title)
    
    # Properly capitalize
    title = ' '.join(word.capitalize() if word not in ['and', 'or', 'the', 'in', 'on', 'at', 'for'] 
                     else word for word in title.split())
    
    return title.strip()

# Apply standardization to job titles
df['standardized_title'] = df['title'].apply(standardize_title)
print(f"Standardized {len(df['title'].unique())} job titles to {len(df['standardized_title'].unique())} unique roles.")

# Function to extract mentioned skills from a job description with proper word boundary handling
def extract_mentioned_skills(description, skill_list, special_cases=special_case_skills):
    if not isinstance(description, str):
        return []
    
    description = description.lower()
    mentioned = []
    
    # First handle special case skills that need word boundary checks
    for skill in special_cases:
        skill_lower = skill.lower()
        # Look for the skill as a whole word
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        if re.search(pattern, description):
            mentioned.append(skill)
    
    # For other skills, check with more context
    for skill in skill_list:
        if skill in special_cases:
            continue  # Already handled
            
        skill_lower = skill.lower()
        
        # For programming languages, frameworks, and tools
        if len(skill_lower) <= 3:  # Very short names need careful handling
            # Skip very short skills already handled in special cases
            continue
            
        # For multi-word skills, check if the entire phrase is present
        if " " in skill_lower:
            if skill_lower in description:
                mentioned.append(skill)
        # For single-word skills, check with word boundaries
        else:
            pattern = r'\b' + re.escape(skill_lower) + r'\b'
            if re.search(pattern, description):
                mentioned.append(skill)
    
    return mentioned

# Extract skills from job descriptions
print("Extracting tech skills from job descriptions...")
df['mentioned_skills'] = df['job_description'].apply(lambda x: extract_mentioned_skills(x, tech_skills))

# Get the most common skills across all job descriptions
all_mentioned_skills = [skill for sublist in df['mentioned_skills'] for skill in sublist]
skill_counts = Counter(all_mentioned_skills)
most_common_skills = skill_counts.most_common(50)

print("\nTop 20 most common tech skills across all job descriptions:")
for skill, count in most_common_skills[:20]:
    print(f"{skill}: {count}")

# Count occurrences of each standardized job title
print("\nFinding the most common job roles...")
role_counts = df['standardized_title'].value_counts()

# Create a DataFrame with the job roles and their counts
role_count_df = pd.DataFrame(role_counts).reset_index()
role_count_df.columns = ['Job Role', 'Count']

# Display the top job roles
print("\nTop 10 most common job roles:")
for role, count in role_count_df.iloc[:10].values:
    print(f"{role}: {count}")

# Save the results to a CSV file
role_count_output = "most_common_job_roles.csv"
role_count_df.to_csv(role_count_output, index=False)
print(f"✅ Most common job roles saved to '{role_count_output}'")

# Function to find the top skills for each standardized job title
def get_top_skills_by_role(df, top_n=5, min_jobs=3):
    role_skills = {}
    
    # Only analyze roles that appear more than min_jobs times
    role_counts = df['standardized_title'].value_counts()
    valid_roles = role_counts[role_counts >= min_jobs].index
    
    for role in valid_roles:
        # Get all job descriptions for this role
        role_df = df[df['standardized_title'] == role]
        
        # Collect all skills mentioned in these job descriptions
        role_skills_list = [skill for sublist in role_df['mentioned_skills'] for skill in sublist]
        
        # Count occurrences of each skill
        role_skill_counts = Counter(role_skills_list)
        
        # Calculate percentage of job postings mentioning each skill
        total_jobs = len(role_df)
        role_skill_percentages = {skill: (count / total_jobs * 100) for skill, count in role_skill_counts.items()}
        
        # Get the top N skills with their percentages
        top_skills_with_pct = [(skill, pct) for skill, pct in 
                              sorted(role_skill_percentages.items(), key=lambda x: x[1], reverse=True)[:top_n]]
        
        # Add to our dictionary
        role_skills[role] = top_skills_with_pct
    
    return role_skills

# Get the top skills for each role
print("\nFinding the top skills for each role...")
role_skills_mapping = get_top_skills_by_role(df, top_n=10, min_jobs=3)

# Create a DataFrame for the results with roles and their top skills
results = []
for role, skills_with_pct in role_skills_mapping.items():
    role_count = len(df[df['standardized_title'] == role])
    skills_formatted = [f"{skill} ({pct:.1f}%)" for skill, pct in skills_with_pct]
    results.append({
        'Role': role,
        'Count': role_count,
        'Top Skills': ', '.join(skills_formatted)
    })

result_df = pd.DataFrame(results)
result_df = result_df.sort_values('Count', ascending=False)

# Save the results to a CSV file
output_file = "role_skills_mapping.csv"
result_df.to_csv(output_file, index=False)
print(f"\n✅ Results saved successfully to '{output_file}'")

# Also output a CSV with the most common skills overall
common_skills_df = pd.DataFrame(most_common_skills, columns=['Skill', 'Count'])
skill_percentage = (common_skills_df['Count'] / len(df) * 100).round(1)
common_skills_df['Percentage'] = skill_percentage.astype(str) + '%'
common_skills_df.to_csv("most_common_skills.csv", index=False)
print(f"✅ Most common skills saved to 'most_common_skills.csv'")

# Check if salary data exists in the dataset
print("\nChecking for salary data...")
salary_columns = [col for col in df.columns if 'salary' in col.lower()]

if not salary_columns:
    print("No salary data found in the dataset.")
else:
    print(f"Found salary column(s): {', '.join(salary_columns)}")
    salary_col = salary_columns[0]  # Use the first salary column found
    
    # Replace the existing clean_salary function with this improved version
    def clean_salary(salary):
        if not isinstance(salary, str) or pd.isna(salary) or salary == 'NA':
            return None
        
        try:
            # Convert to lowercase for consistent detection
            salary_lower = salary.lower()
            
            # Skip nonsensical values
            if any(term in salary_lower for term in ['call', 'contact', 'competitive', 'negotiable']):
                return None
            
            # Determine if hourly or annual
            is_hourly = 'per hour' in salary_lower or 'hourly' in salary_lower
            
            # Extract all numbers from the string
            import re
            numbers = re.findall(r'[\d,]+\.?\d*', salary)
            if not numbers:
                return None
                
            # Clean the extracted numbers
            cleaned_numbers = []
            for num in numbers:
                try:
                    cleaned_numbers.append(float(num.replace(',', '')))
                except ValueError:
                    continue
            
            if not cleaned_numbers:
                return None
                
            # Handle salary ranges
            if len(cleaned_numbers) >= 2:
                # Take the average of the first two numbers (likely a range)
                min_val, max_val = cleaned_numbers[0], cleaned_numbers[1]
                # Ensure min <= max
                if min_val > max_val:
                    min_val, max_val = max_val, min_val
                avg_salary = (min_val + max_val) / 2
            else:
                # Just one number found
                avg_salary = cleaned_numbers[0]
            
            # Sanity check for very low values that are likely hourly rates without explicit "per hour"
            if not is_hourly and avg_salary < 1000:
                is_hourly = True
                
            # Convert hourly to annual (standard 2080 hours per year)
            if is_hourly:
                annual_salary = avg_salary * 2080
            else:
                annual_salary = avg_salary
                
            # Sanity check for reasonable salary range (exclude extreme outliers)
            if annual_salary < 10000 or annual_salary > 1000000:
                return None
                
            return annual_salary
                
        except Exception as e:
            return None

    # Apply the improved salary cleaning function
    df['cleaned_salary'] = df[salary_col].apply(clean_salary)

    # Additional outlier removal for better accuracy
    def remove_salary_outliers(salary_series):
        if len(salary_series) <= 2:
            return salary_series
        
        # Calculate Q1, Q3 and IQR
        Q1 = salary_series.quantile(0.25)
        Q3 = salary_series.quantile(0.75)
        IQR = Q3 - Q1
        
        # Define outlier bounds (more conservative than typical 1.5*IQR)
        lower_bound = max(25000, Q1 - 1.5 * IQR)  # Minimum reasonable salary
        upper_bound = min(400000, Q3 + 1.5 * IQR)  # Maximum reasonable salary
        
        # Filter out outliers
        return salary_series[(salary_series >= lower_bound) & (salary_series <= upper_bound)]

    # Apply outlier removal before analyzing
    print(f"\nBefore outlier removal: {df['cleaned_salary'].dropna().count()} salary data points")
    df['cleaned_salary_filtered'] = df.groupby('standardized_title')['cleaned_salary'].transform(
        lambda x: x if len(x) <= 10 else remove_salary_outliers(x)
    )
    print(f"After outlier removal: {df['cleaned_salary_filtered'].dropna().count()} salary data points")

    # Use the filtered salary for all analysis
    df['cleaned_salary'] = df['cleaned_salary_filtered']
    
    # Calculate salary stats only for non-null values
    salary_data_available = df['cleaned_salary'].notna().sum()
    if salary_data_available > 0:
        print(f"Found {salary_data_available} job postings with valid salary information.")
        
        # 1. Job Role to Salary Mapping
        print("\nAnalyzing salaries by job role...")
        
        role_salary_data = []
        for role, group in df.groupby('standardized_title'):
            valid_salaries = group['cleaned_salary'].dropna()
            
            if len(valid_salaries) >= 3:  # Only include if we have at least 3 data points
                avg_salary = valid_salaries.mean()
                median_salary = valid_salaries.median()
                min_salary = valid_salaries.min()
                max_salary = valid_salaries.max()
                
                role_salary_data.append({
                    'Job Role': role,
                    'Count': len(valid_salaries),
                    'Average Salary': round(avg_salary, 2),
                    'Median Salary': round(median_salary, 2),
                    'Min Salary': round(min_salary, 2),
                    'Max Salary': round(max_salary, 2)
                })
        
        # Create and save DataFrame
        if role_salary_data:
            role_salary_df = pd.DataFrame(role_salary_data)
            role_salary_df = role_salary_df.sort_values('Count', ascending=False)
            
            # Display top roles by salary
            print("\nTop 10 roles by average salary:")
            top_by_salary = role_salary_df.sort_values('Average Salary', ascending=False).head(10)
            for _, row in top_by_salary.iterrows():
                print(f"{row['Job Role']}: ${row['Average Salary']:,.2f} (based on {row['Count']} postings)")
            
            # Save to CSV
            role_salary_file = "job_roles_by_salary.csv"
            role_salary_df.to_csv(role_salary_file, index=False)
            print(f"✅ Job roles with salary data saved to '{role_salary_file}'")
        else:
            print("Not enough salary data to analyze by job role.")
        
        # 2. Skills to Salary Mapping
        print("\nAnalyzing salaries by skill...")
        
        skill_salary_data = []
        # Get list of all unique skills
        all_skills = set(skill for sublist in df['mentioned_skills'] for skill in sublist)
        
        for skill in all_skills:
            # Find all jobs that mention this skill
            skill_jobs = df[df['mentioned_skills'].apply(lambda x: skill in x)]
            
            # Get valid salaries for these jobs
            valid_salaries = skill_jobs['cleaned_salary'].dropna()
            
            if len(valid_salaries) >= 3:  # Only include if we have at least 3 data points
                avg_salary = valid_salaries.mean()
                median_salary = valid_salaries.median()
                job_count = len(valid_salaries)
                
                skill_salary_data.append({
                    'Skill': skill,
                    'Job Count': job_count,
                    'Average Salary': round(avg_salary, 2),
                    'Median Salary': round(median_salary, 2)
                })
        
        # Create and save DataFrame
        if skill_salary_data:
            skill_salary_df = pd.DataFrame(skill_salary_data)
            skill_salary_df = skill_salary_df.sort_values('Job Count', ascending=False)
            
            # Display top skills by salary
            print("\nTop 15 skills by average salary:")
            # Only consider skills that appear in at least 10 job postings
            frequent_skills = skill_salary_df[skill_salary_df['Job Count'] >= 10]
            top_by_salary = frequent_skills.sort_values('Average Salary', ascending=False).head(15)
            for _, row in top_by_salary.iterrows():
                print(f"{row['Skill']}: ${row['Average Salary']:,.2f} (based on {row['Job Count']} postings)")
            
            # Save to CSV
            skill_salary_file = "skills_by_salary.csv"
            skill_salary_df.to_csv(skill_salary_file, index=False)
            print(f"✅ Skills with salary data saved to '{skill_salary_file}'")
        else:
            print("Not enough salary data to analyze by skill.")
    else:
        print("No valid salary information found in the dataset after cleaning.")

# Create visualizations if data is available
print("\nGenerating visualizations based on the collected data...")

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    import os
    
    # Create a directory for the visualizations
    viz_dir = "visualizations"
    os.makedirs(viz_dir, exist_ok=True)
    
    # Set a consistent style for all plots
    sns.set_style("whitegrid")
    plt.rcParams.update({'font.size': 12})
    
    # 1. Top Skills Visualization
    plt.figure(figsize=(12, 8))
    top_skills_df = common_skills_df.head(15)
    sns.barplot(x='Count', y='Skill', data=top_skills_df, palette='viridis')
    plt.title('Top 15 Most In-Demand Tech Skills')
    plt.tight_layout()
    plt.savefig(f"{viz_dir}/top_skills.png", dpi=300)
    plt.close()
    print(f"✅ Created visualization: {viz_dir}/top_skills.png")
    
    # 2. Top Job Roles Visualization
    plt.figure(figsize=(12, 8))
    top_roles_df = role_count_df.head(15)
    sns.barplot(x='Count', y='Job Role', data=top_roles_df, palette='magma')
    plt.title('Top 15 Most Common Job Roles')
    plt.tight_layout()
    plt.savefig(f"{viz_dir}/top_job_roles.png", dpi=300)
    plt.close()
    print(f"✅ Created visualization: {viz_dir}/top_job_roles.png")
    
    # 3. Salary Data Visualizations (if available)
    if 'role_salary_df' in locals() and len(role_salary_df) > 0:
        # Top Paying Roles
        plt.figure(figsize=(12, 8))
        top_paying_roles = role_salary_df.sort_values('Average Salary', ascending=False).head(10)
        sns.barplot(x='Average Salary', y='Job Role', data=top_paying_roles, palette='rocket')
        plt.title('Top 10 Highest Paying Tech Roles')
        plt.xlabel('Average Annual Salary ($)')
        formatter = plt.FuncFormatter(lambda x, p: f'${x:,.0f}')
        plt.gca().xaxis.set_major_formatter(formatter)
        plt.tight_layout()
        plt.savefig(f"{viz_dir}/top_paying_roles.png", dpi=300)
        plt.close()
        print(f"✅ Created visualization: {viz_dir}/top_paying_roles.png")
        
        # Salary vs Job Count
        plt.figure(figsize=(10, 8))
        # Only include roles with sufficient data
        common_roles = role_salary_df[role_salary_df['Count'] >= 5].copy()
        common_roles['Role Label'] = common_roles['Job Role'] + ' (n=' + common_roles['Count'].astype(str) + ')'
        
        plt.scatter(
            common_roles['Average Salary'], 
            common_roles['Count'],
            s=common_roles['Count']*3,  # Size by count
            alpha=0.7,
            c=common_roles['Average Salary'],  # Color by salary
            cmap='viridis'
        )
        
        # Add labels for top roles
        for _, row in common_roles.nlargest(8, 'Count').iterrows():
            plt.annotate(
                row['Job Role'],
                xy=(row['Average Salary'], row['Count']),
                xytext=(5, 5),
                textcoords='offset points',
                fontsize=9
            )
            
        plt.title('Job Popularity vs. Average Salary')
        plt.xlabel('Average Annual Salary ($)')
        plt.ylabel('Number of Job Postings')
        formatter = plt.FuncFormatter(lambda x, p: f'${x:,.0f}')
        plt.gca().xaxis.set_major_formatter(formatter)
        plt.tight_layout()
        plt.savefig(f"{viz_dir}/salary_vs_popularity.png", dpi=300)
        plt.close()
        print(f"✅ Created visualization: {viz_dir}/salary_vs_popularity.png")
    
    # 4. Skills by Salary (if available)
    if 'skill_salary_df' in locals() and len(skill_salary_df) > 0:
        plt.figure(figsize=(12, 8))
        # Filter to skills with significant data
        top_paid_skills = skill_salary_df[skill_salary_df['Job Count'] >= 20].sort_values('Average Salary', ascending=False).head(15)
        sns.barplot(x='Average Salary', y='Skill', data=top_paid_skills, palette='crest')
        plt.title('Top 15 Highest Paying Tech Skills (Minimum 20 Job Postings)')
        plt.xlabel('Average Annual Salary ($)')
        formatter = plt.FuncFormatter(lambda x, p: f'${x:,.0f}')
        plt.gca().xaxis.set_major_formatter(formatter)
        plt.tight_layout()
        plt.savefig(f"{viz_dir}/top_paying_skills.png", dpi=300)
        plt.close()
        print(f"✅ Created visualization: {viz_dir}/top_paying_skills.png")
    
    # 5. Create a skill matrix for top roles and skills
    if 'role_skills_mapping' in locals():
        # Get top roles and top skills
        top_roles = role_count_df.head(10)['Job Role'].tolist()
        top_skills_list = common_skills_df.head(15)['Skill'].tolist()
        
        # Build a matrix of skill prevalence across roles
        heatmap_data = []
        for role in top_roles:
            # Get the role's skill data
            role_data = next((data for r, data in role_skills_mapping.items() if r == role), [])
            
            # Map skills to percentages
            role_skill_dict = {skill: pct for skill, pct in role_data}
            
            # Create row for this role
            row = [role_skill_dict.get(skill, 0) for skill in top_skills_list]
            heatmap_data.append(row)
        
        # Create a DataFrame for the heatmap
        heatmap_df = pd.DataFrame(heatmap_data, index=top_roles, columns=top_skills_list)
        
        # Create heatmap
        plt.figure(figsize=(14, 10))
        sns.heatmap(heatmap_df, annot=True, fmt='.0f', cmap='YlGnBu', cbar_kws={'label': '% of Job Postings'})
        plt.title('Top Skills Required Across Popular Tech Roles')
        plt.tight_layout()
        plt.savefig(f"{viz_dir}/skills_by_role_heatmap.png", dpi=300)
        plt.close()
        print(f"✅ Created visualization: {viz_dir}/skills_by_role_heatmap.png")
    
    print(f"\nAll visualizations saved to the '{viz_dir}' directory.")
    
except ImportError:
    print("Visualizations could not be created. Please install matplotlib and seaborn libraries.")
except Exception as e:
    print(f"Error creating visualizations: {e}")

# Final success message
print("\nTech Skill Extraction and Matching Completed Successfully!")