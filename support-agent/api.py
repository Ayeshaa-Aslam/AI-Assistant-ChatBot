from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi import UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta
import hashlib
import asyncpg
import shutil
import os

from main_graph import app as langgraph_app

load_dotenv()
app = FastAPI()

UPLOAD_DIR = "profile_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "postgresql://postgres:1234@localhost:5432/supportdb"

# JWT setup
SECRET_KEY = "JWT_KEY"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Models
class TicketRequest(BaseModel):
    subject: str
    description: str

class UserSignup(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# Helper functions
def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

# Database connection
async def get_db():
    return await asyncpg.connect(DATABASE_URL)

@app.post("/process-ticket")
async def process_ticket(ticket: TicketRequest):
    state = {
        "subject": ticket.subject,
        "description": ticket.description,
        "category": None,
        "retrieved_context": [],
        "draft_response": None,
        "review_result": None,
        "retry_count": 0
    }
    
    ai_result = langgraph_app.invoke(state)
    
    print(" DEBUG - Full AI result:", ai_result)
    if "AI failed 2 attempts" in str(ai_result):
        return {
            "response": " I need more information. Could you describe your login issue in more detail?",
            "status": "needs_more_info",
            "attempts_used": 2
        }
    else:
        # Extract actual AI response
        response_text = str(ai_result.get("draft_response", 
                          ai_result.get("review_result", 
                          "I'm analyzing your issue...")))
        
        return {
            "response": response_text,
            "status": "answered",
            "attempts_used": 1
        }
    
@app.post("/signup")
async def signup(user: UserSignup):
    """User registration"""
    conn = await get_db()
    try:
        # Check if email exists
        exists = await conn.fetchrow(
            "SELECT id FROM users WHERE email = $1", user.email
        )
        if exists:
            raise HTTPException(status_code=400, detail="Email exists")
        
        # Insert user
        user_id = await conn.fetchval(
            """INSERT INTO users (name, email, password_hash, profile_picture) 
               VALUES ($1, $2, $3, $4) RETURNING id """, 
               user.name, user.email, hash_password(user.password), None)
        
        token = create_token({"sub": user.email, "user_id": user_id})
        
        return {
            "token": token,
            "user": {"id": user_id, "name": user.name, "email": user.email}
        }
    finally:
        await conn.close()

@app.post("/login")
async def login(user: UserLogin):
    """User login"""
    conn = await get_db()
    try:
        # Get user
        db_user = await conn.fetchrow("""
            SELECT id, name, email, password_hash, profile_picture 
            FROM users WHERE email = $1
        """, user.email)
        
        if not db_user or hash_password(user.password) != db_user['password_hash']:
            raise HTTPException(status_code=400, detail="Invalid credentials")
        
        token = create_token({"sub": user.email, "user_id": db_user['id']})
        
        return {
            "token": token,
            "user": {
                "id": db_user['id'],
                "name": db_user['name'],
                "email": db_user['email']
            }
        }
    finally:
        await conn.close()

@app.get("/user")
async def get_user(token: str = Depends(oauth2_scheme)):
    """Get current user WITH profile picture"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        if not user_email:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    conn = await get_db()
    try:
        # Get user WITH profile_picture
        user = await conn.fetchrow(
            "SELECT id, name, email, profile_picture FROM users WHERE email = $1",
            user_email
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Return WITH profile picture if exists
        user_data = {
            "id": user['id'],
            "name": user['name'],
            "email": user['email']
        }
        
        if user['profile_picture']:
            user_data["profilePicture"] = f"http://localhost:8000{user['profile_picture']}"
        
        return user_data 
    finally:
        await conn.close()


@app.post("/upload-profile")
async def upload_profile_picture(
    file: UploadFile = File(...),
    token: str = Depends(oauth2_scheme)
):
    """Upload profile picture"""
    try:
        # Verify user
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        
        if not user_email:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Validate file
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image files allowed")
        
        # Create unique filename
        timestamp = int(datetime.utcnow().timestamp())
        safe_email = user_email.replace("@", "_").replace(".", "_")
        file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        filename = f"{safe_email}_{timestamp}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Update user in database
        conn = await get_db()
        try:
            web_path = f"/uploads/{filename}"
            await conn.execute(
                "UPDATE users SET profile_picture = $1 WHERE email = $2",
                web_path, user_email
            )
        finally:
            await conn.close()
        
        return {
            "message": "Profile picture uploaded successfully",
            "file_path": web_path
        }
        
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Support Agent API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)