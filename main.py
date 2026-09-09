import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from groq import Groq

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Reads the key securely set in Render Environment Variables
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/process")
async def process_text(request: Request):
    data = await request.json()
    user_prompt = data.get("prompt", "")

    # Calling Groq API
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        model="llama3-8b-8192"
    )
    
    return {"response": chat_completion.choices[0].message.content}