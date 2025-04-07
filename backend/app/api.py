from typing import List
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from pymongo import MongoClient
import os
import pandas as pd
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Load .env file
load_dotenv()

# MongoDB setup
MONGO_URL = os.getenv("MONGO_URL")
client = MongoClient(MONGO_URL)
db = client["DB1"]
collection = db["Users"]
industries_collection = db["Industries"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Routes
@app.post("/user/")
def add_user(user: User):
    result = collection.insert_one(user.dict())
    return {"id": str(result.inserted_id)}


# Setting up function to enable login (users credentials are input (email) verify that the encrypted password in DB matches password inputted when encrypted)
# If it does, approve login
# Returns true/false or also could return user information depending on implementation
@app.post("/login/")
def login(email: str, password: str) -> bool:
    # password input should be encrypted
    return True

# Input is users email address, returns information about user to display on profile page/be used for ML functions
# Uses email address to index into DB
# returns user info
@app.get("/user/")
def get_user(email: str) -> User:
    user = collection.find_one()
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
    for user in collection.find():
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

@app.get("/popular-skills", response_model=List)
def get_popular_skills(industry: str = Query(..., description="Industry to get popular skills for")):
    """
    Get popular skills for a specific industry.
    """

    industry_doc = industries_collection.find_one({"Industry": {"$regex": f"^{industry}$", "$options": "i"}})

    print(industry_doc)
    
    if not industry_doc or "Popular_skills" not in industry_doc:
        print("here")
        raise HTTPException(status_code=404, detail="Industry or popular skills not found")
    
    return industry_doc["Popular_skills"]

# Add these functions to your existing FastAPI app

@app.get("/skills/{skill_name}")
def get_skill_details(skill_name: str):
    """
    Get detailed information about a specific skill.
    """
    # Find the skill in the database
    skill = db["Skills"].find_one({"skill_name": {"$regex": f"^{skill_name}$", "$options": "i"}})
    
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    skill["_id"] = str(skill["_id"])
    return skill

@app.get("/roles/{role_name}")
def get_role_details(role_name: str):
    """
    Get detailed information about a specific role.
    """
    # Find the role in the database
    role = db["Roles"].find_one({"role_name": {"$regex": f"^{role_name}$", "$options": "i"}})
    
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    role["_id"] = str(role["_id"])
    return role

@app.get("/detailed-popular-skills")
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
        skill = db["Skills"].find_one({"skill_name": {"$regex": f"^{skill_name}$", "$options": "i"}})
        if skill:
            skill["_id"] = str(skill["_id"])
            # For backward compatibility with your frontend
            skill["skill"] = skill["skill_name"]
            skill["jobs"] = ", ".join(skill.get("related_roles", []))
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

@app.get("/detailed-popular-roles")
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
        role = db["Roles"].find_one({"role_name": {"$regex": f"^{role_name}$", "$options": "i"}})
        if role:
            role["_id"] = str(role["_id"])
            # For backward compatibility with your frontend
            role["title"] = role["role_name"]
            role["roles"] = role.get("open_positions_count", "N/A")
            role["companies"] = ", ".join(role.get("top_hiring_companies", []))
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

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI with synchronous MongoDB"}