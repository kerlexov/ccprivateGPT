from typing import Annotated

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
import aiofiles
import subprocess


app = FastAPI()

@app.put("/query")
async def query(query: str):
    script = f"privateGPT.py"
    process = subprocess.Popen(["python3", script, "--query", f"\"{query}\""], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        # script has returned an error
        return {"success": False, "error": stderr.decode()}
    # script ran successfully
    return {"success": True, "output": stdout.decode()}


@app.post('/upload')
async def post_endpoint(in_file: UploadFile=File(...)):
    async with aiofiles.open(f'source_documents/{in_file.filename}', 'wb') as out_file:
        while content := await in_file.read(1024):  # async read chunk
            await out_file.write(content)  # async write chunk

    script = "ingest.py"
    process = subprocess.Popen(["python3", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        # script has returned an error
        return {"success": False, "error": stderr.decode()}

    # script ran successfully
    return {"success": True, "output": stdout.decode()}


@app.get("/")
async def main():
    content = """
<body>
<form action="/upload/" enctype="multipart/form-data" method="post">
<input name="in-file" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)