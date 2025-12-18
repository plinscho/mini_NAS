from fastapi import APIRouter, HTTPException, UploadFile, File, Request
from fastapi.responses import FileResponse, StreamingResponse
import re
import mimetypes
from app.services.filesystem import list_dir, get_file, save_file, delete_file, delete_dir, create_dir, rename_item

router = APIRouter(prefix="/files", tags=["files"])

@router.get("/download/{path:path}")
def download_file(path: str):
	try:
		file_path = get_file(path)
		return FileResponse(
			file_path,
			filename=file_path.name
		)
	except FileNotFoundError:
		raise HTTPException(status_code=404, detail="File not found")
	except PermissionError:
		raise HTTPException(status_code=403, detail="Forbidden")


@router.get("/stream/{path:path}")
def stream_file(path: str, request: Request):
	"""Stream a file with support for Range requests (for video/audio preview)."""
	try:
		file_path = get_file(path)
		size = file_path.stat().st_size
		mime = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
		range_header = request.headers.get("range")
		if range_header:
			m = re.match(r"bytes=(\d+)-(\d*)", range_header)
			if not m:
				raise HTTPException(status_code=416, detail="Invalid Range")
			start = int(m.group(1))
			end = int(m.group(2)) if m.group(2) else size - 1
			if start >= size or start > end:
				raise HTTPException(status_code=416, detail="Range not satisfiable")
			length = end - start + 1

			def iter_file():
				with file_path.open("rb") as f:
					f.seek(start)
					remaining = length
					chunk_size = 1024 * 1024
					while remaining > 0:
						read = f.read(min(chunk_size, remaining))
						if not read:
							break
						remaining -= len(read)
						yield read

			headers = {
				"Content-Range": f"bytes {start}-{end}/{size}",
				"Accept-Ranges": "bytes",
				"Content-Length": str(length),
				"Content-Type": mime,
			}
			return StreamingResponse(iter_file(), status_code=206, headers=headers, media_type=mime)
		else:
			headers = {"Accept-Ranges": "bytes"}
			return FileResponse(file_path, media_type=mime, headers=headers)
	except FileNotFoundError:
		raise HTTPException(status_code=404, detail="File not found")
	except PermissionError:
		raise HTTPException(status_code=403, detail="Forbidden")

@router.post("/upload/{path:path}")
def upload_file(
	path: str,
	file: UploadFile = File(...)
):
	try:
		saved = save_file(path, file)
		return{
			"filename": saved.name,
			"size": saved.stat().st_size
		}
	except FileNotFoundError:
		raise HTTPException(status_code=404, detail="File not found")
	except PermissionError:
		raise HTTPException(status_code=403, detail="Forbidden")
	except FileExistsError:
		raise HTTPException(status_code=409, detail="File already exists!")

@router.post("/upload/")
def upload_root(file: UploadFile = File(...)):
	try:
		saved = save_file("", file)
		return {"filename": saved.name, "size": saved.stat().st_size}
	except PermissionError:
		raise HTTPException(status_code=403, detail="Forbidden")
	except FileExistsError:
		raise HTTPException(status_code=409, detail="File already exists!")

@router.delete("/delete/{path:path}")
def delete_path(path: str):
	try:
		delete_file(path)
		return {"deleted": path}
	except FileNotFoundError:
		raise HTTPException(status_code=404, detail="File not found")
	except PermissionError:
		raise HTTPException(status_code=403, detail="Forbidden")

@router.delete("/delete-dir/{path:path}")
def delete_dir_route(path: str, recursive: bool = False):
	try:
		delete_dir(path, recursive=recursive)
		return {"deleted": path}
	except FileNotFoundError:
		raise HTTPException(status_code=404, detail="Directory not found")
	except PermissionError:
		raise HTTPException(status_code=403, detail="Forbidden")
	except FileExistsError:
		raise HTTPException(status_code=409, detail="Directory not empty. Use ?recursive=1 to force delete.")

@router.post("/mkdir/{path:path}")
def mkdir(path: str, name: str):
	"""Create a subdirectory inside the given path. `name` is passed as query param."""
	try:
		full = f"{path.rstrip('/')}/{name}"
		created = create_dir(full)
		return {"created": str(created.name)}
	except FileExistsError:
		raise HTTPException(status_code=409, detail="Directory already exists")
	except PermissionError:
		raise HTTPException(status_code=403, detail="Forbidden")

@router.post("/mkdir/")
def mkdir_root(name: str):
	try:
		created = create_dir(name)
		return {"created": str(created.name)}
	except FileExistsError:
		raise HTTPException(status_code=409, detail="Directory already exists")
	except PermissionError:
		raise HTTPException(status_code=403, detail="Forbidden")

@router.post("/rename/{path:path}")
def rename_route(path: str, name: str):
	"""Rename a file or directory at `path` to `name` (query string param)."""
	try:
		new = rename_item(path, name)
		return {"old": path, "new": str(new.name)}
	except FileNotFoundError:
		raise HTTPException(status_code=404, detail="File not found")
	except FileExistsError:
		raise HTTPException(status_code=409, detail="Target name already exists")
	except PermissionError:
		raise HTTPException(status_code=403, detail="Forbidden")
	except ValueError:
		raise HTTPException(status_code=400, detail="Invalid name")

@router.get("/")
def list_root():
	return list_dir("")

@router.get("/{path:path}")
def list_path(path: str):
	try:
		return list_dir(path)
	except FileNotFoundError:
		raise HTTPException(status_code=404, detail="Path not found!")
	except PermissionError:
		raise HTTPException(status_code=402, detail="Forbidden!")

