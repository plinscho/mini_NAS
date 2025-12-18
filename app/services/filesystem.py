from pathlib import Path
from app.config import STORAGE_PATH
from fastapi.responses import FileResponse
from fastapi import UploadFile
import shutil

def save_file(relative_path: str, file: UploadFile):
    relative_path = relative_path.lstrip("/")
    # Normalizar: aceptar tanto "fotos" como "storage/fotos"
    storage_name = STORAGE_PATH.name
    if relative_path == storage_name or relative_path.startswith(f"{storage_name}/"):
        relative_path = relative_path[len(storage_name):].lstrip("/")

    base = STORAGE_PATH.resolve()
    target_dir = (base / relative_path).resolve()

    if not target_dir.is_relative_to(base):
        raise PermissionError

    # Crear la carpeta si no existe (antes fallaba con FileNotFoundError)
    target_dir.mkdir(parents=True, exist_ok=True)

    destination = target_dir / file.filename
    
    if destination.exists():
        raise FileExistsError

    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return destination


def list_dir(relative_path: str = "") -> list[dict]:
    relative_path = relative_path.lstrip("/")
    storage_name = STORAGE_PATH.name
    if relative_path == storage_name or relative_path.startswith(f"{storage_name}/"):
        relative_path = relative_path[len(storage_name):].lstrip("/")

    base = STORAGE_PATH.resolve()
    target = (base / relative_path).resolve()

    if not target.is_relative_to(base):
        raise PermissionError("Invalid Path!")
    
    if not target.exists() or not target.is_dir():
        raise FileNotFoundError("Directory not found!")

    items = []
    for item in target.iterdir():
        items.append({
            "name": item.name,
            "is_dir": item.is_dir(),
            "size": item.stat().st_size if item.is_file() else None
        })
    return items

# Donwload the files
def get_file(relative_path: str):
    relative_path = relative_path.lstrip("/")
    storage_name = STORAGE_PATH.name
    if relative_path == storage_name or relative_path.startswith(f"{storage_name}/"):
        relative_path = relative_path[len(storage_name):].lstrip("/")

    base = STORAGE_PATH.resolve()
    target = (base / relative_path).resolve()

    if not target.is_relative_to(base):
        raise PermissionError
    if not target.exists() or not target.is_file():
        raise FileNotFoundError
    return target


def delete_file(relative_path: str):
    """Delete a file given a relative path inside STORAGE_PATH.

    Raises FileNotFoundError if the target doesn't exist, PermissionError if path escapes storage
    or if the path is a directory (we only allow deleting files).
    """
    relative_path = relative_path.lstrip("/")
    storage_name = STORAGE_PATH.name
    if relative_path == storage_name or relative_path.startswith(f"{storage_name}/"):
        relative_path = relative_path[len(storage_name):].lstrip("/")

    base = STORAGE_PATH.resolve()
    target = (base / relative_path).resolve()

    if not target.is_relative_to(base):
        raise PermissionError
    if not target.exists():
        raise FileNotFoundError
    if target.is_dir():
        # Avoid removing directories with this endpoint
        raise PermissionError
    target.unlink()
    return True


def delete_dir(relative_path: str, recursive: bool = False):
    """Delete a directory inside STORAGE_PATH.

    If recursive is False, only an empty directory will be removed. If recursive is True,
    the directory and all its contents will be removed.
    """
    relative_path = relative_path.lstrip("/")
    storage_name = STORAGE_PATH.name
    if relative_path == storage_name or relative_path.startswith(f"{storage_name}/"):
        relative_path = relative_path[len(storage_name):].lstrip("/")

    base = STORAGE_PATH.resolve()
    target = (base / relative_path).resolve()

    if not target.is_relative_to(base):
        raise PermissionError
    if not target.exists():
        raise FileNotFoundError
    if not target.is_dir():
        # Not a directory
        raise PermissionError

    if recursive:
        shutil.rmtree(target)
        return True

    # Non recursive: only remove empty dirs
    try:
        target.rmdir()
        return True
    except OSError:
        # Directory not empty
        raise FileExistsError("Directory not empty")


def create_dir(relative_path: str):
    """Create a directory inside STORAGE_PATH.

    `relative_path` is a path relative to `STORAGE_PATH` and may contain
    subdirectories (e.g. "fotos/album1"). Raises FileExistsError if the
    directory already exists, PermissionError if the path is outside storage.
    """
    relative_path = relative_path.lstrip("/")
    storage_name = STORAGE_PATH.name
    if relative_path == storage_name or relative_path.startswith(f"{storage_name}/"):
        relative_path = relative_path[len(storage_name):].lstrip("/")

    base = STORAGE_PATH.resolve()
    target = (base / relative_path).resolve()

    if not target.is_relative_to(base):
        raise PermissionError
    if target.exists():
        raise FileExistsError

    target.mkdir(parents=True, exist_ok=False)
    return target

