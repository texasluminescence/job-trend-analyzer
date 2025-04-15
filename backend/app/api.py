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
    allow_origins=["*"],
    allow_credentials=False,
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
    interested_roles: list = [] 
    current_job: str = ""       
    yoe: int
    skills: dict
    type_of_work: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ProfileUpdate(BaseModel):
    education_level: str
    graduation_date: str
    degree: str

class ExperienceUpdate(BaseModel):
    yoe: int
    type_of_work: str
    current_job: Optional[str] = None  # Added current_job field

class IndustriesUpdate(BaseModel):
    industries: List[str]

class RolesUpdate(BaseModel):  # New model for interested roles
    interested_roles: List[str]

class SkillsUpdate(BaseModel):
    skills: Dict[str, Any]

class UserUpdateRequest(BaseModel):
    email: str
    profile: Optional[ProfileUpdate] = None
    experience: Optional[ExperienceUpdate] = None
    industries: Optional[IndustriesUpdate] = None
    interested_roles: Optional[RolesUpdate] = None  # Added field for roles update
    skills: Optional[SkillsUpdate] = None

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

def clean_float_values(obj):
    if isinstance(obj, dict):
        return {k: clean_float_values(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_float_values(item) for item in obj]
    elif isinstance(obj, float):
        import math
        if math.isnan(obj) or math.isinf(obj):
            return str(obj)  # Convert to string representation
    return obj

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
def login(login_data: LoginRequest) -> dict:
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
def get_user(email: str):
    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user["_id"] = str(user["_id"])
    
    return user


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

@app.get("/all-skills")
def get_all_skills():
    """
    Return a list of all skill names for autosuggest.
    """
    skills = skills_collection.find({}, {"skill_name": 1, "_id": 0})
    return sorted([s["skill_name"] for s in skills if "skill_name" in s])

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



@app.get("/highest-paid-skills", response_model=List[Dict[str, Any]])
def get_highest_paid_skills():
    """
    Return the top 10 highest-paid skills based on salary analysis stored in MongoDB.
    """
    try:
        # Only include skills with average_salary and a minimum number of job postings
        pipeline = [
            {"$match": {"average_salary": {"$exists": True}, "job_postings_count": {"$gte": 1}}},
            {"$sort": {"average_salary": -1}},
            {"$limit": 10}
        ]

        top_skills = list(skills_collection.aggregate(pipeline))

        for skill in top_skills:
            skill["_id"] = str(skill["_id"])

        return top_skills

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving skills: {str(e)}")



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
        if len(role_name) > 50 or "?" in role_name or "..." in role_name:
            continue
            
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
            # Only add minimally formatted roles if they seem valid
            if len(role_name) <= 50 and "?" not in role_name and "..." not in role_name:
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
    print(job_postings_collection.count_documents({}))
    print(job_count)
    
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
    limit: int = Query(None, description="Number of results to return"),
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

@app.get("/suggested-skills")
def get_suggested_skills(
    email: str = Query(..., description="User email to identify the profile"),
    limit: int = Query(10, description="Number of suggestions to return")
):
    try:
        user = users_collection.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user_industries = user.get("industries", [])
        user_roles = user.get("interested_roles", [])
        skills_dict = user.get("skills", {})

        user_current_skills = set()

        for skill_group in skills_dict.keys():
            if isinstance(skill_group, list):
                for skill in skill_group:
                    if isinstance(skill, str) and skill.strip():
                        user_current_skills.add(skill.strip().lower())
            elif isinstance(skill_group, dict):
                for skill_name in skill_group.keys():
                    if isinstance(skill_name, str) and skill_name.strip():
                        user_current_skills.add(skill_name.strip().lower())
            elif isinstance(skill_group, str) and skill_group.strip():
                user_current_skills.add(skill_group.strip().lower())

        skill_score_map = {}

        valid_skill_pool = set()

        # Collect all valid skills from selected industries
        for industry in user_industries:
            doc = industries_collection.find_one({"Industry": {"$regex": f"^{industry}$", "$options": "i"}})
            if doc:
                for skill in doc.get("Skills", []):
                    valid_skill_pool.add(skill.strip().lower())
                    if skill.strip().lower() not in user_current_skills:
                        skill_score_map[skill.strip().lower()] = skill_score_map.get(skill.strip().lower(), 0) + 1

        # Collect all valid skills from selected roles
        for role in user_roles:
            doc = roles_collection.find_one({"role_name": {"$regex": f"^{role}$", "$options": "i"}})
            if doc:
                for skill in doc.get("required_skills", []):
                    valid_skill_pool.add(skill.strip().lower())
                    if skill.strip().lower() not in user_current_skills:
                        skill_score_map[skill.strip().lower()] = skill_score_map.get(skill.strip().lower(), 0) + 2

        # Include related skills only if they belong to valid_skill_pool
        for skill_name in user_current_skills:
            skill_doc = skills_collection.find_one({"skill_name": {"$regex": f"^{skill_name}$", "$options": "i"}})
            if skill_doc:
                for rel in skill_doc.get("related_skills", []):
                    s = rel.strip().lower()
                    if s not in user_current_skills and s in valid_skill_pool:
                        skill_score_map[s] = skill_score_map.get(s, 0) + 1

        # Rank and format suggestions
        ranked_skills = sorted(skill_score_map.items(), key=lambda x: x[1], reverse=True)
        suggestions = []

        for i, (skill_name, score) in enumerate(ranked_skills[:limit]):
            doc = skills_collection.find_one({"skill_name": {"$regex": f"^{skill_name}$", "$options": "i"}})
            suggestions.append({
                "letter": chr(65 + i),
                "name": skill_name,
                "relevance_score": score,
                "description": doc.get("description", "") if doc else "",
                "job_count": doc.get("job_postings_count", 0) if doc else 0
            })

        # If not enough suggestions, add fallback popular skills NOT in user skills or already suggested
        if len(suggestions) < limit:
            seen = {s["name"].lower() for s in suggestions}
            fallback_pool = skills_collection.find().sort("job_postings_count", -1).limit(50)
            for doc in fallback_pool:
                name = doc.get("skill_name", "").lower()
                if name and name not in seen and name not in user_current_skills and name in valid_skill_pool:
                    suggestions.append({
                        "letter": chr(65 + len(suggestions)),
                        "name": name,
                        "relevance_score": 1,
                        "description": doc.get("description", ""),
                        "job_count": doc.get("job_postings_count", 0)
                    })
                    seen.add(name)
                    if len(suggestions) >= limit:
                        break

        return suggestions

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating suggestions: {str(e)}")


    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating suggestions: {str(e)}")


@app.get("/job-postings-by-skills")
def get_job_postings_by_skills(
    skills: List[str] = Query(..., description="User's skills to match against job postings"),
    limit: int = Query(10, description="Number of results to return")
):
    try:
        if not skills:
            return JSONResponse(
                status_code=400,
                content={"error": "At least one skill must be provided"}
            )

        # Normalize user skills
        user_skills = [s.strip().lower() for s in skills if s]

        skill_regex_queries = [
            {"skills_required": {"$elemMatch": {"$regex": skill, "$options": "i"}}}
            for skill in user_skills
        ]

        query = {"$or": skill_regex_queries}
        job_postings = list(job_postings_collection.find(
            query,
            {
                "title": 1,
                "role": 1,
                "company": 1,
                "location": 1,
                "description": 1,
                "skills_required": 1,
                "salary_range": 1,
                "url": 1,
                "posted_date": 1,
                "industry": 1
            }
        ))

        job_matches = []
        seen_jobs = set()  # Deduplication based on title+company

        for job in job_postings:
            title = job.get("title", job.get("role", "Unnamed Position"))
            company = job.get("company", "")
            unique_key = f"{title.lower()}::{company.lower()}"
            if unique_key in seen_jobs:
                continue
            seen_jobs.add(unique_key)

            job_skills = job.get("skills_required", [])
            if not isinstance(job_skills, list):
                job_skills = []

            # Normalize and deduplicate job skills
            job_skills = list(set([s.strip().lower() for s in job_skills if isinstance(s, str)]))

            def skill_matches(user_skill, job_skill):
                return user_skill in job_skill or job_skill in user_skill

            matching_skills = sum(
                1 for skill in user_skills
                if any(skill_matches(skill, job_skill) for job_skill in job_skills)
            )

            total_skills = max(len(job_skills), 1)  # avoid divide by zero
            match_score = (matching_skills / total_skills) * 100
            match_score = min(match_score, 100.0)  # clamp to 100
            match_score = round(match_score, 2)

            job_info = {
                "title": title,
                "role": job.get("role", ""),
                "company": company,
                "location": job.get("location", ""),
                "description": job.get("description", ""),
                "skills": job_skills,
                "matching_skills_count": matching_skills,
                "total_skills_count": total_skills,
                "match_score": match_score,
                "salary_range": job.get("salary_range", "Not specified"),
                "posting_url": job.get("url", ""),
                "industry": job.get("industry", ""),
                "recommended": True
            }

            if "_id" in job:
                job_info["_id"] = str(job["_id"])
            if "posted_date" in job and job["posted_date"]:
                try:
                    job_info["posted_date"] = job["posted_date"].isoformat()
                except Exception:
                    job_info["posted_date"] = str(job["posted_date"])

            job_matches.append(job_info)

        job_matches.sort(key=lambda x: x["match_score"], reverse=True)

        if not job_matches:
            return [{
                "title": "No Matching Jobs Found",
                "description": "Try broadening your search or checking your skills",
                "skills": skills,
                "match_score": 0,
                "recommended": False
            }]

        return clean_float_values(job_matches[:limit])

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"Server error: {str(e)}"}
        )


