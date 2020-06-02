import os
import time
from utils import database
import uvicorn

from typing import List
from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.responses import FileResponse
from utils.utils import parse

conn = database.create_connection()

host = "127.0.0.1"
port = 8000


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
    result = database.query(search.keyword, search.limit, search.options, True, conn)
    return result


class Path(BaseModel):
    path: str


@app.post("/download")
async def process_get_mail(path: Path):
    file_path = path.path
    return FileResponse(file_path)


@app.post("/upload")
async def upload_eml(files: List[UploadFile] = File(...)):
    base_path = './data'
    for file in files:
        filename = str(time.time()) + " " + file.filename
        path = os.path.join(base_path, filename)
        with open(path, 'wb') as f:
            f.write(file.file.read())
        parsed_mail = parse(path)
        database.insert(parsed_mail, conn)
    conn.commit()
    return {"status": "OK"}


app.mount("/", StaticFiles(directory="web/build"), name="static")


def serve():
    uvicorn.run(app, host=host, port=port)


if __name__ == '__main__':
    serve()
