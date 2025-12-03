import sqlite3
import os
import random
from datetime import datetime, timedelta

# Создаём файл базы данных
db_file = 'rental_2.db'
if os.path.exists(db_file):
    os.remove(db_file)

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Создание таблиц
cursor.execute('''
CREATE TABLE Grade_remoteness (
    grade_remoteness_id INTEGER PRIMARY KEY,
    ponds_nearest REAL
);
''')

cursor.execute('''
CREATE TABLE Facilitys (
    facility_id INTEGER PRIMARY KEY,
    facility_name TEXT
);
''')

cursor.execute('''
CREATE TABLE Object_types (
    object_type_id INTEGER PRIMARY KEY,
    name_object TEXT
);
''')

cursor.execute('''
CREATE TABLE Objects (
    object_id INTEGER PRIMARY KEY,
    facility_id INTEGER,
    cadastral_number INTEGER,
    city TEXT,
    street TEXT,
    house_number INTEGER,
    number_object INTEGER,
    object_type_id INTEGER,
    total_area REAL,
    floor INTEGER,
    floors_total INTEGER,
    grade_remoteness_id INTEGER,
    rent_price REAL,
    FOREIGN KEY (facility_id) REFERENCES Facilitys(facility_id),
    FOREIGN KEY (object_type_id) REFERENCES Object_types(object_type_id),
    FOREIGN KEY (grade_remoteness_id) REFERENCES Grade_remoteness(grade_remoteness_id)
);
''')

