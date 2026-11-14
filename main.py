import os, sys
APP = os.path.dirname(os.path.abspath(__file__))
os.chdir(APP)
sys.path.insert(0, APP)
from http.server import HTTPServer
import run
print("CodeLearn server on 8085")
HTTPServer(("127.0.0.1", 8085), run.H).serve_forever()
