# Data Engineering Training

# Shopping Cart Database Schema

###### Overview

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

# Cart API Implementation — Stock Deduction on Checkout

After a user checks out, the stock for every variant in the cart is reduced by the purchased quantity. For example, if variant 1 had stock = 50 and the user bought 10, stock becomes 40 after checkout.

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

---

# API Test Cases

This section contains 50 test cases covering all endpoints, success paths, error paths, edge cases, and validation. Use Swagger UI at `http://127.0.0.1:8000/docs` or any API client like Postman to run them.

## Seeded Test Data (from check_db.py)

| Type | ID | Details |
|------|----|---------|
| User | 1 | Asad |
| User | 2 | Muzammil |
| User | 3 | Zainab |
| Variant | 1 | T-Shirt, White, S — stock: 50 |
| Variant | 2 | T-Shirt, Black, M — stock: 30 |
| Variant | 3 | T-Shirt, Red, L — stock: 20 |
| Variant | 4 | Jeans, Blue, 30 — stock: 15 |
| Variant | 5 | Jeans, Black, 32 — stock: 10 |
| Variant | 6 | Sneakers, White, 42 — stock: 8 |
| Variant | 7 | Sneakers, Black, 43 — stock: 5 |

> **Note:** Stock values change as checkout tests run. Reseed the database with `check_db.py` before each test session if you want consistent stock levels. In the test cases below, stock values refer to the freshly seeded state.

---

## Group A — Create Cart (POST /carts)

---

### TC-01 — Create cart for valid user

**Method:** POST `/carts`

**Body:**
```json
{ "user_id": 1 }
```

**Expected status:** `201`

**Expected response:**
```json
{ "cart_id": 1, "user_id": 1, "message": "Cart created successfully" }
```

---

### TC-02 — Create cart for a different valid user

**Method:** POST `/carts`

**Body:**
```json
{ "user_id": 2 }
```

**Expected status:** `201`

**Expected response:**
```json
{ "cart_id": 2, "user_id": 2, "message": "Cart created successfully" }
```

---

### TC-03 — Create cart when user already has an active cart

Run TC-01 first, then call again with the same user.

**Method:** POST `/carts`

**Body:**
```json
{ "user_id": 1 }
```

**Expected status:** `409`

**Expected response:**
```json
{ "error": "CART_ALREADY_EXISTS", "message": "Active cart already exists" }
```

---

### TC-04 — Create cart for non-existent user

**Method:** POST `/carts`

**Body:**
```json
{ "user_id": 999 }
```

**Expected status:** `404`

**Expected response:**
```json
{ "error": "USER_NOT_FOUND", "message": "User not found" }
```

---

### TC-05 — user_id is zero

**Method:** POST `/carts`

**Body:**
```json
{ "user_id": 0 }
```

**Expected status:** `422`

**Expected response:**
```json
{ "error": "VALIDATION_ERROR", "details": [{ "field": "user_id", "message": "Must be greater than 0" }] }
```

---

### TC-06 — user_id is negative

**Method:** POST `/carts`

**Body:**
```json
{ "user_id": -5 }
```

**Expected status:** `422`

**Expected response:**
```json
{ "error": "VALIDATION_ERROR", "details": [{ "field": "user_id", "message": "Must be greater than 0" }] }
```

---

### TC-07 — user_id is a string

**Method:** POST `/carts`

**Body:**
```json
{ "user_id": "abc" }
```

**Expected status:** `422`

**Expected response:**
```json
{ "error": "VALIDATION_ERROR", "details": [{ "field": "user_id", "message": "Must be a valid integer" }] }
```

---

### TC-08 — user_id missing from body

**Method:** POST `/carts`

**Body:**
```json
{}
```

**Expected status:** `422`

**Expected response:**
```json
{ "error": "VALIDATION_ERROR", "details": [{ "field": "user_id", "message": "This field is required" }] }
```

---

### TC-09 — user_id exceeds SQLite integer limit (overflow)

**Method:** POST `/carts`

**Body:**
```json
{ "user_id": 99999999999999999999 }
```

**Expected status:** `422`

**Expected response:**
```json
{ "error": "VALIDATION_ERROR", "details": [{ "field": "user_id", "message": "Value is out of valid range" }] }
```

---

### TC-10 — user_id is a decimal number

**Method:** POST `/carts`

**Body:**
```json
{ "user_id": 1.5 }
```

**Expected status:** `422`

**Expected response:**
```json
{ "error": "VALIDATION_ERROR", "details": [{ "field": "user_id", "message": "Must be a valid integer" }] }
```

