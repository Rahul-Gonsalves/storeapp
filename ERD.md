# Store App ER Diagram

```mermaid
erDiagram
    USERS ||--o{ ORDERS : places
    USERS ||--o{ PRODUCTS : lists
    ORDERS ||--|{ ORDERLINE : contains
    PRODUCTS ||--o{ ORDERLINE : appears_in

    USERS {
        INT UserID PK
        VARCHAR UserName
        VARCHAR Password
        VARCHAR DisplayName
    }

    PRODUCTS {
        INT ProductID PK
        VARCHAR Name
        DOUBLE Price
        DOUBLE Quantity
        INT SellerID FK
    }

    ORDERS {
        INT OrderID PK
        DATE OrderDate
        INT CustomerID FK
        DOUBLE TotalCost
        DOUBLE TotalTax
    }

    ORDERLINE {
        INT OrderID PK, FK
        INT ProductID PK, FK
        DOUBLE Quantity
        DOUBLE Cost
    }
```

## Relationship notes
- `USERS(UserID)` to `ORDERS(CustomerID)`: one user can create many orders.
- `USERS(UserID)` to `PRODUCTS(SellerID)`: one user can create/manage many products.
- `ORDERS(OrderID)` to `ORDERLINE(OrderID)`: one order has one or more order lines.
- `PRODUCTS(ProductID)` to `ORDERLINE(ProductID)`: one product can appear in many order lines.
- `ORDERLINE` uses composite key `(OrderID, ProductID)`.
