import os
import logging
import pathlib
from pathlib import Path
from fastapi import FastAPI, Form, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
import json
import sqlite3
import hashlib

cwd = Path.cwd()
parent = cwd.parent
database_file = parent / 'db/items.db'

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.DEBUG
images = pathlib.Path(__file__).parent.resolve() / "image"
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

# adds onto database with two tables (items and category)
def write_to_database(new_item):
    conn = sqlite3.connect(database_file, check_same_thread=False)
    c = conn.cursor()

    params = (new_item["category"],)

    try:
        c.execute("INSERT OR IGNORE INTO category (name) VALUES (?)", params)
        c2 = c.execute('SELECT * FROM category WHERE name=?',params)
        category_id = c2.fetchone()[0]
        params2 = (new_item["name"], category_id, new_item["image"],)
        c.execute("INSERT OR IGNORE INTO items (name, category_id, image) VALUES (? ,?, ?)",params2)
        conn.commit()
    except sqlite3.Error as er:
        logger.error("SQLite error: %s", (' '.join(er.args)))
        logger.error("Exception class is: ", er.__class__)
        return {"message": f"{er}"}

    conn.close()

def hash256(filename):
    hashed_name = hashlib.sha256(filename.replace('.jpg', '').encode('utf-8')).hexdigest() + ".jpg"
    return hashed_name

#GET request
@app.get("/")
def root():
    return {"message": "Hello, world!"}

#POST request (/items)
@app.post("/items")
def add_item(name: str = Form(...), category: str = Form(...), image: UploadFile = File(...)):

    file_uploaded = images / image.filename
    hashed_filename = hash256(image)

    with open(save_path, 'r') as buffer:
        shutil.copyfile(file_uploaded.file, buffer)

    newItem = {
    "name": f"{name}",
    "category": f"{category}",
    "image" : f"{hashed_filename}"
    }
    write_to_database(newItem)

    received = {"name":{name}, "category" :{category}, "image": {image}}
    logger.info(f"Receive item: {received}")
    return {"message": f"item received: {name} "}

#GET request (/image/image_filename)
@app.get("/image/{image_filename}")
async def get_image(image_filename):
    # Create image path
    image = images / image_filename

    if not image_filename.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)

#GET request (/items)
@app.get("/items")
def get_items():
    data = {"items":[]}

    conn = sqlite3.connect(database_file, check_same_thread=False)
    c = conn.cursor()

    try:
        c.execute('SELECT items.name, category.name, image FROM items JOIN category ON items.category_id = category.id')
        items = c.fetchall()
        conn.commit()

        for item in items:
            new_item = {
            "name": f"{item[0]}",
            "category": f"{item[1]}",
            "image": f"{item[2]}"
            }

            data["items"].append(new_item)

            return data

    except sqlite3.Error as er:
        logger.error("SQLite error: %s", (' '.join(er.args)))
        logger.error("Exception class is: ", er.__class__)
        {"message": f"{er}"}

    conn.close()

# GET request with item_id
@app.get("/items/{item_id}")
def get_item_from_id(item_id):

    conn = sqlite3.connect(database_file, check_same_thread=False)
    c = conn.cursor()

    try:
        c.execute('SELECT items.name, category.name, image FROM items JOIN category ON items.category_id = category.id WHERE items.id = ?',item_id)
        items = c.fetchone()
        res = {
        "name": f"{items[0]}",
        "category": f"{items[1]}",
        "image": f"{items[2]}"
        }
        conn.commit()
        return res

    except sqlite3.Error as er:
        logger.error("SQLite error: %s", (' '.join(er.args)))
        logger.error("Exception class is: %s", er.__class__)
        {"message": f"{er}"}

    conn.close()

# GET request for /search
@app.get("/search")
def search_items(keyword: str):
    data = {"items":[]}
    if not keyword :
        raise HTTPException(status_code=400, detail="Keyword not entered")

    params = (keyword, keyword)

    conn = sqlite3.connect(database_file, check_same_thread=False)
    c = conn.cursor()
    try:
        c.execute('SELECT items.name, category.name, image FROM items JOIN category ON items.category_id = category.id WHERE items.name = ? OR category.name = ?', params)
        items = c.fetchall()
        for item in items:
            new_item = {
            "name": f"{item[0]}",
            "category": f"{item[1]}",
            "image": f"{item[2]}"
            }
            data["items"].append(new_item)
        conn.commit()
        return data

    except sqlite3.error as er:
        logger.error("SQLite error: %s", (' '.join(er.args)))
        logger.error("Exception class is: ", er.__class__)
        {"message": f"{er}"}

    conn.close()