---

## Group B — Add Item to Cart (POST /carts/{cart_id}/items)

> **Prerequisite:** Create a cart first using TC-01. Use the returned `cart_id` in the path.

---

### TC-11 — Add a new item to cart

**Method:** POST `/carts/1/items`

**Body:**
```json
{ "variant_id": 1, "quantity": 2 }
```

**Expected status:** `201`

**Expected response:**
```json
{ "item_id": 1, "cart_id": 1, "variant_id": 1, "quantity": 2, "message": "Item added to cart" }
```

---

### TC-12 — Add same variant again (quantity accumulates)

Run TC-11 first, then add the same variant again.

**Method:** POST `/carts/1/items`

**Body:**
```json
{ "variant_id": 1, "quantity": 3 }
```

**Expected status:** `201`

**Expected response:**
```json
{ "item_id": 1, "cart_id": 1, "variant_id": 1, "quantity": 5, "message": "Item added to cart" }
```

> Note: quantity became 2 + 3 = 5, no duplicate row was created.

---

### TC-13 — Add a different variant to the same cart

**Method:** POST `/carts/1/items`

**Body:**
```json
{ "variant_id": 4, "quantity": 1 }
```

**Expected status:** `201`

**Expected response:**
```json
{ "item_id": 2, "cart_id": 1, "variant_id": 4, "quantity": 1, "message": "Item added to cart" }
```

---

### TC-14 — Add quantity exactly equal to available stock

Variant 7 has stock = 5.

**Method:** POST `/carts/1/items`

**Body:**
```json
{ "variant_id": 7, "quantity": 5 }
```

**Expected status:** `201`

**Expected response:**
```json
{ "item_id": 3, "cart_id": 1, "variant_id": 7, "quantity": 5, "message": "Item added to cart" }
```

---

### TC-15 — Add item to non-existent cart

**Method:** POST `/carts/9999/items`

**Body:**
```json
{ "variant_id": 1, "quantity": 1 }
```

**Expected status:** `404`

**Expected response:**
```json
{ "error": "CART_NOT_FOUND", "message": "Cart not found" }
```

---

### TC-16 — Add non-existent variant to cart

**Method:** POST `/carts/1/items`

**Body:**
```json
{ "variant_id": 9999, "quantity": 1 }
```

**Expected status:** `404`

**Expected response:**
```json
{ "error": "VARIANT_NOT_FOUND", "message": "Variant not found" }
```

---

### TC-17 — Add item to a checked-out cart

First checkout the cart using TC-41, then try to add.

**Method:** POST `/carts/1/items`

**Body:**
```json
{ "variant_id": 2, "quantity": 1 }
```

**Expected status:** `409`

**Expected response:**
```json
{ "error": "CART_CHECKED_OUT", "message": "Cart already checked out" }
```

---

### TC-18 — Quantity exceeds available stock

Variant 7 has stock = 5. Requesting 10.

**Method:** POST `/carts/1/items`

**Body:**
```json
{ "variant_id": 7, "quantity": 10 }
```

**Expected status:** `422`

**Expected response:**
```json
{ "error": "INSUFFICIENT_STOCK", "message": "Requested quantity exceeds available stock" }
```

---

### TC-19 — Accumulated quantity exceeds stock

Variant 7 has stock = 5. Add 4, then add 3 more (total = 7 > 5).

**Step 1:** POST `/carts/1/items` with `{ "variant_id": 7, "quantity": 4 }` → 201

**Step 2:** POST `/carts/1/items` with `{ "variant_id": 7, "quantity": 3 }` → should fail

**Expected status (step 2):** `422`

**Expected response:**
```json
{ "error": "INSUFFICIENT_STOCK", "message": "Requested quantity exceeds available stock" }
```

---

### TC-20 — quantity is zero

**Method:** POST `/carts/1/items`

**Body:**
```json
{ "variant_id": 1, "quantity": 0 }
```

**Expected status:** `422`

**Expected response:**
```json
{ "error": "VALIDATION_ERROR", "details": [{ "field": "quantity", "message": "Must be greater than 0" }] }
```

---

### TC-21 — quantity is negative

**Method:** POST `/carts/1/items`

**Body:**
```json
{ "variant_id": 1, "quantity": -3 }
```

**Expected status:** `422`

**Expected response:**
```json
{ "error": "VALIDATION_ERROR", "details": [{ "field": "quantity", "message": "Must be greater than 0" }] }
```

---

### TC-22 — variant_id is zero

**Method:** POST `/carts/1/items`