@app.put("/update-user/")
def update_user(update_data: UserUpdateRequest):
    """
    Update specific sections of a user's profile
    """
    # Find the user by email
    user = users_collection.find_one({"email": update_data.email})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prepare the update document
    update_fields = {}
    
    # Update profile fields if provided
    if update_data.profile:
        update_fields.update({
            "education_level": update_data.profile.education_level,
            "graduation_date": update_data.profile.graduation_date,
            "degree": update_data.profile.degree
        })
    
    # Update experience fields if provided
    if update_data.experience:
        update_fields.update({
            "yoe": update_data.experience.yoe,
            "type_of_work": update_data.experience.type_of_work
        })
        # Only update current_job if it's provided
        if update_data.experience.current_job is not None:
            update_fields["current_job"] = update_data.experience.current_job
    
    # Update industries if provided
    if update_data.industries:
        update_fields.update({
            "industries": update_data.industries.industries
        })
    
    # Update interested roles if provided
    if update_data.interested_roles:
        update_fields.update({
            "interested_roles": update_data.interested_roles.interested_roles
        })
    
    # Update skills if provided
    if update_data.skills:
        update_fields.update({
            "skills": update_data.skills.skills
        })
    
    # Only perform update if there are fields to update
    if update_fields:
        result = users_collection.update_one(
            {"email": update_data.email},
            {"$set": update_fields}
        )
        
        if result.modified_count == 0:
            # The document wasn't modified (possibly because the values were the same)
            return {"updated": False, "message": "No changes were made"}
        
        return {"updated": True, "message": "User information updated successfully"}
    
    return {"updated": False, "message": "No valid update fields provided"}


