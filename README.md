# Quick Mail Query
## Install Dependencies
`pip install -r requirements.txt`

## TODO List
- [x] Generate eml file with attachments for testing. (QQ mail website can export mail to eml.)
- [x] Use Python to extract information from email.
- [x] Use Python to extract information from emails' attachments.
    - [x] txt
    - [x] docx
    - [x] pdf
    - [x] pptx
    - [x] xlsx
 - [x] Keyword query.
 - [x] Use PyQt to create a GUI.
 - [ ] ~~Package into an exe file.~~
 - [x] Use multi-threaded / multi-process acceleration.
    - [x] Separate the  UI & query part first.
    - [x] Use multi-processes accelerate the query.
 - [ ] Make full use of the given memory to speed up the query.
 - [x] Use FastAPI to create a http server.
 - [ ] Use Vue to create a web application.
 
## Build
 ```shell script
pip install pyinstaller
pyinstaller -F -w main.py
```
And add this in the generated `main.spec`:
```python
import sys
sys.setrecursionlimit(5000)
```
Then run:
```
pyinstaller main.spec
```