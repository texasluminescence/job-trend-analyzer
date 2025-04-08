#!/usr/bin/env python3
"""
Data Aggregation Script for Job Market Analysis

This script processes job data from LinkedIn and Glassdoor CSV files,
extracts relevant information, and populates a MongoDB database with
structured collections for Industries, Roles, Skills, Companies, and JobPostings.
"""

import csv
import re
import pymongo
from pymongo import MongoClient
from datetime import datetime
import os
from collections import Counter, defaultdict
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import spacy
import pandas as pd
from dotenv import load_dotenv

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Load spaCy model for better NLP processing
try:
    nlp = spacy.load("en_core_web_sm")
except:
    print("Downloading spaCy model...")
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Common tech skills for initial extraction (can be expanded)
COMMON_TECH_SKILLS = [
    "python", "java", "javascript", "js", "typescript", "ts", "c++", "c#", "ruby", "php", "swift", 
    "kotlin", "go", "rust", "scala", "dart", "perl", "r", "matlab", "sql", "nosql", "mongodb", 
    "postgresql", "mysql", "oracle", "sql server", "cassandra", "redis", "elasticsearch", 
    "dynamodb", "firebase", "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s",
    "jenkins", "gitlab", "github", "bitbucket", "terraform", "ansible", "puppet", "chef",
    "react", "angular", "vue", "nextjs", "nodejs", "express", "django", "flask", "spring", 
    "laravel", "rails", "asp.net", "html", "css", "sass", "less", "bootstrap", "tailwind",
    "jquery", "redux", "graphql", "rest", "soap", "oauth", "jwt", "machine learning", "ml",
    "artificial intelligence", "ai", "deep learning", "dl", "natural language processing", "nlp",
    "computer vision", "cv", "data science", "big data", "hadoop", "spark", "kafka", "tableau",
    "power bi", "looker", "qlik", "excel", "vba", "linux", "unix", "windows", "macos", "ios", 
    "android", "flutter", "react native", "xamarin", "cordova", "unity", "unreal", "blender",
    "maya", "photoshop", "illustrator", "figma", "sketch", "adobe xd", "ui", "ux", "agile", 
    "scrum", "kanban", "jira", "confluence", "trello", "slack", "teams", "zoom", "git", "svn", 
    "mercurial", "cicd", "devops", "sre", "security", "penetration testing", "pen testing", 
    "ethical hacking", "cybersecurity", "blockchain", "ethereum", "solidity", "smart contracts",
    "crypto", "cryptocurrency", "nft", "web3", "serverless", "microservices", "soa", "apigateway"
]

# Common tech roles
COMMON_TECH_ROLES = [
    "software engineer", "software developer", "frontend developer", "backend developer", 
    "full stack developer", "web developer", "mobile developer", "ios developer", "android developer",
    "data scientist", "data analyst", "data engineer", "machine learning engineer", "ml engineer",
    "ai engineer", "devops engineer", "site reliability engineer", "sre", "cloud engineer",
    "infrastructure engineer", "database administrator", "dba", "system administrator", "sysadmin",
    "network engineer", "security engineer", "cybersecurity analyst", "penetration tester", 
    "ethical hacker", "qa engineer", "quality assurance engineer", "test engineer", "automation engineer",
    "ui developer", "ux designer", "ui/ux designer", "product manager", "project manager", 
    "engineering manager", "technical lead", "tech lead", "scrum master", "agile coach", 
    "business analyst", "solutions architect", "systems architect", "enterprise architect",
    "technical architect", "cto", "cio", "development manager", "it manager", "it director",
    "blockchain developer", "smart contract developer", "game developer", "unity developer",
    "unreal developer", "ar developer", "vr developer", "embedded systems engineer", "iot engineer",
    "firmware engineer", "hardware engineer", "technical writer", "technical support", "help desk"
]

def get_config():
    """Set up configuration for data processing."""
    load_dotenv()

    MONGO_URL = os.getenv("MONGO_URL")
    config = {
        'linkedin': 'machine-learning/linkedin_jobs_filtered.csv',  
        'glassdoor': 'machine-learning/Glassdoor_job_listings_information.csv',  # Path to Glassdoor CSV file
        'mongo_uri': MONGO_URL,
        'db_name': 'Test',
        'industry': 'Tech'
    }
    return config

def connect_to_mongodb(mongo_uri, db_name):
    """Connect to MongoDB and return database object."""
    try:
        client = MongoClient(mongo_uri)
        db = client[db_name]
        print(f"Connected to MongoDB: {db_name}")
        return db
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise

