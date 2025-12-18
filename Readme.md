NAS INITIALIZATION<br>
install python and pip<br>
navigate to the root of the directory and run these commands:<br>
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./run.sh
```
<br>
You can edit the port and the listening IP and port by modifying the run.sh file.<br>
Whenever you upload a file, it will be places on the current directory you have <br>
pressed "Upload file". Make sure you are on the desired directory before uploading.<br>
<br>Have fun!<br>

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

```
app/		--> Codebase
routes/		--> Only HTTP (FastApi)
services/	--> Logic (filesystem)
storage/	--> Files and directories saved and served
```




