from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from app.services.filesystem import list_dir, get_file, save_file, delete_file, delete_dir, create_dir

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

