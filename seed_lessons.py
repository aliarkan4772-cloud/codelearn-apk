import sqlite3
conn = sqlite3.connect("codelearn_pro.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS lessons (id INTEGER PRIMARY KEY, title TEXT, desc TEXT, starter TEXT, expected TEXT, stdin TEXT, hint TEXT, is_free INTEGER DEFAULT 1)")
if c.execute("SELECT COUNT(*) FROM lessons").fetchone()[0] > 0:
    print("Lessons already exist - nothing changed")
else:
    L = [
     ("سلام پایتون!", "تابع print متن را چاپ می‌کند.\nتمرین: عبارت Hello World را دقیقاً چاپ کن.", 'print("Hello World")', "Hello World", "", "متن داخل کوتیشن با همین حروف", 1),
     ("جمع ساده", "پایتون مثل ماشین‌حساب است.\nتمرین: حاصل 12 + 30 را چاپ کن.", "print(12 + 30)", "42", "", "از عملگر + استفاده کن", 1),
     ("متغیرها", "متغیر مقدار را نگه می‌دارد.\nتمرین: به name مقدار Ali بده و چاپش کن.", 'name = ""\nprint(name)', "Ali", "", "داخل کوتیشن بنویس Ali", 1),
     ("توان", "عملگر ** توان است.\nتمرین: 2 به توان 5 را چاپ کن.", "print(2 ** 5)", "32", "", "از ** استفاده کن", 1),
     ("تکرار رشته", "رشته قابل تکرار است.\nتمرین: ha را سه بار پشت سر هم چاپ کن.", 'print("ha" * 3)', "hahaha", "", "رشته را در 3 ضرب کن", 1),
     ("حلقه for", "حلقه کار را تکرار می‌کند.\nتمرین: اعداد 0 تا 4 را هرکدام در یک خط چاپ کن.", "for i in range(5):\n    print(i)", "0\n1\n2\n3\n4", "", "از range(5) استفاده کن", 1),
     ("شرط if", "با if تصمیم می‌گیریم.\nتمرین: چون 10 بزرگ‌تر از 5 است big را چاپ کن.", 'x = 10\nif x > 5:\n    print("big")', "big", "", "بعد از if علامت : و تورفتگی لازم است", 1),
     ("لیست‌ها", "لیست مجموعه‌ای از داده‌هاست.\nتمرین: لیست اعداد 1 و 2 و 3 را بساز و چاپ کن.", "my_list = []\nprint(my_list)", "[1, 2, 3]", "", "اعداد 1, 2, 3 را داخل [] بگذار", 1),
     ("عضو اول لیست", "شماره‌گذاری از 0 شروع می‌شود.\nتمرین: عضو اول nums را چاپ کن.", "nums = [10, 20, 30]\nprint(nums[0])", "10", "", "از nums[0] استفاده کن", 0),
     ("دیکشنری", "دیکشنری یعنی کلید و مقدار.\nتمرین: مقدار کلید age را چاپ کن.", "user = {'name': 'Ali', 'age': 25}\nprint(user['age'])", "25", "", "از user['age'] استفاده کن", 0),
     ("تابع بساز", "با def تابع می‌سازی.\nتمرین: خروجی double(7) را چاپ کن.", "def double(n):\n    return n * 2\n\nprint(double(7))", "14", "", "از return استفاده کن", 0),
     ("کتابخانه math", "کتابخانه ابزار آماده دارد.\nتمرین: جذر 16 را چاپ کن.", "import math\nprint(math.sqrt(16))", "4.0", "", "اول import math بنویس", 0),
    ]
    c.executemany("INSERT INTO lessons (title,desc,starter,expected,stdin,hint,is_free) VALUES (?,?,?,?,?,?,?)", L)
    conn.commit()
    print("Added", len(L), "lessons OK")
conn.close()
