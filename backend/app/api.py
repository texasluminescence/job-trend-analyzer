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
    industry_doc = industries_collection.find_one({"name": {"$regex": f"^{industry}$", "$options": "i"}})
    
    if not industry_doc or "popular_roles" not in industry_doc:
        raise HTTPException(status_code=404, detail="Industry or popular roles not found")
    
    return industry_doc["popular_roles"]

@app.get("/popular-skills", response_model=List)
def get_popular_skills(industry: str = Query(..., description="Industry to get popular skills for")):
    """
    Get popular skills for a specific industry.
    """
    industry_doc = industries_collection.find_one({"name": {"$regex": f"^{industry}$", "$options": "i"}})
    
    if not industry_doc or "popular_skills" not in industry_doc:
        raise HTTPException(status_code=404, detail="Industry or popular skills not found")
    
    return industry_doc["popular_skills"]

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI with synchronous MongoDB"}