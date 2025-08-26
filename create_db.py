import sqlite3
import os
import random

# Создаём файл базы данных
db_file = 'real_estate_3.db'
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
    total_amount REAL,
    payment_terms TEXT,
    discount_amount REAL,
    order_date TEXT,
    order_status TEXT,
    FOREIGN KEY (client_id) REFERENCES Clients(client_id),
    FOREIGN KEY (staff_id) REFERENCES Staff(staff_id),
    FOREIGN KEY (complex_id) REFERENCES Residential_complex(complex_id),
    FOREIGN KEY (building_id) REFERENCES Buildings(building_id)
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
# Object_types (7 записей)
cursor.executemany('''
INSERT INTO Object_types (object_type, name_object)
VALUES (?, ?)
''', [
    (1, 'Квартира'),
    (2, 'Апартаменты'),
    (3, 'Студия'),
    (4, 'Кладовка'),
    (5, 'Парковка'),
    (6, 'Мансарда'),
    (7, 'Терраса')
])

# Residential_complex (7 записей)
residential_data = [
    (1, 'Зелёный Оазис', 'Москва', 'Ленина', 'Парк Культуры', 0.5, 1, 1),
    (2, 'Городские Высоты', 'Санкт-Петербург', 'Невский', 'Площадь Восстания', 0.3, 1, 0),
    (3, 'Риверсайд', 'Москва', 'Кутузовский', 'Киевская', 1.2, 0, 1),
    (4, 'Солнечный Берег', 'Новосибирск', 'Горская', 'Речной Вокзал', 0.8, 1, 1),
    (5, 'Центральный', 'Москва', 'Тверская', 'Тверская', 0.4, 0, 0),
    (6, 'Морской Бриз', 'Санкт-Петербург', 'Морская', 'Приморская', 0.6, 1, 1),
    (7, 'Лесной Уют', 'Новосибирск', 'Лесная', 'Заельцовская', 1.0, 0, 1)
]
cursor.executemany('''
INSERT INTO Residential_complex (complex_id, complex_name, city, street, subway, subway_nearest, childrens_playground, sports_ground)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', residential_data)

# Buildings (около 33 записей, по 4–5 зданий на комплекс)
buildings_data = []
building_id = 1
for complex_id in range(1, 8):
    num_buildings = random.randint(4, 5)