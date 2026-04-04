# Running Store App

## Homework 2 mode

### 1. Install backend dependencies

```bash
pip3 install -r requirements.txt
```

### 2. Start the REST backend

Set your database environment variables, then run:

```bash
python3 backend_api.py
```

Important environment variables:

```bash
STOREAPP_DB_HOST=localhost
STOREAPP_DB_PORT=3306
STOREAPP_DB_NAME=storeapp
STOREAPP_DB_USER=root
STOREAPP_DB_PASSWORD=your_password

STOREAPP_REDIS_HOST=localhost
STOREAPP_REDIS_PORT=6379
STOREAPP_REDIS_USER=
STOREAPP_REDIS_PASSWORD=
STOREAPP_REDIS_DB=0

MONGODB_URI=mongodb://localhost:27017/
STOREAPP_MONGO_DB=storeapp
STOREAPP_MONGO_COLLECTION=orders
STOREAPP_API_HOST=127.0.0.1
STOREAPP_API_PORT=9000
```

### 3. Compile and run the Java client in REST mode

```bash
javac -cp "lib/*" -d bin src/*.java
STOREAPP_DATA_MODE=rest \
STOREAPP_API_BASE_URL=http://127.0.0.1:9000 \
java -cp "bin:lib/*" Application
```

### 4. Optional migration from Homework 1 data

This copies products and orders from your old Homework 1 database into Redis and MongoDB.

```bash
python3 migrate_homework1_data.py
```

To migrate from MySQL instead of `store.db`:

```bash
STOREAPP_MIGRATE_SOURCE=mysql python3 migrate_homework1_data.py
```

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
