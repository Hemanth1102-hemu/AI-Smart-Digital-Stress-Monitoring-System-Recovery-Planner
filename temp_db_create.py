import pymysql

try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='Hemanth1102@'
    )
    with connection.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS stress_monitoring_db;")
    connection.commit()
    print("Database stress_monitoring_db created successfully.")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'connection' in locals() and connection.open:
        connection.close()