cursor.execute('''
CREATE TABLE Clients (
    client_id INTEGER PRIMARY KEY,
    client_name TEXT,
    phone TEXT,
    email TEXT
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

# ⚡️ Убрали object_id
cursor.execute('''
CREATE TABLE Leases (
    lease_id INTEGER PRIMARY KEY,
    client_id INTEGER,
    staff_id INTEGER,
    start_date TEXT,
    end_date TEXT,
    total_monthly_rent REAL,
    status TEXT,
    FOREIGN KEY (client_id) REFERENCES Clients(client_id),
    FOREIGN KEY (staff_id) REFERENCES Staff(staff_id)
);
''')

cursor.execute('''
CREATE TABLE Lease_objects (
    lease_id INTEGER,
    object_id INTEGER,
    rent_price REAL,
    PRIMARY KEY (lease_id, object_id),
    FOREIGN KEY (lease_id) REFERENCES Leases(lease_id),
    FOREIGN KEY (object_id) REFERENCES Objects(object_id)
);
''')

cursor.execute('''
CREATE TABLE Payment_schedule (
    schedule_id INTEGER PRIMARY KEY,
    lease_id INTEGER,
    scheduled_date TEXT,
    scheduled_amount REAL,
    is_paid INTEGER,
    FOREIGN KEY (lease_id) REFERENCES Leases(lease_id)
);
''')

cursor.execute('''
CREATE TABLE Transactions (
    transaction_id INTEGER PRIMARY KEY,
    schedule_id INTEGER,
    payment_amount REAL,
    transaction_date TEXT,
    FOREIGN KEY (schedule_id) REFERENCES Payment_schedule(schedule_id)
);
''')

# Grade_remoteness (6 записей)
cursor.executemany('''
INSERT INTO Grade_remoteness (grade_remoteness_id, ponds_nearest)
VALUES (?, ?)
''', [
    (0, 0),
    (1, 1000),
    (2, 2000),
    (3, 3000),
    (4, 4000),
    (5, 5000)
])

# Facilitys (15 записей)
facilitys_data = [
    (1, 'ООО Недвижимость Прогресс'),
    (2, 'ЗАО Аренда Сити'),
    (3, 'ООО Городские Активы'),
    (4, 'ПАО СтройИнвест'),
    (5, 'ООО КоммерцГрупп'),
    (6, 'ЗАО Простор'),
    (7, 'ООО БизнесПарк'),
    (8, 'ПАО АрендаПлюс'),
    (9, 'ООО ГлобалРент'),
    (10, 'ЗАО СитиПроперти'),
    (11, 'ООО ТехноАренда'),
    (12, 'ПАО Урбан Девелопмент'),
    (13, 'ООО РенталСистемс'),
    (14, 'ЗАО Капитал Аренда'),
    (15, 'ООО ПромНедвижимость')
]
cursor.executemany('''
INSERT INTO Facilitys (facility_id, facility_name)
VALUES (?, ?)
''', facilitys_data)

# Object_types (6 записей)
cursor.executemany('''
INSERT INTO Object_types (object_type_id, name_object)
VALUES (?, ?)
''', [
    (1, 'Склад'),
    (2, 'Административное'),
    (3, 'Общепит'),
    (4, 'Торговая площадь'),
    (5, 'Ангар'),
    (6, 'Ремонтная база')
])

# Objects (300 записей, по 20 на facility) — ⚡️ только Москва
objects_data = []
object_id = 1
for facility_id in range(1, 16):
    for i in range(20):
        obj_type = (object_id % 6) + 1
        total_area = random.uniform(10, 500)
        grade_id = random.randint(0, 5)
        base_price = 50000 + (total_area * 1000) - (grade_id * 50000)
        rent_price = max(50000, min(850000, base_price))
        objects_data.append((
            object_id,
            facility_id,
            77010001000 + object_id,
            'Москва',   # ✅ только Москва
            f'Улица {object_id}',
            object_id * 2,
            object_id,
            obj_type,
            total_area,
            random.randint(1, 8),
            random.randint(1, 8),
            grade_id,
            round(rent_price, 2)
        ))
        object_id += 1
cursor.executemany('''
INSERT INTO Objects (object_id, facility_id, cadastral_number, city, street, house_number, number_object, object_type_id, total_area, floor, floors_total, grade_remoteness_id, rent_price)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', objects_data)

# Clients (90 записей)
clients_data = []
for i in range(1, 91):
    clients_data.append((
        i,
        f'ООО Клиент {i}',
        f'+7{i:010d}',
        f'client{i}@rental.com'
    ))
cursor.executemany('''
INSERT INTO Clients (client_id, client_name, phone, email)
VALUES (?, ?, ?, ?)
''', clients_data)

# Staff (10 записей)
staff_data = [
    (1, 'Иванов', 'Иван', 'Иванович', 'Менеджер', 'ivanov@rental.com'),
    (2, 'Петрова', 'Анна', 'Сергеевна', 'Старший менеджер', 'petrova@rental.com'),
    (3, 'Сидоров', 'Алексей', 'Викторович', 'Менеджер', 'sidorov@rental.com'),
    (4, 'Кузнецова', 'Мария', 'Алексеевна', 'Менеджер', 'kuznetsova@rental.com'),
    (5, 'Лебедев', 'Сергей', 'Петрович', 'Старший менеджер', 'lebedev@rental.com'),
    (6, 'Морозова', 'Елена', 'Дмитриевна', 'Менеджер', 'morozova@rental.com'),
    (7, 'Васильев', 'Дмитрий', 'Андреевич', 'Менеджер', 'vasiliev@rental.com'),
    (8, 'Смирнова', 'Ольга', 'Николаевна', 'Старший менеджер', 'smirnova@rental.com'),
    (9, 'Попов', 'Михаил', 'Сергеевич', 'Менеджер', 'popov@rental.com'),
    (10, 'Федорова', 'Наталья', 'Игоревна', 'Менеджер', 'fedorova@rental.com')
]
cursor.executemany('''
INSERT INTO Staff (staff_id, last_name, first_name, patronymic, job_title, email)
VALUES (?, ?, ?, ?, ?, ?)
''', staff_data)

# Leases (~200 записей) — ⚡️ без object_id
leases_data = []
lease_objects_data = []
lease_id = 1
start_date = datetime(2020, 1, 1)
end_date_limit = datetime(2027, 12, 31)
current_date = datetime(2025, 8, 29)

while lease_id <= 200:
    duration_months = random.randint(1, 24)
    lease_start = start_date + timedelta(days=random.randint(0, (end_date_limit - start_date).days - duration_months * 30))
    lease_end = lease_start + timedelta(days=duration_months * 30)
    if lease_end > end_date_limit:
        continue

    # выбираем случайный facility → объекты только оттуда
    facility_id = random.randint(1, 15)
    object_ids = random.sample([o[0] for o in objects_data if o[1] == facility_id], random.randint(1, 5))

    total_rent = sum(o[12] for o in objects_data if o[0] in object_ids)
    status = 'closed' if lease_end < current_date else 'open'

    leases_data.append((
        lease_id,
        random.randint(1, 90),
        random.randint(1, 10),
        lease_start.strftime('%Y-%m-%d'),
        lease_end.strftime('%Y-%m-%d'),
        round(total_rent, 2),
        status
    ))

    for obj_id in object_ids:
        rent_price = next(o[12] for o in objects_data if o[0] == obj_id)
        lease_objects_data.append((lease_id, obj_id, rent_price))

    lease_id += 1

cursor.executemany('''
INSERT INTO Leases (lease_id, client_id, staff_id, start_date, end_date, total_monthly_rent, status)
VALUES (?, ?, ?, ?, ?, ?, ?)
''', leases_data)

cursor.executemany('''
INSERT INTO Lease_objects (lease_id, object_id, rent_price)
VALUES (?, ?, ?)
''', lease_objects_data)

# Payment_schedule (~2400 записей, ежемесячные платежи)
payment_schedule_data = []
schedule_id = 1
for lease in leases_data:
    lease_id = lease[0]
    start = datetime.strptime(lease[3], '%Y-%m-%d')
    end = datetime.strptime(lease[4], '%Y-%m-%d')
    total_rent = lease[5]
    current = start
    while current <= end:
        scheduled_date = (current + timedelta(days=(31 - current.day))).replace(day=1) - timedelta(days=1)
        if scheduled_date > end:
            scheduled_date = end
        payment_schedule_data.append((
            schedule_id,
            lease_id,
            scheduled_date.strftime('%Y-%m-%d'),
            round(total_rent, 2),
            random.randint(0, 1)
        ))
        schedule_id += 1
        current = (current + timedelta(days=31)).replace(day=1)

cursor.executemany('''
INSERT INTO Payment_schedule (schedule_id, lease_id, scheduled_date, scheduled_amount, is_paid)
VALUES (?, ?, ?, ?, ?)
''', payment_schedule_data)

# Transactions (~2400 записей)
transactions_data = []
for i, schedule in enumerate(payment_schedule_data, 1):
    transactions_data.append((
        i,
        schedule[0],
        schedule[3],
        schedule[2]
    ))
cursor.executemany('''
INSERT INTO Transactions (transaction_id, schedule_id, payment_amount, transaction_date)
VALUES (?, ?, ?, ?)
''', transactions_data)

conn.commit()
conn.close()

print(f"База данных '{db_file}' успешно создана и заполнена данными.")
