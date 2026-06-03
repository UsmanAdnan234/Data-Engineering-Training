# Data Engineering Training

# Shopping Cart Database Schema

## Overview

This project implements a normalized relational database schema for a shopping cart system. The database manages users, products, product variants, shopping carts, and cart items while maintaining data integrity through primary keys, foreign keys, unique constraints, check constraints, and cascading deletes.

---

## Entity Relationship Diagram (ERD)

The database schema is illustrated in the ERD below.

**ERD File:** 'erd-of-cart.png'

---

# Database Structure

## Users

Stores information about registered users.

### Attributes

* 'user_id' – Primary key, auto-incremented identifier.
* 'name' – User's full name.
* 'email' – User's email address.
* 'phone' – User's phone number.

### Constraints

* 'user_id' is the primary key.
* 'email' must be unique.
* 'phone' must be unique.
* All fields are required.

---

## Carts

Represents a shopping cart associated with a user.

### Attributes

* 'cart_id' – Primary key, auto-incremented identifier.
* 'user_id' – References the owner of the cart.

### Constraints

* 'cart_id' is the primary key.
* 'user_id' is a foreign key referencing 'users(user_id)'.
* 'user_id' is unique, ensuring one cart per user.
* Deleting a user automatically deletes the associated cart through 'ON DELETE CASCADE'.

---

## Products

Stores general product information.

### Attributes

* 'product_id' – Primary key, auto-incremented identifier.
* 'name' – Product name.

### Constraints

* 'product_id' is the primary key.
* Product name is required.

---

## Product Variants

Stores purchasable variations of products such as different colors, sizes, prices, and stock quantities.

### Attributes

* 'variant_id' – Primary key, auto-incremented identifier.
* 'product_id' – References the parent product.
* 'color' – Product color variation.
* 'size' – Product size variation.
* 'price' – Selling price of the variant.
* 'stock' – Available inventory quantity.

### Constraints

* 'variant_id' is the primary key.
* 'product_id' is a foreign key referencing 'products(product_id)'.
* 'price' must be greater than zero.
* 'stock' cannot be negative.
* Deleting a product automatically deletes all associated variants through 'ON DELETE CASCADE'.

---

## Cart Items

Acts as a junction table between carts and product variants. It stores the specific variants added to each cart and their quantities.

### Attributes

* 'item_id' – Primary key, auto-incremented identifier.
* 'cart_id' – References a shopping cart.
* 'variant_id' – References a product variant.
* 'quantity' – Number of units of the variant in the cart.

### Constraints

* 'item_id' is the primary key.
* 'cart_id' is a foreign key referencing 'carts(cart_id)'.
* 'variant_id' is a foreign key referencing 'product_variants(variant_id)'.
* 'quantity' defaults to '1'.
* 'quantity' must be greater than '0'.
* '(cart_id, variant_id)' must be unique to prevent duplicate variant entries within the same cart.
* Deleting a cart automatically deletes its cart items through 'ON DELETE CASCADE'.
* Deleting a product variant automatically deletes related cart items through 'ON DELETE CASCADE'.

---

# Relationships

## Users and Carts (One-to-One)

* Each user can own exactly one cart.
* Each cart belongs to exactly one user.

## Products and Product Variants (One-to-Many)

* A product can have multiple variants.
* Each variant belongs to exactly one product.

### Examples

* Air 31 Earbuds → White Variant
* Air 31 Earbuds → Black Variant
* Air 31 Earbuds → Blue Variant

## Carts and Cart Items (One-to-Many)

* A cart can contain multiple cart items.
* Each cart item belongs to exactly one cart.

## Product Variants and Cart Items (One-to-Many)

* A product variant can appear in multiple cart items.
* Each cart item references exactly one product variant.

## Indirect Relationship: Carts and Product Variants (Many-to-Many)

The many-to-many relationship between carts and product variants is implemented through the 'cart_items' junction table.

* A cart can contain multiple product variants.
* A product variant can appear in multiple carts.
* Each record in 'cart_items' represents a specific product variant added to a specific cart.

---

# Business Rules

* Every user must have a unique email address.
* Every user must have a unique phone number.
* Each user can own only one shopping cart.
* A product can have multiple variants.
* Variants may differ in color, size, price, and stock levels.
* A cart can contain multiple product variants.
* A product variant can exist in multiple carts.
* Duplicate variants within the same cart are not allowed.
* Product quantities are maintained through the 'quantity' attribute.
* Stock values cannot be negative.
* Product prices must be greater than zero.

---

# Data Integrity

The schema ensures consistency and reliability through:

* Primary keys for unique record identification.
* Foreign keys for referential integrity.
* 'ON DELETE CASCADE' rules to prevent orphan records.
* Unique constraints to prevent duplicate records.
* 'NOT NULL' constraints to enforce required fields.
* Check constraints on price and stock values.
* Default values for product quantities.

