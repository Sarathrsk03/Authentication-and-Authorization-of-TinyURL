import csv
import hashlib
import os
import random
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


templates = Jinja2Templates(directory="templates")
CSV_FILE = "urls.csv"
YOUTUBE_CSV_FILE = "youtube_urls.csv"


class URLBase:
    original_url: str

class URLCreate(URLBase):
    name: str
    dob: str

class URL(URLBase):
    short_url: str
    name: str
    dob: str

# Function to get top 10 music videos URL from CSV file
def random_read_youtube_urls():
    if not os.path.exists(YOUTUBE_CSV_FILE):
        return []
    with open(YOUTUBE_CSV_FILE, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        readerList = [row for row in reader]
        return readerList[random.randint(1,20)]["Youtube_links"]

# Function to read URLs from the CSV file
def read_urls():
    if not os.path.exists(CSV_FILE):
        return []
    with open(CSV_FILE, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        return [row for row in reader]

# Function to write URLs to the CSV file
def write_url(original_url: str, short_url: str, name: str, dob: str):
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([original_url, short_url, name, dob])

# Generate a short URL
def generate_short_url(original_url: str) -> str:
    return hashlib.md5(original_url.encode()).hexdigest()[:6]

@app.get("/",response_class=HTMLResponse)
async def redirect_create_page():
    return RedirectResponse(url="/create/")

# Route to render the form to create a short URL
@app.get("/create/", response_class=HTMLResponse)
async def create_short_url_page(request: Request):
    return templates.TemplateResponse("create_short_url.html", {"request": request})

# Handle the form submission to create a short URL
@app.post("/create/", response_class=HTMLResponse)
async def handle_create_short_url(
    request: Request, 
    original_url: str = Form(...), 
    name: str = Form(...), 
    dob: str = Form(...)
):
    short_url = generate_short_url(original_url)
    urls = read_urls()
    
    # Prevent duplicates
    while any(url['short_url'] == short_url for url in urls):
        short_url = generate_short_url(original_url + short_url)
    
    write_url(original_url, short_url, name, dob)
    
    return templates.TemplateResponse("create_short_url.html", {
        "request": request, 
        "short_url": short_url, 
        "original_url": original_url
    })

# Feedback and submission logic remains the same as earlier
@app.get("/{short_url}", response_class=HTMLResponse)
async def redirect_to_feedback(short_url: str, request: Request):
    urls = read_urls()
    for url in urls:
        if url['short_url'] == short_url:
            return templates.TemplateResponse("feedback_form.html", {
                "request": request, 
                "short_url": short_url, 
                "original_url": url['original_url']
            })
    raise HTTPException(status_code=404, detail="URL not found")

@app.post("/submit_feedback/")
async def submit_feedback(
    request:Request,
    short_url: str = Form(...), 
    feedback: str = Form(...), 
    name: str = Form(...), 
    dob: str = Form(...)
):
    urls = read_urls()
    for url in urls:
        if url['short_url'] == short_url:
            if name == url['name'] and dob == url['dob']:
                return templates.TemplateResponse("redirect.html", {
                    "request": request,
                    "original_url": url['original_url'], 
                })
    return templates.TemplateResponse("redirect.html", {
                    "request": request,
                    "original_url":random_read_youtube_urls() ,  
                })
