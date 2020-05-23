from typing import List

from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.responses import FileResponse

from database import query, get_mail_by_path
from util import parse


class Mail(BaseModel):
    subject: str
    sender: str
    receiver: str
    date: str
    content: str
    attachments: list
    path: str


app = FastAPI()


@app.get('/')
def index():
    return FileResponse('static/index.html')


class Search(BaseModel):
    keyword: str
    limit: int
    options: list


@app.get("/search")
async def process_search(search: Search):
    result = query(search.keyword, search.limit, search.options)
    return result


class Path(BaseModel):
    path: str


@app.get("/mail")
async def process_get_mail(path: Path):
    result = get_mail_by_path(path.path)
    return result


@app.post("/mail")
async def upload_eml(files: List[UploadFile] = File(...)):
    for file in files:
        filename = file.filename
    return {"file_sizes": [file.filename for file in files]}


app.mount("/", StaticFiles(directory="static"), name="static")
