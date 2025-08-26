import sqlite3
import os

# Создаём файл базы данных
db_file = 'real_estate.db'
if os.path.exists(db_file):
    os.remove(db_file)

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Создание таблиц
cursor.execute('''
CREATE TABLE Residential_complex (
    complex_id INTEGER PRIMARY KEY,
    complex_name TEXT,
    city TEXT,
    street TEXT,
    subway TEXT,
    subway_nearest REAL,
    childrens_playground INTEGER,
    sports_ground INTEGER
);
''')

cursor.execute('''
CREATE TABLE Object_types (
    object_type INTEGER PRIMARY KEY,
    name_object TEXT
);
''')

cursor.execute('''
CREATE TABLE Buildings (
    building_id INTEGER PRIMARY KEY,
    complex_id INTEGER,
    city TEXT,
    street TEXT,
    house_number TEXT,
    day_commissioning TEXT,
    type_housing TEXT,
    estate_class TEXT,
    wall_material TEXT,
    parking INTEGER,
    floors_total INTEGER,
    FOREIGN KEY (complex_id) REFERENCES Residential_complex(complex_id)
);
''')

cursor.execute('''
CREATE TABLE Objects (
    object_id INTEGER PRIMARY KEY,
    complex_id INTEGER,
    building_id INTEGER,
    number_object TEXT,
    cadastral_number TEXT,
    object_type INTEGER,
    total_area REAL,
    living_area REAL,
    studio INTEGER,
    rooms INTEGER,
    bathrooms INTEGER,
    bedrooms INTEGER,
    floor INTEGER,
    finish_type TEXT,
    ceiling_height REAL,
    sold INTEGER,
    price REAL,
    FOREIGN KEY (complex_id) REFERENCES Residential_complex(complex_id),
    FOREIGN KEY (building_id) REFERENCES Buildings(building_id),
    FOREIGN KEY (object_type) REFERENCES Object_types(object_type)
);
''')

cursor.execute('''
CREATE TABLE Staff (
    staff_id INTEGER PRIMARY KEY,
    last_name TEXT,
    first_name TEXT,
    patronymic TEXT,
    job_title TEXT,
    email TEXT
);
''')

cursor.execute('''
CREATE TABLE Clients (
    client_id INTEGER PRIMARY KEY,
    last_name TEXT,
    first_name TEXT,
    patronymic TEXT,
    phone TEXT,
    email TEXT,
    gender TEXT,
    age TEXT,
    family_status TEXT,
    children INTEGER,
    home_address TEXT
);
''')

cursor.execute('''
CREATE TABLE Orders (
    order_id INTEGER PRIMARY KEY,
    order_type TEXT,
    client_id INTEGER,
    staff_id INTEGER,
    complex_id INTEGER,
    building_id INTEGER,
    object_id INTEGER,
    total_amount REAL,
    payment_terms TEXT,
    discount_amount REAL,
    order_date TEXT,
    order_status TEXT,
    FOREIGN KEY (client_id) REFERENCES Clients(client_id),
    FOREIGN KEY (staff_id) REFERENCES Staff(staff_id),
    FOREIGN KEY (complex_id) REFERENCES Residential_complex(complex_id),
    FOREIGN KEY (building_id) REFERENCES Buildings(building_id),
    FOREIGN KEY (object_id) REFERENCES Objects(object_id)
);
''')

cursor.execute('''
CREATE TABLE Order_items (
    order_id INTEGER,
    object_id INTEGER,
    sale_price REAL,
    PRIMARY KEY (order_id, object_id),
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (object_id) REFERENCES Objects(object_id)
);
''')

cursor.execute('''
CREATE TABLE Payment_schedule (
    schedule_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    scheduled_date TEXT,
    scheduled_amount REAL,
    is_paid INTEGER,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
);
''')

cursor.execute('''
CREATE TABLE Transactions (
    transaction_id INTEGER PRIMARY KEY,
    schedule_id INTEGER,
    payment_amount REAL,
    transaction_date TEXT,
    payment_method TEXT,
    FOREIGN KEY (schedule_id) REFERENCES Payment_schedule(schedule_id)
);
''')

# Заполнение данными
# Object_types (добавлены 'Кладовка' и 'Парковка')
cursor.executemany('''
INSERT INTO Object_types (object_type, name_object)
VALUES (?, ?)
''', [
    (1, 'Квартира'),
    (2, 'Апартаменты'),
    (3, 'Студия'),
    (4, 'Кладовка'),
    (5, 'Парковка')
] + [(i+6, f'Тип {i}') for i in range(25)])

# Residential_complex (30 записей)
residential_data = []
for i in range(1, 31):
    residential_data.append((
        i,
        f'Комплекс {i}',
        ['Москва', 'Санкт-Петербург', 'Новосибирск'][i % 3],
        f'Улица {i}',
        f'Метро {i}',
        round(0.1 * (i % 10) + 0.5, 1),
        i % 2,
        (i + 1) % 2
    ))
