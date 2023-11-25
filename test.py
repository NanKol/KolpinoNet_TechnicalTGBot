import sqlite3
from datetime import datetime

with sqlite3.connect("test.db") as con:
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    date = datetime.now()#.strftime('%Y-%m-%d %H:%M:%S')
    print(date)
    cur.execute(f"""UPDATE troubles SET date_start = '{date}', date_end = 0, plan_time = 0 WHERE id in (2, 3)""")