NAS INITIALIZATION
install python and pip
navigate to the root of the directory and run these commands:
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./run.sh
```

You can edit the port and the listening IP and port by modifying the run.sh file.
Whenever you upload a file, it will be places on the current directory you have 
pressed "Upload file". Make sure you are on the desired directory before uploading.
Have fun!

----------------------------------------------------
NAS STRUCTURE
```
mini-nas/
├── app/
│   ├── frontend
│   │   └── app.js
│   │   └── index.html
│   │   └── styles.css
│   ├── main.py
│   ├── config.py
│   ├── routes/
│   │   └── files.py
│   └── services/
│       └── filesystem.py
├── storage/
│   └── .keep
└── requirements.txt
```

app/		--> Codebase
routes/		--> Only HTTP (FastApi)
services/	--> Logic (filesystem)
storage/	--> Files and directories saved and served