cursor.executemany('''
INSERT INTO Residential_complex (complex_id, complex_name, city, street, subway, subway_nearest, childrens_playground, sports_ground)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', residential_data)

# Buildings (30 записей)
buildings_data = []
for i in range(1, 31):
    buildings_data.append((
        i,
        (i % 30) + 1,
        ['Москва', 'Санкт-Петербург', 'Новосибирск'][i % 3],
        f'Улица {i}',
        f'{i*2}',
        f'202{i % 10 + 1}-0{i % 9 + 1}-01',
        ['residential_building', 'apartment'][i % 2],
        ['Бизнес', 'Эконом', 'Премиум'][i % 3],
        ['Кирпич', 'Панель', 'Монолит'][i % 3],
        i % 2,
        10 + i % 20
    ))
cursor.executemany('''
INSERT INTO Buildings (building_id, complex_id, city, street, house_number, day_commissioning, type_housing, estate_class, wall_material, parking, floors_total)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', buildings_data)

# Objects (30 записей)
objects_data = []
for i in range(1, 31):
    obj_type = (i % 5) + 1
    total_area = 20 + i * 2.5
    living_area = total_area * 0.7 if obj_type in [1,2,3] else None
    studio = 1 if obj_type == 3 else 0
    rooms = (i % 4) + 1 if obj_type in [1,2] else 0
    bathrooms = (i % 2) + 1 if obj_type in [1,2,3] else 0
    bedrooms = rooms - 1 if rooms else 0
    objects_data.append((
        i,
        (i % 30) + 1,
        (i % 30) + 1,
        f'{100 + i}',
        f'77:01:0001{i:03d}:101',
        obj_type,
        total_area,
        living_area,
        studio,
        rooms,
        bathrooms,
        bedrooms,
        (i % 25) + 1,
        ['Черновая', 'Чистовая', 'Дизайнерская'][i % 3],
        2.5 + (i % 5) * 0.1,
        i % 2,
        1000000 + i * 100000
    ))
cursor.executemany('''
INSERT INTO Objects (object_id, complex_id, building_id, number_object, cadastral_number, object_type, total_area, living_area, studio, rooms, bathrooms, bedrooms, floor, finish_type, ceiling_height, sold, price)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', objects_data)

# Staff (30 записей)
staff_data = []
for i in range(1, 31):
    staff_data.append((
        i,
        f'Фамилия{i}',
        f'Имя{i}',
        f'Отчество{i}',
        ['Менеджер', 'Агент', 'Директор'][i % 3],
        f'email{i}@example.com'
    ))
cursor.executemany('''
INSERT INTO Staff (staff_id, last_name, first_name, patronymic, job_title, email)
VALUES (?, ?, ?, ?, ?, ?)
''', staff_data)

# Clients (30 записей)
clients_data = []
for i in range(1, 31):
    clients_data.append((
        i,
        f'ФамилияК{i}',
        f'ИмяК{i}',
        f'ОтчествоК{i}',
        f'+7{i:010d}',
        f'client{i}@example.com',
        ['Мужской', 'Женский'][i % 2],
        f'19{i % 50 + 70}-0{i % 9 + 1}-01',
        ['Женат', 'Не замужем', 'Разведён'][i % 3],
        i % 4,
        f'Город {i}, ул. {i}'
    ))
cursor.executemany('''
INSERT INTO Clients (client_id, last_name, first_name, patronymic, phone, email, gender, age, family_status, children, home_address)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', clients_data)

# Orders (30 записей)
orders_data = []
for i in range(1, 31):
    orders_data.append((
        i,
        ['sale', 'rent'][i % 2],
        (i % 30) + 1,
        (i % 30) + 1,
        (i % 30) + 1,
        (i % 30) + 1,
        (i % 30) + 1,
        1000000 + i * 100000,
        ['Рассрочка', 'Единовременно', 'Ипотека'][i % 3],
        i * 10000,
        f'2025-0{(i % 9) + 1}-{(i % 28) + 1:02d}',
        ['active', 'closed'][i % 2]
    ))
cursor.executemany('''
INSERT INTO Orders (order_id, order_type, client_id, staff_id, complex_id, building_id, object_id, order_date, order_status, total_amount, payment_terms, discount_amount)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', orders_data)

# Order_items (30 записей)
order_items_data = []
for i in range(1, 31):
    order_items_data.append((
        i,
        i,
        1000000 + i * 100000
    ))
cursor.executemany('''
INSERT INTO Order_items (order_id, object_id, sale_price)
VALUES (?, ?, ?)
''', order_items_data)

# Payment_schedule (60 записей, по 2 на order)
payment_schedule_data = []
schedule_id = 1
for order_id in range(1, 31):
    for j in range(2):
        payment_schedule_data.append((
            schedule_id,
            order_id,
            f'2025-0{(order_id % 9) + 2}-{(order_id + j) % 28 + 1:02d}',
            (1000000 + order_id * 100000) / 2,
            j % 2
        ))
        schedule_id += 1
cursor.executemany('''
INSERT INTO Payment_schedule (schedule_id, order_id, scheduled_date, scheduled_amount, is_paid)
VALUES (?, ?, ?, ?, ?)
''', payment_schedule_data)

# Transactions (30 записей)
transactions_data = []
for i in range(1, 31):
    transactions_data.append((
        i,
        i,
        500000 + i * 50000,
        f'2025-0{(i % 9) + 1}-{(i % 28) + 1:02d} 12:00:00',
        ['card', 'wire_transfer'][i % 2]
    ))
cursor.executemany('''
INSERT INTO Transactions (transaction_id, schedule_id, payment_amount, transaction_date, payment_method)
VALUES (?, ?, ?, ?, ?)
''', transactions_data)

# Проверка количества записей
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f"Таблица {table[0]} содержит {count} записей")

# Коммит и закрытие
conn.commit()
conn.close()

print(f"База данных '{db_file}' успешно создана и заполнена данными.")