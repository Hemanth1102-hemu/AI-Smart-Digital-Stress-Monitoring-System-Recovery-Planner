import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb

try:
    db = MySQLdb.connect(
        host="localhost",
        user="root",
        passwd="Hemanth1102@",
        db="stress_monitoring_db",
        port=3306
    )
    print("Connection successful!")
    db.close()
except Exception as e:
    print(f"Connection failed: {e}")
