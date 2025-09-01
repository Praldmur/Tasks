import sqlite3

conn = sqlite3.connect('Sber.db')
c = conn.cursor()

# Create Orders table
c.execute('''
CREATE TABLE IF NOT EXISTS Orders (
    OrderID INTEGER PRIMARY KEY,
    CustomerID INTEGER,
    OrderDate TEXT CHECK(length(OrderDate) = 8),
    OrderState TEXT CHECK(OrderState IN ('Fulfilled', 'Cancelled')),
    DeliveryDays INTEGER
)
''')

# Create Order_List table
c.execute('''
CREATE TABLE IF NOT EXISTS Order_List (
    OrderID INTEGER,
    SKU INTEGER,
    Quantity INTEGER,
    Price INTEGER,
    PRIMARY KEY (OrderID, SKU)
)
''')

# Create Customers table
c.execute('''
CREATE TABLE IF NOT EXISTS Customers (
    CustomerID INTEGER PRIMARY KEY,
    CityID INTEGER
)
''')

# Create trigger for default CityID = 1 if NULL
c.execute('''
CREATE TRIGGER IF NOT EXISTS default_city
AFTER INSERT ON Customers
WHEN NEW.CityID IS NULL
BEGIN
    UPDATE Customers SET CityID = 1 WHERE CustomerID = NEW.CustomerID;
END;
''')

# Create City_Region table
c.execute('''
CREATE TABLE IF NOT EXISTS City_Region (
    CityID INTEGER PRIMARY KEY,
    Region TEXT CHECK(Region IN ('Central', 'North', 'South', 'East', 'West'))
)
''')

# Insert sample data into City_Region
regions = [
    (1, 'Central'),
    (2, 'North'),
    (3, 'South'),
    (4, 'East'),
    (5, 'West')
]
c.executemany("INSERT OR IGNORE INTO City_Region VALUES (?, ?)", regions)

# Insert sample data into Customers (one with NULL to trigger default)
customers = [
    (1, 1),
    (2, 2),
    (3, None),  # Will be set to 1 via trigger
    (4, 3),
    (5, 4)
]
c.executemany("INSERT OR IGNORE INTO Customers VALUES (?, ?)", customers)

# Insert sample data into Orders (around current date: September 2025)
orders = [
    (1, 1, '20250901', 'Fulfilled', 0),
    (2, 2, '20250902', 'Fulfilled', 1),
    (3, 3, '20250903', 'Cancelled', None),
    (4, 4, '20250904', 'Fulfilled', 2),
    (5, 5, '20250905', 'Cancelled', None)
]
c.executemany("INSERT OR IGNORE INTO Orders VALUES (?, ?, ?, ?, ?)", orders)

# Insert sample data into Order_List
order_lists = [
    (1, 101, 2, 100),  # Order 1: Item 101 (2 units @ 100)
    (1, 102, 1, 150),  # Order 1: Item 102 (1 unit @ 150)
    (2, 103, 3, 50),   # Order 2: Item 103 (3 units @ 50)
    (3, 101, 1, 100),  # Order 3 (cancelled): Item 101
    (4, 104, 4, 75),   # Order 4: Item 104 (4 units @ 75)
    (4, 105, 2, 200),  # Order 4: Item 105 (2 units @ 200)
    (5, 106, 5, 30)    # Order 5 (cancelled): Item 106
]
c.executemany("INSERT OR IGNORE INTO Order_List VALUES (?, ?, ?, ?)", order_lists)

conn.commit()
conn.close()

print("Database created and populated successfully.")