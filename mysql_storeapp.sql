DROP DATABASE IF EXISTS storeapp;
CREATE DATABASE storeapp;
USE storeapp;

CREATE TABLE Users (
    UserID INT NOT NULL,
    UserName VARCHAR(30) NOT NULL,
    Password VARCHAR(30) NOT NULL,
    DisplayName VARCHAR(30),
    PRIMARY KEY (UserID),
    UNIQUE KEY uq_users_username (UserName)
);

CREATE TABLE Products (
    ProductID INT NOT NULL,
    Name VARCHAR(30) NOT NULL,
    Price DOUBLE NOT NULL,
    Quantity DOUBLE,
    SellerID INT,
    PRIMARY KEY (ProductID),
    CONSTRAINT fk_products_seller
        FOREIGN KEY (SellerID)
        REFERENCES Users(UserID)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

CREATE TABLE Orders (
    OrderID INT NOT NULL,
    OrderDate DATE NOT NULL,
    CustomerID INT,
    TotalCost DOUBLE,
    TotalTax DOUBLE,
    PRIMARY KEY (OrderID),
    CONSTRAINT fk_orders_customer
        FOREIGN KEY (CustomerID)
        REFERENCES Users(UserID)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

CREATE TABLE OrderLine (
    OrderID INT NOT NULL,
    ProductID INT NOT NULL,
    Quantity DOUBLE,
    Cost DOUBLE,
    PRIMARY KEY (ProductID, OrderID),
    CONSTRAINT fk_orderline_order
        FOREIGN KEY (OrderID)
        REFERENCES Orders(OrderID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_orderline_product
        FOREIGN KEY (ProductID)
        REFERENCES Products(ProductID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

INSERT INTO Users (UserID, UserName, Password, DisplayName) VALUES
(1, 'admin', 'password', 'Adam Smith');

INSERT INTO Products (ProductID, Name, Price, Quantity, SellerID) VALUES
(1, 'Apple', 0.99, 100.0, 1),
(2, 'Milk', 3.99, 159.5, 1),
(3, 'Cheese', 4.99, 3.5, 1),
(4, 'Bread', 1.99, 20.0, 1),
(5, 'Hamburger', 3.99, 50.0, 1),
(10, 'Apple', 1.99, 10.0, 1),
(11, 'Candy', 9.99, 19.0, 1),
(20, 'Skim Milk', 2.99, 1000.0, 1),
(100, 'Samsung TV', 399.99, 1000.0, 1),
(111, 'iPhone X', 999.99, 10.0, 1),
(200, 'LG Phone', 99.99, 100.0, 1),
(300, 'Huawei Phone', 999.99, 10.0, 1),
(100001, 'Apple iPhone Xs Max', 1599.99, 8.0, 1);

INSERT INTO Orders (OrderID, OrderDate, CustomerID, TotalCost, TotalTax) VALUES
(1, '2026-02-23', 1, 0.00, 0.00);

INSERT INTO OrderLine (OrderID, ProductID, Quantity, Cost) VALUES
(1, 1, 0, 0);
