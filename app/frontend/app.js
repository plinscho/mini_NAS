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

function isVideo(name){ const ext = name.split('.').pop().toLowerCase(); return ['mp4','webm','ogg','mov'].includes(ext); }
function isImage(name){ const ext = name.split('.').pop().toLowerCase(); return ['png','jpg','jpeg','gif','webp','bmp'].includes(ext); }
function isAudio(name){ const ext = name.split('.').pop().toLowerCase(); return ['mp3','wav','ogg','m4a'].includes(ext); }

function createPreviewModal(){
  let modal = document.getElementById("previewModal");
  if (modal) return modal;
  modal = document.createElement("div");
  modal.id = "previewModal";
  modal.className = "modal";
  modal.style.display = "none";
  modal.innerHTML = `
    <div class="modal-content">
      <button id="closePreview" class="close">Close</button>
      <div id="previewBody"></div>
    </div>`;
  document.body.appendChild(modal);
  modal.querySelector("#closePreview").onclick = () => modal.style.display = "none";
  return modal;
}

function previewFile(filePath, name){
  const modal = createPreviewModal();
  const body = modal.querySelector("#previewBody");
  body.innerHTML = "";
  const src = `/files/stream/${encodePath(filePath)}`;
  if (isImage(name)){
    const img = document.createElement("img");
    img.src = src;
    img.alt = name;
    body.appendChild(img);
  } else if (isVideo(name)){
    const video = document.createElement("video");
    video.controls = true;
    video.src = src;
    video.style.maxWidth = "100%";
    body.appendChild(video);
  } else if (isAudio(name)){
    const audio = document.createElement("audio");
    audio.controls = true;
    audio.src = src;
    body.appendChild(audio);
  } else {
    body.innerHTML = `<div class="hint">No preview available. <a href="/files/download/${encodePath(filePath)}" target="_blank" rel="noopener">Download</a></div>`;
  }
  modal.style.display = "flex";
}

async function list(path = "") {
  currentPath = path;
  // Habilitar o deshabilitar botón de subir (ir al padre)
  upBtn.disabled = !currentPath;
  breadcrumbs.textContent = "/" + path;
  const url = path ? `/files/${encodePath(path)}` : `/files/`;
  listing.innerHTML = "Loading...";
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
    listing.innerHTML = "<div class='empty'>Empty folder</div>";
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
      open.textContent = "Open";
      open.onclick = () => list(next);
      li.appendChild(open);

      const renameBtn = document.createElement("button");
      renameBtn.textContent = "Rename";
      renameBtn.onclick = async () => {
        const newName = prompt("New name:", it.name);
        if (!newName) return;
        if (newName.includes("/")) return alert("Name cannot contain '/'.");
        renameBtn.disabled = true;
        try {
          const res = await fetch(`/files/rename/${encodePath(next)}?name=${encodeURIComponent(newName)}`, { method: "POST" });
          if (!res.ok) throw new Error(await res.text());
          // If we renamed the folder we're viewing, navigate to the new folder
          if (currentPath === next) {
            const parts = currentPath.split("/");
            parts.pop();
            const parent = parts.filter(Boolean).join("/");
            await list(parent);
            // open the renamed folder
            await list(parent ? `${parent}/${newName}` : newName);
          } else {
            await list(currentPath);
          }
        } catch (e) {
          alert("Error renaming folder: " + e.message);
        } finally {
          renameBtn.disabled = false;
        }
      };
      li.appendChild(renameBtn);

      const del = document.createElement("button");
      del.textContent = "Delete";
      del.className = "delete";
      del.onclick = async () => {
        if (!confirm(`Delete folder ${next}? This will delete all its contents.`)) return;
        del.disabled = true;
        try {
          const res = await fetch(`/files/delete-dir/${encodePath(next)}?recursive=1`, { method: "DELETE" });
          if (!res.ok) throw new Error(await res.text());
          // If we deleted the folder we're viewing, go up
          if (next === currentPath) {
            const parts = currentPath.split("/");
            parts.pop();
            const parent = parts.filter(Boolean).join("/");
            await list(parent);
          } else {
            await list(currentPath);
          }
        } catch (e) {
          alert("Error deleting folder: " + e.message);
          del.disabled = false;
        }
      };
      li.appendChild(del);
    } else {
      const filePath = currentPath ? `${currentPath}/${it.name}` : it.name;

      const previewBtn = document.createElement("button");
      previewBtn.textContent = "Preview";
      previewBtn.onclick = () => previewFile(filePath, it.name);
      li.appendChild(previewBtn);

      const renameBtn = document.createElement("button");
      renameBtn.textContent = "Rename";
      renameBtn.onclick = async () => {
        const newName = prompt("New name:", it.name);
        if (!newName) return;
        if (newName.includes("/")) return alert("Name cannot contain '/'.");
        renameBtn.disabled = true;
        try {
          const res = await fetch(`/files/rename/${encodePath(filePath)}?name=${encodeURIComponent(newName)}`, { method: "POST" });
          if (!res.ok) throw new Error(await res.text());
          await list(currentPath);
        } catch (e) {
          alert("Error renaming file: " + e.message);
        } finally {
          renameBtn.disabled = false;
        }
      };
      li.appendChild(renameBtn);

      const dl = document.createElement("a");
      dl.href = `/files/download/${encodePath(filePath)}`;
      dl.textContent = "Download";
      dl.className = "download";
      li.appendChild(dl);

      const del = document.createElement("button");
      del.textContent = "Delete";
      del.className = "delete";
      del.onclick = async () => {
        if (!confirm(`Delete ${filePath}?`)) return;
        del.disabled = true;
        try {
          const res = await fetch(`/files/delete/${encodePath(filePath)}`, { method: "DELETE" });
          if (!res.ok) throw new Error(await res.text());
          await list(currentPath);
        } catch (e) {
          alert("Error deleting: " + e.message);
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

// open selector with single button
uploadBtn.onclick = () => fileInput.click();

// automatic upload on file selection
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
    alert("Upload error: " + e.message);
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
  const name = prompt("Name of the new folder:");
  if (!name) return;
  if (name.includes("/")) return alert("Name cannot contain '/'.");

  const url = currentPath ? `/files/mkdir/${encodePath(currentPath)}?name=${encodeURIComponent(name)}` : `/files/mkdir/?name=${encodeURIComponent(name)}`;
  mkdirBtn.disabled = true;
  try {
    const res = await fetch(url, { method: "POST" });
    if (!res.ok) throw new Error(await res.text());
    await list(currentPath);
  } catch (e) {
    alert("Error creating folder: " + e.message);
  } finally {
    mkdirBtn.disabled = false;
  }
};

// iniciar en root
list("");