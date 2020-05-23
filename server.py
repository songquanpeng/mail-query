import os
import time
import database
import uvicorn

from typing import List
from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.responses import FileResponse
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
    return FileResponse('web/build/index.html')


class Search(BaseModel):
    keyword: str
    limit: int
    options: list


@app.post("/search")
async def process_search(search: Search):
    result = database.query(search.keyword, search.limit, search.options)
    return result


class Path(BaseModel):
    path: str


@app.post("/getMail")
async def process_get_mail(path: Path):
    result = database.get_mail_by_path(path.path)
    return result


@app.post("/mail")
async def upload_eml(files: List[UploadFile] = File(...)):
    base_path = './data'
    database.init()
    for file in files:
        filename = str(time.time()) + " " + file.filename
        path = os.path.join(base_path, filename)
        with open(path, 'wb') as f:
            f.write(file.file.read())
        parsed_mail = parse(path)
        database.insert(parsed_mail)
    database.close()
    return {"status": "OK"}


app.mount("/", StaticFiles(directory="web/build"), name="static")

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=3000)
