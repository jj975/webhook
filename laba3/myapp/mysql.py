import pymysql
from myapp.credentials import HOSTDB, DBNAME, PORTDB, USERDB, PASSDB, TIMEOUT
timeout = TIMEOUT
connection = pymysql.connect(
    charset="utf8mb4",
    connect_timeout=timeout,
    cursorclass=pymysql.cursors.DictCursor,
    db=DBNAME,
    host=HOSTDB,
    password=PASSDB,
    read_timeout=timeout,
    port=PORTDB,
    user=USERDB,
    write_timeout=timeout,
)

try:
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE mytest (id INTEGER PRIMARY KEY)")
    cursor.execute("INSERT INTO mytest (id) VALUES (1), (2)")
    cursor.execute("SELECT * FROM mytest")
    print(cursor.fetchall())
finally:
    connection.close()
