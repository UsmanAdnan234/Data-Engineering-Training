# Data Engineering Training

## Shopping Cart Database Schema

### Overview

This project implements a relational database schema for a shopping cart system. The database is designed to manage users, products, shopping carts, and cart items while maintaining data integrity through the use of primary keys, foreign keys, unique constraints, and default values.

---

## Entity Relationship Diagram

The database schema is illustrated in the ERD below:

**ERD File:** 'erd-of-cart.png'

---

## Database Structure

### Users

Stores information about registered users.

**Attributes**

* 'user_id' – Primary key, auto-incremented identifier.
* 'name' – User's full name.
* 'email' – User's email address.
* 'phone' – User's phone number.

**Constraints**

* 'user_id' is the primary key.
* 'email' must be unique.
* 'phone' must be unique.
* All fields are required.

---

### Carts

Represents a shopping cart associated with a user.

**Attributes**

* 'cart_id' – Primary key, auto-incremented identifier.
* 'user_id' – References the owner of the cart.
* 'created_at' – Timestamp indicating when the cart was created.

**Constraints**

* 'cart_id' is the primary key.
* 'user_id' is a foreign key referencing 'users(user_id)'.
* 'user_id' is unique, ensuring one cart per user.
* 'created_at' defaults to the current timestamp.

---

### Products

Stores information about products available in the system.

**Attributes**

* 'product_id' – Primary key, auto-incremented identifier.
* 'name' – Product name.
* 'price' – Product price.

**Constraints**

* `product_id` is the primary key.
* Product name is required.
* Product price is required.

---

### Cart Items

Acts as a junction table between carts and products. It stores the products added to each cart and their quantities.

**Attributes**

* 'item_id' – Primary key, auto-incremented identifier.
* 'cart_id' – References a shopping cart.
* 'product_id' – References a product.
* 'quantity' – Number of units of the product in the cart.
* 'added_at' – Timestamp indicating when the product was added.

**Constraints**

* 'item_id' is the primary key.
* 'cart_id' is a foreign key referencing `carts(cart_id)`.
* 'product_id' is a foreign key referencing `products(product_id)`.
* 'quantity' defaults to '1'.
* '(cart_id, product_id)' must be unique to prevent duplicate product entries within the same cart.

---

## Relationships

### Users and Carts (One-to-One)

- Each user can own exactly one cart.
- Each cart belongs to exactly one user.

### Carts and Cart Items (One-to-Many)

- A cart can contain multiple cart items.
- Each cart item belongs to exactly one cart.

### Products and Cart Items (One-to-Many)

- A product can appear in multiple cart items.
- Each cart item references exactly one product.

### Indirect Relationship: Carts and Products (Many-to-Many)

The many-to-many relationship between carts and products is implemented through the 'cart_items' junction table:

- A cart can contain multiple products.
- A product can appear in multiple carts.
- Each record in 'cart_items' represents a product added to a specific cart.

---

## Business Rules

* Every user must have a unique email address.
* Every user must have a unique phone number.
* Each user can own only one shopping cart.
* A cart can contain multiple products.
* A product can exist in multiple carts.
* Duplicate products within the same cart are not allowed.
* Product quantities are maintained through the 'quantity' attribute.
* Creation timestamps are automatically generated for carts and cart items.

---

## Data Integrity

The schema ensures consistency and reliability through:

* Primary keys for unique record identification.
* Foreign keys for referential integrity.
* Unique constraints to prevent duplicate records.
* Not-null constraints to enforce required fields.
* Default values for timestamps and quantities.

---

## Design Benefits

* Simple and normalized relational design.
* Prevents data duplication.
* Supports efficient cart management.
* Maintains strong referential integrity.
* Easily extensible for future e-commerce features such as orders, payments, inventory management, and product categories.

--- 

## Database Normalization

The database schema is normalized up to **Third Normal Form (3NF)**.

### First Normal Form (1NF)

The schema satisfies 1NF because:

* Each table has a primary key that uniquely identifies each record.
* All attributes contain atomic (indivisible) values.
* There are no repeating groups or multi-valued attributes.

### Second Normal Form (2NF)

The schema satisfies 2NF because:

* It is already in 1NF.
* All non-key attributes are fully dependent on their respective primary keys.
* No partial dependencies exist.

Examples:

* In 'users', 'name', 'email', and 'phone' depend entirely on 'user_id'.
* In 'products', 'name' and 'price' depend entirely on 'product_id'.
* In 'cart_items', 'quantity' depends on the specific cart-product association.

### Third Normal Form (3NF)

The schema satisfies 3NF because:

* It is already in 2NF.
* No non-key attribute depends on another non-key attribute.
* All non-key attributes depend only on the primary key and nothing else.

Examples:

* User information is stored only in the 'users' table.
* Product information is stored only in the 'products' table.
* Cart information is stored only in the 'carts' table.
* The 'cart_items' table stores only the relationship between carts and products along with the quantity.

### Benefits of Normalization

* Reduces data redundancy.
* Prevents update, insertion, and deletion anomalies.
* Improves data consistency and integrity.
* Simplifies maintenance and future schema extensions.

Therefore, the schema is considered to be in **Third Normal Form (3NF)**, providing a well-structured and efficient relational database design.


---

## Conclusion

This schema provides a robust foundation for implementing shopping cart functionality in an e-commerce application. By enforcing clear relationships and integrity constraints, the design ensures accurate data management while remaining scalable and easy to maintain.
