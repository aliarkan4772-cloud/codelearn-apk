import os, json, sqlite3, datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import multiprocessing, io, ast, sys

# --- کدهای هسته امنیتی (درون خود فایل برای اطمینان) ---
def worker(code, stdin_data, ret):
    out = io.StringIO()
    sys.stdout = sys.stderr = out
    sys.stdin = io.StringIO(stdin_data)
    try:
        tree = ast.parse(code)
        exec(compile(tree, "<code_user>", "exec"), {"__builtins__": __builtins__})
        ret["OK"], ret["OUT"], ret["ERR"] = True, out.getvalue().strip(), ""
    except Exception as e:
        ret["OK"], ret["OUT"], ret["ERR"] = False, out.getvalue().strip(), str(e)

def run_safe(code, stdin_data=""):
    m = multiprocessing.Manager()
    ret = m.dict()
    p = multiprocessing.Process(target=worker, args=(code, stdin_data, ret))
    p.start()
    p.join(3.0)
    if p.is_alive():
        p.terminate()
        return {"OK": False, "OUT": "", "ERR": "زمان اجرا بیش از ۳ ثانیه شد."}
    return dict(ret)

from db import auth_user, get_conn

HTML = """<!DOCTYPE html><html lang="fa" dir="rtl"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>CodeLearn Pro - v6</title>
<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
<style>
:root { --bg: #0f172a; --card: #1e293b; --prim: #38bdf8; --accent: #a855f7; --gold: #fbbf24; --success: #22c55e; }
body{background:var(--bg);color:#f8fafc;font-family:Tahoma,sans-serif;margin:0;padding:0;user-select:none;padding-bottom:75px}
.card{background:var(--card);border:1px solid #334155;border-radius:14px;padding:14px;margin:10px}
.btn{width:100%;padding:12px;border:none;border-radius:10px;background:#0284c7;color:#fff;font-weight:bold;font-size:15px;margin-top:8px;cursor:pointer;transition:0.2s}
.btn:active{transform:scale(0.98)} .btn-sec{background:#475569} 
input, select{width:100%;padding:12px;margin-top:8px;border-radius:10px;border:1px solid #475569;background:#090d16;color:#fff;box-sizing:border-box}
#cert-page { background: white; color: #1e293b; padding: 40px; border: 15px solid #1e293b; text-align: center; position: relative; margin: 10px; border-radius: 5px; box-shadow: 0 0 20px rgba(0,0,0,0.5); }
.cert-title { font-size: 30px; font-weight: bold; color: #1e293b; margin-bottom: 20px; border-bottom: 2px solid #38bdf8; display: inline-block; }
.cert-name { font-size: 25px; color: #a855f7; margin: 20px 0; font-family: 'Times New Roman', serif; }
.editor-container { position: relative; width: 100%; height: 200px; background: #060910; border-radius: 10px; border: 1px solid #475569; overflow: hidden; }
#ed, #hl { position: absolute; top:0; left:0; width:100%; height:100%; padding:10px; font-family:monospace; font-size:16px; line-height:1.5; white-space:pre-wrap; outline:none; border:none; }
#ed { background:transparent; color:transparent; caret-color:white; z-index:2; resize:none; }
#hl { z-index:1; color:#f8fafc; pointer-events:none; }
.kw { color: #f472b6; font-weight: bold; } .str { color: #fbbf24; }
.item{display:flex;justify-content:space-between;align-items:center;padding:15px;cursor:pointer;border-bottom:1px solid #334155}
.bottom-nav { position: fixed; bottom: 0; width: 100%; height: 65px; background: #0f172a; border-top: 1px solid #334155; display: flex; justify-content: space-around; align-items: center; }
.nav-item { color: #94a3b8; font-size: 12px; text-align: center; cursor: pointer; }
.nav-item.active { color: var(--prim); font-weight: bold; }
.hide{display:none}
</style></head><body>

<div id="auth-page" class="card" style="margin-top:50px">
    <h2 style="text-align:center;color:var(--prim)">CodeLearn Pro 🐍</h2>
    <input type="text" id="user" placeholder="نام کاربری">
    <input type="password" id="pass" placeholder="رمز عبور">
    <button class="btn" onclick="handleAuth(false)">ورود</button>
    <button class="btn btn-sec" onclick="handleAuth(true)">ثبت‌نام</button>
</div>

<div id="main-content" class="hide">
    <header class="card" style="display:flex;justify-content:space-between;align-items:center">
        <div><b id="display-user"></b> <br><small id="display-xp" style="color:var(--prim)"></small></div>
        <button onclick="location.reload()" style="background:none;border:none;color:#ef4444">خروج</button>
    </header>
    <div id="tab-lessons">
        <div id="cert-notif" class="card hide" style="background:linear-gradient(45deg, #10b981, #3b82f6); border:none; text-align:center">
            <h3 style="margin:0">🎓 تبریک! دوره تمام شد</h3>
            <button class="btn" style="background:#fff; color:#000; margin-top:10px" onclick="showCert()">دریافت گواهی‌نامه</button>
        </div>
        <button id="admin-btn" class="btn hide" style="background:var(--accent);margin:10px;width:calc(100% - 20px)" onclick="showAdmin()">🛠 مدیریت محتوا</button>
        <div id="lessons-list" class="card" style="padding:0"></div>
    </div>
    <div id="tab-leaderboard" class="hide">
        <div class="card"><h3 style="text-align:center;color:var(--accent)">🏆 برترین‌ها</h3><div id="leaderboard-list"></div></div>
    </div>
</div>

<div id="admin-page" class="hide">
    <button class="btn btn-sec" onclick="switchTab('lessons')">🔙 بازگشت</button>
    <div class="card">
        <h3 style="color:var(--accent)">➕ افزودن درس جدید</h3>
        <input type="text" id="a-title" placeholder="عنوان درس">
        <input type="text" id="a-desc" placeholder="توضیحات">
        <input type="text" id="a-starter" placeholder="کد اولیه">
        <input type="text" id="a-expected" placeholder="خروجی هدف">
        <select id="a-free"><option value="1">رایگان</option><option value="0">ویژه</option></select>
        <button class="btn" onclick="addLesson()">ذخیره درس</button>
    </div>
</div>

<div id="view-cert" class="hide">
    <button class="btn btn-sec" onclick="switchTab('lessons')" style="margin:10px; width:auto">🔙 بازگشت</button>
    <div id="cert-page">
        <div class="cert-title">CERTIFICATE</div>
        <p>بدین‌وسیله گواهی می‌شود که</p>
        <div class="cert-name" id="cert-user-name"></div>
        <p>با موفقیت دوره پایتون را در <b>CodeLearn</b> به پایان رسانده است.</p>
        <br><div style="display:flex; justify-content:space-between; margin-top:30px"><div>تاریخ: <span id="cert-date"></span></div><div>امضا: <b>CodeLearn</b></div></div>
    </div>
</div>

<div id="editor-page" class="hide">
    <div class="card">
        <button class="btn btn-sec" style="width:auto" onclick="switchTab('lessons')">🔙 بازگشت</button>
        <h3 id="lt" style="color:var(--prim);margin-top:10px"></h3>
        <p id="ld" style="font-size:14px"></p>
    </div>
    <div class="card">
        <div class="editor-container"><div id="hl"></div><textarea id="ed" spellcheck="false" oninput="updateHl()" onscroll="sync()"></textarea></div>
        <button id="run-btn" class="btn" onclick="runCode()">▶ اجرا و بررسی</button>
        <div id="out" class="box hide"></div>
    </div>
</div>

<nav id="navbar" class="bottom-nav hide">
    <div class="nav-item active" id="nav-l" onclick="switchTab('lessons')">📚<br>درس‌ها</div>
    <div class="nav-item" id="nav-r" onclick="switchTab('leaderboard')">🏆<br>رتبه</div>
</nav>

<script>
let userData = null; let currentLesson = null;
async function handleAuth(isReg) {
    const u = document.getElementById("user").value; const p = document.getElementById("pass").value;
    const res = await fetch("/api/auth", {method:"POST", body:JSON.stringify({u, p, isReg})});
    const data = await res.json(); if(data.ok) { userData = data.user; startApp(); } else alert(data.msg);
}
function startApp() {
    document.getElementById("auth-page").classList.add("hide");
    document.getElementById("main-content").classList.remove("hide");
    document.getElementById("navbar").classList.remove("hide");
    document.getElementById("display-user").innerText = userData.username;
    document.getElementById("display-xp").innerText = userData.xp + " XP";
    if(userData.is_admin) document.getElementById("admin-btn").classList.remove("hide");
    switchTab('lessons');
}
function switchTab(tab) {
    document.body.querySelectorAll("body > div:not(#navbar)").forEach(d => d.classList.add("hide"));
    if(tab === 'lessons') { document.getElementById("main-content").classList.remove("hide"); document.getElementById("tab-lessons").classList.remove("hide"); loadLessons(); }
    else if(tab === 'leaderboard') { document.getElementById("main-content").classList.remove("hide"); document.getElementById("tab-leaderboard").classList.remove("hide"); loadLeaderboard(); }
}
async function loadLessons() {
    const res = await fetch("/api/get_lessons"); const lessons = await res.json();
    let h = ""; lessons.forEach(l => {
        const isDone = userData.completed.includes(l.id);
        h += `<div class="item" onclick="openLesson(${l.id})"><div><b>${l.id}. ${l.title}</b></div><span>${isDone ? '✅' : '⏳'}</span></div>`;
    });
    document.getElementById("lessons-list").innerHTML = h;
    if(userData.completed.length >= lessons.length && lessons.length > 0) document.getElementById("cert-notif").classList.remove("hide");
}
async function loadLeaderboard() {
    const res = await fetch("/api/leaderboard"); const top = await res.json();
    let h = ""; top.forEach((u, i) => h += `<div class="item"><span>${i+1}. ${u.username}</span><b>${u.xp} XP</b></div>`);
    document.getElementById("leaderboard-list").innerHTML = h;
}
function openLesson(id) {
    fetch("/api/get_lesson_detail?id="+id).then(r => r.json()).then(l => {
        currentLesson = l; document.getElementById("main-content").classList.add("hide");
        document.getElementById("editor-page").classList.remove("hide");
        document.getElementById("lt").innerText = l.title; document.getElementById("ld").innerText = l.desc;
        document.getElementById("ed").value = l.starter; updateHl();
    });
}
function updateHl() {
    let code = document.getElementById("ed").value; let text = code.replace(/&/g, "&amp;").replace(/</g, "&lt;");
    const kw = ["print", "if", "else", "for", "while", "def", "return", "input", "int"];
    kw.forEach(k => { text = text.replace(new RegExp("\\\\b"+k+"\\\\b", "g"), `<span class="kw">${k}</span>`); });
    document.getElementById("hl").innerHTML = text + "\\n";
}
function sync() { document.getElementById("hl").scrollTop = document.getElementById("ed").scrollTop; }
async function runCode() {
    const code = document.getElementById("ed").value;
    const res = await fetch("/api/run", {method:"POST", body:JSON.stringify({code, lesson_id: currentLesson.id, user: userData.username})});
    const d = await res.json(); const o = document.getElementById("out"); o.classList.remove("hide");
    if(d.ok && d.out === currentLesson.expected) {
        o.style.color="var(--success)"; o.innerText="✅ درست بود! امتیاز گرفتی.";
        confetti({ particleCount: 150, spread: 70, origin: { y: 0.6 } });
        userData.xp = d.new_xp; userData.completed = d.new_completed;
        document.getElementById("display-xp").innerText = userData.xp + " XP";
    } else { o.style.color="#f87171"; o.innerText="❌ خطا یا خروجی اشتباه:\\n" + (d.err || d.out); }
}
function showCert() {
    document.getElementById("main-content").classList.add("hide");
    document.getElementById("view-cert").classList.remove("hide");
    document.getElementById("cert-user-name").innerText = userData.username.toUpperCase();
    document.getElementById("cert-date").innerText = new Date().toLocaleDateString('fa-IR');
}
function showAdmin() {
    document.getElementById("main-content").classList.add("hide");
    document.getElementById("admin-page").classList.remove("hide");
}
async function addLesson() {
    const data = {
        title: document.getElementById("a-title").value, desc: document.getElementById("a-desc").value,
        starter: document.getElementById("a-starter").value, expected: document.getElementById("a-expected").value,
        is_free: document.getElementById("a-free").value
    };
    await fetch("/api/add_lesson", {method:"POST", body:JSON.stringify(data)});
    alert("درس اضافه شد!"); switchTab('lessons');
}
</script></body></html>"""

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        conn = get_conn(); c = conn.cursor()
        if self.path == "/api/leaderboard":
            c.execute("SELECT username, xp FROM users ORDER BY xp DESC LIMIT 10")
            res = json.dumps([dict(r) for r in c.fetchall()])
        elif self.path.startswith("/api/get_lesson_detail"):
            lid = self.path.split("=")[1]; c.execute("SELECT * FROM lessons WHERE id=?", (lid,))
            res = json.dumps(dict(c.fetchone()))
        elif self.path == "/api/get_lessons":
            c.execute("SELECT id, title, is_free FROM lessons")
            res = json.dumps([dict(r) for r in c.fetchall()])
        else:
            self.send_response(200); self.send_header("Content-Type","text/html;charset=utf-8"); self.end_headers()
            return self.wfile.write(HTML.encode())
        conn.close(); self.send_response(200); self.send_header("Content-Type","application/json"); self.end_headers()
        self.wfile.write(res.encode())
    def do_POST(self):
        length = int(self.headers["Content-Length"])
        body = json.loads(self.rfile.read(length).decode())
        conn = get_conn(); c = conn.cursor()
        if self.path == "/api/auth":
            res = auth_user(body["u"], body["p"], body["isReg"])
        elif self.path == "/api/add_lesson":
            c.execute("INSERT INTO lessons (title, desc, starter, expected, is_free) VALUES (?,?,?,?,?)", (body["title"], body["desc"], body["starter"], body["expected"], body["is_free"]))
            conn.commit(); res = {"ok": True}
        elif self.path == "/api/run":
            c.execute("SELECT expected FROM lessons WHERE id=?", (body["lesson_id"],))
            expected = c.fetchone()["expected"]
            exec_res = run_safe(body["code"])
            if exec_res["OK"] and exec_res["OUT"] == expected:
                c.execute("SELECT xp, completed FROM users WHERE username=?", (body["user"],))
                u = c.fetchone(); comp = json.loads(u["completed"]); new_xp = u["xp"]
                if body["lesson_id"] not in comp: new_xp += 50; comp.append(body["lesson_id"])
                c.execute("UPDATE users SET xp=?, completed=? WHERE username=?", (new_xp, json.dumps(comp), body["user"]))
                conn.commit(); exec_res.update({"new_xp": new_xp, "new_completed": comp})
            exec_res["ok"]=exec_res.pop("OK"); exec_res["out"]=exec_res.pop("OUT"); exec_res["err"]=exec_res.pop("ERR"); res = exec_res
        conn.close(); self.send_response(200); self.send_header("Content-Type","application/json"); self.end_headers()
        self.wfile.write(json.dumps(res).encode())

if __name__ == "__main__":
    print("🚀 CodeLearn v6 Online -> http://127.0.0.1:8085")
    HTTPServer(("127.0.0.1", 8085), H).serve_forever()
