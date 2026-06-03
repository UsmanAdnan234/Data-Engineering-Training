import sqlite3
from app.core.config import DB_NAME

conn = sqlite3.connect(DB_NAME)

# --- Clear all tables ---
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

# --- Users ---
users = [
    ("Asad",     "asad@gmail.com",     "03345678910"),
    ("Muzammil", "muzammil@gmail.com", "03001234588"),
    ("Zainab",   "zainab@gmail.com",   "03005556677"),
]
conn.executemany("INSERT INTO users (name, email, phone) VALUES (?, ?, ?)", users)

# --- Products ---
products = [
    ("T-Shirt",),
    ("Jeans",),
    ("Sneakers",),
]
conn.executemany("INSERT INTO products (name) VALUES (?)", products)

# --- Product Variants (product_id, color, size, price, stock) ---
variants = [
    (1, "White",  "S",  499.99, 50),
    (1, "Black",  "M",  499.99, 30),
    (1, "Red",    "L",  549.99, 20),
    (2, "Blue",   "30", 1999.00, 15),
    (2, "Black",  "32", 2199.00, 10),
    (3, "White",  "42", 3499.00, 8),
    (3, "Black",  "43", 3499.00, 5),
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
for row in conn.execute(
    "SELECT v.variant_id, p.name, v.color, v.size, v.price, v.stock "
    "FROM product_variants v JOIN products p ON v.product_id = p.product_id"
).fetchall():
    print(row)

print("\n=== Carts ===")
for row in conn.execute("SELECT * FROM carts").fetchall():
    print(row)

print("\n=== Carts_Items ===")
for row in conn.execute("SELECT * FROM cart_items").fetchall():
    print(row)
    
conn.close()
print("\nDone.")
