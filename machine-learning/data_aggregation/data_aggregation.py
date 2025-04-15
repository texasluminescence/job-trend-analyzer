#!/usr/bin/env python3
"""
Enhanced Data Aggregation Script for Job Market Analysis

This script processes job data from LinkedIn and Glassdoor CSV files,
extracts relevant information, and populates a MongoDB database with
structured collections for Industries, Roles, Skills, Companies, and JobPostings.
Now with enhanced salary analysis and visualization capabilities.
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
import numpy as np
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import seaborn as sns

# Download necessary NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# Load spaCy model for better NLP processing
try:
    nlp = spacy.load("en_core_web_sm")
except:
    print("Downloading spaCy model...")
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

INVALID_SKILL_TERMS = {
    "con edison", "con edison of", "coop", "co-op", "internship", "intern", "work study",
    "summer internship", "research assistant", "graduate assistant", "student", "education",
    "project", "team", "collaboration", "communication", "resume", "linkedin", "email",
    "writing", "microsoft", "google", "apple", "amazon", "meta", "problem solving",
    "school", "university", "volunteer", "training", "learning", "class", "lecture",
    "campus", "leadership", "presentation", "organization", "detail-oriented", "motivation",
    "hardworking", "job", "employment", "assistant", "associate"
}

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

# Function to standardize job titles (from paste-2.txt)
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

# Salary cleaning function from paste-2.txt
def clean_salary(salary):
    """Extract and clean salary information from text"""
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

def remove_salary_outliers(salary_series):
    """Remove outliers from a series of salary values"""
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

def get_config():
    """Set up configuration for data processing."""
    load_dotenv()

    MONGO_URL = os.getenv("MONGO_URL")
    config = {
        'linkedin': 'machine-learning/linkedin_jobs_filtered.csv',  
        'glassdoor': 'machine-learning/Glassdoor_job_listings_information.csv',  # Path to Glassdoor CSV file
        'mongo_uri': MONGO_URL,
        'db_name': 'Test',
        'industry': 'Tech',
        'output_dir': 'job_market_analysis'  # Directory for output files/visualizations
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
    """Enhanced skill extraction with better NLP capabilities."""
    if not text or not isinstance(text, str):
        print("WARNING: Empty or non-string input to extract_skills_from_text")
        return []
    
    text = text.lower()
    extracted_skills = set()  # Using a set for faster lookups and to avoid duplicates
    extracted_skills_with_confidence = {}  # Store skills with confidence score
    
    # Process with spaCy for better entity recognition

    doc = nlp(text)
    
    # Define skill context indicators - words that suggest a term is a skill
    skill_indicators = [
        'experience', 'skill', 'knowledge', 'proficiency', 'familiar', 'working with',
        'expertise', 'proficient', 'competent', 'trained in', 'certified', 'background in',
        'understanding of', 'ability to use', 'ability to work with', 'hands-on', 'exposure to'
    ]
    
    # Define words to ignore as skills - generic terms
    generic_terms = [
        'software', 'programming', 'language', 'framework', 'library', 'platform', 'tool',
        'environment', 'development', 'engineer', 'engineering', 'solution', 'system', 'quality',
        'knowledge', 'experience', 'proficiency', 'familiar', 'ability', 'skill', 'expertise',
        'proficient', 'competent', 'trained', 'certified', 'background', 'understanding', 
        'hands-on', 'exposure', 'working', 'with', 'using', 'utilize', 'implementation',
        'developing', 'designing', 'building', 'creating', 'writing', 'coding', 'implementing',
        'supporting', 'maintaining', 'troubleshooting', 'debugging', 'testing', 'deploying',
        'managing', 'leading', 'directing', 'coordinating', 'organizing'
    ]
    
    # 1. Extract skills from common skills list with confidence scoring

    for skill in common_skills:
        # Check for exact matches with word boundaries
        skill_pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(skill_pattern, text, re.IGNORECASE):
            # Calculate confidence score based on context and frequency
            confidence = 0
            matches = list(re.finditer(skill_pattern, text, re.IGNORECASE))
            
            # More mentions = higher confidence (capped at 3)
            confidence += min(len(matches), 3)
            
            # Check context around each mention
            has_skill_context = False
            for match in matches:
                start, end = match.span()
                # Get context (up to 75 chars before and after)
                context_start = max(0, start - 75)
                context_end = min(len(text), end + 75)
                context = text[context_start:context_end]
                
                # Check if it's used in a skill context
                if any(indicator in context for indicator in skill_indicators):
                    has_skill_context = True
                    confidence += 2
                    break
            
            # Store the skill with its confidence score
            if skill not in extracted_skills_with_confidence or confidence > extracted_skills_with_confidence[skill]:
                extracted_skills_with_confidence[skill] = confidence
                extracted_skills.add(skill)
    
    # 2. Extract technical entities and products (using spaCy)
    
    for ent in doc.ents:
        if ent.label_ in ["PRODUCT", "ORG"] and len(ent.text) > 2:
            candidate = ent.text.lower()
            
            # Filter out common non-skill entities and check it's not just a generic term
            if (candidate not in ["company", "organization", "team", "staff", "employee", "employer"] and
                candidate not in extracted_skills and
                not any(generic in candidate for generic in generic_terms)):
                
                # Check if it's a technology name
                confidence = 1
                context_start = max(0, ent.start_char - 75)
                context_end = min(len(text), ent.end_char + 75)
                context = text[context_start:context_end]
                
                if any(indicator in context for indicator in skill_indicators):
                    confidence += 2
                
                extracted_skills_with_confidence[candidate] = confidence
                extracted_skills.add(candidate)
    
    # 3. Look for additional technical skills beyond the common list
    # Look for specific technical patterns like X.js, X++ frameworks, etc.
    tech_patterns = [
        (r'\b[A-Za-z][\w-]*\.js\b', "JavaScript library/framework"),
        (r'\b[A-Za-z][\w-]*\+\+\b', "Programming language"),
        (r'\b[A-Za-z][\w-]*SQL\b', "Database technology"),
        (r'\b[A-Za-z][\w-]*DB\b', "Database technology"),
        (r'\b[A-Za-z][\w-]*lang\b', "Programming language")
    ]
    
    for pattern, category in tech_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            tech_name = match.group(0).lower()
            if tech_name not in extracted_skills:
                extracted_skills_with_confidence[tech_name] = 2  # Good confidence for pattern matches
                extracted_skills.add(tech_name)
    
    # 4. Extract specific technical skills from probable skill sections
    skill_section_patterns = [
        r'(?:technical skills|skills & expertise|technologies|tech stack)(?:[\s:]+)(.*?)(?:\n\n|\n\w+:|$)',
        r'(?:experience|expertise) (?:with|in)(?:[\s:]+)(.*?)(?:\.|$)',
        r'(?:proficiency|proficient) (?:with|in)(?:[\s:]+)(.*?)(?:\.|$)',
        r'(?:requirements|qualifications)(?:[\s:]*)(.*?)(?:\n\n|\n\w+:|$)'
    ]
    
    for pattern in skill_section_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            skill_section = match.group(1).lower()
            # Look for comma or bullet separated lists in these sections
            for skill_phrase in re.split(r',|\n|•|-|;|\|', skill_section):
                skill_phrase = skill_phrase.strip()
                if 2 <= len(skill_phrase.split()) <= 3 and skill_phrase and not any(generic == skill_phrase for generic in generic_terms):
                    # Check if it contains at least one technical indicator
                    if any(tech_word in skill_phrase for tech_word in ["framework", "language", "stack", "api", "sdk", "library"]):
                        extracted_skills_with_confidence[skill_phrase] = 2
                        extracted_skills.add(skill_phrase)
    
    # 5. SPECIAL STEP: Direct check for explicitly mentioned skills
    # This step ensures we don't miss important skills due to regex issues

    critical_skills = [
    "c++", "c#", ".net", "asp.net", "node.js", "vue.js", "react.js", 
    "typescript", "javascript", "python", "java", "golang", "ruby",
    "tensorflow", "pytorch", "opencv", "docker", "kubernetes", "aws",
    "azure", "gcp", "sql", "nosql", "mongodb", "postgresql", 
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
    
    # Add variations of skills with special characters
    variations = {
        "c++": ["c plus plus", "cplusplus", "c-plus-plus"],
        "c#": ["c sharp", "csharp", "c-sharp"],
        "node.js": ["node js", "nodejs"],
        "vue.js": ["vue js", "vuejs"],
        "react.js": ["react js", "reactjs"]
    }
    
    for skill in critical_skills:
        # Check for the skill itself
        if skill.lower() in text.lower():
            if skill not in extracted_skills:
                extracted_skills.add(skill)
                extracted_skills_with_confidence[skill] = 3  # High confidence for explicit mentions
                            
        # Check for variations if they exist
        if skill in variations:
            for variant in variations[skill]:
                if variant.lower() in text.lower():
                    if skill not in extracted_skills:
                        extracted_skills.add(skill)
                        extracted_skills_with_confidence[skill] = 3
    
    # 6. Skill mapping and normalization
    
    cleaned_skills = []
    skill_mapping = {
        "js": "javascript",
        "ts": "typescript",
        "k8s": "kubernetes",
        "ml": "machine learning",
        "ai": "artificial intelligence",
        "dl": "deep learning",
        "nlp": "natural language processing",
        "cv": "computer vision",
        "react.js": "react",
        "reactjs": "react",
        "vue.js": "vue",
        "node.js": "nodejs",
        "golang": "go",
        "dotnet": ".net",
        "postgres": "postgresql",
        "aws cloud": "aws",
        "amazon web services": "aws",
        "microsoft azure": "azure",
        "google cloud platform": "gcp",
        "tensorflow": "tensorflow",
        "opencv": "opencv",
        "c plus plus": "c++",
        "cplusplus": "c++",
        "c-plus-plus": "c++",
        "c sharp": "c#",
        "csharp": "c#",
        "c-sharp": "c#",
        "objective c": "objective-c",
        "objective-c": "objective-c",
        "gcp": "google cloud",
        "rest api development": "api development",
        "api-development": "api development",
        "api": "api development"
    }
    
    # Add plural to singular mapping
    plural_mapping = {}
    for skill in common_skills:
        if skill.endswith('s') and skill[:-1] in common_skills:
            plural_mapping[skill] = skill[:-1]
        elif not skill.endswith('s'):
            plural_mapping[f"{skill}s"] = skill
    
    skill_mapping.update(plural_mapping)
    
    # Sort skills by confidence score
    sorted_skills = sorted(
        [(skill, score) for skill, score in extracted_skills_with_confidence.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    # Keep only skills with sufficient confidence or that are in common skills list
    for skill, confidence in sorted_skills:
        if confidence >= 2 or skill in common_skills:
            # Map abbreviations and variants to standard names
            mapped_skill = skill_mapping.get(skill, skill)
            
            # Filter out skills that are just generic terms
            if mapped_skill not in generic_terms and len(mapped_skill) > 1:
                if mapped_skill not in cleaned_skills:
                    cleaned_skills.append(mapped_skill)

    cleaned_skills = [s for s in cleaned_skills if s.lower() not in INVALID_SKILL_TERMS]
    return cleaned_skills

def extract_role_from_title(title):
    """
    Extract a standardized role from job title using the improved standardize_title function.
    """
    if not title or not isinstance(title, str):
        return None
    
    return standardize_title(title)

def process_job_data(file_path, source_name, db, industry_name):
    """
    Process job data from a CSV file (LinkedIn or Glassdoor) and extract relevant information.
    This is a unified function that handles both sources with source-specific adaptations.
    """
    print(f"Processing {source_name} data from: {file_path}")
    
    companies_data = {}
    roles_data = {}
    skills_data = {}
    job_postings = []
    salary_data = []
    
    try:
        # Load the data
        df = pd.read_csv(file_path)
        print(f"{source_name} data loaded with {len(df)} rows")
        
        # Map column names based on source
        if source_name.lower() == 'linkedin':
            col_map = {
                'title': 'title',
                'company': 'company',
                'location': 'location',
                'description': 'job_description',
                'url': 'job_url',
                'date': 'date_loaded',
                'salary': 'salary'
            }
        else:  # Glassdoor
            col_map = {
                'title': 'job_title',
                'company': 'company_name',
                'location': 'job_location',
                'description': 'job_overview',
                'url': 'job_application_link',
                'date': None,
                'salary': 'pay_range_glassdoor_est',
                'median_salary': 'pay_median_glassdoor',
                'company_industry': 'company_industry',
                'company_revenue': 'company_revenue',
                'company_size': 'company_size',
                'company_type': 'company_type',
                'company_rating': 'company_rating',
                'company_website': 'company_website'
            }
        
        # Standardize job titles
        df['standardized_title'] = df[col_map['title']].apply(standardize_title)
        
        # Process salary information if available
        salary_col = col_map.get('salary')
        median_salary_col = col_map.get('median_salary')
        
        if salary_col and salary_col in df.columns:
            df['cleaned_salary'] = df[salary_col].apply(clean_salary)
            df['cleaned_salary_filtered'] = df.groupby('standardized_title')['cleaned_salary'].transform(
                lambda x: x if len(x) <= 10 else remove_salary_outliers(x)
            )
            df['cleaned_salary'] = df['cleaned_salary_filtered']
        
        # Process each job posting
        for _, row in df.iterrows():
            title = row.get(col_map['title'], '')
            company = row.get(col_map['company'], '')
            location = row.get(col_map['location'], '')
            description = row.get(col_map['description'], '')
            job_url = row.get(col_map['url'], '')
            
            if not title or not company or not description:
                continue
            
            role_name = row.get('standardized_title')
            
            # Extract skills
            skills = extract_skills_from_text(description)
            
            # Get salary information
            salary_info = None
            salary_range = None
            median_salary = None
            
            if 'cleaned_salary' in df.columns:
                salary_info = row.get('cleaned_salary')
            
            if salary_col and salary_col in df.columns:
                salary_range = row.get(salary_col)
            
            if median_salary_col and median_salary_col in df.columns:
                median_salary = row.get(median_salary_col)
            
            # Get company industry (Glassdoor specific)
            company_industry = None
            if 'company_industry' in col_map and col_map['company_industry'] in df.columns:
                company_industry = row.get(col_map['company_industry'])
            
            # Determine if the job is tech-related
            is_tech_job = False
            if role_name and any(tech_role.lower() in role_name.lower() for tech_role in COMMON_TECH_ROLES):
                is_tech_job = True
            elif skills and any(skill.lower() in [s.lower() for s in COMMON_TECH_SKILLS] for skill in skills):
                is_tech_job = True
            
            # Assign industry: prioritize "Tech" for tech-related jobs
            if is_tech_job:
                final_industry = "Tech"
            else:
                final_industry = company_industry or industry_name
            
            # For salary analysis
            if salary_info:
                salary_data.append({
                    'role': role_name,
                    'company': company,
                    'skills': skills,
                    'salary': salary_info
                })
            
            # Update companies data
            if company not in companies_data:
                company_entry = {
                    'name': company,
                    'industry': final_industry,
                    'job_postings': 1,
                    'roles': [role_name] if role_name else [],
                    'locations': [location] if location else []
                }
                
                if source_name.lower() == 'glassdoor':
                    if 'company_revenue' in col_map and col_map['company_revenue'] in df.columns:
                        company_entry['revenue'] = row.get(col_map['company_revenue'])
                    if 'company_size' in col_map and col_map['company_size'] in df.columns:
                        company_entry['size'] = row.get(col_map['company_size'])
                    if 'company_type' in col_map and col_map['company_type'] in df.columns:
                        company_entry['type'] = row.get(col_map['company_type'])
                    if 'company_rating' in col_map and col_map['company_rating'] in df.columns:
                        company_entry['rating'] = row.get(col_map['company_rating'])
                    if 'company_website' in col_map and col_map['company_website'] in df.columns:
                        company_entry['website'] = row.get(col_map['company_website'])
                
                companies_data[company] = company_entry
            else:
                companies_data[company]['job_postings'] += 1
                if role_name and role_name not in companies_data[company]['roles']:
                    companies_data[company]['roles'].append(role_name)
                if location and location not in companies_data[company]['locations']:
                    companies_data[company]['locations'].append(location)
            
            # Update roles data
            if role_name:
                if role_name not in roles_data:
                    role_entry = {
                        'role_name': role_name,
                        'industries': [final_industry],
                        'open_positions_count': 1,
                        'top_hiring_companies': [company] if company else [],
                        'required_skills': skills,
                        'description': f"{role_name}s are responsible for {', '.join(skills[:3]) if skills else 'technical tasks'} and other technical tasks."
                    }
                    
                    if salary_range:
                        role_entry['salary_range'] = salary_range
                    if median_salary:
                        role_entry['median_salary'] = median_salary
                    if salary_info:
                        role_entry['calculated_salary'] = salary_info
                    
                    roles_data[role_name] = role_entry
                else:
                    roles_data[role_name]['open_positions_count'] += 1
                    if company and company not in roles_data[role_name]['top_hiring_companies']:
                        roles_data[role_name]['top_hiring_companies'].append(company)
                    if final_industry and final_industry not in roles_data[role_name]['industries']:
                        roles_data[role_name]['industries'].append(final_industry)
                    for skill in skills:
                        if skill not in roles_data[role_name]['required_skills']:
                            roles_data[role_name]['required_skills'].append(skill)
                    
                    if salary_info and 'salary_data' not in roles_data[role_name]:
                        roles_data[role_name]['salary_data'] = [salary_info]
                    elif salary_info and 'salary_data' in roles_data[role_name]:
                        roles_data[role_name]['salary_data'].append(salary_info)
            
            # Update skills data
            for skill in skills:
                if skill not in skills_data:
                    skill_entry = {
                        'skill_name': skill,
                        'industries': [final_industry],
                        'job_postings_count': 1,
                        'related_roles': [role_name] if role_name else [],
                        'description': f"{skill.title()} is a technical skill used in {final_industry}.",
                        'learning_resources': []
                    }
                    
                    if salary_info:
                        skill_entry['salary_data'] = [salary_info]
                    
                    skills_data[skill] = skill_entry
                else:
                    skills_data[skill]['job_postings_count'] += 1
                    if role_name and role_name not in skills_data[skill]['related_roles']:
                        skills_data[skill]['related_roles'].append(role_name)
                    if final_industry and final_industry not in skills_data[skill]['industries']:
                        skills_data[skill]['industries'].append(final_industry)
                    
                    if salary_info:
                        if 'salary_data' not in skills_data[skill]:
                            skills_data[skill]['salary_data'] = [salary_info]
                        else:
                            skills_data[skill]['salary_data'].append(salary_info)
            
            # Create job posting entry
            try:
                if col_map['date'] and col_map['date'] in df.columns:
                    date_str = row.get(col_map['date'], '')
                    posted_date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.now()
                else:
                    posted_date = datetime.now()
            except:
                posted_date = datetime.now()
                
            job_posting = {
                'title': title,
                'standardized_title': role_name,
                'company': company,
                'role': role_name,
                'location': location,
                'description': description,
                'skills_required': skills,
                'url': job_url,
                'posted_date': posted_date,
                'source': source_name,
                'industry': final_industry
            }
            
            if salary_range:
                job_posting['salary_range'] = salary_range
            if median_salary:
                job_posting['median_salary'] = median_salary
            if salary_info:
                job_posting['calculated_salary'] = salary_info
                
            job_postings.append(job_posting)
            
    except Exception as e:
        print(f"Error processing {source_name} data: {e}")
    
    return companies_data, roles_data, skills_data, job_postings, salary_data

def process_linkedin_data(file_path, db, industry_name):
    """
    Process LinkedIn CSV data and update MongoDB collections.
    Now using the unified processing function.
    """
    return process_job_data(file_path, 'LinkedIn', db, industry_name)

def process_glassdoor_data(file_path, db, industry_name):
    """
    Process Glassdoor CSV data and update MongoDB collections.
    Now using the unified processing function.
    """
    return process_job_data(file_path, 'Glassdoor', db, industry_name)

def calculate_salary_metrics(salary_data):
    """
    Calculate salary metrics from collected salary data.
    Returns dictionaries for role_salary_metrics and skill_salary_metrics.
    """
    # Create DataFrame from collected salary data
    salary_df = pd.DataFrame(salary_data)
    
    # Initialize result dictionaries
    role_salary_metrics = {}
    skill_salary_metrics = {}
    
    # Calculate metrics by role
    for role, group in salary_df.groupby('role'):
        salaries = group['salary'].dropna()
        if len(salaries) >= 3:  # Only calculate metrics if we have enough data points
            role_salary_metrics[role] = {
                'count': len(salaries),
                'min': salaries.min(),
                'max': salaries.max(),
                'mean': salaries.mean(),
                'median': salaries.median(),
                'p25': salaries.quantile(0.25),
                'p75': salaries.quantile(0.75)
            }
    
    # Calculate metrics by skill
    # Explode the skills column to get one row per skill per job
    exploded_df = salary_df.explode('skills')
    exploded_df = exploded_df[exploded_df['skills'].notna()]  # Remove rows with NA skills
    
    for skill, group in exploded_df.groupby('skills'):
        salaries = group['salary'].dropna()
        if len(salaries) >= 3:  # Only calculate if we have enough data points
            skill_salary_metrics[skill] = {
                'count': len(salaries),
                'min': salaries.min(),
                'max': salaries.max(),
                'mean': salaries.mean(),
                'median': salaries.median(),
                'p25': salaries.quantile(0.25),
                'p75': salaries.quantile(0.75)
            }
    
    return role_salary_metrics, skill_salary_metrics

def update_industry_collection(db, industry_name, roles_data, skills_data, role_salary_metrics=None):
    """
    Update the Industries collection with aggregated data.
    Now includes salary information.
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
    
    # 1. Traditional approach from original script
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
        
        # Also include calculated salary values if available
        if 'salary_data' in data and data['salary_data']:
            for salary in data['salary_data']:
                if salary and isinstance(salary, (int, float)):
                    median_salaries.append(salary)
            
        if 'salary_range' in data and data['salary_range']:
            salary_ranges.append(data['salary_range'])
    
    if role_salary_metrics:
        for role, metrics in role_salary_metrics.items():
            if metrics.get('median'):
                median_salaries.append(metrics['median'])
            
    industry_median_salary = None
    industry_avg_salary = None
    if median_salaries:
        # Filter out any NaN values before calculating median and mean
        filtered_salaries = [s for s in median_salaries if not (isinstance(s, float) and np.isnan(s))]
        
        if filtered_salaries:  # Only calculate if we have valid values after filtering
            # Calculate the median and round to nearest whole dollar
            industry_median_salary = round(np.median(filtered_salaries))
            industry_avg_salary = round(np.mean(filtered_salaries))
        
    # Update industry document
    industry["Roles"] = industry_roles
    industry["Skills"] = industry_skills
    industry["Popular_skills"] = [skill for skill, count in popular_skills]
    industry["Popular_roles"] = [role for role, count in popular_roles]

    # Add salary information
    if industry_median_salary:
        industry["median_salary"] = industry_median_salary
    if industry_avg_salary:
        industry["average_salary"] = industry_avg_salary
    if salary_ranges:
        industry["salary_ranges"] = salary_ranges[:5]  # Store up to 5 representative ranges
    
    # Add popular skills with salary information
    if role_salary_metrics:
        top_paying_roles = sorted(
            [r for r in role_salary_metrics.keys() if r in industry_roles],
            key=lambda r: role_salary_metrics[r]['median'],
            reverse=True
        )[:5]
        
        industry["top_paying_roles"] = [{
            "role": role,
            "median_salary": role_salary_metrics[role]['median'],
            "average_salary": role_salary_metrics[role]['mean']
        } for role in top_paying_roles]
    
    # Upsert industry document
    db.Industries.update_one(
        {"Industry": industry_name},
        {"$set": industry},
        upsert=True
    )
    print(f"Updated industry: {industry_name}")