---

# Design Benefits

* Normalized separation of products and product variants.
* Eliminates duplication of product information.
* Supports products with multiple colors, sizes, and pricing options.
* Prevents duplicate variants within a cart.
* Maintains strong referential integrity through cascading deletes.
* Easily extensible for future e-commerce features such as orders, payments, inventory tracking, product categories, and product images.

---

# Database Normalization

The database schema is normalized up to **Third Normal Form (3NF)**.

## First Normal Form (1NF)

The schema satisfies 1NF because:

* Each table has a primary key that uniquely identifies each record.
* All attributes contain atomic values.
* There are no repeating groups or multi-valued attributes.

## Second Normal Form (2NF)

The schema satisfies 2NF because:

* It is already in 1NF.
* All non-key attributes are fully dependent on their respective primary keys.
* No partial dependencies exist.

### Examples

* In 'users', 'name', 'email', and 'phone' depend entirely on 'user_id'.
* In 'products', 'name' depends entirely on 'product_id'.
* In 'product_variants', 'color', 'size', 'price', and 'stock' depend entirely on 'variant_id'.
* In 'cart_items', 'quantity' depends entirely on the cart-variant relationship.

## Third Normal Form (3NF)

The schema satisfies 3NF because:

* It is already in 2NF.
* No non-key attribute depends on another non-key attribute.
* All non-key attributes depend only on the primary key.

### Examples

* User information is stored only in the 'users' table.
* Product information is stored only in the 'products' table.
* Variant-specific information such as color, size, price, and stock is stored only in the 'product_variants' table.
* Cart information is stored only in the 'carts' table.
* The 'cart_items' table stores only the relationship between carts and product variants along with quantity.

### Benefits of Normalization

* Reduces data redundancy.
* Prevents update, insertion, and deletion anomalies.
* Improves data consistency and integrity.
* Simplifies maintenance and future schema extensions.

---

# Conclusion

This schema provides a robust foundation for implementing shopping cart functionality in an e-commerce application. By separating products from their variants and enforcing strong integrity constraints, the design ensures accurate data management while remaining scalable, maintainable, and extensible.

# API Endpoints

The following REST API endpoints can be implemented for interacting with the shopping cart database.

---

## Users

### Create User

POST /users

Creates a new user.

### Get User

GET /users/{user_id}

Retrieves a specific user.

### Update User

PUT /users/{user_id}

Updates user information.

### Delete User

DELETE /users/{user_id}

Deletes a user and automatically removes the associated cart through 'ON DELETE CASCADE'.

---

## Carts

### Create Cart

POST /carts

Creates a shopping cart for a user.

### Get Cart

GET /carts/{cart_id}

Retrieves a specific cart.

### Get User Cart

GET /users/{user_id}/cart

Retrieves the cart belonging to a specific user.

### Delete Cart

DELETE /carts/{cart_id}

Deletes a cart and all associated cart items.

---

## Products

### Create Product

POST /products

Creates a new product.

### Get All Products

GET /products

Retrieves all products.

### Get Product

GET /products/{product_id}

Retrieves a specific product.

### Update Product

PUT /products/{product_id}

Updates product information.

### Delete Product

DELETE /products/{product_id}

Deletes a product and all associated variants.

---

## Product Variants

### Create Product Variant

POST /products/{product_id}/variants

Creates a variant for a specific product.

### Get Product Variants

GET /products/{product_id}/variants

Retrieves all variants of a product.

### Get Variant

GET /variants/{variant_id}

Retrieves a specific variant.

### Update Variant

PUT /variants/{variant_id}

Updates variant information such as color, size, price, or stock.

### Delete Variant

DELETE /variants/{variant_id}

Deletes a variant and all related cart items.

---

## Cart Items

### Add Item to Cart

POST /carts/{cart_id}/items

Adds a product variant to a cart.

Request Body:

json
{
  "variant_id": 1,
  "quantity": 2
}

### Get Cart Items

GET /carts/{cart_id}/items

Retrieves all items in a cart.

### Update Cart Item Quantity

PATCH /cart-items/{item_id}

Request Body:

json
{
  "quantity": 5
}

Updates the quantity of a cart item.

### Remove Cart Item

DELETE /cart-items/{item_id}

Removes an item from a cart.

### Clear Cart

DELETE /carts/{cart_id}/items

Removes all items from a cart.

---

# Cart API Implementation

This section explains how the cart API is built, how it works, and what decisions were made during implementation.

---

## Project Structure

The code is split into four layers. Each layer has one job:

```
app/
├── api/            → Receives HTTP requests, sends HTTP responses
├── services/       → Business logic (rules like "cart must be active to add items")
├── repositories/   → Talks to the database (all SQL lives here)
├── schemas/        → Defines what request and response data looks like
└── core/
    ├── exceptions.py  → Custom error types
    ├── logger.py      → Logging setup
    └── config.py      → Database name config
```

