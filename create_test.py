import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="rental_2",
        user="postgres",
        password="yourpassword",   # замените на свой пароль!
        client_encoding="UTF8"
    )
    print("Соединение установлено!")
    conn.close()
except Exception as e:
    print("Ошибка подключения:", e)