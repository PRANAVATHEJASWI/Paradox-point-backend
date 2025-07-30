from fastapi import FastAPI, HTTPException, status
from models import UserCreate, UserLogin, ResetPassword, UserOut
from database import users_collection
from auth import hash_password, verify_password
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
@app.get("/")
def root():
    return {"status": "working fine"}
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://paradox-point.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ➕ Register User
@app.post("/register", status_code=201)
async def register_user(user: UserCreate):
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already exists")
    
    hashed_pwd = hash_password(user.password)
    new_user = {
        "name": user.name,
        "email": user.email,
        "mobile_number": user.mobile_number,
        "age": user.age,
        "password": hashed_pwd
    }

    result = await users_collection.insert_one(new_user)
    return {"message": "User registered", "user_id": str(result.inserted_id)}

# 🔓 Login
@app.post("/login")
async def login_user(login: UserLogin):
    user = await users_collection.find_one({"email": login.email})
    if not user or not verify_password(login.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "user_id": str(user["_id"])}

@app.patch("/reset-password")
async def reset_password(reset: ResetPassword):
    if reset.new_password != reset.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    user = await users_collection.find_one({"email": reset.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_hashed = hash_password(reset.new_password)
    await users_collection.update_one(
        {"email": reset.email},
        {"$set": {"password": new_hashed}}
    )
    return {"message": "Password updated successfully"}

@app.delete("/delete/{email}")
async def delete_user(email: str):
    result = await users_collection.delete_one({"email": email})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}
@app.get("/user/{email}", response_model=UserOut)
async def get_user(email: str):
    user = await users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "mobile_number": user["mobile_number"],
        "age": user["age"],
    }

