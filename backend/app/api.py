from datetime import datetime
import math
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import bcrypt
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# # Load .env file
load_dotenv()

# MongoDB setup
MONGO_URL = os.getenv("MONGO_URL")
client = MongoClient(MONGO_URL)
db = client["Test"]

industries_collection = db["Industries"]
roles_collection = db["Roles"]
skills_collection = db["Skills"]
companies_collection = db["Companies"]
job_postings_collection = db["JobPostings"]
users_collection = db["Users"]

# Pydantic model for request validation
class User(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    education_level: str
    graduation_date: str
    degree: str
    industries: list
    yoe: int
    skills: dict
    type_of_work: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Routes
@app.post("/user/")
def add_user(user: User):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    user_dict = user.dict()
    user_dict["password"] = hashed_password.decode('utf-8')
    result = users_collection.insert_one(user_dict )
    return {"id": str(result.inserted_id)}


# Setting up function to enable login (users credentials are input (email) verify that the encrypted password in DB matches password inputted when encrypted)
# If it does, approve login
# Returns true/false or also could return user information depending on implementation
@app.post("/login/")
def login(login_data: LoginRequest) -> bool:
    found_user = users_collection.find_one({"email": login_data.email})
    if not found_user:
        raise HTTPException(status_code=404, detail="User not found")

    stored_hashed_password = found_user["password"].encode('utf-8')
    if bcrypt.checkpw(login_data.password.encode('utf-8'), stored_hashed_password):
        return {"login": True}
    return {"login": False}

# Input is users email address, returns information about user to display on profile page/be used for ML functions
# Uses email address to index into DB
# returns user info
@app.get("/user/")
def get_user(email: str) -> User:
    user = users_collection.find_one()
    return user.dict()

@app.get("/top_jobs/")
def get_top_jobs() -> List[str]:
    # make a call to job model that returns most popular jobs for your industry
    # we might store these in a DB and only refresh them with the model every 15 days
    # returns a list of jobs
    return ['job #1']

@app.get("/top_skills/")
def get_top_skills() -> List[str]:
    # make a call to skill model to get top skills for industry to display
    # returns a list of skills
    return ['skill #1']


@app.get("/users/")
def get_users():
    users = []
    for user in users_collection.find():
        user["_id"] = str(user["_id"])
        users.append(user)
    return {"data": users}

@app.get("/data")
async def get_data():
    df = pd.read_csv("backend/app/data/postings.csv")
    return df.to_dict(orient="records")

@app.get("/industries/{industry_name}")
def get_industry(industry_name: str):
    """
    Get industry details including popular roles.
    """
    industry = industries_collection.find_one({"name": {"$regex": f"^{industry_name}$", "$options": "i"}})
    
    if not industry:
        raise HTTPException(status_code=404, detail="Industry not found")

    industry["_id"] = str(industry["_id"])
    
    return industry
# Models for response validation
class Industry(BaseModel):
    Industry: str
    Roles: List[str] = []
    Skills: List[str] = []
    Popular_skills: List[str] = []
    Popular_roles: List[str] = []

class RoleDetail(BaseModel):
    role_name: str
    industries: List[str] = []
    open_positions_count: int = 0
    top_hiring_companies: List[str] = []
    required_skills: List[str] = []
    description: str = ""
    salary_range: Optional[str] = None
    median_salary: Optional[str] = None

class JobPostingResponse(BaseModel):
    title: str
    company: str
    role: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    skills: List[str] = []
    matching_skills_count: Optional[int] = None
    total_skills_count: Optional[int] = None
    match_score: Optional[float] = None
    salary_range: Optional[str] = None
    posting_url: Optional[str] = None
    industry: Optional[str] = None
    posted_date: Optional[str] = None
    
    class Config:
        extra = "allow"  # Allow extra fields not defined in the model

class SkillDetail(BaseModel):
    skill_name: str
    industries: List[str] = []
    job_postings_count: int = 0
    related_roles: List[str] = []
    description: str = ""
    learning_resources: List[str] = []

class CompanyDetail(BaseModel):
    name: str
    industry: str = ""
    job_postings: int = 0
    roles: List[str] = []
    locations: List[str] = []
    revenue: Optional[str] = None
    size: Optional[str] = None
    type: Optional[str] = None
    rating: Optional[float] = None
    website: Optional[str] = None

class IndustryMetrics(BaseModel):
    job_count: int = 0
    company_count: int = 0
    skill_count: int = 0
    average_salary: Optional[str] = None
    top_locations: List[str] = []

@app.get("/")
def read_root():
    return {"message": "Welcome to the Job Market API"}

@app.get("/industries")
def get_all_industries():
    """
    Get list of all available industries.
    """
    industries = industries_collection.find({}, {"Industry": 1})
    return [{"name": industry["Industry"], "_id": str(industry["_id"])} for industry in industries]

@app.get("/popular-roles")
def get_popular_roles(industry: str = Query(..., description="Industry to get popular roles for")):
    """
    Get popular roles for a specific industry.
    """
    industry_doc = industries_collection.find_one({"Industry": {"$regex": f"^{industry}$", "$options": "i"}})
    
    if not industry_doc or "Popular_roles" not in industry_doc:
        raise HTTPException(status_code=404, detail="Industry or popular roles not found")
    
    return industry_doc["Popular_roles"]

@app.get("/popular-skills")
def get_popular_skills(industry: str = Query(..., description="Industry to get popular skills for")):
    """
    Get popular skills for a specific industry.
    """
    industry_doc = industries_collection.find_one({"Industry": {"$regex": f"^{industry}$", "$options": "i"}})
    
    if not industry_doc or "Popular_skills" not in industry_doc:
        raise HTTPException(status_code=404, detail="Industry or popular skills not found")
    
    return industry_doc["Popular_skills"]

# New enhanced endpoints
@app.get("/industries/{industry_name}", response_model=Dict[str, Any])
def get_industry_details(industry_name: str):
    """
    Get comprehensive details about a specific industry.
    """
    industry = industries_collection.find_one({"Industry": {"$regex": f"^{industry_name}$", "$options": "i"}})
    
    if not industry:
        raise HTTPException(status_code=404, detail="Industry not found")
    
    # Convert ObjectId to string for JSON serialization
    industry["_id"] = str(industry["_id"])
    
    return industry

@app.get("/roles/{role_name}", response_model=Dict[str, Any])
def get_role_details(role_name: str):
    """
    Get detailed information about a specific role.
    """
    role = roles_collection.find_one({"role_name": {"$regex": f"^{role_name}$", "$options": "i"}})
    
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    role["_id"] = str(role["_id"])
    return role

@app.get("/skills/{skill_name}", response_model=Dict[str, Any])
def get_skill_details(skill_name: str):
    """
    Get detailed information about a specific skill.
    """
    skill = skills_collection.find_one({"skill_name": {"$regex": f"^{skill_name}$", "$options": "i"}})
    
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    skill["_id"] = str(skill["_id"])
    return skill

@app.get("/companies/{company_name}", response_model=Dict[str, Any])
def get_company_details(company_name: str):
    """
    Get detailed information about a specific company.
    """
    company = companies_collection.find_one({"name": {"$regex": f"^{company_name}$", "$options": "i"}})
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    company["_id"] = str(company["_id"])
    return company

@app.get("/detailed-popular-roles", response_model=List[Dict[str, Any]])
def get_detailed_popular_roles(industry: str = Query(..., description="Industry to get popular roles for")):
    """
    Get detailed information about popular roles for a specific industry.
    """
    # Get the industry document which contains the list of popular roles
    industry_doc = industries_collection.find_one({"Industry": {"$regex": f"^{industry}$", "$options": "i"}})
    
    if not industry_doc or "Popular_roles" not in industry_doc:
        raise HTTPException(status_code=404, detail="Industry or popular roles not found")
    
    # Get the role names from the industry document
    role_names = industry_doc["Popular_roles"]
    
    # Get detailed information for each role
    detailed_roles = []
    for role_name in role_names:
        role = roles_collection.find_one({"role_name": {"$regex": f"^{role_name}$", "$options": "i"}})
        if role:
            role["_id"] = str(role["_id"])
            # For backward compatibility with frontend
            role["title"] = role["role_name"]
            role["roles"] = role.get("open_positions_count", "N/A")
            
            # Format top hiring companies for display
            if "top_hiring_companies" in role and role["top_hiring_companies"]:
                role["companies"] = ", ".join(role["top_hiring_companies"][:5])  # Limit to 5 for display
            else:
                role["companies"] = "Various companies"
                
            detailed_roles.append(role)
        else:
            # If detailed information not found, create a minimal entry
            detailed_roles.append({
                "title": role_name,
                "role_name": role_name,
                "roles": "N/A",
                "companies": "Various companies"
            })
    
    return detailed_roles

@app.get("/detailed-popular-skills", response_model=List[Dict[str, Any]])
def get_detailed_popular_skills(industry: str = Query(..., description="Industry to get popular skills for")):
    """
    Get detailed information about popular skills for a specific industry.
    """
    # Get the industry document which contains the list of popular skills
    industry_doc = industries_collection.find_one({"Industry": {"$regex": f"^{industry}$", "$options": "i"}})
    
    if not industry_doc or "Popular_skills" not in industry_doc:
        raise HTTPException(status_code=404, detail="Industry or popular skills not found")
    
    # Get the skill names from the industry document
    skill_names = industry_doc["Popular_skills"]
    
    # Get detailed information for each skill
    detailed_skills = []
    for skill_name in skill_names:
        skill = skills_collection.find_one({"skill_name": {"$regex": f"^{skill_name}$", "$options": "i"}})
        if skill:
            skill["_id"] = str(skill["_id"])
            # For backward compatibility with frontend
            skill["skill"] = skill["skill_name"]
            
            # Format related roles for display
            if "related_roles" in skill and skill["related_roles"]:
                skill["jobs"] = ", ".join(skill["related_roles"][:5])  # Limit to 5 for display
            else:
                skill["jobs"] = "Various positions"
                
            skill["number"] = skill.get("job_postings_count", "N/A")
            detailed_skills.append(skill)
        else:
            # If detailed information not found, create a minimal entry
            detailed_skills.append({
                "skill": skill_name,
                "skill_name": skill_name,
                "jobs": "Various positions",
                "number": "N/A"
            })
    
    return detailed_skills

@app.get("/industry-metrics", response_model=IndustryMetrics)
def get_industry_metrics(industry: str = Query(..., description="Industry to get metrics for")):
    """
    Get aggregate metrics for a specific industry.
    """
    # Get job count for industry
    job_count = job_postings_collection.count_documents({"industry": {"$regex": f"^{industry}$", "$options": "i"}})
    
    # Get company count for industry
    company_count = companies_collection.count_documents({"industry": {"$regex": f"^{industry}$", "$options": "i"}})
    
    # Get skill count for industry
    skills = skills_collection.find({"industries": {"$regex": f"^{industry}$", "$options": "i"}})
    skill_count = len(list(skills))
    
    # Get top locations for jobs in this industry
    pipeline = [
        {"$match": {"industry": {"$regex": f"^{industry}$", "$options": "i"}}},
        {"$group": {"_id": "$location", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    top_locations_result = list(job_postings_collection.aggregate(pipeline))
    top_locations = [item["_id"] for item in top_locations_result if item["_id"]]
    
    # Calculate average salary - simplified approach
    average_salary = "Not available"
    
    try:
        # First, try job_postings with salary info
        job_salary_data = list(job_postings_collection.find({
            "industry": {"$regex": f"^{industry}$", "$options": "i"},
            "median_salary": {"$exists": True, "$ne": None}
        }))
        
        # Then try roles collection
        role_salary_data = list(roles_collection.find({
            "industries": {"$regex": f"^{industry}$", "$options": "i"},
            "median_salary": {"$exists": True, "$ne": None}
        }))
        
        # Try to get from Industries collection as well
        industry_data = industries_collection.find_one({
            "Industry": {"$regex": f"^{industry}$", "$options": "i"},
            "median_salary": {"$exists": True, "$ne": None}
        })
        
        # Combine all salary data
        all_salary_data = job_salary_data + role_salary_data
        
        numeric_salaries = []
        
        for item in all_salary_data:
            salary = item.get("median_salary")
            
            # Skip None and NaN values
            if salary is None or (isinstance(salary, float) and math.isnan(salary)):
                continue
                
            try:
                if isinstance(salary, str):
                    # Handle string salaries like "$75,000"
                    # Remove all non-digit characters except decimal point
                    clean_salary = ''.join(c for c in salary if c.isdigit() or c == '.')
                    if clean_salary and clean_salary != '.':
                        numeric_salaries.append(float(clean_salary))
                elif isinstance(salary, (int, float)):
                    numeric_salaries.append(float(salary))
            except Exception:
                continue
        
        # If we have industry data with median_salary, use it directly
        if industry_data and "median_salary" in industry_data:
            industry_salary = industry_data["median_salary"]
            if isinstance(industry_salary, (int, float)) and not (isinstance(industry_salary, float) and math.isnan(industry_salary)):
                average_salary = f"${industry_salary:,.2f}"
            elif isinstance(industry_salary, str):
                clean_salary = ''.join(c for c in industry_salary if c.isdigit() or c == '.')
                if clean_salary and clean_salary != '.':
                    average_salary = f"${float(clean_salary):,.2f}"
        # Otherwise calculate from collected salaries
        elif numeric_salaries:
            avg = sum(numeric_salaries) / len(numeric_salaries)
            average_salary = f"${avg:,.2f}"
    except Exception:
        average_salary = "Not available"
    
    return {
        "job_count": job_count,
        "company_count": company_count,
        "skill_count": skill_count,
        "average_salary": average_salary,
        "top_locations": top_locations
    }

@app.get("/top-companies", response_model=List[Dict[str, Any]])
def get_top_companies(industry: str = Query(..., description="Industry to get top companies for")):
    """
    Get top companies for a specific industry based on job postings.
    """
    pipeline = [
        {"$match": {"industry": {"$regex": f"^{industry}$", "$options": "i"}}},
        {"$sort": {"job_postings": -1}},
        {"$limit": 10}
    ]
    
    top_companies = list(companies_collection.aggregate(pipeline))
    
    # Convert ObjectId to string for JSON serialization
    for company in top_companies:
        company["_id"] = str(company["_id"])
    
    return top_companies

@app.get("/job-postings", response_model=List[Dict[str, Any]])
def get_job_postings(
    industry: str = Query(None, description="Filter by industry"),
    role: str = Query(None, description="Filter by role"),
    company: str = Query(None, description="Filter by company"),
    limit: int = Query(20, description="Number of results to return"),
    skip: int = Query(0, description="Number of results to skip")
):
    """
    Get job postings with optional filters.
    """
    # Build query based on provided filters
    query = {}
    if industry:
        query["industry"] = {"$regex": f"^{industry}$", "$options": "i"}
    if role:
        query["role"] = {"$regex": f"^{role}$", "$options": "i"}
    if company:
        query["company"] = {"$regex": f"^{company}$", "$options": "i"}
    
    # Query job postings
    postings = job_postings_collection.find(query).sort("posted_date", -1).skip(skip).limit(limit)
    
    # Convert to list and process for JSON serialization
    result = []
    for posting in postings:
        posting["_id"] = str(posting["_id"])
        # Convert datetime to string if present
        if "posted_date" in posting and posting["posted_date"]:
            posting["posted_date"] = posting["posted_date"].isoformat()
        result.append(posting)
    
    return result

@app.get("/job-postings-by-skills")
def get_job_postings_by_skills(
    skills: List[str] = Query(..., description="User's skills to match against job postings"),
    limit: int = Query(10, description="Number of results to return")
):
    """
    Get actual job postings that match the user's skills.
    Returns job postings sorted by relevance (number of matching skills).
    """
    try:
        # Input validation
        if not skills:
            return JSONResponse(
                status_code=400,
                content={"error": "At least one skill must be provided"}
            )
        
        print(f"Processing request with skills: {skills}, limit: {limit}")
        
        # Create a flexible regex-based query for partial and case-insensitive skill matching
        # This will help match variations like "Machine Learning" with "ml", "machine learning", etc.
        skill_regex_queries = [
            {"skills": {"$regex": skill, "$options": "i"}} 
            for skill in skills
        ]
        
        # MongoDB query
        try:
            # Check database connection
            db_status = job_postings_collection.find_one({}, {"_id": 1})
            if db_status is None:
                print("Warning: Database connection issue or collection is empty")
            
            # Get job postings that have at least one of the user's skills
            # Use $or to match any of the skill regex patterns
            query = {"$or": skill_regex_queries}
            print(f"Executing flexible MongoDB query: {query}")
            
            # Print out all documents to help debug
            all_docs = list(job_postings_collection.find())
            print(f"Total documents in collection: {len(all_docs)}")
            
            # If no documents, print out a sample document to understand the schema
            if not all_docs:
                sample_doc_in_collection = job_postings_collection.find_one()
                print("Sample document in collection:", sample_doc_in_collection)
            
            # Attempt to print out skills in existing documents
            skills_in_docs = set()
            for doc in all_docs:
                doc_skills = doc.get("skills", [])
                if isinstance(doc_skills, list):
                    skills_in_docs.update(doc_skills)
            
            print("Skills found in existing documents:", list(skills_in_docs))
            
            job_postings = list(job_postings_collection.find(
                query,
                {
                    "title": 1, 
                    "role": 1, 
                    "company": 1, 
                    "location": 1,
                    "description": 1, 
                    "skills": 1, 
                    "salary_range": 1,
                    "url": 1,
                    "posted_date": 1,
                    "industry": 1
                }
            ))
            print(f"Found {len(job_postings)} matching job postings")
            
        except Exception as db_error:
            print(f"Database error: {str(db_error)}")
            return JSONResponse(
                status_code=500,
                content={"error": f"Database error: {str(db_error)}"}
            )
        
        # Process job postings and calculate match scores
        job_matches = []
        for job in job_postings:
            try:
                # Convert job skills to lowercase for case-insensitive matching
                job_skills = job.get("skills", [])
                if not isinstance(job_skills, list):
                    print(f"Warning: skills field is not a list for job {job.get('_id', 'unknown')}")
                    job_skills = []
                
                # Flexible skill matching
                def skill_matches(user_skill, job_skill):
                    # Convert both to lowercase for case-insensitive matching
                    user_skill_lower = user_skill.lower()
                    job_skill_lower = job_skill.lower()
                    
                    # Check for exact match or partial match
                    return (user_skill_lower in job_skill_lower) or (job_skill_lower in user_skill_lower)
                
                # Count matching skills with flexible matching
                matching_skills = sum(1 for skill in skills 
                                      if any(skill_matches(skill, job_skill) for job_skill in job_skills))
                total_skills = max(len(job_skills), 1)  # Avoid division by zero
                
                # Calculate match score as percentage
                match_score = (matching_skills / total_skills) * 100
                
                # Add match information
                job_info = {
                    "title": job.get("title", job.get("role", "Unnamed Position")),
                    "role": job.get("role", ""),
                    "company": job.get("company", ""),
                    "location": job.get("location", ""),
                    "description": job.get("description", ""),
                    "skills": job_skills,
                    "matching_skills_count": matching_skills,
                    "total_skills_count": total_skills,
                    "match_score": match_score,
                    "salary_range": job.get("salary_range", "Not specified"),
                    "posting_url": job.get("url", ""),
                    "industry": job.get("industry", "")
                }
                
                # Convert ObjectId to string for JSON serialization
                if "_id" in job:
                    job_info["_id"] = str(job["_id"])
                    
                # Convert posted_date to string if it exists
                if "posted_date" in job and job["posted_date"]:
                    try:
                        job_info["posted_date"] = job["posted_date"].isoformat() if hasattr(job["posted_date"], "isoformat") else str(job["posted_date"])
                    except Exception as date_error:
                        print(f"Error formatting date: {str(date_error)}")
                        job_info["posted_date"] = str(job["posted_date"])
                
                job_matches.append(job_info)
                
            except Exception as job_error:
                print(f"Error processing job {job.get('_id', 'unknown')}: {str(job_error)}")
                # Continue with next job instead of failing completely
                continue
        
        # Sort by match score in descending order
        job_matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        # If no matches, return a helpful message
        if not job_matches:
            return [
                {
                    "title": "No Matching Jobs Found",
                    "description": "Try broadening your search or checking your skills",
                    "skills": skills,
                    "match_score": 0
                }
            ]
        
        # Return only the top 'limit' results
        return job_matches[:limit]
        
    except Exception as e:
        print(f"Unexpected error in job-postings-by-skills: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Server error: {str(e)}"})