def extract_skills_from_text(text, common_skills=COMMON_TECH_SKILLS):
    """
    Extract skills from job description text using NLP techniques.
    """
    if not text or not isinstance(text, str):
        return []
    
    text = text.lower()
    extracted_skills = []
    
    # Process with spaCy for better entity recognition
    doc = nlp(text)
    
    # Extract skills from common skills list
    for skill in common_skills:
        # Check for exact matches with word boundaries
        skill_pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(skill_pattern, text):
            extracted_skills.append(skill)
    
    # Extract technical terms and frameworks that might be skills
    for ent in doc.ents:
        if ent.label_ in ["PRODUCT", "ORG"] and len(ent.text) > 2:
            candidate = ent.text.lower()
            # Filter out common non-skill entities
            if candidate not in ["company", "organization", "team"] and candidate not in extracted_skills:
                extracted_skills.append(candidate)
    
    # Clean up skills (remove duplicates, standardize names)
    cleaned_skills = []
    skill_mapping = {
        "js": "javascript",
        "ts": "typescript",
        "k8s": "kubernetes",
        "ml": "machine learning",
        "ai": "artificial intelligence",
        "dl": "deep learning",
        "nlp": "natural language processing",
        "cv": "computer vision"
    }
    
    for skill in extracted_skills:
        # Map abbreviations to full names
        if skill in skill_mapping:
            skill = skill_mapping[skill]
        
        if skill not in cleaned_skills:
            cleaned_skills.append(skill)
    
    return cleaned_skills

def extract_role_from_title(title):
    """
    Extract a standardized role from job title.
    """
    if not title or not isinstance(title, str):
        return None
    
    title = title.lower()
    
    # Check for common tech roles
    for role in COMMON_TECH_ROLES:
        if role in title:
            return role.title()  # Return with proper capitalization
    
    # Fall back to basic role categories based on keywords
    if any(keyword in title for keyword in ["software", "developer", "programmer", "coder", "engineer"]):
        return "Software Engineer"
    elif any(keyword in title for keyword in ["data", "analyst", "scientist", "analytics"]):
        return "Data Scientist"
    elif any(keyword in title for keyword in ["web", "frontend", "backend", "full stack", "fullstack"]):
        return "Web Developer"
    elif any(keyword in title for keyword in ["devops", "sre", "reliability", "infrastructure"]):
        return "DevOps Engineer"
    elif any(keyword in title for keyword in ["product", "pm"]):
        return "Product Manager"
    elif any(keyword in title for keyword in ["design", "ui", "ux"]):
        return "UX/UI Designer"
    
    # Default fallback - use the first 3 words of the title
    words = title.split()
    default_title = " ".join(words[:min(3, len(words))])
    return default_title.title()

def process_linkedin_data(file_path, db, industry_name):
    """
    Process LinkedIn CSV data and update MongoDB collections.
    """
    print(f"Processing LinkedIn data from: {file_path}")
    companies_data = {}
    roles_data = {}
    skills_data = {}
    job_postings = []
    
    try:
        df = pd.read_csv(file_path)
        print(f"LinkedIn data loaded with {len(df)} rows")
        
        # Process each job posting
        for index, row in df.iterrows():
            title = row.get('title', '')
            company = row.get('company', '')
            location = row.get('location', '')
            job_url = row.get('job_url', '')
            job_description = row.get('job_description', '')
            date_loaded = row.get('date_loaded', '')
            
            # Skip if missing essential data
            if not title or not company or not job_description:
                continue
            
            # Extract role from job title
            role_name = extract_role_from_title(title)
            
            # Extract skills from job description
            skills = extract_skills_from_text(job_description)
            
            # Update companies data
            if company not in companies_data:
                companies_data[company] = {
                    'name': company,
                    'industry': industry_name,
                    'job_postings': 1,
                    'roles': [role_name] if role_name else [],
                    'locations': [location] if location else []
                }
            else:
                companies_data[company]['job_postings'] += 1
                if role_name and role_name not in companies_data[company]['roles']:
                    companies_data[company]['roles'].append(role_name)
                if location and location not in companies_data[company]['locations']:
                    companies_data[company]['locations'].append(location)
            
            # Update roles data
            if role_name:
                if role_name not in roles_data:
                    roles_data[role_name] = {
                        'role_name': role_name,
                        'industries': [industry_name],
                        'open_positions_count': 1,
                        'top_hiring_companies': [company] if company else [],
                        'required_skills': skills,
                        'description': f"{role_name}s are responsible for {', '.join(skills[:3])} and other technical tasks."
                    }
                else:
                    roles_data[role_name]['open_positions_count'] += 1
                    if company and company not in roles_data[role_name]['top_hiring_companies']:
                        roles_data[role_name]['top_hiring_companies'].append(company)
                    for skill in skills:
                        if skill not in roles_data[role_name]['required_skills']:
                            roles_data[role_name]['required_skills'].append(skill)
            
            # Update skills data
            for skill in skills:
                if skill not in skills_data:
                    skills_data[skill] = {
                        'skill_name': skill,
                        'industries': [industry_name],
                        'job_postings_count': 1,
                        'related_roles': [role_name] if role_name else [],
                        'description': f"{skill.title()} is a technical skill used in {industry_name}.",
                        'learning_resources': []
                    }
                else:
                    skills_data[skill]['job_postings_count'] += 1
                    if role_name and role_name not in skills_data[skill]['related_roles']:
                        skills_data[skill]['related_roles'].append(role_name)
            
            # Create job posting entry
            try:
                posted_date = datetime.strptime(date_loaded, '%Y-%m-%d') if date_loaded else datetime.now()
            except:
                posted_date = datetime.now()
                
            job_posting = {
                'title': title,
                'company': company,
                'role': role_name,
                'location': location,
                'description': job_description,
                'skills_required': skills,
                'url': job_url,
                'posted_date': posted_date,
                'source': 'LinkedIn',
                'industry': industry_name
            }
            job_postings.append(job_posting)
            
    except Exception as e:
        print(f"Error processing LinkedIn data: {e}")
    
    return companies_data, roles_data, skills_data, job_postings

