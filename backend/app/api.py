from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Load .env file
load_dotenv()

# MongoDB setup
MONGO_URL = os.getenv("MONGO_URL")
client = MongoClient(MONGO_URL)
db = client["DB1"] 

industries_collection = db["Industries"]
roles_collection = db["Roles"]
skills_collection = db["Skills"]
companies_collection = db["Companies"]
job_postings_collection = db["JobPostings"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Current endpoints that I'll maintain
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
    
    # Calculate average salary if available
    average_salary = "Not available"
    salary_data = roles_collection.find(
        {"industries": {"$regex": f"^{industry}$", "$options": "i"}, "median_salary": {"$exists": True, "$ne": None}}
    )
    salary_data = list(salary_data)
    if salary_data:
        # This assumes median_salary is a numeric value - adjust if it's stored as a string
        salaries = [item.get("median_salary") for item in salary_data if item.get("median_salary")]
        if salaries:
            # Convert to numbers if they're stored as strings
            numeric_salaries = []
            for salary in salaries:
                try:
                    if isinstance(salary, str):
                        # Remove currency symbols, commas, etc. and convert to float
                        clean_salary = ''.join(c for c in salary if c.isdigit() or c == '.')
                        numeric_salaries.append(float(clean_salary))
                    else:
                        numeric_salaries.append(float(salary))
                except (ValueError, TypeError):
                    continue
            
            if numeric_salaries:
                avg = sum(numeric_salaries) / len(numeric_salaries)
                average_salary = f"${avg:,.2f}"
    
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