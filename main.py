import os, sys, shutil, sqlite3
APP = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("ANDROID_PRIVATE") or os.path.join(os.path.expanduser("~"), ".codelearn")
os.makedirs(DATA, exist_ok=True)
SRC = os.path.join(APP, "codelearn_pro.db")
DST = os.path.join(DATA, "codelearn_pro.db")
if not os.path.exists(DST):
    if os.path.exists(SRC):
        shutil.copyfile(SRC, DST)
    else:
        sqlite3.connect(DST).close()
os.chdir(DATA)
sys.path.insert(0, APP)
from http.server import HTTPServer
import run
print("CodeLearn server on 8085")
HTTPServer(("127.0.0.1", 8085), run.H).serve_forever()
