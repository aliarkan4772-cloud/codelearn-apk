p = "run.py"
s = open(p, encoding="utf-8").read()
old = """async function loadLessons() {
    const res = await fetch("/api/get_lessons"); const lessons = await res.json();
    let h = ""; lessons.forEach(l => {
        const isDone = userData.completed.includes(l.id);
        h += `<div class="item" onclick="openLesson(${l.id})"><div><b>${l.id}. ${l.title}</b></div><span>${isDone ? '✅' : '⏳'}</span></div>`;
    });
    document.getElementById("lessons-list").innerHTML = h;
    if(userData.completed.length >= lessons.length && lessons.length > 0) document.getElementById("cert-notif").classList.remove("hide");
}"""
new = """async function loadLessons() {
    const box = document.getElementById("lessons-list");
    box.innerHTML = '<div style="padding:20px;text-align:center;color:#94a3b8">در حال بارگذاری درس‌ها...</div>';
    let lessons = [];
    try { const res = await fetch("/api/get_lessons"); lessons = await res.json(); }
    catch(e) { box.innerHTML = '<div style="padding:20px;text-align:center;color:#f87171">اتصال به سرور برقرار نشد. اپ را ببند و دوباره باز کن.</div>'; return; }
    if(!lessons.length) {
        box.innerHTML = '<div style="padding:25px;text-align:center;line-height:2"><div style="font-size:34px">📭</div><b>هنوز درسی ثبت نشده</b><br><small style="color:#94a3b8">با حساب admin وارد شو و از «مدیریت محتوا» درس اضافه کن</small></div>';
        return;
    }
    const done = lessons.filter(l => userData.completed.includes(l.id)).length;
    let h = `<div style="padding:12px 15px;border-bottom:1px solid #334155;display:flex;justify-content:space-between;align-items:center"><b style="color:var(--prim)">📚 ${lessons.length} درس</b><small style="color:#94a3b8">${done} انجام شده</small></div>`;
    lessons.forEach(l => {
        const isDone = userData.completed.includes(l.id);
        const tag = l.is_free ? "" : ' <span style="color:var(--gold);font-size:11px">ویژه</span>';
        h += `<div class="item" onclick="openLesson(${l.id})"><div><b>${l.id}. ${l.title}</b>${tag}</div><span>${isDone ? '✅' : '⏳'}</span></div>`;
    });
    box.innerHTML = h;
    if(done >= lessons.length) document.getElementById("cert-notif").classList.remove("hide");
    else document.getElementById("cert-notif").classList.add("hide");
}"""
if old in s:
    s = s.replace(old, new)
    open(p, "w", encoding="utf-8").write(s)
    compile(s, p, "exec")
    print("LESSONS UI PATCH OK")
else:
    print("SKIP: already patched")
