import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from groq import Groq

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Groq Client Initialization
# Replace YOUR_GROQ_API_KEY with the actual key you copied (e.g., "gsk_...")
client = Groq(api_key="gsk_YOUR_ACTUAL_KEY_HERE")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process")
async def process_text(request: Request):
    data = await request.json()
    user_prompt = data.get("prompt", "")

    # Calling Groq API (Ultra-fast Llama-3 model)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": user_prompt,
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    
    bot_response = chat_completion.choices[0].message.content
    return {"response": bot_response}