def process_glassdoor_data(file_path, db, industry_name):
    """
    Process Glassdoor CSV data and update MongoDB collections.
    """
    print(f"Processing Glassdoor data from: {file_path}")
    companies_data = {}
    roles_data = {}
    skills_data = {}
    job_postings = []
    
    try:
        df = pd.read_csv(file_path)
        print(f"Glassdoor data loaded with {len(df)} rows")
        
        # Process each job posting
        for index, row in df.iterrows():
            # Extract and clean data from Glassdoor CSV
            company_name = row.get('company_name', '')
            job_title = row.get('job_title', '')
            job_location = row.get('job_location', '')
            job_overview = row.get('job_overview', '')
            company_industry = row.get('company_industry', '')
            company_revenue = row.get('company_revenue', '')
            company_size = row.get('company_size', '')
            company_type = row.get('company_type', '')
            company_rating = row.get('company_rating', '')
            job_application_link = row.get('job_application_link', '')
            company_website = row.get('company_website', '')
            pay_range = row.get('pay_range_glassdoor_est', '')
            pay_median = row.get('pay_median_glassdoor', '')
            
            # Skip if missing essential data
            if not job_title or not company_name or not job_overview:
                continue
            
            # Extract role from job title
            role_name = extract_role_from_title(job_title)
            
            # Extract skills from job overview
            skills = extract_skills_from_text(job_overview)
            
            # Update companies data
            if company_name not in companies_data:
                companies_data[company_name] = {
                    'name': company_name,
                    'industry': company_industry or industry_name,
                    'job_postings': 1,
                    'roles': [role_name] if role_name else [],
                    'locations': [job_location] if job_location else [],
                    'revenue': company_revenue,
                    'size': company_size,
                    'type': company_type,
                    'rating': company_rating,
                    'website': company_website
                }
            else:
                companies_data[company_name]['job_postings'] += 1
                if role_name and role_name not in companies_data[company_name]['roles']:
                    companies_data[company_name]['roles'].append(role_name)
                if job_location and job_location not in companies_data[company_name]['locations']:
                    companies_data[company_name]['locations'].append(job_location)
            
            # Update roles data - similar to LinkedIn processing
            if role_name:
                if role_name not in roles_data:
                    roles_data[role_name] = {
                        'role_name': role_name,
                        'industries': [company_industry or industry_name],
                        'open_positions_count': 1,
                        'top_hiring_companies': [company_name] if company_name else [],
                        'required_skills': skills,
                        'description': f"{role_name}s are responsible for {', '.join(skills[:3]) if skills else 'technical tasks'} in the {company_industry or industry_name} industry.",
                        'salary_range': pay_range,
                        'median_salary': pay_median
                    }
                else:
                    roles_data[role_name]['open_positions_count'] += 1
                    if company_name and company_name not in roles_data[role_name]['top_hiring_companies']:
                        roles_data[role_name]['top_hiring_companies'].append(company_name)
                    if company_industry and company_industry not in roles_data[role_name]['industries']:
                        roles_data[role_name]['industries'].append(company_industry)
                    for skill in skills:
                        if skill not in roles_data[role_name]['required_skills']:
                            roles_data[role_name]['required_skills'].append(skill)
            
            # Update skills data - similar to LinkedIn processing
            for skill in skills:
                if skill not in skills_data:
                    skills_data[skill] = {
                        'skill_name': skill,
                        'industries': [company_industry or industry_name],
                        'job_postings_count': 1,
                        'related_roles': [role_name] if role_name else [],
                        'description': f"{skill.title()} is a technical skill used in {company_industry or industry_name}.",
                        'learning_resources': []
                    }
                else:
                    skills_data[skill]['job_postings_count'] += 1
                    if role_name and role_name not in skills_data[skill]['related_roles']:
                        skills_data[skill]['related_roles'].append(role_name)
                    if company_industry and company_industry not in skills_data[skill]['industries']:
                        skills_data[skill]['industries'].append(company_industry)
            
            # Create job posting entry
            job_posting = {
                'title': job_title,
                'company': company_name,
                'role': role_name,
                'location': job_location,
                'description': job_overview,
                'skills_required': skills,
                'url': job_application_link,
                'posted_date': datetime.now(),  # Glassdoor may not have a posted date
                'source': 'Glassdoor',
                'industry': company_industry or industry_name,
                'salary_range': pay_range,
                'median_salary': pay_median
            }
            job_postings.append(job_posting)
            
    except Exception as e:
        print(f"Error processing Glassdoor data: {e}")
    
    return companies_data, roles_data, skills_data, job_postings