def update_collections(db, companies_data, roles_data, skills_data, job_postings, role_salary_metrics=None, skill_salary_metrics=None):
    """
    Update all MongoDB collections with processed data.
    Now includes additional salary metrics.
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
        
        # Add additional salary metrics if available
        if role_salary_metrics and role_name in role_salary_metrics:
            metrics = role_salary_metrics[role_name]
            role_data['salary_metrics'] = {
                'count': metrics['count'],
                'min': metrics['min'],
                'max': metrics['max'],
                'mean': metrics['mean'],
                'median': metrics['median'],
                'p25': metrics['p25'],
                'p75': metrics['p75']
            }
            
            # Also update main salary fields if not already set
            if not role_data.get('median_salary') and 'median' in metrics:
                role_data['median_salary'] = metrics['median']
            if not role_data.get('salary_range') and 'min' in metrics and 'max' in metrics:
                role_data['salary_range'] = f"${metrics['min']:,.0f} - ${metrics['max']:,.0f}"
        
        # Calculate salary statistics from raw data if available
        if 'salary_data' in role_data and role_data['salary_data']:
            salaries = [s for s in role_data['salary_data'] if s is not None]
            if len(salaries) >= 3:
                if 'salary_metrics' not in role_data:
                    role_data['salary_metrics'] = {}
                
                role_data['salary_metrics']['raw_data'] = {
                    'count': len(salaries),
                    'min': min(salaries),
                    'max': max(salaries),
                    'mean': sum(salaries) / len(salaries),
                    'median': sorted(salaries)[len(salaries) // 2]
                }
                
                # Remove raw salary data after calculations to save space
                role_data.pop('salary_data', None)
        
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
        
        # Add salary metrics if available
        if skill_salary_metrics and skill_name in skill_salary_metrics:
            metrics = skill_salary_metrics[skill_name]
            skill_data['salary_metrics'] = {
                'count': metrics['count'],
                'min': metrics['min'],
                'max': metrics['max'],
                'mean': metrics['mean'],
                'median': metrics['median'],
                'p25': metrics['p25'],
                'p75': metrics['p75']
            }
        
        # Calculate salary statistics from raw data if available
        if 'salary_data' in skill_data and skill_data['salary_data']:
            salaries = [s for s in skill_data['salary_data'] if s is not None]
            if len(salaries) >= 3:
                if 'salary_metrics' not in skill_data:
                    skill_data['salary_metrics'] = {}
                
                skill_data['salary_metrics']['raw_data'] = {
                    'count': len(salaries),
                    'min': min(salaries),
                    'max': max(salaries),
                    'mean': sum(salaries) / len(salaries),
                    'median': sorted(salaries)[len(salaries) // 2]
                }
                
                # Remove raw salary data after calculations to save space
                skill_data.pop('salary_data', None)
        
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
    
    # Create a new SalaryAnalysis collection for aggregated salary data
    if role_salary_metrics or skill_salary_metrics:
        # Store top paying roles
        if role_salary_metrics:
            top_roles = sorted(
                role_salary_metrics.items(), 
                key=lambda x: x[1]['median'] if 'median' in x[1] else 0, 
                reverse=True
            )[:20]  # Store top 20 highest paying roles
            
            for role, metrics in top_roles:
                db.SalaryAnalysis.update_one(
                    {"type": "role", "name": role},
                    {"$set": {
                        "type": "role",
                        "name": role,
                        "metrics": metrics
                    }},
                    upsert=True
                )
        
        # Store top paying skills
        if skill_salary_metrics:
            # Only consider skills with significant data
            significant_skills = {k: v for k, v in skill_salary_metrics.items() if v.get('count', 0) >= 5}
            
            top_skills = sorted(
                significant_skills.items(),
                key=lambda x: x[1]['median'] if 'median' in x[1] else 0,
                reverse=True
            )[:20]  # Store top 20 highest paying skills
            
            for skill, metrics in top_skills:
                db.SalaryAnalysis.update_one(
                    {"type": "skill", "name": skill},
                    {"$set": {
                        "type": "skill",
                        "name": skill,
                        "metrics": metrics
                    }},
                    upsert=True
                )
        
        print("Created/updated SalaryAnalysis collection with top paying roles and skills")

def generate_visualizations(config, role_salary_metrics, skill_salary_metrics, all_roles, all_skills):
    """
    Generate and save visualizations based on the processed data.
    """
    # Create output directory if it doesn't exist
    output_dir = config.get('output_dir', 'job_market_analysis')
    viz_dir = os.path.join(output_dir, 'visualizations')
    os.makedirs(viz_dir, exist_ok=True)
    
    print(f"Generating visualizations in {viz_dir}...")
    
    # Set visualization style
    sns.set_style("whitegrid")
    plt.rcParams.update({'font.size': 12})
    
    # 1. Top 15 Roles by Job Count
    try:
        roles_by_count = {role: data['open_positions_count'] for role, data in all_roles.items()}
        roles_df = pd.DataFrame(list(roles_by_count.items()), columns=['Role', 'Count'])
        roles_df = roles_df.sort_values('Count', ascending=False).head(15)
        
        plt.figure(figsize=(12, 8))
        sns.barplot(x='Count', y='Role', data=roles_df, palette='viridis')
        plt.title('Top 15 Most In-Demand Roles')
        plt.tight_layout()
        plt.savefig(os.path.join(viz_dir, 'top_roles_by_demand.png'), dpi=300)
        plt.close()
        print(f"✅ Created visualization: top_roles_by_demand.png")
    except Exception as e:
        print(f"Error creating top roles visualization: {e}")
    
    # 2. Top 15 Skills by Job Count
    try:
        skills_by_count = {skill: data['job_postings_count'] for skill, data in all_skills.items()}
        skills_df = pd.DataFrame(list(skills_by_count.items()), columns=['Skill', 'Count'])
        skills_df = skills_df.sort_values('Count', ascending=False).head(15)
        
        plt.figure(figsize=(12, 8))
        sns.barplot(x='Count', y='Skill', data=skills_df, palette='magma')
        plt.title('Top 15 Most In-Demand Skills')
        plt.tight_layout()
        plt.savefig(os.path.join(viz_dir, 'top_skills_by_demand.png'), dpi=300)
        plt.close()
        print(f"✅ Created visualization: top_skills_by_demand.png")
    except Exception as e:
        print(f"Error creating top skills visualization: {e}")
    
    # 3. Top 15 Highest Paying Roles
    if role_salary_metrics:
        try:
            # Only include roles with sufficient data
            significant_roles = {k: v for k, v in role_salary_metrics.items() if v.get('count', 0) >= 3}
            
            # Create DataFrame with salary metrics
            salary_rows = []
            for role, metrics in significant_roles.items():
                salary_rows.append({
                    'Role': role,
                    'Median Salary': metrics.get('median', 0),
                    'Count': metrics.get('count', 0)
                })
            
            salary_df = pd.DataFrame(salary_rows)
            top_salary_df = salary_df.sort_values('Median Salary', ascending=False).head(15)
            
            plt.figure(figsize=(12, 8))
            bars = sns.barplot(x='Median Salary', y='Role', data=top_salary_df, palette='rocket')
            
            # Add count annotations to bars
            for i, (_, row) in enumerate(top_salary_df.iterrows()):
                bars.text(row['Median Salary'] + 1000, i, f"n={row['Count']}", va='center')
                
            plt.title('Top 15 Highest Paying Roles')
            plt.xlabel('Median Annual Salary ($)')
            formatter = plt.FuncFormatter(lambda x, p: f'${x:,.0f}')
            plt.gca().xaxis.set_major_formatter(formatter)
            plt.tight_layout()
            plt.savefig(os.path.join(viz_dir, 'top_roles_by_salary.png'), dpi=300)
            plt.close()
            print(f"✅ Created visualization: top_roles_by_salary.png")
        except Exception as e:
            print(f"Error creating roles by salary visualization: {e}")
    
    # 4. Top 15 Highest Paying Skills
    if skill_salary_metrics:
        try:
            # Only include skills with significant data
            significant_skills = {k: v for k, v in skill_salary_metrics.items() if v.get('count', 0) >= 5}
            
            # Create DataFrame with salary metrics
            skill_rows = []
            for skill, metrics in significant_skills.items():
                skill_rows.append({
                    'Skill': skill,
                    'Median Salary': metrics.get('median', 0),
                    'Count': metrics.get('count', 0)
                })
            
            skill_salary_df = pd.DataFrame(skill_rows)
            top_skill_salary_df = skill_salary_df.sort_values('Median Salary', ascending=False).head(15)
            
            plt.figure(figsize=(12, 8))
            bars = sns.barplot(x='Median Salary', y='Skill', data=top_skill_salary_df, palette='crest')
            
            # Add count annotations to bars
            for i, (_, row) in enumerate(top_skill_salary_df.iterrows()):
                bars.text(row['Median Salary'] + 1000, i, f"n={row['Count']}", va='center')
                
            plt.title('Top 15 Highest Paying Skills (Minimum 5 Data Points)')
            plt.xlabel('Median Annual Salary ($)')
            formatter = plt.FuncFormatter(lambda x, p: f'${x:,.0f}')
            plt.gca().xaxis.set_major_formatter(formatter)
            plt.tight_layout()
            plt.savefig(os.path.join(viz_dir, 'top_skills_by_salary.png'), dpi=300)
            plt.close()
            print(f"✅ Created visualization: top_skills_by_salary.png")
        except Exception as e:
            print(f"Error creating skills by salary visualization: {e}")
    
    # 5. Salary Range Distribution
    if role_salary_metrics:
        try:
            # Collect all salary values across roles
            all_salaries = []
            for metrics in role_salary_metrics.values():
                if 'median' in metrics:
                    all_salaries.append(metrics['median'])
            
            if all_salaries:
                plt.figure(figsize=(10, 6))
                sns.histplot(all_salaries, bins=20, kde=True)
                plt.title('Distribution of Median Salaries Across Tech Roles')
                plt.xlabel('Annual Salary ($)')
                plt.ylabel('Number of Roles')
                formatter = plt.FuncFormatter(lambda x, p: f'${x:,.0f}')
                plt.gca().xaxis.set_major_formatter(formatter)
                plt.tight_layout()
                plt.savefig(os.path.join(viz_dir, 'salary_distribution.png'), dpi=300)
                plt.close()
                print(f"✅ Created visualization: salary_distribution.png")
        except Exception as e:
            print(f"Error creating salary distribution visualization: {e}")
    
    # 6. Export data to CSV for further analysis
    try:
        # Create CSVs directory
        csv_dir = os.path.join(output_dir, 'csv_data')
        os.makedirs(csv_dir, exist_ok=True)
        
        # Export role salary data
        if role_salary_metrics:
            role_salary_rows = []
            for role, metrics in role_salary_metrics.items():
                row = {
                    'Role': role,
                    'Count': metrics.get('count', 0),
                    'Min Salary': metrics.get('min', 0),
                    'Max Salary': metrics.get('max', 0),
                    'Mean Salary': metrics.get('mean', 0),
                    'Median Salary': metrics.get('median', 0),
                    'P25 Salary': metrics.get('p25', 0),
                    'P75 Salary': metrics.get('p75', 0)
                }
                role_salary_rows.append(row)
            
            role_salary_df = pd.DataFrame(role_salary_rows)
            role_salary_df.to_csv(os.path.join(csv_dir, 'role_salary_data.csv'), index=False)
            print(f"✅ Exported role salary data to CSV")
        
        # Export skill salary data
        if skill_salary_metrics:
            skill_salary_rows = []
            for skill, metrics in skill_salary_metrics.items():
                if metrics.get('count', 0) >= 3:  # Only include skills with sufficient data
                    row = {
                        'Skill': skill,
                        'Count': metrics.get('count', 0),
                        'Min Salary': metrics.get('min', 0),
                        'Max Salary': metrics.get('max', 0),
                        'Mean Salary': metrics.get('mean', 0),
                        'Median Salary': metrics.get('median', 0),
                        'P25 Salary': metrics.get('p25', 0),
                        'P75 Salary': metrics.get('p75', 0)
                    }
                    skill_salary_rows.append(row)
            
            skill_salary_df = pd.DataFrame(skill_salary_rows)
            skill_salary_df.to_csv(os.path.join(csv_dir, 'skill_salary_data.csv'), index=False)
            print(f"✅ Exported skill salary data to CSV")
        
        # Export roles by demand
        roles_df.to_csv(os.path.join(csv_dir, 'top_roles_by_demand.csv'), index=False)
        
        # Export skills by demand  
        skills_df.to_csv(os.path.join(csv_dir, 'top_skills_by_demand.csv'), index=False)
        
        print(f"✅ All data exported to CSV files in {csv_dir}")
    except Exception as e:
        print(f"Error exporting data to CSV: {e}")
    
    return viz_dir

def main():
    """Main function to process data and update MongoDB."""
    config = get_config()
    
    # Create output directory
    output_dir = config.get('output_dir', 'job_market_analysis')
    os.makedirs(output_dir, exist_ok=True)
    
    # Connect to MongoDB
    db = connect_to_mongodb(config['mongo_uri'], config['db_name'])

    db.Skills.drop()
    db.JobPostings.drop()
    db.Roles.drop()
    db.Industries.drop()
    db.SalaryAnalysis.drop()
    db.Companies.drop()

    
    # Initialize data dictionaries
    all_companies = {}
    all_roles = {}
    all_skills = {}
    all_job_postings = []
    all_salary_data = []
    
    # Process LinkedIn data if provided
    if config['linkedin']:
        print(f"Processing LinkedIn data from {config['linkedin']}")
        companies, roles, skills, job_postings, salary_data = process_linkedin_data(
            config['linkedin'], db, config['industry']
        )
        # Merge data
        all_companies.update(companies)
        all_job_postings.extend(job_postings)
        all_salary_data.extend(salary_data)
        
        # Merge roles data
        for role, data in roles.items():
            if role in all_roles:
                all_roles[role]['open_positions_count'] += data['open_positions_count']
                all_roles[role]['top_hiring_companies'].extend(data['top_hiring_companies'])
                all_roles[role]['required_skills'].extend(data['required_skills'])
                all_roles[role]['top_hiring_companies'] = list(set(all_roles[role]['top_hiring_companies']))
                all_roles[role]['required_skills'] = list(set(all_roles[role]['required_skills']))
                
                # Merge salary data if present
                if 'salary_data' in data:
                    if 'salary_data' not in all_roles[role]:
                        all_roles[role]['salary_data'] = []
                    all_roles[role]['salary_data'].extend(data['salary_data'])
            else:
                all_roles[role] = data
        
        # Merge skills data
        for skill, data in skills.items():
            if skill in all_skills:
                all_skills[skill]['job_postings_count'] += data['job_postings_count']
                all_skills[skill]['related_roles'].extend(data['related_roles'])
                all_skills[skill]['related_roles'] = list(set(all_skills[skill]['related_roles']))
                
                # Merge salary data if present
                if 'salary_data' in data:
                    if 'salary_data' not in all_skills[skill]:
                        all_skills[skill]['salary_data'] = []
                    all_skills[skill]['salary_data'].extend(data['salary_data'])
            else:
                all_skills[skill] = data
    
    # Process Glassdoor data if provided
    if config['glassdoor']:
        print(f"Processing Glassdoor data from {config['glassdoor']}")
        companies, roles, skills, job_postings, salary_data = process_glassdoor_data(
            config['glassdoor'], db, config['industry']
        )
        # Merge data (similar to LinkedIn)
        all_companies.update(companies)
        all_job_postings.extend(job_postings)
        all_salary_data.extend(salary_data)
        
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
                    
                # Merge salary data if present
                if 'salary_data' in data:
                    if 'salary_data' not in all_roles[role]:
                        all_roles[role]['salary_data'] = []
                    all_roles[role]['salary_data'].extend(data['salary_data'])
            else:
                all_roles[role] = data
        
        # Merge skills data
        for skill, data in skills.items():
            if skill in all_skills:
                all_skills[skill]['job_postings_count'] += data['job_postings_count']
                all_skills[skill]['related_roles'].extend(data['related_roles'])
                all_skills[skill]['related_roles'] = list(set(all_skills[skill]['related_roles']))
                
                # Merge salary data if present
                if 'salary_data' in data:
                    if 'salary_data' not in all_skills[skill]:
                        all_skills[skill]['salary_data'] = []
                    all_skills[skill]['salary_data'].extend(data['salary_data'])
            else:
                all_skills[skill] = data
    
    # Calculate salary metrics if we have salary data
    role_salary_metrics = None
    skill_salary_metrics = None
    if all_salary_data:
        print(f"Calculating salary metrics from {len(all_salary_data)} data points...")
        role_salary_metrics, skill_salary_metrics = calculate_salary_metrics(all_salary_data)
        print(f"Generated salary metrics for {len(role_salary_metrics)} roles and {len(skill_salary_metrics)} skills")
    
    # Update industry collection with salary metrics
    update_industry_collection(db, config['industry'], all_roles, all_skills, role_salary_metrics)
    
    # Update all collections with merged data
    update_collections(db, all_companies, all_roles, all_skills, all_job_postings, 
                      role_salary_metrics, skill_salary_metrics)
    
    # Generate visualizations if requested
    viz_dir = None
    if config.get('generate_visualizations', True):
        viz_dir = generate_visualizations(config, role_salary_metrics, skill_salary_metrics, all_roles, all_skills)
    
    print("Data processing and MongoDB updates complete!")
    
    # Return path to visualization directory if generated
    if viz_dir:
        print(f"Visualizations available in: {viz_dir}")

if __name__ == "__main__":
    import argparse
    
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Job Market Data Aggregation with Salary Analysis')
    parser.add_argument('--linkedin', help='Path to LinkedIn CSV file')
    parser.add_argument('--glassdoor', help='Path to Glassdoor CSV file')
    parser.add_argument('--industry', default='Tech', help='Industry name (default: Tech)')
    parser.add_argument('--output', default='job_market_analysis', help='Output directory for visualizations and CSVs')
    parser.add_argument('--no-viz', action='store_true', help='Skip visualization generation')
    
    args = parser.parse_args()
    
    # Override config with command line arguments if provided
    if args.linkedin or args.glassdoor or args.industry or args.output or args.no_viz:
        config = get_config()
        if args.linkedin:
            config['linkedin'] = args.linkedin
        if args.glassdoor:
            config['glassdoor'] = args.glassdoor
        if args.industry:
            config['industry'] = args.industry
        if args.output:
            config['output_dir'] = args.output
        if args.no_viz:
            config['generate_visualizations'] = False
            
        # Connect to MongoDB and run the main processing
        db = connect_to_mongodb(config['mongo_uri'], config['db_name'])
        main()
    else:
        # Run with default configuration
        main()