The flow for every request is:

```
Request → API → Service → Repository → Database
Response ← API ← Service ← Repository ← Database
```

This separation means if the database changes, only the repository needs updating. The API and service layers stay the same.

---

## Cart Lifecycle

A cart has two statuses:

```
active  →  checked_out
```

- A cart starts as `active` when created.
- After checkout, it becomes `checked_out` and can no longer be modified.
- A user can create a new `active` cart after their previous one is checked out.
- A user can only have **one active cart at a time**.

The `status` column lives in the `carts` table because it describes the cart itself, not the items inside it.

> **Why user_id is not UNIQUE in carts:** Originally the schema had `UNIQUE(user_id)` in the carts table, which meant a user could only ever have one cart total — even after checkout. This was removed so users can create a new cart after checking out. The one-active-cart rule is enforced in the service layer instead.

---

## Implemented Endpoints

### POST /carts
Creates a new cart for a user.

- Checks the user exists.
- Checks the user does not already have an **active** cart.
- Creates the cart with status `active`.

**Request:**
```json
{ "user_id": 1 }
```

**Response (201):**
```json
{ "cart_id": 1, "user_id": 1, "message": "Cart created successfully" }
```

---

### POST /carts/{cart_id}/items
Adds a product variant to a cart.

- Checks the cart exists.
- Checks the cart is `active` (not checked out).
- Checks the product variant exists.
- If the same variant is already in the cart, the quantity is added to the existing amount instead of creating a duplicate.

**Request:**
```json
{ "variant_id": 2, "quantity": 3 }
```

**Response (201):**
```json
{ "item_id": 1, "cart_id": 1, "variant_id": 2, "quantity": 3, "message": "Item added to cart" }
```

---

### DELETE /carts/{cart_id}/items/{item_id}
Removes a specific item from a cart.

- Checks the cart exists.
- Checks the cart is `active`.
- Checks the item belongs to that cart.
- Deletes the item.

**Response (200):**
```json
{ "message": "Item removed from cart" }
```

---

### DELETE /carts/{cart_id}
Deletes a cart completely.

- Checks the cart exists.
- Deletes the cart. All items inside are deleted automatically by the database (`ON DELETE CASCADE`).

**Response (200):**
```json
{ "message": "Cart deleted successfully" }
```

---

### POST /carts/{cart_id}/checkout
Checks out a cart.

- Checks the cart exists.
- Checks the cart is `active` (cannot checkout twice).
- Checks the cart has at least one item (cannot checkout an empty cart).
- Changes the cart status to `checked_out`.

**Response (200):**
```json
{ "cart_id": 1, "status": "checked_out", "message": "Checkout successful" }
```

---

## Error Codes

| Code | Meaning | Example |
|------|---------|---------|
| 404 | Something was not found | User, cart, variant, or item does not exist |
| 409 | Conflict with current state | Cart already exists, or cart is already checked out |
| 422 | Request is valid but cannot be processed | Trying to checkout an empty cart |
| 500 | Unexpected server error | Database failure or unhandled exception |

---

## Logging

Every request and important event is logged to `logs/app.log`.

- **INFO** — normal events (request received, cart created, item added)
- **WARNING** — expected failures (cart not found, already checked out)
- **EXCEPTION** — unexpected errors with full traceback for debugging

**What is NOT logged:** email addresses, phone numbers, and names are never written to logs to protect user privacy. Only IDs, quantities, and statuses are logged.

Example log entries:
```
2026-06-03 10:00:01,123 INFO Create cart request user_id=1
2026-06-03 10:00:01,130 INFO Cart created cart_id=3 user_id=1
2026-06-03 10:00:05,210 WARNING Cart not found cart_id=99
```

---

## Setup and Running

**1. Install dependencies:**
```bash
pip install fastapi uvicorn
```

**2. Initialize the database (first time only):**
```bash
python init_db.py
```

**3. Seed sample data (users, products, variants):**
```bash
python check_db.py
```

**4. If you already have a database from before the `status` column was added, run the migration instead of reinitializing:**
```bash
python migrate_db.py
```

**5. Start the server:**
```bash
uvicorn app.main:app --reload
```

**6. Open Swagger UI to test the endpoints:**
```
http://127.0.0.1:8000/docs
```

---

## Sample Test Flow

```
1. POST /carts           { "user_id": 1 }              → cart_id = 1
2. POST /carts/1/items   { "variant_id": 1, "quantity": 2 }
3. POST /carts/1/items   { "variant_id": 4, "quantity": 1 }
4. POST /carts/1/checkout                              → status = checked_out
5. POST /carts           { "user_id": 1 }              → cart_id = 2 (new active cart)
```