@app.get("/industry-skills-demand")
def get_industry_skills_demand(
    email: str = Query(..., description="User email to identify industry preferences"),
    limit: int = Query(10, description="Number of skills to return")
):
    """
    Get in-demand skills for a user's preferred industry with demand score.
    This endpoint is designed to provide data for the personalized page bar chart.
    """
    try:
        # Find the user by email to get their industry preference
        user = users_collection.find_one({"email": email})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user's primary industry (use first in list or default to "Tech")
        user_industries = user.get("industries", [])
        primary_industry = user_industries[0] if user_industries else "Tech"
        
        # Get industry details including popular skills
        industry = industries_collection.find_one({"Industry": {"$regex": f"^{primary_industry}$", "$options": "i"}})
        
        if not industry:
            # Fallback to Tech industry if user's industry not found
            industry = industries_collection.find_one({"Industry": "Tech"})
            if not industry:
                return [{"skill": "Python", "demand": 100}, {"skill": "JavaScript", "demand": 85}]
        
        # Get popular skills for this industry
        popular_skills = industry.get("Popular_skills", [])
        
        # If no popular skills found, return some defaults
        if not popular_skills:
            return [{"skill": "Python", "demand": 100}, {"skill": "JavaScript", "demand": 85}]
        
        # Enrich with job counts data
        skill_demand = []
        max_count = 0
        
        for skill_name in popular_skills:
            # Find skill in skills collection to get job posting count
            skill_doc = skills_collection.find_one({"skill_name": {"$regex": f"^{skill_name}$", "$options": "i"}})
            if skill_doc:
                count = skill_doc.get("job_postings_count", 0)
                if count > max_count:
                    max_count = count
                skill_demand.append({
                    "skill": skill_name,
                    "job_count": count
                })
        
        # Sort by job count descending
        skill_demand.sort(key=lambda x: x["job_count"], reverse=True)
        
        # Limit to requested number and calculate relative demand percentage
        result = []
        for item in skill_demand[:limit]:
            # Normalize to percentage with maximum skill at 100%
            normalized_demand = 100 if max_count == 0 else int((item["job_count"] / max_count) * 100)
            result.append({
                "skill": item["skill"].title(),  # Capitalize skill name
                "demand": normalized_demand,
                "job_count": item["job_count"]
            })
        
        return result
        
    except Exception as e:
        print(f"Error in industry-skills-demand endpoint: {str(e)}")
        # Return some default data if error occurs
        return [
            {"skill": "Python", "demand": 100},
            {"skill": "JavaScript", "demand": 85},
            {"skill": "SQL", "demand": 75},
            {"skill": "React", "demand": 68},
            {"skill": "AWS", "demand": 60}
        ]
    
@app.get("/skill-details")
def get_skill_details_by_query(name: str = Query(..., description="Name of the skill to get details for")):
    """
    Get detailed information about a specific skill using query parameters.
    This is an alternative to the path parameter endpoint /skills/{skill_name}.
    """
    skill = skills_collection.find_one({"skill_name": {"$regex": f"^{name}$", "$options": "i"}})
    
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    skill["_id"] = str(skill["_id"])

    
    # Clean the skill data
    clean_skill = clean_float_values(skill)
    
    return JSONResponse(content=clean_skill)