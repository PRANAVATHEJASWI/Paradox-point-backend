from fastapi import FastAPI, HTTPException
from models import UserCreate, UserLogin, ResetPassword, UserOut
from database import users_collection
from auth import hash_password, verify_password
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
from mock_forwarder import forward_to_mock  # ⬅️ import here

app = FastAPI()

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

@app.get("/")
def root():
    return {"status": "working fine"}

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

    # Forward to mock server
    mock_response = await forward_to_mock("/register", new_user, method="POST")

    return {
        "message": "User registered",
        "user_id": str(result.inserted_id),
        "mock_server_response": mock_response
    }

# 🔓 Login
@app.post("/login")
async def login_user(login: UserLogin):
    user = await users_collection.find_one({"email": login.email})
    if not user or not verify_password(login.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    payload = {"email": login.email, "password": login.password}
    mock_response = await forward_to_mock("/login", payload, method="POST")

    return {
        "message": "Login successful",
        "user_id": str(user["_id"]),
        "mock_server_response": mock_response
    }

# 🔁 Reset Password
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

    payload = {
        "email": reset.email,
        "new_password": reset.new_password,
        "confirm_password": reset.confirm_password
    }
    mock_response = await forward_to_mock("/reset-password", payload, method="PATCH")

    return {
        "message": "Password updated successfully",
        "mock_server_response": mock_response
    }

# ❌ Delete User
@app.delete("/delete/{email}")
async def delete_user(email: str):
    result = await users_collection.delete_one({"email": email})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    mock_response = await forward_to_mock(f"/delete/{email}", method="DELETE")

    return {
        "message": "User deleted",
        "mock_server_response": mock_response
    }

# 🔍 Get User
@app.get("/user/{email}", response_model=UserOut)
async def get_user(email: str):
    user = await users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    mock_response = await forward_to_mock(f"/user/{email}", method="GET")

    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "mobile_number": user["mobile_number"],
        "age": user["age"],
        "mock_server_response": mock_response
    }
