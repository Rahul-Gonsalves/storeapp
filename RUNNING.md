# Running Store App

## 1) Compile (both SQLite and MySQL modes)
From project root:

```bash
javac -cp "lib/*" -d bin src/*.java
```

## 2) Run in current SQLite mode

```bash
STOREAPP_DB=sqlite java -cp "bin:lib/*" Application
```

## 3) Prepare MySQL database
Create schema/data:

```bash
mysql -u root -p < mysql_storeapp.sql
```

## 4) Run in MySQL mode
Set your MySQL connection variables and run:

```bash
STOREAPP_DB=mysql \
STOREAPP_DB_HOST=localhost \
STOREAPP_DB_PORT=3306 \
STOREAPP_DB_NAME=storeapp \
STOREAPP_DB_USER=root \
STOREAPP_DB_PASSWORD=your_password \
java -cp "bin:lib/*" Application
```

## 5) Windows to capture screenshots
- Login window (`LoginScreen`)
- Main window (`MainScreen`)
- Product window (`ProductView`)
- Order window (`OrderView`)

## 6) Use cases to capture screenshots (MySQL mode)
- Login with `admin / password`
- Find an existing product: in Product View, enter `Product ID` then `Load Product`
- Modify price/quantity: load product, edit `Price` or `Quantity`, click `Save Product`
- Add a new product: enter new ID + name + price + quantity, click `Save Product`
- Make a new order: open Order View, click `Add a new item`, provide ProductID and quantity, then `Finish and pay`