**Body:**
```json
{ "variant_id": 0, "quantity": 1 }
```

**Expected status:** `422`

**Expected response:**
```json
{ "error": "VALIDATION_ERROR", "details": [{ "field": "variant_id", "message": "Must be greater than 0" }] }
```

---

### TC-23 — variant_id is negative

**Method:** POST `/carts/1/items`

**Body:**
```json
{ "variant_id": -1, "quantity": 1 }
```

**Expected status:** `422`

**Expected response:**
```json
{ "error": "VALIDATION_ERROR", "details": [{ "field": "variant_id", "message": "Must be greater than 0" }] }
```

---

### TC-24 — variant_id missing from body

**Method:** POST `/carts/1/items`

**Body:**
```json
{ "quantity": 2 }
```

**Expected status:** `422`

**Expected response:**
```json
{ "error": "VALIDATION_ERROR", "details": [{ "field": "variant_id", "message": "This field is required" }] }
```

---

### TC-25 — quantity missing from body

**Method:** POST `/carts/1/items`

**Body:**
```json
{ "variant_id": 1 }
```

**Expected status:** `422`

**Expected response:**
```json
{ "error": "VALIDATION_ERROR", "details": [{ "field": "quantity", "message": "This field is required" }] }
```

---

## Group C — Remove Item (DELETE /carts/{cart_id}/items/{item_id})

> **Prerequisite:** Create a cart and add an item. Use the returned `cart_id` and `item_id` in the path.

---

### TC-26 — Remove an existing item from cart

**Method:** DELETE `/carts/1/items/1`

**Expected status:** `200`

**Expected response:**
```json
{ "message": "Item removed from cart" }
```

---

### TC-27 — Remove item from non-existent cart

**Method:** DELETE `/carts/9999/items/1`

**Expected status:** `404`

**Expected response:**
```json
{ "error": "CART_NOT_FOUND", "message": "Cart not found" }
```

---

### TC-28 — Remove non-existent item

**Method:** DELETE `/carts/1/items/9999`

**Expected status:** `404`

**Expected response:**
```json
{ "error": "ITEM_NOT_FOUND", "message": "Item not found" }
```

---

### TC-29 — Remove item that belongs to a different cart

Create two carts (user 1 and user 2), add an item to cart 1. Then try to remove that item using cart 2's ID.

**Method:** DELETE `/carts/2/items/1`

**Expected status:** `404`

**Expected response:**
```json
{ "error": "ITEM_NOT_FOUND", "message": "Item not found" }
```

> This confirms items are checked against the specific cart, not just their own existence.

---

### TC-30 — Remove item from checked-out cart

First checkout the cart, then try to remove an item.

**Method:** DELETE `/carts/1/items/1`

**Expected status:** `409`

**Expected response:**
```json
{ "error": "CART_CHECKED_OUT", "message": "Cart already checked out" }
```

---

### TC-31 — cart_id is zero in path

**Method:** DELETE `/carts/0/items/1`

**Expected status:** `422`

**Expected response:**
```json
{ "error": "VALIDATION_ERROR", "details": [{ "field": "cart_id", "message": "Must be greater than 0" }] }
```

---

### TC-32 — item_id is zero in path

**Method:** DELETE `/carts/1/items/0`

**Expected status:** `422`

**Expected response:**
```json
{ "error": "VALIDATION_ERROR", "details": [{ "field": "item_id", "message": "Must be greater than 0" }] }
```

---

### TC-33 — cart_id overflow in path

**Method:** DELETE `/carts/99999999999999999999/items/1`

**Expected status:** `422`

**Expected response:**
```json
{ "error": "VALIDATION_ERROR", "details": [{ "field": "cart_id", "message": "Value is out of valid range" }] }
```

---

## Group D — Delete Cart (DELETE /carts/{cart_id})

---

### TC-34 — Delete an existing active cart

**Method:** DELETE `/carts/1`

**Expected status:** `200`

**Expected response:**
```json
{ "message": "Cart deleted successfully" }
```

---

### TC-35 — Delete a cart that has items (cascade check)

Create a cart, add multiple items, then delete the cart. All items should be deleted automatically.

**Method:** DELETE `/carts/1`

**Expected status:** `200`

**Expected response:**
```json
{ "message": "Cart deleted successfully" }
```

> Verify by checking `cart_items` in `check_db.py` — no orphan rows should remain.

---

### TC-36 — Delete non-existent cart

**Method:** DELETE `/carts/9999`

**Expected status:** `404`

**Expected response:**
```json
{ "error": "CART_NOT_FOUND", "message": "Cart not found" }
```

