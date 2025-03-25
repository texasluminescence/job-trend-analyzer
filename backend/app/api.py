from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
import os
import pandas as pd
from dotenv import load_dotenv
import bcrypt

app = FastAPI()

# Load .env file
load_dotenv()

# MongoDB setup
MONGO_URL = os.getenv("MONGO_URL")
client = MongoClient(MONGO_URL)
db = client["DB1"]
collection = db["Users"]

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
    # result = collection.insert_one(user.dict())
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    user_dict = user.dict()
    user_dict["password"] = hashed_password.decode('utf-8')
    result = collection.insert_one(user_dict )
    return {"id": str(result.inserted_id)}


# Setting up function to enable login (users credentials are input (email) verify that the encrypted password in DB matches password inputted when encrypted)
# If it does, approve login
# Returns true/false or also could return user information depending on implementation
@app.post("/login/")
def login(email: str, password: str) -> bool:
    # password input should be encrypted
    user = collection.find_one({"email": email})
    stored_hashed_password = user["password"].encode('utf-8')
    if user and bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
        return True
    return False

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

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI with synchronous MongoDB"}