def update_industry_collection(db, industry_name, roles_data, skills_data):
    """
    Update the Industries collection with aggregated data.
    """
    # Get existing industry or create new one
    industry = db.Industries.find_one({"Industry": industry_name})
    
    if not industry:
        industry = {
            "Industry": industry_name,
            "Roles": [],
            "Skills": [],
            "Popular_skills": [],
            "Popular_roles": []
        }
    
    # Get list of roles for this industry
    industry_roles = [role for role, data in roles_data.items()]
    
    # Get list of skills for this industry
    industry_skills = [skill for skill, data in skills_data.items()]
    
    # Calculate popular skills
    skills_count = {skill: data['job_postings_count'] for skill, data in skills_data.items()}
    popular_skills = sorted(skills_count.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Calculate popular roles
    roles_count = {role: data['open_positions_count'] for role, data in roles_data.items()}
    popular_roles = sorted(roles_count.items(), key=lambda x: x[1], reverse=True)[:5]
    
# Calculate median salary for the industry
    median_salaries = []
    salary_ranges = []
    for role, data in roles_data.items():
        if 'median_salary' in data and data['median_salary']:
            try:
                # Extract numeric value from median salary string
                salary_str = str(data['median_salary'])
                # Remove non-numeric characters except decimal point
                salary_cleaned = ''.join(c for c in salary_str if c.isdigit() or c == '.')
                if salary_cleaned:
                    salary_value = float(salary_cleaned)
                    median_salaries.append(salary_value)
            except (ValueError, TypeError):
                pass
            
    if 'salary_range' in data and data['salary_range']:
        salary_ranges.append(data['salary_range'])

    # Calculate industry median salary if we have data
    industry_median_salary = None
    if median_salaries:
        # Calculate the average and round to nearest whole dollar
        industry_median_salary = round(sum(median_salaries) / len(median_salaries))

    # Update industry document
    industry["Roles"] = industry_roles
    industry["Skills"] = industry_skills
    industry["Popular_skills"] = [skill for skill, count in popular_skills]
    industry["Popular_roles"] = [role for role, count in popular_roles]

    # Add salary information
    if industry_median_salary:
        industry["median_salary"] = industry_median_salary
    if salary_ranges:
        industry["salary_ranges"] = salary_ranges[:5]  # Store up to 5 representative ranges
    
    # Upsert industry document
    db.Industries.update_one(
        {"Industry": industry_name},
        {"$set": industry},
        upsert=True
    )
    print(f"Updated industry: {industry_name}")

def update_collections(db, companies_data, roles_data, skills_data, job_postings):
    """
    Update all MongoDB collections with processed data.
    """
    # Update Companies collection
    for company_name, company_data in companies_data.items():
        db.Companies.update_one(
            {"name": company_name},
            {"$set": company_data},
            upsert=True
        )
    print(f"Updated {len(companies_data)} companies")
    
    # Update Roles collection
    for role_name, role_data in roles_data.items():
        # Limit top hiring companies to top 10
        if len(role_data['top_hiring_companies']) > 10:
            role_data['top_hiring_companies'] = role_data['top_hiring_companies'][:10]
        
        # Add ObjectIds for references if needed
        db.Roles.update_one(
            {"role_name": role_name},
            {"$set": role_data},
            upsert=True
        )
    print(f"Updated {len(roles_data)} roles")
    
    # Update Skills collection
    for skill_name, skill_data in skills_data.items():
        # Limit related roles to top 10
        if len(skill_data['related_roles']) > 10:
            skill_data['related_roles'] = skill_data['related_roles'][:10]
        
        db.Skills.update_one(
            {"skill_name": skill_name},
            {"$set": skill_data},
            upsert=True
        )
    print(f"Updated {len(skills_data)} skills")
    
    # Update JobPostings collection
    for job_posting in job_postings:
        db.JobPostings.update_one(
            {
                "title": job_posting['title'],
                "company": job_posting['company'],
                "url": job_posting['url']
            },
            {"$set": job_posting},
            upsert=True
        )
    print(f"Updated {len(job_postings)} job postings")

def main():
    """Main function to process data and update MongoDB."""
    config = get_config()
    
    # Connect to MongoDB
    db = connect_to_mongodb(config['mongo_uri'], config['db_name'])
    
    # Initialize data dictionaries
    all_companies = {}
    all_roles = {}
    all_skills = {}
    all_job_postings = []
    
    # Process LinkedIn data if provided
    if config['linkedin']:
        print(f"Processing LinkedIn data from {config['linkedin']}")
        companies, roles, skills, job_postings = process_linkedin_data(
            config['linkedin'], db, config['industry']
        )
        # Merge data
        all_companies.update(companies)
        all_job_postings.extend(job_postings)
        
        # Merge roles data
        for role, data in roles.items():
            if role in all_roles:
                all_roles[role]['open_positions_count'] += data['open_positions_count']
                all_roles[role]['top_hiring_companies'].extend(data['top_hiring_companies'])
                all_roles[role]['required_skills'].extend(data['required_skills'])
                all_roles[role]['top_hiring_companies'] = list(set(all_roles[role]['top_hiring_companies']))
                all_roles[role]['required_skills'] = list(set(all_roles[role]['required_skills']))
            else:
                all_roles[role] = data
        
        # Merge skills data
        for skill, data in skills.items():
            if skill in all_skills:
                all_skills[skill]['job_postings_count'] += data['job_postings_count']
                all_skills[skill]['related_roles'].extend(data['related_roles'])
                all_skills[skill]['related_roles'] = list(set(all_skills[skill]['related_roles']))
            else:
                all_skills[skill] = data
    
    # Process Glassdoor data if provided
    if config['glassdoor']:
        print(f"Processing Glassdoor data from {config['glassdoor']}")
        companies, roles, skills, job_postings = process_glassdoor_data(
            config['glassdoor'], db, config['industry']
        )
        # Merge data (similar to LinkedIn)
        all_companies.update(companies)
        all_job_postings.extend(job_postings)
        
        # Merge roles data
        for role, data in roles.items():
            if role in all_roles:
                all_roles[role]['open_positions_count'] += data['open_positions_count']
                all_roles[role]['top_hiring_companies'].extend(data['top_hiring_companies'])
                all_roles[role]['required_skills'].extend(data['required_skills'])
                all_roles[role]['top_hiring_companies'] = list(set(all_roles[role]['top_hiring_companies']))
                all_roles[role]['required_skills'] = list(set(all_roles[role]['required_skills']))
                
                # Add salary info if present
                if 'salary_range' in data and data['salary_range']:
                    all_roles[role]['salary_range'] = data['salary_range']
                if 'median_salary' in data and data['median_salary']:
                    all_roles[role]['median_salary'] = data['median_salary']
            else:
                all_roles[role] = data
        
        # Merge skills data
        for skill, data in skills.items():
            if skill in all_skills:
                all_skills[skill]['job_postings_count'] += data['job_postings_count']
                all_skills[skill]['related_roles'].extend(data['related_roles'])
                all_skills[skill]['related_roles'] = list(set(all_skills[skill]['related_roles']))
            else:
                all_skills[skill] = data
    
    # Update industry collection
    update_industry_collection(db, config['industry'], all_roles, all_skills)
    
    # Update all collections with merged data
    update_collections(db, all_companies, all_roles, all_skills, all_job_postings)
    
    print("Data processing and MongoDB updates complete!")

if __name__ == "__main__":
    main()