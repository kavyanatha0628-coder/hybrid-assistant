import os
import datetime
from fastapi import FastAPI, Request, Form, HTTPException, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
import jwt
from groq import Groq

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Security Configurations
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-this")
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-Memory User Database (In production, use SQLite/PostgreSQL)
db_users = {}

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Helper Functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/register")
async def register(email: str = Form(...), password: str = Form(...)):
    if email in db_users:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_users[email] = hash_password(password)
    return {"message": "User registered successfully! Please login."}

@app.post("/login")
async def login(email: str = Form(...), password: str = Form(...)):
    user_hash = db_users.get(email)
    if not user_hash or not verify_password(password, user_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_access_token({"sub": email})
    return {"access_token": token, "token_type": "bearer", "message": "Login successful!"}

@app.post("/process")
async def process_text(request: Request):
    data = await request.json()
    user_prompt = data.get("prompt", "")

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": user_prompt}],
        model="llama3-8b-8192"
    )
    return {"response": chat_completion.choices[0].message.content}