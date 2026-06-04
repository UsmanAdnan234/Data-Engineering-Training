import sqlite3
from app.core.config import DB_NAME

conn = sqlite3.connect(DB_NAME)


conn.execute("DELETE FROM cart_items")
conn.execute("DELETE FROM carts")
conn.execute("DELETE FROM product_variants")
conn.execute("DELETE FROM products")
conn.execute("DELETE FROM users")

conn.execute("DELETE FROM sqlite_sequence WHERE name='cart_items'")
conn.execute("DELETE FROM sqlite_sequence WHERE name='carts'")
conn.execute("DELETE FROM sqlite_sequence WHERE name='product_variants'")
conn.execute("DELETE FROM sqlite_sequence WHERE name='products'")
conn.execute("DELETE FROM sqlite_sequence WHERE name='users'")

users = [
    ("Asad", "asad@gmail.com", "03345678910"),
    ("Muzammil", "muzammil@gmail.com", "03001234588"),
    ("Zainab", "zainab@gmail.com", "03005556677"),
    ("Ali", "ali@gmail.com", "03011111111"),
    ("Ahmed", "ahmed@gmail.com", "03022222222"),
    ("Fatima", "fatima@gmail.com", "03033333333"),
    ("Ayesha", "ayesha@gmail.com", "03044444444"),
    ("Bilal", "bilal@gmail.com", "03055555555"),
    ("Hassan", "hassan@gmail.com", "03066666666"),
    ("Sara", "sara@gmail.com", "03077777777"),
]
conn.executemany("INSERT INTO users (name, email, phone) VALUES (?, ?, ?)", users)

products = [
    ("T-Shirt",),
    ("Jeans",),
    ("Sneakers",),
    ("Hoodie",),
    ("Cap",),
    ("Jacket",),
    ("Shirt",),
    ("Watch",),
    ("Backpack",),
    ("Socks",),
]
conn.executemany("INSERT INTO products (name) VALUES (?)", products)

variants = [
    # T-Shirt (product_id=1)
    (1, "White", "S", 499.99, 50),
    (1, "White", "M", 499.99, 40),
    (1, "Black", "L", 549.99, 20),

    # Jeans (product_id=2)
    (2, "Blue", "30", 1999.00, 15),
    (2, "Blue", "32", 1999.00, 12),
    (2, "Black", "34", 2199.00, 10),

    # Sneakers (product_id=3)
    (3, "White", "41", 3499.00, 8),
    (3, "White", "42", 3499.00, 6),
    (3, "Black", "43", 3699.00, 5),

    # Hoodie (product_id=4)
    (4, "Gray", "S", 1499.00, 25),
    (4, "Gray", "M", 1499.00, 20),
    (4, "Black", "L", 1599.00, 15),

    # Cap (product_id=5)
    (5, "Black", "Free", 299.00, 100),
    (5, "White", "Free", 299.00, 80),
    (5, "Red", "Free", 349.00, 60),

    # Jacket (product_id=6)
    (6, "Brown", "M", 2999.00, 12),
    (6, "Brown", "L", 2999.00, 10),
    (6, "Black", "XL", 3299.00, 8),

    # Shirt (product_id=7)
    (7, "White", "M", 899.00, 30),
    (7, "White", "L", 899.00, 25),
    (7, "Blue", "XL", 999.00, 20),

    # Watch (product_id=8)
    (8, "Silver", "Standard", 4999.00, 20),
    (8, "Black", "Standard", 5499.00, 15),
    (8, "Gold", "Standard", 6499.00, 10),

    # Backpack (product_id=9)
    (9, "Black", "Large", 2499.00, 18),
    (9, "Blue", "Large", 2499.00, 15),
    (9, "Gray", "Medium", 2299.00, 12),

    # Socks (product_id=10)
    (10, "White", "Free", 199.00, 200),
    (10, "Black", "Free", 199.00, 180),
    (10, "Gray", "Free", 249.00, 150),
]
conn.executemany(
    "INSERT INTO product_variants (product_id, color, size, price, stock) VALUES (?, ?, ?, ?, ?)",
    variants
)

conn.commit()

# --- Print seeded data ---
print("=== Users ===")
for row in conn.execute("SELECT user_id, name, email FROM users").fetchall():
    print(row)

print("\n=== Products ===")
for row in conn.execute("SELECT * FROM products").fetchall():
    print(row)

print("\n=== Product Variants ===")
rows = conn.execute("""
    SELECT
        v.variant_id,
        p.product_id,
        p.name,
        v.color,
        v.size,
        v.price,
        v.stock
    FROM products p
    JOIN product_variants v
      ON p.product_id = v.product_id
    ORDER BY p.product_id, v.variant_id
""").fetchall()

for row in rows:
    print(row)

print("\n=== Carts ===")
for row in conn.execute("SELECT * FROM carts").fetchall():
    print(row)

print("\n=== Carts_Items ===")
for row in conn.execute("SELECT * FROM cart_items").fetchall():
    print(row)
    
conn.close()
print("\nDone.")