---

### TC-37 — cart_id is zero

**Method:** DELETE `/carts/0`

**Expected status:** `422`

**Expected response:**
```json
{ "error": "VALIDATION_ERROR", "details": [{ "field": "cart_id", "message": "Must be greater than 0" }] }
```

---

### TC-38 — cart_id is negative

**Method:** DELETE `/carts/-1`

**Expected status:** `422`

**Expected response:**
```json
{ "error": "VALIDATION_ERROR", "details": [{ "field": "cart_id", "message": "Must be greater than 0" }] }
```

---

### TC-39 — cart_id overflow

**Method:** DELETE `/carts/99999999999999999999`

**Expected status:** `422`

**Expected response:**
```json
{ "error": "VALIDATION_ERROR", "details": [{ "field": "cart_id", "message": "Value is out of valid range" }] }
```

---

### TC-40 — Delete a checked-out cart

First checkout a cart, then delete it. Deletion is allowed regardless of status.

**Method:** DELETE `/carts/1`

**Expected status:** `200`

**Expected response:**
```json
{ "message": "Cart deleted successfully" }
```

---

## Group E — Checkout (POST /carts/{cart_id}/checkout)

---

### TC-41 — Checkout an active cart with items

Create a cart, add at least one item, then checkout.

**Method:** POST `/carts/1/checkout`

**Expected status:** `200`

**Expected response:**
```json
{ "cart_id": 1, "status": "checked_out", "message": "Checkout successful" }
```

---

### TC-42 — Stock is reduced after checkout

**Step 1:** Run `check_db.py` and note stock of variant 1 (e.g., stock = 50).

**Step 2:** Create cart, add 10 units of variant 1, checkout.

**Step 3:** Run `check_db.py` again.

**Expected result:** Stock of variant 1 is now 40.

> This confirms stock deduction works correctly on checkout.

---

### TC-43 — Checkout non-existent cart

**Method:** POST `/carts/9999/checkout`

**Expected status:** `404`

**Expected response:**
```json
{ "error": "CART_NOT_FOUND", "message": "Cart not found" }
```

---

### TC-44 — Checkout an already checked-out cart

First checkout successfully (TC-41), then checkout again.

**Method:** POST `/carts/1/checkout`

**Expected status:** `409`

**Expected response:**
```json
{ "error": "CART_CHECKED_OUT", "message": "Cart already checked out" }
```

---

### TC-45 — Checkout an empty cart (no items)

Create a cart but do not add any items.

**Method:** POST `/carts/1/checkout`

**Expected status:** `422`

**Expected response:**
```json
{ "error": "CART_EMPTY", "message": "Cart is empty" }
```

---

### TC-46 — cart_id is zero

**Method:** POST `/carts/0/checkout`

**Expected status:** `422`

**Expected response:**
```json
{ "error": "VALIDATION_ERROR", "details": [{ "field": "cart_id", "message": "Must be greater than 0" }] }
```

---

### TC-47 — cart_id overflow

**Method:** POST `/carts/99999999999999999999/checkout`

**Expected status:** `422`

**Expected response:**
```json
{ "error": "VALIDATION_ERROR", "details": [{ "field": "cart_id", "message": "Value is out of valid range" }] }
```

---

## Group F — Full Lifecycle & Business Logic Tests

---

### TC-48 — Complete happy path flow

Run these steps in order:

| Step | Request | Expected |
|------|---------|----------|
| 1 | POST `/carts` `{ "user_id": 1 }` | 201, cart created |
| 2 | POST `/carts/1/items` `{ "variant_id": 1, "quantity": 2 }` | 201, item added |
| 3 | POST `/carts/1/items` `{ "variant_id": 4, "quantity": 1 }` | 201, second item added |
| 4 | DELETE `/carts/1/items/{item_id}` | 200, item removed |
| 5 | POST `/carts/1/items` `{ "variant_id": 4, "quantity": 1 }` | 201, item re-added |
| 6 | POST `/carts/1/checkout` | 200, status = checked_out |

> This is the complete normal user journey from cart creation to checkout.

---

### TC-49 — User can create a new cart after checkout

After completing TC-48, the user should be able to open a new cart.

**Method:** POST `/carts`

**Body:**
```json
{ "user_id": 1 }
```

**Expected status:** `201`

**Expected response:**
```json
{ "cart_id": 2, "user_id": 1, "message": "Cart created successfully" }
```

> A user is only blocked from creating a second cart if their current one is still active. After checkout, they are free to start a new one.

---

### TC-50 — Stock enforcement carries over between sessions

