const listing = document.getElementById("listing");
const breadcrumbs = document.getElementById("breadcrumbs");
const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");
const upBtn = document.getElementById("upBtn");
const mkdirBtn = document.getElementById("mkdirBtn");

let currentPath = "";

function encodePath(p) {
  return encodeURIComponent(p).replace(/%2F/g, "/");
}

async function list(path = "") {
  currentPath = path;
  // Habilitar o deshabilitar botón de subir (ir al padre)
  upBtn.disabled = !currentPath;
  breadcrumbs.textContent = "/" + path;
  const url = path ? `/files/${encodePath(path)}` : `/files/`;
  listing.innerHTML = "Cargando...";
  try {
    const r = await fetch(url);
    if (!r.ok) throw new Error(await r.text());
    const items = await r.json();
    renderList(items);
  } catch (e) {
    listing.innerHTML = `<div class="error">Error: ${e.message}</div>`;
  }
}

function renderList(items) {
  if (!items.length) {
    listing.innerHTML = "<div class='empty'>Carpeta vacía</div>";
    return;
  }
  const ul = document.createElement("ul");
  items.forEach(it => {
    const li = document.createElement("li");
    li.className = it.is_dir ? "dir" : "file";
    const name = document.createElement("span");
    name.textContent = it.name;
    li.appendChild(name);

    if (it.is_dir) {
      const next = currentPath ? `${currentPath}/${it.name}` : it.name;

      const open = document.createElement("button");
      open.textContent = "Abrir";
      open.onclick = () => list(next);
      li.appendChild(open);

      const del = document.createElement("button");
      del.textContent = "Eliminar";
      del.className = "delete";
      del.onclick = async () => {
        if (!confirm(`¿Borrar la carpeta ${next}? Esto eliminará todo su contenido.`)) return;
        del.disabled = true;
        try {
          const res = await fetch(`/files/delete-dir/${encodePath(next)}?recursive=1`, { method: "DELETE" });
          if (!res.ok) throw new Error(await res.text());
          // Si borramos la carpeta actual, subir al padre
          if (next === currentPath) {
            const parts = currentPath.split("/");
            parts.pop();
            const parent = parts.filter(Boolean).join("/");
            await list(parent);
          } else {
            await list(currentPath);
          }
        } catch (e) {
          alert("Error al eliminar carpeta: " + e.message);
          del.disabled = false;
        }
      };
      li.appendChild(del);
    } else {
      const filePath = currentPath ? `${currentPath}/${it.name}` : it.name;

      const dl = document.createElement("a");
      dl.href = `/files/download/${encodePath(filePath)}`;
      dl.textContent = "Descargar";
      dl.className = "download";
      li.appendChild(dl);

      const del = document.createElement("button");
      del.textContent = "Eliminar";
      del.className = "delete";
      del.onclick = async () => {
        if (!confirm(`¿Borrar ${filePath}?`)) return;
        del.disabled = true;
        try {
          const res = await fetch(`/files/delete/${encodePath(filePath)}`, { method: "DELETE" });
          if (!res.ok) throw new Error(await res.text());
          await list(currentPath);
        } catch (e) {
          alert("Error al eliminar: " + e.message);
          del.disabled = false;
        }
      };
      li.appendChild(del);
    }
    ul.appendChild(li);
  });
  listing.innerHTML = "";
  listing.appendChild(ul);
}

// abrir selector con único botón
uploadBtn.onclick = () => fileInput.click();

// subida automática al seleccionar archivo
fileInput.onchange = async () => {
  const f = fileInput.files[0];
  if (!f) return;
  uploadBtn.disabled = true;
  try {
    const form = new FormData();
    form.append("file", f);
    const uploadPath = currentPath ? `/files/upload/${encodePath(currentPath)}` : `/files/upload/`;
    const res = await fetch(uploadPath, { method: "POST", body: form });
    if (!res.ok) throw new Error(await res.text());
    await list(currentPath);
    fileInput.value = "";
  } catch (e) {
    alert("Error al subir: " + e.message);
  } finally {
    uploadBtn.disabled = false;
  }
};

// botón subir nivel
upBtn.onclick = () => {
  if (!currentPath) return;
  const parts = currentPath.split("/");
  parts.pop();
  const parent = parts.filter(Boolean).join("/");
  list(parent);
};

// crear directorio
mkdirBtn.onclick = async () => {
  const name = prompt("Nombre de la nueva carpeta:");
  if (!name) return;
  if (name.includes("/")) return alert("El nombre no puede contener '/'.");

  const url = currentPath ? `/files/mkdir/${encodePath(currentPath)}?name=${encodeURIComponent(name)}` : `/files/mkdir/?name=${encodeURIComponent(name)}`;
  mkdirBtn.disabled = true;
  try {
    const res = await fetch(url, { method: "POST" });
    if (!res.ok) throw new Error(await res.text());
    await list(currentPath);
  } catch (e) {
    alert("Error al crear carpeta: " + e.message);
  } finally {
    mkdirBtn.disabled = false;
  }
};

// iniciar en root
list("");