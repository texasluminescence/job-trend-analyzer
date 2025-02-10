from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
import os
import pandas as pd
from dotenv import load_dotenv

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
    name: str
    password: str

# Routes
@app.post("/users/")
def add_user(user: User):
    result = collection.insert_one(user.dict())
    return {"id": str(result.inserted_id)}

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