**Step 1:** Note variant 7 has stock = 5.

**Step 2:** Create a cart for user 3, add 5 units of variant 7, checkout.
- Variant 7 stock is now 0.

**Step 3:** Create a new cart for user 3.

**Step 4:** Try to add 1 unit of variant 7.

**Method:** POST `/carts/{new_cart_id}/items`

**Body:**
```json
{ "variant_id": 7, "quantity": 1 }
```

**Expected status:** `422`

**Expected response:**
```json
{ "error": "INSUFFICIENT_STOCK", "message": "Requested quantity exceeds available stock" }
```

> This confirms the full stock lifecycle: stock is checked on add, deducted on checkout, and enforced on the next purchase attempt.

---

## Test Summary Table

| TC | Endpoint | Scenario | Expected |
|----|----------|----------|----------|
| 01 | POST /carts | Valid user | 201 |
| 02 | POST /carts | Different valid user | 201 |
| 03 | POST /carts | User already has active cart | 409 |
| 04 | POST /carts | Non-existent user | 404 |
| 05 | POST /carts | user_id = 0 | 422 |
| 06 | POST /carts | user_id negative | 422 |
| 07 | POST /carts | user_id is string | 422 |
| 08 | POST /carts | user_id missing | 422 |
| 09 | POST /carts | user_id overflow | 422 |
| 10 | POST /carts | user_id decimal | 422 |
| 11 | POST /carts/{id}/items | New item | 201 |
| 12 | POST /carts/{id}/items | Same variant again (accumulate) | 201 |
| 13 | POST /carts/{id}/items | Different variant | 201 |
| 14 | POST /carts/{id}/items | Quantity exactly equals stock | 201 |
| 15 | POST /carts/{id}/items | Cart not found | 404 |
| 16 | POST /carts/{id}/items | Variant not found | 404 |
| 17 | POST /carts/{id}/items | Cart checked out | 409 |
| 18 | POST /carts/{id}/items | Quantity exceeds stock | 422 |
| 19 | POST /carts/{id}/items | Accumulated quantity exceeds stock | 422 |
| 20 | POST /carts/{id}/items | quantity = 0 | 422 |
| 21 | POST /carts/{id}/items | quantity negative | 422 |
| 22 | POST /carts/{id}/items | variant_id = 0 | 422 |
| 23 | POST /carts/{id}/items | variant_id negative | 422 |
| 24 | POST /carts/{id}/items | variant_id missing | 422 |
| 25 | POST /carts/{id}/items | quantity missing | 422 |
| 26 | DELETE /carts/{id}/items/{id} | Remove existing item | 200 |
| 27 | DELETE /carts/{id}/items/{id} | Cart not found | 404 |
| 28 | DELETE /carts/{id}/items/{id} | Item not found | 404 |
| 29 | DELETE /carts/{id}/items/{id} | Item belongs to different cart | 404 |
| 30 | DELETE /carts/{id}/items/{id} | Cart checked out | 409 |
| 31 | DELETE /carts/{id}/items/{id} | cart_id = 0 | 422 |
| 32 | DELETE /carts/{id}/items/{id} | item_id = 0 | 422 |
| 33 | DELETE /carts/{id}/items/{id} | cart_id overflow | 422 |
| 34 | DELETE /carts/{id} | Delete active cart | 200 |
| 35 | DELETE /carts/{id} | Delete cart with items (cascade) | 200 |
| 36 | DELETE /carts/{id} | Cart not found | 404 |
| 37 | DELETE /carts/{id} | cart_id = 0 | 422 |
| 38 | DELETE /carts/{id} | cart_id negative | 422 |
| 39 | DELETE /carts/{id} | cart_id overflow | 422 |
| 40 | DELETE /carts/{id} | Delete checked-out cart | 200 |
| 41 | POST /carts/{id}/checkout | Active cart with items | 200 |
| 42 | POST /carts/{id}/checkout | Verify stock reduced after checkout | verify DB |
| 43 | POST /carts/{id}/checkout | Cart not found | 404 |
| 44 | POST /carts/{id}/checkout | Cart already checked out | 409 |
| 45 | POST /carts/{id}/checkout | Empty cart | 422 |
| 46 | POST /carts/{id}/checkout | cart_id = 0 | 422 |
| 47 | POST /carts/{id}/checkout | cart_id overflow | 422 |
| 48 | All endpoints | Complete happy path flow | all pass |
| 49 | POST /carts | New cart after checkout | 201 |
| 50 | POST /carts/{id}/items | Stock at 0 after prior checkout | 422 |
