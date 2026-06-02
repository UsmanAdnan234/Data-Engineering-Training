CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL CHECK (email LIKE '%_@_%._%'),
    phone VARCHAR(20) UNIQUE NOT NULL CHECK (phone GLOB '+[0-9]*' OR phone GLOB '[0-9]*')
);

CREATE TABLE carts (
    cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'checked_out')),

    FOREIGN KEY(user_id)
    REFERENCES users(user_id)
    ON DELETE CASCADE
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE product_variants (
    variant_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    color VARCHAR(50),
    size VARCHAR(50),
    price DECIMAL(10,2) NOT NULL CHECK(price > 0),
    stock INTEGER NOT NULL CHECK(stock >= 0),

    FOREIGN KEY(product_id)
    REFERENCES products(product_id)
    ON DELETE CASCADE
);

CREATE TABLE cart_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cart_id INTEGER NOT NULL,
    variant_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK(quantity > 0),

    FOREIGN KEY(cart_id)
    REFERENCES carts(cart_id)
    ON DELETE CASCADE,

    FOREIGN KEY(variant_id)
    REFERENCES product_variants(variant_id)
    ON DELETE CASCADE,

    UNIQUE(cart_id, variant_id)
);